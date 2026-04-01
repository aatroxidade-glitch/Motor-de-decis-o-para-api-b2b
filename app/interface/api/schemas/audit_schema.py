"""
Audit Schema - Schemas de Auditoria

Define estruturas de dados para os endpoints de auditoria do sistema.

Autor: Cristovao Caldeira
Data: Marco 2026
Projeto: Portfolio Python - Projeto 3/5 - Etapa 5
"""

from pydantic import BaseModel, Field
from datetime import datetime


class AuditEntry(BaseModel):
    request_id: str = Field(..., description="ID unico da requisicao")
    client_id: str = Field(..., description="ID do cliente")
    client_nome: str = Field(..., description="Nome do cliente")
    tipo: str = Field(..., description="Tipo de validacao executada")
    aprovada: bool = Field(..., description="True se aprovada, False se rejeitada")
    motivo: str = Field(..., description="Motivo da decisao")
    timestamp: str = Field(..., description="Momento da requisicao")
    payload_size: int = Field(..., description="Tamanho do payload em bytes")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                    "client_id": "CLI_001",
                    "client_nome": "TechStart LTDA",
                    "tipo": "validacao_cpf",
                    "aprovada": True,
                    "motivo": "Requisicao autorizada: validacao_cpf",
                    "timestamp": "2026-03-25T16:35:14.125160",
                    "payload_size": 101
                }
            ]
        }
    }


class AuditListResponse(BaseModel):
    total: int = Field(..., description="Total de registros retornados")
    registros: list[AuditEntry] = Field(..., description="Lista de registros de auditoria")


class AuditStats(BaseModel):
    total_requisicoes: int = Field(..., description="Total de requisicoes no sistema")
    total_aprovadas: int = Field(..., description="Total de requisicoes aprovadas")
    total_rejeitadas: int = Field(..., description="Total de requisicoes rejeitadas")
    taxa_aprovacao: float = Field(..., description="Taxa de aprovacao global (%)")
    cliente_mais_ativo: str = Field(..., description="ID do cliente com mais requisicoes")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total_requisicoes": 10,
                    "total_aprovadas": 8,
                    "total_rejeitadas": 2,
                    "taxa_aprovacao": 80.0,
                    "cliente_mais_ativo": "CLI_001"
                }
            ]
        }
    }
