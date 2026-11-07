import socket

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_us01_ca2_real_driver_connection_refused():
    """Driver real contra porta local sem servidor; sem mock e sem PostgreSQL ativo."""
    # Socket reservado, sem listen: impede que outro servidor ocupe a porta durante o teste.
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        app = create_app(
            Settings(
                _env_file=None,
                database_url=f"postgresql+psycopg://ficticio:segredo_demo@127.0.0.1:{port}/portfolio_test",
            )
        )
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 503
            assert response.json()["error"]["code"] == "storage_unavailable"
            assert "segredo_demo" not in response.text
