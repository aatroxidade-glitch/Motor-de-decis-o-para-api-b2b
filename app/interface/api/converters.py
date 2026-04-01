"""
Converters - Transformação entre Schemas e Domain

Responsável por converter dados entre camadas:
- API Schemas (Pydantic) → Domain Objects (Python puro)
- Domain Objects → API Schemas (respostas)

Autor: Cristóvão Caldeira
Data: Fevereiro 2026
Projeto: Portfólio Python - Projeto 2/5 - Etapa 3 - Mini-Etapa 3.2
"""

from datetime import datetime

from app.domain.payload import Payload
from app.domain.request import Request
from app.domain.decision import Decision
from app.domain.client import Client

from app.interface.api.schemas.request_schema import ValidateRequest
from app.interface.api.schemas.response_schema import (
    ValidateResponseApproved,
    ValidateResponseRejected,
    UsageInfo
)


# =============================================================================
# CONVERSÃO: API SCHEMAS → DOMAIN OBJECTS
# =============================================================================

def convert_request_to_payload(validate_request: ValidateRequest) -> Payload:
    """
    Converte ValidateRequest (Pydantic) em Payload (Domain).
    
    Args:
        validate_request: Schema Pydantic recebido da API
    
    Returns:
        Payload: Objeto de domínio
    
    Mapeamento:
        ValidateRequest.tipo → Payload.tipo
        ValidateRequest.dados → Payload.dados
    
    Exemplo:
        >>> request_schema = ValidateRequest(
        ...     client_id="CLI_001",
        ...     tipo="validacao_cpf",
        ...     dados={"cpf": "123", "nome": "João"}
        ... )
        >>> payload = convert_request_to_payload(request_schema)
        >>> print(payload.tipo)  # "validacao_cpf"
        >>> print(payload.dados)  # {"cpf": "123", "nome": "João"}
    """
    return Payload(
        tipo=validate_request.tipo,
        dados=validate_request.dados
    )


def convert_to_domain_request(validate_request: ValidateRequest, client: Client) -> Request:
    """
    Converte ValidateRequest + Client em Request (Domain).
    
    Args:
        validate_request: Schema Pydantic da API
        client: Cliente que faz a requisição
    
    Returns:
        Request: Objeto de domínio completo
    
    Processo:
        1. Converte ValidateRequest → Payload
        2. Cria Request(client, payload)
        3. Request gera ID único automaticamente
    
    Exemplo:
        >>> from app.domain.client import Client
        >>> from app.domain.plans import BASIC_PLAN
        >>> 
        >>> client = Client("CLI_001", "Empresa X", BASIC_PLAN)
        >>> request_schema = ValidateRequest(
        ...     client_id="CLI_001",
        ...     tipo="validacao_cpf",
        ...     dados={"cpf": "123", "nome": "João"}
        ... )
        >>> 
        >>> domain_request = convert_to_domain_request(request_schema, client)
        >>> print(domain_request.id)  # UUID gerado automaticamente
        >>> print(domain_request.client.nome)  # "Empresa X"
        >>> print(domain_request.payload.tipo)  # "validacao_cpf"
    """
    # Converte schema → payload
    payload = convert_request_to_payload(validate_request)
    
    # Cria request de domínio
    return Request(client=client, payload=payload)


# =============================================================================
# CONVERSÃO: DOMAIN OBJECTS → API SCHEMAS
# =============================================================================

def convert_to_usage_info(client: Client) -> UsageInfo:
    """
    Converte informações de uso do cliente em UsageInfo (schema).
    
    Args:
        client: Cliente de domínio
    
    Returns:
        UsageInfo: Schema Pydantic com informações de uso
    
    Cálculos:
        - used: client.requisicoes_usadas
        - limit: client.plan.max_requests
        - percentage: (used / limit) * 100
    
    Exemplo:
        >>> from app.domain.client import Client
        >>> from app.domain.plans import BASIC_PLAN
        >>> 
        >>> client = Client("CLI_001", "Empresa", BASIC_PLAN)
        >>> client.requisicoes_usadas = 50
        >>> 
        >>> usage = convert_to_usage_info(client)
        >>> print(usage.used)  # 50
        >>> print(usage.limit)  # 100
        >>> print(usage.percentage)  # 50.0
    """
    return UsageInfo(
        used=client.requisicoes_usadas,
        limit=client.plan.max_requests,
        percentage=client.usage_percentage()
    )


def convert_decision_to_approved_response(
    decision: Decision,
    request: Request
) -> ValidateResponseApproved:
    """
    Converte Decision aprovada em ValidateResponseApproved (schema).
    
    Args:
        decision: Decisão de domínio (deve estar aprovada)
        request: Request de domínio que gerou a decisão
    
    Returns:
        ValidateResponseApproved: Schema de resposta aprovada
    
    Importante:
        Só deve ser chamado quando decision.aprovada == True
    
    Mapeamento:
        - status: "approved" (fixo)
        - request_id: request.id
        - client_id: request.client.id
        - tipo: request.payload.tipo
        - motivo: decision.motivo
        - timestamp: decision.timestamp
        - usage: convert_to_usage_info(request.client)
    
    Exemplo:
        >>> # (Assumindo decision aprovada e request válido)
        >>> response = convert_decision_to_approved_response(decision, request)
        >>> print(response.status)  # "approved"
        >>> print(response.request_id)  # UUID da request
        >>> print(response.usage.used)  # Requisições usadas
    """
    return ValidateResponseApproved(
        status="approved",
        request_id=request.id,
        client_id=request.client.id,
        tipo=request.payload.tipo,
        motivo=decision.motivo,
        timestamp=decision.timestamp,
        usage=convert_to_usage_info(request.client)
    )


def convert_decision_to_rejected_response(
    decision: Decision,
    request: Request,
    suggestion: str | None = None
) -> ValidateResponseRejected:
    """
    Converte Decision rejeitada em ValidateResponseRejected (schema).
    
    Args:
        decision: Decisão de domínio (deve estar rejeitada)
        request: Request de domínio que gerou a decisão
        suggestion: Sugestão opcional de ação (ex: "Faça upgrade para Silver")
    
    Returns:
        ValidateResponseRejected: Schema de resposta rejeitada
    
    Importante:
        Só deve ser chamado quando decision.aprovada == False
    
    Mapeamento:
        - status: "rejected" (fixo)
        - request_id: request.id
        - client_id: request.client.id
        - tipo: request.payload.tipo
        - motivo: decision.motivo
        - timestamp: decision.timestamp
        - suggestion: gerado automaticamente ou recebido como parâmetro
    
    Sugestões automáticas:
        - Tipo não permitido → "Faça upgrade para [plano superior]"
        - Limite excedido → "Aguarde renovação mensal ou faça upgrade"
        - Payload inválido → None (cliente deve corrigir dados)
    
    Exemplo:
        >>> # (Assumindo decision rejeitada e request válido)
        >>> response = convert_decision_to_rejected_response(decision, request)
        >>> print(response.status)  # "rejected"
        >>> print(response.motivo)  # Motivo detalhado da rejeição
        >>> print(response.suggestion)  # Sugestão de ação (se aplicável)
    """
    # Gera sugestão automática se não fornecida
    if suggestion is None:
        suggestion = _generate_suggestion(decision, request)
    
    return ValidateResponseRejected(
        status="rejected",
        request_id=request.id,
        client_id=request.client.id,
        tipo=request.payload.tipo,
        motivo=decision.motivo,
        timestamp=decision.timestamp,
        suggestion=suggestion
    )


def _generate_suggestion(decision: Decision, request: Request) -> str | None:
    """
    Gera sugestão automática baseada no motivo da rejeição.
    
    Args:
        decision: Decisão rejeitada
        request: Request original
    
    Returns:
        str | None: Sugestão de ação ou None
    
    Regras:
        - "não permite validação do tipo" → Sugestão de upgrade
        - "Limite de requisições excedido" → Aguardar ou upgrade
        - "Payload inválido" → None (cliente corrige)
        - "excede limite" (tamanho) → None ou upgrade para maior
    """
    motivo = decision.motivo.lower()
    plano_atual = request.client.plan.nome
    
    # Tipo não permitido pelo plano
    if "não permite validação do tipo" in motivo:
        if plano_atual == "Basic":
            return "Faça upgrade para o plano Silver para desbloquear validação de endereço"
        elif plano_atual == "Silver":
            return "Faça upgrade para o plano Gold para desbloquear validação de dados bancários"
        else:
            return None
    
    # Limite de requisições excedido
    elif "limite de requisições excedido" in motivo:
        return "Aguarde renovação mensal ou faça upgrade de plano para aumentar limite"
    
    # Payload muito grande
    elif "excede limite" in motivo:
        if plano_atual == "Basic":
            return "Plano Basic suporta até 1KB. Faça upgrade para Silver (10KB) ou Gold (100KB)"
        elif plano_atual == "Silver":
            return "Plano Silver suporta até 10KB. Faça upgrade para Gold (100KB)"
        else:
            return None
    
    # Payload inválido (cliente deve corrigir)
    elif "payload inválido" in motivo:
        return None
    
    # Outros casos
    else:
        return None


# =============================================================================
# FUNÇÃO PRINCIPAL DE CONVERSÃO (UNIFICA APROVADA E REJEITADA)
# =============================================================================

def convert_decision_to_response(
    decision: Decision,
    request: Request
) -> ValidateResponseApproved | ValidateResponseRejected:
    """
    Converte Decision em response apropriada (Approved ou Rejected).
    
    Args:
        decision: Decisão do motor
        request: Request original
    
    Returns:
        ValidateResponseApproved: Se decision.aprovada == True
        ValidateResponseRejected: Se decision.aprovada == False
    
    Esta é a função principal usada pelo endpoint.
    Decide automaticamente qual tipo de resposta retornar.
    
    Exemplo:
        >>> # No endpoint /validate
        >>> decision = engine.evaluate(domain_request)
        >>> response = convert_decision_to_response(decision, domain_request)
        >>> # response será Approved ou Rejected automaticamente
    """
    if decision.aprovada:
        return convert_decision_to_approved_response(decision, request)
    else:
        return convert_decision_to_rejected_response(decision, request)


# =============================================================================
# CONVERSAO: DICT DO BANCO → DOMAIN OBJECT
# =============================================================================

def dict_to_client(data: dict):
    """
    Converte dicionario do banco de dados em objeto Client do dominio.

    Args:
        data: dict com campos do banco (id, nome, plano, requisicoes_usadas)

    Returns:
        Client: Objeto de dominio completo com plano correto
    """
    from app.domain.plans import BASIC_PLAN, SILVER_PLAN, GOLD_PLAN

    planos = {
        "Basic": BASIC_PLAN,
        "Silver": SILVER_PLAN,
        "Gold": GOLD_PLAN
    }

    from app.domain.client import Client

    client = Client(
        id=data["id"],
        nome=data["nome"],
        plan=planos[data["plano"]]
    )
    client.requisicoes_usadas = data["requisicoes_usadas"]
    return client
