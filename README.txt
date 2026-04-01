# 🚀 Motor de Decisão Automatizado para API B2B

> Sistema de decisão inteligente para validação de dados em ambiente SaaS B2B

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Produção-green.svg)]()
[![Arquitetura](https://img.shields.io/badge/Arquitetura-DDD-orange.svg)]()

**Projeto 1 de 5** — Portfólio Python: Arquitetura de Lógica, Sistemas e Decisão Automatizada

---

## 📖 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Problema Resolvido](#problema-resolvido)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Como Executar](#como-executar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Decisões de Design](#decisões-de-design)
- [Roadmap](#roadmap)
- [Autor](#autor)

---

## 🎯 Sobre o Projeto

Este projeto implementa o **núcleo lógico** de uma API SaaS B2B de validação de dados, demonstrando:

- ✅ Modelagem de domínio profissional
- ✅ Arquitetura em camadas (Domain-Driven Design)
- ✅ Motor de decisão automatizado
- ✅ Sistema de auditoria completo
- ✅ Controle de limites por plano comercial

### Objetivo do Portfólio

Demonstrar capacidade de:
- Modelar sistemas reais
- Aplicar arquitetura de software
- Escrever código limpo e profissional
- Resolver problemas de mercado

---

## 💼 Problema Resolvido

### Contexto de Mercado

Empresas SaaS B2B que oferecem serviços de validação de dados via API enfrentam desafios:

- **Controle de Acesso:** Quem pode consumir o serviço?
- **Gestão de Limites:** Quantas requisições cada cliente pode fazer?
- **Validação de Dados:** Como garantir que payloads estão corretos?
- **Decisões Automáticas:** Como aprovar/rejeitar sem intervenção humana?
- **Auditoria:** Como rastrear e justificar cada decisão?

### Solução Implementada

Sistema completo que:

1. **Valida automaticamente** requisições de clientes
2. **Aplica regras de negócio** baseadas em planos contratados
3. **Controla limites** de uso em tempo real
4. **Registra e audita** todas as decisões
5. **Fornece justificativas** explícitas para cada resultado

---

## ⚡ Funcionalidades

### 1. Validação de Dados

**3 Tipos de Validação Suportados:**

| Tipo | Campos Obrigatórios | Caso de Uso |
|------|---------------------|-------------|
| **CPF** | cpf, nome | Onboarding, KYC |
| **Endereço** | cep, logradouro, numero | E-commerce, Logística |
| **Dados Bancários** | banco, agencia, conta | Fintechs, Pagamentos |

### 2. Planos Comerciais

**3 Planos com Limites Diferentes:**

| Plano | Requests/mês | Tamanho Max | Tipos Permitidos |
|-------|--------------|-------------|------------------|
| **Basic** | 100 | 1 KB | Apenas CPF |
| **Silver** | 500 | 10 KB | CPF + Endereço |
| **Gold** | 2.000 | 100 KB | Todos os tipos |

### 3. Motor de Decisão

**Validações Executadas (sequencial, fail-fast):**

1. ✅ Tipo de validação é permitido pelo plano?
2. ✅ Payload tem estrutura válida (dict não vazio)?
3. ✅ Campos obrigatórios estão presentes?
4. ✅ Tipos de dados estão corretos?
5. ✅ Tamanho do payload cabe no limite?
6. ✅ Cliente não excedeu limite de requests?

**Resultado:** Decisão aprovada ou rejeitada com motivo explícito

### 4. Sistema de Auditoria

- 📝 Registro completo de todas as decisões
- 🕒 Timeline de eventos com timestamps precisos
- 🔍 Rastreamento por cliente, período ou motivo
- 📊 Reconstrução de estado completa
- ✅ Compliance (LGPD, GDPR)

---

## 🏗️ Arquitetura

### Visão em Camadas (Domain-Driven Design)

```
┌─────────────────────────────────────────┐
│          INTERFACE LAYER                │  ← Pontos de entrada
│  (CLI, Menu, Futuros endpoints REST)    │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│        APPLICATION LAYER                │  ← Orquestração
│  • DecisionEngine (motor de decisão)    │
│  • Simulator (demonstração)             │
│  • TestScenarios (validação)            │
│  • AuditDemo (auditoria)                │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│          DOMAIN LAYER                   │  ← Regras de negócio
│  • Client (identidade e uso)            │
│  • Plan (limites comerciais)            │
│  • Payload (auto-validação)             │
│  • Request (ato de consumo)             │
│  • Decision (resultado)                 │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│      INFRASTRUCTURE LAYER               │  ← Persistência (futuro)
│  (Preparado para Projeto 2)             │
└─────────────────────────────────────────┘
```

### Regra de Dependência

```
Interface → Application → Domain
              ↑
        Infrastructure
```

**Princípio:** Dependências fluem sempre para dentro, nunca reverso.

### Fluxo de Uma Requisição

```
1. Cliente + Payload → Request criado
2. Request → DecisionEngine.evaluate()
3. Motor executa 6 validações sequenciais
4. Decisão gerada (aprovada ou rejeitada)
5. Se aprovada: incrementa uso do cliente
6. Decision retornada com motivo explícito
```

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.14+
- Nenhuma dependência externa (Python puro)

### Instalação

```bash
# Clone o repositório
git clone <seu-repositorio>
cd "Motor de decisão automático Saas b2b"

# Não precisa instalar dependências (Python puro)
```

### Execução

```bash
# Executar sistema completo
python main.py
```

### O que acontece ao executar

1. **Demonstração Rápida:** 6 testes básicos executam automaticamente
2. **Menu Interativo:** Escolha entre:
   - Simulador (10 clientes, 50 requisições)
   - Cenários de Teste (12 cenários específicos)
   - Demonstração de Auditoria (rastreamento completo)
   - Executar todos sequencialmente

### Exemplos de Uso Programático

```python
from app.domain.client import Client
from app.domain.payload import Payload
from app.domain.request import Request
from app.domain.plans import BASIC_PLAN
from app.application.decision_engine import DecisionEngine

# Criar cliente e motor
cliente = Client(id="001", nome="TechStart LTDA", plan=BASIC_PLAN)
engine = DecisionEngine()

# Criar payload válido
payload = Payload(
    tipo=Payload.TIPO_CPF,
    dados={"cpf": "12345678900", "nome": "João Silva"}
)

# Criar requisição e avaliar
request = Request(client=cliente, payload=payload)
decision = engine.evaluate(request)

# Verificar resultado
if decision.is_approved():
    print(f"✅ Aprovada: {decision.motivo}")
    print(f"Uso atual: {cliente.requisicoes_usadas}/{cliente.plan.max_requests}")
else:
    print(f"❌ Rejeitada: {decision.motivo}")
```

---

## 📂 Estrutura do Projeto

```
Motor de decisão automático Saas b2b/
│
├── main.py                          # Ponto de entrada principal
│
├── README.md                        # Este arquivo
├── ARCHITECTURE.md                  # Documentação técnica
├── API_REFERENCE.md                 # Referência de classes
│
└── app/
    ├── __init__.py
    │
    ├── domain/                      # Camada de Domínio (regras puras)
    │   ├── __init__.py
    │   ├── client.py                # Entidade Cliente
    │   ├── plan.py                  # Entidade Plano
    │   ├── payload.py               # Entidade Payload (validação)
    │   ├── request.py               # Entidade Request
    │   ├── decision.py              # Entidade Decision
    │   └── plans.py                 # Catálogo de planos
    │
    ├── application/                 # Camada de Aplicação (orquestração)
    │   ├── __init__.py
    │   ├── decision_engine.py       # Motor de decisão
    │   ├── simulator.py             # Simulador de uso real
    │   ├── test_scenarios.py        # Cenários de teste
    │   └── audit_demo.py            # Sistema de auditoria
    │
    ├── infrastructure/              # Camada de Infraestrutura
    │   └── __init__.py              # (Preparado para Projeto 2)
    │
    └── interface/                   # Camada de Interface
        └── __init__.py              # (Preparado para Projeto 2)
```

---

## 🛠️ Tecnologias Utilizadas

### Stack Técnico

- **Linguagem:** Python 3.14 (puro, sem frameworks)
- **Paradigma:** Programação Orientada a Objetos
- **Arquitetura:** Domain-Driven Design (DDD)
- **Padrões:** Strategy, Value Object, Stateful Entities

### Bibliotecas Nativas

```python
import uuid          # Geração de IDs únicos
import sys           # Cálculo de tamanho de objetos
import random        # Geração de cenários variados
from datetime import datetime  # Timestamp de eventos
import time          # Efeitos visuais
```

**Nenhuma dependência externa** — Python puro para máxima portabilidade

---

## 🎨 Decisões de Design

### 1. Por que Payload valida a si mesmo?

**Decisão:** Auto-validação (métodos dentro da classe Payload)

**Motivos:**
- ✅ Encapsulamento: dados e regras juntos
- ✅ Reutilização: qualquer parte do sistema pode validar
- ✅ Testabilidade: validação isolada
- ✅ Manutenção: mudança em regra afeta apenas Payload

### 2. Por que Motor incrementa uso?

**Decisão:** DecisionEngine incrementa `client.requisicoes_usadas`

**Motivos:**
- ✅ Consistência: aprovação sempre incrementa
- ✅ Atomicidade: decisão + incremento = operação única
- ✅ Auditoria: estado muda apenas em aprovações
- ✅ Simplicidade: não precisa lembrar de incrementar externamente

### 3. Por que Decision é imutável?

**Decisão:** Decision não muda após criação

**Motivos:**
- ✅ Rastreabilidade: resultado não pode ser alterado
- ✅ Auditoria: histórico confiável
- ✅ Thread-safe: pode ser compartilhado sem riscos
- ✅ Clareza: separação entre decisão e execução

### 4. Por que usar mapas no Payload?

**Decisão:** Validações baseadas em dicionários (data-driven)

**Motivos:**
- ✅ Escalabilidade: novo tipo = adicionar entrada no mapa
- ✅ Manutenção: regras centralizadas
- ✅ Legibilidade: estrutura declarativa
- ✅ Sem if/elif gigantes: lógica limpa

---

## 🗺️ Roadmap

### Projeto 1 — Motor de Decisão (ATUAL)
✅ Python puro, foco em domínio e lógica

### Projeto 2 — API Modularizada (PRÓXIMO)
- Adicionar FastAPI
- Endpoints REST
- Autenticação via API Keys
- Documentação OpenAPI automática

### Projeto 3 — Persistência e Auditoria
- Banco de dados (SQLite)
- Histórico persistente
- Migrations

### Projeto 4 — Automação e Qualidade
- Testes automatizados (pytest)
- Logging estruturado
- CI/CD

### Projeto 5 — Sistema SaaS Completo
- Integrações externas
- Billing
- Dashboard

---

## 📈 Métricas do Projeto

- **Linhas de código:** ~1.200
- **Classes:** 11 principais
- **Métodos:** ~50
- **Cenários de teste:** 12 específicos + 50 simulados
- **Tipos de validação:** 3
- **Planos comerciais:** 3
- **Cobertura funcional:** 100%

---

## 🎓 Conceitos Demonstrados

### Arquitetura de Software
- Domain-Driven Design (DDD)
- Separation of Concerns
- Dependency Inversion
- Single Responsibility Principle
- Open/Closed Principle

### Programação
- POO avançada (encapsulamento, herança, polimorfismo)
- Data-driven validation
- Fail-fast pattern
- Stateful vs Stateless
- Immutability

### Pensamento de Produto
- Modelagem de planos SaaS
- Controle de quota
- Auditabilidade
- Compliance

---

## 👤 Autor

**[Seu Nome]**

- GitHub: [@seu-usuario](https://github.com/seu-usuario)
- LinkedIn: [seu-perfil](https://linkedin.com/in/seu-perfil)
- Email: seu@email.com

---

## 📄 Licença

Este projeto é parte de um portfólio educacional e está disponível para fins de demonstração.

---

## 🙏 Agradecimentos

Este projeto faz parte de um portfólio progressivo de 5 projetos focado em demonstrar evolução técnica real e alinhamento com o mercado de tecnologia.

---

**⭐ Se este projeto foi útil, considere dar uma estrela!**