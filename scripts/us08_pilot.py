"""Preparação sem rede por padrão. Execução paga exige aprovação externa e flag explícita."""

import argparse
import json
import os
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import httpx
from dotenv import dotenv_values
from pydantic import SecretStr
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

from app.agent.diagnostics import sanitized_429
from app.agent.openai_provider import OpenAIProvider, verified_tls_context
from app.application.tickets import register_ticket
from app.application.triage import triage_ticket
from app.domain.editing import TicketError
from app.infrastructure.database import make_sessions

MODEL = "gpt-6-luna"
INPUT = Decimal("0.10") / 1_000_000
OUTPUT = Decimal("0.50") / 1_000_000
CACHED = Decimal("0.01") / 1_000_000
WRITE = Decimal("0.125") / 1_000_000
INPUT_ASSUMPTIONS = (1500, 2500, 3500)
MAX_OUTPUT = 2000
TRIAGE_RESERVE = sum(Decimal(n) * WRITE + MAX_OUTPUT * OUTPUT for n in INPUT_ASSUMPTIONS)


class MeteredTransport(httpx.AsyncBaseTransport):
    """Consumo por HTTP, inclusive respostas rejeitadas; não registra corpos/chaves."""

    def __init__(self, pilot_budget, round_budget, emit, *, transport_factory=None):
        self.pilot_budget = pilot_budget
        self.round_budget = round_budget
        self.emit = emit
        self.transport_factory = transport_factory or (
            lambda: httpx.AsyncHTTPTransport(
                verify=verified_tls_context(), retries=0, trust_env=False
            )
        )
        self.requests = 0
        self.cost = Decimal(0)
        self.stopped = False

    def check_projection(self):
        pending = sum(
            Decimal(n) * WRITE + MAX_OUTPUT * OUTPUT for n in INPUT_ASSUMPTIONS[self.requests :]
        )
        pilot = self.cost + pending
        total = pilot + 23 * TRIAGE_RESERVE  # Piloto incluído nas 24, não 25.
        if (
            self.stopped
            or pilot > self.pilot_budget
            or (self.round_budget is not None and total > self.round_budget)
        ):
            self.stopped = True
            self.emit({"event": "stopped", "reason": "budget_or_previous_error"})
            raise ConnectionError("Avaliação interrompida.")

    async def handle_async_request(self, request):
        self.check_projection()
        if self.requests >= 3:
            raise ConnectionError("Limite de requisições.")
        self.requests += 1
        self.emit({"event": "request_started", "request_number": self.requests})
        try:
            # Cliente novo por request, pois a interface síncrona usa event loops distintos.
            async with self.transport_factory() as transport:
                result = await transport.handle_async_request(request)
                await result.aread()
            details = {
                "http_status": result.status_code,
                "request_id": result.headers.get("x-request-id"),
            }
            if result.status_code == 429:
                secret = request.headers.get("authorization", "").removeprefix("Bearer ")
                details = sanitized_429(result, secret=secret)
                details["request_id"] = details["x-request-id"]
            self.emit({"event": "response_received", "request_number": self.requests, **details})
            data = result.json()
            usage = data.get("usage") or {}
            inp, out, total = (
                usage.get(key) for key in ("input_tokens", "output_tokens", "total_tokens")
            )
            cached = (usage.get("input_tokens_details") or {}).get("cached_tokens", 0)
            reasoning = (usage.get("output_tokens_details") or {}).get("reasoning_tokens", 0)
            if (
                any(type(n) is not int or n < 0 for n in (inp, out, total, cached, reasoning))
                or cached > inp
                or reasoning > out
                or total != inp + out
            ):
                raise ValueError("Consumo ausente ou inválido.")
            nominal = (inp - cached) * INPUT + cached * CACHED + out * OUTPUT
            reserve = (inp - cached) * WRITE + cached * CACHED + out * OUTPUT
            self.cost += reserve
            self.emit(
                {
                    "event": "usage",
                    "request_number": self.requests,
                    "response_id": data.get("id") if result.status_code == 200 else None,
                    "request_id": details["request_id"],
                    "model": data.get("model") if result.status_code == 200 else None,
                    "service_tier": data.get("service_tier") if result.status_code == 200 else None,
                    "http_status": result.status_code,
                    "input_tokens": inp,
                    "cached_tokens": cached,
                    "output_tokens": out,
                    "reasoning_tokens": reasoning,
                    "total_tokens": total,
                    "cost_nominal_usd": str(nominal),
                    "cost_reserve_usd": str(reserve),
                }
            )
            if result.status_code != 200 or data.get("status") != "completed":
                raise ValueError("Resposta não concluída.")
            if data.get("service_tier") not in (None, "default", "standard"):
                raise ValueError("Revisar preço do tier antes de continuar.")
            if inp > INPUT_ASSUMPTIONS[self.requests - 1] or out > MAX_OUTPUT:
                raise ValueError("Consumo fora das premissas; revisar antes de continuar.")
            self.check_projection()
            return result
        except BaseException as exc:
            self.stopped = True
            self.emit(
                {
                    "event": "stopped",
                    "request_number": self.requests,
                    "reason": "error_or_unknown_usage_reconcile_before_retry",
                    "exception_type": type(exc).__name__,
                }
            )
            raise


def money(value):
    try:
        parsed = Decimal(value)
    except ArithmeticError:
        raise argparse.ArgumentTypeError("Orçamento deve ser USD positivo e finito.") from None
    if not parsed.is_finite() or parsed <= 0:
        raise argparse.ArgumentTypeError("Orçamento deve ser USD positivo e finito.")
    return parsed


def execute(args):
    key = os.environ.get("OPENAI_API_KEY") or dotenv_values(".env").get("OPENAI_API_KEY") or ""
    if args.model != MODEL or not key.strip():
        raise ValueError("Exige modelo revisado e chave local após aprovação.")
    url = make_url(os.environ.get("TEST_DATABASE_URL", ""))
    if (
        url.drivername != "postgresql+psycopg"
        or url.host not in {"127.0.0.1", "localhost"}
        or not (url.database or "").startswith("portfolio_test")
    ):
        raise ValueError("Exige TEST_DATABASE_URL administrativa local portfolio_test*.")
    run_id = uuid4().hex
    name = "portfolio_test_us08_" + run_id
    report = Path("reports/us08") / (run_id + ".jsonl")
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open("x", encoding="utf-8") as log:

        def emit(event):
            log.write(json.dumps(event, ensure_ascii=False) + "\n")
            log.flush()

        meter = MeteredTransport(args.pilot_budget_usd, args.round_budget_usd, emit)
        emit(
            {
                "event": "run_parameters",
                "model": args.model,
                "pilot_budget_usd": str(args.pilot_budget_usd),
                "round_budget_usd": (
                    str(args.round_budget_usd) if args.round_budget_usd is not None else None
                ),
                "authorized_triages": 1,
                "input_token_assumptions": INPUT_ASSUMPTIONS,
                "max_output_tokens_per_request": MAX_OUTPUT,
                "max_requests": 3,
                "max_tool_calls": 4,
                "deadline_seconds": 20,
                "pricing_checked_on": "2026-11-09",
            }
        )
        meter.check_projection()  # Sem rede/banco se a projeção já ultrapassa aprovação.
        admin = create_engine(url, isolation_level="AUTOCOMMIT", hide_parameters=True)
        engine = None
        try:
            with admin.connect() as connection:
                connection.exec_driver_sql(f'CREATE DATABASE "{name}"')
            emit({"event": "database_created", "database": name, "case": "AV02", "repetition": 1})
            test_url = url.set(database=name).render_as_string(hide_password=False)
            subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                env={
                    **os.environ,
                    "DATABASE_URL": test_url,
                    "AI_MODE": "simulated",
                    "APP_ENV": "test",
                },
                check=True,
                capture_output=True,
            )
            engine = create_engine(test_url, hide_parameters=True)
            sessions = make_sessions(engine)
            with sessions() as session:
                ticket = register_ticket(
                    session,
                    "Erro ao salvar cadastro fictício",
                    "No ambiente de demonstração fictício, três pessoas não conseguem salvar "
                    "o cadastro desde 08h, sem alternativa. Abrir o formulário, preencher os "
                    "campos e clicar em Salvar retorna erro e bloqueia o trabalho.",
                )
                ticket_id = ticket.id
            emit({"event": "ticket_created", "ticket_id": str(ticket_id)})
            provider = OpenAIProvider(SecretStr(key), args.model, transport=meter)
            result = triage_ticket(sessions, ticket_id, 1, provider)
            emit(
                {
                    "event": "triage_completed_requires_human_review",
                    "attempt_id": str(result["attempt"].id),
                    "category": result["attempt"].suggestion["category"],
                    "priority": result["attempt"].suggestion["priority"],
                }
            )
            print("Triagem concluída; verificar critérios e revisar antes de novas execuções.")
            return 0
        except (Exception, KeyboardInterrupt) as exc:
            emit(
                {
                    "event": "pilot_stopped",
                    "code": exc.code if isinstance(exc, TicketError) else "pilot_error",
                }
            )
            print("Piloto interrompido; conferir ledger e banco. Não repetir automaticamente.")
            return 1
        finally:
            if engine is not None:
                engine.dispose()
            admin.dispose()
            print(f"Evidência: {report}. Banco exclusivo preservado para revisão: {name}.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-approved", action="store_true")
    parser.add_argument("--model")
    parser.add_argument("--pilot-budget-usd", type=money)
    parser.add_argument("--round-budget-usd", type=money)
    args = parser.parse_args(argv)
    if not args.execute_approved:
        print(f"PREPARAÇÃO: modelo proposto {MODEL}; sem chave, banco ou chamada externa.")
        print(f"Reserva estimada: piloto USD {TRIAGE_RESERVE}; 24 USD {24 * TRIAGE_RESERVE}.")
        print(
            "Depende de aprovação de modelo/orçamentos/execução; estimativa não é teto de cobrança."
        )
        return 0
    if args.pilot_budget_usd is None:
        parser.error("Execução exige orçamento do piloto explicitamente aprovado.")
    try:
        return execute(args)
    except Exception:
        print("Pré-condição inválida; conferir configuração local sem expor segredos.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
