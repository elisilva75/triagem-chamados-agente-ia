from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Event
from uuid import UUID

import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session

from app.agent.simulated import SimulatedProvider
from app.application.triage import triage_ticket
from app.domain.editing import TicketError
from app.infrastructure.models import TriageAttempt
from tests.api.test_triage import create

pytestmark = pytest.mark.postgres


def test_us05_ca3_late_result_cannot_overwrite_recovered_attempt(client, monkeypatch):
    from app.application import triage

    now = [datetime.now(timezone.utc)]
    monkeypatch.setattr(triage, "utc_now", lambda: now[0])
    path, original = create(client)
    entered, release = Event(), Event()
    delegate = SimulatedProvider()

    class Paused:
        def respond(self, *args, **kwargs):
            entered.set()
            if not release.wait(10):
                raise TimeoutError
            return delegate.respond(*args, **kwargs)

    with ThreadPoolExecutor(max_workers=1) as pool:
        previous = pool.submit(
            triage_ticket, client.app.state.sessions, UUID(original["id"]), 1, Paused()
        )
        try:
            assert entered.wait(5)
            active = client.get(path + "/triage-attempts").json()
            blocked = client.post(path + "/triage", json={"expected_version": 2})
            assert blocked.status_code == 409
            assert blocked.json()["error"]["code"] == "triage_in_progress"
            assert client.get(path + "/triage-attempts").json() == active
            now[0] += timedelta(seconds=20)
            response = client.post(path + "/triage", json={"expected_version": 2})
            assert response.status_code == 200, response.text
            winner = response.json()["ticket"]
            history = client.get(path + "/triage-attempts").json()
            assert history["total"] == 2
            assert history["items"][0]["error_code"] == "execucao_expirada"
            assert history["items"][0]["suggestion"] is None
            assert winner["version"] == 5 and winner["content_revision"] == 1
        finally:
            release.set()
        with pytest.raises(TicketError) as exc:
            previous.result(timeout=5)
        assert exc.value.status == 409 and exc.value.code == "version_conflict"
    assert client.get(path).json() == winner
    assert client.get(path + "/triage-attempts").json() == history


def test_us05_recovery_and_new_attempt_are_atomic(client, monkeypatch):
    from app.application import triage

    now = [datetime.now(timezone.utc)]
    monkeypatch.setattr(triage, "utc_now", lambda: now[0])
    path, original = create(client)

    class Interrupted(BaseException):
        pass

    class Crash:
        def respond(self, *args, **kwargs):
            raise Interrupted

    with pytest.raises(Interrupted):
        triage_ticket(client.app.state.sessions, UUID(original["id"]), 1, Crash())
    before = client.get(path).json()
    history = client.get(path + "/triage-attempts").json()
    now[0] += timedelta(seconds=21)

    def break_new_attempt(session, flush_context, instances):
        for obj in session.new:
            if isinstance(obj, TriageAttempt) and obj.attempt_number == 2:
                obj.mode = "invalido"  # falha real da aquisição, após marcar anterior expirada

    event.listen(Session, "before_flush", break_new_attempt)
    try:
        failed = client.post(path + "/triage", json={"expected_version": 2})
    finally:
        event.remove(Session, "before_flush", break_new_attempt)
    assert failed.status_code == 503 and failed.json()["error"]["code"] == "storage_unavailable"
    assert client.get(path).json() == before
    assert client.get(path + "/triage-attempts").json() == history
    response = client.post(path + "/triage", json={"expected_version": 2})
    assert response.status_code == 200
    assert response.json()["ticket"]["version"] == 5
