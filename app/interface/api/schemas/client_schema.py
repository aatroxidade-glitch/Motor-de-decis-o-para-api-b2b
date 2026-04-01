"""
Schemas de Cliente - Respostas de Consulta

Define estruturas de dados para endpoints de consulta de clientes.

Autor: Cristovao Caldeira
Data: Fevereiro 2026
Projeto: Portfolio Python - Projeto 2/5 - Etapa 4
"""

from pydantic import BaseModel, Field
from datetime import datetime


class ClientInfo(BaseModel):
    id: str = Field(..., description="ID unico do cliente", json_schema_extra={"example": "CLI_001"})
    nome: str = Field(..., description="Nome da empresa/cliente", json_schema_extra={"example": "TechStart LTDA"})
    plano: str = Field(..., description="Nome do plano contratado", json_schema_extra={"example": "Basic"})
    uso: int = Field(..., ge=0, description="Requisicoes ja utilizadas", json_schema_extra={"example": 45})
    limite: int = Field(..., gt=0, description="Limite total de requisicoes", json_schema_extra={"example": 100})
    percentual_uso: float = Field(..., ge=0.0, le=100.0, description="Percentual de uso (0-100)", json_schema_extra={"example": 45.0})

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "CLI_001",
                    "nome": "TechStart LTDA",
                    "plano": "Basic",
                    "uso": 45,
                    "limite": 100,
                    "percentual_uso": 45.0
                }
            ]
        }
    }


class ClientListResponse(BaseModel):
    total: int = Field(..., ge=0, description="Total de clientes cadastrados", json_schema_extra={"example": 3})
    clientes: list[ClientInfo] = Field(..., description="Lista de clientes")


class PlanInfo(BaseModel):
    nome: str = Field(..., description="Nome do plano", json_schema_extra={"example": "Basic"})
    max_requests: int = Field(..., description="Limite maximo de requisicoes", json_schema_extra={"example": 100})
    max_payload_size: int = Field(..., description="Tamanho maximo de payload em bytes", json_schema_extra={"example": 1024})
    tipos_permitidos: list[str] = Field(..., description="Tipos de validacao permitidos", json_schema_extra={"example": ["validacao_cpf"]})

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "nome": "Basic",
                    "max_requests": 100,
                    "max_payload_size": 1024,
                    "tipos_permitidos": ["validacao_cpf"]
                }
            ]
        }
    }


class ClientDetailResponse(BaseModel):
    id: str = Field(..., description="ID unico do cliente", json_schema_extra={"example": "CLI_001"})
    nome: str = Field(..., description="Nome da empresa/cliente", json_schema_extra={"example": "TechStart LTDA"})
    plano: PlanInfo = Field(..., description="Informacoes detalhadas do plano")
    uso: int = Field(..., ge=0, description="Requisicoes ja utilizadas", json_schema_extra={"example": 45})
    requisicoes_restantes: int = Field(..., ge=0, description="Requisicoes ainda disponiveis", json_schema_extra={"example": 55})
    percentual_uso: float = Field(..., ge=0.0, le=100.0, description="Percentual de uso (0-100)", json_schema_extra={"example": 45.0})
    proximo_do_limite: bool = Field(..., description="True se uso >= 80% do limite", json_schema_extra={"example": False})

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "CLI_001",
                    "nome": "TechStart LTDA",
                    "plano": {
                        "nome": "Basic",
                        "max_requests": 100,
                        "max_payload_size": 1024,
                        "tipos_permitidos": ["validacao_cpf"]
                    },
                    "uso": 45,
                    "requisicoes_restantes": 55,
                    "percentual_uso": 45.0,
                    "proximo_do_limite": False
                }
            ]
        }
    }


class RequestHistoryEntry(BaseModel):
    request_id: str = Field(..., description="ID unico da requisicao (UUID)", json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"})
    client_id: str = Field(..., description="ID do cliente", json_schema_extra={"example": "CLI_001"})
    tipo: str = Field(..., description="Tipo de validacao executada", json_schema_extra={"example": "validacao_cpf"})
    aprovada: bool = Field(..., description="True se aprovada, False se rejeitada", json_schema_extra={"example": True})
    motivo: str = Field(..., description="Motivo da decisao", json_schema_extra={"example": "Requisicao autorizada: validacao_cpf"})
    timestamp: datetime = Field(..., description="Momento da decisao", json_schema_extra={"example": "2026-02-09T14:30:45.123456"})
    payload_size: int = Field(..., ge=0, description="Tamanho do payload em bytes", json_schema_extra={"example": 128})


class RequestHistoryStats(BaseModel):
    total: int = Field(..., ge=0, description="Total de requisicoes", json_schema_extra={"example": 10})
    aprovadas: int = Field(..., ge=0, description="Total de aprovacoes", json_schema_extra={"example": 7})
    rejeitadas: int = Field(..., ge=0, description="Total de rejeicoes", json_schema_extra={"example": 3})
    taxa_aprovacao: float = Field(..., ge=0.0, le=100.0, description="Taxa de aprovacao (%)", json_schema_extra={"example": 70.0})


class ClientRequestsResponse(BaseModel):
    client_id: str = Field(..., description="ID do cliente", json_schema_extra={"example": "CLI_001"})
    client_nome: str = Field(..., description="Nome do cliente", json_schema_extra={"example": "TechStart LTDA"})
    stats: RequestHistoryStats = Field(..., description="Estatisticas do historico")
    requisicoes: list[RequestHistoryEntry] = Field(..., description="Lista de requisicoes processadas")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "client_id": "CLI_001",
                    "client_nome": "TechStart LTDA",
                    "stats": {
                        "total": 2,
                        "aprovadas": 1,
                        "rejeitadas": 1,
                        "taxa_aprovacao": 50.0
                    },
                    "requisicoes": [
                        {
                            "request_id": "550e8400-e29b-41d4-a716-446655440000",
                            "client_id": "CLI_001",
                            "tipo": "validacao_cpf",
                            "aprovada": True,
                            "motivo": "Requisicao autorizada: validacao_cpf",
                            "timestamp": "2026-02-09T14:30:45.123456",
                            "payload_size": 128
                        },
                        {
                            "request_id": "660f9511-f3ac-52e5-b827-557766551111",
                            "client_id": "CLI_001",
                            "tipo": "validacao_endereco",
                            "aprovada": False,
                            "motivo": "Plano Basic nao permite validacao do tipo validacao_endereco",
                            "timestamp": "2026-02-09T14:35:20.654321",
                            "payload_size": 156
                        }
                    ]
                }
            ]
        }
    }
