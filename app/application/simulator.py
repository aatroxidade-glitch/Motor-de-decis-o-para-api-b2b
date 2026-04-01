import random
from app.domain.client import Client
from app.domain.payload import Payload
from app.domain.request import Request
from app.domain.plans import BASIC_PLAN, SILVER_PLAN, GOLD_PLAN
from app.application.decision_engine import DecisionEngine


class Simulator:
    """Simula uso real do sistema com múltiplos clientes e requisições"""
    
    def __init__(self):
        self.clients = []
        self.engine = DecisionEngine()
        self.results = []
    
    def setup_clients(self, quantidade=10):
        """
        Cria clientes com distribuição realista de planos
        60% Basic, 30% Silver, 10% Gold
        """
        planos = [BASIC_PLAN, SILVER_PLAN, GOLD_PLAN]
        distribuicao = [0.6, 0.3, 0.1]
        
        empresas = [
            "TechCorp", "DataFlow", "CloudSys", "ApiHub", "DevTools",
            "SyncPro", "LogicNet", "CodeBase", "AppStream", "InfoTech",
            "ByteWorks", "NetCore", "SoftWave", "DigiServ", "ProCode"
        ]
        
        for i in range(quantidade):
            plano = random.choices(planos, weights=distribuicao)[0]
            nome_empresa = f"{empresas[i % len(empresas)]} #{i+1}"
            
            cliente = Client(
                id=f"client_{i+1:03d}",
                nome=nome_empresa,
                plan=plano
            )
            self.clients.append(cliente)
        
        print(f"✅ {quantidade} clientes criados")
        print(f"   Basic: {sum(1 for c in self.clients if c.plan.nome == 'Basic')}")
        print(f"   Silver: {sum(1 for c in self.clients if c.plan.nome == 'Silver')}")
        print(f"   Gold: {sum(1 for c in self.clients if c.plan.nome == 'Gold')}")
        print()
    
    def _generate_valid_payload(self, tipo):
        """Gera payload válido para um tipo específico"""
        if tipo == Payload.TIPO_CPF:
            return {
                "cpf": "12345678900",
                "nome": "João Silva"
            }
        elif tipo == Payload.TIPO_ENDERECO:
            return {
                "cep": "12345-678",
                "logradouro": "Rua das Flores",
                "numero": "123"
            }
        elif tipo == Payload.TIPO_DADOS_BANCARIOS:
            return {
                "banco": "001",
                "agencia": "1234",
                "conta": "56789-0"
            }
    
    def _generate_invalid_payload(self, tipo):
        """Gera payload inválido (faltando campos)"""
        if tipo == Payload.TIPO_CPF:
            return {"cpf": "12345678900"}  # falta 'nome'
        elif tipo == Payload.TIPO_ENDERECO:
            return {"cep": "12345-678"}  # falta 'logradouro' e 'numero'
        elif tipo == Payload.TIPO_DADOS_BANCARIOS:
            return {"banco": "001"}  # falta 'agencia' e 'conta'
    
    def _generate_oversized_payload(self, tipo):
        """Gera payload que excede limite de tamanho"""
        dados = self._generate_valid_payload(tipo)
        # Adiciona campo muito grande
        dados["campo_extra"] = "x" * 200000  # 200KB
        return dados
    
    def generate_requests(self, requests_por_cliente=5):
        """
        Gera requisições variadas para cada cliente
        Mix de válidas, inválidas, tipos não permitidos, etc
        """
        requests = []
        
        for cliente in self.clients:
            tipos_permitidos = cliente.plan.tipos_permitidos
            
            for _ in range(requests_por_cliente):
                # 50% chance de ser válida
                if random.random() < 0.5:
                    tipo = random.choice(tipos_permitidos)
                    dados = self._generate_valid_payload(tipo)
                
                # 20% chance de payload inválido
                elif random.random() < 0.7:
                    tipo = random.choice(tipos_permitidos)
                    dados = self._generate_invalid_payload(tipo)
                
                # 15% chance de tipo não permitido
                elif random.random() < 0.85:
                    todos_tipos = [Payload.TIPO_CPF, Payload.TIPO_ENDERECO, Payload.TIPO_DADOS_BANCARIOS]
                    tipos_nao_permitidos = [t for t in todos_tipos if t not in tipos_permitidos]
                    if tipos_nao_permitidos:
                        tipo = random.choice(tipos_nao_permitidos)
                        dados = self._generate_valid_payload(tipo)
                    else:
                        tipo = random.choice(tipos_permitidos)
                        dados = self._generate_valid_payload(tipo)
                
                # 15% chance de payload muito grande
                else:
                    tipo = random.choice(tipos_permitidos)
                    dados = self._generate_oversized_payload(tipo)
                
                payload = Payload(tipo=tipo, dados=dados)
                request = Request(client=cliente, payload=payload)
                requests.append(request)
        
        print(f"✅ {len(requests)} requisições geradas ({requests_por_cliente} por cliente)")
        print()
        return requests
    
    def run_simulation(self, requests):
        """Processa todas as requisições através do motor de decisão"""
        print("🔄 Processando requisições...\n")
        
        for i, request in enumerate(requests, 1):
            decision = self.engine.evaluate(request)
            self.results.append({
                'request_id': request.id,
                'client_id': request.client.id,
                'client_name': request.client.nome,
                'plan': request.client.plan.nome,
                'payload_type': request.payload.tipo,
                'approved': decision.aprovada,
                'reason': decision.motivo
            })
            
            # Progresso visual
            if i % 10 == 0:
                print(f"   Processadas: {i}/{len(requests)}")
        
        print(f"\n✅ Simulação concluída: {len(requests)} requisições processadas\n")
    
    def print_results(self):
        """Exibe estatísticas e exemplos de decisões"""
        total = len(self.results)
        aprovadas = sum(1 for r in self.results if r['approved'])
        rejeitadas = total - aprovadas
        
        print("=" * 70)
        print("📊 RELATÓRIO DA SIMULAÇÃO")
        print("=" * 70)
        print()
        
        # Estatísticas gerais
        print("📈 ESTATÍSTICAS GERAIS")
        print(f"   Total de requisições: {total}")
        print(f"   ✅ Aprovadas: {aprovadas} ({aprovadas/total*100:.1f}%)")
        print(f"   ❌ Rejeitadas: {rejeitadas} ({rejeitadas/total*100:.1f}%)")
        print()
        
        # Motivos de rejeição
        print("🚫 MOTIVOS DE REJEIÇÃO")
        motivos = {}
        for r in self.results:
            if not r['approved']:
                # Simplifica o motivo para categoria
                if "não permite validação do tipo" in r['reason']:
                    categoria = "Tipo não permitido pelo plano"
                elif "Payload inválido" in r['reason']:
                    categoria = "Payload inválido"
                elif "excede limite" in r['reason']:
                    categoria = "Payload muito grande"
                elif "Limite de requisições excedido" in r['reason']:
                    categoria = "Limite de requests excedido"
                else:
                    categoria = "Outro"
                
                motivos[categoria] = motivos.get(categoria, 0) + 1
        
        for motivo, count in sorted(motivos.items(), key=lambda x: x[1], reverse=True):
            print(f"   {motivo}: {count}")
        print()
        
        # Desempenho por plano
        print("📋 DESEMPENHO POR PLANO")
        planos_stats = {}
        for r in self.results:
            plano = r['plan']
            if plano not in planos_stats:
                planos_stats[plano] = {'total': 0, 'aprovadas': 0}
            planos_stats[plano]['total'] += 1
            if r['approved']:
                planos_stats[plano]['aprovadas'] += 1
        
        for plano, stats in sorted(planos_stats.items()):
            taxa = stats['aprovadas'] / stats['total'] * 100
            print(f"   {plano}: {stats['aprovadas']}/{stats['total']} aprovadas ({taxa:.1f}%)")
        print()
        
        # Exemplos de decisões
        print("💡 EXEMPLOS DE DECISÕES")
        print()
        
        # 1 exemplo aprovado
        aprovado = next((r for r in self.results if r['approved']), None)
        if aprovado:
            print(f"   ✅ APROVADA")
            print(f"      Cliente: {aprovado['client_name']} ({aprovado['plan']})")
            print(f"      Tipo: {aprovado['payload_type']}")
            print(f"      Motivo: {aprovado['reason']}")
            print()
        
        # Exemplos de cada tipo de rejeição
        exemplos_mostrados = set()
        for r in self.results:
            if not r['approved']:
                # Categoriza
                if "não permite validação do tipo" in r['reason']:
                    categoria = "tipo"
                elif "Payload inválido" in r['reason']:
                    categoria = "payload"
                elif "excede limite" in r['reason']:
                    categoria = "tamanho"
                elif "Limite de requisições excedido" in r['reason']:
                    categoria = "limite"
                else:
                    continue
                
                if categoria not in exemplos_mostrados:
                    print(f"   ❌ REJEITADA ({categoria.upper()})")
                    print(f"      Cliente: {r['client_name']} ({r['plan']})")
                    print(f"      Tipo: {r['payload_type']}")
                    print(f"      Motivo: {r['reason']}")
                    print()
                    exemplos_mostrados.add(categoria)
                
                if len(exemplos_mostrados) >= 4:
                    break
        
        print("=" * 70)


def main():
    """Executa simulação completa"""
    print("\n" + "=" * 70)
    print("🚀 SIMULADOR DO MOTOR DE DECISÃO B2B")
    print("=" * 70)
    print()
    
    # Configuração
    NUM_CLIENTES = 10
    REQUESTS_POR_CLIENTE = 5
    
    # Executar simulação
    simulator = Simulator()
    simulator.setup_clients(NUM_CLIENTES)
    requests = simulator.generate_requests(REQUESTS_POR_CLIENTE)
    simulator.run_simulation(requests)
    simulator.print_results()
    
    print("\n✨ Simulação concluída com sucesso!\n")


if __name__ == "__main__":
    main()