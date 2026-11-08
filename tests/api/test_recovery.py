from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timedelta, timezone
from threading import Barrier, Event
from uuid import UUID

import pytest
from sqlalchemy import event, select
from sqlalchemy.orm import Session

from app.agent.protocol import ModelReply
from app.agent.simulated import SimulatedProvider
from app.infrastructure.models import TicketEvent, TriageAttempt
from tests.agent_helpers import BOTH, VALID, ScriptProvider
from tests.api.test_triage import create

pytestmark = pytest.mark.postgres


@pytest.mark.parametrize(
    "failure,status,code",
    [
        ([TimeoutError("segredo_ficticio")], 504, "ai_timeout"),
        ([ConnectionError("segredo_ficticio")], 503, "ai_unavailable"),
        (
            [BOTH, ModelReply(result={**VALID, "category": "financeiro"})],
            502,
            "invalid_ai_response",
        ),
    ],
)
def test_us05_ca1_retry_preserves_content_and_failed_attempt(client, failure, status, code):
    path, original = create(client)
    client.app.state.provider = ScriptProvider(failure)
    failed = client.post(path + "/triage", json={"expected_version": 1})
    assert failed.status_code == status and failed.json()["error"]["code"] == code
    first = client.get(path + "/triage-attempts").json()["items"][0]
    assert first["status"] == "falha" and first["suggestion"] is None
    assert client.post(path + "/triage", json={"expected_version": 1}).status_code == 409
    client.app.state.provider = SimulatedProvider()
    current = client.get(path).json()
    assert current["version"] == 3
    response = client.post(path + "/triage", json={"expected_version": current["version"]})
    assert response.status_code == 200, response.text
    ticket = response.json()["ticket"]
    assert ticket["version"] == 5 and ticket["triage_status"] == "sugerida"
    for field in ("title", "description", "content_revision", "created_at", "status"):
        assert ticket[field] == original[field]
    assert ticket["final_classification"] is None
    history = client.get(path + "/triage-attempts").json()
    assert history["total"] == 2 and history["items"][0] == first
    assert history["items"][1]["attempt_number"] == 2
    assert history["items"][1]["suggestion"] == ticket["suggestion"]
    with client.app.state.sessions() as session:
        events = session.scalars(select(TicketEvent)).all()
        assert len(events) == 1 and events[0].type == "criado"


def test_us05_ca2_two_simultaneous_retry_posts_run_one_agent(client):
    path, _ = create(client)
    client.app.state.provider = ScriptProvider([TimeoutError()])
    assert client.post(path + "/triage", json={"expected_version": 1}).status_code == 504
    barrier, release = Barrier(2), Event()
    delegate = SimulatedProvider()
    invocations = []

    class Paused:
        def respond(self, *args, **kwargs):
            invocations.append(1)
            if not release.wait(5):
                raise TimeoutError
            return delegate.respond(*args, **kwargs)

    client.app.state.provider = Paused()

    def post():
        barrier.wait(timeout=5)
        return client.post(path + "/triage", json={"expected_version": 3})

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(post) for _ in range(2)]
        try:
            done, _ = wait(futures, timeout=5, return_when=FIRST_COMPLETED)
            assert len(done) == 1
            assert next(iter(done)).result().status_code == 409
        finally:
            release.set()
        responses = [future.result(timeout=5) for future in futures]
    assert sorted(r.status_code for r in responses) == [200, 409]
    assert len(invocations) == 3  # três passos de UM agente simulado
    assert client.get(path + "/triage-attempts").json()["total"] == 2
    assert client.get(path).json()["version"] == 5


@pytest.mark.parametrize("elapsed,status", [(19.999, 200), (20.0, 504), (20.001, 504)])
def test_us05_ca1_ca3_finalization_deadline_boundary(client, monkeypatch, elapsed, status):
    from app.application import triage

    now = [datetime.now(timezone.utc)]
    start = now[0]
    monkeypatch.setattr(triage, "utc_now", lambda: now[0])
    delegate = SimulatedProvider()

    class AdvanceClock:
        def respond(self, *args, **kwargs):
            reply = delegate.respond(*args, **kwargs)
            if reply.result is not None:
                now[0] = start + timedelta(seconds=elapsed)
            return reply

    client.app.state.provider = AdvanceClock()
    path, _ = create(client)
    response = client.post(path + "/triage", json={"expected_version": 1})
    assert response.status_code == status, response.text
    attempt = client.get(path + "/triage-attempts").json()["items"][0]
    if status == 504:
        assert attempt["error_code"] == "ai_timeout" and attempt["suggestion"] is None
        assert client.get(path).json()["suggestion"] is None
    else:
        assert attempt["status"] == "sucesso"


def test_us05_ca4_real_constraint_failure_rolls_back_finalization_then_recovers(
    client, monkeypatch
):
    from app.application import triage

    now = [datetime.now(timezone.utc)]
    monkeypatch.setattr(triage, "utc_now", lambda: now[0])
    path, original = create(client)

    def break_finalization(session, flush_context, instances):
        for obj in session.dirty:
            if (
                isinstance(obj, TriageAttempt)
                and obj.ticket_id == UUID(original["id"])
                and obj.status == "sucesso"
            ):
                obj.status = "invalido"  # violação real de CHECK no PostgreSQL isolado

    event.listen(Session, "before_flush", break_finalization)
    try:
        response = client.post(path + "/triage", json={"expected_version": 1})
    finally:
        event.remove(Session, "before_flush", break_finalization)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "storage_unavailable"
    assert response.json()["error"]["details"] == []
    current = client.get(path).json()
    assert current["version"] == 2 and current["triage_status"] == "em_analise"
    assert current["suggestion"] is None
    active = client.get(path + "/triage-attempts").json()["items"][0]
    assert active["status"] == "em_analise" and active["finished_at"] is None
    assert active["error_code"] is None and active["suggestion"] is None
    blocked = client.post(path + "/triage", json={"expected_version": 2})
    assert blocked.status_code == 409 and blocked.json()["error"]["code"] == "triage_in_progress"
    now[0] += timedelta(seconds=20)
    # Versão antiga não pode recuperar nem alterar histórico.
    assert client.post(path + "/triage", json={"expected_version": 1}).status_code == 409
    assert client.get(path + "/triage-attempts").json()["items"][0] == active
    recovered = client.post(path + "/triage", json={"expected_version": 2})
    assert recovered.status_code == 200, recovered.text
    ticket = recovered.json()["ticket"]
    assert ticket["version"] == 5 and ticket["content_revision"] == 1
    assert ticket["description"] == original["description"]
    history = client.get(path + "/triage-attempts").json()
    assert history["total"] == 2
    assert history["items"][0]["error_code"] == "execucao_expirada"
    assert history["items"][1]["status"] == "sucesso"
    assert history["items"][1]["attempt_number"] == 2
