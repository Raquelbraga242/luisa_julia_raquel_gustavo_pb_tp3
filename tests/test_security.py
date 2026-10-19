import sys
from pathlib import Path
from fastapi.testclient import TestClient

FASTAPI_DIR = Path(__file__).resolve().parents[1] / "fastapi"
sys.path.insert(0, str(FASTAPI_DIR))

from main import app

client = TestClient(app)


def obter_token(username: str, password: str):
    response = client.post(
        "/auth/token",
        data={
            "username": username,
            "password": password
        }
    )

    assert response.status_code == 200
    return response.json()["access_token"]


def test_acesso_sem_token():
    response = client.get("/predict/1")

    assert response.status_code == 401


def test_acesso_recurso_de_outro_usuario():
    token = obter_token("jose", "1234")
    response = client.get(
        "/predict/1",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 404


def test_campo_extra_no_body():
    token = obter_token("admin", "admin")
    response = client.post(
        "/predict",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "message": "Quero solicitar um reembolso",
            "campo_extra": "não permitido"
        }
    )
    assert response.status_code == 422