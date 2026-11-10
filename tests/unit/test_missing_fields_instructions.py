import json

import httpx
import pytest
from pydantic import SecretStr

from app.agent.groq_provider import GroqProvider
from app.agent.orchestrator import run_agent
from app.agent.tools import FIELD_CHECK_GUIDANCE, TOOLS
from scripts.us08_groq_pilot import PilotTransport
from tests.agent_helpers import EVALUATION_CASES
from tests.openai_helpers import calls, message, response
from tests.unit.test_openai_provider import no_external_network  # noqa: F401


@pytest.mark.parametrize(
    "index,fields,rationale",
    [
        (
            1,
            ["passos_reproducao"],
            "Ambiente demo, início e impacto coletivo informados; faltam passos.",
        ),
        (
            4,
            [],
            "Dúvida de uso sem incidente: reprodução e início não se aplicam; "
            "sem bloqueio informa impacto.",
        ),
        (
            5,
            ["ambiente", "passos_reproducao", "impacto", "inicio_ocorrencia"],
            "Demonstração é contexto genérico; faltam ambiente, passos, impacto e início.",
        ),
        (
            7,
            ["ambiente", "passos_reproducao", "inicio_ocorrencia"],
            "Impacto coletivo já informado; faltam ambiente, passos e início.",
        ),
    ],
)
def test_actual_payload_explains_applicability_and_preserves_reference_lists(
    index, fields, rationale
):
    description, category, priority = EVALUATION_CASES[index - 1]
    received = []
    decisions = []
    output = {
        "category": category,
        "priority": priority,
        "rationale": rationale,
        "missing_fields": fields,
    }

    def handler(req):
        body = json.loads(req.content)
        received.append(body)
        assert FIELD_CHECK_GUIDANCE in body["input"][0]["content"]
        assert json.loads(body["input"][1]["content"])["ticket_data"]["description"] == description
        if len(received) == 1:
            policy = next(tool for tool in body["tools"] if tool["name"] == TOOLS[1])
            assert FIELD_CHECK_GUIDANCE in policy["description"]
            return response(calls())
        tool_values = [
            json.loads(item["output"])
            for item in body["input"]
            if item.get("type") == "function_call_output"
        ]
        policy = next(value for value in tool_values if "expected_fields" in value)
        assert policy["version"] == "2"
        assert len(policy["expected_fields"]) == 4
        assert policy["expected_fields_guidance"] == FIELD_CHECK_GUIDANCE
        return response(message(output))

    meter = PilotTransport(
        {"requests": []}, lambda: None, factory=lambda: httpx.MockTransport(handler)
    )
    provider = GroqProvider(
        SecretStr("credencial-ficticia-instrucoes"),
        "openai/gpt-oss-20b",
        transport=meter,
        on_tool_decision=decisions.append,
    )
    result = run_agent(provider, f"AV{index:02} exemplo offline", description)
    assert result.error_code is None
    assert result.output.missing_fields == fields
    assert meter.final_suggestion == output
    assert decisions == [{"name": name, "decision": "allow"} for name in TOOLS]


@pytest.mark.parametrize(
    "name,arguments,expected_name",
    [
        ("shell", '{"password":"segredo-ficticio"}', "shell"),
        ("gsk_credencial_ficticia", "{}", "[redacted]"),
        (TOOLS[1], '{"password":"segredo-ficticio"}', TOOLS[1]),
        (TOOLS[1], "argumentos-invalidos-segredo-ficticio", TOOLS[1]),
    ],
)
def test_ordered_decisions_include_blocked_requests_but_no_arguments(
    name, arguments, expected_name
):
    decisions = []

    def handler(req):
        first, second = calls()
        second.update(name=name, arguments=arguments)
        return response([first, second])

    provider = GroqProvider(
        SecretStr("credencial-ficticia-trace"),
        "openai/gpt-oss-20b",
        transport=httpx.MockTransport(handler),
        on_tool_decision=decisions.append,
    )
    result = run_agent(provider, "AV06 offline", EVALUATION_CASES[5][0])
    assert result.error_code == (
        "invalid_ai_response"
        if arguments.startswith("argumentos-invalidos")
        else "tool_protocol_error"
    )
    assert decisions == [
        {"name": TOOLS[0], "decision": "allow"},
        {"name": expected_name, "decision": "block"},
    ]
    serialized = json.dumps(decisions)
    assert "password" not in serialized and "segredo-ficticio" not in serialized
    assert "credencial" not in serialized
    assert all(set(entry) == {"name", "decision"} for entry in decisions)
