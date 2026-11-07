from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.infrastructure.models import Ticket, TicketEvent

pytestmark = pytest.mark.postgres
BODY = {"title": "Chamado para edição", "description": "Descrição fictícia original para edição."}


def test_us03_ca1_patch_content_and_history(client, migrated_url):
    original = client.post("/api/v1/tickets", json=BODY).json()
    path = "/api/v1/tickets/" + original["id"]
    response = client.patch(
        path, json={"expected_version": 1, "description": "Nova descrição fictícia corrigida."}
    )
    assert response.status_code == 200
    changed = response.json()
    assert changed["title"] == original["title"]
    assert changed["description"] == "Nova descrição fictícia corrigida."
    assert changed["version"] == changed["content_revision"] == 2
    assert changed["created_at"] == original["created_at"]
    assert changed["updated_at"] >= original["updated_at"]
    assert changed["triage_status"] == "pendente" and changed["status"] == "aberto"
    assert changed["suggestion"] is changed["final_classification"] is None
    assert client.get(path).json() == changed
    engine = create_engine(migrated_url)
    try:
        with Session(engine) as session:
            events = session.scalars(
                select(TicketEvent).order_by(TicketEvent.content_revision)
            ).all()
            assert [event.type for event in events] == ["criado", "editado"]
            assert events[1].previous_classification["content_revision"] == 1
    finally:
        engine.dispose()


def test_us03_ca2_stale_version_and_not_found(client):
    original = client.post("/api/v1/tickets", json=BODY).json()
    path = "/api/v1/tickets/" + original["id"]
    response = client.patch(path, json={"expected_version": 2, "title": "Novo título fictício"})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "version_conflict"
    assert client.get(path).json() == original
    assert (
        client.patch(
            f"/api/v1/tickets/{uuid4()}",
            json={"expected_version": 1, "title": "Novo título fictício"},
        ).status_code
        == 404
    )


@pytest.mark.parametrize("status,triage", [("resolvido", "revisada"), ("aberto", "em_analise")])
def test_us03_ca2_blocks_state_without_changes(client, migrated_url, status, triage):
    from uuid import UUID

    original = client.post("/api/v1/tickets", json=BODY).json()
    engine = create_engine(migrated_url)
    try:
        with Session(engine) as session, session.begin():
            ticket = session.get(Ticket, UUID(original["id"]))
            ticket.status, ticket.triage_status = status, triage
        path = "/api/v1/tickets/" + original["id"]
        before = client.get(path).json()
        response = client.patch(path, json={"expected_version": 1, "title": "Título corrigido"})
        assert response.status_code == 409
        assert response.json()["error"]["code"] == "invalid_transition"
        assert client.get(path).json() == before
        with Session(engine) as session:
            assert len(session.scalars(select(TicketEvent)).all()) == 1
    finally:
        engine.dispose()


def test_us03_ca2_ca3_invalid_patch_does_not_change_database(client):
    original = client.post("/api/v1/tickets", json=BODY).json()
    path = "/api/v1/tickets/" + original["id"]
    invalids = [
        {"expected_version": 1},
        {"expected_version": 1, "title": None},
        {"expected_version": 1, "description": None},
        {"title": "Título corrigido"},
        {"expected_version": 1, "title": "a" * 4},
        {"expected_version": 1, "title": "a" * 121},
        {"expected_version": 1, "description": "d" * 19},
        {"expected_version": 1, "description": "d" * 5001},
        {"expected_version": 1, "title": "Título", "final_classification": {}},
    ]
    for body in invalids:
        assert client.patch(path, json=body).status_code == 422
        assert client.get(path).json() == original


def test_us03_ca3_noop_keeps_timestamps_and_event_count(client, migrated_url):
    original = client.post("/api/v1/tickets", json=BODY).json()
    path = "/api/v1/tickets/" + original["id"]
    response = client.patch(
        path, json={"expected_version": 1, "title": "  " + BODY["title"] + "  "}
    )
    assert response.status_code == 200 and response.json() == original
    engine = create_engine(migrated_url)
    try:
        with Session(engine) as session:
            assert len(session.scalars(select(TicketEvent)).all()) == 1
    finally:
        engine.dispose()


def test_us03_ca3_http_boundary_values(client):
    original = client.post("/api/v1/tickets", json=BODY).json()
    path = "/api/v1/tickets/" + original["id"]
    for version, title, description in [(1, 5, 20), (2, 120, 5000)]:
        response = client.patch(
            path,
            json={
                "expected_version": version,
                "title": "  " + "á" * title + "  ",
                "description": "\n" + "ç" * description + "\n",
            },
        )
        assert response.status_code == 200
        assert response.json()["version"] == version + 1
        assert len(response.json()["title"]) == title
        assert len(response.json()["description"]) == description
