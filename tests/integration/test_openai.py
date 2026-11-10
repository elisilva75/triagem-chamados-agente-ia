import socket
import subprocess
from pathlib import Path

import httpx
import pytest
from pydantic import SecretStr
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

from app.agent.groq_provider import GroqProvider
from tests.conftest import migrate
from tests.openai_helpers import OUTPUT, calls, fake_provider, message, response
from tests.review_helpers import REVIEW, suggested


@pytest.fixture(autouse=True)
def block_external(monkeypatch):
    original = socket.socket.connect

    def connect(sock, address):
        if isinstance(address, tuple) and address[0] in {"127.0.0.1", "::1"}:
            return original(sock, address)
        raise AssertionError("Rede externa bloqueada.")

    monkeypatch.setattr(socket.socket, "connect", connect)


@pytest.mark.parametrize("provider_name", ["openai", "groq"])
@pytest.mark.parametrize("outcome", ["success", "invalid", "timeout", "quota", "rate", "missing"])
def test_openai_persistence_and_human_review(client, migrated_url, outcome, provider_name):
    requests = []

    def handler(request):
        requests.append(request)
        if outcome == "timeout":
            raise httpx.ReadTimeout("Dado fictício privado", request=request)
        if outcome in {"quota", "rate", "missing"}:
            error = {"message": "Detalhe privado fictício do provedor."}
            if outcome == "quota":
                error.update(code="insufficient_quota", type="insufficient_quota")
            elif outcome == "rate":
                error.update(code="rate_limit_exceeded", type="requests")
            return httpx.Response(
                429, json={"error": error}, headers={"x-request-id": "req_fake429"}
            )
        if len(requests) == 1:
            return response(calls())
        return response(
            message({**OUTPUT, "category": "financeiro"} if outcome == "invalid" else OUTPUT)
        )

    client.app.state.provider = fake_provider(handler)
    if provider_name == "groq":
        client.app.state.provider = GroqProvider(
            SecretStr("chave-ficticia-sem-validade"),
            "modelo-ficticio",
            transport=httpx.MockTransport(handler),
        )
    payload = {
        "title": "Erro fictício OpenAI",
        "description": "Descrição fictícia para triagem local.",
    }
    before = client.post("/api/v1/tickets", json=payload).json()
    path = "/api/v1/tickets/" + before["id"]
    result = client.post(path + "/triage", json={"expected_version": 1})
    assert (
        result.status_code
        == {
            "success": 200,
            "invalid": 502,
            "timeout": 504,
            "quota": 503,
            "rate": 503,
            "missing": 503,
        }[outcome]
    )
    if outcome in {"quota", "rate", "missing"}:
        public = result.json()["error"]
        assert public["code"] == "ai_unavailable"
        assert public["message"] == "A triagem falhou; consulte o chamado."
        assert set(public) == {"code", "message", "details", "request_id"}
        assert public["details"] == [
            {
                "ticket_id": before["id"],
                "attempt_id": public["details"][0]["attempt_id"],
                "triage_status": "falha",
            }
        ]
        for private in (
            "insufficient_quota",
            "rate_limit_exceeded",
            "req_fake429",
            "Detalhe privado",
        ):
            assert private not in result.text
        assert len(requests) == 1
    current = client.get(path).json()
    assert {key: current[key] for key in payload} == payload
    assert current["id"] == before["id"]
    attempts = client.get(path + "/triage-attempts").json()["items"]
    assert len(attempts) == 1
    assert attempts[0]["mode"] == attempts[0]["provider"] == provider_name
    assert attempts[0]["model"] == "modelo-ficticio"
    assert attempts[0]["status"] == ("sucesso" if outcome == "success" else "falha")
    assert "chave-ficticia" not in result.text
    assert "Dado fictício privado" not in result.text
    if outcome == "success":
        assert current["suggestion"]["mode"] == provider_name
        reviewed = client.post(path + "/reviews", json={"expected_version": 3, **REVIEW})
        assert reviewed.status_code == 201
        resolved = client.post(path + "/resolve", json={"expected_version": 4})
        assert resolved.status_code == 200
        engine = create_engine(migrated_url)
        try:
            sql = (
                Path(__file__).resolve().parents[2] / "scripts/triage_review_agreement.sql"
            ).read_text(encoding="utf-8")
            with engine.connect() as connection:
                row = connection.exec_driver_sql(sql).one()
                assert tuple(row[:3]) == (provider_name, 1, 1)
                assert row[4] == row[6] == 1
            for change in ("model=NULL", "provider=NULL", "mode='simulated'", "mode='outro'"):
                with pytest.raises(IntegrityError), engine.begin() as connection:
                    connection.exec_driver_sql(f"UPDATE triage_attempts SET {change}")
            # O downgrade não pode apagar/converter tentativas do provedor.
            with pytest.raises(subprocess.CalledProcessError):
                migrate(migrated_url, "downgrade", "0005" if provider_name == "groq" else "0004")
            with engine.connect() as connection:
                assert (
                    connection.exec_driver_sql("SELECT version_num FROM alembic_version").scalar()
                    == "0006"
                )
                assert (
                    connection.exec_driver_sql("SELECT mode FROM triage_attempts").scalar()
                    == provider_name
                )
            assert client.get(path).json() == resolved.json()
            if provider_name == "openai":
                # Valida 0005 -> 0006 também com metadados e revisão OpenAI existentes.
                migrate(migrated_url, "downgrade", "0005")
                with engine.connect() as connection:
                    before_upgrade = (
                        connection.exec_driver_sql(
                            "SELECT to_jsonb(t) FROM triage_attempts t ORDER BY id"
                        )
                        .scalars()
                        .all()
                    )
                migrate(migrated_url, "upgrade", "head")
                with engine.connect() as connection:
                    assert (
                        connection.exec_driver_sql(
                            "SELECT to_jsonb(t) FROM triage_attempts t ORDER BY id"
                        )
                        .scalars()
                        .all()
                        == before_upgrade
                    )
                assert client.get(path).json() == resolved.json()
        finally:
            engine.dispose()
    else:
        assert current["triage_status"] == "falha"
        assert current["suggestion"] is None
        assert current["version"] == 3


def test_upgrade_preserves_simulated_history(client, migrated_url):
    path, _ = suggested(client)
    assert client.post(path + "/reviews", json={"expected_version": 3, **REVIEW}).status_code == 201
    engine = create_engine(migrated_url)
    try:
        # Retorno a 0004 somente neste banco descartável com dados simulados.
        migrate(migrated_url, "downgrade", "0004")

        def snapshot():
            with engine.connect() as connection:
                return {
                    table: connection.execute(
                        text(
                            f"SELECT to_jsonb(t) - 'provider' - 'model' FROM {table} t ORDER BY id"
                        )
                    )
                    .scalars()
                    .all()
                    for table in ("tickets", "ticket_events", "triage_attempts", "human_reviews")
                }

        before = snapshot()
        assert all(before.values())
        migrate(migrated_url, "upgrade", "head")
        assert snapshot() == before
        migrate(migrated_url, "check")
        with engine.connect() as connection:
            assert connection.execute(
                text("SELECT provider, model FROM triage_attempts")
            ).all() == [(None, None)]
        assert client.get(path).json()["triage_status"] == "revisada"
    finally:
        engine.dispose()
