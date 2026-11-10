import json
from pathlib import Path
from uuid import uuid4

import httpx
import pytest

from scripts import us08_groq_pilot as pilot
from scripts.us08_batch import BODY_BYTES, CASES, execute_batch
from tests.openai_helpers import OUTPUT, calls, message, response
from tests.unit.test_openai_provider import no_external_network  # noqa: F401


@pytest.mark.parametrize("failure", ["429", "invalid", "timeout"])
def test_sequential_batch_stops_and_retains_prior_evidence(
    database_url, monkeypatch, request, failure
):
    def forbidden(*args, **kwargs):
        raise AssertionError("Chave e rede externa proibidas no ensaio.")

    monkeypatch.setattr(pilot, "dotenv_values", forbidden)
    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", forbidden)
    counts = {}
    received = []

    def factory(case_id):
        def handler(req):
            received.append((case_id, len(req.content)))
            assert len(req.content) <= BODY_BYTES
            counts[case_id] = counts.get(case_id, 0) + 1
            if case_id == "AV01-R2":
                if failure == "429":
                    return httpx.Response(429, json={"error": {"code": "rate_limit_exceeded"}})
                if failure == "timeout":
                    raise httpx.ReadTimeout("PRIVATE", request=req)
            if counts[case_id] <= 2:
                return response(calls()[counts[case_id] - 1 : counts[case_id]])
            value = {**OUTPUT, "category": "acesso", "priority": "critica"}
            if case_id == "AV01-R2":
                value["category"] = "invalida"
            return response(message(value))

        return httpx.MockTransport(handler)

    folder = Path("reports/us08") / f"batch-guards-{failure}-{uuid4().hex}"
    request.node.user_properties.append(("batch_manifest", str(folder / "manifest.json")))
    result = execute_batch(folder, test_admin_url=database_url, mock_factory=factory)
    saved = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    assert saved == result
    assert list(saved["cases"]) == list(CASES)
    assert saved["cases"]["AV01-R1"]["status"] == "sucesso"
    assert saved["cases"]["AV01-R2"]["status"] == "interrompido"
    assert all(
        row["status"] == "not_executed"
        for key, row in saved["cases"].items()
        if key not in {"AV01-R1", "AV01-R2"}
    )
    assert saved["budget"]["send_attempts"] == (6 if failure == "invalid" else 4)
    assert saved["budget"]["reserved_output_tokens"] == len(received) * 2000
    for case_id in ("AV01-R1", "AV01-R2"):
        evidence = json.loads((folder / f"{case_id}.json").read_text(encoding="utf-8"))
        assert evidence["database_discarded"] is True
        assert "PRIVATE" not in json.dumps(evidence)
        if case_id == "AV01-R1":
            assert evidence["suggestion"]["rationale"] == OUTPUT["rationale"]
            assert evidence["suggestion"]["missing_fields"] == []
        else:
            assert evidence["suggestion"] is None
            assert evidence["persisted_state"]["error_code"] in {
                "invalid_ai_response",
                "ai_timeout",
                "ai_unavailable",
            }
