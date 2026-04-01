"""
Motor de Decisão Automatizado para API B2B de Validação de Dados

Sistema interativo completo com gerenciamento de clientes e auditoria de requisições.

Autor: [Cristóvão Caldeira]
Data: Janeiro 2026
Projeto: Portfólio Python - Projeto 4/5
"""

import time

# Camada de Domínio
from app.domain.client import Client
from app.domain.payload import Payload
from app.domain.request import Request
from app.domain.decision import Decision
from app.domain.plan import Plan
from app.domain.plans import BASIC_PLAN, SILVER_PLAN, GOLD_PLAN

# Camada de Aplicação
from app.application.decision_engine import DecisionEngine
from app.application.simulator import main as run_simulator
from app.application.testecenário import main as run_test_scenarios
from app.application.audit_demo import main as run_audit_demo


# =============================================================================
# SISTEMA DE GERENCIAMENTO GLOBAL
# =============================================================================

class SystemManager:
    """Gerenciador global do sistema com clientes e histórico de requests"""
    
    def __init__(self):
        self.engine = DecisionEngine()
        self.clients = []
        self.all_requests = []  # Histórico de todas as requests
        self.all_decisions = []  # Histórico de todas as decisões
        self._initialize_sample_clients()
    
    def _initialize_sample_clients(self):
        """Inicializa sistema com clientes de exemplo"""
        sample_clients = [
            Client(id="CLI_001", nome="TechStart LTDA", plan=BASIC_PLAN),
            Client(id="CLI_002", nome="DataFlow Solutions", plan=SILVER_PLAN),
            Client(id="CLI_003", nome="FinTech Global Corp", plan=GOLD_PLAN),
            Client(id="CLI_004", nome="Startup Inovadora", plan=BASIC_PLAN),
            Client(id="CLI_005", nome="E-commerce Brasil", plan=SILVER_PLAN),
        ]
        self.clients.extend(sample_clients)
    
    def get_client_by_id(self, client_id: str):
        """Busca cliente por ID"""
        for client in self.clients:
            if client.id == client_id:
                return client
        return None
    
    def get_requests_by_client(self, client_id: str):
        """Retorna todas as requests de um cliente"""
        return [
            (req, dec) for req, dec in zip(self.all_requests, self.all_decisions)
            if req.client.id == client_id
        ]
    
    def process_request(self, client, payload):
        """Processa uma request e salva no histórico"""
        request = Request(client=client, payload=payload)
        decision = self.engine.evaluate(request)
        
        self.all_requests.append(request)
        self.all_decisions.append(decision)
        
        return request, decision


# Instância global do sistema
system = SystemManager()


# =============================================================================
# FUNÇÕES DO MENU
# =============================================================================

def limpar_tela():
    """Limpa visualmente a tela com linhas em branco"""
    print("\n" * 2)


def pausar():
    """Pausa e aguarda usuário pressionar ENTER"""
    input("\n⏸️  Pressione ENTER para continuar...")


def animacao_carregamento(mensagem, dots=3, intervalo=0.3):
    """Exibe animação de carregamento"""
    print(f"\n{mensagem}", end="", flush=True)
    for _ in range(dots):
        time.sleep(intervalo)
        print(".", end="", flush=True)
    print(" ✅")
    time.sleep(0.5)


def exibir_cabecalho():
    """Exibe cabeçalho do sistema"""
    print("\n" + "=" * 80)
    print("🚀 MOTOR DE DECISÃO B2B - SISTEMA DE GERENCIAMENTO")
    print("=" * 80)


def exibir_menu_principal():
    """Exibe menu principal de opções"""
    print("\n" + "─" * 80)
    print("📋 MENU PRINCIPAL")
    print("─" * 80)
    print()
    print("🔹 DEMONSTRAÇÕES")
    print("   1 - Simulador de Múltiplos Clientes (50 requisições)")
    print("   2 - Cenários de Teste Específicos (12 cenários)")
    print("   3 - Demonstração de Auditabilidade")
    print()
    print("🔹 GERENCIAMENTO")
    print("   4 - Listar Todos os Clientes")
    print("   5 - Ver Requisições de um Cliente")
    print("   6 - Processar Nova Requisição")
    print()
    print("🔹 SISTEMA")
    print("   0 - Sair do Sistema")
    print()
    print("─" * 80)


# =============================================================================
# OPÇÃO 1, 2, 3: DEMONSTRAÇÕES
# =============================================================================

def executar_simulador():
    """Executa o Simulador de Múltiplos Clientes"""
    animacao_carregamento("🔄 Inicializando Simulador")
    run_simulator()
    pausar()


def executar_cenarios():
    """Executa os Cenários de Teste Específicos"""
    animacao_carregamento("🔄 Inicializando Cenários de Teste")
    run_test_scenarios()
    pausar()


def executar_auditoria():
    """Executa a Demonstração de Auditabilidade"""
    animacao_carregamento("🔄 Inicializando Sistema de Auditoria")
    run_audit_demo()
    pausar()


# =============================================================================
# OPÇÃO 4: LISTAR CLIENTES
# =============================================================================

def listar_clientes():
    """Lista todos os clientes cadastrados no sistema"""
    limpar_tela()
    print("=" * 80)
    print("👥 CLIENTES CADASTRADOS NO SISTEMA")
    print("=" * 80)
    print()
    
    if not system.clients:
        print("⚠️  Nenhum cliente cadastrado no sistema.")
        pausar()
        return
    
    print(f"{'ID':<12} {'Nome':<30} {'Plano':<10} {'Uso':<20}")
    print("─" * 80)
    
    for client in system.clients:
        uso = f"{client.requisicoes_usadas}/{client.plan.max_requests}"
        percentage = client.usage_percentage()
        
        print(
            f"{client.id:<12} "
            f"{client.nome:<30} "
            f"{client.plan.nome:<10} "
            f"{uso:<10} ({percentage:.1f}%)"
        )
    
    print()
    print(f"📊 Total de clientes: {len(system.clients)}")
    pausar()


# =============================================================================
# OPÇÃO 5: VER REQUISIÇÕES DE UM CLIENTE
# =============================================================================

def ver_requisicoes_cliente():
    """Permite escolher um cliente e ver suas requisições"""
    limpar_tela()
    print("=" * 80)
    print("🔍 SELECIONAR CLIENTE PARA VER REQUISIÇÕES")
    print("=" * 80)
    print()
    
    if not system.clients:
        print("⚠️  Nenhum cliente cadastrado no sistema.")
        pausar()
        return
    
    # Listar clientes
    print("Clientes disponíveis:")
    print()
    for i, client in enumerate(system.clients, 1):
        print(f"   {i}. {client.nome} ({client.id}) - Plano {client.plan.nome}")
    
    print()
    print("   0. Voltar ao menu principal")
    print()
    
    # Escolher cliente
    try:
        escolha = input("👉 Escolha o número do cliente: ").strip()
        
        if escolha == "0":
            return
        
        indice = int(escolha) - 1
        
        if 0 <= indice < len(system.clients):
            client = system.clients[indice]
            exibir_requisicoes_cliente(client)
        else:
            print("\n❌ Opção inválida!")
            pausar()
    
    except ValueError:
        print("\n❌ Entrada inválida! Digite um número.")
        pausar()


def exibir_requisicoes_cliente(client):
    """Exibe todas as requisições de um cliente específico"""
    limpar_tela()
    print("=" * 80)
    print(f"📋 REQUISIÇÕES DO CLIENTE: {client.nome}")
    print("=" * 80)
    print()
    print(f"🆔 ID: {client.id}")
    print(f"📦 Plano: {client.plan.nome}")
    print(f"📊 Uso atual: {client.requisicoes_usadas}/{client.plan.max_requests}")
    print()
    
    # Buscar requisições deste cliente
    client_requests = system.get_requests_by_client(client.id)
    
    if not client_requests:
        print("⚠️  Nenhuma requisição registrada para este cliente.")
        print()
        print("💡 Dica: Use a opção '6 - Processar Nova Requisição' para criar requisições.")
        pausar()
        return
    
    print(f"Total de requisições: {len(client_requests)}")
    print()
    print("─" * 80)
    
    # Listar requisições
    for i, (req, dec) in enumerate(client_requests, 1):
        status = "✅ APROVADA" if dec.aprovada else "❌ REJEITADA"
        timestamp = req.get_formatted_timestamp("%d/%m/%Y %H:%M:%S")
        
        print(f"{i}. [{timestamp}] {status}")
        print(f"   Tipo: {req.payload.tipo}")
        print(f"   ID: {req.id[:16]}...")
        print()
    
    print("─" * 80)
    print()
    
    # Submenu: escolher requisição para ver detalhes
    escolher_requisicao_detalhada(client_requests)


def escolher_requisicao_detalhada(client_requests):
    """Permite escolher uma requisição para ver detalhes completos"""
    print("🔍 Ver detalhes de uma requisição específica")
    print()
    print(f"   Digite o número da requisição (1-{len(client_requests)})")
    print("   ou 0 para voltar")
    print()
    
    try:
        escolha = input("👉 Escolha: ").strip()
        
        if escolha == "0":
            return
        
        indice = int(escolha) - 1
        
        if 0 <= indice < len(client_requests):
            req, dec = client_requests[indice]
            exibir_detalhes_requisicao(req, dec)
        else:
            print("\n❌ Opção inválida!")
            pausar()
    
    except ValueError:
        print("\n❌ Entrada inválida! Digite um número.")
        pausar()


def exibir_detalhes_requisicao(request, decision):
    """Exibe todos os detalhes de uma requisição"""
    limpar_tela()
    print("=" * 80)
    print("🔍 DETALHES COMPLETOS DA REQUISIÇÃO")
    print("=" * 80)
    print()
    
    # Informações da Request
    print("📋 INFORMAÇÕES DA REQUISIÇÃO")
    print("─" * 80)
    print(f"🆔 Request ID: {request.id}")
    print(f"📅 Timestamp: {request.get_formatted_timestamp('%d/%m/%Y %H:%M:%S')}")
    print(f"⏱️  Idade: {request.age_in_seconds():.2f} segundos atrás")
    print()
    
    # Informações do Cliente
    print("👤 INFORMAÇÕES DO CLIENTE")
    print("─" * 80)
    print(f"🆔 Cliente ID: {request.client.id}")
    print(f"📛 Nome: {request.client.nome}")
    print(f"📦 Plano: {request.client.plan.nome}")
    print(f"📊 Uso no momento da request: {request.get_context()['requests_used_before']}/{request.client.plan.max_requests}")
    print()
    
    # Informações do Payload
    print("📦 INFORMAÇÕES DO PAYLOAD")
    print("─" * 80)
    print(f"🏷️  Tipo de Validação: {request.payload.tipo}")
    print(f"💾 Tamanho: {request.payload.size()} bytes")
    print(f"📄 Dados enviados:")
    for key, value in request.payload.dados.items():
        print(f"   • {key}: {value}")
    print()
    
    # Resultado da Decisão
    print("⚖️  DECISÃO DO MOTOR")
    print("─" * 80)
    status = "✅ APROVADA" if decision.aprovada else "❌ REJEITADA"
    print(f"Status: {status}")
    print(f"Motivo: {decision.motivo}")
    print(f"Categoria: {decision.get_category()}")
    print(f"Timestamp da decisão: {decision.get_formatted_timestamp('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Contexto Completo (para debugging)
    print("🔧 CONTEXTO TÉCNICO (DEBUG)")
    print("─" * 80)
    context = request.get_context()
    for key, value in context.items():
        print(f"   {key}: {value}")
    
    print()
    print("=" * 80)
    pausar()


# =============================================================================
# OPÇÃO 6: PROCESSAR NOVA REQUISIÇÃO
# =============================================================================

def processar_nova_requisicao():
    """Permite criar e processar uma nova requisição manualmente"""
    limpar_tela()
    print("=" * 80)
    print("➕ PROCESSAR NOVA REQUISIÇÃO")
    print("=" * 80)
    print()
    
    # Escolher cliente
    print("📋 PASSO 1: Selecionar Cliente")
    print()
    
    for i, client in enumerate(system.clients, 1):
        print(f"   {i}. {client.nome} ({client.id}) - Plano {client.plan.nome}")
    
    print()
    print("   0. Cancelar")
    print()
    
    try:
        escolha = input("👉 Escolha o cliente: ").strip()
        
        if escolha == "0":
            return
        
        indice = int(escolha) - 1
        
        if not (0 <= indice < len(system.clients)):
            print("\n❌ Opção inválida!")
            pausar()
            return
        
        client = system.clients[indice]
        
        # Escolher tipo de validação
        print()
        print("📋 PASSO 2: Selecionar Tipo de Validação")
        print()
        print("   1. Validação de CPF")
        print("   2. Validação de Endereço")
        print("   3. Validação de Dados Bancários")
        print()
        print("   0. Cancelar")
        print()
        
        tipo_escolha = input("👉 Escolha o tipo: ").strip()
        
        if tipo_escolha == "0":
            return
        
        tipo_map = {
            "1": (Payload.TIPO_CPF, criar_payload_cpf),
            "2": (Payload.TIPO_ENDERECO, criar_payload_endereco),
            "3": (Payload.TIPO_DADOS_BANCARIOS, criar_payload_bancario)
        }
        
        if tipo_escolha not in tipo_map:
            print("\n❌ Opção inválida!")
            pausar()
            return
        
        tipo, criar_payload_func = tipo_map[tipo_escolha]
        
        # Criar payload
        print()
        print("📋 PASSO 3: Fornecer Dados")
        print()
        
        dados = criar_payload_func()
        
        if dados is None:
            return
        
        # Criar e processar requisição
        payload = Payload(tipo=tipo, dados=dados)
        request, decision = system.process_request(client, payload)
        
        # Exibir resultado
        print()
        print("=" * 80)
        print("⚖️  RESULTADO DA REQUISIÇÃO")
        print("=" * 80)
        print()
        
        status = "✅ APROVADA" if decision.aprovada else "❌ REJEITADA"
        print(f"Status: {status}")
        print(f"Motivo: {decision.motivo}")
        print(f"Request ID: {request.id}")
        print()
        print(f"Uso do cliente: {client.requisicoes_usadas}/{client.plan.max_requests}")
        print()
        
        pausar()
    
    except ValueError:
        print("\n❌ Entrada inválida!")
        pausar()


def criar_payload_cpf():
    """Coleta dados para validação de CPF"""
    cpf = input("CPF: ").strip()
    nome = input("Nome: ").strip()
    
    if not cpf or not nome:
        print("\n❌ Todos os campos são obrigatórios!")
        pausar()
        return None
    
    return {"cpf": cpf, "nome": nome}


def criar_payload_endereco():
    """Coleta dados para validação de Endereço"""
    cep = input("CEP: ").strip()
    logradouro = input("Logradouro: ").strip()
    numero = input("Número: ").strip()
    
    if not cep or not logradouro or not numero:
        print("\n❌ Todos os campos são obrigatórios!")
        pausar()
        return None
    
    return {"cep": cep, "logradouro": logradouro, "numero": numero}


def criar_payload_bancario():
    """Coleta dados para validação de Dados Bancários"""
    banco = input("Banco: ").strip()
    agencia = input("Agência: ").strip()
    conta = input("Conta: ").strip()
    
    if not banco or not agencia or not conta:
        print("\n❌ Todos os campos são obrigatórios!")
        pausar()
        return None
    
    return {"banco": banco, "agencia": agencia, "conta": conta}


# =============================================================================
# LOOP PRINCIPAL DO MENU
# =============================================================================

def menu_principal():
    """Loop principal do sistema"""
    
    while True:
        limpar_tela()
        exibir_cabecalho()
        exibir_menu_principal()
        
        escolha = input("👉 Digite sua opção: ").strip()
        
        if escolha == "1":
            executar_simulador()
        
        elif escolha == "2":
            executar_cenarios()
        
        elif escolha == "3":
            executar_auditoria()
        
        elif escolha == "4":
            listar_clientes()
        
        elif escolha == "5":
            ver_requisicoes_cliente()
        
        elif escolha == "6":
            processar_nova_requisicao()
        
        elif escolha == "0":
            limpar_tela()
            print("=" * 80)
            print("👋 ENCERRANDO SISTEMA")
            print("=" * 80)
            print()
            print("✅ Sistema encerrado com sucesso!")
            print()
            print("📊 Estatísticas da sessão:")
            print(f"   • Clientes no sistema: {len(system.clients)}")
            print(f"   • Requisições processadas: {len(system.all_requests)}")
            print(f"   • Decisões aprovadas: {sum(1 for d in system.all_decisions if d.aprovada)}")
            print(f"   • Decisões rejeitadas: {sum(1 for d in system.all_decisions if not d.aprovada)}")
            print()
            print("🎉 Obrigado por usar o Motor de Decisão B2B!")
            print("=" * 80)
            print()
            break
        
        else:
            print("\n❌ Opção inválida! Digite um número de 0 a 6.")
            pausar()


# =============================================================================
# PONTO DE ENTRADA PRINCIPAL
# =============================================================================

def main():
    """Ponto de entrada do programa"""
    menu_principal()


if __name__ == "__main__":
    main()
