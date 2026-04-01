"""
Middleware de Autenticacao - API Key

Intercepta todas as requisicoes e valida API Key no header.
Distingue entre autenticacao de administrador e de cliente.

Autor: Cristovao Caldeira
Data: Fevereiro 2026
Projeto: Portfolio Python - Projeto 2/5 - Etapa Administrativa
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Callable

from app.interface.api.api_keys_manager import (
    validate_key,
    is_admin_key,
    is_client_key,
    get_client_by_key
)
from app.interface.api.rate_limiter import check_rate_limit, get_reset_time


# =============================================================================
# CONFIGURACAO DE ENDPOINTS
# =============================================================================

PUBLIC_ENDPOINTS = [
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
]

ADMIN_ENDPOINTS = [
    "/clients",
    "/schemas",
    "/audit",
]

CLIENT_ENDPOINTS = [
    "/validate",
]


def is_options_request(request: Request) -> bool:
    return request.method == "OPTIONS"


def is_public_endpoint(path: str) -> bool:
    for public_path in PUBLIC_ENDPOINTS:
        if path == public_path or path.startswith(f"{public_path}/"):
            return True
    return False


def is_admin_endpoint(path: str) -> bool:
    for admin_path in ADMIN_ENDPOINTS:
        if path == admin_path or path.startswith(f"{admin_path}/"):
            return True
    return False


def is_client_endpoint(path: str) -> bool:
    for client_path in CLIENT_ENDPOINTS:
        if path == client_path or path.startswith(f"{client_path}/"):
            return True
    return False


# =============================================================================
# MIDDLEWARE DE AUTENTICACAO + RATE LIMITING
# =============================================================================

async def authenticate_request(request: Request, call_next: Callable):
    """
    Middleware que valida API Key e aplica rate limiting.

    Fluxo:
        1. Endpoints publicos e OPTIONS passam direto
        2. Extrai API Key do header
        3. Endpoints administrativos exigem key de admin
        4. Endpoints de cliente exigem key de cliente
        5. Aplica rate limiting
        6. Prossegue para o endpoint
    """

    # PASSO 1: Endpoints publicos e OPTIONS passam direto
    if is_public_endpoint(request.url.path) or is_options_request(request):
        return await call_next(request)

    # PASSO 2: Extrair API Key do header
    api_key = request.headers.get("X-API-Key")

    if not api_key:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "Authentication Required",
                "message": "API Key nao fornecida. Envie no header X-API-Key",
                "status_code": 401,
                "timestamp": datetime.now().isoformat(),
                "path": request.url.path
            }
        )

    # PASSO 3: Validar se key existe (admin ou cliente)
    if not validate_key(api_key):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "Invalid API Key",
                "message": "API Key invalida ou expirada",
                "status_code": 401,
                "timestamp": datetime.now().isoformat(),
                "path": request.url.path
            }
        )

    # PASSO 4: Verificar permissao por tipo de endpoint
    if is_admin_endpoint(request.url.path):
        if not is_admin_key(api_key):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "Forbidden",
                    "message": "Acesso negado. Este endpoint requer API Key de administrador.",
                    "status_code": 403,
                    "timestamp": datetime.now().isoformat(),
                    "path": request.url.path
                }
            )
        # Admin autenticado - sem client no state
        request.state.is_admin = True

    elif is_client_endpoint(request.url.path):
        if not is_client_key(api_key):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "Forbidden",
                    "message": "Acesso negado. Este endpoint requer API Key de cliente.",
                    "status_code": 403,
                    "timestamp": datetime.now().isoformat(),
                    "path": request.url.path
                }
            )
        # Cliente autenticado - busca cliente no state
        client = get_client_by_key(api_key)
        if not client:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "Client Not Found",
                    "message": "Cliente associado a API Key nao encontrado",
                    "status_code": 401,
                    "timestamp": datetime.now().isoformat(),
                    "path": request.url.path
                }
            )
        # Carrega cliente do banco para garantir dados atualizados
        from app.infrastructure.repositories import cliente_repo
        from app.interface.api.converters import dict_to_client
        client_dict = cliente_repo.buscar_por_id(client.id)
        if client_dict:
            client = dict_to_client(client_dict)
        request.state.client = client
        request.state.is_admin = False

    # PASSO 5: Verificar Rate Limit
    allowed, used, remaining = check_rate_limit(api_key)

    if not allowed:
        reset_time = get_reset_time(api_key)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            headers={
                "X-RateLimit-Limit": "10",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_time),
                "Retry-After": str(reset_time)
            },
            content={
                "error": "Rate Limit Exceeded",
                "message": f"Limite de 10 requisicoes por minuto excedido. Tente novamente em {reset_time} segundos.",
                "status_code": 429,
                "timestamp": datetime.now().isoformat(),
                "path": request.url.path,
                "retry_after_seconds": reset_time
            }
        )

    request.state.api_key = api_key

    # PASSO 6: Prosseguir para o endpoint
    response = await call_next(request)

    # PASSO 7: Adicionar headers de rate limit na resposta
    response.headers["X-RateLimit-Limit"] = "10"
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(get_reset_time(api_key))

    return response


# =============================================================================
# FUNCOES HELPER PARA ENDPOINTS
# =============================================================================

def get_authenticated_client(request: Request):
    """Extrai cliente autenticado do request."""
    if not hasattr(request.state, "client"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cliente nao autenticado"
        )
    return request.state.client
