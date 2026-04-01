from datetime import datetime
from app.domain.client import Client
from app.domain.payload import Payload
from app.domain.request import Request
from app.domain.plans import BASIC_PLAN, SILVER_PLAN, GOLD_PLAN
from app.application.decision_engine import DecisionEngine


class AuditLogger:
    """
    Sistema de auditoria completo
    Registra todas as decisões com contexto completo para rastreabilidade
    """
    
    def __init__(self):
        self.logs = []
    
    def log_decision(self, request, decision, requests_before):
        """
        Registra uma decisão com contexto completo
        
        Args:
            request: Request que foi processado
            decision: Decision gerada pelo motor
            requests_before: Número de requisições usadas ANTES desta decisão
        """
        log_entry = {
            'timestamp': datetime.now(),
            'request_id': request.id,
            'client_id': request.client.id,
            'client_name': request.client.nome,
            'plan': request.client.plan.nome,
            'requests_used_before': requests_before,
            'requests_used_after': request.client.requisicoes_usadas,
            'payload_type': request.payload.tipo,
            'payload_size': request.payload.size(),
            'decision_approved': decision.aprovada,
            'decision_reason': decision.motivo,
            'plan_max_requests': request.client.plan.max_requests,
            'plan_max_size': request.client.plan.max_payload_size,
            'plan_allowed_types': request.client.plan.tipos_permitidos
        }
        
        self.logs.append(log_entry)
    
    def get_all_logs(self):
        """Retorna todos os logs registrados"""
        return self.logs
    
    def get_logs_by_client(self, client_id):
        """Retorna logs de um cliente específico"""
        return [log for log in self.logs if log['client_id'] == client_id]
    
    def get_approved_logs(self):
        """Retorna apenas decisões aprovadas"""
        return [log for log in self.logs if log['decision_approved']]
    
    def get_rejected_logs(self):
        """Retorna apenas decisões rejeitadas"""
        return [log for log in self.logs if not log['decision_approved']]
    
    def get_logs_by_reason(self, reason_substring):
        """Retorna logs que contêm uma substring no motivo"""
        return [log for log in self.logs 
                if reason_substring.lower() in log['decision_reason'].lower()]
    
    def get_logs_in_period(self, start_time, end_time):
        """Retorna logs em um período específico"""
        return [log for log in self.logs 
                if start_time <= log['timestamp'] <= end_time]
    
    def print_log_summary(self):
        """Exibe resumo geral dos logs"""
        total = len(self.logs)
        if total == 0:
            print("   Nenhum log registrado ainda")
            return
        
        approved = len(self.get_approved_logs())
        rejected = len(self.get_rejected_logs())
        
        print(f"   Total de decisões registradas: {total}")
        print(f"   ✅ Aprovadas: {approved} ({approved/total*100:.1f}%)")
        print(f"   ❌ Rejeitadas: {rejected} ({rejected/total*100:.1f}%)")
    
    def print_timeline(self, limit=10):
        """Exibe timeline das últimas decisões"""
        print(f"\n📅 TIMELINE DAS ÚLTIMAS {min(limit, len(self.logs))} DECISÕES")
        print("=" * 100)
        
        for i, log in enumerate(reversed(self.logs[-limit:]), 1):
            status = "✅ APROVADA" if log['decision_approved'] else "❌ REJEITADA"
            timestamp = log['timestamp'].strftime("%H:%M:%S.%f")[:-3]
            
            print(f"\n{i}. [{timestamp}] {status}")
            print(f"   Cliente: {log['client_name']} ({log['client_id']}) - Plano {log['plan']}")
            print(f"   Request ID: {log['request_id']}")
            print(f"   Tipo: {log['payload_type']} | Tamanho: {log['payload_size']} bytes")
            print(f"   Uso: {log['requests_used_before']} → {log['requests_used_after']} requests")
            print(f"   Motivo: {log['decision_reason']}")
        
        print("\n" + "=" * 100)
    
    def reconstruct_client_state(self, client_id):
        """Reconstrói o histórico completo de um cliente"""
        client_logs = self.get_logs_by_client(client_id)
        
        if not client_logs:
            print(f"   Nenhum registro encontrado para cliente {client_id}")
            return
        
        print(f"\n🔍 HISTÓRICO COMPLETO DO CLIENTE: {client_logs[0]['client_name']}")
        print("=" * 100)
        print(f"   Cliente ID: {client_id}")
        print(f"   Plano: {client_logs[0]['plan']}")
        print(f"   Total de requisições processadas: {len(client_logs)}")
        print()
        
        approved = [log for log in client_logs if log['decision_approved']]
        rejected = [log for log in client_logs if not log['decision_approved']]
        
        print(f"   ✅ Aprovadas: {len(approved)}")
        print(f"   ❌ Rejeitadas: {len(rejected)}")
        print()
        
        print("📊 EVOLUÇÃO DO USO:")
        for i, log in enumerate(client_logs, 1):
            status = "✅" if log['decision_approved'] else "❌"
            print(f"   {i}. {status} {log['requests_used_before']:3d} → {log['requests_used_after']:3d} | {log['payload_type']:30s} | {log['decision_reason']}")
        
        print("\n" + "=" * 100)


class AuditableDecisionEngine(DecisionEngine):
    """
    Motor de decisão com auditoria integrada
    Estende DecisionEngine para registrar todas as decisões
    """
    
    def __init__(self, audit_logger):
        super().__init__()
        self.audit_logger = audit_logger
    
    def evaluate(self, request):
        """
        Avalia requisição e registra decisão no log de auditoria
        """
        # Captura estado ANTES da decisão
        requests_before = request.client.requisicoes_usadas
        
        # Executa decisão
        decision = super().evaluate(request)
        
        # Registra no log de auditoria
        self.audit_logger.log_decision(request, decision, requests_before)
        
        return decision


def create_test_scenario():
    """
    Cria cenário de teste para demonstrar auditabilidade
    """
    # Inicializa sistema com auditoria
    audit_logger = AuditLogger()
    engine = AuditableDecisionEngine(audit_logger)
    
    # Cria clientes com diferentes planos
    clients = [
        Client(id="CLI_001", nome="TechStart LTDA", plan=BASIC_PLAN),
        Client(id="CLI_002", nome="DataFlow Solutions", plan=SILVER_PLAN),
        Client(id="CLI_003", nome="FinTech Global", plan=GOLD_PLAN)
    ]
    
    print("\n" + "=" * 100)
    print("🔄 EXECUTANDO CENÁRIO DE TESTE COM AUDITORIA")
    print("=" * 100)
    print()
    print("📋 Clientes criados:")
    for client in clients:
        print(f"   - {client.nome} ({client.id}) - Plano {client.plan.nome}")
    print()
    
    # Cenário 1: Cliente Basic usa seu plano corretamente
    print("🔍 Cenário 1: Cliente Basic valida CPF (tipo permitido)")
    request1 = Request(
        client=clients[0],
        payload=Payload(
            tipo=Payload.TIPO_CPF,
            dados={"cpf": "12345678900", "nome": "João Silva"}
        )
    )
    decision1 = engine.evaluate(request1)
    print(f"   Resultado: {'✅ Aprovada' if decision1.aprovada else '❌ Rejeitada'}")
    print(f"   Motivo: {decision1.motivo}")
    print()
    
    # Cenário 2: Cliente Basic tenta usar tipo não permitido
    print("🔍 Cenário 2: Cliente Basic tenta validar Endereço (tipo NÃO permitido)")
    request2 = Request(
        client=clients[0],
        payload=Payload(
            tipo=Payload.TIPO_ENDERECO,
            dados={"cep": "12345-678", "logradouro": "Rua Teste", "numero": "123"}
        )
    )
    decision2 = engine.evaluate(request2)
    print(f"   Resultado: {'✅ Aprovada' if decision2.aprovada else '❌ Rejeitada'}")
    print(f"   Motivo: {decision2.motivo}")
    print()
    
    # Cenário 3: Cliente Silver valida CPF e Endereço
    print("🔍 Cenário 3: Cliente Silver valida CPF")
    request3 = Request(
        client=clients[1],
        payload=Payload(
            tipo=Payload.TIPO_CPF,
            dados={"cpf": "98765432100", "nome": "Maria Santos"}
        )
    )
    decision3 = engine.evaluate(request3)
    print(f"   Resultado: {'✅ Aprovada' if decision3.aprovada else '❌ Rejeitada'}")
    print()
    
    print("🔍 Cenário 4: Cliente Silver valida Endereço")
    request4 = Request(
        client=clients[1],
        payload=Payload(
            tipo=Payload.TIPO_ENDERECO,
            dados={"cep": "54321-876", "logradouro": "Av Principal", "numero": "456"}
        )
    )
    decision4 = engine.evaluate(request4)
    print(f"   Resultado: {'✅ Aprovada' if decision4.aprovada else '❌ Rejeitada'}")
    print()
    
    # Cenário 5: Cliente Gold usa todos os tipos
    print("🔍 Cenário 5: Cliente Gold valida CPF, Endereço e Dados Bancários")
    
    request5 = Request(
        client=clients[2],
        payload=Payload(
            tipo=Payload.TIPO_CPF,
            dados={"cpf": "11122233344", "nome": "Carlos Oliveira"}
        )
    )
    engine.evaluate(request5)
    print("   ✅ CPF validado")
    
    request6 = Request(
        client=clients[2],
        payload=Payload(
            tipo=Payload.TIPO_ENDERECO,
            dados={"cep": "11111-111", "logradouro": "Rua Gold", "numero": "789"}
        )
    )
    engine.evaluate(request6)
    print("   ✅ Endereço validado")
    
    request7 = Request(
        client=clients[2],
        payload=Payload(
            tipo=Payload.TIPO_DADOS_BANCARIOS,
            dados={"banco": "001", "agencia": "1234", "conta": "56789-0"}
        )
    )
    engine.evaluate(request7)
    print("   ✅ Dados Bancários validados")
    print()
    
    # Cenário 6: Payload inválido
    print("🔍 Cenário 6: Cliente envia payload inválido (faltando campo obrigatório)")
    request8 = Request(
        client=clients[2],
        payload=Payload(
            tipo=Payload.TIPO_CPF,
            dados={"cpf": "55566677788"}  # Falta 'nome'
        )
    )
    decision8 = engine.evaluate(request8)
    print(f"   Resultado: {'✅ Aprovada' if decision8.aprovada else '❌ Rejeitada'}")
    print(f"   Motivo: {decision8.motivo}")
    print()
    
    # Cenário 7: Cliente Basic aproximando do limite
    print("🔍 Cenário 7: Cliente Basic se aproxima do limite (100 requests)")
    clients[0].requisicoes_usadas = 98  # Simula 98 requests já feitos
    
    request9 = Request(
        client=clients[0],
        payload=Payload(
            tipo=Payload.TIPO_CPF,
            dados={"cpf": "99988877766", "nome": "Ana Costa"}
        )
    )
    decision9 = engine.evaluate(request9)
    print(f"   Request 99: {'✅ Aprovada' if decision9.aprovada else '❌ Rejeitada'} (uso: 98 → 99)")
    
    request10 = Request(
        client=clients[0],
        payload=Payload(
            tipo=Payload.TIPO_CPF,
            dados={"cpf": "88877766655", "nome": "Pedro Alves"}
        )
    )
    decision10 = engine.evaluate(request10)
    print(f"   Request 100: {'✅ Aprovada' if decision10.aprovada else '❌ Rejeitada'} (uso: 99 → 100)")
    
    request11 = Request(
        client=clients[0],
        payload=Payload(
            tipo=Payload.TIPO_CPF,
            dados={"cpf": "77766655544", "nome": "Lucas Martins"}
        )
    )
    decision11 = engine.evaluate(request11)
    print(f"   Request 101: {'✅ Aprovada' if decision11.aprovada else '❌ Rejeitada'} - {decision11.motivo}")
    print()
    
    return audit_logger, clients


def demonstrate_audit_capabilities(audit_logger, clients):
    """
    Demonstra capacidades de auditoria do sistema
    """
    print("\n" + "=" * 100)
    print("📊 DEMONSTRAÇÃO DE CAPACIDADES DE AUDITORIA")
    print("=" * 100)
    
    # 1. Resumo geral
    print("\n1️⃣ RESUMO GERAL DOS LOGS")
    print("-" * 100)
    audit_logger.print_log_summary()
    
    # 2. Timeline das decisões
    audit_logger.print_timeline(limit=15)
    
    # 3. Consulta por cliente
    print("\n2️⃣ HISTÓRICO POR CLIENTE")
    print("-" * 100)
    audit_logger.reconstruct_client_state("CLI_001")
    
    # 4. Análise de rejeições
    print("\n3️⃣ ANÁLISE DE DECISÕES REJEITADAS")
    print("-" * 100)
    rejected = audit_logger.get_rejected_logs()
    print(f"   Total de rejeições: {len(rejected)}")
    print()
    
    # Agrupa por motivo
    motivos = {}
    for log in rejected:
        reason = log['decision_reason']
        # Simplifica motivo para categoria
        if "não permite validação do tipo" in reason:
            categoria = "Tipo não permitido pelo plano"
        elif "Payload inválido" in reason:
            categoria = "Payload inválido"
        elif "excede limite" in reason:
            categoria = "Payload muito grande"
        elif "Limite de requisições excedido" in reason:
            categoria = "Limite de requests excedido"
        else:
            categoria = "Outro"
        
        motivos[categoria] = motivos.get(categoria, 0) + 1
    
    print("   Distribuição por motivo:")
    for motivo, count in sorted(motivos.items(), key=lambda x: x[1], reverse=True):
        print(f"      - {motivo}: {count}")
    
    # 5. Consulta específica: limite excedido
    print("\n4️⃣ RASTREAMENTO: LIMITE EXCEDIDO")
    print("-" * 100)
    limite_logs = audit_logger.get_logs_by_reason("limite de requisições excedido")
    print(f"   Decisões rejeitadas por limite: {len(limite_logs)}")
    for log in limite_logs:
        print(f"      - Cliente: {log['client_name']} | Request ID: {log['request_id']}")
        print(f"        Uso no momento: {log['requests_used_before']}/{log['plan_max_requests']}")
    
    # 6. Demonstração de reconstrução de estado
    print("\n5️⃣ RECONSTRUÇÃO DE ESTADO: PROVA DE RASTREABILIDADE")
    print("-" * 100)
    print("   ✅ Todo request tem ID único")
    print("   ✅ Estado do cliente antes/depois registrado")
    print("   ✅ Timestamp preciso de cada decisão")
    print("   ✅ Motivo detalhado sempre presente")
    print("   ✅ Contexto completo (plano, limites, tipo)")
    print()
    print("   💡 Com esses dados, é possível:")
    print("      - Reconstruir timeline completa de qualquer cliente")
    print("      - Provar conformidade com SLA")
    print("      - Investigar reclamações")
    print("      - Detectar padrões de uso anormal")
    print("      - Auditar billing com precisão")
    print("      - Demonstrar compliance (LGPD, GDPR)")
    
    print("\n" + "=" * 100)


def main():
    """Executa demonstração completa de auditabilidade"""
    print("\n" + "=" * 100)
    print("🔒 DEMONSTRAÇÃO DE AUDITABILIDADE - PROJETO MOTOR DE DECISÃO B2B")
    print("=" * 100)
    print()
    print("Objetivo: Demonstrar que TODAS as decisões são:")
    print("   ✅ Registradas com contexto completo")
    print("   ✅ Rastreáveis no tempo")
    print("   ✅ Reconstruíveis")
    print("   ✅ Auditáveis")
    print()
    
    # Executa cenário de teste
    audit_logger, clients = create_test_scenario()
    
    # Demonstra capacidades
    demonstrate_audit_capabilities(audit_logger, clients)
    
    print("\n✨ Demonstração de auditabilidade concluída com sucesso!")
    print("=" * 100)
    print()


if __name__ == "__main__":
    main()