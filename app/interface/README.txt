# 🚀 Motor de Decisão B2B - API REST

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> Sistema B2B/SaaS de tomada de decisão automatizada com autenticação, rate limiting e múltiplas camadas de segurança.

---

## 📋 Sobre o Projeto

API REST profissional para **validação automatizada de dados** baseada em regras de negócio, planos comerciais e controle de quota. Construída seguindo princípios de **Domain-Driven Design (DDD)**, **Clean Architecture** e padrões de mercado.

### ✨ Principais Funcionalidades

- 🔐 **Autenticação via API Key** - Sistema seguro de identificação de clientes
- 🚦 **Rate Limiting** - Controle de taxa (10 requisições/minuto)
- 🛡️ **Security Headers** - Proteção contra XSS, clickjacking, MIME sniffing
- 🌐 **CORS** - Suporte para aplicações frontend cross-origin
- 📊 **3 Planos Comerciais** - Basic, Silver e Gold com limites diferenciados
- 📚 **Swagger UI** - Documentação interativa com botão "Authorize"
- 🎯 **Validações Customizadas** - CPF, Endereço, Dados Bancários
- 📈 **Auditoria Completa** - Rastreamento de todas as decisões

---

## 🏗️ Arquitetura

Projeto construído seguindo **Clean Architecture** e **DDD** (Domain-Driven Design):
```
app/
├── domain/              # Camada de Domínio (Entidades puras)
│   ├── client.py       # Entidade Cliente
│   ├── plan.py         # Entidade Plano
│   ├── request.py      # Entidade Requisição
│   └── decision.py     # Entidade Decisão
│
├── application/         # Camada de Aplicação (Casos de uso)
│   ├── decision_engine.py    # Motor de decisão
│   ├── rules/                # Regras de negócio
│   └── repositories/         # Repositórios
│
└── interface/           # Camada de Interface
    └── api/             # API REST
        ├── main.py                         # FastAPI app
        ├── auth_middleware.py              # Autenticação
        ├── rate_limiter.py                 # Rate limiting
        ├── security_headers_middleware.py  # Security headers
        └── schemas/                        # Pydantic schemas
```

### 🎯 Princípios Aplicados

- ✅ **SOLID** (Single Responsibility, Dependency Inversion)
- ✅ **DDD** (Domain-Driven Design)
- ✅ **Clean Architecture** (Separação de camadas)
- ✅ **Design Patterns** (Singleton, Middleware, Strategy)
- ✅ **Security in Depth** (Múltiplas camadas de proteção)

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| **Python** | 3.13 | Linguagem principal |
| **FastAPI** | 0.115 | Framework web moderno |
| **Pydantic** | 2.x | Validação de dados |
| **Uvicorn** | latest | Servidor ASGI |

---

## 🚀 Instalação e Uso

### Pré-requisitos

- Python 3.13+
- pip

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/motor-decisao-b2b.git
cd motor-decisao-b2b
```

### 2. Crie ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale dependências
```bash
pip install fastapi uvicorn pydantic
```

### 4. Execute o servidor
```bash
uvicorn app.interface.api.main:app --reload
```

### 5. Acesse a documentação
```
http://localhost:8000/docs
```

---

## 🔑 Como Usar a API

### 1. Obter API Key

Ao iniciar o servidor, as **API Keys** são exibidas no console:
```
🔑 API KEYS GERADAS PARA CLIENTES MOCK
============================================================
Cliente: CLI_001  | Plano: Basic  | Key: c1cc841589684a34f9723ed251c7c7cf
Cliente: CLI_002  | Plano: Silver | Key: a6a3084d4eec777570813b0035468cae
Cliente: CLI_003  | Plano: Gold   | Key: 2c750f51279bc5ea200791820d5c10a6
```

### 2. Fazer Requisição
```bash
curl -X POST "http://localhost:8000/validate" \
  -H "X-API-Key: c1cc841589684a34f9723ed251c7c7cf" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "validacao_cpf",
    "dados": {
      "cpf": "12345678900",
      "nome": "João Silva"
    }
  }'
```

### 3. Resposta (200 OK)
```json
{
  "status": "approved",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "client_id": "CLI_001",
  "tipo": "validacao_cpf",
  "motivo": "Requisição autorizada: validacao_cpf",
  "timestamp": "2026-03-05T10:30:00.123456",
  "usage": {
    "used": 1,
    "limit": 100,
    "percentage": 1.0
  }
}
```

---

## 📊 Planos Disponíveis

| Plano | Limite Mensal | Tipos Permitidos | Tamanho Payload |
|-------|---------------|------------------|-----------------|
| **Basic** | 100 requests | CPF | 1 KB |
| **Silver** | 500 requests | CPF, Endereço | 5 KB |
| **Gold** | 2.000 requests | CPF, Endereço, Dados Bancários | 10 KB |

---

## 🔐 Recursos de Segurança

### Autenticação
- ✅ API Key no header `X-API-Key`
- ✅ Validação centralizada via middleware
- ✅ Cliente identificado automaticamente

### Rate Limiting
- ✅ **10 requisições por minuto** por API Key
- ✅ Headers informativos (`X-RateLimit-Remaining`, `X-RateLimit-Reset`)
- ✅ Erro **429 Too Many Requests** quando excedido

### Security Headers
- ✅ `X-Content-Type-Options: nosniff`
- ✅ `X-Frame-Options: DENY`
- ✅ `X-XSS-Protection: 1; mode=block`
- ✅ `Content-Security-Policy`
- ✅ `Referrer-Policy: no-referrer`
- ✅ `Permissions-Policy`

### CORS
- ✅ Configurado para cross-origin
- ✅ Suporte a preflight (OPTIONS)
- ✅ Headers customizados permitidos

---

## 📚 Endpoints Disponíveis

### Públicos (sem autenticação)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/` | Root - Status da API |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI |
| GET | `/openapi.json` | OpenAPI schema |

### Protegidos (requer API Key)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/validate` | Validar dados de cliente |
| GET | `/clients` | Listar todos os clientes |
| GET | `/clients/{client_id}` | Detalhes de um cliente |
| GET | `/clients/{client_id}/requests` | Histórico de requisições |

---

## 🧪 Testando com Swagger UI

1. Acesse: `http://localhost:8000/docs`
2. Clique no botão **"Authorize"** 🔓 (canto superior direito)
3. Cole uma API Key do console
4. Clique em **"Authorize"** e depois **"Close"**
5. Teste qualquer endpoint com **"Try it out"**!

---

## 🎯 Códigos de Status HTTP

| Código | Significado | Quando ocorre |
|--------|-------------|---------------|
| **200** | OK | Requisição processada com sucesso |
| **401** | Unauthorized | API Key ausente ou inválida |
| **404** | Not Found | Recurso não encontrado |
| **422** | Unprocessable Entity | Dados de entrada inválidos |
| **429** | Too Many Requests | Rate limit excedido |
| **500** | Internal Server Error | Erro interno do servidor |

---

## 📈 Exemplo de Fluxo Completo
```
1. Cliente → POST /validate + X-API-Key
2. CORS Middleware → Valida origem
3. Security Headers Middleware → Adiciona proteções
4. Auth Middleware → Valida API Key + Rate Limit
5. Endpoint /validate → Processa validação
6. DecisionEngine → Aplica regras de negócio
7. Response → 200 OK com decisão + headers
```

---

## 🏆 Destaques Técnicos

### 🎨 Clean Architecture
- Separação clara entre Domain, Application e Interface
- Baixo acoplamento, alta coesão
- Fácil manutenção e testes

### 🔧 Design Patterns
- **Singleton:** `APIKeysManager`, `RateLimiter`
- **Middleware:** Interceptação de requisições
- **Strategy:** Diferentes regras por tipo de validação
- **Repository:** Acesso a dados abstraído

### 🛡️ Security Best Practices
- Defense in Depth (múltiplas camadas)
- Principle of Least Privilege
- Security Headers conforme OWASP
- Rate Limiting contra abuso

---

## 🚧 Roadmap Futuro

- [ ] Banco de dados PostgreSQL
- [ ] Testes automatizados (pytest, >80% coverage)
- [ ] Cache com Redis
- [ ] Observabilidade (logs estruturados, métricas)
- [ ] CI/CD pipeline (Docker, GitHub Actions)
- [ ] Deploy em produção (AWS/Azure/GCP)
- [ ] Autenticação OAuth2
- [ ] Webhooks para notificações

---

## 📝 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👤 Autor

**Cristóvão Caldeira**

- GitHub: [@cristovao-caldeira](https://github.com/cristovao-caldeira)
- LinkedIn: [Cristóvão Caldeira](https://linkedin.com/in/cristovao-caldeira)
- Email: cristovao.caldeira@exemplo.com

---

## 🙏 Agradecimentos

Projeto desenvolvido como parte do portfólio técnico para demonstrar habilidades em:
- Desenvolvimento de APIs REST profissionais
- Arquitetura de software (DDD, Clean Architecture)
- Segurança de aplicações web
- Boas práticas de desenvolvimento Python

---

<p align="center">
  Feito com ❤️ e muito ☕ por Cristóvão Caldeira
</p>