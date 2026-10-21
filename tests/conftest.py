import shutil
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine

# permite importar o código da pasta fastapi/
FASTAPI_DIR = Path(__file__).resolve().parents[1] / "fastapi"
sys.path.insert(0, str(FASTAPI_DIR))

from database import DB_PATH, get_session  # noqa: E402
from main import app  # noqa: E402
from security.rate_limit import limiter  # noqa: E402


@pytest.fixture(autouse=True)
def resetar_rate_limit():
    # o limite de /auth/token é 10 por minuto e o contador fica em memória;
    # sem o reset, logins de outros testes causariam 429
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture
def client(tmp_path):
    # usa uma cópia do database.db para os testes não alterarem o banco versionado
    banco_teste = tmp_path / "banco_teste.db"
    shutil.copy(DB_PATH, banco_teste)

    engine = create_engine(
        f"sqlite:///{banco_teste}", connect_args={"check_same_thread": False}
    )

    def get_session_teste():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_teste

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def obter_headers(client):

    def _obter_headers(username: str, password: str) -> dict:
        resposta = client.post(
            "/auth/token",
            data={"username": username, "password": password},
        )
        assert resposta.status_code == 200
        return {"Authorization": f"Bearer {resposta.json()['access_token']}"}

    return _obter_headers
