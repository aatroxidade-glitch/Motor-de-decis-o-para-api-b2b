"""
Cliente Repository - Persistencia de Clientes

Responsavel por todas as operacoes de banco de dados
relacionadas a clientes.

Autor: Cristovao Caldeira
Data: Marco 2026
Projeto: Portfolio Python - Projeto 3/5 - Etapa 2
"""

import sqlite3
from typing import Optional
from app.infrastructure.database import get_connection


class ClienteRepository:
    """
    Repository para operacoes com a tabela clientes.

    Responsabilidades:
        - Buscar cliente por ID
        - Listar todos os clientes
        - Atualizar uso do cliente
    """

    def __init__(self):
        pass

    def _get_conn(self) -> sqlite3.Connection:
        return get_connection()

    def buscar_por_id(self, client_id: str) -> Optional[dict]:
        """
        Busca um cliente pelo ID.

        Args:
            client_id: ID do cliente (ex: CLI_001)

        Returns:
            dict com dados do cliente ou None se nao encontrado
        """
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "SELECT * FROM clientes WHERE id = ?",
                (client_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def listar_todos(self) -> list[dict]:
        """
        Lista todos os clientes cadastrados.

        Returns:
            Lista de dicts com dados de todos os clientes
        """
        conn = self._get_conn()
        try:
            cursor = conn.execute("SELECT * FROM clientes")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def atualizar_uso(self, client_id: str) -> None:
        """
        Incrementa em 1 o contador de requisicoes_usadas do cliente.

        Args:
            client_id: ID do cliente a atualizar
        """
        conn = self._get_conn()
        try:
            conn.execute(
                "UPDATE clientes SET requisicoes_usadas = requisicoes_usadas + 1 WHERE id = ?",
                (client_id,)
            )
            conn.commit()
        finally:
            conn.close()
