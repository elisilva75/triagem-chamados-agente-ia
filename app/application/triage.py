import logging
import time
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from app.agent.orchestrator import run_agent
from app.agent.protocol import AIProvider
from app.agent.tools import POLICY_VERSION
from app.domain.catalog import CATALOG_VERSION
from app.domain.classification import Suggestion
from app.domain.editing import TicketError
from app.infrastructure.models import Ticket, TriageAttempt

logger = logging.getLogger(__name__)


class TriageFailure(TicketError):
    def __init__(self, code, ticket_id, attempt_id):
        status = 504 if code == "ai_timeout" else 503 if code == "ai_unavailable" else 502
        super().__init__(status, code, "A triagem simulada falhou; consulte o chamado.")
        self.details = [
            {"ticket_id": str(ticket_id), "attempt_id": str(attempt_id), "triage_status": "falha"}
        ]


def triage_ticket(sessions, ticket_id, expected_version, provider: AIProvider):
    started = time.monotonic()
    # A tentativa é confirmada antes de executar qualquer ferramenta/provedor.
    with sessions() as session, session.begin():
        ticket = session.scalar(select(Ticket).where(Ticket.id == ticket_id).with_for_update())
        if ticket is None:
            raise TicketError(404, "not_found", "Chamado não encontrado.")
        if ticket.version != expected_version:
            raise TicketError(409, "version_conflict", "Consulte a versão atual.")
        if ticket.status != "aberto" or ticket.triage_status != "pendente":
            # Retry/recuperação de prazo são US05; falha só sai por edição efetiva nesta entrega.
            raise TicketError(
                409,
                "invalid_transition",
                "Triagem exige chamado aberto e pendente; recuperação de falha permanece em US05.",
            )
        now = datetime.now(timezone.utc)
        number = (
            session.scalar(
                select(func.coalesce(func.max(TriageAttempt.attempt_number), 0)).where(
                    TriageAttempt.ticket_id == ticket_id
                )
            )
            + 1
        )
        attempt = TriageAttempt(
            ticket_id=ticket_id,
            attempt_number=number,
            content_revision=ticket.content_revision,
            status="em_analise",
            mode="simulated",
            catalog_version=CATALOG_VERSION,
            policy_version=POLICY_VERSION,
            started_at=now,
            deadline_at=now + timedelta(seconds=20),
        )
        session.add(attempt)
        ticket.triage_status = "em_analise"
        ticket.version += 1
        ticket.updated_at = now
        session.flush()
        attempt_id, revision, active_version = attempt.id, ticket.content_revision, ticket.version
        title, description = ticket.title, ticket.description
        deadline = attempt.deadline_at
    # Nenhuma sessão/conexão mantida durante o agente.
    result = run_agent(
        provider, title, description, budget=(deadline - datetime.now(timezone.utc)).total_seconds()
    )
    with sessions() as session, session.begin():
        ticket = session.scalar(select(Ticket).where(Ticket.id == ticket_id).with_for_update())
        attempt = session.get(TriageAttempt, attempt_id)
        now = datetime.now(timezone.utc)
        if (
            ticket.version != active_version
            or ticket.content_revision != revision
            or ticket.triage_status != "em_analise"
            or attempt.status != "em_analise"
        ):
            raise TicketError(409, "version_conflict", "Resultado obsoleto descartado.")
        if now >= deadline:
            result.output, result.error_code = None, "ai_timeout"
        attempt.model_calls, attempt.tool_calls = result.model_calls, result.tool_calls
        attempt.finished_at = now
        attempt.error_code = result.error_code
        attempt.status = "falha" if result.error_code else "sucesso"
        ticket.triage_status = "falha" if result.error_code else "sugerida"
        ticket.version += 1
        ticket.updated_at = now
        if result.output:
            attempt.suggestion = Suggestion.model_validate(
                {
                    **result.output.model_dump(mode="json"),
                    "attempt_id": str(attempt_id),
                    "mode": "simulated",
                }
            ).model_dump(mode="json")
            ticket.suggestion = attempt.suggestion
        session.flush()
        # Saída validada pelo domínio; serialização HTTP permanece na borda.
        response = {"ticket": ticket, "attempt": attempt}
    logger.info(
        "triage attempt=%s ticket=%s code=%s model_calls=%s tool_calls=%s duration_ms=%s",
        attempt_id,
        ticket_id,
        result.error_code or "success",
        result.model_calls,
        result.tool_calls,
        round((time.monotonic() - started) * 1000),
    )
    if result.error_code:
        raise TriageFailure(result.error_code, ticket_id, attempt_id)
    return response
