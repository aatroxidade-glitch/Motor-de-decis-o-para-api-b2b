"""
Schemas de Response - Validação de Saída da API

Define a estrutura de dados que a API retorna para o cliente
após processar uma validação.

Autor: Cristóvão Caldeira
Data: Fevereiro 2026
Projeto: Portfólio Python - Projeto 2/5
"""

from pydantic import BaseModel, Field
from datetime import datetime


class UsageInfo(BaseModel):
    used: int = Field(..., ge=0, description="Requisições já utilizadas", json_schema_extra={"example": 46})
    limit: int = Field(..., gt=0, description="Limite total do plano", json_schema_extra={"example": 500})
    percentage: float = Field(..., ge=0.0, le=100.0, description="Percentual de uso", json_schema_extra={"example": 9.2})


class ValidateResponseApproved(BaseModel):
    status: str = Field(default="approved", description="Status da validação", json_schema_extra={"example": "approved"})
    request_id: str = Field(..., description="ID único da requisição (UUID)", json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"})
    client_id: str = Field(..., description="ID do cliente", json_schema_extra={"example": "CLI_001"})
    tipo: str = Field(..., description="Tipo de validação executada", json_schema_extra={"example": "validacao_cpf"})
    motivo: str = Field(..., description="Justificativa da aprovação", json_schema_extra={"example": "Requisição autorizada: validacao_cpf"})
    timestamp: datetime = Field(..., description="Momento da decisão (ISO 8601)", json_schema_extra={"example": "2026-01-25T14:30:45.123456"})
    usage: UsageInfo = Field(..., description="Informações de uso do cliente")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "approved",
                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                    "client_id": "CLI_001",
                    "tipo": "validacao_cpf",
                    "motivo": "Requisição autorizada: validacao_cpf",
                    "timestamp": "2026-01-25T14:30:45.123456",
                    "usage": {
                        "used": 46,
                        "limit": 500,
                        "percentage": 9.2
                    }
                }
            ]
        }
    }


class ValidateResponseRejected(BaseModel):
    status: str = Field(default="rejected", description="Status da validação", json_schema_extra={"example": "rejected"})
    request_id: str = Field(..., description="ID único da requisição (UUID)", json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"})
    client_id: str = Field(..., description="ID do cliente", json_schema_extra={"example": "CLI_001"})
    tipo: str = Field(..., description="Tipo de validação tentada", json_schema_extra={"example": "validacao_endereco"})
    motivo: str = Field(..., description="Justificativa detalhada da rejeição", json_schema_extra={"example": "Plano Basic não permite validação do tipo validacao_endereco"})
    timestamp: datetime = Field(..., description="Momento da decisão (ISO 8601)", json_schema_extra={"example": "2026-01-25T14:30:45.123456"})
    suggestion: str | None = Field(default=None, description="Sugestão de ação para resolver o problema", json_schema_extra={"example": "Faça upgrade para o plano Silver para desbloquear validação de endereço"})

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "rejected",
                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                    "client_id": "CLI_001",
                    "tipo": "validacao_endereco",
                    "motivo": "Plano Basic não permite validação do tipo validacao_endereco",
                    "timestamp": "2026-01-25T14:30:45.123456",
                    "suggestion": "Faça upgrade para o plano Silver para desbloquear validação de endereço"
                },
                {
                    "status": "rejected",
                    "request_id": "660f9511-f3ac-52e5-b827-557766551111",
                    "client_id": "CLI_002",
                    "tipo": "validacao_cpf",
                    "motivo": "Limite de requisições excedido",
                    "timestamp": "2026-01-25T15:45:30.654321",
                    "suggestion": "Aguarde renovação mensal ou faça upgrade de plano"
                }
            ]
        }
    }
