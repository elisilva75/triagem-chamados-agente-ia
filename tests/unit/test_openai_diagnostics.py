import json
import logging
from decimal import Decimal

import httpx
import pytest

from app.agent.orchestrator import run_agent
from scripts.us08_pilot import MeteredTransport
from tests.openai_helpers import fake_provider

SECRET = "chave-ficticia-sem-validade"
PRIVATE = "Mensagem privada fictícia que nunca deve aparecer no registro."
CASES = [
    (
        {"error": {"code": "insufficient_quota", "type": "insufficient_quota", "message": PRIVATE}},
        "req_quota_test",
        {"code": "insufficient_quota", "type": "insufficient_quota"},
        "req_quota_test",
    ),
    (
        {"error": {"code": "rate_limit_exceeded", "type": "requests", "message": PRIVATE}},
        "req_rate_test",
        {"code": "rate_limit_exceeded", "type": "requests"},
        "req_rate_test",
    ),
    ({"error": {"message": PRIVATE}}, None, {"code": None, "type": None}, None),
    ({"error": {"code": None, "type": None}}, None, {"code": None, "type": None}, None),
    (PRIVATE, "req_invalid_json", {"code": None, "type": None}, "req_invalid_json"),
    (
        {"error": {"code": SECRET, "type": {"text": PRIVATE}}},
        "req_" + SECRET,
        {"code": "[redacted]", "type": "[redacted]"},
        "[redacted]",
    ),
    (
        {"error": {"code": "x" * 1000, "type": "unknown_kind"}},
        "req_" + "a" * 129,
        {"code": "[redacted]", "type": "[redacted]"},
        "[redacted]",
    ),
    (
        {"error": {"code": "rate_limit_exceeded\n" + PRIVATE, "type": "requests"}},
        "req_fake\r\ninjection_private",
        {"code": "[redacted]", "type": "requests"},
        "[redacted]",
    ),
    ([SECRET], None, {"code": None, "type": None}, None),
]


@pytest.fixture(autouse=True)
def block_real_http(monkeypatch):
    async def blocked(*args, **kwargs):
        raise AssertionError("HTTP externo proibido.")

    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", blocked)


@pytest.mark.parametrize("metered", [False, True], ids=["adapter-log", "pilot-ledger"])
@pytest.mark.parametrize("body,request_id,expected_error,expected_id", CASES)
def test_429_diagnostics_offline(body, request_id, expected_error, expected_id, metered, caplog):
    requests = []

    def handler(request):
        requests.append(request)
        headers = {"x-request-id": request_id} if request_id is not None else {}
        if isinstance(body, str):
            return httpx.Response(429, text=body, headers=headers)
        return httpx.Response(429, json=body, headers=headers)

    provider = fake_provider(handler)
    events = []
    if metered:
        provider._transport = MeteredTransport(
            Decimal("0.01"),
            None,
            events.append,
            transport_factory=lambda: httpx.MockTransport(handler),
        )
    caplog.set_level(logging.WARNING, logger="app.agent.openai_provider")
    result = run_agent(provider, "Chamado fictício", "Dados fictícios locais.")
    assert result.error_code == "ai_unavailable"
    assert result.output is None
    assert (result.model_calls, result.tool_calls) == (1, 0)
    assert len(requests) == 1  # Sem retentativa, inclusive para rate_limit_exceeded.
    if metered:
        details = next(event for event in events if event["event"] == "response_received")
        assert details["request_id"] == expected_id  # Campo anterior também sanitizado.
        assert provider._transport.stopped
        assert not any(event["event"] == "usage" for event in events)
    else:
        records = [r for r in caplog.records if r.name == "app.agent.openai_provider"]
        assert len(records) == 1
        details = json.loads(records[0].getMessage().removeprefix("openai_http_error "))
        assert set(details) == {"http_status", "error", "x-request-id"}
    assert details["http_status"] == 429
    assert details["error"] == expected_error
    assert details["x-request-id"] == expected_id
    serialized = caplog.text + json.dumps(events, ensure_ascii=False)
    for forbidden in (SECRET, PRIVATE, "unknown_kind", "x" * 1000, "Authorization"):
        assert forbidden not in serialized
