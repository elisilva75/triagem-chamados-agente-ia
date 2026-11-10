"""Piloto Groq único: execução explícita, projeto gratuito confirmado externamente."""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4

import httpx
from dotenv import dotenv_values
from pydantic import SecretStr
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.agent.diagnostics import sanitized_429
from app.agent.groq_provider import GroqProvider
from app.agent.openai_provider import verified_tls_context
from app.application.tickets import register_ticket
from app.application.triage import triage_ticket
from app.infrastructure.database import make_sessions
from scripts.us08_confirmation import SINGLE_PILOT_SCOPE, validate_confirmation

MODEL = "openai/gpt-oss-20b"
REPORT = Path("reports/us08/groq-authorized-single-pilot.json")


def write_json(path, value):
    """Fecha o temporário antes do replace; tolera só bloqueio transitório Windows."""
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    for attempt in range(5):
        try:
            temp.replace(path)
            return
        except PermissionError as exc:
            if getattr(exc, "winerror", None) not in {5, 32, 33} or attempt == 4:
                raise
            # Apenas a operação atômica local; não repete triagem/HTTP nem libera saldo.
            time.sleep(0.01 * 2**attempt)


def error_metadata(exc):
    return {
        "type": type(exc).__name__,
        "errno": exc.errno if isinstance(exc, OSError) else None,
        "winerror": getattr(exc, "winerror", None) if isinstance(exc, OSError) else None,
    }


class PilotTransport(httpx.AsyncBaseTransport):
    def __init__(self, report, save, *, factory=None):
        self.report = report
        self.save = save
        self.factory = factory or (
            lambda: httpx.AsyncHTTPTransport(
                verify=verified_tls_context(), retries=0, trust_env=False
            )
        )
        self.stopped = False
        self.final_suggestion = None

    async def handle_async_request(self, request):
        if self.stopped or len(self.report["requests"]) >= 3:
            raise ConnectionError
        if str(request.url) != "https://api.groq.com/openai/v1/responses":
            self.stopped = True
            raise ConnectionError
        event = {
            "number": len(self.report["requests"]) + 1,
            "status": None,
            "code": None,
            "request_id": None,
        }
        self.report["requests"].append(event)
        self.save()
        try:
            async with self.factory() as transport:
                response = await transport.handle_async_request(request)
                await response.aread()
            secret = request.headers.get("authorization", "").removeprefix("Bearer ")
            metadata = sanitized_429(response, secret=secret)
            event["status"] = response.status_code
            event["request_id"] = metadata["x-request-id"]
            # Apenas cabeçalhos numéricos de limite; nunca corpo de erro ou autenticação.
            event["rate_limits"] = {
                name: int(value)
                for name in (
                    "x-ratelimit-limit-requests",
                    "x-ratelimit-limit-tokens",
                    "x-ratelimit-remaining-requests",
                    "x-ratelimit-remaining-tokens",
                )
                if (value := response.headers.get(name, "")).isascii()
                and value.isdecimal()
                and len(value) <= 12
            }
            if response.is_error:
                # Nunca persiste mensagem, corpo, tipo ou cabeçalho de autorização.
                event["code"] = metadata["error"]["code"]
                self.stopped = True
                self.save()
                return response
            data = response.json()
            usage = data.get("usage") or {}
            values = {
                key: usage.get(key) for key in ("input_tokens", "output_tokens", "total_tokens")
            }
            if any(type(n) is not int or n < 0 for n in values.values()):
                raise ValueError
            if values["total_tokens"] != values["input_tokens"] + values["output_tokens"]:
                raise ValueError
            event["usage"] = values
            # Preserve os valores originais do JSON, antes da normalização do domínio.
            output = data.get("output") or []
            if not any(item.get("type") == "function_call" for item in output):
                texts = [
                    content["text"]
                    for item in output
                    if item.get("type") == "message"
                    for content in item.get("content", [])
                    if content.get("type") == "output_text"
                ]
                if len(texts) == 1:
                    candidate = json.loads(texts[0])
                    if isinstance(candidate, dict):
                        self.final_suggestion = {
                            key: candidate.get(key)
                            for key in ("category", "priority", "rationale", "missing_fields")
                        }
            self.save()
            return response
        except BaseException:
            self.stopped = True
            self.save()
            raise


def execute(
    *,
    report_path=None,
    mock_factory=None,
    test_admin_url=None,
    ticket_data=None,
    approved_key=None,
    confirmation=None,
):
    report_path = report_path or REPORT
    mocked = mock_factory is not None and approved_key is None
    # Chaves fornecidas pela rodada já passaram pelo preflight daquele escopo.
    # O piloto avulso valida aqui antes de arquivo, chave, banco ou transporte.
    checked_confirmation = None
    if not mocked and approved_key is None:
        checked_confirmation = validate_confirmation(
            confirmation, expected_scope=SINGLE_PILOT_SCOPE
        )
    if mocked and test_admin_url is None:
        raise ValueError("Ensaio exige banco administrativo de teste explícito.")
    if test_admin_url is not None:
        test_url = make_url(test_admin_url)
        if (
            test_url.drivername != "postgresql+psycopg"
            or test_url.host not in {"127.0.0.1", "localhost"}
            or not (test_url.database or "").startswith("portfolio_test")
        ):
            raise ValueError("Banco de ensaio deve ser PostgreSQL local portfolio_test*.")
    # Relatório exclusivo impede repetir esta autorização ao executar o comando novamente.
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("x", encoding="utf-8"):
        pass
    report = {
        "provider": "groq",
        "model": MODEL,
        "authorized_triages": 1,
        "max_requests": 3,
        "billing_basis": "not_applicable_mock" if mocked else "user_confirmed_free_default_project",
        "dashboard_cost_usd": None,
        "cost_status": "nao_confirmado",
        "requests": [],
        "result": "not_started",
        "operational_status": "ok",
        "confirmation": checked_confirmation,
        "human_review": "nao_realizada",
        "evidence_kind": "ensaio_automatizado_com_mocks" if mocked else "piloto_real",
        "suggestion": None,
        "tool_decisions": [],
        "tool_decisions_scope": "provider_function_contract_not_execution",
    }

    def save():
        write_json(report_path, report)

    save()
    admin = None
    engine = None
    created = False
    name = "portfolio_test_us08_groq_" + uuid4().hex
    # Somente configuração do processo filho; .env não é modificado.
    os.environ["AI_MODE"] = "simulated" if mocked else "groq"
    os.environ["GROQ_MODEL"] = MODEL
    previous_logging = logging.root.manager.disable
    logging.disable(logging.CRITICAL)
    try:
        key = (
            approved_key.get_secret_value()
            if approved_key is not None
            else (
                "credencial-ficticia-ensaio-sem-validade"
                if mocked
                else (dotenv_values(".env").get("GROQ_API_KEY") or "")
            )
        )
        if not key.strip():
            raise ValueError
        admin_url = test_admin_url or (
            "postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test"
        )
        admin = create_engine(admin_url, isolation_level="AUTOCOMMIT", hide_parameters=True)
        with admin.connect() as connection:
            connection.exec_driver_sql(f'CREATE DATABASE "{name}"')
        created = True
        report["database"] = name
        save()
        url = admin.url.set(database=name).render_as_string(hide_password=False)
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            env={**os.environ, "AI_MODE": "simulated", "APP_ENV": "test", "DATABASE_URL": url},
            check=True,
            capture_output=True,
        )
        engine = create_engine(url, hide_parameters=True)
        sessions = make_sessions(engine)
        if ticket_data is None:
            ticket_data = {
                "title": "Erro ao salvar cadastro fictício",
                "description": "No ambiente fictício de demonstração, "
                "três pessoas não conseguem salvar "
                "o cadastro desde 08h, sem alternativa. Preencher o formulário e clicar "
                "em Salvar retorna erro e bloqueia o trabalho.",
            }
        with sessions() as session:
            ticket = register_ticket(
                session,
                ticket_data["title"],
                ticket_data["description"],
            )
            ticket_id = ticket.id
        report["ticket_id"] = str(ticket_id)
        report["ticket"] = {"title": ticket.title, "description": ticket.description}
        save()
        meter = PilotTransport(report, save, factory=mock_factory)

        def record_tool_decision(event):
            report["tool_decisions"].append(event)
            save()

        provider = GroqProvider(
            SecretStr(key), MODEL, transport=meter, on_tool_decision=record_tool_decision
        )
        # Exatamente uma chamada da aplicação, sem laço de retry.
        result = triage_ticket(sessions, ticket_id, 1, provider)
        report["result"] = "sucesso"
        report["suggestion"] = meter.final_suggestion
        report["attempt_id"] = str(result["attempt"].id)
        report["classification"] = {
            k: result["attempt"].suggestion[k] for k in ("category", "priority")
        }
        report["tool_calls"] = result["attempt"].tool_calls
        report["usage_totals"] = {
            key: sum(event["usage"][key] for event in report["requests"])
            for key in ("input_tokens", "output_tokens", "total_tokens")
        }
    except (Exception, KeyboardInterrupt) as exc:
        report.setdefault("execution_error", error_metadata(exc))
        report["result"] = "interrompido"
        report["operational_status"] = "execution_error"
    finally:
        if engine is not None:
            try:
                with engine.connect() as connection:
                    report["persisted_state"] = dict(
                        connection.execute(
                            text(
                                "SELECT id::text AS attempt_id, status, error_code, "
                                "model_calls, tool_calls, "
                                "suggestion IS NULL AS no_suggestion "
                                "FROM triage_attempts ORDER BY started_at DESC LIMIT 1"
                            )
                        )
                        .mappings()
                        .one()
                    )
                    report["human_review_count"] = connection.exec_driver_sql(
                        "SELECT count(*) FROM human_reviews"
                    ).scalar()
            except Exception:
                pass
            engine.dispose()
        if created:
            try:
                # Nome gerado acima: nunca aponta para demo nem banco administrativo.
                assert name.startswith("portfolio_test_us08_groq_")
                with admin.connect() as connection:
                    connection.exec_driver_sql(f'DROP DATABASE "{name}" WITH (FORCE)')
                report["database_discarded"] = True
            except Exception as exc:
                report["database_discarded"] = False
                report["cleanup_error"] = error_metadata(exc)
                report["operational_status"] = "cleanup_error"
        if admin is not None:
            admin.dispose()
        os.environ["AI_MODE"] = "simulated"
        logging.disable(previous_logging)
        save()
    if approved_key is None:
        print(json.dumps(report, ensure_ascii=True))
    if report["operational_status"] == "cleanup_error":
        return 2
    return 0 if report["result"] == "sucesso" else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-approved", action="store_true")
    parser.add_argument("--confirmation", type=Path)
    args = parser.parse_args(argv)
    if not args.execute_approved:
        print(
            "Preparação: sem chave, banco ou rede. Execução exige autorização e plano confirmado."
        )
        return 0
    if args.confirmation is None:
        parser.error("--execute-approved exige --confirmation atual para o piloto avulso.")
    try:
        confirmation = json.loads(args.confirmation.read_text(encoding="utf-8"))
        confirmation = validate_confirmation(confirmation, expected_scope=SINGLE_PILOT_SCOPE)
    except (OSError, ValueError):
        parser.error("Confirmação ausente, inválida, vencida ou fora do escopo do piloto avulso.")
    if REPORT.exists():
        print("Autorização já registrada; não repetir.")
        return 1
    return execute(confirmation=confirmation)


if __name__ == "__main__":
    raise SystemExit(main())
