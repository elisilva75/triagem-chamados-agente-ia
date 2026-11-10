import asyncio
import json
import ssl
from decimal import Decimal

import httpx
import pytest
from pydantic import SecretStr

from app.agent.openai_provider import OpenAIProvider
from app.agent.orchestrator import run_agent
from scripts import us08_pilot as pilot
from tests.openai_helpers import OUTPUT, calls, message, response


@pytest.fixture(autouse=True)
def no_real_transport(monkeypatch):
    async def blocked(*args, **kwargs):
        raise AssertionError("Rede real proibida.")

    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", blocked)


def test_default_does_not_read_key_or_connect(monkeypatch, capsys):
    def forbidden(*args, **kwargs):
        pytest.fail("Preparação não deve ler ambiente ou conectar.")

    monkeypatch.setattr(pilot.os, "environ", {})
    monkeypatch.setattr(pilot, "create_engine", forbidden)
    monkeypatch.setattr(pilot, "execute", forbidden)
    assert pilot.main([]) == 0
    assert "sem chave, banco ou chamada externa" in capsys.readouterr().out
    assert pilot.TRIAGE_RESERVE == Decimal("0.0039375")
    assert 24 * pilot.TRIAGE_RESERVE == Decimal("0.0945000")


def metered(handler, *, budget="0.004", round_budget="0.10"):
    events = []
    transport = pilot.MeteredTransport(
        Decimal(budget),
        Decimal(round_budget),
        events.append,
        transport_factory=lambda: httpx.MockTransport(handler),
    )
    return transport, events


def send(transport):
    async def request():
        async with httpx.AsyncClient(transport=transport) as client:
            return await client.post("https://api.openai.com/v1/responses", json={"fake": True})

    return asyncio.run(request())


def test_registers_api_tokens_without_response_text():
    def handler(request):
        result = response(message(OUTPUT))
        data = json.loads(result.content)
        data["usage"]["input_tokens_details"] = {"cached_tokens": 2}
        data["usage"]["output_tokens_details"] = {"reasoning_tokens": 5}
        return httpx.Response(200, json=data, headers={"x-request-id": "request_fake"})

    transport, events = metered(handler)
    send(transport)
    event = next(e for e in events if e["event"] == "usage")
    assert event["input_tokens"] == 10
    assert event["output_tokens"] == 20
    assert event["reasoning_tokens"] == 5
    assert event["request_id"] == "request_fake"
    assert Decimal(event["cost_nominal_usd"]) == Decimal("0.00001082")
    assert OUTPUT["rationale"] not in json.dumps(events)


def test_meter_with_existing_adapter_and_two_tool_calls():
    count = 0

    def handler(request):
        nonlocal count
        count += 1
        return response(calls() if count == 1 else message(OUTPUT))

    transport, events = metered(handler)
    provider = OpenAIProvider(SecretStr("chave-ficticia"), pilot.MODEL, transport=transport)
    result = run_agent(provider, "Chamado fictício", "Descrição fictícia")
    assert result.error_code is None
    assert (result.model_calls, result.tool_calls) == (2, 2)
    assert len([e for e in events if e["event"] == "usage"]) == 2


@pytest.mark.parametrize("budget,round_budget", [("0.001", "0.10"), ("0.004", "0.01")])
def test_budget_blocks_before_sending(budget, round_budget):
    def handler(request):
        pytest.fail("Orçamento insuficiente deve bloquear antes de enviar.")

    transport, _ = metered(handler, budget=budget, round_budget=round_budget)
    with pytest.raises(ConnectionError):
        send(transport)
    assert transport.requests == 0


@pytest.mark.parametrize("failure", ["http", "usage", "timeout", "input", "incomplete", "tier"])
def test_stops_on_errors_and_blocks_next_request(failure):
    count = 0

    def handler(request):
        nonlocal count
        count += 1
        if failure == "timeout":
            raise httpx.ReadTimeout("Privado fictício", request=request)
        data = json.loads(response(calls()).content)
        if failure == "usage":
            data.pop("usage")
        if failure == "input":
            data["usage"]["input_tokens"] = 1501
            data["usage"]["total_tokens"] = 1521
        if failure == "incomplete":
            data["status"] = "incomplete"
        if failure == "tier":
            data["service_tier"] = "priority"
        return httpx.Response(500 if failure == "http" else 200, json=data)

    transport, events = metered(handler)
    with pytest.raises((ValueError, httpx.ReadTimeout)):
        send(transport)
    with pytest.raises(ConnectionError):
        send(transport)
    assert count == 1
    assert transport.stopped
    assert any(e["event"] == "stopped" for e in events)


def test_budget_recomputed_after_usage():
    transport, _ = metered(lambda request: response(calls()))
    send(transport)
    # Redução da verba restante simula custo acumulado de uma rodada revista.
    transport.round_budget = Decimal("0.001")
    with pytest.raises(ConnectionError):
        send(transport)
    assert transport.requests == 1


def test_pilot_transport_verifies_tls_without_retries(monkeypatch):
    captured = {}

    def factory(**kwargs):
        captured.update(kwargs)
        return httpx.MockTransport(lambda request: response(calls()))

    monkeypatch.setattr(pilot.httpx, "AsyncHTTPTransport", factory)
    meter = pilot.MeteredTransport(Decimal("0.01"), None, lambda event: None)
    send(meter)
    assert captured["verify"].verify_mode == ssl.CERT_REQUIRED
    assert captured["verify"].check_hostname is True
    assert captured["retries"] == 0
    assert captured["trust_env"] is False


def test_pilot_only_does_not_require_round_authorization():
    events = []
    transport = pilot.MeteredTransport(
        Decimal("0.01"),
        None,
        events.append,
        transport_factory=lambda: httpx.MockTransport(lambda request: response(calls())),
    )
    send(transport)
    assert transport.requests == 1
    assert not transport.stopped


def test_cli_accepts_pilot_only(monkeypatch):
    def execute(args):
        assert args.pilot_budget_usd == Decimal("0.01")
        assert args.round_budget_usd is None
        return 0

    monkeypatch.setattr(pilot, "execute", execute)
    assert (
        pilot.main(["--execute-approved", "--model", pilot.MODEL, "--pilot-budget-usd", "0.01"])
        == 0
    )


@pytest.mark.parametrize("value", ["NaN", "-1", "0", "Infinity", "nao-e-numero"])
def test_invalid_budget(value):
    with pytest.raises(pilot.argparse.ArgumentTypeError):
        pilot.money(value)
