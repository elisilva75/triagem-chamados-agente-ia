import os
import socket
import subprocess
import sys
import time

import httpx
import pytest

pytestmark = [pytest.mark.postgres, pytest.mark.e2e]


def test_us02_http_real_process(migrated_url):
    """US02: usa TCP e Uvicorn real, com banco exclusivo criado pela fixture."""
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = {**os.environ, "DATABASE_URL": migrated_url, "AI_MODE": "simulated", "APP_ENV": "test"}
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:create_app",
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--no-access-log",
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        with httpx.Client(
            base_url=f"http://127.0.0.1:{port}", timeout=3, trust_env=False
        ) as client:
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    pytest.fail("Uvicorn encerrou antes de ficar pronto.")
                try:
                    if client.get("/health").status_code == 200:
                        break
                except httpx.TransportError:
                    pass
                time.sleep(0.1)
            else:
                pytest.fail("Servidor não ficou pronto em 20 segundos.")
            response = client.post(
                "/api/v1/tickets",
                json={
                    "title": "Chamado por HTTP real",
                    "description": "Dados fictícios pela rede local.",
                },
            )
            assert response.status_code == 201
            assert client.get(response.headers["location"]).json() == response.json()
            assert client.get("/api/v1/tickets").json()["total"] == 1
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
