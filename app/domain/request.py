"""
Módulo de Request - Entidade de Domínio

Representa uma requisição de validação feita por um cliente, conectando:
- Cliente (quem está fazendo a requisição)
- Payload (dados a serem validados)
- Metadados (timestamp, ID único)

Request é imutável após criação e representa um snapshot no tempo.

Autor: [Seu Nome]
Data: Janeiro 2026
"""

import uuid
from datetime import datetime


class Request:
    """
    Representa o ato de consumo do serviço de validação.
    
    Responsabilidades:
        - Conectar cliente e payload em uma unidade lógica
        - Gerar ID único para rastreabilidade
        - Registrar timestamp da criação
        - Servir como input para o motor de decisão
    
    Design:
        Request é imutável após criação. Representa um momento específico
        no tempo em que um cliente solicitou validação de dados.
        
        Padrão: Value Object (identificado por ID único)
    
    Atributos:
        id (str): UUID único gerado automaticamente
        client (Client): Cliente que fez a requisição
        payload (Payload): Dados a serem validados
        timestamp (datetime): Momento exato da criação da requisição
    
    Regras de Negócio:
        - ID gerado automaticamente (UUID4)
        - Timestamp capturado no momento da criação
        - Imutável após criação (não deve ser modificado)
        - Representa snapshot do estado naquele momento
    
    Exemplo:
        >>> from app.domain.client import Client
        >>> from app.domain.payload import Payload
        >>> from app.domain.plans import BASIC_PLAN
        >>> 
        >>> cliente = Client("001", "Empresa X", BASIC_PLAN)
        >>> payload = Payload("validacao_cpf", {"cpf": "123", "nome": "João"})
        >>> request = Request(client=cliente, payload=payload)
        >>> 
        >>> print(request.id)  # "550e8400-e29b-41d4-a716-446655440000"
        >>> print(request.timestamp)  # 2026-01-21 14:30:45.123456
    """
    
    def __init__(self, client, payload):
        """
        Inicializa uma requisição de validação.
        
        Args:
            client: Objeto Client que está fazendo a requisição
            payload: Objeto Payload contendo os dados a serem validados
        
        Comportamento:
            - Gera ID único automaticamente (UUID4)
            - Captura timestamp no momento da criação
            - Armazena referências ao cliente e payload
        
        Nota:
            Request é imutável. Não modifique atributos após criação.
            Para nova requisição, crie nova instância.
        
        Exemplo:
            >>> request = Request(client=meu_cliente, payload=meu_payload)
            >>> # ID e timestamp já estão definidos
        """
        self.id = str(uuid.uuid4())
        self.client = client
        self.payload = payload
        self.timestamp = datetime.now()
    
    def get_context(self) -> dict:
        """
        Retorna contexto completo da requisição.
        
        Returns:
            dict: Dicionário com informações contextuais da requisição
        
        Útil para:
            - Logging estruturado
            - Auditoria
            - Debugging
            - Relatórios
        
        Exemplo:
            >>> request = Request(client=cliente, payload=payload)
            >>> context = request.get_context()
            >>> print(context['client_id'])  # "001"
            >>> print(context['payload_type'])  # "validacao_cpf"
        """
        return {
            'request_id': self.id,
            'client_id': self.client.id,
            'client_name': self.client.nome,
            'plan': self.client.plan.nome,
            'payload_type': self.payload.tipo,
            'payload_size': self.payload.size(),
            'timestamp': self.timestamp.isoformat(),
            'requests_used_before': self.client.requisicoes_usadas
        }
    
    def get_formatted_timestamp(self, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Retorna timestamp formatado.
        
        Args:
            format_str: String de formato strftime (padrão: "YYYY-MM-DD HH:MM:SS")
        
        Returns:
            str: Timestamp formatado
        
        Exemplo:
            >>> request = Request(client=cliente, payload=payload)
            >>> request.get_formatted_timestamp()  # "2026-01-21 14:30:45"
            >>> request.get_formatted_timestamp("%d/%m/%Y")  # "21/01/2026"
        """
        return self.timestamp.strftime(format_str)
    
    def age_in_seconds(self) -> float:
        """
        Calcula idade da requisição em segundos.
        
        Returns:
            float: Tempo decorrido desde criação em segundos
        
        Útil para:
            - Métricas de performance
            - Timeout de requisições
            - SLA tracking
        
        Exemplo:
            >>> request = Request(client=cliente, payload=payload)
            >>> import time
            >>> time.sleep(2)
            >>> request.age_in_seconds()  # ~2.0
        """
        return (datetime.now() - self.timestamp).total_seconds()
    
    def is_from_client(self, client_id: str) -> bool:
        """
        Verifica se requisição pertence a um cliente específico.
        
        Args:
            client_id: ID do cliente a verificar
        
        Returns:
            bool: True se requisição é do cliente especificado
        
        Útil para:
            - Filtros de auditoria
            - Relatórios por cliente
            - Controle de acesso
        
        Exemplo:
            >>> request = Request(client=cliente, payload=payload)
            >>> request.is_from_client("001")  # True
            >>> request.is_from_client("999")  # False
        """
        return self.client.id == client_id
    
    def __repr__(self):
        """
        Representação string da requisição para debugging.
        
        Returns:
            str: Representação legível da requisição
        """
        return (
            f"Request(id='{self.id[:8]}...', "
            f"client='{self.client.nome}', "
            f"payload_type='{self.payload.tipo}', "
            f"timestamp='{self.get_formatted_timestamp()}')"
        )
    
    def __str__(self):
        """
        Representação string amigável da requisição.
        
        Returns:
            str: Descrição legível para usuário
        """
        return (
            f"Requisição {self.id[:8]} - {self.client.nome} "
            f"({self.payload.tipo}) em {self.get_formatted_timestamp()}"
        )
    
    def __eq__(self, other):
        """
        Compara igualdade entre requisições.
        
        Args:
            other: Outra Request
        
        Returns:
            bool: True se têm o mesmo ID (requisições únicas)
        
        Nota:
            Requisições são comparadas por ID, não por conteúdo.
            Cada Request é única mesmo com mesmo cliente/payload.
        """
        if not isinstance(other, Request):
            return False
        return self.id == other.id
    
    def __hash__(self):
        """
        Hash da requisição baseado no ID único.
        
        Returns:
            int: Hash do ID da requisição
        
        Permite usar Request em sets e como chave de dict.
        """
        return hash(self.id)