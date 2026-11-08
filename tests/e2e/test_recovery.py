import os
import socket
import subprocess
import sys
import sysconfig
import time
from datetime import datetime, timezone

import httpx
import pytest

from tests.conftest import ROOT

pytestmark = [pytest.mark.postgres, pytest.mark.e2e]


def start_server(url, factory):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = {
        **os.environ,
        "DATABASE_URL": url,
        "AI_MODE": "simulated",
        "APP_ENV": "test",
        # Binário nativo evita launcher intermediário no Windows e permite wait/kill
        # do processo exato criado pelo teste. Usa os mesmos pacotes da .venv.
        "PYTHONPATH": os.pathsep.join((str(ROOT), sysconfig.get_paths()["purelib"])),
    }
    process = subprocess.Popen(
        [
            sys._base_executable,
            "-m",
            "uvicorn",
            factory,
            "--factory",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--no-access-log",
        ],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    client = httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=5, trust_env=False)
    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            assert process.poll() is None, "Uvicorn encerrou durante inicialização."
            try:
                if client.get("/health").status_code == 200:
                    return process, client
            except httpx.TransportError:
                pass
            time.sleep(0.1)
        raise AssertionError("Servidor não iniciou em 20 segundos.")
    except BaseException:
        stop_server(process, client)
        raise


def stop_server(process, client):
    client.close()
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def test_us05_ca3_actual_process_interruption_restart_and_expiration(migrated_url):
    first, client = start_server(migrated_url, "tests.interrupted_server:create_interrupted_app")
    try:
        original = client.post(
            "/api/v1/tickets",
            json={
                "title": "Erro fictício com interrupção",
                "description": "No ambiente demo, ao salvar dados fictícios ocorre uma falha.",
            },
        )
        assert original.status_code == 201
        path = original.headers["location"]
        with pytest.raises(httpx.TransportError):
            client.post(path + "/triage", json={"expected_version": 1})
        assert first.wait(timeout=10) == 17
    finally:
        stop_server(first, client)
    second, client = start_server(migrated_url, "app.main:create_app")
    try:
        current = client.get(path).json()
        assert current["version"] == 2 and current["triage_status"] == "em_analise"
        active = client.get(path + "/triage-attempts").json()["items"][0]
        blocked = client.post(path + "/triage", json={"expected_version": 2})
        assert blocked.status_code == 409
        assert blocked.json()["error"]["code"] == "triage_in_progress"
        expires = datetime.fromisoformat(active["deadline_at"].replace("Z", "+00:00"))
        # Espera real do lease de 20 s; não altera prazo diretamente no banco.
        while datetime.now(timezone.utc) <= expires:
            time.sleep(0.1)
        response = client.post(path + "/triage", json={"expected_version": 2})
        assert response.status_code == 200, response.text
        ticket = response.json()["ticket"]
        assert ticket["version"] == 5 and ticket["content_revision"] == 1
        assert ticket["description"] == original.json()["description"]
        history = client.get(path + "/triage-attempts").json()
        assert history["total"] == 2
        assert history["items"][0]["error_code"] == "execucao_expirada"
        assert history["items"][1]["status"] == "sucesso"
        assert history["items"][1]["attempt_number"] == 2
    finally:
        stop_server(second, client)
