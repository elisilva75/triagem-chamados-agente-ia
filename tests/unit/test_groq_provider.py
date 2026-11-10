import json

import httpx
import pytest
from pydantic import SecretStr, ValidationError

from app.agent.factory import make_provider
from app.agent.groq_provider import GroqProvider
from app.agent.orchestrator import run_agent
from app.agent.simulated import SimulatedProvider
from app.config import Settings
from tests.openai_helpers import OUTPUT, calls, message, response
from tests.unit.test_openai_provider import no_external_network  # noqa: F401


@pytest.mark.parametrize(
    "key,model",
    [(None, None), ("fake", None), (None, "fake"), (" ", "x"), ("x", " "), ("x", "x" * 201)],
)
def test_incomplete_configuration(monkeypatch, key, model):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_MODEL", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None, ai_mode="groq", groq_api_key=key, groq_model=model)


def test_explicit_selection(monkeypatch):
    monkeypatch.delenv("AI_MODE", raising=False)
    settings = Settings(_env_file=None, groq_api_key="fake", groq_model="fake")
    assert isinstance(make_provider(settings), SimulatedProvider)
    settings.ai_mode = "groq"
    assert isinstance(make_provider(settings), GroqProvider)
    assert "fake" not in str(settings.groq_api_key)


@pytest.mark.parametrize("sequential", [False, True])
def test_tools_then_structured_output(sequential):
    requests = []

    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        assert str(request.url) == "https://api.groq.com/openai/v1/responses"
        incompatible = {
            "store",
            "previous_response_id",
            "truncation",
            "include",
            "safety_identifier",
            "prompt_cache_key",
            "prompt",
        }
        assert incompatible.isdisjoint(body)
        assert body["model"] == "openai/gpt-oss-20b"
        assert body["max_output_tokens"] == 2000
        if len(requests) == 1:
            assert set(body) == {"model", "input", "max_output_tokens", "tools", "tool_choice"}
            assert "text" not in body
            assert body["tool_choice"] == "required"
            return response(calls()[:1] if sequential else calls())
        if sequential and len(requests) == 2:
            assert set(body) == {"model", "input", "max_output_tokens", "tools", "tool_choice"}
            assert [tool["name"] for tool in body["tools"]] == [calls()[1]["name"]]
            assert "text" not in body
            return response(calls()[1:])
        assert "tools" not in body and "tool_choice" not in body
        assert set(body) == {"model", "input", "max_output_tokens", "text"}
        assert body["text"]["format"]["type"] == "json_schema"
        assert body["text"]["format"]["strict"] is True
        assert body["text"]["format"]["schema"]["additionalProperties"] is False
        outputs = [item for item in body["input"] if item.get("type") == "function_call_output"]
        assert {item["call_id"] for item in outputs} == {"call_0", "call_1"}
        return response(message(OUTPUT))

    provider = GroqProvider(
        SecretStr("chave-ficticia"), "openai/gpt-oss-20b", transport=httpx.MockTransport(handler)
    )
    result = run_agent(provider, "Erro fictício", "Descrição fictícia.")
    assert result.error_code is None
    assert result.output.category == "defeito"
    assert result.tool_calls == 2
    assert result.model_calls == (3 if sequential else 2)


@pytest.mark.parametrize(
    "error", ["insufficient_quota", "rate_limit_exceeded", None, "private\nvalue"]
)
def test_429_no_retry_and_sanitized(caplog, error):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(
            429,
            json={"error": {"code": error, "type": error, "message": "PRIVATE_BODY"}},
            headers={"x-request-id": "req_fake"},
        )

    provider = GroqProvider(
        SecretStr("chave-ficticia"), "modelo-ficticio", transport=httpx.MockTransport(handler)
    )
    result = run_agent(provider, "Erro fictício", "Descrição fictícia.")
    assert result.error_code == "ai_unavailable"
    assert result.output is None
    assert len(requests) == 1
    assert "groq_http_error" in caplog.text
    assert '"http_status": 429' in caplog.text
    assert '"x-request-id": "req_fake"' in caplog.text
    assert "PRIVATE_BODY" not in caplog.text
    assert "chave-ficticia" not in caplog.text
    if error == "private\nvalue":
        assert "[redacted]" in caplog.text
    else:
        assert f'"code": {json.dumps(error)}' in caplog.text
