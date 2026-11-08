from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.tickets import edit_ticket, register_ticket
from app.domain.editing import TicketError
from app.infrastructure.models import Ticket, TicketEvent

pytestmark = pytest.mark.postgres


def seed_classified(engine):
    """Fixture sintética no banco de teste; não representa triagem/revisão executada."""
    suggestion = {
        "attempt_id": str(uuid4()),
        "mode": "simulated",
        "category": "defeito",
        "priority": "alta",
        "rationale": "Classificação fictícia para teste de edição.",
        "missing_fields": ["impacto"],
    }
    final = {"review_id": str(uuid4()), "category": "defeito", "priority": "media"}
    with Session(engine, expire_on_commit=False) as session:
        ticket = register_ticket(
            session, "Título original", "Descrição original fictícia de teste."
        )
        with session.begin():
            ticket.triage_status = "revisada"
            ticket.suggestion, ticket.final_classification = suggestion, final
        return ticket.id, suggestion, final


def test_us03_ca1_archive_classification_and_preserve_history(migrated_url, client):
    """Reaproveitado em US06: agora produz classificação pelas rotas públicas."""
    from tests.review_helpers import REVIEW

    engine = create_engine(migrated_url)
    try:
        created = client.post(
            "/api/v1/tickets",
            json={
                "title": "Título original",
                "description": "Descrição original fictícia de teste.",
            },
        )
        assert created.status_code == 201
        path = created.headers["location"]
        ticket_id = UUID(created.json()["id"])
        triaged = client.post(path + "/triage", json={"expected_version": 1})
        assert triaged.status_code == 200
        reviewed = client.post(path + "/reviews", json={"expected_version": 3, **REVIEW})
        assert reviewed.status_code == 201
        before = client.get(path).json()
        suggestion, final = before["suggestion"], before["final_classification"]
        assert before["suggestion"] == suggestion and before["final_classification"] == final
        history = client.get(path + "/reviews").json()
        attempts = client.get(path + "/triage-attempts").json()
        noop = client.patch(path, json={"expected_version": 4, "title": "  Título original  "})
        assert noop.status_code == 200 and noop.json() == before
        assert client.get(path).json() == before  # inclui timestamps e classificações
        with Session(engine) as session:
            assert len(session.scalars(select(TicketEvent)).all()) == 1
        changed = client.patch(path, json={"expected_version": 4, "title": "Título modificado"})
        assert changed.status_code == 200
        assert changed.json()["suggestion"] is changed.json()["final_classification"] is None
        assert changed.json()["triage_status"] == "pendente"
        assert changed.json()["version"] == 5 and changed.json()["content_revision"] == 2
        assert client.post(path + "/resolve", json={"expected_version": 5}).status_code == 409
        second = client.patch(
            path, json={"expected_version": 5, "description": "Outra descrição fictícia de teste."}
        )
        assert second.status_code == 200
        assert client.get(path + "/reviews").json() == history
        assert client.get(path + "/triage-attempts").json() == attempts
        with Session(engine) as session:
            events = session.scalars(
                select(TicketEvent).order_by(TicketEvent.content_revision)
            ).all()
            assert [event.type for event in events] == ["criado", "editado", "editado"]
            assert events[1].previous_classification == {
                "content_revision": 1,
                "suggestion": suggestion,
                "final_classification": final,
            }
            assert events[2].previous_classification["suggestion"] is None
            assert session.get(Ticket, ticket_id).version == 6
        new_triage = client.post(path + "/triage", json={"expected_version": 6})
        assert new_triage.status_code == 200
        new_review = client.post(path + "/reviews", json={"expected_version": 8, **REVIEW})
        assert new_review.status_code == 201
        assert new_review.json()["review"]["content_revision"] == 3
        assert new_review.json()["review"]["attempt_id"] != reviewed.json()["review"]["attempt_id"]
        assert client.get(path + "/reviews").json()["items"][0] == history["items"][0]
        with Session(engine) as session:
            archived = session.scalar(select(TicketEvent).where(TicketEvent.content_revision == 2))
            assert archived.previous_classification == {
                "content_revision": 1,
                "suggestion": suggestion,
                "final_classification": final,
            }
    finally:
        engine.dispose()


def test_us03_ca2_two_connections_only_one_version_wins(migrated_url):
    engine = create_engine(migrated_url)
    try:
        ticket_id, _, _ = seed_classified(engine)
        barrier = Barrier(2)

        def edit(title):
            with (
                engine.connect() as connection,
                Session(connection, expire_on_commit=False) as session,
            ):
                # Duas conexões reais adquiridas antes da disputa pela mesma linha.
                barrier.wait(timeout=10)
                try:
                    result = edit_ticket(session, ticket_id, 1, {"title": title})
                    return (200, result.title)
                except TicketError as exc:
                    return (exc.status, exc.code)

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(edit, ["Edição concorrente A", "Edição concorrente B"]))
        assert sorted(code for code, _ in results) == [200, 409]
        assert (409, "version_conflict") in results
        with Session(engine) as session:
            ticket = session.get(Ticket, ticket_id)
            assert ticket.version == ticket.content_revision == 2
            assert ticket.title == next(title for code, title in results if code == 200)
            assert len(session.scalars(select(TicketEvent)).all()) == 2
    finally:
        engine.dispose()


def test_us03_edit_event_failure_rolls_back_everything(migrated_url, monkeypatch):
    import app.application.tickets as service

    engine = create_engine(migrated_url)
    try:
        ticket_id, suggestion, final = seed_classified(engine)

        def invalid_event(**kwargs):
            return TicketEvent(**{**kwargs, "type": "invalido"})

        monkeypatch.setattr(service, "TicketEvent", invalid_event)
        with Session(engine) as session:
            with pytest.raises(IntegrityError):
                edit_ticket(session, ticket_id, 1, {"title": "Edição não confirmada"})
        with Session(engine) as session:
            ticket = session.get(Ticket, ticket_id)
            assert ticket.version == ticket.content_revision == 1
            assert ticket.title == "Título original" and ticket.triage_status == "revisada"
            assert ticket.suggestion == suggestion and ticket.final_classification == final
            assert len(session.scalars(select(TicketEvent)).all()) == 1
    finally:
        engine.dispose()


def test_us03_migration_preserves_existing_ticket(database_url):
    from tests.conftest import migrate

    engine = create_engine(database_url)
    try:
        migrate(database_url, "upgrade", "0001")
        ticket_id = uuid4()
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "INSERT INTO tickets "
                "(id,title,description,status,triage_status,version,content_revision) "
                "VALUES (%s,%s,%s,'aberto','pendente',1,1)",
                (ticket_id, "Chamado preservado", "Descrição fictícia anterior à migração."),
            )
        migrate(database_url, "upgrade", "head")
        with Session(engine) as session:
            ticket = session.get(Ticket, ticket_id)
            assert ticket.title == "Chamado preservado" and ticket.suggestion is None
        migrate(database_url, "downgrade", "0001")
        migrate(database_url, "upgrade", "head")
        with Session(engine) as session:
            assert session.get(Ticket, ticket_id).title == "Chamado preservado"
    finally:
        engine.dispose()
