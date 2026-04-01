"""
Gerenciamento de API Keys - Autenticacao

Sistema de geracao e validacao de API Keys para autenticacao na API.
Cada cliente recebe uma API Key unica que deve ser enviada no header.
O administrador recebe uma API Key separada com acesso total ao sistema.

Autor: Cristovao Caldeira
Data: Fevereiro 2026
Projeto: Portfolio Python - Projeto 2/5 - Etapa Administrativa
"""

import secrets
from typing import Optional

from app.domain.client import Client


class APIKeysManager:
    """
    Gerenciador de API Keys para autenticacao.

    Responsabilidades:
        - Gerar API Keys unicas e seguras para clientes
        - Gerar API Key de administrador separada
        - Associar API Key de cliente ao Cliente
        - Validar API Key fornecida
        - Identificar se key e de admin ou cliente

    Design:
        - API Keys geradas com secrets (criptograficamente seguro)
        - Mapeamento bidirecional: key -> client e client -> key
        - Admin key armazenada separadamente
        - Validacao O(1) usando dicionario
    """

    def __init__(self):
        """Inicializa gerenciador vazio."""
        self._keys_to_clients: dict[str, Client] = {}
        self._clients_to_keys: dict[str, str] = {}
        self._admin_key: Optional[str] = None

    def generate_key(self) -> str:
        """Gera uma API Key unica e criptograficamente segura."""
        return secrets.token_hex(16)

    def generate_admin_key(self) -> str:
        """
        Gera e armazena a API Key do administrador.

        Returns:
            str: API Key de admin gerada

        Comportamento:
            - Gera nova key se nao existe
            - Retorna key existente se ja gerada
        """
        if self._admin_key:
            return self._admin_key
        self._admin_key = self.generate_key()
        return self._admin_key

    def is_admin_key(self, api_key: str) -> bool:
        """
        Verifica se a API Key e a key de administrador.

        Args:
            api_key: API Key a verificar

        Returns:
            bool: True se for a key de admin
        """
        if not api_key or not self._admin_key:
            return False
        return api_key == self._admin_key

    def is_client_key(self, api_key: str) -> bool:
        """
        Verifica se a API Key e de um cliente.

        Args:
            api_key: API Key a verificar

        Returns:
            bool: True se for key de cliente valido
        """
        if not api_key:
            return False
        return api_key in self._keys_to_clients

    def register_client(self, client: Client) -> str:
        """
        Registra cliente e gera API Key unica.

        Args:
            client: Cliente a registrar

        Returns:
            str: API Key gerada para o cliente
        """
        if client.id in self._clients_to_keys:
            return self._clients_to_keys[client.id]

        api_key = self.generate_key()
        self._keys_to_clients[api_key] = client
        self._clients_to_keys[client.id] = api_key

        return api_key

    def validate_key(self, api_key: str) -> bool:
        """
        Valida se API Key existe (admin ou cliente).

        Args:
            api_key: API Key a validar

        Returns:
            bool: True se valida
        """
        if not api_key:
            return False
        return self.is_admin_key(api_key) or self.is_client_key(api_key)

    def get_client_by_key(self, api_key: str) -> Optional[Client]:
        """
        Busca cliente pela API Key.

        Args:
            api_key: API Key fornecida

        Returns:
            Client: Cliente associado a key
            None: Se key invalida ou for key de admin
        """
        return self._keys_to_clients.get(api_key)

    def get_key_by_client_id(self, client_id: str) -> Optional[str]:
        """
        Busca API Key de um cliente.

        Args:
            client_id: ID do cliente

        Returns:
            str: API Key do cliente ou None
        """
        return self._clients_to_keys.get(client_id)

    def revoke_key(self, api_key: str) -> bool:
        """
        Revoga uma API Key de cliente.

        Args:
            api_key: API Key a revogar

        Returns:
            bool: True se revogada, False se nao existia
        """
        if api_key not in self._keys_to_clients:
            return False

        client = self._keys_to_clients[api_key]
        del self._keys_to_clients[api_key]
        del self._clients_to_keys[client.id]

        return True

    def list_all_keys(self) -> dict[str, str]:
        """
        Lista todas as API Keys de clientes.

        Returns:
            dict: Mapeamento client_id -> api_key
        """
        return self._clients_to_keys.copy()

    def __repr__(self):
        """Representacao string do gerenciador."""
        return f"APIKeysManager(clients={len(self._keys_to_clients)}, admin={'sim' if self._admin_key else 'nao'})"


# =============================================================================
# INSTANCIA SINGLETON
# =============================================================================

api_keys_manager = APIKeysManager()


# =============================================================================
# FUNCOES DE CONVENIENCIA
# =============================================================================

def register_client(client: Client) -> str:
    return api_keys_manager.register_client(client)


def validate_key(api_key: str) -> bool:
    return api_keys_manager.validate_key(api_key)


def is_admin_key(api_key: str) -> bool:
    return api_keys_manager.is_admin_key(api_key)


def is_client_key(api_key: str) -> bool:
    return api_keys_manager.is_client_key(api_key)


def get_client_by_key(api_key: str) -> Optional[Client]:
    return api_keys_manager.get_client_by_key(api_key)


def get_key_by_client_id(client_id: str) -> Optional[str]:
    return api_keys_manager.get_key_by_client_id(client_id)


def list_all_keys() -> dict[str, str]:
    return api_keys_manager.list_all_keys()


# =============================================================================
# INICIALIZACAO - REGISTRAR CLIENTES MOCK E ADMIN
# =============================================================================

def initialize_mock_keys():
    """
    Gera API Key de administrador e registra clientes mock.

    Exibe no console a key de admin separada das keys de clientes.
    """
    from app.infrastructure.repositories import cliente_repo
    from app.interface.api.converters import dict_to_client

    # Gera key de admin
    admin_key = api_keys_manager.generate_admin_key()

    print("\n" + "="*60)
    print("🔐 API KEY DO ADMINISTRADOR")
    print("="*60)
    print(f"Admin Key: {admin_key}")
    print("="*60)

    # Gera keys dos clientes
    clientes_dict = cliente_repo.listar_todos()
    clients = [dict_to_client(c) for c in clientes_dict]

    print("\n" + "="*60)
    print("🔑 API KEYS DOS CLIENTES")
    print("="*60)

    for client in clients:
        api_key = register_client(client)
        print(f"Cliente: {client.id:8} | Plano: {client.plan.nome:6} | Key: {api_key}")

    print("="*60 + "\n")
