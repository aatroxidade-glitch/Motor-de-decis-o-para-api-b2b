"""
Módulo DecisionEngine - Camada de Aplicação

Motor de decisão responsável por avaliar requisições e aplicar regras de negócio.

Este é o coração do sistema, orquestrando validações e tomando decisões
automáticas sobre aprovar ou rejeitar requisições de clientes B2B.

Características:
    - Validação sequencial (fail-fast)
    - Decisões determinísticas (mesma entrada = mesma saída)
    - Sem side effects em rejeições (quota preservada)
    - Auditável (toda decisão tem motivo explícito)

Autor: [Cristóvão Caldeira Dos Reis]
Data: Janeiro 2026
"""

from app.domain.decision import Decision
from app.domain.request import Request


class DecisionEngine:
    """
    Motor de decisão automatizado para API B2B de validação de dados.
    
    Responsabilidades:
        - Orquestrar validações em sequência
        - Aplicar regras de negócio do domínio
        - Gerar decisões automáticas (aprovar/rejeitar)
        - Incrementar uso apenas em aprovações
        - Garantir rastreabilidade de decisões
    
    Design Pattern:
        Strategy Pattern (implícito) - Validações são estratégias aplicadas
        sequencialmente. Fail-fast: para na primeira que falhar.
    
    Fluxo de Validação (6 etapas):
        1. Tipo de validação é permitido pelo plano?
        2. Payload tem estrutura válida?
        3. Payload tem campos obrigatórios?
        4. Payload tem tipos de dados corretos?
        5. Payload respeita limite de tamanho?
        6. Cliente não excedeu limite de requisições?
        
        Se TODAS passarem: Aprova + Incrementa uso
        Se QUALQUER falhar: Rejeita + Mantém uso
    
    Regras Críticas:
        - Uso só é incrementado em aprovações (não gasta quota em rejeições)
        - Validações são executadas em ordem específica (otimização)
        - Decisões são imutáveis após retorno
        - Todo resultado tem justificativa explícita
    
    Exemplo:
        >>> from app.domain.client import Client
        >>> from app.domain.payload import Payload
        >>> from app.domain.request import Request
        >>> from app.domain.plans import BASIC_PLAN
        >>> 
        >>> engine = DecisionEngine()
        >>> cliente = Client("001", "Empresa X", BASIC_PLAN)
        >>> payload = Payload("validacao_cpf", {"cpf": "123", "nome": "João"})
        >>> request = Request(client=cliente, payload=payload)
        >>> 
        >>> decision = engine.evaluate(request)
        >>> print(decision.aprovada)  # True
        >>> print(cliente.requisicoes_usadas)  # 1 (incrementado)
    """
    
    def __init__(self):
        """
        Inicializa o motor de decisão.
        
        Comportamento:
            Motor é stateless. Não mantém histórico de decisões.
            Cada chamada a evaluate() é independente.
        """
        pass
    
    def evaluate(self, request: Request) -> Decision:
        """
        Avalia uma requisição e retorna decisão automática.
        
        Este é o método principal do motor. Executa todas as validações
        em sequência e retorna Decision com resultado e motivo.
        
        Args:
            request: Requisição contendo cliente e payload
        
        Returns:
            Decision: Decisão aprovada ou rejeitada com motivo explícito
        
        Side Effects:
            Se aprovada: Incrementa request.client.requisicoes_usadas
            Se rejeitada: Nenhum (quota preservada)
        
        Fluxo de Validação:
            1. Tipo permitido pelo plano? (validação mais rápida primeiro)
            2. Payload estruturalmente válido?
            3. Payload respeita tamanho máximo?
            4. Cliente não excedeu limite de requests?
            
            Se todas passarem: APROVAR + incrementar uso
            Se qualquer falhar: REJEITAR + preservar uso
        
        Exemplo de Uso:
            >>> engine = DecisionEngine()
            >>> decision = engine.evaluate(request)
            >>> 
            >>> if decision.is_approved():
            ...     print("Prosseguir com validação")
            ... else:
            ...     print(f"Rejeitada: {decision.motivo}")
        
        Exemplo de Decisões Retornadas:
            Aprovada:
                Decision(True, "Requisição autorizada: validacao_cpf")
            
            Rejeitada por plano:
                Decision(False, "Plano Basic não permite validação do tipo 'validacao_endereco'")
            
            Rejeitada por payload:
                Decision(False, "Payload inválido: Campos obrigatórios ausentes: nome")
            
            Rejeitada por tamanho:
                Decision(False, "Payload excede limite do plano Basic")
            
            Rejeitada por limite:
                Decision(False, "Limite de requisições excedido")
        """
        
        # VALIDAÇÃO 1: Tipo de validação permitido pelo plano
        # Mais rápida, executa primeiro (fail-fast otimizado)
        if not self._validate_validation_type(request):
            return Decision(
                aprovada=False,
                motivo=f"Plano {request.client.plan.nome} não permite validação do tipo '{request.payload.tipo}'"
            )
        
        # VALIDAÇÃO 2: Estrutura completa do payload
        # Valida: estrutura + campos obrigatórios + tipos de dados
        valido, mensagem = request.payload.validar_completo()
        if not valido:
            return Decision(
                aprovada=False,
                motivo=f"Payload inválido: {mensagem}"
            )
        
        # VALIDAÇÃO 3: Tamanho do payload vs plano
        if not self._validate_payload_size(request):
            return Decision(
                aprovada=False,
                motivo=f"Payload excede limite do plano {request.client.plan.nome}"
            )
        
        # VALIDAÇÃO 4: Limite de requisições
        if not self._validate_request_limit(request):
            return Decision(
                aprovada=False,
                motivo="Limite de requisições excedido"
            )
        
        # TODAS AS VALIDAÇÕES PASSARAM: APROVAR
        # Side effect: incrementa uso (registra consumo)
        request.client.increment_usage()
        
        return Decision(
            aprovada=True,
            motivo=f"Requisição autorizada: {request.payload.tipo}"
        )
    
    def evaluate_batch(self, requests: list[Request]) -> list[Decision]:
        """
        Avalia múltiplas requisições em lote.
        
        Args:
            requests: Lista de requisições a avaliar
        
        Returns:
            list[Decision]: Lista de decisões na mesma ordem
        
        Comportamento:
            Cada requisição é avaliada independentemente.
            Falha em uma não afeta as outras.
        
        Útil para:
            - Processar lotes de requisições
            - Simulações
            - Testes em massa
        
        Exemplo:
            >>> engine = DecisionEngine()
            >>> requests = [request1, request2, request3]
            >>> decisions = engine.evaluate_batch(requests)
            >>> approved = [d for d in decisions if d.is_approved()]
        """
        return [self.evaluate(request) for request in requests]
    
    def get_rejection_reasons(self, request: Request) -> list[str]:
        """
        Retorna TODOS os motivos pelos quais uma requisição seria rejeitada.
        
        Args:
            request: Requisição a analisar
        
        Returns:
            list[str]: Lista de motivos de rejeição (vazia se aprovaria)
        
        Diferença de evaluate():
            evaluate() para no primeiro erro (fail-fast).
            Este método executa TODAS as validações para análise completa.
        
        Útil para:
            - Debugging
            - Feedback detalhado ao cliente
            - Análise de qualidade dos dados
        
        Exemplo:
            >>> engine = DecisionEngine()
            >>> reasons = engine.get_rejection_reasons(request)
            >>> if reasons:
            ...     print("Problemas encontrados:")
            ...     for reason in reasons:
            ...         print(f"  - {reason}")
        """
        reasons = []
        
        # Validação 1: Tipo
        if not self._validate_validation_type(request):
            reasons.append(
                f"Plano {request.client.plan.nome} não permite tipo '{request.payload.tipo}'"
            )
        
        # Validação 2: Payload
        valido, mensagem = request.payload.validar_completo()
        if not valido:
            reasons.append(f"Payload: {mensagem}")
        
        # Validação 3: Tamanho
        if not self._validate_payload_size(request):
            reasons.append(f"Payload excede limite do plano")
        
        # Validação 4: Limite
        if not self._validate_request_limit(request):
            reasons.append("Limite de requisições excedido")
        
        return reasons
    
    # ========== MÉTODOS PRIVADOS DE VALIDAÇÃO ==========
    
    def _validate_validation_type(self, request: Request) -> bool:
        """
        Valida se o plano do cliente permite o tipo de validação solicitado.
        
        Args:
            request: Requisição a validar
        
        Returns:
            bool: True se tipo é permitido, False caso contrário
        
        Regra de Negócio:
            Tipo de validação solicitado deve estar na lista
            tipos_permitidos do plano do cliente.
        
        Exemplo:
            Cliente Basic (permite apenas CPF) tenta validar Endereço → False
            Cliente Silver (permite CPF + Endereço) valida CPF → True
        """
        return request.client.plan.allows_validation_type(request.payload.tipo)
    
    def _validate_payload_size(self, request: Request) -> bool:
        """
        Valida se o payload respeita o limite de tamanho do plano.
        
        Args:
            request: Requisição a validar
        
        Returns:
            bool: True se tamanho OK, False se excede
        
        Regra de Negócio:
            payload.size() <= plan.max_payload_size
            Tamanho exatamente no limite é considerado válido (<=).
        
        Exemplo:
            Payload 2KB em plano Basic (limite 1KB) → False
            Payload 5KB em plano Gold (limite 100KB) → True
        """
        return request.client.plan.allows_payload_size(request.payload)
    
    def _validate_request_limit(self, request: Request) -> bool:
        """
        Valida se o cliente não excedeu o limite de requisições.
        
        Args:
            request: Requisição a validar
        
        Returns:
            bool: True se ainda tem quota, False se excedeu
        
        Regra de Negócio:
            requisicoes_usadas < max_requests do plano
            Última requisição permitida: 100/100 → True
            Primeira excedente: 101/100 → False
        
        Exemplo:
            Cliente com 99/100 requisições usadas → True
            Cliente com 100/100 requisições usadas → False
        
        Nota:
            Este método é chamado ANTES de incrementar uso.
            Por isso usa < e não <=.
        """
        return request.client.requisicoes_usadas < request.client.plan.max_requests
    
    def __repr__(self):
        """
        Representação string do motor para debugging.
        
        Returns:
            str: Identificação do motor
        """
        return "DecisionEngine(stateless)"