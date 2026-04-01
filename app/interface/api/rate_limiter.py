"""
Rate Limiter - Controle de Taxa de Requisições

Implementa limitação de requisições por API Key para proteger
a API contra abuso e ataques DDoS.

Autor: Cristóvão Caldeira
Data: Fevereiro 2026
Projeto: Portfólio Python - Projeto 2/5 - Etapa 5 - Mini-Etapa 5.4
"""

from datetime import datetime, timedelta
from typing import Dict, Tuple


class RateLimiter:
    """
    Gerenciador de rate limiting em memória.
    
    Responsabilidades:
        - Rastrear número de requisições por API Key
        - Verificar se limite foi excedido
        - Resetar contadores após janela de tempo
    
    Design:
        - Armazena: {api_key: (contador, timestamp_inicio)}
        - Janela de tempo: 1 minuto (60 segundos)
        - Limite padrão: 10 requisições por minuto
    """
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Inicializa rate limiter.
        
        Args:
            max_requests: Máximo de requisições permitidas na janela
            window_seconds: Tamanho da janela em segundos
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        
        # Dicionário: api_key → (contador, timestamp_inicio_janela)
        self._requests: Dict[str, Tuple[int, datetime]] = {}
    
    def is_allowed(self, api_key: str) -> Tuple[bool, int, int]:
        """
        Verifica se requisição é permitida.
        
        Args:
            api_key: API Key do cliente
        
        Returns:
            Tuple[bool, int, int]: (permitido?, usado, restante)
        """
        now = datetime.now()
        
        # CASO 1: Primeira requisição desta API Key
        if api_key not in self._requests:
            self._requests[api_key] = (1, now)
            return True, 1, self.max_requests - 1
        
        count, window_start = self._requests[api_key]
        
        # CASO 2: Janela de tempo expirou (resetar contador)
        if now - window_start > timedelta(seconds=self.window_seconds):
            self._requests[api_key] = (1, now)
            return True, 1, self.max_requests - 1
        
        # CASO 3: Dentro da janela, verificar limite
        if count >= self.max_requests:
            # Limite excedido
            return False, count, 0
        
        # CASO 4: Dentro da janela e abaixo do limite
        self._requests[api_key] = (count + 1, window_start)
        return True, count + 1, self.max_requests - (count + 1)
    
    def get_reset_time(self, api_key: str) -> int:
        """
        Retorna segundos até o reset do contador.
        
        Args:
            api_key: API Key do cliente
        
        Returns:
            int: Segundos até reset (0 se key não existe)
        """
        if api_key not in self._requests:
            return 0
        
        _, window_start = self._requests[api_key]
        elapsed = (datetime.now() - window_start).total_seconds()
        remaining = max(0, self.window_seconds - elapsed)
        return int(remaining)
    
    def reset(self, api_key: str) -> bool:
        """
        Reseta contador de uma API Key manualmente.
        
        Args:
            api_key: API Key a resetar
        
        Returns:
            bool: True se resetado, False se não existia
        """
        if api_key in self._requests:
            del self._requests[api_key]
            return True
        return False
    
    def reset_all(self):
        """Reseta todos os contadores (útil para testes)."""
        self._requests.clear()
    
    def __repr__(self):
        return f'RateLimiter(max={self.max_requests}, window={self.window_seconds}s, tracked={len(self._requests)})'


# =============================================================================
# INSTÂNCIA SINGLETON
# =============================================================================

# Configuração: 10 requisições por minuto
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)


# =============================================================================
# FUNÇÕES DE CONVENIÊNCIA
# =============================================================================

def check_rate_limit(api_key: str) -> Tuple[bool, int, int]:
    """
    Verifica se requisição é permitida.
    
    Args:
        api_key: API Key do cliente
    
    Returns:
        Tuple[bool, int, int]: (permitido?, usado, restante)
    """
    return rate_limiter.is_allowed(api_key)


def get_reset_time(api_key: str) -> int:
    """
    Retorna segundos até reset.
    
    Args:
        api_key: API Key do cliente
    
    Returns:
        int: Segundos até reset
    """
    return rate_limiter.get_reset_time(api_key)