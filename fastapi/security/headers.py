from fastapi import Request

"""
Configuração de headers de segurança HTTP e Content-Security-Policy (CSP)

Correções OWASP ZAP:
- Finding Medium (CSP: Failure to Define Directive with No Fallback):
    Adicionada a diretiva (form-action \'self\') para restringir o envio de dados de formulários (ex.: login form do Swagger).

- Finding Medium (Clickjacking / frame-ancestors):
    Garantida a diretiva (frame-ancestors \'none\') em conjunto com o (X-Frame-Options: DENY).

- Finding High (Credenciais de Autenticação Capturadas):
    Mitigado pelo uso do cabeçalho Strict-Transport-Security (HSTS) e disponibilização da API por HTTPS via Cloudflare Tunnel em ambiente acessível externamente.
"""


# Rotas da documentação interativa (Swagger e ReDoc) carregam scripts e estilos
# do CDN jsdelivr, então precisam de uma CSP menos restritiva que a da API.
ROTAS_DOCUMENTACAO = ("/docs", "/redoc")

# CSP para as respostas da API (JSON): nada pode ser carregado nem embutido.
# [CORREÇÃO ZAP]: Nos endpoints JSON da API, bloqueia totalmente scripts/estilos inline
# e recursos externos sem SRI (mitigando CSP unsafe-inline e Sub Resource Integrity Missing).
CSP_API = "default-src 'none'; frame-ancestors 'none'; form-action 'self'"

# CSP das rotas de documentação: libera apenas o CDN usado pelo Swagger/ReDoc.
# [CORREÇÃO ZAP]: adicionada a diretiva 'form-action \'self\'' para cobrir diretivas sem fallback em default-src.
CSP_DOCUMENTACAO = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "img-src 'self' data: https://fastapi.tiangolo.com; "
    "worker-src 'self' blob:; "
    "frame-ancestors 'none'; "
    "form-action 'self'; "
)

HEADERS_SEGURANCA = {
    # [CORREÇÃO ZAP]: Transporte seguro / HSTS
    # Força HTTPS por 1 ano em navegadores que já acessaram a API por HTTPS.
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    # Impede que a API seja carregada dentro de iframe (clickjacking).
    # [CORREÇÃO ZAP]: Anti-Clickjacking
    "X-Frame-Options": "DENY",
    # Impede o navegador de "adivinhar" o tipo do conteúdo (MIME sniffing).
    "X-Content-Type-Options": "nosniff",
    # Proteção de referrer em requisições externas
    "Referrer-Policy": "strict-origin-when-cross-origin",
}


async def adicionar_headers_seguranca(request: Request, call_next):
    response = await call_next(request)

    for nome, valor in HEADERS_SEGURANCA.items():
        response.headers[nome] = valor

    if request.url.path.startswith(ROTAS_DOCUMENTACAO):
        response.headers["Content-Security-Policy"] = CSP_DOCUMENTACAO
    else:
        response.headers["Content-Security-Policy"] = CSP_API

    return response
