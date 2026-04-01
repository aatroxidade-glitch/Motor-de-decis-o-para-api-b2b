"""
Módulo de Client - Entidade de Domínio

Define a representação de um cliente B2B que consome o serviço de validação.
Responsável por manter identidade, plano contratado e controle de uso.

Esta entidade é stateful (mantém estado de consumo) e é modificada pelo
motor de decisão ao aprovar requisições.

Autor: [Seu Nome]
Data: Janeiro 2026
"""


class Client:
    """
    Representa um cliente B2B que consome o serviço de validação.
    
    Responsabilidades:
        - Armazenar identidade do cliente (ID e nome)
        - Referenciar plano contratado
        - Controlar quantidade de requisições consumidas
        - Incrementar uso quando requisição é aprovada
    
    Design:
        Cliente é uma entidade stateful. O atributo `requisicoes_usadas`
        é modificado pelo motor de decisão ao aprovar requisições válidas.
    
    Atributos:
        id (str): Identificador único do cliente
        nome (str): Nome da empresa/cliente
        plan (Plan): Plano contratado pelo cliente
        requisicoes_usadas (int): Contador de requisições já consumidas
    
    Regras de Negócio:
        - Contador inicia em 0
        - Apenas incrementa quando requisição é aprovada
        - Não reseta automaticamente (responsabilidade externa)
        - Sempre vinculado a um plano válido
    
    Exemplo:
        >>> from app.domain.plans import BASIC_PLAN
        >>> cliente = Client(
        ...     id="CLI_001",
        ...     nome="TechStart LTDA",
        ...     plan=BASIC_PLAN
        ... )
        >>> print(cliente.requisicoes_usadas)  # 0
        >>> cliente.increment_usage()
        >>> print(cliente.requisicoes_usadas)  # 1
    """
    
    def __init__(self, id: str, nome: str, plan):
        """
        Inicializa um cliente B2B.
        
        Args:
            id: Identificador único do cliente (ex: "CLI_001", "client_123")
            nome: Nome da empresa/cliente (ex: "TechStart LTDA")
            plan: Instância de Plan representando o plano contratado
        
        Nota:
            O contador de requisições inicia em 0. Use increment_usage()
            para registrar consumo após aprovação de requisições.
        """
        self.id = id
        self.nome = nome
        self.plan = plan
        self.requisicoes_usadas = 0
    
    def increment_usage(self):
        """
        Incrementa o contador de requisições consumidas.
        
        Este método deve ser chamado apenas quando uma requisição é
        aprovada pelo motor de decisão. Requisições rejeitadas NÃO
        devem incrementar o contador.
        
        Efeito colateral:
            Modifica o estado interno do cliente (requisicoes_usadas += 1)
        
        Exemplo:
            >>> cliente = Client(id="001", nome="Empresa X", plan=BASIC_PLAN)
            >>> cliente.requisicoes_usadas  # 0
            >>> cliente.increment_usage()
            >>> cliente.requisicoes_usadas  # 1
        """
        self.requisicoes_usadas += 1
    
    def has_quota_available(self) -> bool:
        """
        Verifica se o cliente ainda tem quota disponível.
        
        Returns:
            bool: True se ainda pode fazer requisições, False caso contrário
        
        Exemplo:
            >>> cliente = Client(id="001", nome="Empresa", plan=BASIC_PLAN)
            >>> cliente.requisicoes_usadas = 99
            >>> cliente.has_quota_available()  # True (ainda pode fazer 1)
            >>> cliente.requisicoes_usadas = 100
            >>> cliente.has_quota_available()  # False (limite atingido)
        """
        return self.requisicoes_usadas < self.plan.max_requests
    
    def remaining_quota(self) -> int:
        """
        Calcula quantas requisições ainda podem ser feitas.
        
        Returns:
            int: Número de requisições restantes (mínimo 0)
        
        Exemplo:
            >>> cliente = Client(id="001", nome="Empresa", plan=BASIC_PLAN)
            >>> cliente.requisicoes_usadas = 75
            >>> cliente.remaining_quota()  # 25 (100 - 75)
        """
        return max(0, self.plan.max_requests - self.requisicoes_usadas)
    
    def usage_percentage(self) -> float:
        """
        Calcula percentual de uso da quota.
        
        Returns:
            float: Percentual de uso (0.0 a 100.0)
        
        Exemplo:
            >>> cliente = Client(id="001", nome="Empresa", plan=BASIC_PLAN)
            >>> cliente.requisicoes_usadas = 50
            >>> cliente.usage_percentage()  # 50.0
        """
        if self.plan.max_requests == 0:
            return 0.0
        return (self.requisicoes_usadas / self.plan.max_requests) * 100
    
    def __repr__(self):
        """
        Representação string do cliente para debugging.
        
        Returns:
            str: Representação legível do cliente
        """
        return (
            f"Client(id='{self.id}', nome='{self.nome}', "
            f"plan='{self.plan.nome}', uso={self.requisicoes_usadas}/{self.plan.max_requests})"
        )
    
    def __str__(self):
        """
        Representação string amigável do cliente.
        
        Returns:
            str: Descrição legível para usuário
        """
        return f"{self.nome} ({self.id}) - Plano {self.plan.nome}"