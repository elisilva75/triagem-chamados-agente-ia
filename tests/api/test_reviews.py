from uuid import UUID, uuid4

import pytest
from sqlalchemy import select

from app.agent.simulated import SimulatedProvider
from app.infrastructure.models import HumanReview, TicketEvent
from tests.agent_helpers import ScriptProvider
from tests.api.test_triage import create
from tests.review_helpers import REVIEW, suggested

pytestmark = pytest.mark.postgres


def test_us06_ca1_ca3_review_correct_resolve_reopen_and_preserve_history(client):
    path, initial = suggested(client)
    attempts = client.get(path + "/triage-attempts").json()

    class Forbidden:
        def respond(self, *args, **kwargs):
            raise AssertionError("Revisão/transição não pode chamar provedor")

    client.app.state.provider = Forbidden()
    first = client.post(path + "/reviews", json={"expected_version": 3, **REVIEW})
    assert first.status_code == 201, first.text
    assert client.get(first.headers["location"]).json() == first.json()["review"]
    ticket, review = first.json()["ticket"], first.json()["review"]
    assert ticket["version"] == 4 and ticket["content_revision"] == 1
    assert ticket["status"] == "aberto" and ticket["triage_status"] == "revisada"
    assert ticket["suggestion"] == initial["suggestion"]
    assert ticket["final_classification"] == {
        "review_id": review["id"],
        "category": "defeito",
        "priority": "alta",
    }
    assert review["attempt_id"] == initial["suggestion"]["attempt_id"]
    assert (
        review["reason"] == REVIEW["reason"]
        and review["declared_reviewer"] == REVIEW["declared_reviewer"]
    )
    assert review["created_at"].endswith("Z")
    corrected = client.post(
        path + "/reviews",
        json={
            "expected_version": 4,
            **REVIEW,
            "category": "infraestrutura",
            "priority": "media",
            "reason": "Corrigi a decisão após verificar os dados fictícios.",
        },
    )
    assert corrected.status_code == 201
    current = corrected.json()["ticket"]
    assert current["version"] == 5 and current["content_revision"] == 1
    assert current["final_classification"]["review_id"] != review["id"]
    assert current["final_classification"]["category"] == "infraestrutura"
    assert current["suggestion"] == initial["suggestion"]
    history = client.get(path + "/reviews").json()
    assert history["total"] == 2 and history["items"][0] == review
    assert client.get(path + "/reviews?limit=1&offset=1").json()["items"] == [
        corrected.json()["review"]
    ]
    assert client.get(path + "/reviews?offset=2").json()["items"] == []
    resolved = client.post(path + "/resolve", json={"expected_version": 5})
    assert resolved.status_code == 200, resolved.text
    closed = resolved.json()
    assert closed["version"] == 6 and closed["status"] == "resolvido"
    assert closed["final_classification"] == current["final_classification"]
    assert closed["created_at"] == initial["created_at"] and closed["content_revision"] == 1
    assert client.get(path).json() == closed
    # Inclui o bloqueio de no-op em resolvido, pendência integrada de US03.
    rejected = [
        ("/resolve", {"expected_version": 6}),
        ("/resolve", {"expected_version": 5}),
        ("/reviews", {"expected_version": 6, **REVIEW}),
        ("/triage", {"expected_version": 6}),
    ]
    for suffix, body in rejected:
        assert client.post(path + suffix, json=body).status_code == 409
    for title in (closed["title"], "Título corrigido mas bloqueado"):
        assert client.patch(path, json={"expected_version": 6, "title": title}).status_code == 409
    assert client.post(path + "/reopen", json={"expected_version": 5}).status_code == 409
    assert client.get(path).json() == closed
    assert client.get(path + "/reviews").json() == history
    reopened = client.post(path + "/reopen", json={"expected_version": 6})
    assert reopened.status_code == 200
    opened = reopened.json()
    assert opened["version"] == 7 and opened["status"] == "aberto"
    assert opened["triage_status"] == "revisada"
    assert opened["final_classification"] == closed["final_classification"]
    assert opened["suggestion"] == closed["suggestion"]
    assert client.post(path + "/reopen", json={"expected_version": 7}).status_code == 409
    assert client.get(path).json() == opened
    assert client.get(path + "/triage-attempts").json() == attempts
    with client.app.state.sessions() as session:
        events = session.scalars(
            select(TicketEvent).order_by(TicketEvent.created_at, TicketEvent.id)
        ).all()
        assert [e.type for e in events] == ["criado", "resolvido", "reaberto"]
        assert all(e.content_revision == 1 for e in events)
    subsequent = client.post(path + "/reviews", json={"expected_version": 7, **REVIEW})
    assert subsequent.status_code == 201
    assert subsequent.json()["ticket"]["version"] == 8
    assert client.get(first.headers["location"]).json() == review


def test_us06_ca2_pending_failure_suggested_cannot_resolve_without_review(client):
    path, _ = create(client)

    def blocked(version):
        before = client.get(path).json()
        history = client.get(path + "/reviews").json()
        for action in ("reviews", "resolve", "reopen"):
            body = {"expected_version": version, **(REVIEW if action == "reviews" else {})}
            assert client.post(path + "/" + action, json=body).status_code == 409
        assert client.get(path).json() == before
        assert client.get(path + "/reviews").json() == history

    blocked(1)
    client.app.state.provider = ScriptProvider([TimeoutError()])
    assert client.post(path + "/triage", json={"expected_version": 1}).status_code == 504
    blocked(3)
    client.app.state.provider = SimulatedProvider()
    assert client.post(path + "/triage", json={"expected_version": 3}).status_code == 200
    before = client.get(path).json()
    assert client.post(path + "/resolve", json={"expected_version": 5}).status_code == 409
    assert client.post(path + "/reopen", json={"expected_version": 5}).status_code == 409
    assert client.get(path).json() == before


def test_us06_ca2_ca3_invalid_review_leaves_all_data_unchanged(client):
    path, before = suggested(client)
    attempts = client.get(path + "/triage-attempts").json()
    for patch in [
        {"category": "financeiro"},
        {"priority": "urgente"},
        {"reason": "a" * 9},
        {"reason": "a" * 501},
        {"declared_reviewer": "a"},
        {"declared_reviewer": "a" * 81},
        {"expected_version": True},
        {"attempt_id": str(uuid4())},
    ]:
        response = client.post(path + "/reviews", json={"expected_version": 3, **REVIEW, **patch})
        assert response.status_code == 422
        assert response.json()["error"]["code"] == "validation_error"
        assert client.get(path).json() == before
        assert client.get(path + "/reviews").json()["total"] == 0
    assert client.get(path + "/triage-attempts").json() == attempts
    with client.app.state.sessions() as session:
        assert len(session.scalars(select(TicketEvent)).all()) == 1


@pytest.mark.parametrize("reason,author", [(10, 2), (500, 80)])
def test_us06_ca3_http_boundaries(client, reason, author):
    path, _ = suggested(client)
    response = client.post(
        path + "/reviews",
        json={
            "expected_version": 3,
            **REVIEW,
            "reason": "  " + "á" * reason + "\n",
            "declared_reviewer": "  " + "ç" * author + "  ",
        },
    )
    assert response.status_code == 201, response.text
    review = response.json()["review"]
    assert len(review["reason"]) == reason and len(review["declared_reviewer"]) == author
    assert client.get(response.headers["location"]).json() == review


def test_us06_ca4_version_guards_and_scoped_review_reads(client):
    path, _ = suggested(client)
    response = client.post(path + "/reviews", json={"expected_version": 3, **REVIEW})
    assert response.status_code == 201
    before = client.get(path).json()
    for action in ("reviews", "resolve", "reopen"):
        body = {"expected_version": 3, **(REVIEW if action == "reviews" else {})}
        result = client.post(path + "/" + action, json=body)
        assert result.status_code == 409 and result.json()["error"]["code"] == "version_conflict"
        absent = client.post(f"/api/v1/tickets/{uuid4()}/" + action, json=body)
        assert absent.status_code == 404
    assert client.get(path).json() == before
    assert client.get(path + "/reviews").json()["total"] == 1
    other, _ = create(client)
    review_id = response.json()["review"]["id"]
    assert client.get(other + "/reviews/" + review_id).status_code == 404
    assert client.get(f"/api/v1/tickets/{uuid4()}/reviews").status_code == 404
    for query in ("limit=0", "limit=101", "offset=-1"):
        assert client.get(path + "/reviews?" + query).status_code == 422
    with client.app.state.sessions() as session:
        reviews = session.scalars(
            select(HumanReview).where(HumanReview.ticket_id == UUID(before["id"]))
        ).all()
        assert len(reviews) == 1
