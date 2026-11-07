from uuid import uuid4

import pytest
from sqlalchemy import create_engine, func, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.tickets import register_ticket
from app.infrastructure.database import Base
from app.infrastructure.models import Ticket, TicketEvent
from tests.conftest import migrate

pytestmark = pytest.mark.postgres


def test_us02_service_rolls_back_when_event_fails(migrated_url, monkeypatch):
    from app.infrastructure import repositories

    def invalid_event(**kwargs):
        return TicketEvent(**{**kwargs, "type": "invalido"})

    monkeypatch.setattr(repositories, "TicketEvent", invalid_event)
    engine = create_engine(migrated_url)
    try:
        with Session(engine) as session:
            with pytest.raises(IntegrityError):
                register_ticket(session, "Chamado fictício", "d" * 20)
            assert session.scalar(select(func.count()).select_from(Ticket)) == 0
            assert session.scalar(select(func.count()).select_from(TicketEvent)) == 0
    finally:
        engine.dispose()


def test_us01_ca3_migrations_roundtrip_and_metadata(database_url):
    engine = create_engine(database_url)
    try:
        migrate(database_url, "upgrade", "head")
        migrate(database_url, "upgrade", "head")
        assert {"tickets", "ticket_events"} <= set(inspect(engine).get_table_names())
        migrate(database_url, "check")
        migrate(database_url, "downgrade", "base")
        assert "tickets" not in inspect(engine).get_table_names()
        migrate(database_url, "upgrade", "head")
        assert set(Base.metadata.tables) <= set(inspect(engine).get_table_names())
    finally:
        engine.dispose()


def test_us02_atomic_event_and_reconnect(migrated_url):
    engine = create_engine(migrated_url)
    with Session(engine, expire_on_commit=False) as session:
        ticket = register_ticket(session, "Chamado fictício", "d" * 20)
        ticket_id = ticket.id
    engine.dispose()
    with Session(engine) as session:
        assert session.get(Ticket, ticket_id).title == "Chamado fictício"
        event = session.scalar(select(TicketEvent).where(TicketEvent.ticket_id == ticket_id))
        assert event.type == "criado"
    engine.dispose()


def test_us02_rollback_and_database_constraints(migrated_url):
    engine = create_engine(migrated_url)
    try:
        with Session(engine) as session:
            with pytest.raises(IntegrityError), session.begin():
                ticket = Ticket(title="Chamado fictício", description="d" * 20)
                session.add(ticket)
                session.flush()
                session.add(TicketEvent(ticket_id=uuid4(), type="criado", content_revision=1))
                session.flush()
            assert session.scalar(select(func.count()).select_from(Ticket)) == 0
            session.rollback()
            with pytest.raises(IntegrityError), session.begin():
                session.add(Ticket(title="cur", description="d" * 20))
                session.flush()
    finally:
        engine.dispose()
