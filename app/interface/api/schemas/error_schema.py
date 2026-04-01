"""
Schema de Error - Respostas de Erro da API

Define a estrutura de dados retornada quando ocorrem erros
na API (validação, autenticação, não encontrado, etc).

Autor: [Seu Nome]
Data: Janeiro 2026
Projeto: Portfólio Python - Projeto 2/5
"""

from pydantic import BaseModel, Field
from datetime import datetime


class ErrorDetail(BaseModel):
    """
    Detalhes específicos de um erro.
    
    Attributes:
        field: Campo que causou o erro (opcional)
        message: Mensagem descritiva do erro
        type: Tipo de erro (validation, not_found, etc)
    """
    
    field: str | None = Field(
        default=None,
        description="Campo que causou o erro",
        json_schema_extra={"example": "client_id"}
    )
    
    message: str = Field(
        ...,
        description="Mensagem descritiva do erro",
        json_schema_extra={"example": "Campo obrigatório ausente"}
    )
    
    type: str = Field(
        ...,
        description="Tipo do erro",
        json_schema_extra={"example": "missing_field"}
    )


class ErrorResponse(BaseModel):
    """
    Response padrão para erros da API.
    
    Estrutura consistente para comunicar erros ao cliente,
    incluindo código HTTP, mensagem principal e detalhes específicos.
    
    Attributes:
        error: Título do erro (curto)
        message: Mensagem principal explicativa
        status_code: Código HTTP do erro
        timestamp: Momento em que o erro ocorreu
        path: Endpoint que causou o erro
        details: Lista de detalhes específicos (opcional)
    """
    
    error: str = Field(
        ...,
        description="Título do erro",
        json_schema_extra={"example": "Validation Error"}
    )
    
    message: str = Field(
        ...,
        description="Mensagem principal do erro",
        json_schema_extra={"example": "Os dados enviados são inválidos"}
    )
    
    status_code: int = Field(
        ...,
        ge=400,
        le=599,
        description="Código HTTP do erro",
        json_schema_extra={"example": 422}
    )
    
    timestamp: datetime = Field(
        ...,
        description="Momento do erro (ISO 8601)",
        json_schema_extra={"example": "2026-01-25T14:30:45.123456"}
    )
    
    path: str = Field(
        ...,
        description="Endpoint que causou o erro",
        json_schema_extra={"example": "/validate"}
    )
    
    details: list[ErrorDetail] | None = Field(
        default=None,
        description="Detalhes específicos dos erros",
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "error": "Validation Error",
                    "message": "Os dados enviados são inválidos",
                    "status_code": 422,
                    "timestamp": "2026-01-25T14:30:45.123456",
                    "path": "/validate",
                    "details": [
                        {
                            "field": "client_id",
                            "message": "Campo obrigatório ausente",
                            "type": "missing_field"
                        },
                        {
                            "field": "tipo",
                            "message": "Deve começar com 'validacao_'",
                            "type": "value_error"
                        }
                    ]
                },
                {
                    "error": "Not Found",
                    "message": "Cliente não encontrado",
                    "status_code": 404,
                    "timestamp": "2026-01-25T14:35:20.987654",
                    "path": "/clients/CLI_999",
                    "details": None
                },
                {
                    "error": "Unauthorized",
                    "message": "API Key inválida ou ausente",
                    "status_code": 401,
                    "timestamp": "2026-01-25T14:40:10.123789",
                    "path": "/validate",
                    "details": None
                }
            ]
        }
    }
