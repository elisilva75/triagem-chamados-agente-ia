import asyncio
import json
from datetime import date

import httpx
import pytest

from scripts import us08_round_r1 as runner
from scripts.us08_batch import BatchBudget, GuardedTransport
from scripts.us08_round_r1 import REVALIDATION_IDS
from tests.unit.test_openai_provider import no_external_network  # noqa: F401


def request(tokens=2000, *, large=False):
    return httpx.Request(
        "POST",
        "https://api.groq.com/openai/v1/responses",
        content=b"x" * 150564 if large else json.dumps({"max_output_tokens": tokens}).encode(),
    )


def test_nine_attempts_reserve_18000_and_block_tenth():
    assert REVALIDATION_IDS == ("AV01-R1", "AV05-R1", "AV06-R1")
    budget = BatchBudget(
        lambda: None, max_requests=9, output_budget=18000, case_ids=REVALIDATION_IDS
    )
    received = []

    def handler(req):
        received.append(req)
        assert budget.state["reserved_output_tokens"] == len(received) * 2000
        return httpx.Response(200)

    async def run():
        for cid in REVALIDATION_IDS:
            guard = GuardedTransport(budget, cid, lambda: httpx.MockTransport(handler))
            for _ in range(3):
                await guard.handle_async_request(request())
        with pytest.raises(ConnectionError, match="batch_request_limit"):
            await guard.handle_async_request(request())

    asyncio.run(run())
    assert len(received) == 9 and budget.state["reserved_output_tokens"] == 18000


@pytest.mark.parametrize("limit", ["scope", "bytes", "output", "fourth", "budget"])
def test_three_case_guards(limit):
    budget = BatchBudget(
        lambda: None,
        max_requests=9,
        output_budget=2000 if limit == "budget" else 18000,
        case_ids=REVALIDATION_IDS,
    )
    received = []

    def handler(req):
        received.append(req)
        return httpx.Response(200)

    async def run():
        cid = "AV02-R1" if limit == "scope" else "AV01-R1"
        guard = GuardedTransport(budget, cid, lambda: httpx.MockTransport(handler))
        allowed = 3 if limit == "fourth" else int(limit == "budget")
        for _ in range(allowed):
            await guard.handle_async_request(request())
        with pytest.raises(ConnectionError):
            await guard.handle_async_request(
                request(2001 if limit == "output" else 2000, large=limit == "bytes")
            )
        assert len(received) == allowed

    asyncio.run(run())


def test_old_scope_confirmation_cannot_authorize_revalidation(tmp_path, monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("Chave não pode ser lida com confirmação de outro escopo.")

    monkeypatch.setattr(runner, "dotenv_values", forbidden)
    with pytest.raises(ValueError, match="não corresponde"):
        runner.run_round(
            tmp_path / "not-created",
            profile="revalidate-fields-v2",
            confirmation={
                "plan": "Livre",
                "active": True,
                "checked_on": date.today().isoformat(),
                "expires_on": "2099-01-01",
                "scope": "AV01-R1_to_AV08-R1_once",
            },
        )
    assert not (tmp_path / "not-created").exists()
