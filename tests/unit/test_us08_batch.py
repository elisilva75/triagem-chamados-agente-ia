import asyncio
import json
from pathlib import Path

import httpx
import pytest
from pydantic import SecretStr

from app.agent.groq_provider import GroqProvider
from app.agent.orchestrator import run_agent
from scripts.us08_batch import CASES, BatchBudget, GuardedTransport, execute_batch
from tests.openai_helpers import OUTPUT, calls, message, response
from tests.unit.test_openai_provider import no_external_network  # noqa: F401


def request(tokens=2000, *, content=None):
    return httpx.Request(
        "POST",
        "https://api.groq.com/openai/v1/responses",
        content=content or json.dumps({"max_output_tokens": tokens}).encode(),
    )


def test_73rd_send_is_blocked_and_all_reservations_precede_transport():
    received = []
    budget = BatchBudget(lambda: None)

    def handler(req):
        received.append(req)
        assert budget.state["send_attempts"] == len(received)
        assert budget.state["reserved_output_tokens"] == len(received) * 2000
        return httpx.Response(200, json={})

    async def run():
        for case_id in CASES:
            guard = GuardedTransport(budget, case_id, lambda: httpx.MockTransport(handler))
            for _ in range(3):
                await guard.handle_async_request(request())
        with pytest.raises(ConnectionError, match="batch_request_limit"):
            await guard.handle_async_request(request())

    asyncio.run(run())
    assert len(received) == 72
    assert budget.state["reserved_output_tokens"] == 144000


@pytest.mark.parametrize("reason", ["output_budget", "case_request_limit", "output_request_limit"])
def test_limits_reject_before_sending(reason):
    received = []
    budget = BatchBudget(lambda: None, output_budget=2000 if reason == "output_budget" else 144000)

    def handler(req):
        received.append(req)
        return httpx.Response(200)

    async def run():
        guard = GuardedTransport(budget, "AV01-R1", lambda: httpx.MockTransport(handler))
        permitted = {"output_budget": 1, "case_request_limit": 3, "output_request_limit": 0}[reason]
        for _ in range(permitted):
            await guard.handle_async_request(request())
        with pytest.raises(ConnectionError, match=reason):
            await guard.handle_async_request(
                request(2001 if reason == "output_request_limit" else 2000)
            )
        assert len(received) == permitted
        assert budget.state["reserved_output_tokens"] == permitted * 2000

    asyncio.run(run())


@pytest.mark.parametrize("failure", ["timeout", "429"])
def test_failed_sends_consume_attempt_and_reservation_without_retry(failure):
    received = []
    budget = BatchBudget(lambda: None)

    def handler(req):
        received.append(req)
        if failure == "timeout":
            raise httpx.ReadTimeout("private", request=req)
        return httpx.Response(429)

    async def run():
        guard = GuardedTransport(budget, "AV01-R1", lambda: httpx.MockTransport(handler))
        if failure == "timeout":
            with pytest.raises(httpx.ReadTimeout):
                await guard.handle_async_request(request())
        else:
            assert (await guard.handle_async_request(request())).status_code == 429
        with pytest.raises(ConnectionError, match="batch_stopped"):
            await guard.handle_async_request(request())

    asyncio.run(run())
    assert len(received) == budget.state["send_attempts"] == 1
    assert budget.state["reserved_output_tokens"] == 2000


def test_serialized_150564_byte_body_is_blocked_before_transport():
    budget = BatchBudget(lambda: None)

    def handler(req):
        pytest.fail("Corpo grande não pode chegar ao transporte.")

    content = json.dumps({"max_output_tokens": 2000, "input": "x" * 150000}).encode()
    content += b" " * (150564 - len(content))

    async def run():
        guard = GuardedTransport(budget, "AV01-R1", lambda: httpx.MockTransport(handler))
        with pytest.raises(ConnectionError, match="body_byte_limit"):
            await guard.handle_async_request(request(content=content))

    asyncio.run(run())
    assert budget.state["send_attempts"] == budget.state["reserved_output_tokens"] == 0


def test_real_execution_disabled_before_any_side_effect(tmp_path):
    destination = tmp_path / "must-not-exist"
    with pytest.raises(ValueError, match="real desabilitada"):
        execute_batch(destination)
    assert not destination.exists()


def test_all_24_ids_fit_byte_guard_with_complete_sdk_payloads():
    budget = BatchBudget(lambda: None)
    counts = {}

    for case_id, case in CASES.items():

        def handler(req):
            counts[case_id] = counts.get(case_id, 0) + 1
            body = json.loads(req.content)
            if counts[case_id] < 3:
                assert "tools" in body
                return response(calls()[counts[case_id] - 1 : counts[case_id]])
            assert body["text"]["format"]["type"] == "json_schema"
            assert (
                len([item for item in body["input"] if item.get("type") == "function_call_output"])
                == 2
            )
            return response(
                message(
                    {
                        **OUTPUT,
                        "category": case["accepted_categories"][0],
                        "priority": case["expected_priority"],
                    }
                )
            )

        guard = GuardedTransport(budget, case_id, lambda: httpx.MockTransport(handler))
        provider = GroqProvider(
            SecretStr("credencial-ficticia-guards"), "openai/gpt-oss-20b", transport=guard
        )
        result = run_agent(provider, case["title"], case["description"])
        assert result.error_code is None
    assert list(counts) == list(CASES)
    assert budget.state["send_attempts"] == 72
    assert budget.state["reserved_output_tokens"] == 144000
    path = Path("reports/us08/batch-guards-wire-measurements.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"kind": "ensaio_com_mocks", **budget.state}, indent=2), encoding="utf-8"
    )
