"""
Módulo de Payload - Entidade de Domínio

Define a estrutura de dados enviados para validação, incluindo:
- Tipos de validação suportados
- Campos obrigatórios por tipo
- Validação de estrutura, campos e tipos de dados

Esta classe implementa auto-validação (data-driven), permitindo escalabilidade
sem modificação de código ao adicionar novos tipos de validação.

Autor: [Cristóvão Caldeira Dos Reis]
Data: Janeiro 2026
"""

import sys


class Payload:
    """
    Representa os dados enviados por um cliente para validação.
    
    Responsabilidades:
        - Armazenar tipo de validação e dados
        - Auto-validar estrutura, campos obrigatórios e tipos
        - Calcular tamanho em bytes
        - Fornecer mensagens de erro específicas e acionáveis
    
    Design Pattern: Data-Driven Validation
        Validações baseadas em mapas de configuração, permitindo adicionar
        novos tipos sem modificar a lógica de validação.
    
    Atributos:
        tipo (str): Tipo de validação solicitada
        dados (dict): Dicionário contendo os dados a serem validados
    
    Exemplo:
        >>> payload = Payload(
        ...     tipo=Payload.TIPO_CPF,
        ...     dados={"cpf": "12345678900", "nome": "João Silva"}
        ... )
        >>> valido, mensagem = payload.validar_completo()
        >>> print(valido)  # True
    """
    
    # ========== CONSTANTES DE TIPO ==========
    
    TIPO_CPF = "validacao_cpf"
    TIPO_ENDERECO = "validacao_endereco"
    TIPO_DADOS_BANCARIOS = "validacao_dados_bancarios"
    
    # ========== CONFIGURAÇÃO DATA-DRIVEN ==========
    
    # Mapa: tipo de validação → campos obrigatórios
    CAMPOS_OBRIGATORIOS = {
        TIPO_CPF: ["cpf", "nome"],
        TIPO_ENDERECO: ["cep", "logradouro", "numero"],
        TIPO_DADOS_BANCARIOS: ["banco", "agencia", "conta"]
    }
    
    # Mapa: campo → tipo(s) Python esperado(s)
    TIPOS_ESPERADOS = {
        "cpf": str,
        "nome": str,
        "cep": str,
        "logradouro": str,
        "numero": (str, int),  # Aceita string OU int
        "banco": str,
        "agencia": str,
        "conta": str
    }
    
    # ========== MÉTODOS PÚBLICOS ==========
    
    def __init__(self, tipo: str, dados: dict):
        """
        Inicializa um payload para validação.
        
        Args:
            tipo: Tipo de validação solicitada (use constantes TIPO_*)
            dados: Dicionário com os dados a serem validados
        
        Nota:
            Validação não é executada no __init__. Use validar_completo()
            para verificar se o payload é válido.
        """
        self.tipo = tipo
        self.dados = dados
    
    def size(self) -> int:
        """
        Calcula o tamanho do payload em bytes.
        
        Returns:
            int: Tamanho aproximado do payload em bytes
        
        Implementação:
            Usa sys.getsizeof() sobre a representação string do dicionário.
            Útil para verificar limites de tamanho por plano.
        """
        return sys.getsizeof(str(self.dados))
    
    def validar_estrutura(self) -> tuple[bool, str]:
        """
        Valida se o payload tem estrutura mínima válida.
        
        Validações executadas:
            1. Dados são um dicionário?
            2. Dicionário não está vazio?
        
        Returns:
            tuple[bool, str]: (é_válido, mensagem)
                - (True, "Estrutura válida") se passou
                - (False, mensagem_erro) se falhou
        
        Exemplo:
            >>> payload = Payload(tipo="validacao_cpf", dados={})
            >>> valido, msg = payload.validar_estrutura()
            >>> print(msg)  # "Payload não pode estar vazio"
        """
        if not isinstance(self.dados, dict):
            return False, "Payload deve ser um dicionário"
        
        if len(self.dados) == 0:
            return False, "Payload não pode estar vazio"
        
        return True, "Estrutura válida"
    
    def validar_campos_obrigatorios(self) -> tuple[bool, str]:
        """
        Valida se todos os campos obrigatórios estão presentes.
        
        Validações executadas:
            1. Tipo de validação é reconhecido?
            2. Todos os campos obrigatórios estão presentes nos dados?
        
        Returns:
            tuple[bool, str]: (é_válido, mensagem)
                - (True, mensagem_sucesso) se todos os campos presentes
                - (False, mensagem_erro) listando campos faltantes
        
        Exemplo:
            >>> payload = Payload(
            ...     tipo=Payload.TIPO_CPF,
            ...     dados={"cpf": "12345678900"}  # falta 'nome'
            ... )
            >>> valido, msg = payload.validar_campos_obrigatorios()
            >>> print(msg)  # "Campos obrigatórios ausentes: nome"
        """
        if self.tipo not in self.CAMPOS_OBRIGATORIOS:
            return False, f"Tipo de validação '{self.tipo}' não reconhecido"
        
        campos_necessarios = self.CAMPOS_OBRIGATORIOS[self.tipo]
        
        campos_faltantes = [
            campo for campo in campos_necessarios 
            if campo not in self.dados
        ]
        
        if campos_faltantes:
            return False, f"Campos obrigatórios ausentes: {', '.join(campos_faltantes)}"
        
        return True, "Todos os campos obrigatórios presentes"
    
    def validar_tipos(self) -> tuple[bool, str]:
        """
        Valida se os campos têm os tipos de dados corretos.
        
        Validações executadas:
            Para cada campo que tem tipo definido em TIPOS_ESPERADOS,
            verifica se o valor tem o tipo Python correto.
        
        Returns:
            tuple[bool, str]: (é_válido, mensagem)
                - (True, "Tipos válidos") se todos os tipos corretos
                - (False, mensagem_erro) listando campos com tipo incorreto
        
        Comportamento especial:
            Campos que aceitam múltiplos tipos (ex: 'numero': (str, int))
            são validados com isinstance() sobre a tupla.
        
        Exemplo:
            >>> payload = Payload(
            ...     tipo=Payload.TIPO_DADOS_BANCARIOS,
            ...     dados={"banco": 123, "agencia": "1234", "conta": "56789"}
            ... )
            >>> valido, msg = payload.validar_tipos()
            >>> print(msg)  # "Campo 'banco' deve ser str, recebido int"
        """
        erros = []
        
        for campo, valor in self.dados.items():
            if campo in self.TIPOS_ESPERADOS:
                tipo_esperado = self.TIPOS_ESPERADOS[campo]
                
                if isinstance(tipo_esperado, tuple):
                    # Campo aceita múltiplos tipos
                    if not isinstance(valor, tipo_esperado):
                        tipos_nomes = " ou ".join([t.__name__ for t in tipo_esperado])
                        erros.append(
                            f"Campo '{campo}' deve ser {tipos_nomes}, "
                            f"recebido {type(valor).__name__}"
                        )
                else:
                    # Campo aceita apenas um tipo
                    if not isinstance(valor, tipo_esperado):
                        erros.append(
                            f"Campo '{campo}' deve ser {tipo_esperado.__name__}, "
                            f"recebido {type(valor).__name__}"
                        )
        
        if erros:
            return False, "; ".join(erros)
        
        return True, "Tipos válidos"
    
    def validar_completo(self) -> tuple[bool, str]:
        """
        Executa cadeia completa de validações do payload.
        
        Ordem de validação (fail-fast):
            1. Estrutura (é dict? não está vazio?)
            2. Campos obrigatórios (todos presentes?)
            3. Tipos de dados (tipos corretos?)
        
        Para na primeira validação que falhar.
        
        Returns:
            tuple[bool, str]: (é_válido, mensagem)
                - (True, "Payload completamente válido") se passou em tudo
                - (False, mensagem_erro) da primeira validação que falhou
        
        Uso recomendado:
            Este é o método principal de validação. Use-o antes de
            processar o payload no motor de decisão.
        
        Exemplo:
            >>> payload = Payload(
            ...     tipo=Payload.TIPO_CPF,
            ...     dados={"cpf": "12345678900", "nome": "João Silva"}
            ... )
            >>> valido, mensagem = payload.validar_completo()
            >>> if valido:
            ...     print("Payload OK!")
        """
        valido, msg = self.validar_estrutura()
        if not valido:
            return False, msg
        
        valido, msg = self.validar_campos_obrigatorios()
        if not valido:
            return False, msg
        
        valido, msg = self.validar_tipos()
        if not valido:
            return False, msg
        
        return True, "Payload completamente válido"
    
    def __repr__(self):
        """
        Representação string do payload para debugging.
        
        Returns:
            str: Representação legível do payload
        """
        return f"Payload(tipo='{self.tipo}', dados={self.dados})"