# TP2 — Análise e Segurança de Agentes de IA

Projeto de Bloco: Análise e Segurança de Agentes de IA. Este repositório contém a
segunda entrega (TP2), que reúne a análise exploratória completa do
**Customer Support Ticket Dataset** (com correlação, análise multivariada e testes
de hipóteses formais com SciPy) e a evolução da API FastAPI com controles de segurança
defensiva baseados no OWASP Top 10, persistência com SQLite/SQLModel, rate limiting,
testes automatizados e auditoria passiva com OWASP ZAP.

## Objetivo

Completar a análise exploratória do **Customer Support Ticket Dataset** — incluindo correlações, testes de hipótese formais e visualizações com SciPy — e evoluir a API FastAPI aplicando controles defensivos do OWASP Top 10 (persistência com SQLite/SQLModel, proteção contra BOLA, validação de campos com `extra='forbid'`, headers de segurança e rate limiting), preparando a aplicação para ser auditada via OWASP ZAP e testada com Pytest.

## Estrutura de pastas

```
.
├── README.md             Este arquivo
├── requirements.txt      Dependências do projeto
├── data/                 customer_support_tickets.csv (dataset do tp)
├── eda/                  Exatamente um arquivo .ipynb com o EDA completo
├── fastapi/              Código-fonte modular da API
│ ├── database.db         Banco de dados SQLite persistido
│ ├── sqlite_database.py  Script para criação e população inicial do banco
│ ├── main.py             Ponto de entrada da aplicação FastAPI
│ ├── routes/             Definição modular dos endpoints
│ ├── models/             Modelos Pydantic (extra='forbid') e classes SQLModel
│ └── security/           Autenticação JWT, middlewares de segurança e rate limiting
├── tests/                Suíte de testes automatizados com pytest
└── zap/                  Relatório do scan passivo OWASP ZAP e scan_passivo_zap.md
```

## Instalação

Requer Python 3.10 ou superior. Recomendado usar um ambiente virtual.

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### Criação e População do Banco de Dados

Antes de iniciar a API pela primeira vez, execute o script para criar as tabelas e
popular o banco SQLite com usuários e predições iniciais vinculadas por `owner_id`:

```bash
python fastapi/sqlite_database.py
```

O banco `database.db` será gerado automaticamente dentro do diretório `fastapi/`.

O banco já vem populado com 3 usuários de demonstração (senhas armazenadas como hash bcrypt) e 4 predições de donos diferentes:

| Usuário | Senha | Predições (id) |
|---|---|---|
| `admin` | `admin` | 1, 2 |
| `jose` | `1234` | 3 |
| `maria` | `senha123` | 4 |

Exemplo de login: `POST /auth/token` com `username` e `password` em formulário (`application/x-www-form-urlencoded`). Use o `access_token` retornado no header `Authorization: Bearer <token>`.

### Como executar o EDA

O notebook está em `eda/`. Dá pra abrir no Jupyter ou no Google Colab. Se rodar local:

```bash
jupyter notebook eda/eda_completo.ipynb
```

O CSV é carregado via caminho relativo diretamente da pasta `data/`.

### Como executar a API

A partir da pasta `fastapi/`:

```bash
uvicorn main:app --reload
```

A API sobe em `http://127.0.0.1:8000`. A documentação interativa (Swagger) fica em
`http://127.0.0.1:8000/docs`.

Recursos e controles implementados na API:

- `GET /health` — verifica a integridade e status da API.

- `POST /auth/token` — autentica usuários cadastrados no banco (senhas armazenadas com hash bcrypt) e emite token JWT. Limitado a 10 requisições por minuto por cliente.

- `POST /predict` — endpoint protegido por JWT que classifica a mensagem e salva a predição com o `owner_id` do usuário autenticado. O body é validado com `extra='forbid'`: campos extras retornam 422.

- `GET /predict/{id}` — consulta de predição por ID com validação de ownership (prevenção contra BOLA): se a predição pertence a outro usuário, a API responde 404, igual a uma predição inexistente.

- Middlewares globais injetando headers de segurança (HSTS, CSP, X-Frame-Options, X-Content-Type-Options) e CORS com allowlist explícita.

#### Headers de segurança HTTP

Implementados em `fastapi/security/headers.py` por meio de middleware FastAPI, presentes em todas as respostas (inclusive nas de erro 401 e 429):

| Header | Valor | Objetivo |
|---|---|---|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Força HTTPS em acessos seguintes |
| `X-Frame-Options` | `DENY` | Bloqueia uso da API em iframe (clickjacking) |
| `X-Content-Type-Options` | `nosniff` | Impede MIME sniffing |
| `Content-Security-Policy` | `default-src 'none'; frame-ancestors 'none'` | Respostas da API não carregam nem embutem nenhum recurso |

As rotas `/docs` e `/redoc` usam uma CSP menos restritiva, que libera apenas o CDN `cdn.jsdelivr.net`, necessário para o Swagger funcionar.

#### CORS

Configurado em `fastapi/security/cors.py` com `CORSMiddleware` e allowlist explícita de origens (`http://localhost:3000` e `http://localhost:8501`, também em `127.0.0.1`). Não é usado `"*"`. Métodos permitidos: `GET`, `POST`, `OPTIONS`. Headers permitidos: `Authorization` e `Content-Type`. Origens adicionais podem ser informadas na variável de ambiente `CORS_ORIGENS_EXTRAS`, separadas por vírgula.

#### Rate limiting

Implementado com SlowAPI em `fastapi/security/rate_limit.py` e aplicado ao endpoint `POST /auth/token`.

- **Limite:** 10 requisições por minuto por cliente (identificado pelo IP).
- **Resposta ao exceder:** HTTP `429`.
- **Justificativa:** 10 tentativas por minuto atendem um usuário legítimo que erra a senha algumas vezes, mas limitam um ataque de força bruta a no máximo 600 tentativas por hora por IP.
- **Observação:** o contador fica em memória, então reinicia quando a API reinicia. Nos testes automatizados, é preciso chamar `limiter.reset()` entre os testes que usam `/auth/token`.

### Como executar os testes automatizados

Os testes cobrem os cenários de segurança exigidos (acesso sem token, violação de
ownership/BOLA e envio de campos extras não mapeados):

```bash
pytest tests/ -v
```

## Integrantes

- Luisa Hering Bell de Otero
- Júlia Reinke
- Raquel Braga dos Santos
- Gustavo Malfa Corrêa
