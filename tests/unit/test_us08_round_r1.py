import asyncio
import json
from datetime import date

import httpx
import pytest

from scripts import us08_round_r1 as r1
from scripts.us08_batch import BatchBudget, GuardedTransport, execute_batch
from tests.unit.test_openai_provider import no_external_network  # noqa: F401


def body(tokens=2000, content=None):
    return httpx.Request(
        "POST",
        "https://api.groq.com/openai/v1/responses",
        content=content or json.dumps({"max_output_tokens": tokens}).encode(),
    )


def test_scope_eight_blocks_25th_and_reserves_48000_before_send():
    assert r1.ROUND_IDS == tuple(f"AV{i:02}-R1" for i in range(1, 9))
    received = []
    budget = BatchBudget(lambda: None, max_requests=24, output_budget=48000, case_ids=r1.ROUND_IDS)

    def handler(req):
        received.append(req)
        assert budget.state["reserved_output_tokens"] == len(received) * 2000
        assert budget.state["send_attempts"] == len(received)
        return httpx.Response(200)

    async def run():
        for cid in r1.ROUND_IDS:
            guard = GuardedTransport(budget, cid, lambda: httpx.MockTransport(handler))
            for _ in range(3):
                await guard.handle_async_request(body())
        with pytest.raises(ConnectionError, match="batch_request_limit"):
            await guard.handle_async_request(body())

    asyncio.run(run())
    assert len(received) == 24
    assert budget.state["reserved_output_tokens"] == 48000


@pytest.mark.parametrize("limit", ["fourth", "output_budget", "output_request", "bytes", "scope"])
def test_r1_rejects_before_transport(limit):
    budget = BatchBudget(
        lambda: None,
        max_requests=24,
        output_budget=2000 if limit == "output_budget" else 48000,
        case_ids=r1.ROUND_IDS,
    )
    received = []

    def handler(req):
        received.append(req)
        return httpx.Response(200)

    async def run():
        guard = GuardedTransport(budget, "AV01-R1", lambda: httpx.MockTransport(handler))
        permitted = 3 if limit == "fourth" else int(limit == "output_budget")
        for _ in range(permitted):
            await guard.handle_async_request(body())
        denied = body(2001) if limit == "output_request" else body()
        if limit == "bytes":
            denied = body(content=b"x" * 150564)
        if limit == "scope":
            guard = GuardedTransport(budget, "AV01-R2", lambda: httpx.MockTransport(handler))
        with pytest.raises(ConnectionError):
            await guard.handle_async_request(denied)
        assert len(received) == permitted

    asyncio.run(run())


@pytest.mark.parametrize(
    "confirmation",
    [
        None,
        {"plan": "Paid", "active": True},
        {"plan": "Livre", "active": True, "checked_on": "2020-01-01", "expires_on": "2020-01-02"},
    ],
)
def test_preflight_fails_before_key_or_side_effects(tmp_path, monkeypatch, confirmation):
    def forbidden(*args, **kwargs):
        pytest.fail("Não pode ler chave sem pré-condições.")

    monkeypatch.setattr(r1, "dotenv_values", forbidden)
    destination = tmp_path / "not-created"
    with pytest.raises(ValueError):
        r1.run_round(destination, confirmation=confirmation)
    assert not destination.exists()


def test_real_scoped_path_with_fake_key_and_mock_transport(tmp_path, monkeypatch):
    # Exercita a rota de execução explícita, sem chave verdadeira nem banco/rede.
    destination = tmp_path / "offline-realpath-test"
    monkeypatch.setattr(r1, "REAL_DIR", destination)
    monkeypatch.setattr(r1, "dotenv_values", lambda _: {"GROQ_API_KEY": "ficticia-r1-sem-validade"})
    monkeypatch.setattr(
        r1.httpx,
        "AsyncHTTPTransport",
        lambda **kwargs: httpx.MockTransport(lambda req: httpx.Response(429)),
    )
    captured = []

    def fake_execute(**kwargs):
        assert kwargs["approved_key"].get_secret_value() == "ficticia-r1-sem-validade"
        with kwargs["report_path"].open("x") as stream:
            stream.write('{"result":"interrompido"}')

        async def run():
            async with kwargs["mock_factory"]() as transport:
                captured.append((await transport.handle_async_request(body())).status_code)

        asyncio.run(run())
        return 1

    monkeypatch.setattr(r1.pilot, "execute", fake_execute)
    manifest = r1.run_round(
        destination,
        confirmation={
            "plan": "Livre",
            "active": True,
            "checked_on": date.today().isoformat(),
            "expires_on": "2099-01-01",
            "source": "offline_fixture_not_real_execution",
        },
    )
    assert captured == [429]
    assert manifest["budget"]["send_attempts"] == 1
    assert manifest["budget"]["reserved_output_tokens"] == 2000
    assert manifest["cases"]["AV01-R1"]["status"] == "interrompido"
    assert all(
        row["status"] == "not_executed"
        for cid, row in manifest["cases"].items()
        if cid != "AV01-R1"
    )
    with pytest.raises(ValueError):
        execute_batch(tmp_path / "full-24-stays-disabled")
