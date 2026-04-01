"""
Middleware de Security Headers

Adiciona headers HTTP de segurança em todas as respostas da API
para proteger contra ataques comuns (XSS, clickjacking, MIME sniffing).

Autor: Cristóvão Caldeira
Data: Fevereiro 2026
Projeto: Portfólio Python - Projeto 2/5 - Etapa 5 - Mini-Etapa 5.5
"""

from fastapi import Request
from typing import Callable


async def add_security_headers(request: Request, call_next: Callable):
    """
    Middleware que adiciona headers de segurança em todas as respostas.
    
    Headers adicionados:
        - X-Content-Type-Options: nosniff
        - X-Frame-Options: DENY
        - X-XSS-Protection: 1; mode=block
        - Content-Security-Policy: (configurado para permitir Swagger UI)
        - Referrer-Policy: no-referrer
        - Permissions-Policy: geolocation=(), microphone=(), camera=()
    
    Fluxo:
        1. Processa a requisição (call_next)
        2. Adiciona headers na resposta
        3. Retorna resposta com headers de segurança
    """
    
    # Processar requisição
    response = await call_next(request)
    
    # Adicionar headers de segurança
    
    # Impede MIME sniffing (navegador não pode adivinhar tipo de arquivo)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Impede que página seja carregada em iframe (proteção contra clickjacking)
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Ativa proteção XSS em navegadores antigos
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Content Security Policy (configurado para permitir Swagger UI)
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https://fastapi.tiangolo.com"
    
    # Controla quanto de informação de referrer é enviado
    # 'no-referrer' = não envia informação de onde veio
    response.headers['Referrer-Policy'] = 'no-referrer'
    
    # Controla quais features do navegador podem ser usadas
    # Desabilita geolocalização, microfone e câmera
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    # IMPORTANTE: HSTS (Strict-Transport-Security) deve ser usado APENAS em produção com HTTPS
    # Descomente a linha abaixo quando deploy em produção com SSL/TLS:
    # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response