# usuários do banco de exemplo: admin/admin, jose/1234, maria/senha123


def test_login_com_credenciais_validas(client):
    resposta = client.post(
        "/auth/token", data={"username": "jose", "password": "1234"}
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["token_type"] == "bearer"
    assert isinstance(corpo["access_token"], str) and corpo["access_token"]


def test_login_com_senha_incorreta(client):
    resposta = client.post(
        "/auth/token", data={"username": "jose", "password": "senha-errada"}
    )

    assert resposta.status_code == 401
    assert resposta.json() == {"detail": "Usuário ou senha inválidos"}
    assert "access_token" not in resposta.json()


def test_login_com_usuario_inexistente_nao_revela_o_motivo(client):
    resposta = client.post(
        "/auth/token", data={"username": "fulano", "password": "qualquer"}
    )

    # mesma resposta da senha errada, pra não revelar quais usuários existem
    assert resposta.status_code == 401
    assert resposta.json() == {"detail": "Usuário ou senha inválidos"}


def test_acesso_sem_token(client):
    resposta_get = client.get("/predict/1")
    resposta_post = client.post("/predict", json={"message": "oi"})

    assert resposta_get.status_code == 401
    assert resposta_post.status_code == 401
    assert resposta_get.headers["www-authenticate"] == "Bearer"


def test_acesso_com_token_invalido(client):
    resposta = client.get(
        "/predict/1", headers={"Authorization": "Bearer token.invalido.123"}
    )

    assert resposta.status_code == 401
    assert resposta.json() == {"detail": "Token inválido ou expirado"}


def test_dono_acessa_a_propria_predicao(client, obter_headers):
    # controle: a predição 3 existe e é do jose, então o 404 do próximo teste é por causa do dono
    resposta = client.get("/predict/3", headers=obter_headers("jose", "1234"))

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["id"] == 3
    assert corpo["owner_id"] == 2


def test_acesso_recurso_de_outro_usuario(client, obter_headers):
    # a predição 1 é do admin, o jose está logado mas não é o dono
    resposta = client.get("/predict/1", headers=obter_headers("jose", "1234"))

    assert resposta.status_code == 404
    assert resposta.json() == {"detail": "Prediction não encontrada"}
    # a resposta não pode vazar dados da predição do admin
    assert "reembolso" not in resposta.text
    assert "owner_id" not in resposta.text


def test_bola_em_predicao_recem_criada(client, obter_headers):
    headers_jose = obter_headers("jose", "1234")
    headers_maria = obter_headers("maria", "senha123")

    criada = client.post(
        "/predict", json={"message": "Quero reembolso"}, headers=headers_jose
    )
    assert criada.status_code == 200
    id_criada = criada.json()["id"]

    # a maria não vê a predição do jose, o jose continua vendo
    assert client.get(f"/predict/{id_criada}", headers=headers_maria).status_code == 404
    assert client.get(f"/predict/{id_criada}", headers=headers_jose).status_code == 200


def test_predicao_inexistente_responde_igual_a_de_outro_usuario(
    client, obter_headers
):
    headers_jose = obter_headers("jose", "1234")

    de_outro_usuario = client.get("/predict/1", headers=headers_jose)
    inexistente = client.get("/predict/9999", headers=headers_jose)

    # mesma resposta nos dois casos, pra não revelar quais ids existem
    assert inexistente.status_code == de_outro_usuario.status_code == 404
    assert inexistente.json() == de_outro_usuario.json()


def test_campo_extra_no_body(client, obter_headers):
    resposta = client.post(
        "/predict",
        headers=obter_headers("admin", "admin"),
        json={
            "message": "Quero solicitar um reembolso",
            "campo_extra": "não permitido",
        },
    )

    assert resposta.status_code == 422
    erro = resposta.json()["detail"][0]
    assert erro["type"] == "extra_forbidden"
    assert erro["loc"] == ["body", "campo_extra"]


def test_body_sem_campo_obrigatorio(client, obter_headers):
    resposta = client.post(
        "/predict", headers=obter_headers("admin", "admin"), json={}
    )

    assert resposta.status_code == 422
    erro = resposta.json()["detail"][0]
    assert erro["type"] == "missing"
    assert erro["loc"] == ["body", "message"]


def test_body_com_tipo_invalido(client, obter_headers):
    resposta = client.post(
        "/predict",
        headers=obter_headers("admin", "admin"),
        json={"message": 12345},
    )

    assert resposta.status_code == 422
    assert resposta.json()["detail"][0]["loc"] == ["body", "message"]


def test_requisicao_rejeitada_nao_grava_predicao(client, obter_headers):
    headers = obter_headers("jose", "1234")

    client.post(
        "/predict",
        headers=headers,
        json={"message": "texto", "owner_id": 1},  # tenta definir o dono
    )

    # nada foi gravado: a próxima predição (id 5) não existe
    assert client.get("/predict/5", headers=headers).status_code == 404


def test_rate_limit_bloqueia_apos_10_tentativas_de_login(client):
    dados = {"username": "jose", "password": "senha-errada"}

    # as 10 primeiras são recusadas pela senha (401)
    for _ in range(10):
        assert client.post("/auth/token", data=dados).status_code == 401

    # a 11ª é bloqueada pelo rate limit (429)
    bloqueada = client.post("/auth/token", data=dados)
    assert bloqueada.status_code == 429
    assert "Rate limit exceeded" in bloqueada.json()["error"]


def test_rate_limit_bloqueia_ate_credenciais_validas(client):
    for _ in range(10):
        client.post("/auth/token", data={"username": "jose", "password": "x"})

    resposta = client.post(
        "/auth/token", data={"username": "jose", "password": "1234"}
    )

    assert resposta.status_code == 429
    assert "access_token" not in resposta.json()


def test_rate_limit_nao_afeta_outras_rotas(client):
    for _ in range(11):
        client.post("/auth/token", data={"username": "jose", "password": "x"})

    assert client.get("/health").status_code == 200
