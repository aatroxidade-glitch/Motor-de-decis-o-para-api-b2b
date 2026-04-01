"""
Requisicao Repository - Persistencia de Requisicoes

Responsavel por todas as operacoes de banco de dados
relacionadas a requisicoes.

Autor: Cristovao Caldeira
Data: Marco 2026
Projeto: Portfolio Python - Projeto 3/5 - Etapa 2
"""

import sqlite3
from typing import Optional
from app.infrastructure.database import get_connection


class RequisicaoRepository:
    """
    Repository para operacoes com a tabela requisicoes.

    Responsabilidades:
        - Inserir nova requisicao
        - Buscar requisicoes por cliente
    """

    def __init__(self):
        pass

    def _get_conn(self) -> sqlite3.Connection:
        return get_connection()

    def inserir(self, requisicao: dict) -> None:
        """
        Insere uma nova requisicao no banco.

        Args:
            requisicao: dict com os campos:
                - id
                - client_id
                - tipo
                - payload_size
                - timestamp
        """
        conn = self._get_conn()
        try:
            conn.execute(
                """
                INSERT INTO requisicoes (id, client_id, tipo, payload_size, timestamp)
                VALUES (:id, :client_id, :tipo, :payload_size, :timestamp)
                """,
                requisicao
            )
            conn.commit()
        finally:
            conn.close()

    def buscar_por_cliente(self, client_id: str) -> list[dict]:
        """
        Busca todas as requisicoes de um cliente.

        Args:
            client_id: ID do cliente

        Returns:
            Lista de dicts com as requisicoes do cliente
            ordenadas da mais recente para a mais antiga
        """
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                """
                SELECT * FROM requisicoes
                WHERE client_id = ?
                ORDER BY timestamp DESC
                """,
                (client_id,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def listar_todas_com_decisoes(self, aprovada: str = None, tipo: str = None, data_inicio: str = None, data_fim: str = None) -> list[dict]:
        """
        Lista todas as requisicoes com dados da decisao e do cliente.
        Suporta filtros opcionais por status, tipo e data.

        Args:
            aprovada: "true" ou "false" para filtrar por status
            tipo: tipo de validacao para filtrar
            data_inicio: data inicial no formato YYYY-MM-DD
            data_fim: data final no formato YYYY-MM-DD

        Returns:
            Lista de dicts com dados completos de auditoria
        """
        conn = self._get_conn()
        try:
            query = """
                SELECT
                    r.id as request_id,
                    r.client_id,
                    c.nome as client_nome,
                    r.tipo,
                    d.aprovada,
                    d.motivo,
                    r.timestamp,
                    r.payload_size
                FROM requisicoes r
                JOIN clientes c ON r.client_id = c.id
                LEFT JOIN decisoes d ON d.request_id = r.id
                WHERE 1=1
            """
            params = []

            if aprovada is not None:
                query += " AND d.aprovada = ?"
                params.append(1 if aprovada == "true" else 0)

            if tipo is not None:
                query += " AND r.tipo = ?"
                params.append(tipo)

            if data_inicio is not None:
                query += " AND r.timestamp >= ?"
                params.append(data_inicio)

            if data_fim is not None:
                query += " AND r.timestamp <= ?"
                params.append(data_fim + "T23:59:59")

            query += " ORDER BY r.timestamp DESC"

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_stats_globais(self) -> dict:
        """
        Retorna estatisticas globais do sistema.

        Returns:
            dict com total, aprovadas, rejeitadas, taxa e cliente mais ativo
        """
        conn = self._get_conn()
        try:
            # Total e aprovadas
            cursor = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN d.aprovada = 1 THEN 1 ELSE 0 END) as aprovadas
                FROM requisicoes r
                LEFT JOIN decisoes d ON d.request_id = r.id
            """)
            row = dict(cursor.fetchone())
            total = row["total"] or 0
            aprovadas = row["aprovadas"] or 0
            rejeitadas = total - aprovadas
            taxa = (aprovadas / total * 100) if total > 0 else 0.0

            # Cliente mais ativo
            cursor = conn.execute("""
                SELECT client_id, COUNT(*) as total
                FROM requisicoes
                GROUP BY client_id
                ORDER BY total DESC
                LIMIT 1
            """)
            row_ativo = cursor.fetchone()
            cliente_mais_ativo = dict(row_ativo)["client_id"] if row_ativo else "N/A"

            return {
                "total_requisicoes": total,
                "total_aprovadas": aprovadas,
                "total_rejeitadas": rejeitadas,
                "taxa_aprovacao": round(taxa, 2),
                "cliente_mais_ativo": cliente_mais_ativo
            }
        finally:
            conn.close()

    def listar_todas_com_decisoes(self, aprovada: str = None, tipo: str = None, data_inicio: str = None, data_fim: str = None) -> list[dict]:
        """
        Lista todas as requisicoes com dados da decisao e do cliente.
        Suporta filtros opcionais por status, tipo e data.

        Args:
            aprovada: "true" ou "false" para filtrar por status
            tipo: tipo de validacao para filtrar
            data_inicio: data inicial no formato YYYY-MM-DD
            data_fim: data final no formato YYYY-MM-DD

        Returns:
            Lista de dicts com dados completos de auditoria
        """
        conn = self._get_conn()
        try:
            query = """
                SELECT
                    r.id as request_id,
                    r.client_id,
                    c.nome as client_nome,
                    r.tipo,
                    d.aprovada,
                    d.motivo,
                    r.timestamp,
                    r.payload_size
                FROM requisicoes r
                JOIN clientes c ON r.client_id = c.id
                LEFT JOIN decisoes d ON d.request_id = r.id
                WHERE 1=1
            """
            params = []

            if aprovada is not None:
                query += " AND d.aprovada = ?"
                params.append(1 if aprovada == "true" else 0)

            if tipo is not None:
                query += " AND r.tipo = ?"
                params.append(tipo)

            if data_inicio is not None:
                query += " AND r.timestamp >= ?"
                params.append(data_inicio)

            if data_fim is not None:
                query += " AND r.timestamp <= ?"
                params.append(data_fim + "T23:59:59")

            query += " ORDER BY r.timestamp DESC"

            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_stats_globais(self) -> dict:
        """
        Retorna estatisticas globais do sistema.

        Returns:
            dict com total, aprovadas, rejeitadas, taxa e cliente mais ativo
        """
        conn = self._get_conn()
        try:
            # Total e aprovadas
            cursor = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN d.aprovada = 1 THEN 1 ELSE 0 END) as aprovadas
                FROM requisicoes r
                LEFT JOIN decisoes d ON d.request_id = r.id
            """)
            row = dict(cursor.fetchone())
            total = row["total"] or 0
            aprovadas = row["aprovadas"] or 0
            rejeitadas = total - aprovadas
            taxa = (aprovadas / total * 100) if total > 0 else 0.0

            # Cliente mais ativo
            cursor = conn.execute("""
                SELECT client_id, COUNT(*) as total
                FROM requisicoes
                GROUP BY client_id
                ORDER BY total DESC
                LIMIT 1
            """)
            row_ativo = cursor.fetchone()
            cliente_mais_ativo = dict(row_ativo)["client_id"] if row_ativo else "N/A"

            return {
                "total_requisicoes": total,
                "total_aprovadas": aprovadas,
                "total_rejeitadas": rejeitadas,
                "taxa_aprovacao": round(taxa, 2),
                "cliente_mais_ativo": cliente_mais_ativo
            }
        finally:
            conn.close()
