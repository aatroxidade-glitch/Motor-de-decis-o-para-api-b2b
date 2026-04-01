# 🚀 Motor de Decisão Automatizado para API B2B

> Sistema de decisão inteligente para validação de dados em ambiente SaaS B2B

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-lightblue.svg)](https://www.sqlite.org/)
[![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow.svg)]()
[![Arquitetura](https://img.shields.io/badge/Arquitetura-DDD-orange.svg)]()

**Projeto 3 de 5** — Portfólio Python: Arquitetura de Lógica, Sistemas e Decisão Automatizada

---

## 📖 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Problema Resolvido](#problema-resolvido)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Como Executar](#como-executar)
- [Endpoints da API](#endpoints-da-api)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Roadmap](#roadmap)
- [Autor](#autor)

---

## 🎯 Sobre o Projeto

Sistema completo de decisão automatizada B2B com API REST, autenticação, persistência e auditoria. Construído em 5 projetos progressivos demonstrando evolução técnica real.

### Projetos Concluídos

| Projeto | Descrição | Status |
|---------|-----------|--------|
| **1** | Motor de decisão puro em Python | ✅ Concluído |
| **2** | API REST com FastAPI e autenticação | ✅ Concluído |
| **3** | Persistência com SQLite e auditoria | ✅ Concluído |
| **4** | Qualidade e observabilidade | 🔄 Em desenvolvimento |
| **5** | SaaS completo com interface web | ⏳ Planejado |

---

## 💼 Problema Resolvido

Empresas SaaS B2B que oferecem serviços de validação de dados via API enfrentam desafios:

- **Controle de Acesso:** Quem pode consumir o serviço?
- **Gestão de Limites:** Quantas requisições cada cliente pode fazer?
- **Validação de Dados:** Como garantir que payloads estão corretos?
- **Decisões Automáticas:** Como aprovar/rejeitar sem intervenção humana?
- **Auditoria:** Como rastrear e justificar cada decisão?
- **Persistência:** Como garantir que dados sobrevivem a reinicializações?

---

## ⚡ Funcionalidades

### Validação de Dados

| Tipo | Campos Obrigatórios | Caso de Uso |
|------|---------------------|-------------|
| **CPF** | cpf, nome | Onboarding, KYC |
| **Endereço** | cep, logradouro, numero, cidade, estado | E-commerce, Logística |
| **Dados Bancários** | banco, agencia, conta, digito | Fintechs, Pagamentos |

### Planos Comerciais

| Plano | Requests/mês | Tamanho Max | Tipos Permitidos |
|-------|--------------|-------------|------------------|
| **Basic** | 100 | 1 KB | Apenas CPF |
| **Silver** | 500 | 10 KB | CPF + Endereço |
| **Gold** | 2.000 | 100 KB | Todos os tipos |

### Motor de Decisão — 6 Etapas Fail-Fast

1. Tipo de validação é permitido pelo plano?
2. Payload tem estrutura válida?
3. Campos obrigatórios estão presentes?
4. Tipos de dados estão corretos?
5. Tamanho do payload cabe no limite?
6. Cliente não excedeu limite de requisições?

### Autenticação em Duas Camadas

- **Admin Key** — acesso ao painel administrativo
- **Client Key** — acesso ao endpoint de validação

### Auditoria Completa

- Histórico permanente de todas as requisições e decisões
- Filtros por status, tipo e data
- Estatísticas globais do sistema
- Imutabilidade garantida por design

---

## 🏗️ Arquitetura

### Visão em Camadas (Domain-Driven Design)
```
┌─────────────────────────────────────────┐
│          INTERFACE LAYER                │
│  API REST (FastAPI) + Painel Admin      │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│        APPLICATION LAYER                │
│  • DecisionEngine (motor de decisão)    │
│  • Converters (transformações)          │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│          DOMAIN LAYER                   │
│  • Client, Plan, Payload                │
│  • Request, Decision                    │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│      INFRASTRUCTURE LAYER               │
│  • SQLite (banco de dados)              │
│  • Repositories (persistência)          │
└─────────────────────────────────────────┘
```

### Fluxo de uma Requisição
```
Cliente → POST /validate + Client Key
    → auth_middleware (valida key + carrega cliente do banco)
    → DecisionEngine (6 validações fail-fast)
    → requisicao_repo.inserir()
    → decisao_repo.inserir()
    → cliente_repo.atualizar_uso()
    → Response (approved/rejected)
```

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.13+
- pip

### Instalação
```bash
# Clone o repositório
git clone https://github.com/aatroxidade-glitch/Motor-de-decis-o-para-api-b2b.git
cd "Motor-de-decis-o-para-api-b2b"

# Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\Activate.ps1  # Windows PowerShell

# Instale as dependências
pip install -r requirements.txt
```

### Executar a API
```bash
python -m uvicorn app.interface.api.main:app --reload
```

### Acessar o Painel Administrativo
```
http://localhost:8000/docs
```

A Admin Key é exibida no console do servidor ao inicializar. Use-a no botão **Authorize** do Swagger.

### Executar o Motor de Decisão (CLI)
```bash
python main.py
```

---

## 📡 Endpoints da API

### Monitoramento (Público)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | / | Status da API |
| GET | /health | Health check |

### Validação (Client Key)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | /validate | Validar dados de cliente |

### Consultas (Admin Key)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /clients | Listar todos os clientes |
| GET | /clients/{id} | Detalhes de um cliente |
| GET | /clients/{id}/requests | Histórico de um cliente |

### Auditoria (Admin Key)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /audit | Histórico global com filtros |
| GET | /audit/stats | Estatísticas globais |

### Schemas (Admin Key)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /schemas/request | Exemplo de request |
| GET | /schemas/response/approved | Exemplo de aprovação |
| GET | /schemas/response/rejected | Exemplo de rejeição |

---

## 📂 Estrutura do Projeto
```
Motor-de-decisao-b2b/
├── data/
│   └── decisoes.db              # Banco de dados SQLite
├── main.py                      # Portal CLI (Projeto 1)
├── requirements.txt
└── app/
    ├── domain/                  # Entidades puras (intocável)
    │   ├── client.py
    │   ├── plan.py
    │   ├── payload.py
    │   ├── request.py
    │   ├── decision.py
    │   └── plans.py
    ├── application/             # Lógica de negócio
    │   └── decision_engine.py
    ├── infrastructure/          # Persistência
    │   ├── database.py
    │   ├── cliente_repository.py
    │   ├── requisicao_repository.py
    │   ├── decisao_repository.py
    │   └── repositories.py
    └── interface/
        └── api/
            ├── main.py          # FastAPI app
            ├── auth_middleware.py
            ├── api_keys_manager.py
            ├── rate_limiter.py
            ├── converters.py
            ├── engine.py
            ├── security_headers_middleware.py
            └── schemas/
                ├── request_schema.py
                ├── response_schema.py
                ├── error_schema.py
                ├── client_schema.py
                └── audit_schema.py
```

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Python** | 3.13 | Linguagem principal |
| **FastAPI** | 0.115 | Framework web |
| **Pydantic** | 2.10 | Validação de dados |
| **Uvicorn** | latest | Servidor ASGI |
| **SQLite** | 3 | Banco de dados |

---

## 🗺️ Roadmap

- ✅ **Projeto 1** — Motor de decisão puro em Python
- ✅ **Projeto 2** — API REST com FastAPI, autenticação e segurança
- ✅ **Projeto 3** — Persistência com SQLite, repositories e auditoria
- 🔄 **Projeto 4** — Testes automatizados, logs estruturados e métricas
- ⏳ **Projeto 5** — SaaS completo com interface web e portal do cliente

---

## 👤 Autor

**Cristóvão Caldeira**

- GitHub: [@aatroxidade-glitch](https://github.com/aatroxidade-glitch)

---

## 📄 Licença

Este projeto é parte de um portfólio educacional e está disponível para fins de demonstração.

---

**⭐ Se este projeto foi útil, considere dar uma estrela!**
