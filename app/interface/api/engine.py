"""
Decision Engine Instance - API

Instância singleton do motor de decisão para uso na API.
Centraliza a criação e acesso ao DecisionEngine.

Autor: Cristóvão Caldeira
Data: Fevereiro 2026
Projeto: Portfólio Python - Projeto 2/5 - Etapa 3 - Mini-Etapa 3.3
"""

from app.application.decision_engine import DecisionEngine


# =============================================================================
# INSTÂNCIA SINGLETON DO MOTOR DE DECISÃO
# =============================================================================

# Instância global compartilhada por toda a API
decision_engine = DecisionEngine()


# =============================================================================
# FUNÇÃO DE CONVENIÊNCIA
# =============================================================================

def get_engine() -> DecisionEngine:
    """
    Retorna a instância do motor de decisão.
    
    Returns:
        DecisionEngine: Instância singleton do motor
    
    Uso:
        >>> from app.interface.api.engine import get_engine
        >>> engine = get_engine()
        >>> decision = engine.evaluate(request)
    """
    return decision_engine
