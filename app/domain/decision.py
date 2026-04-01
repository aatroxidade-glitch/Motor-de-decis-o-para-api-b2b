"""
Módulo de Decision - Entidade de Domínio

Representa o resultado de uma avaliação do motor de decisão.
Encapsula se uma requisição foi aprovada ou rejeitada e o motivo.

Decision é imutável e não executa ações - apenas carrega o resultado.

Autor: [Seu Nome]
Data: Janeiro 2026
"""

from datetime import datetime


class Decision:
    """
    Representa o resultado da avaliação de uma requisição.
    
    Responsabilidades:
        - Armazenar resultado da decisão (aprovada ou rejeitada)
        - Armazenar justificativa explícita (motivo)
        - Servir como output do motor de decisão
        - Garantir rastreabilidade e auditabilidade
    
    Design:
        Decision é um Value Object imutável. Não executa ações, apenas
        carrega informação sobre o resultado de uma avaliação.
        
        Princípio: Separação entre decisão e execução.
        O motor DECIDE, mas não EXECUTA. A execução (ex: incrementar uso)
        é responsabilidade de quem processa a decisão.
    
    Atributos:
        aprovada (bool): True se requisição foi autorizada, False se rejeitada
        motivo (str): Justificativa explícita da decisão
        timestamp (datetime): Momento em que a decisão foi tomada
    
    Regras de Negócio:
        - Toda decisão SEMPRE tem motivo explícito
        - Decisão é imutável após criação
        - Motivo deve ser claro e acionável
        - Aprovações e rejeições são tratadas igualmente (ambas auditáveis)
    
    Exemplo de Decisões:
        Aprovada:
            >>> Decision(True, "Requisição autorizada: validacao_cpf")
        
        Rejeitada por plano:
            >>> Decision(False, "Plano Basic não permite validação do tipo 'validacao_endereco'")
        
        Rejeitada por payload:
            >>> Decision(False, "Payload inválido: Campos obrigatórios ausentes: nome")
        
        Rejeitada por limite:
            >>> Decision(False, "Limite de requisições excedido")
    """
    
    def __init__(self, aprovada: bool, motivo: str):
        """
        Inicializa uma decisão.
        
        Args:
            aprovada: True se requisição foi autorizada, False se rejeitada
            motivo: Justificativa clara e explícita da decisão
        
        Raises:
            ValueError: Se motivo estiver vazio
        
        Comportamento:
            - Timestamp é capturado automaticamente no momento da criação
            - Motivo não pode ser vazio (validação obrigatória)
        
        Exemplo:
            >>> decision = Decision(True, "Requisição autorizada: validacao_cpf")
            >>> decision.aprovada  # True
            >>> decision.motivo  # "Requisição autorizada: validacao_cpf"
        """
        if not motivo or motivo.strip() == "":
            raise ValueError("Motivo da decisão não pode estar vazio")
        
        self.aprovada = aprovada
        self.motivo = motivo
        self.timestamp = datetime.now()
    
    def is_approved(self) -> bool:
        """
        Verifica se a decisão foi de aprovar.
        
        Returns:
            bool: True se aprovada, False se rejeitada
        
        Nota:
            Método explícito para melhorar legibilidade do código.
        
        Exemplo:
            >>> decision = Decision(True, "Requisição autorizada")
            >>> if decision.is_approved():
            ...     print("Proceder com operação")
        """
        return self.aprovada
    
    def is_rejected(self) -> bool:
        """
        Verifica se a decisão foi de rejeitar.
        
        Returns:
            bool: True se rejeitada, False se aprovada
        
        Exemplo:
            >>> decision = Decision(False, "Limite excedido")
            >>> if decision.is_rejected():
            ...     print("Notificar cliente sobre rejeição")
        """
        return not self.aprovada
    
    def get_status_emoji(self) -> str:
        """
        Retorna emoji visual do status da decisão.
        
        Returns:
            str: "✅" se aprovada, "❌" se rejeitada
        
        Útil para:
            - Logs visuais
            - Relatórios para usuário
            - Dashboards
        
        Exemplo:
            >>> decision = Decision(True, "OK")
            >>> print(f"{decision.get_status_emoji()} {decision.motivo}")
            # "✅ OK"
        """
        return "✅" if self.aprovada else "❌"
    
    def get_category(self) -> str:
        """
        Categoriza a decisão com base no motivo.
        
        Returns:
            str: Categoria da decisão
        
        Categorias possíveis:
            - "aprovada"
            - "rejeitada_plano" (tipo não permitido, limite excedido)
            - "rejeitada_payload" (payload inválido)
            - "rejeitada_tamanho" (payload muito grande)
            - "rejeitada_outro"
        
        Útil para:
            - Estatísticas agregadas
            - Análise de motivos de rejeição
            - Relatórios
        
        Exemplo:
            >>> decision = Decision(False, "Plano Basic não permite validação do tipo")
            >>> decision.get_category()  # "rejeitada_plano"
        """
        if self.aprovada:
            return "aprovada"
        
        motivo_lower = self.motivo.lower()
        
        if "não permite validação do tipo" in motivo_lower:
            return "rejeitada_plano"
        elif "limite de requisições excedido" in motivo_lower:
            return "rejeitada_limite"
        elif "payload inválido" in motivo_lower:
            return "rejeitada_payload"
        elif "excede limite" in motivo_lower:
            return "rejeitada_tamanho"
        else:
            return "rejeitada_outro"
    
    def to_dict(self) -> dict:
        """
        Converte decisão para dicionário.
        
        Returns:
            dict: Representação em dicionário da decisão
        
        Útil para:
            - Serialização JSON
            - Logging estruturado
            - APIs REST
            - Persistência
        
        Exemplo:
            >>> decision = Decision(True, "Requisição autorizada")
            >>> decision.to_dict()
            {
                'aprovada': True,
                'motivo': 'Requisição autorizada',
                'timestamp': '2026-01-21T14:30:45.123456',
                'categoria': 'aprovada'
            }
        """
        return {
            'aprovada': self.aprovada,
            'motivo': self.motivo,
            'timestamp': self.timestamp.isoformat(),
            'categoria': self.get_category()
        }
    
    def get_formatted_timestamp(self, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Retorna timestamp formatado.
        
        Args:
            format_str: String de formato strftime
        
        Returns:
            str: Timestamp formatado
        
        Exemplo:
            >>> decision = Decision(True, "OK")
            >>> decision.get_formatted_timestamp()  # "2026-01-21 14:30:45"
        """
        return self.timestamp.strftime(format_str)
    
    def __repr__(self):
        """
        Representação string da decisão para debugging.
        
        Returns:
            str: Representação legível da decisão
        """
        status = "APROVADA" if self.aprovada else "REJEITADA"
        return f"Decision({status}, motivo='{self.motivo}')"
    
    def __str__(self):
        """
        Representação string amigável da decisão.
        
        Returns:
            str: Descrição legível para usuário
        """
        emoji = self.get_status_emoji()
        status = "APROVADA" if self.aprovada else "REJEITADA"
        return f"{emoji} {status}: {self.motivo}"
    
    def __bool__(self):
        """
        Permite uso da decisão em contexto booleano.
        
        Returns:
            bool: Valor de self.aprovada
        
        Permite:
            >>> decision = Decision(True, "OK")
            >>> if decision:  # Equivalente a if decision.aprovada:
            ...     print("Aprovada!")
        """
        return self.aprovada
    
    def __eq__(self, other):
        """
        Compara igualdade entre decisões.
        
        Args:
            other: Outra Decision
        
        Returns:
            bool: True se têm mesmo status e motivo
        """
        if not isinstance(other, Decision):
            return False
        return self.aprovada == other.aprovada and self.motivo == other.motivo