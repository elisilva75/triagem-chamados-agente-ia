import json
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from uuid import UUID

import pytest
from sqlalchemy import create_engine, text

from app.agent.simulated import SimulatedProvider
from app.application.triage import triage_ticket
from app.domain.editing import TicketError
from tests.conftest import migrate

pytestmark = pytest.mark.postgres


def test_us04_migration_preserves_existing_data(database_url):
    migrate(database_url, "upgrade", "0002")
    engine = create_engine(database_url)
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO tickets (id,title,description,status,triage_status,"
                    "version,content_revision,suggestion) VALUES "
                    "('11111111-1111-4111-8111-111111111111','Chamado anterior',"
                    "'Descrição fictícia anterior à migração.','aberto','pendente',2,2,NULL)"
                )
            )
            connection.execute(
                text(
                    "INSERT INTO ticket_events (id,ticket_id,type,content_revision,"
                    "previous_classification) VALUES "
                    "('22222222-2222-4222-8222-222222222222',"
                    "'11111111-1111-4111-8111-111111111111','editado',2,"
                    "CAST(:snapshot AS jsonb))"
                ),
                {
                    "snapshot": json.dumps(
                        {"suggestion": None, "content_revision": 1, "final_classification": None}
                    )
                },
            )

        def snapshot():
            with engine.connect() as connection:
                return [
                    connection.execute(text(f"SELECT row_to_json(t) FROM {table} t ORDER BY id"))
                    .scalars()
                    .all()
                    for table in ("tickets", "ticket_events")
                ]

        before = snapshot()
        migrate(database_url, "upgrade", "head")
        assert snapshot() == before
        migrate(database_url, "check")
        migrate(database_url, "downgrade", "0002")
        assert snapshot() == before
        migrate(database_url, "upgrade", "head")
        assert snapshot() == before
    finally:
        engine.dispose()


def test_us04_only_one_simulator_runs_for_concurrent_requests(client):
    created = client.post(
        "/api/v1/tickets",
        json={
            "title": "Erro fictício concorrente",
            "description": "Descrição fictícia de teste concorrente.",
        },
    ).json()
    ticket_id = UUID(created["id"])
    entered, release = Event(), Event()
    delegate = SimulatedProvider()

    class Paused:
        def respond(self, *args, **kwargs):
            entered.set()
            if not release.wait(5):
                raise TimeoutError
            return delegate.respond(*args, **kwargs)

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(triage_ticket, client.app.state.sessions, ticket_id, 1, Paused())
        try:
            assert entered.wait(5)
            with pytest.raises(TicketError) as exc:
                triage_ticket(client.app.state.sessions, ticket_id, 1, delegate)
            assert exc.value.code == "version_conflict"
        finally:
            release.set()
        response = future.result(timeout=5)
    assert response["ticket"].version == 3
    history = client.get(f"/api/v1/tickets/{ticket_id}/triage-attempts").json()
    assert history["total"] == 1
