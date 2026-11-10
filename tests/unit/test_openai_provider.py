import asyncio
import json
import socket
import ssl

import httpx
import pytest
from pydantic import ValidationError

from app.agent.factory import make_provider
from app.agent.openai_provider import OpenAIProvider, verified_tls_context
from app.agent.orchestrator import run_agent
from app.agent.simulated import SimulatedProvider
from app.config import Settings
from tests.openai_helpers import OUTPUT, calls, fake_provider, message, response


@pytest.fixture(autouse=True)
def no_external_network(monkeypatch):
    original = socket.socket.connect

    def blocked(sock, address):
        # asyncio no Windows cria um socketpair em loopback.
        if isinstance(address, tuple) and address[0] in {"127.0.0.1", "::1"}:
            return original(sock, address)
        raise AssertionError("Rede externa proibida neste teste.")

    monkeypatch.setattr(socket.socket, "connect", blocked)


@pytest.mark.parametrize(
    "key,model",
    [(None, None), ("ficticia", None), (None, "modelo-ficticio"), (" ", "x"), ("x", " ")],
)
def test_incomplete_configuration(key, model):
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None, ai_mode="openai", openai_api_key=key, openai_model=model)
    assert "exige OPENAI_API_KEY e OPENAI_MODEL" in str(error.value)
    assert "ficticia" not in str(error.value)


def test_selection_and_secret(monkeypatch):
    monkeypatch.delenv("AI_MODE", raising=False)
    settings = Settings(_env_file=None)
    assert isinstance(make_provider(settings), SimulatedProvider)
    settings = Settings(
        _env_file=None,
        ai_mode="openai",
        openai_api_key="chave-ficticia-sem-validade",
        openai_model="modelo-ficticio",
    )
    assert isinstance(make_provider(settings), OpenAIProvider)
    assert "chave-ficticia-sem-validade" not in repr(settings)


def test_tools_structured_output_and_protocol():
    requests = []

    def handler(request):
        body = json.loads(request.content)
        requests.append(body)
        assert str(request.url) == "https://api.openai.com/v1/responses"
        assert body["model"] == "modelo-ficticio"
        assert body["store"] is False
        assert body["max_output_tokens"] == 2000
        assert body["text"]["format"]["strict"] is True
        assert body["text"]["format"]["schema"]["additionalProperties"] is False
        assert len(body["tools"]) == 2
        assert all(tool["strict"] for tool in body["tools"])
        if len(requests) == 1:
            assert body["input"][1]["role"] == "user"
            return response(calls())
        outputs = [item for item in body["input"] if item.get("type") == "function_call_output"]
        assert {item["call_id"] for item in outputs} == {"call_0", "call_1"}
        assert all(json.loads(item["output"]) for item in outputs)
        assert len([item for item in body["input"] if item.get("type") == "function_call"]) == 2
        return response(message(OUTPUT))

    result = run_agent(fake_provider(handler), "Erro fictício", "Descrição fictícia.")
    assert result.error_code is None
    assert result.output.category == "defeito"
    assert (result.model_calls, result.tool_calls) == (2, 2)


@pytest.mark.parametrize(
    "case,expected",
    [
        ("invalid", "invalid_ai_response"),
        ("timeout", "ai_timeout"),
        ("unavailable", "ai_unavailable"),
        ("refusal", "invalid_ai_response"),
        ("incomplete", "invalid_ai_response"),
        ("forbidden", "tool_protocol_error"),
        ("arguments", "tool_protocol_error"),
        ("tokens", "execution_limit"),
        ("repeat", "execution_limit"),
        ("early", "tool_protocol_error"),
    ],
)
def test_failures_no_retries(case, expected, caplog):
    requests = []

    def handler(request):
        requests.append(request)
        if case == "timeout":
            raise httpx.ReadTimeout("Detalhe privado fictício", request=request)
        if case == "unavailable":
            return httpx.Response(429, json={"error": {"message": "Detalhe privado fictício"}})
        if case == "forbidden":
            items = calls()
            items[0]["name"] = "shell"
            return response(items)
        if case == "arguments":
            items = calls()
            items[0]["arguments"] = '{"extra":true}'
            return response(items)
        if case == "tokens":
            return response(calls(), tokens=2001)
        if case == "repeat" or (len(requests) == 1 and case != "early"):
            return response(calls())
        if case == "refusal":
            items = message(OUTPUT)
            items[0]["content"] = [{"type": "refusal", "refusal": "Recusa fictícia"}]
            return response(items)
        if case == "incomplete":
            return response(message(OUTPUT), status="incomplete")
        return response(
            message({**OUTPUT, "category": "financeiro"} if case == "invalid" else OUTPUT)
        )

    result = run_agent(fake_provider(handler), "Chamado fictício", "Dados fictícios")
    assert result.error_code == expected
    assert len(requests) <= 3
    if case in {"timeout", "unavailable"}:
        assert len(requests) == 1
    assert "chave-ficticia-sem-validade" not in caplog.text
    assert "Detalhe privado fictício" not in caplog.text


def test_total_deadline():
    async def slow(request):
        await asyncio.sleep(1)
        return response(calls())

    result = run_agent(fake_provider(slow), "Fictício", "Fictício", budget=0.05)
    assert result.error_code == "ai_timeout"


def test_tls_uses_system_cas_and_verifies_identity():
    context = verified_tls_context()
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True
    assert context.keylog_filename is None
