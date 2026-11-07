from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.api.routes import get_session
from app.config import Settings
from app.main import create_app


def test_us01_ca2_us02_storage_error_sanitized():
    """Banco simulado por mock; não comprova conexão nem persistência."""
    app = create_app(Settings(_env_file=None))
    session = MagicMock()
    session.execute.side_effect = OperationalError("secret-database-url", {}, Exception("password"))
    session.flush.side_effect = session.execute.side_effect
    app.dependency_overrides[get_session] = lambda: session
    with TestClient(app) as client:
        for response in [
            client.get("/health"),
            client.post(
                "/api/v1/tickets",
                json={"title": "Erro fictício", "description": "Descrição de teste fictícia."},
            ),
        ]:
            assert response.status_code == 503
            assert response.json()["error"]["code"] == "storage_unavailable"
            assert "password" not in response.text
            assert "secret-database-url" not in response.text
            assert response.json()["error"]["request_id"] == response.headers["X-Request-ID"]


def test_us02_invalid_input_without_database():
    app = create_app(Settings(_env_file=None))
    with TestClient(app) as client:
        response = client.post("/api/v1/tickets", json={"title": "SECRETO"})
        assert response.status_code == 422
        assert "SECRETO" not in response.text
        assert response.json()["error"]["details"][0]["field"] == "body.description"
