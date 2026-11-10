import json
import re

import httpx
import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine

from scripts import us08_batch as batch
from scripts import us08_groq_pilot as pilot
from scripts import us08_round_r1 as round_r1
from tests.openai_helpers import OUTPUT, calls, message, response
from tests.unit.test_groq_pilot_confirmation import current_confirmation
from tests.unit.test_openai_provider import no_external_network  # noqa: F401


@pytest.mark.parametrize("executor", ["round", "batch"])
def test_cleanup_failure_preserves_success_and_stops_before_next_case(
    database_url, tmp_path, monkeypatch, executor
):
    received = []
    codes = []
    drop_attempts = []
    original_execute = pilot.execute

    def execute(**kwargs):
        code = original_execute(**kwargs)
        codes.append(code)
        return code

    def forbidden(*args, **kwargs):
        pytest.fail("Sem chave ou rede externa.")

    monkeypatch.setattr(pilot, "execute", execute)
    monkeypatch.setattr(pilot, "dotenv_values", forbidden)
    monkeypatch.setattr(round_r1, "dotenv_values", forbidden)

    def factory(case_id):
        def handler(request):
            received.append(case_id)
            if len(received) <= 2:
                return response(calls()[len(received) - 1 : len(received)])
            return response(message(OUTPUT))

        return httpx.MockTransport(handler)

    def reject_drop(conn, cursor, statement, parameters, context, many):
        if statement.startswith('DROP DATABASE "portfolio_test_us08_groq_'):
            drop_attempts.append(statement)
            raise RuntimeError("PRIVATE_CLEANUP_FAILURE")

    folder = tmp_path / executor
    evidence = None
    event.listen(Engine, "before_cursor_execute", reject_drop)
    try:
        if executor == "round":
            result = round_r1.run_round(folder, mock_factory=factory, test_admin_url=database_url)
        else:
            result = batch.execute_batch(folder, mock_factory=factory, test_admin_url=database_url)
        evidence = json.loads((folder / "AV01-R1.json").read_text(encoding="utf-8"))
        assert codes == [2]  # erro operacional distinto de triagem inválida
        assert received == ["AV01-R1"] * 3
        assert len(drop_attempts) == 1  # sem retry de limpeza/triagem
        assert result["budget"]["send_attempts"] == 3
        assert result["budget"]["stopped"] is True
        assert result["budget"]["stop_reason"] == "database_cleanup_error"
        first = result["cases"]["AV01-R1"]
        assert first["status"] == evidence["result"] == "sucesso"
        assert first["operational_status"] == evidence["operational_status"] == "cleanup_error"
        assert (
            first["cleanup_error"]
            == evidence["cleanup_error"]
            == {
                "type": "RuntimeError",
                "errno": None,
                "winerror": None,
            }
        )
        assert all(
            row["status"] == "not_executed"
            for cid, row in result["cases"].items()
            if cid != "AV01-R1"
        )
        assert evidence["database_discarded"] is False
        assert evidence["suggestion"] == OUTPUT
        assert evidence["persisted_state"]["status"] == "sucesso"
        assert evidence["persisted_state"]["no_suggestion"] is False
        assert len(evidence["requests"]) == 3
        assert evidence["usage_totals"]["total_tokens"] > 0
        assert "PRIVATE_CLEANUP_FAILURE" not in json.dumps(evidence)
        assert json.loads((folder / "manifest.json").read_text(encoding="utf-8")) == result
        admin = create_engine(database_url)
        try:
            with admin.connect() as connection:
                assert (
                    connection.execute(
                        text("SELECT 1 FROM pg_database WHERE datname=:name"),
                        {"name": evidence["database"]},
                    ).scalar()
                    == 1
                )
        finally:
            admin.dispose()
    finally:
        event.remove(Engine, "before_cursor_execute", reject_drop)
        # Limpeza apenas do banco gerado neste teste, depois de retirar a injeção.
        # Se uma asserção anterior falhar, ainda buscar evidência para não abandonar recurso.
        path = folder / "AV01-R1.json"
        if evidence is None and path.exists():
            evidence = json.loads(path.read_text(encoding="utf-8"))
        if evidence and (name := evidence.get("database")):
            assert re.fullmatch(r"portfolio_test_us08_groq_[0-9a-f]{32}", name)
            admin = create_engine(database_url, isolation_level="AUTOCOMMIT")
            try:
                with admin.connect() as connection:
                    connection.exec_driver_sql(f'DROP DATABASE "{name}" WITH (FORCE)')
            finally:
                admin.dispose()


def test_standalone_cli_current_confirmation_valid_with_mock_transport(
    database_url, tmp_path, monkeypatch
):
    confirmation = current_confirmation()
    path = tmp_path / "confirmation.json"
    path.write_text(json.dumps(confirmation), encoding="utf-8")
    report_path = tmp_path / "pilot.json"
    monkeypatch.setattr(pilot, "REPORT", report_path)
    received = []
    key_reads = []

    def read_key(filename):
        key_reads.append(filename)
        assert not report_path.exists() or report_path.is_file()
        return {"GROQ_API_KEY": "ficticia-piloto-confirmado"}

    def handler(request):
        received.append(request)
        return response(calls() if len(received) == 1 else message(OUTPUT))

    monkeypatch.setattr(pilot, "dotenv_values", read_key)
    monkeypatch.setattr(httpx, "AsyncHTTPTransport", lambda **kwargs: httpx.MockTransport(handler))
    original_execute = pilot.execute

    def execute(**kwargs):
        assert kwargs["confirmation"] == confirmation
        return original_execute(**kwargs, test_admin_url=database_url)

    monkeypatch.setattr(pilot, "execute", execute)
    assert pilot.main(["--execute-approved", "--confirmation", str(path)]) == 0
    evidence = json.loads(report_path.read_text(encoding="utf-8"))
    assert key_reads == [".env"]
    assert len(received) == 2
    assert evidence["confirmation"] == confirmation
    assert evidence["result"] == "sucesso" and evidence["database_discarded"] is True
    assert evidence["operational_status"] == "ok"
    assert evidence["suggestion"] == OUTPUT
    assert "ficticia-piloto-confirmado" not in json.dumps(evidence)
