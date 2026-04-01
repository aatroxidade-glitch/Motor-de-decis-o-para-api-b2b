from app.domain.client import Client
from app.domain.payload import Payload
from app.domain.request import Request
from app.domain.plans import BASIC_PLAN, SILVER_PLAN, GOLD_PLAN
from app.application.decision_engine import DecisionEngine


class TestScenarios:
    """
    Executa cenários de teste específicos e determinísticos
    Valida edge cases e comportamento esperado do sistema
    """
    
    def __init__(self):
        self.engine = DecisionEngine()
        self.passed = 0
        self.failed = 0
        self.results = []
    
    def run_scenario(self, name, client, payload, expected_approved, expected_reason_contains=None):
        """
        Executa um cenário específico e valida o resultado
        
        Args:
            name: Nome descritivo do cenário
            client: Cliente que fará a requisição
            payload: Payload a ser validado
            expected_approved: True se deve ser aprovada, False se rejeitada
            expected_reason_contains: Substring esperada no motivo (opcional)
        """
        request = Request(client=client, payload=payload)
        decision = self.engine.evaluate(request)
        
        # Validação do resultado
        approved_match = decision.aprovada == expected_approved
        reason_match = True
        
        if expected_reason_contains:
            reason_match = expected_reason_contains.lower() in decision.motivo.lower()
        
        success = approved_match and reason_match
        
        if success:
            self.passed += 1
            status = "✅ PASSOU"
        else:
            self.failed += 1
            status = "❌ FALHOU"
        
        # Registra resultado
        result = {
            'name': name,
            'status': status,
            'expected_approved': expected_approved,
            'got_approved': decision.aprovada,
            'reason': decision.motivo,
            'success': success
        }
        self.results.append(result)
        
        return success
    
    # ========== CATEGORIA 1: RESTRIÇÕES DE PLANO ==========
    
    def test_basic_restricts_endereco(self):
        """Cenário 1: Basic tenta validar Endereço"""
        print("\n🔍 Cenário 1: Basic tenta validar Endereço")
        
        client = Client(id="test_001", nome="TechCorp Basic", plan=BASIC_PLAN)
        payload = Payload(
            tipo=Payload.TIPO_ENDERECO,
            dados={"cep": "12345-678", "logradouro": "Rua Teste", "numero": "123"}
        )
        
        return self.run_scenario(
            name="Basic rejeita Endereço",
            client=client,
            payload=payload,
            expected_approved=False,
            expected_reason_contains="não permite validação do tipo"
        )
    
    def test_silver_restricts_dados_bancarios(self):
        """Cenário 2: Silver tenta validar Dados Bancários"""
        print("🔍 Cenário 2: Silver tenta validar Dados Bancários")
        
        client = Client(id="test_002", nome="DataFlow Silver", plan=SILVER_PLAN)
        payload = Payload(
            tipo=Payload.TIPO_DADOS_BANCARIOS,
            dados={"banco": "001", "agencia": "1234", "conta": "56789-0"}
        )
        
        return self.run_scenario(
            name="Silver rejeita Dados Bancários",
            client=client,
            payload=payload,
            expected_approved=False,
            expected_reason_contains="não permite validação do tipo"
        )
    
    def test_gold_accepts_all_types(self):
        """Cenário 3: Gold valida todos os tipos"""
        print("🔍 Cenário 3: Gold valida todos os tipos")
        
        client = Client(id="test_003", nome="CloudSys Gold", plan=GOLD_PLAN)
        
        # Teste 1: CPF
        payload_cpf = Payload(
            tipo=Payload.TIPO_CPF,
            dados={"cpf": "12345678900", "nome": "João Silva"}
        )
        result1 = self.run_scenario(
            name="Gold aprova CPF",
            client=client,
            payload=payload_cpf,
            expected_approved=True
        )
        
        # Teste 2: Endereço
        payload_endereco = Payload(
            tipo=Payload.TIPO_ENDERECO,
            dados={"cep": "12345-678", "logradouro": "Rua Teste", "numero": "123"}
        )
        result2 = self.run_scenario(
            name="Gold aprova Endereço",
            client=client,
            payload=payload_endereco,
            expected_approved=True
        )
        
        # Teste 3: Dados Bancários
        payload_bancario = Payload(
            tipo=Payload.TIPO_DADOS_BANCARIOS,
            dados={"banco": "001", "agencia": "1234", "conta": "56789-0"}
        )
        result3 = self.run_scenario(
            name="Gold aprova Dados Bancários",
            client=client,
            payload=payload_bancario,
            expected_approved=True
        )
        
        return result1 and result2 and result3
    
    # ========== CATEGORIA 2: LIMITES DE USO ==========
    
    def test_basic_hits_exact_limit(self):
        """Cenário 4: Basic atinge limite exato (100 requests)"""
        print("\n🔍 Cenário 4: Basic atinge limite exato (100 requests)")
        
        client = Client(id="test_004", nome="LimitTest Basic", plan=BASIC_PLAN)
        payload = Payload(
            tipo=Payload.TIPO_CPF,
            dados={"cpf": "12345678900", "nome": "Teste Limite"}
        )
        
        # Simula 99 requisições já feitas
        client.requisicoes_usadas = 99
        
        # Request 100 (última permitida)
        result1 = self.run_scenario(
            name="Request 100 (última permitida)",
            client=client,
            payload=payload,
            expected_approved=True
        )
        
        # Request 101 (excede limite)
        result2 = self.run_scenario(
            name="Request 101 (excede limite)",
            client=client,
            payload=payload,
            expected_approved=False,
            expected_reason_contains="limite de requisições excedido"
        )
        
        return result1 and result2
    
    def test_silver_hits_limit(self):
        """Cenário 5: Silver no limite (500 requests)"""
        print("🔍 Cenário 5: Silver no limite (500 requests)")
        
        client = Client(id="test_005", nome="LimitTest Silver", plan=SILVER_PLAN)
        payload = Payload(
            tipo=Payload.TIPO_CPF,
            dados={"cpf": "12345678900", "nome": "Teste Limite Silver"}
        )
        
        # Simula 499 requisições já feitas
        client.requisicoes_usadas = 499
        
        # Request 500 (última permitida)
        result1 = self.run_scenario(
            name="Request 500 (última permitida)",
            client=client,
            payload=payload,
            expected_approved=True
        )
        
        # Request 501 (excede limite)
        result2 = self.run_scenario(
            name="Request 501 (excede limite)",
            client=client,
            payload=payload,
            expected_approved=False,
            expected_reason_contains="limite de requisições excedido"
        )
        
        return result1 and result2
    
    # ========== CATEGORIA 3: VALIDAÇÃO DE PAYLOAD ==========
    
    def test_cpf_missing_required_field(self):
        """Cenário 6: CPF sem campo obrigatório 'nome'"""
        print("\n🔍 Cenário 6: CPF sem campo obrigatório 'nome'")
        
        client = Client(id="test_006", nome="ValidationTest", plan=GOLD_PLAN)
        payload = Payload(
            tipo=Payload.TIPO_CPF,
            dados={"cpf": "12345678900"}  # Falta 'nome'
        )
        
        return self.run_scenario(
            name="CPF sem nome obrigatório",
            client=client,
            payload=payload,
            expected_approved=False,
            expected_reason_contains="campos obrigatórios ausentes"
        )
    
    def test_endereco_missing_numero(self):
        """Cenário 7: Endereço sem 'numero'"""
        print("🔍 Cenário 7: Endereço sem 'numero'")
        
        client = Client(id="test_007", nome="ValidationTest2", plan=GOLD_PLAN)
        payload = Payload(
            tipo=Payload.TIPO_ENDERECO,
            dados={"cep": "12345-678", "logradouro": "Rua Teste"}  # Falta 'numero'
        )
        
        return self.run_scenario(
            name="Endereço sem numero",
            client=client,
            payload=payload,
            expected_approved=False,
            expected_reason_contains="campos obrigatórios ausentes"
        )
    
    def test_dados_bancarios_wrong_type(self):
        """Cenário 8: Dados Bancários com tipo incorreto"""
        print("🔍 Cenário 8: Dados Bancários com tipo incorreto")
        
        client = Client(id="test_008", nome="TypeTest", plan=GOLD_PLAN)
        payload = Payload(
            tipo=Payload.TIPO_DADOS_BANCARIOS,
            dados={"banco": 123, "agencia": "1234", "conta": "56789"}  # 'banco' deveria ser str
        )
        
        return self.run_scenario(
            name="Dados Bancários com tipo incorreto",
            client=client,
            payload=payload,
            expected_approved=False,
            expected_reason_contains="deve ser str"
        )
    
    # ========== CATEGORIA 4: TAMANHO DE PAYLOAD ==========
    
    def test_oversized_payload_basic(self):
        """Cenário 9: Payload 2KB em plano Basic (limite 1KB)"""
        print("\n🔍 Cenário 9: Payload grande demais para Basic")
        
        client = Client(id="test_009", nome="SizeTest Basic", plan=BASIC_PLAN)
        
        # Cria payload com aproximadamente 2KB
        dados = {"cpf": "12345678900", "nome": "Teste", "extra": "x" * 2000}
        payload = Payload(tipo=Payload.TIPO_CPF, dados=dados)
        
        return self.run_scenario(
            name="Payload excede limite Basic",
            client=client,
            payload=payload,
            expected_approved=False,
            expected_reason_contains="excede limite"
        )
    
    def test_acceptable_size_gold(self):
        """Cenário 10: Payload 5KB em plano Gold (limite 100KB)"""
        print("🔍 Cenário 10: Payload aceitável em Gold")
        
        client = Client(id="test_010", nome="SizeTest Gold", plan=GOLD_PLAN)
        
        # Cria payload com aproximadamente 5KB (bem abaixo do limite de 100KB)
        dados = {"cpf": "12345678900", "nome": "Teste", "extra": "x" * 5000}
        payload = Payload(tipo=Payload.TIPO_CPF, dados=dados)
        
        return self.run_scenario(
            name="Payload OK em Gold",
            client=client,
            payload=payload,
            expected_approved=True
        )
    
    # ========== CATEGORIA 5: CASOS EXTREMOS ==========
    
    def test_empty_payload(self):
        """Cenário 11: Payload vazio"""
        print("\n🔍 Cenário 11: Payload vazio")
        
        client = Client(id="test_011", nome="EdgeTest", plan=GOLD_PLAN)
        payload = Payload(tipo=Payload.TIPO_CPF, dados={})
        
        return self.run_scenario(
            name="Payload vazio",
            client=client,
            payload=payload,
            expected_approved=False,
            expected_reason_contains="não pode estar vazio"
        )
    
    def test_last_available_request(self):
        """Cenário 12: Cliente no último request disponível"""
        print("🔍 Cenário 12: Último request disponível")
        
        client = Client(id="test_012", nome="EdgeTest2", plan=BASIC_PLAN)
        client.requisicoes_usadas = 99  # Já usou 99 de 100
        
        payload = Payload(
            tipo=Payload.TIPO_CPF,
            dados={"cpf": "12345678900", "nome": "Último Request"}
        )
        
        return self.run_scenario(
            name="Último request permitido",
            client=client,
            payload=payload,
            expected_approved=True
        )
    
    # ========== EXECUÇÃO E RELATÓRIO ==========
    
    def run_all(self):
        """Executa todos os cenários de teste"""
        print("\n" + "=" * 70)
        print("🧪 EXECUÇÃO DE CENÁRIOS DE TESTE ESPECÍFICOS")
        print("=" * 70)
        
        # Categoria 1: Restrições de Plano
        print("\n" + "=" * 70)
        print("📋 CATEGORIA 1: RESTRIÇÕES DE PLANO")
        print("=" * 70)
        self.test_basic_restricts_endereco()
        self.test_silver_restricts_dados_bancarios()
        self.test_gold_accepts_all_types()
        
        # Categoria 2: Limites de Uso
        print("\n" + "=" * 70)
        print("🔢 CATEGORIA 2: LIMITES DE USO")
        print("=" * 70)
        self.test_basic_hits_exact_limit()
        self.test_silver_hits_limit()
        
        # Categoria 3: Validação de Payload
        print("\n" + "=" * 70)
        print("✅ CATEGORIA 3: VALIDAÇÃO DE PAYLOAD")
        print("=" * 70)
        self.test_cpf_missing_required_field()
        self.test_endereco_missing_numero()
        self.test_dados_bancarios_wrong_type()
        
        # Categoria 4: Tamanho de Payload
        print("\n" + "=" * 70)
        print("📦 CATEGORIA 4: TAMANHO DE PAYLOAD")
        print("=" * 70)
        self.test_oversized_payload_basic()
        self.test_acceptable_size_gold()
        
        # Categoria 5: Casos Extremos
        print("\n" + "=" * 70)
        print("⚠️ CATEGORIA 5: CASOS EXTREMOS")
        print("=" * 70)
        self.test_empty_payload()
        self.test_last_available_request()
        
        # Exibir relatório final
        self.print_report()
    
    def print_report(self):
        """Exibe relatório final dos testes"""
        print("\n" + "=" * 70)
        print("📊 RELATÓRIO FINAL DE TESTES")
        print("=" * 70)
        print()
        
        total = len(self.results)
        print(f"📈 RESUMO GERAL")
        print(f"   Total de cenários: {total}")
        print(f"   ✅ Passou: {self.passed} ({self.passed/total*100:.1f}%)")
        print(f"   ❌ Falhou: {self.failed} ({self.failed/total*100:.1f}%)")
        print()
        
        # Detalhes dos cenários
        print("📋 DETALHAMENTO POR CENÁRIO")
        print()
        
        for i, result in enumerate(self.results, 1):
            print(f"{i}. {result['status']} {result['name']}")
            
            if not result['success']:
                print(f"   ⚠️ Esperado: {'Aprovada' if result['expected_approved'] else 'Rejeitada'}")
                print(f"   ⚠️ Obtido: {'Aprovada' if result['got_approved'] else 'Rejeitada'}")
                print(f"   ⚠️ Motivo: {result['reason']}")
            
            print()
        
        print("=" * 70)
        
        if self.failed == 0:
            print("🎉 TODOS OS CENÁRIOS PASSARAM!")
        else:
            print(f"⚠️ {self.failed} CENÁRIO(S) FALHARAM")
        
        print("=" * 70)


def main():
    """Executa todos os cenários de teste"""
    tester = TestScenarios()
    tester.run_all()


if __name__ == "__main__":
    main()