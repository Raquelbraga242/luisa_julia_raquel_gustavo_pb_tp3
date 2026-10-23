# TP3 — Análise e Segurança de Agentes de IA

Projeto de Bloco: Análise e Segurança de Agentes de IA.

Este repositório contém a terceira entrega do projeto, desenvolvida a partir do TP2 utilizando o **Customer Support Ticket Dataset**. Nesta etapa foram adicionados o experimento de regressão linear, a formalização do problema de classificação, novos testes de segurança, integração contínua com GitHub Actions e a auditoria final da API com OWASP ZAP.

## Objetivo

Consolidar a análise estatística realizada nos TPs anteriores e preparar o projeto para a etapa de classificação de intenções, mantendo a API FastAPI com os controles de segurança e testes automatizados desenvolvidos ao longo do projeto.

## Estrutura de pastas

```text
.
├── README.md
├── requirements.txt
├── data/
│   └── customer_support_tickets.csv
├── eda/
│   └── eda_tp3.ipynb
├── fastapi/
│   ├── database.db
│   ├── sqlite_database.py
│   ├── sqlite_populate.py
│   ├── main.py
│   ├── routes/
│   ├── models/
│   └── security/
├── tests/
├── zap/
│   └── scan_passivo_zap_TP3.md
├── others/
│   └── planejamento.md
│   └── ...        Documentos complementares do projeto
└── .github/
    └── workflows/
        └── testes.yml
```

## Instalação

Requer Python 3.10 ou superior. Recomenda-se utilizar um ambiente virtual.

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Banco de dados

O projeto utiliza SQLite.

Para criar o banco:

```bash
python fastapi/sqlite_database.py
```

Para realizar a população inicial:

```bash
python fastapi/sqlite_populate.py
```

O arquivo `database.db` fica localizado dentro de `fastapi/` e contém usuários e predições de exemplo pertencentes a usuários diferentes.

## EDA

O notebook com as etapas dos TP1, TP2 e TP3 está em:

```text
eda/eda_tp3.ipynb
```

Para executá-lo localmente:

```bash
jupyter notebook eda/eda_tp3.ipynb
```

Nesta etapa foram acrescentados o experimento de regressão linear, as métricas R² e RMSE, Residual Plot, Q-Q Plot e a formalização do problema de classificação de intenções.

## API

A partir da pasta `fastapi/`:

```bash
uvicorn main:app --reload
```

A API ficará disponível em:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

Principais rotas:

- `GET /health`
- `POST /auth/token`
- `POST /predict`
- `GET /predict/{id}`

A API utiliza autenticação JWT, validação de ownership para prevenção de BOLA, modelos Pydantic com `extra='forbid'`, CORS com allowlist, headers HTTP de segurança e rate limiting no endpoint de autenticação.

## Testes automatizados

Os testes estão localizados em `tests/` e utilizam `pytest` e o `TestClient` do FastAPI.

A suíte cobre cenários de autenticação, autorização/BOLA, validação de entrada, rate limiting e acesso a rotas protegidas.

Para executar:

```bash
pytest tests/ -v
```

## GitHub Actions

O workflow de integração contínua está em:

```text
.github/workflows/testes.yml
```

A cada push, o GitHub Actions instala as dependências do projeto e executa:

```bash
pytest tests/ -v
```

As execuções podem ser acompanhadas na aba **Actions** do repositório.

## OWASP ZAP

A auditoria final da API é realizada com OWASP ZAP.

O relatório exportado fica na pasta `zap/` e a análise dos findings Medium e High está documentada em:

```text
zap/scan_passivo_zap_TP3.md
```

## Cloudflare Tunnel

Para disponibilizar temporariamente a API por HTTPS durante a preparação dos testes adversariais, foi utilizado o Cloudflare Tunnel:

```bash
cloudflared tunnel --url http://localhost:8000
```

A URL gerada no TP3 está registrada em `others/planejamento.md`.

## Repositório

https://github.com/Raquelbraga242/luisa_julia_raquel_gustavo_pb_tp3

## Integrantes

- Luisa Hering Bell de Otero
- Júlia Reinke
- Raquel Braga dos Santos
- Gustavo Malfa Corrêa