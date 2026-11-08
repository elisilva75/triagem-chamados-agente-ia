from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.agent.protocol import ModelReply, ToolCall
from app.agent.simulated import SimulatedProvider
from app.infrastructure.models import Ticket, TicketEvent, TriageAttempt
from tests.agent_helpers import BOTH, VALID, ScriptProvider

pytestmark = pytest.mark.postgres
BODY = {
    "title": "Erro ao salvar fictício",
    "description": (
        "No ambiente demo, ao salvar, três usuários ficam bloqueados sem alternativa desde 09h."
    ),
}


def create(client, title=None):
    response = client.post("/api/v1/tickets", json={**BODY, **({"title": title} if title else {})})
    assert response.status_code == 201
    return response.headers["location"], response.json()


def test_us04_ca1_real_suggestion_noop_edit_and_immutable_history(client):
    path, original = create(client)
    response = client.post(path + "/triage", json={"expected_version": 1})
    assert response.status_code == 200, response.text
    data = response.json()
    ticket, attempt = data["ticket"], data["attempt"]
    assert ticket["version"] == 3 and ticket["content_revision"] == 1
    assert ticket["status"] == "aberto" and ticket["triage_status"] == "sugerida"
    assert ticket["final_classification"] is None
    assert ticket["suggestion"] == attempt["suggestion"]
    assert attempt["status"] == "sucesso" and attempt["mode"] == "simulated"
    assert attempt["catalog_version"] == attempt["policy_version"] == "1"
    assert attempt["model_calls"] == 3 and attempt["tool_calls"] == 2
    assert attempt["suggestion"]["category"] == "defeito"
    assert attempt["suggestion"]["priority"] == "alta"
    assert attempt["deadline_at"].endswith("Z")
    assert client.get(path).json() == ticket
    noop = client.patch(
        path, json={"expected_version": 3, "title": "  " + original["title"] + "  "}
    )
    assert noop.json() == ticket
    history_before = client.get(path + "/triage-attempts").json()
    edited = client.patch(
        path,
        json={
            "expected_version": 3,
            "description": "Descrição fictícia corrigida para nova análise.",
        },
    )
    assert edited.status_code == 200
    assert edited.json()["version"] == 4 and edited.json()["content_revision"] == 2
    assert edited.json()["suggestion"] is None and edited.json()["triage_status"] == "pendente"
    assert client.get(path + "/triage-attempts").json() == history_before
    with client.app.state.sessions() as session:
        events = session.scalars(
            select(TicketEvent)
            .where(TicketEvent.ticket_id == UUID(ticket["id"]))
            .order_by(TicketEvent.content_revision)
        ).all()
        assert len(events) == 2
        assert events[1].previous_classification["suggestion"] == ticket["suggestion"]
    second = client.post(path + "/triage", json={"expected_version": 4})
    assert second.status_code == 200 and second.json()["attempt"]["attempt_number"] == 2
    history = client.get(path + "/triage-attempts?limit=1&offset=1").json()
    assert history["total"] == 2 and len(history["items"]) == 1
    assert client.get(path + "/triage-attempts?offset=2").json()["items"] == []
    assert client.get(path + "/triage-attempts").json()["items"][0] == attempt


@pytest.mark.parametrize(
    "replies,code,status",
    [
        (
            [BOTH, ModelReply(result={**VALID, "category": "financeiro"})],
            "invalid_ai_response",
            502,
        ),
        ([BOTH, ModelReply(result={**VALID, "priority": "urgente"})], "invalid_ai_response", 502),
        (
            [BOTH, ModelReply(result={**VALID, "extra": "segredo_ficticio"})],
            "invalid_ai_response",
            502,
        ),
        ([BOTH, ModelReply(result={**VALID, "rationale": "curta"})], "invalid_ai_response", 502),
        ([ModelReply(calls=(ToolCall("shell"),))], "tool_protocol_error", 502),
        ([ModelReply(result=VALID)], "tool_protocol_error", 502),
        ([BOTH, BOTH, BOTH], "execution_limit", 502),
        ([TimeoutError("segredo_ficticio")], "ai_timeout", 504),
        ([ConnectionError("segredo_ficticio")], "ai_unavailable", 503),
    ],
)
def test_us04_ca2_failures_persist_without_publishing(client, replies, code, status, caplog):
    path, original = create(client)
    client.app.state.provider = ScriptProvider(replies)
    with caplog.at_level("INFO", logger="app.application.triage"):
        response = client.post(path + "/triage", json={"expected_version": 1})
    assert response.status_code == status, response.text
    assert response.json()["error"]["code"] == code
    assert response.json()["error"]["details"][0]["triage_status"] == "falha"
    after = client.get(path).json()
    assert after["title"] == original["title"] and after["description"] == original["description"]
    assert after["version"] == 3 and after["content_revision"] == 1
    assert after["triage_status"] == "falha" and after["suggestion"] is None
    assert after["final_classification"] is None
    attempt = client.get(path + "/triage-attempts").json()["items"][0]
    assert attempt["status"] == "falha" and attempt["error_code"] == code
    assert attempt["suggestion"] is None
    assert "segredo_ficticio" not in response.text + str(attempt) + caplog.text
    assert original["description"] not in caplog.text


def test_us04_public_simulation_failure_marker(client):
    path, _ = create(client, "[SIMULADO:saida-invalida]")
    response = client.post(path + "/triage", json={"expected_version": 1})
    assert response.status_code == 502
    assert (
        client.get(path + "/triage-attempts").json()["items"][0]["error_code"]
        == "invalid_ai_response"
    )


def test_us04_attempt_committed_and_no_connection_held_during_provider(client):
    path, original = create(client)
    delegate = SimulatedProvider()

    class Observer:
        def respond(self, *args, **kwargs):
            # A conexão do início já foi devolvida ao pool antes da chamada.
            assert client.app.state.engine.pool.checkedout() == 0
            with client.app.state.sessions() as session:
                ticket = session.get(Ticket, UUID(original["id"]))
                assert ticket.triage_status == "em_analise" and ticket.version == 2
                attempt = session.scalar(select(TriageAttempt))
                assert attempt.status == "em_analise"
            assert (
                client.patch(
                    path, json={"expected_version": 2, "title": "Alteração bloqueada"}
                ).status_code
                == 409
            )
            assert client.post(path + "/triage", json={"expected_version": 2}).status_code == 409
            return delegate.respond(*args, **kwargs)

    client.app.state.provider = Observer()
    response = client.post(path + "/triage", json={"expected_version": 1})
    assert response.status_code == 200, response.text
    assert client.get(path + "/triage-attempts").json()["total"] == 1


def test_us04_contract_guards_and_no_provider_on_crud(client):
    class Forbidden:
        def respond(self, *args, **kwargs):
            raise AssertionError("CRUD chamou provedor")

    client.app.state.provider = Forbidden()
    path, _ = create(client)
    assert client.get(path).status_code == 200
    assert client.get("/api/v1/tickets").status_code == 200
    assert (
        client.patch(
            path, json={"expected_version": 1, "title": "Título corrigido fictício"}
        ).status_code
        == 200
    )
    for body in [
        {},
        {"expected_version": True},
        {"expected_version": "2"},
        {"expected_version": 0},
        {"expected_version": 2, "scenario": "sucesso"},
    ]:
        assert client.post(path + "/triage", json=body).status_code == 422
    assert client.post(path + "/triage", json={"expected_version": 1}).status_code == 409
    assert (
        client.post(f"/api/v1/tickets/{uuid4()}/triage", json={"expected_version": 1}).status_code
        == 404
    )
    assert client.get(f"/api/v1/tickets/{uuid4()}/triage-attempts").status_code == 404
    for query in ["limit=0", "limit=101", "offset=-1"]:
        assert client.get(path + "/triage-attempts?" + query).status_code == 422
    assert client.get(path + "/triage-attempts").json()["total"] == 0
    client.app.state.provider = SimulatedProvider()
    response = client.post(path + "/triage", json={"expected_version": 2})
    assert response.status_code == 200
    assert client.post(path + "/triage", json={"expected_version": 4}).status_code == 409


def test_us04_database_active_attempt_and_result_constraints(client):
    _, original = create(client)
    now = datetime.now(timezone.utc)
    values = dict(
        ticket_id=UUID(original["id"]),
        content_revision=1,
        status="em_analise",
        mode="simulated",
        catalog_version="1",
        policy_version="1",
        started_at=now,
        deadline_at=now + timedelta(seconds=20),
    )
    with client.app.state.sessions() as session:
        with session.begin():
            session.add(TriageAttempt(**values, attempt_number=1))
        with pytest.raises(IntegrityError), session.begin():
            session.add(TriageAttempt(**values, attempt_number=2))
            session.flush()
        with pytest.raises(IntegrityError), session.begin():
            session.add(TriageAttempt(**{**values, "status": "sucesso"}, attempt_number=2))
            session.flush()
