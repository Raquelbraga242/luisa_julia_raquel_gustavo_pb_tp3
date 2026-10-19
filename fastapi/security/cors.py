import os

# Allowlist explícita de origens que podem chamar a API a partir de um navegador.
# Nunca usar "*" aqui: com allow_credentials=True qualquer site poderia
# enviar requisições autenticadas em nome do usuário.
ORIGENS_PERMITIDAS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]

# Origens extras podem ser informadas por variável de ambiente, separadas por vírgula
# (ex.: CORS_ORIGENS_EXTRAS="https://meu-front.exemplo.com").
_extras = os.getenv("CORS_ORIGENS_EXTRAS", "")
ORIGENS_PERMITIDAS += [origem.strip() for origem in _extras.split(",") if origem.strip()]

CONFIG_CORS = {
    "allow_origins": ORIGENS_PERMITIDAS,
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Authorization", "Content-Type"],
}
