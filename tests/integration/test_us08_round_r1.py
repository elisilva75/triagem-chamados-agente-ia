import json
from pathlib import Path
from uuid import uuid4

import httpx
import pytest

from scripts import us08_groq_pilot as pilot
from scripts import us08_round_r1 as r1
from tests.openai_helpers import OUTPUT, calls, message, response
from tests.unit.test_openai_provider import no_external_network  # noqa: F401


@pytest.mark.parametrize("failure", ["success", "429", "invalid", "timeout"])
def test_r1_sequential_and_evidence_preserved(database_url, monkeypatch, request, failure):
    def forbidden(*args, **kwargs):
        raise AssertionError("Chave/rede externa proibidas.")

    monkeypatch.setattr(r1, "dotenv_values", forbidden)
    monkeypatch.setattr(pilot, "dotenv_values", forbidden)
    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", forbidden)
    received = []
    counts = {}

    def factory(cid):
        def handler(req):
            received.append(cid)
            counts[cid] = counts.get(cid, 0) + 1
            if cid == "AV02-R1" and failure in {"429", "timeout"}:
                if failure == "timeout":
                    raise httpx.ReadTimeout("private", request=req)
                return httpx.Response(429, json={"error": {"code": "rate_limit_exceeded"}})
            if counts[cid] < 3:
                return response(calls()[counts[cid] - 1 : counts[cid]])
            case = r1.CASES[cid]
            value = {
                **OUTPUT,
                "category": case["accepted_categories"][0],
                "priority": case["expected_priority"],
            }
            if cid == "AV02-R1" and failure == "invalid":
                value["category"] = "invalida"
            return response(message(value))

        return httpx.MockTransport(handler)

    folder = Path("reports/us08") / f"r1-mock-{failure}-{uuid4().hex}"
    request.node.user_properties.append(("r1_mock_manifest", str(folder / "manifest.json")))
    report = r1.run_round(folder, mock_factory=factory, test_admin_url=database_url)
    saved = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    assert saved == report
    assert tuple(saved["cases"]) == r1.ROUND_IDS
    assert saved["full_24_real_enabled"] is False
    assert saved["budget"]["max_requests"] == 24
    assert saved["budget"]["output_budget"] == 48000
    expected = 24 if failure == "success" else 6 if failure == "invalid" else 4
    assert len(received) == saved["budget"]["send_attempts"] == expected
    assert saved["budget"]["reserved_output_tokens"] == expected * 2000
    assert received == sorted(received)
    if failure != "success":
        assert all(
            row["status"] == "not_executed"
            for cid, row in saved["cases"].items()
            if cid not in {"AV01-R1", "AV02-R1"}
        )
    for cid in set(received):
        evidence = json.loads((folder / f"{cid}.json").read_text(encoding="utf-8"))
        assert evidence["database_discarded"] is True
        assert "private" not in json.dumps(evidence)
    first = json.loads((folder / "AV01-R1.json").read_text(encoding="utf-8"))
    assert first["suggestion"]["rationale"] == OUTPUT["rationale"]


def test_r1_records_first_persistent_write_error_after_twelve_requests(
    database_url, monkeypatch, tmp_path
):
    """Injeção explícita: não atribui retrospectivamente causa ao ensaio histórico."""
    counts = {}
    original = pilot.write_json

    def write(path, value):
        if (
            value.get("ticket", {}).get("title") == "AV04 repetição 1"
            and len(value.get("requests", [])) == 3
            and value["requests"][-1].get("status") == 200
        ):
            exc = PermissionError(13, "private")
            exc.winerror = 5
            raise exc
        original(path, value)

    def factory(cid):
        def handler(req):
            counts[cid] = counts.get(cid, 0) + 1
            if counts[cid] < 3:
                return response(calls()[counts[cid] - 1 : counts[cid]])
            return response(message(OUTPUT))

        return httpx.MockTransport(handler)

    monkeypatch.setattr(pilot, "write_json", write)
    monkeypatch.setattr(r1, "dotenv_values", lambda *args: pytest.fail("Sem chave"))
    report = r1.run_round(
        tmp_path / "disk-failure", mock_factory=factory, test_admin_url=database_url
    )
    assert sum(counts.values()) == report["budget"]["send_attempts"] == 12
    assert report["budget"]["stopped"] is True
    assert report["cases"]["AV04-R1"]["execution_error"] == {
        "type": "PermissionError",
        "errno": 13,
        "winerror": 5,
    }
    assert report["cases"]["AV05-R1"]["status"] == "not_executed"
    assert "private" not in json.dumps(report)
