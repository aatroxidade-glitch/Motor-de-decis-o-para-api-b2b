"""
Repositories - Instancias Singleton

Instancias compartilhadas dos repositories para uso na API.

Autor: Cristovao Caldeira
Data: Marco 2026
Projeto: Portfolio Python - Projeto 3/5 - Etapa 3
"""

from app.infrastructure.cliente_repository import ClienteRepository
from app.infrastructure.requisicao_repository import RequisicaoRepository
from app.infrastructure.decisao_repository import DecisaoRepository

# Instancias singleton
cliente_repo = ClienteRepository()
requisicao_repo = RequisicaoRepository()
decisao_repo = DecisaoRepository()
