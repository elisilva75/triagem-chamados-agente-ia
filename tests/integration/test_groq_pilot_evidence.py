import json
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import create_engine, text

from app.agent.tools import TOOLS
from scripts import us08_groq_pilot as pilot
from tests.openai_helpers import OUTPUT, calls, message, response
from tests.unit.test_openai_provider import no_external_network  # noqa: F401


@pytest.mark.parametrize("outcome", ["success", "invalid", "quota"])
def test_evidence_survives_database_removal(database_url, monkeypatch, request, outcome):
    monkeypatch.setenv("AI_MODE", "simulated")
    monkeypatch.setenv("GROQ_MODEL", "modelo-ficticio")

    def forbidden(*args, **kwargs):
        raise AssertionError("Leitura de chave e HTTP externo proibidos no ensaio.")

    monkeypatch.setattr(pilot, "dotenv_values", forbidden)
    monkeypatch.setattr(httpx.AsyncHTTPTransport, "handle_async_request", forbidden)
    requests = []
    original = {
        **OUTPUT,
        "rationale": "  Justificativa original fictícia, com acentuação.  ",
        "missing_fields": ["ambiente", "impacto"],
    }

    def handler(http_request):
        requests.append(http_request)
        if outcome == "quota":
            return httpx.Response(
                429,
                json={
                    "error": {
                        "code": "insufficient_quota",
                        "message": "PRIVATE_ERROR_BODY",
                    }
                },
            )
        if len(requests) == 1:
            return response(calls())
        value = {**original, "category": "invalida"} if outcome == "invalid" else original
        return response(message(value))

    path = Path("reports/us08") / f"mock-evidence-{outcome}-{uuid4().hex}.json"
    request.node.user_properties.append(("evidence_report", str(path)))
    result = pilot.execute(
        report_path=path,
        mock_factory=lambda: httpx.MockTransport(handler),
        test_admin_url=database_url,
    )
    assert result == (0 if outcome == "success" else 1)
    # Leitura do arquivo em disco após execute já ter descartado o banco.
    saved_text = path.read_text(encoding="utf-8")
    saved = json.loads(saved_text)
    assert saved["evidence_kind"] == "ensaio_automatizado_com_mocks"
    assert saved["database_discarded"] is True
    assert saved["tool_decisions_scope"] == "provider_function_contract_not_execution"
    assert saved["tool_decisions"] == (
        [] if outcome == "quota" else [{"name": name, "decision": "allow"} for name in TOOLS]
    )
    admin = create_engine(database_url)
    try:
        with admin.connect() as connection:
            assert (
                connection.execute(
                    text("SELECT count(*) FROM pg_database WHERE datname=:name"),
                    {"name": saved["database"]},
                ).scalar()
                == 0
            )
    finally:
        admin.dispose()
    assert saved["ticket"]["title"] == "Erro ao salvar cadastro fictício"
    assert "três pessoas" in saved["ticket"]["description"]
    for forbidden_text in (
        "credencial-ficticia-ensaio-sem-validade",
        "authorization",
        "Bearer",
        "PRIVATE_ERROR_BODY",
        "postgresql+psycopg",
    ):
        assert forbidden_text not in saved_text
    if outcome == "success":
        assert saved["suggestion"] == original
        assert saved["classification"] == {"category": "defeito", "priority": "alta"}
        assert saved["result"] == "sucesso"
        assert saved["usage_totals"] == {
            "input_tokens": 20,
            "output_tokens": 40,
            "total_tokens": 60,
        }
        assert saved["human_review_count"] == 0
    else:
        assert saved["suggestion"] is None
        assert "classification" not in saved
        assert saved["persisted_state"]["no_suggestion"] is True
        assert saved["result"] == "interrompido"
        assert len(requests) == (1 if outcome == "quota" else 2)
