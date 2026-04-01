"""
Schema de Request - Validação de Entrada da API

Define a estrutura de dados que o cliente deve enviar para
o endpoint de validação.

Autor: Cristóvão Caldeira
Data: Fevereiro 2026
Projeto: Portfólio Python - Projeto 2/5 - Etapa 5
"""

from pydantic import BaseModel, Field


class ValidateRequest(BaseModel):
    """
    Schema de request para validação de dados.
    
    Define a estrutura esperada quando cliente envia dados
    para validação via POST /validate.
    
    IMPORTANTE: client_id NÃO é mais necessário no body.
    O cliente é identificado automaticamente pela API Key enviada no header.
    
    Attributes:
        tipo: Tipo de validação solicitada
        dados: Dicionário com dados a serem validados
    """
    
    tipo: str = Field(
        ...,
        min_length=1,
        pattern='^validacao_',
        description='Tipo de validação solicitada',
        json_schema_extra={
            'example': 'validacao_cpf',
            'enum': [
                'validacao_cpf',
                'validacao_endereco',
                'validacao_dados_bancarios'
            ]
        }
    )
    
    dados: dict = Field(
        ...,
        description='Dados a serem validados (estrutura varia por tipo)',
        json_schema_extra={
            'example': {
                'cpf': '12345678900',
                'nome': 'João Silva'
            }
        }
    )
    
    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    'tipo': 'validacao_cpf',
                    'dados': {
                        'cpf': '12345678900',
                        'nome': 'João Silva'
                    }
                },
                {
                    'tipo': 'validacao_endereco',
                    'dados': {
                        'cep': '01310-100',
                        'logradouro': 'Avenida Paulista',
                        'numero': '1578'
                    }
                },
                {
                    'tipo': 'validacao_dados_bancarios',
                    'dados': {
                        'banco': '001',
                        'agencia': '1234',
                        'conta': '56789-0'
                    }
                }
            ]
        }
    }