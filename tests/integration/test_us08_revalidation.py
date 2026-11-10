import json
from pathlib import Path
from uuid import uuid4

import httpx
import pytest

from scripts import us08_groq_pilot as pilot
from scripts import us08_round_r1 as runner
from tests.openai_helpers import OUTPUT, calls, message, response
from tests.unit.test_openai_provider import no_external_network  # noqa: F401


@pytest.mark.parametrize("outcome", ["success", "429", "invalid", "timeout", "shell"])
def test_revalidation_scope_stops_and_preserves_trace(database_url, monkeypatch, request, outcome):
    def forbidden(*args, **kwargs):
        raise AssertionError("Sem chave real ou HTTP externo no ensaio.")

    monkeypatch.setattr(runner, "dotenv_values", forbidden)
    monkeypatch.setattr(pilot, "dotenv_values", forbidden)
    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", forbidden)
    received = []
    counts = {}

    def factory(cid):
        def handler(req):
            received.append(cid)
            counts[cid] = counts.get(cid, 0) + 1
            if cid == "AV05-R1" and outcome in {"429", "timeout"}:
                if outcome == "timeout":
                    raise httpx.ReadTimeout("private", request=req)
                return httpx.Response(429, json={"error": {"code": "rate_limit_exceeded"}})
            if cid == "AV06-R1" and outcome == "shell":
                item = calls()[0]
                item.update(name="shell", arguments='{"password":"private"}')
                return response([item])
            if counts[cid] < 3:
                return response(calls()[counts[cid] - 1 : counts[cid]])
            case = runner.CASES[cid]
            value = {
                **OUTPUT,
                "category": case["accepted_categories"][0],
                "priority": case["expected_priority"],
            }
            if cid == "AV05-R1" and outcome == "invalid":
                value["category"] = "invalida"
            return response(message(value))

        return httpx.MockTransport(handler)

    folder = Path("reports/us08") / f"revalidation-mock-{outcome}-{uuid4().hex}"
    request.node.user_properties.append(
        ("revalidation_mock_manifest", str(folder / "manifest.json"))
    )
    report = runner.run_round(
        folder, mock_factory=factory, test_admin_url=database_url, profile="revalidate-fields-v2"
    )
    saved = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    assert saved == report
    assert tuple(saved["scope"]) == runner.REVALIDATION_IDS
    assert saved["policy_version"] == "2"
    assert saved["budget"]["max_requests"] == 9
    assert saved["budget"]["output_budget"] == 18000
    expected = {"success": 9, "429": 4, "invalid": 6, "timeout": 4, "shell": 7}[outcome]
    assert len(received) == saved["budget"]["send_attempts"] == expected
    assert saved["budget"]["reserved_output_tokens"] == expected * 2000
    for cid in set(received):
        evidence = json.loads((folder / f"{cid}.json").read_text(encoding="utf-8"))
        assert evidence["database_discarded"] is True
        assert "private" not in json.dumps(evidence)
    if outcome in {"429", "invalid", "timeout"}:
        assert saved["cases"]["AV06-R1"]["status"] == "not_executed"
    elif outcome == "shell":
        av06 = json.loads((folder / "AV06-R1.json").read_text(encoding="utf-8"))
        assert av06["tool_decisions"] == [{"name": "shell", "decision": "block"}]
        assert av06["suggestion"] is None
    first = json.loads((folder / "AV01-R1.json").read_text(encoding="utf-8"))
    assert first["suggestion"]["rationale"] == OUTPUT["rationale"]


@pytest.mark.parametrize("outcome", ["success", "429"])
def test_av08_only_revised(database_url, monkeypatch, tmp_path, outcome):
    monkeypatch.setattr(runner, "dotenv_values", lambda *a: pytest.fail("Sem chave"))
    received = []

    def factory(cid):
        assert cid == "AV08-R1"

        def handler(req):
            received.append(req)
            assert len(req.content) <= 16384
            assert json.loads(req.content)["max_output_tokens"] <= 2000
            if outcome == "429":
                return httpx.Response(429, json={"error": {"code": "rate_limit_exceeded"}})
            if len(received) < 3:
                return response(calls()[len(received) - 1 : len(received)])
            return response(message(OUTPUT))

        return httpx.MockTransport(handler)

    folder = tmp_path / "av08"
    report = runner.run_round(
        folder, profile="av08-revised", mock_factory=factory, test_admin_url=database_url
    )
    assert report["scope"] == ["AV08-R1"]
    assert report["policy_version"] == "2"
    assert report["budget"]["max_requests"] == 3
    assert report["budget"]["output_budget"] == 6000
    assert len(received) == (1 if outcome == "429" else 3)
    saved = json.loads((folder / "AV08-R1.json").read_text(encoding="utf-8"))
    assert saved["database_discarded"] is True
    assert bool(saved["suggestion"]) == (outcome == "success")
    assert report["budget"]["stopped"] == (outcome == "429")
