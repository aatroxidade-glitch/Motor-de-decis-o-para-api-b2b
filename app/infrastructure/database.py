"""
Database - Conexao com SQLite

Responsavel por criar e gerenciar a conexao com o banco de dados SQLite.
O arquivo do banco fica em data/decisoes.db na raiz do projeto.

Autor: Cristovao Caldeira
Data: Março 2026
Projeto: Portfolio Python - Projeto 3/5 - Etapa 1
"""

import sqlite3
import pathlib
from typing import Optional

# Caminho do banco de dados
BASE_DIR = pathlib.Path(__file__).parent.parent.parent
DB_PATH = BASE_DIR / "data" / "decisoes.db"


def get_connection() -> sqlite3.Connection:
    """
    Cria e retorna uma conexao com o banco de dados.

    Returns:
        sqlite3.Connection: Conexao com o banco

    Configuracoes:
        - row_factory: retorna rows como dicionarios
        - check_same_thread: False para uso com FastAPI
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def get_db_path() -> pathlib.Path:
    """Retorna o caminho do arquivo do banco."""
    return DB_PATH


def create_table_clientes(conn):
    """
    Cria a tabela clientes se nao existir.

    Campos:
        id              - Identificador unico do cliente (ex: CLI_001)
        nome            - Nome da empresa/cliente
        plano           - Nome do plano contratado (Basic, Silver, Gold)
        requisicoes_usadas - Contador de requisicoes ja utilizadas
        criado_em       - Timestamp de criacao do registro
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id                  TEXT PRIMARY KEY,
            nome                TEXT NOT NULL,
            plano               TEXT NOT NULL,
            requisicoes_usadas  INTEGER NOT NULL DEFAULT 0,
            criado_em           TEXT NOT NULL
        )
    """)
    conn.commit()


def create_table_requisicoes(conn):
    """
    Cria a tabela requisicoes se nao existir.

    Campos:
        id          - UUID unico da requisicao
        client_id   - ID do cliente (FK para clientes)
        tipo        - Tipo de validacao executada
        payload_size - Tamanho do payload em bytes
        timestamp   - Momento em que a requisicao foi feita
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS requisicoes (
            id           TEXT PRIMARY KEY,
            client_id    TEXT NOT NULL,
            tipo         TEXT NOT NULL,
            payload_size INTEGER NOT NULL,
            timestamp    TEXT NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clientes(id)
        )
    """)
    conn.commit()


def create_table_decisoes(conn):
    """
    Cria a tabela decisoes se nao existir.

    Campos:
        id          - UUID unico da decisao
        request_id  - ID da requisicao (FK para requisicoes)
        aprovada    - 1 se aprovada, 0 se rejeitada
        motivo      - Justificativa da decisao
        timestamp   - Momento em que a decisao foi tomada
    """
    conn.execute("""
        CREATE TABLE IF NOT EXISTS decisoes (
            id          TEXT PRIMARY KEY,
            request_id  TEXT NOT NULL,
            aprovada    INTEGER NOT NULL,
            motivo      TEXT NOT NULL,
            timestamp   TEXT NOT NULL,
            FOREIGN KEY (request_id) REFERENCES requisicoes(id)
        )
    """)
    conn.commit()


def init_db():
    """
    Inicializa o banco de dados.

    Cria a pasta data/ se nao existir, abre a conexao
    e chama a criacao de todas as tabelas.
    """
    # Garante que a pasta data/ existe
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection()
    try:
        create_table_clientes(conn)
        create_table_requisicoes(conn)
        create_table_decisoes(conn)
        seed_clientes_mock(conn)
        print(f"Banco de dados inicializado em: {DB_PATH}")
    finally:
        conn.close()


def seed_clientes_mock(conn):
    """
    Popula o banco com os clientes mock se ainda nao existirem.

    Clientes mock:
        CLI_001 - TechStart LTDA    - Basic
        CLI_002 - DataFlow Solutions - Silver
        CLI_003 - FinTech Global Corp - Gold
    """
    from datetime import datetime

    clientes_mock = [
        ("CLI_001", "TechStart LTDA",      "Basic",  0, datetime.now().isoformat()),
        ("CLI_002", "DataFlow Solutions",   "Silver", 0, datetime.now().isoformat()),
        ("CLI_003", "FinTech Global Corp",  "Gold",   0, datetime.now().isoformat()),
    ]

    for cliente in clientes_mock:
        conn.execute("""
            INSERT OR IGNORE INTO clientes (id, nome, plano, requisicoes_usadas, criado_em)
            VALUES (?, ?, ?, ?, ?)
        """, cliente)

    conn.commit()
    print("Clientes mock inseridos no banco.")
