from fastapi import Request

# Rotas da documentação interativa (Swagger e ReDoc) carregam scripts e estilos
# do CDN jsdelivr, então precisam de uma CSP menos restritiva que a da API.
ROTAS_DOCUMENTACAO = ("/docs", "/redoc")

# CSP para as respostas da API (JSON): nada pode ser carregado nem embutido.
CSP_API = "default-src 'none'; frame-ancestors 'none'"

# CSP das rotas de documentação: libera apenas o CDN usado pelo Swagger/ReDoc.
CSP_DOCUMENTACAO = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "img-src 'self' data: https://fastapi.tiangolo.com; "
    "worker-src 'self' blob:; "
    "frame-ancestors 'none'"
)

HEADERS_SEGURANCA = {
    # Força HTTPS por 1 ano em navegadores que já acessaram a API por HTTPS.
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    # Impede que a API seja carregada dentro de iframe (clickjacking).
    "X-Frame-Options": "DENY",
    # Impede o navegador de "adivinhar" o tipo do conteúdo (MIME sniffing).
    "X-Content-Type-Options": "nosniff",
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
