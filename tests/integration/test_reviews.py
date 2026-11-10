from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import UUID

import pytest
from sqlalchemy import create_engine, event, func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.infrastructure.models import HumanReview, Ticket, TicketEvent
from tests.review_helpers import REVIEW, suggested

pytestmark = pytest.mark.postgres


def reviewed(client):
    path, _ = suggested(client)
    response = client.post(path + "/reviews", json={"expected_version": 3, **REVIEW})
    assert response.status_code == 201
    return path, response.json()["ticket"]


def test_us06_review_and_projection_rollback_together(client):
    path, before = suggested(client)
    attempts = client.get(path + "/triage-attempts").json()

    def invalid_projection(session, flush_context, instances):
        for obj in session.dirty:
            if (
                isinstance(obj, Ticket)
                and obj.id == UUID(before["id"])
                and obj.triage_status == "revisada"
            ):
                obj.title = "x"  # CHECK real, depois de inserir HumanReview na transação

    event.listen(Session, "before_flush", invalid_projection)
    try:
        response = client.post(path + "/reviews", json={"expected_version": 3, **REVIEW})
    finally:
        event.remove(Session, "before_flush", invalid_projection)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "storage_unavailable"
    assert client.get(path).json() == before
    assert client.get(path + "/reviews").json()["total"] == 0
    assert client.get(path + "/triage-attempts").json() == attempts


@pytest.mark.parametrize("action", ["resolve", "reopen"])
def test_us06_transition_event_failure_rolls_back_everything(client, monkeypatch, action):
    from app.application import reviews

    path, before = reviewed(client)
    if action == "reopen":
        response = client.post(path + "/resolve", json={"expected_version": 4})
        assert response.status_code == 200
        before = response.json()
    history = client.get(path + "/reviews").json()
    with client.app.state.sessions() as session:
        event_count = session.scalar(select(func.count()).select_from(TicketEvent))

    def invalid_event(**values):
        return TicketEvent(**{**values, "type": "invalido"})

    monkeypatch.setattr(reviews, "TicketEvent", invalid_event)
    response = client.post(path + "/" + action, json={"expected_version": before["version"]})
    assert response.status_code == 503
    assert client.get(path).json() == before
    assert client.get(path + "/reviews").json() == history
    with client.app.state.sessions() as session:
        assert session.scalar(select(func.count()).select_from(TicketEvent)) == event_count


@pytest.mark.parametrize(
    "actions",
    [
        ("reviews", "reviews"),
        ("reviews", "edit"),
        ("resolve", "resolve"),
        ("resolve", "edit"),
        ("resolve", "reviews"),
        ("reopen", "reopen"),
    ],
)
def test_us06_ca4_two_connections_one_version_wins(client, actions):
    path, before = suggested(client)
    if actions != ("reviews", "reviews"):
        response = client.post(path + "/reviews", json={"expected_version": 3, **REVIEW})
        before = response.json()["ticket"]
    if "reopen" in actions:
        before = client.post(path + "/resolve", json={"expected_version": 4}).json()
    history = client.get(path + "/reviews").json()
    attempts = client.get(path + "/triage-attempts").json()
    with client.app.state.sessions() as session:
        event_count = session.scalar(select(func.count()).select_from(TicketEvent))
    barrier = Barrier(2)

    def run(action):
        barrier.wait(timeout=5)
        body = {"expected_version": before["version"]}
        if action == "edit":
            return client.patch(path, json={**body, "title": "Título corrigido concorrente"})
        return client.post(
            path + "/" + action, json={**body, **(REVIEW if action == "reviews" else {})}
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(run, actions))
    assert sum(r.status_code in (200, 201) for r in responses) == 1
    loser = next(r for r in responses if r.status_code == 409)
    assert loser.json()["error"]["code"] == "version_conflict"
    winner = next(action for action, r in zip(actions, responses) if r.status_code in (200, 201))
    current = client.get(path).json()
    assert current["version"] == before["version"] + 1
    assert current["content_revision"] == before["content_revision"] + (winner == "edit")
    after = client.get(path + "/reviews").json()
    assert after["total"] == history["total"] + (winner == "reviews")
    assert after["items"][: history["total"]] == history["items"]
    assert client.get(path + "/triage-attempts").json() == attempts
    with client.app.state.sessions() as session:
        assert session.scalar(select(func.count()).select_from(TicketEvent)) == event_count + (
            winner != "reviews"
        )
    if winner == "edit":
        assert current["triage_status"] == "pendente" and current["final_classification"] is None
    elif winner in ("resolve", "reopen"):
        assert current["final_classification"] == before["final_classification"]
        assert current["status"] == ("resolvido" if winner == "resolve" else "aberto")


def test_us06_review_fk_and_current_projection_belong_to_same_content(client):
    path, first = reviewed(client)
    other_path, second = reviewed(client)
    first_review = client.get(path + "/reviews").json()["items"][0]
    values = {
        "ticket_id": UUID(first["id"]),
        "attempt_id": UUID(first_review["attempt_id"]),
        "content_revision": 1,
        **REVIEW,
    }
    for changes in (
        {"ticket_id": UUID(second["id"])},
        {"content_revision": 2},
        {"category": "financeiro"},
        {"reason": "curta"},
    ):
        with client.app.state.sessions() as session:
            with pytest.raises(IntegrityError), session.begin():
                session.add(HumanReview(**{**values, **changes}))
                session.flush()
    assert client.get(path + "/reviews").json()["total"] == 1
    assert client.get(other_path + "/reviews").json()["total"] == 1
    # A projeção atual é interna: fixture corrompida testa a checagem transacional,
    # além da FK composta de HumanReview, sem criar essa possibilidade pela API.
    with client.app.state.sessions() as session, session.begin():
        ticket = session.get(Ticket, UUID(first["id"]))
        ticket.final_classification = second["final_classification"]
    before = client.get(path).json()
    for action in ("resolve", "reviews"):
        body = {"expected_version": 4, **(REVIEW if action == "reviews" else {})}
        response = client.post(path + "/" + action, json=body)
        assert response.status_code == 409
    assert client.get(path).json() == before


def test_us06_migration_preserves_attempts_and_classification_snapshots(database_url):
    from app.agent.simulated import SimulatedProvider
    from app.application.tickets import edit_ticket, register_ticket
    from app.application.triage import triage_ticket
    from app.infrastructure.database import make_sessions
    from tests.conftest import migrate

    # O código atual exige head; preparar dados e só então retornar ao esquema histórico.
    migrate(database_url, "upgrade", "head")
    engine = create_engine(database_url)
    sessions = make_sessions(engine)
    try:
        with sessions() as session:
            ticket_id = register_ticket(
                session, "Erro fictício anterior", "Descrição fictícia anterior à migração."
            ).id
        triage_ticket(sessions, ticket_id, 1, SimulatedProvider())
        with sessions() as session:
            edit_ticket(session, ticket_id, 3, {"title": "Título corrigido anterior"})
        migrate(database_url, "downgrade", "0003")

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
                    for table in ("tickets", "ticket_events", "triage_attempts")
                }

        before = snapshot()
        migrate(database_url, "upgrade", "head")
        assert snapshot() == before
        migrate(database_url, "check")
        migrate(database_url, "downgrade", "0003")
        assert snapshot() == before
        migrate(database_url, "upgrade", "head")
        assert snapshot() == before
    finally:
        engine.dispose()
