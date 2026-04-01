"""
Módulo de Plan - Entidade de Domínio

Define a estrutura de planos comerciais do sistema, incluindo:
- Limites de requisições mensais
- Tamanho máximo de payload
- Tipos de validação permitidos

Planos determinam as capacidades e restrições de cada cliente B2B.

Autor: [Seu Nome]
Data: Janeiro 2026
"""


class Plan:
    """
    Representa um plano comercial (contrato SaaS) para clientes B2B.
    
    Responsabilidades:
        - Armazenar configuração de limites do plano
        - Definir tipos de validação permitidos
        - Validar se payload respeita limite de tamanho
        - Validar se tipo de validação é permitido
    
    Design:
        Plano é imutável após criação. Não deve ser modificado durante
        a execução do sistema. Novos planos são criados como novas instâncias.
    
    Atributos:
        nome (str): Nome identificador do plano (ex: "Basic", "Silver", "Gold")
        max_requests (int): Limite mensal de requisições
        max_payload_size (int): Tamanho máximo de payload em bytes
        tipos_permitidos (list[str]): Tipos de validação que o plano permite
    
    Regras de Negócio:
        - Limites são fixos após criação
        - Tipos permitidos não podem ser vazios
        - Validações são determinísticas (mesma entrada = mesma saída)
        - Plano não conhece clientes (separação de responsabilidades)
    
    Exemplo:
        >>> plan = Plan(
        ...     nome="Basic",
        ...     max_requests=100,
        ...     max_payload_size=1024,
        ...     tipos_permitidos=["validacao_cpf"]
        ... )
        >>> plan.allows_validation_type("validacao_cpf")  # True
        >>> plan.allows_validation_type("validacao_endereco")  # False
    """
    
    def __init__(
        self,
        nome: str,
        max_requests: int,
        max_payload_size: int,
        tipos_permitidos: list
    ):
        """
        Inicializa um plano comercial.
        
        Args:
            nome: Nome identificador do plano (ex: "Basic", "Silver", "Gold")
            max_requests: Número máximo de requisições permitidas por mês
            max_payload_size: Tamanho máximo do payload em bytes
            tipos_permitidos: Lista de tipos de validação permitidos pelo plano
        
        Raises:
            ValueError: Se max_requests <= 0 ou max_payload_size <= 0
                       ou tipos_permitidos vazio
        
        Exemplo:
            >>> plan = Plan(
            ...     nome="Silver",
            ...     max_requests=500,
            ...     max_payload_size=10240,
            ...     tipos_permitidos=["validacao_cpf", "validacao_endereco"]
            ... )
        """
        # Validações de entrada
        if max_requests <= 0:
            raise ValueError("max_requests deve ser maior que 0")
        
        if max_payload_size <= 0:
            raise ValueError("max_payload_size deve ser maior que 0")
        
        if not tipos_permitidos or len(tipos_permitidos) == 0:
            raise ValueError("tipos_permitidos não pode estar vazio")
        
        self.nome = nome
        self.max_requests = max_requests
        self.max_payload_size = max_payload_size
        self.tipos_permitidos = tipos_permitidos
    
    def allows_payload_size(self, payload) -> bool:
        """
        Verifica se o payload respeita o limite de tamanho do plano.
        
        Args:
            payload: Objeto Payload a ser validado (deve ter método size())
        
        Returns:
            bool: True se payload cabe no limite, False caso contrário
        
        Comportamento:
            Compara payload.size() com max_payload_size do plano.
            Payload exatamente no limite é considerado válido (<=).
        
        Exemplo:
            >>> from app.domain.payload import Payload
            >>> plan = Plan("Basic", 100, 1024, ["validacao_cpf"])
            >>> payload_pequeno = Payload("validacao_cpf", {"cpf": "123", "nome": "X"})
            >>> plan.allows_payload_size(payload_pequeno)  # True
        """
        return payload.size() <= self.max_payload_size
    
    def allows_validation_type(self, tipo: str) -> bool:
        """
        Verifica se o plano permite determinado tipo de validação.
        
        Args:
            tipo: Tipo de validação solicitada (ex: "validacao_cpf")
        
        Returns:
            bool: True se o tipo é permitido pelo plano, False caso contrário
        
        Comportamento:
            Verifica se o tipo está na lista tipos_permitidos.
            Comparação é case-sensitive.
        
        Exemplo:
            >>> plan = Plan("Silver", 500, 10240, ["validacao_cpf", "validacao_endereco"])
            >>> plan.allows_validation_type("validacao_cpf")  # True
            >>> plan.allows_validation_type("validacao_dados_bancarios")  # False
        """
        return tipo in self.tipos_permitidos
    
    def get_readable_limits(self) -> dict:
        """
        Retorna limites do plano em formato legível.
        
        Returns:
            dict: Dicionário com limites formatados
        
        Útil para:
            - Exibir informações do plano para usuário
            - Gerar relatórios
            - Documentação de API
        
        Exemplo:
            >>> plan = Plan("Gold", 2000, 102400, ["validacao_cpf", "validacao_endereco"])
            >>> limits = plan.get_readable_limits()
            >>> print(limits['payload_size'])  # "100.0 KB"
        """
        # Converter bytes para KB/MB
        if self.max_payload_size < 1024:
            size_readable = f"{self.max_payload_size} bytes"
        elif self.max_payload_size < 1048576:  # 1MB
            size_readable = f"{self.max_payload_size / 1024:.1f} KB"
        else:
            size_readable = f"{self.max_payload_size / 1048576:.1f} MB"
        
        return {
            'nome': self.nome,
            'max_requests': f"{self.max_requests} requests/mês",
            'payload_size': size_readable,
            'tipos_permitidos': len(self.tipos_permitidos),
            'tipos_lista': self.tipos_permitidos
        }
    
    def is_near_limit(self, requests_usados: int, threshold: float = 0.8) -> bool:
        """
        Verifica se uso está próximo do limite.
        
        Args:
            requests_usados: Número de requisições já consumidas
            threshold: Percentual que define "próximo" (padrão: 0.8 = 80%)
        
        Returns:
            bool: True se uso >= threshold do limite
        
        Útil para:
            - Alertas ao cliente
            - Notificações de upgrade
            - Dashboard de uso
        
        Exemplo:
            >>> plan = Plan("Basic", 100, 1024, ["validacao_cpf"])
            >>> plan.is_near_limit(85)  # True (85% > 80%)
            >>> plan.is_near_limit(75)  # False (75% < 80%)
        """
        if self.max_requests == 0:
            return False
        
        usage_ratio = requests_usados / self.max_requests
        return usage_ratio >= threshold
    
    def __repr__(self):
        """
        Representação string do plano para debugging.
        
        Returns:
            str: Representação legível do plano
        """
        return (
            f"Plan(nome='{self.nome}', max_requests={self.max_requests}, "
            f"max_payload_size={self.max_payload_size}, "
            f"tipos={len(self.tipos_permitidos)})"
        )
    
    def __str__(self):
        """
        Representação string amigável do plano.
        
        Returns:
            str: Descrição legível para usuário
        """
        return f"Plano {self.nome} ({self.max_requests} requests/mês)"
    
    def __eq__(self, other):
        """
        Compara igualdade entre planos.
        
        Args:
            other: Outro objeto Plan
        
        Returns:
            bool: True se planos são idênticos
        
        Nota:
            Útil para testes e comparações
        """
        if not isinstance(other, Plan):
            return False
        
        return (
            self.nome == other.nome and
            self.max_requests == other.max_requests and
            self.max_payload_size == other.max_payload_size and
            self.tipos_permitidos == other.tipos_permitidos
        )