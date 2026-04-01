"""
Painel Administrativo - Motor de Decisao B2B

Interface administrativa para gerenciamento do sistema de decisao automatizado.
Acesso restrito a administradores do sistema.

Autor: Cristovao Caldeira
Data: Fevereiro 2026
Projeto: Portfolio Python - Projeto 2/5
"""

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from app.interface.api.schemas.request_schema import ValidateRequest
from app.interface.api.schemas.response_schema import (
    ValidateResponseApproved,
    ValidateResponseRejected,
    UsageInfo
)
from app.interface.api.schemas.error_schema import ErrorResponse, ErrorDetail
from app.interface.api.schemas.client_schema import (
    ClientInfo,
    ClientListResponse,
    ClientDetailResponse,
    PlanInfo,
    RequestHistoryEntry,
    RequestHistoryStats,
    ClientRequestsResponse
)
from app.infrastructure.repositories import (
    cliente_repo,
    requisicao_repo,
    decisao_repo
)
from app.interface.api.converters import dict_to_client
from app.interface.api.converters import (
    convert_to_domain_request,
    convert_decision_to_response
)
from app.interface.api.engine import get_engine
from app.interface.api.auth_middleware import authenticate_request
from app.interface.api.api_keys_manager import initialize_mock_keys
from app.interface.api.security_headers_middleware import add_security_headers


# =============================================================================
# SCHEMAS DE MONITORAMENTO
# =============================================================================

class StatusResponse(BaseModel):
    status: str
    version: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"status": "operational", "version": "2.0.0"}]
        }
    }


class StatusDetailResponse(BaseModel):
    status: str
    version: str
    message: str
    authentication: str
    docs: str

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "status": "operational",
                "version": "2.0.0",
                "message": "Motor de Decisao B2B - API Online",
                "authentication": "Admin Key required (X-API-Key header)",
                "docs": "http://localhost:8000/docs"
            }]
        }
    }


class HealthResponse(BaseModel):
    status: str
    environment: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"status": "healthy", "environment": "development"}]
        }
    }


class HealthDetailResponse(BaseModel):
    status: str
    environment: str
    version: str
    project: str

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "status": "healthy",
                "environment": "development",
                "version": "2.0.0",
                "project": "Motor de Decisao B2B"
            }]
        }
    }


# =============================================================================
# METADATA DA API
# =============================================================================

metadata = {
    "title": "Motor de Decisao B2B - Painel Administrativo",
    "description": """
<details>
<summary>🔐 Acesso Administrativo</summary>

Esta interface e exclusiva para administradores do sistema.

Utilize a **Admin Key** exibida no console do servidor ao inicializar:

X-API-Key: sua_admin_key_aqui

</details>

<details>
<summary>📋 Como Acessar</summary>

1. Inicie o servidor e copie a **Admin Key** do console
2. Clique no botao **Authorize** (canto superior direito)
3. Cole a Admin Key e clique em **Authorize**
4. Todos os endpoints administrativos estao liberados

</details>

<details>
<summary>👥 Clientes Cadastrados</summary>

As API Keys dos clientes sao exibidas no console do servidor.
Clientes utilizam suas keys diretamente no endpoint de validacao.

</details>

<details>
<summary>⚙️ Funcionalidades</summary>

* **Monitoramento**: Status e integridade da API
* **Gestao de Clientes**: Visualizar clientes, planos e uso
* **Historico**: Rastrear requisicoes e decisoes
* **Validacao**: Testar o motor de decisao diretamente

</details>

<details>
<summary>💼 Planos Disponíveis</summary>

* **Basic**: 100 requests/mes - validacao de CPF
* **Silver**: 500 requests/mes - CPF + Endereco
* **Gold**: 2.000 requests/mes - CPF + Endereco + Dados Bancarios

</details>
""",
    "version": "2.0.0",
    "contact": {
        "name": "Cristovao Caldeira",
        "email": "cristovao.caldeira@exemplo.com",
        "url": "https://github.com/cristovao-caldeira"
    },
    "license_info": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    "openapi_tags": [
        {"name": "Monitoramento", "description": "Status e integridade da API"},
        {"name": "Validacao", "description": "Testar o motor de decisao"},
        {"name": "Consultas", "description": "Gestao e consulta de clientes"},
        {"name": "Schemas", "description": "Referencia de schemas de request/response"},
        {"name": "Auditoria", "description": "Historico e estatisticas globais do sistema"}
    ]
}

app = FastAPI(**metadata)


# =============================================================================
# SECURITY SCHEME - SWAGGER UI
# =============================================================================

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "Coloque a key de acesso"
        }
    }

    openapi_schema["security"] = [{"APIKeyHeader": []}]

    schemas = openapi_schema.get("components", {}).get("schemas", {})
    for model in ["HTTPValidationError", "ValidationError"]:
        schemas.pop(model, None)

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# =============================================================================
# CORS
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)


# =============================================================================
# STARTUP EVENT
# =============================================================================

@app.on_event("startup")
async def startup_event():
    print("\n🚀 Iniciando Motor de Decisao B2B API...")
    from app.infrastructure.database import init_db
    init_db()
    initialize_mock_keys()
    print("✅ API pronta para receber requisicoes!")
    print("📚 Painel Administrativo: http://localhost:8000/docs")
    print("🔐 Use a Admin Key no botao Authorize para acessar\n")


# =============================================================================
# MIDDLEWARE
# =============================================================================

app.middleware("http")(add_security_headers)
app.middleware("http")(authenticate_request)


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail if isinstance(exc.detail, str) else "Error",
            message=exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            status_code=exc.status_code,
            timestamp=datetime.now().isoformat(),
            path=request.url.path
        ).model_dump(mode="json")
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        details.append(
            ErrorDetail(
                field=field if field else None,
                message=error["msg"],
                type=error["type"]
            )
        )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Validation Error",
            message="Os dados enviados sao invalidos",
            status_code=422,
            timestamp=datetime.now().isoformat(),
            path=request.url.path,
            details=details
        ).model_dump(mode="json")
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            message="Ocorreu um erro interno no servidor",
            status_code=500,
            timestamp=datetime.now().isoformat(),
            path=request.url.path
        ).model_dump(mode="json")
    )


# =============================================================================
# ENDPOINTS DE MONITORAMENTO
# =============================================================================

@app.get(
    "/",
    summary="Status da API",
    tags=["Monitoramento"],
    description="Retorna status atual da API. Use **?details=true** para informacoes completas."
)
def root(details: bool = False):
    if details:
        return StatusDetailResponse(
            status="operational",
            version="2.0.0",
            message="Motor de Decisao B2B - API Online",
            authentication="Admin Key required (X-API-Key header)",
            docs="http://localhost:8000/docs"
        )
    return StatusResponse(status="operational", version="2.0.0")


@app.get(
    "/health",
    summary="Health Check - Verificar integridade da API",
    tags=["Monitoramento"],
    description="Verifica se a API esta saudavel e operacional. Use **?details=true** para informacoes completas."
)
def health_check(details: bool = False):
    if details:
        return HealthDetailResponse(
            status="healthy",
            environment="development",
            version="2.0.0",
            project="Motor de Decisao B2B"
        )
    return HealthResponse(status="healthy", environment="development")


# =============================================================================
# ENDPOINT PRINCIPAL: VALIDACAO
# =============================================================================

@app.post(
    "/validate",
    response_model=ValidateResponseApproved | ValidateResponseRejected,
    status_code=status.HTTP_200_OK,
    tags=["Validacao"],
    summary="Validar dados de cliente",
    description="""
Processa validacao de dados baseada no plano contratado pelo cliente.

**Autenticacao:** Requer API Key do cliente no header X-API-Key.

**Fluxo:**
1. Valida API Key do cliente (middleware)
2. Identifica cliente pela API Key
3. Valida tipo de validacao permitido pelo plano
4. Valida estrutura e campos do payload
5. Verifica limites de uso
6. Registra requisicao no historico
7. Retorna decisao (aprovada ou rejeitada)
""",
    responses={
        200: {"description": "Validacao processada (aprovada ou rejeitada)"},
        401: {
            "description": "API Key ausente ou invalida",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authentication Required",
                        "message": "API Key nao fornecida. Envie no header X-API-Key",
                        "status_code": 401,
                        "timestamp": "2026-02-13T14:30:45.123456",
                        "path": "/validate"
                    }
                }
            }
        },
        403: {
            "description": "Acesso negado - requer key de cliente",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden",
                        "message": "Acesso negado. Este endpoint requer API Key de cliente.",
                        "status_code": 403,
                        "timestamp": "2026-02-13T14:30:45.123456",
                        "path": "/validate"
                    }
                }
            }
        },
        422: {
            "description": "Dados de entrada invalidos",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Validation Error",
                        "message": "Os dados enviados sao invalidos",
                        "status_code": 422,
                        "timestamp": "2026-02-13T14:30:45.123456",
                        "path": "/validate",
                        "details": [
                            {
                                "field": "tipo",
                                "message": "Deve comecar com validacao_",
                                "type": "value_error"
                            }
                        ]
                    }
                }
            }
        },
        429: {
            "description": "Rate limit excedido",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Rate Limit Exceeded",
                        "message": "Limite de 10 requisicoes por minuto excedido.",
                        "status_code": 429,
                        "timestamp": "2026-02-13T14:30:45.123456",
                        "path": "/validate",
                        "retry_after_seconds": 45
                    }
                }
            }
        },
        500: {
            "description": "Erro interno do servidor",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Internal Server Error",
                        "message": "Ocorreu um erro interno no servidor",
                        "status_code": 500,
                        "timestamp": "2026-02-13T14:30:45.123456",
                        "path": "/validate"
                    }
                }
            }
        }
    }
)
def validate(request: Request, validate_request: ValidateRequest):
    client = request.state.client
    domain_request = convert_to_domain_request(validate_request, client)
    engine = get_engine()
    decision = engine.evaluate(domain_request)

    # Persistir requisicao no banco
    requisicao_repo.inserir({
        "id": domain_request.id,
        "client_id": domain_request.client.id,
        "tipo": domain_request.payload.tipo,
        "payload_size": domain_request.payload.size(),
        "timestamp": domain_request.timestamp.isoformat()
    })

    # Persistir decisao no banco
    import uuid
    decisao_repo.inserir({
        "id": str(uuid.uuid4()),
        "request_id": domain_request.id,
        "aprovada": 1 if decision.aprovada else 0,
        "motivo": decision.motivo,
        "timestamp": decision.timestamp.isoformat()
    })

    # Atualizar uso do cliente no banco
    cliente_repo.atualizar_uso(domain_request.client.id)

    response = convert_decision_to_response(decision, domain_request)
    return response


# =============================================================================
# ENDPOINTS DE CONSULTA
# =============================================================================

@app.get(
    "/clients",
    response_model=ClientListResponse,
    status_code=status.HTTP_200_OK,
    tags=["Consultas"],
    summary="Listar todos os clientes",
    description="Retorna lista completa de clientes cadastrados com informacoes de uso e plano.",
    responses={
        401: {
            "description": "API Key ausente ou invalida",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authentication Required",
                        "message": "API Key nao fornecida. Envie no header X-API-Key",
                        "status_code": 401,
                        "timestamp": "2026-02-13T14:30:45.123456",
                        "path": "/clients"
                    }
                }
            }
        },
        403: {
            "description": "Acesso negado - requer key de admin",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden",
                        "message": "Acesso negado. Este endpoint requer API Key de administrador.",
                        "status_code": 403,
                        "timestamp": "2026-02-13T14:30:45.123456",
                        "path": "/clients"
                    }
                }
            }
        }
    }
)
def get_clients():
    clientes_dict = cliente_repo.listar_todos()
    clients = [dict_to_client(c) for c in clientes_dict]
    clients_info = [
        ClientInfo(
            id=client.id,
            nome=client.nome,
            plano=client.plan.nome,
            uso=client.requisicoes_usadas,
            limite=client.plan.max_requests,
            percentual_uso=client.usage_percentage()
        )
        for client in clients
    ]
    return ClientListResponse(total=len(clients_info), clientes=clients_info)


@app.get(
    "/clients/{client_id}",
    response_model=ClientDetailResponse,
    status_code=status.HTTP_200_OK,
    tags=["Consultas"],
    summary="Detalhes de um cliente",
    description="Retorna informacoes detalhadas de um cliente especifico incluindo plano completo e status de uso.",
    responses={
        401: {
            "description": "API Key ausente ou invalida",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authentication Required",
                        "message": "API Key nao fornecida. Envie no header X-API-Key",
                        "status_code": 401,
                        "timestamp": "2026-02-13T14:30:45.123456",
                        "path": "/clients/CLI_001"
                    }
                }
            }
        },
        403: {
            "description": "Acesso negado - requer key de admin",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden",
                        "message": "Acesso negado. Este endpoint requer API Key de administrador.",
                        "status_code": 403,
                        "timestamp": "2026-02-13T14:30:45.123456",
                        "path": "/clients/CLI_001"
                    }
                }
            }
        },
        404: {
            "description": "Cliente nao encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Cliente CLI_999 nao encontrado",
                        "message": "Cliente CLI_999 nao encontrado",
                        "status_code": 404,
                        "timestamp": "2026-02-13T14:30:45.123456",
                        "path": "/clients/CLI_999"
                    }
                }
            }
        },
        422: {
            "description": "Dados de entrada invalidos",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Validation Error",
                        "message": "Os dados enviados sao invalidos",
                        "status_code": 422,
                        "timestamp": "2026-02-13T14:30:45.123456",
                        "path": "/clients/CLI_001"
                    }
                }
            }
        }
    }
)
def get_client_detail(client_id: str):
    client_dict = cliente_repo.buscar_por_id(client_id)
    if not client_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente {client_id} nao encontrado"
        )
    client = dict_to_client(client_dict)
    plano_info = PlanInfo(
        nome=client.plan.nome,
        max_requests=client.plan.max_requests,
        max_payload_size=client.plan.max_payload_size,
        tipos_permitidos=client.plan.tipos_permitidos
    )
    return ClientDetailResponse(
        id=client.id,
        nome=client.nome,
        plano=plano_info,
        uso=client.requisicoes_usadas,
        requisicoes_restantes=client.remaining_quota(),
        percentual_uso=client.usage_percentage(),
        proximo_do_limite=client.plan.is_near_limit(client.requisicoes_usadas)
    )


@app.get(
    "/clients/{client_id}/requests",
    response_model=ClientRequestsResponse,
    status_code=status.HTTP_200_OK,
    tags=["Consultas"],
    summary="Historico de requisicoes de um cliente",
    description="Retorna historico completo de requisicoes processadas de um cliente com estatisticas de aprovacao.",
    responses={
        401: {
            "description": "API Key ausente ou invalida",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authentication Required",
                        "message": "API Key nao fornecida. Envie no header X-API-Key",
                        "status_code": 401,
                        "timestamp": "2026-02-13T14:30:45.123456",
                        "path": "/clients/CLI_001/requests"
                    }
                }
            }
        },
        403: {
            "description": "Acesso negado - requer key de admin",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Forbidden",
                        "message": "Acesso negado. Este endpoint requer API Key de administrador.",
                        "status_code": 403,
                        "timestamp": "2026-02-13T14:30:45.123456",
                        "path": "/clients/CLI_001/requests"
                    }
                }
            }
        },
        404: {
            "description": "Cliente nao encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Cliente CLI_999 nao encontrado",
                        "message": "Cliente CLI_999 nao encontrado",
                        "status_code": 404,
                        "timestamp": "2026-02-13T14:30:45.123456",
                        "path": "/clients/CLI_999/requests"
                    }
                }
            }
        },
        422: {
            "description": "Dados de entrada invalidos",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Validation Error",
                        "message": "Os dados enviados sao invalidos",
                        "status_code": 422,
                        "timestamp": "2026-02-13T14:30:45.123456",
                        "path": "/clients/CLI_001/requests"
                    }
                }
            }
        }
    }
)
def get_client_requests(client_id: str):
    client_dict = cliente_repo.buscar_por_id(client_id)
    if not client_dict:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente {client_id} nao encontrado"
        )
    client = dict_to_client(client_dict)
    history = requisicao_repo.buscar_por_cliente(client_id)
    total = len(history)
    aprovadas = 0
    requisicoes = []
    for entry in history:
        decisao = decisao_repo.buscar_por_requisicao(entry["id"])
        aprovada = decisao["aprovada"] == 1 if decisao else False
        motivo = decisao["motivo"] if decisao else ""
        if aprovada:
            aprovadas += 1
        requisicoes.append(
            RequestHistoryEntry(
                request_id=entry["id"],
                client_id=entry["client_id"],
                tipo=entry["tipo"],
                aprovada=aprovada,
                motivo=motivo,
                timestamp=entry["timestamp"],
                payload_size=entry["payload_size"]
            )
        )
    rejeitadas = total - aprovadas
    taxa_aprovacao = (aprovadas / total * 100) if total > 0 else 0.0
    history_stats = RequestHistoryStats(
        total=total,
        aprovadas=aprovadas,
        rejeitadas=rejeitadas,
        taxa_aprovacao=taxa_aprovacao
    )
    return ClientRequestsResponse(
        client_id=client.id,
        client_nome=client.nome,
        stats=history_stats,
        requisicoes=requisicoes
    )


# =============================================================================
# ENDPOINTS DE AUDITORIA
# =============================================================================

from app.interface.api.schemas.audit_schema import AuditEntry, AuditListResponse, AuditStats

@app.get(
    "/audit",
    response_model=AuditListResponse,
    status_code=200,
    tags=["Auditoria"],
    summary="Historico completo de todas as requisicoes",
    description="""
Retorna historico completo de todas as requisicoes do sistema com dados do cliente e decisao.

**Filtros opcionais:**
- **aprovada**: true ou false
- **tipo**: validacao_cpf, validacao_endereco, validacao_dados_bancarios
- **data_inicio**: formato YYYY-MM-DD
- **data_fim**: formato YYYY-MM-DD
""",
    responses={
        401: {"description": "API Key ausente ou invalida"},
        403: {"description": "Acesso negado - requer key de admin"},
        422: {"description": "Dados de entrada invalidos"}
    }
)
def get_audit(
    aprovada: str = None,
    tipo: str = None,
    data_inicio: str = None,
    data_fim: str = None
):
    registros = requisicao_repo.listar_todas_com_decisoes(
        aprovada=aprovada,
        tipo=tipo,
        data_inicio=data_inicio,
        data_fim=data_fim
    )
    entries = [
        AuditEntry(
            request_id=r["request_id"],
            client_id=r["client_id"],
            client_nome=r["client_nome"],
            tipo=r["tipo"],
            aprovada=r["aprovada"] == 1 if r["aprovada"] is not None else False,
            motivo=r["motivo"] if r["motivo"] else "",
            timestamp=r["timestamp"],
            payload_size=r["payload_size"]
        )
        for r in registros
    ]
    return AuditListResponse(total=len(entries), registros=entries)


@app.get(
    "/audit/stats",
    response_model=AuditStats,
    status_code=200,
    tags=["Auditoria"],
    summary="Estatisticas globais do sistema",
    description="Retorna estatisticas globais do sistema — total de requisicoes, taxa de aprovacao e cliente mais ativo.",
    responses={
        401: {"description": "API Key ausente ou invalida"},
        403: {"description": "Acesso negado - requer key de admin"},
        422: {"description": "Dados de entrada invalidos"}
    }
)
def get_audit_stats():
    stats = requisicao_repo.get_stats_globais()
    return AuditStats(**stats)


# =============================================================================
# ENDPOINTS DE SCHEMAS
# =============================================================================

@app.get(
    "/schemas/request",
    response_model=ValidateRequest,
    tags=["Schemas"],
    summary="Exemplo de ValidateRequest",
    description="Exibe a estrutura esperada no body do POST /validate. Use como referencia ao enviar requisicoes.",
    responses={
        401: {
            "description": "API Key ausente ou invalida",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authentication Required",
                        "message": "API Key nao fornecida. Envie no header X-API-Key",
                        "status_code": 401,
                        "timestamp": "2026-02-13T14:30:45.123456",
                        "path": "/schemas/request"
                    }
                }
            }
        }
    }
)
def get_request_schema():
    return ValidateRequest(
        tipo="validacao_cpf",
        dados={"cpf": "12345678900", "nome": "Joao Silva"}
    )


@app.get(
    "/schemas/response/approved",
    response_model=ValidateResponseApproved,
    tags=["Schemas"],
    summary="Exemplo de ValidateResponseApproved",
    description="Exibe a estrutura retornada quando uma validacao e aprovada pelo motor de decisao.",
    responses={
        401: {
            "description": "API Key ausente ou invalida",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authentication Required",
                        "message": "API Key nao fornecida. Envie no header X-API-Key",
                        "status_code": 401,
                        "timestamp": "2026-02-13T14:30:45.123456",
                        "path": "/schemas/response/approved"
                    }
                }
            }
        }
    }
)
def get_approved_schema():
    return ValidateResponseApproved(
        request_id="550e8400-e29b-41d4-a716-446655440000",
        client_id="CLI_001",
        tipo="validacao_cpf",
        motivo="Requisicao autorizada",
        timestamp=datetime.now().isoformat(),
        usage=UsageInfo(used=46, limit=500, percentage=9.2)
    )


@app.get(
    "/schemas/response/rejected",
    response_model=ValidateResponseRejected,
    tags=["Schemas"],
    summary="Exemplo de ValidateResponseRejected",
    description="Exibe a estrutura retornada quando uma validacao e rejeitada pelo motor de decisao.",
    responses={
        401: {
            "description": "API Key ausente ou invalida",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authentication Required",
                        "message": "API Key nao fornecida. Envie no header X-API-Key",
                        "status_code": 401,
                        "timestamp": "2026-02-13T14:30:45.123456",
                        "path": "/schemas/response/rejected"
                    }
                }
            }
        }
    }
)
def get_rejected_schema():
    return ValidateResponseRejected(
        request_id="660f9511-f3ac-52e5-b827-557766551111",
        client_id="CLI_001",
        tipo="validacao_endereco",
        motivo="Plano Basic nao permite este tipo",
        timestamp=datetime.now().isoformat(),
        suggestion="Faca upgrade para Silver"
    )
