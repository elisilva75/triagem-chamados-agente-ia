"""Diagnóstico offline de passagem da lista; não reproduz a decisão do modelo real."""

import json
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from pydantic import SecretStr

from app.agent.groq_provider import GroqProvider
from app.agent.orchestrator import run_agent
from app.agent.tools import TOOLS, execute_tool
from app.domain.classification import Suggestion
from scripts.us08_groq_pilot import PilotTransport
from tests.openai_helpers import OUTPUT, calls, message, response
from tests.unit.test_openai_provider import no_external_network  # noqa: F401


@pytest.mark.parametrize(
    "scenario,fields",
    [
        ("empty", []),
        ("subset", ["inicio_ocorrencia"]),
        ("full", ["ambiente", "passos_reproducao", "impacto", "inicio_ocorrencia"]),
        ("absent", None),
    ],
)
def test_model_list_is_not_filled_from_tool_or_schema(scenario, fields, monkeypatch):
    monkeypatch.setenv("AI_MODE", "simulated")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    async def forbidden(*args, **kwargs):
        raise AssertionError("HTTP externo proibido.")

    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", forbidden)
    captured = []
    value = {**OUTPUT, "missing_fields": fields}
    if fields is None:
        value.pop("missing_fields")
    expected = execute_tool(TOOLS[1], {})["expected_fields"]

    def handler(request):
        body = json.loads(request.content)
        captured.append(body)
        if len(captured) == 1:
            return response(calls())
        outputs = [
            json.loads(item["output"])
            for item in body["input"]
            if item.get("type") == "function_call_output"
        ]
        assert any(output.get("expected_fields") == expected for output in outputs)
        schema = body["text"]["format"]["schema"]
        assert "missing_fields" in schema["required"]
        array = schema["properties"]["missing_fields"]
        assert array["maxItems"] == 4
        assert array.get("minItems", 0) == 0
        assert "default" not in array
        return response(message(value))

    report = {"requests": []}
    meter = PilotTransport(report, lambda: None, factory=lambda: httpx.MockTransport(handler))
    provider = GroqProvider(
        SecretStr("credencial-ficticia-diagnostico"), "openai/gpt-oss-20b", transport=meter
    )
    result = run_agent(provider, "Diagnóstico fictício", "Sem bloqueio no ambiente fictício.")
    assert meter.final_suggestion["missing_fields"] == fields
    if fields is None:
        assert result.error_code == "invalid_ai_response"
        assert result.output is None
    else:
        assert result.error_code is None
        assert result.output.missing_fields == fields
        persisted = Suggestion.model_validate(
            {**result.output.model_dump(mode="json"), "mode": "groq", "attempt_id": uuid4()}
        )
        assert persisted.missing_fields == fields
    root = Path("reports/us08/missing-fields-offline-diagnostic")
    root.mkdir(parents=True, exist_ok=True)
    (root / f"{scenario}.json").write_text(
        json.dumps(
            {
                "kind": "diagnostico_com_mocks_nao_reexecucao_real",
                "tool_expected_fields": expected,
                "mock_model_missing_fields": fields,
                "captured_before_sdk_validation": meter.final_suggestion["missing_fields"],
                "validated_missing_fields": result.output.missing_fields if result.output else None,
                "result_error_code": result.error_code,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
