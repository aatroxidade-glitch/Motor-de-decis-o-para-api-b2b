"""
Decisao Repository - Persistencia de Decisoes

Responsavel por todas as operacoes de banco de dados
relacionadas a decisoes.

Autor: Cristovao Caldeira
Data: Marco 2026
Projeto: Portfolio Python - Projeto 3/5 - Etapa 2
"""

import sqlite3
from typing import Optional
from app.infrastructure.database import get_connection


class DecisaoRepository:
    """
    Repository para operacoes com a tabela decisoes.

    Responsabilidades:
        - Inserir nova decisao
        - Buscar decisao por requisicao
    """

    def __init__(self):
        pass

    def _get_conn(self) -> sqlite3.Connection:
        return get_connection()

    def inserir(self, decisao: dict) -> None:
        """
        Insere uma nova decisao no banco.

        Args:
            decisao: dict com os campos:
                - id
                - request_id
                - aprovada (1 ou 0)
                - motivo
                - timestamp
        """
        conn = self._get_conn()
        try:
            conn.execute(
                """
                INSERT INTO decisoes (id, request_id, aprovada, motivo, timestamp)
                VALUES (:id, :request_id, :aprovada, :motivo, :timestamp)
                """,
                decisao
            )
            conn.commit()
        finally:
            conn.close()

    def buscar_por_requisicao(self, request_id: str) -> Optional[dict]:
        """
        Busca a decisao de uma requisicao especifica.

        Args:
            request_id: ID da requisicao

        Returns:
            dict com dados da decisao ou None se nao encontrada
        """
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "SELECT * FROM decisoes WHERE request_id = ?",
                (request_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
