from app.domain.plan import Plan
from app.domain.payload import Payload

# Planos pré-definidos do sistema com tipos de validação permitidos

BASIC_PLAN = Plan(
    nome="Basic",
    max_requests=100,
    max_payload_size=1024,  # 1KB
    tipos_permitidos=[
        Payload.TIPO_CPF  # Apenas validação de CPF
    ]
)

SILVER_PLAN = Plan(
    nome="Silver",
    max_requests=500,
    max_payload_size=10240,  # 10KB
    tipos_permitidos=[
        Payload.TIPO_CPF,
        Payload.TIPO_ENDERECO  # CPF + Endereço
    ]
)

GOLD_PLAN = Plan(
    nome="Gold",
    max_requests=2000,
    max_payload_size=102400,  # 100KB
    tipos_permitidos=[
        Payload.TIPO_CPF,
        Payload.TIPO_ENDERECO,
        Payload.TIPO_DADOS_BANCARIOS  # Todos os tipos
    ]
)