"""Inspeção offline do envelope completo; bytes não são tokens da Groq."""

import json
from pathlib import Path

import httpx
import pytest
from pydantic import SecretStr

from app.agent.groq_provider import GroqProvider
from app.agent.orchestrator import run_agent
from tests.agent_helpers import EVALUATION_CASES
from tests.openai_helpers import OUTPUT, calls, message, response
from tests.unit.test_openai_provider import no_external_network  # noqa: F401


def test_full_payload_input_accounting_and_current_gap(monkeypatch):
    monkeypatch.setenv("AI_MODE", "simulated")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    async def forbidden(*args, **kwargs):
        raise AssertionError("HTTP externo proibido; somente mocks.")

    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", forbidden)
    manifest = []
    for index, (description, category, priority) in enumerate(EVALUATION_CASES, 1):
        captured = []

        def handler(request):
            body = json.loads(request.content)
            captured.append(body)
            assert body["max_output_tokens"] == 2000
            assert (
                not {"max_input_tokens", "truncation", "store", "previous_response_id"}
                & body.keys()
            )
            assert body["input"][0]["role"] == "system"
            assert (
                json.loads(body["input"][1]["content"])["ticket_data"]["description"] == description
            )
            if len(captured) <= 2:
                assert "tools" in body and "text" not in body
                return response(calls()[len(captured) - 1 : len(captured)])
            outputs = [item for item in body["input"] if item.get("type") == "function_call_output"]
            assert len(outputs) == 2
            assert all(json.loads(item["output"]) for item in outputs)
            assert "tools" not in body
            assert body["text"]["format"]["type"] == "json_schema"
            assert body["text"]["format"]["schema"]["required"]
            return response(message({**OUTPUT, "category": category, "priority": priority}))

        provider = GroqProvider(
            SecretStr("credencial-ficticia-plan-review"),
            "openai/gpt-oss-20b",
            transport=httpx.MockTransport(handler),
        )
        result = run_agent(provider, f"AV{index:02} repetição de ensaio", description)
        assert result.error_code is None
        assert (result.model_calls, result.tool_calls) == (3, 2)
        manifest.append(
            {
                "case": f"AV{index:02}",
                "mock_requests": 3,
                "request_json_utf8_bytes": [
                    len(json.dumps(body, ensure_ascii=False).encode("utf-8")) for body in captured
                ],
                "output_token_limit_per_request": 2000,
                "verified_input_token_limit": None,
            }
        )

    # Contraprova: o adaptador aceita uma entrada muito maior sem guarda prévia.
    # É teste direto da interface do adaptador, não mudança das fixtures do lote.
    oversized = "dado fictício " * 10_000
    reached = []

    def large_handler(request):
        reached.append(len(request.content))
        assert json.loads(request.content)["max_output_tokens"] == 2000
        return response(calls())

    provider = GroqProvider(
        SecretStr("credencial-ficticia-plan-review"),
        "openai/gpt-oss-20b",
        transport=httpx.MockTransport(large_handler),
    )
    provider.respond(
        [{"role": "system", "content": oversized}],
        tuple(call["name"] for call in calls()),
        remaining_seconds=20,
        max_output_tokens=9999,
    )
    assert len(reached) == 1 and reached[0] > 100_000
    report = {
        "kind": "ensaio_offline_payloads_nao_avaliacao_semantica",
        "cases": manifest,
        "mock_requests": 25,
        "oversized_request_reached_mock_bytes": reached[0],
        "input_token_limit": None,
        "batch_request_limit": "72 planejado, nao implementado",
        "planned_batch_max_output_tokens": 144000,
    }
    path = Path("reports/us08/plan-payloads-offline.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


@pytest.mark.parametrize("code", ["insufficient_quota", "rate_limit_exceeded", None])
def test_429_stops_before_next_stage(code):
    received = []

    def handler(request):
        received.append(request)
        return httpx.Response(429, json={"error": {"code": code}})

    provider = GroqProvider(
        SecretStr("credencial-ficticia-plan-review"),
        "openai/gpt-oss-20b",
        transport=httpx.MockTransport(handler),
    )
    result = run_agent(provider, "AV06", EVALUATION_CASES[5][0])
    assert result.error_code == "ai_unavailable" and result.output is None
    assert len(received) == 1
