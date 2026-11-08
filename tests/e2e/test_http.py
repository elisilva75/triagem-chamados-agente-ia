import os
import socket
import subprocess
import sys
import time

import httpx
import pytest

pytestmark = [pytest.mark.postgres, pytest.mark.e2e]


def test_us02_http_real_process(migrated_url):
    """US02/US03: usa TCP e Uvicorn real, com banco exclusivo criado pela fixture."""
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
            path = response.headers["location"]
            edited = client.patch(
                path,
                json={
                    "expected_version": 1,
                    "title": "Título corrigido por HTTP real",
                },
            )
            assert edited.status_code == 200
            assert edited.json()["version"] == edited.json()["content_revision"] == 2
            assert client.get(path).json() == edited.json()
            conflict = client.patch(
                path,
                json={
                    "expected_version": 1,
                    "title": "Edição com versão antiga",
                },
            )
            assert conflict.status_code == 409
            assert conflict.json()["error"]["code"] == "version_conflict"
            triaged = client.post(path + "/triage", json={"expected_version": 2})
            assert triaged.status_code == 200, triaged.text
            suggested = triaged.json()["ticket"]
            assert suggested["version"] == 4
            assert suggested["suggestion"]["mode"] == "simulated"
            assert suggested["final_classification"] is None
            assert client.get(path).json() == suggested
            from tests.review_helpers import REVIEW

            reviewed = client.post(path + "/reviews", json={"expected_version": 4, **REVIEW})
            assert reviewed.status_code == 201, reviewed.text
            review = reviewed.json()["review"]
            assert client.get(reviewed.headers["location"]).json() == review
            resolved = client.post(path + "/resolve", json={"expected_version": 5})
            assert resolved.status_code == 200 and resolved.json()["status"] == "resolvido"
            assert (
                client.patch(
                    path, json={"expected_version": 6, "title": "Bloqueado em resolvido"}
                ).status_code
                == 409
            )
            reopened = client.post(path + "/reopen", json={"expected_version": 6})
            assert reopened.status_code == 200 and reopened.json()["status"] == "aberto"
            assert (
                reopened.json()["final_classification"]
                == reviewed.json()["ticket"]["final_classification"]
            )
            edited_again = client.patch(
                path,
                json={
                    "expected_version": 7,
                    "description": "Texto fictício corrigido após triagem.",
                },
            )
            assert edited_again.status_code == 200
            assert edited_again.json()["suggestion"] is None
            assert edited_again.json()["final_classification"] is None
            assert edited_again.json()["triage_status"] == "pendente"
            assert client.get(path + "/reviews").json()["items"] == [review]
            history = client.get(path + "/triage-attempts").json()
            assert history["total"] == 1
            assert history["items"][0]["suggestion"] == suggested["suggestion"]
            failed_ticket = client.post(
                "/api/v1/tickets",
                json={
                    "title": "[SIMULADO:saida-invalida]",
                    "description": "Dados fictícios para falha simulada.",
                },
            )
            failed_path = failed_ticket.headers["location"]
            failed = client.post(failed_path + "/triage", json={"expected_version": 1})
            assert failed.status_code == 502
            assert failed.json()["error"]["code"] == "invalid_ai_response"
            assert client.get(failed_path).json()["triage_status"] == "falha"
            assert client.get(failed_path + "/triage-attempts").json()["total"] == 1
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
