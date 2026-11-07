from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from uuid import uuid4

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
    engine = create_engine(migrated_url)
    try:
        ticket_id, suggestion, final = seed_classified(engine)
        before = client.get(f"/api/v1/tickets/{ticket_id}").json()
        assert before["suggestion"] == suggestion and before["final_classification"] == final
        with Session(engine, expire_on_commit=False) as session:
            unchanged = edit_ticket(session, ticket_id, 1, {"title": "Título original"})
            assert unchanged.suggestion == suggestion and unchanged.final_classification == final
            assert unchanged.triage_status == "revisada"
            changed = edit_ticket(session, ticket_id, 1, {"title": "Título modificado"})
            assert changed.suggestion is changed.final_classification is None
            assert changed.triage_status == "pendente"
            edit_ticket(
                session, ticket_id, 2, {"description": "Outra descrição fictícia de teste."}
            )
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
            assert session.get(Ticket, ticket_id).version == 3
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
