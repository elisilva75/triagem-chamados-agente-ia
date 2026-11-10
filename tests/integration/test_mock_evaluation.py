"""Ensaio automatizado com mocks: 24 fixtures, sem inferência ou revisão humana real."""

import json
from decimal import Decimal
from pathlib import Path

import httpx
import pytest
from sqlalchemy import func, select

from app.infrastructure.models import HumanReview, Ticket, TriageAttempt
from tests.agent_helpers import EVALUATION_CASES
from tests.openai_helpers import OUTPUT, calls, fake_provider, message, response

SQL = (Path(__file__).resolve().parents[2] / "scripts/triage_review_agreement.sql").read_text(
    encoding="utf-8"
)


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    async def blocked(*args, **kwargs):
        raise AssertionError("Ensaio exige MockTransport; HTTP externo proibido.")

    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", blocked)
    monkeypatch.setenv("AI_MODE", "simulated")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


def test_24_fixture_evaluation_with_existing_sql(client, request, caplog):
    manifest = []
    http_requests = []
    correction = None

    def agreement():
        with client.app.state.sessions() as session:
            return session.connection().exec_driver_sql(SQL).one()

    def submit_review(path, category, priority):
        current = client.get(path).json()
        reviewed = client.post(
            path + "/reviews",
            json={
                "expected_version": current["version"],
                "category": category,
                "priority": priority,
                "reason": "Decisão fictícia roteirizada no ensaio automatizado com mocks.",
                "declared_reviewer": "Fixture automatizada, sem revisão humana real",
            },
        )
        assert reviewed.status_code == 201, reviewed.text
        return reviewed.json()["review"]["id"]

    for case, (description, category, priority) in enumerate(EVALUATION_CASES, start=1):
        for repetition in range(1, 4):
            expected_error = None
            # Falhas deliberadas nas três repetições AV08; não inferir causa do piloto real.
            if case == 8:
                expected_error = (
                    {"code": "insufficient_quota", "type": "insufficient_quota"},
                    {"code": "rate_limit_exceeded", "type": "requests"},
                    {},
                )[repetition - 1]
            requests_this_attempt = []

            def handler(http_request):
                body = json.loads(http_request.content)
                http_requests.append(body)
                requests_this_attempt.append(body)
                if expected_error is not None:
                    return httpx.Response(
                        429,
                        json={
                            "error": {**expected_error, "message": "Falha fictícia roteirizada."}
                        },
                        headers={"x-request-id": f"req_mock_av{case:02}_{repetition}"},
                    )
                if len(requests_this_attempt) == 1:
                    return response(calls())
                assert len(requests_this_attempt) == 2
                tool_outputs = [
                    item for item in body["input"] if item.get("type") == "function_call_output"
                ]
                assert {item["call_id"] for item in tool_outputs} == {"call_0", "call_1"}
                return response(
                    message(
                        {
                            **OUTPUT,
                            "category": category,
                            "priority": priority,
                            "missing_fields": ["ambiente", "passos_reproducao", "impacto"]
                            if case == 5
                            else [],
                        }
                    )
                )

            client.app.state.provider = fake_provider(handler)
            original = {
                "title": f"Ensaio mock AV{case:02} repetição {repetition}",
                "description": description,
            }
            created = client.post("/api/v1/tickets", json=original)
            assert created.status_code == 201
            ticket_id = created.json()["id"]
            path = "/api/v1/tickets/" + ticket_id
            triaged = client.post(path + "/triage", json={"expected_version": 1})
            assert triaged.status_code == (503 if expected_error is not None else 200)
            ticket = client.get(path).json()
            assert {key: ticket[key] for key in original} == original
            attempts = client.get(path + "/triage-attempts").json()["items"]
            assert len(attempts) == 1
            attempt = attempts[0]
            manifest.append(
                {
                    "case": f"AV{case:02}",
                    "repetition": repetition,
                    "ticket_id": ticket_id,
                    "attempt_id": attempt["id"],
                    "status": attempt["status"],
                }
            )
            if expected_error is not None:
                assert (
                    len(requests_this_attempt) == 1
                )  # Sem retry, mesmo com limite de requisições.
                assert attempt["status"] == "falha" and attempt["error_code"] == "ai_unavailable"
                assert ticket["suggestion"] is None and attempt["suggestion"] is None
                assert attempt["tool_calls"] == 0
                assert client.get(path + "/reviews").json()["total"] == 0
                continue
            assert (attempt["model_calls"], attempt["tool_calls"]) == (2, 2)
            if case == 7 and repetition == 3:
                continue  # Sucesso sem revisão: excluído do denominador.
            reviewed_category, reviewed_priority = category, priority
            if case == 1 and repetition in (2, 3):
                reviewed_category = "outros"  # Divergência só de categoria ou de ambas.
            if case == 1 and repetition in (1, 3):
                reviewed_priority = "baixa"  # Divergência só de prioridade ou de ambas.
            if case == 2 and repetition == 1:
                # Revisão inicialmente divergente, corrigida depois da rodada.
                reviewed_category, reviewed_priority = "outros", "baixa"
                correction = (path, category, priority)
            submit_review(path, reviewed_category, reviewed_priority)

    # 24 tentativas: 3 falhas + 1 sucesso sem revisão excluídos = 20 elegíveis.
    assert tuple(agreement()) == ("openai", 20, 17, Decimal("85.00"), 17, Decimal("85.00"), 16)
    assert correction is not None
    path, category, priority = correction
    old_reviews = client.get(path + "/reviews").json()["items"]
    corrected_id = submit_review(path, category, priority)
    new_reviews = client.get(path + "/reviews").json()["items"]
    assert len(old_reviews) == 1 and len(new_reviews) == 2
    assert old_reviews[0] in new_reviews
    assert corrected_id != old_reviews[0]["id"]
    # Correção substitui o valor anterior no cálculo sem aumentar o denominador.
    assert tuple(agreement()) == ("openai", 20, 18, Decimal("90.00"), 18, Decimal("90.00"), 17)
    with client.app.state.sessions() as session:
        assert session.scalar(select(func.count()).select_from(Ticket)) == 24
        assert session.scalar(select(func.count()).select_from(TriageAttempt)) == 24
        assert session.scalar(select(func.count()).select_from(HumanReview)) == 21
    assert len(http_requests) == 45  # 21 sucessos × 2 + 3 falhas × 1, tudo em memória.
    diagnostics = [
        json.loads(record.getMessage().removeprefix("openai_http_error "))
        for record in caplog.records
        if record.name == "app.agent.openai_provider"
    ]
    assert [entry["error"]["code"] for entry in diagnostics] == [
        "insufficient_quota",
        "rate_limit_exceeded",
        None,
    ]
    assert "chave-ficticia-sem-validade" not in caplog.text
    request.node.user_properties.extend(
        [
            ("evaluation_kind", "ensaio automatizado com mocks"),
            ("fixture_executions", 24),
            ("eligible_attempts", 20),
            ("category_agreements", 18),
            ("priority_agreements", 18),
            ("both_agreements", 17),
            ("mock_http_requests", 45),
            ("mock_fixture_manifest", json.dumps(manifest)),
        ]
    )
