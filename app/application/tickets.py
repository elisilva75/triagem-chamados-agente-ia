from copy import deepcopy
from datetime import datetime, timezone

from sqlalchemy import select

from app.domain.catalog import TriageStatus
from app.domain.editing import TicketError, check_edit
from app.infrastructure.models import Ticket, TicketEvent
from app.infrastructure.repositories import TicketRepository


def register_ticket(session, title: str, description: str):
    """US02: ticket e evento confirmados juntos; nenhum provedor de IA é utilizado."""
    with session.begin():
        return TicketRepository(session).add(title, description)


def edit_ticket(session, ticket_id, expected_version: int, changes: dict):
    """US03: lock de linha mantém comparação, invalidação e evento atômicos."""
    with session.begin():
        ticket = session.scalar(select(Ticket).where(Ticket.id == ticket_id).with_for_update())
        if ticket is None:
            raise TicketError(404, "not_found", "Chamado não encontrado.")
        if not check_edit(ticket, expected_version, changes):
            return ticket
        previous = deepcopy(
            {
                "content_revision": ticket.content_revision,
                "suggestion": ticket.suggestion,
                "final_classification": ticket.final_classification,
            }
        )
        for field, value in changes.items():
            setattr(ticket, field, value)
        ticket.version += 1
        ticket.content_revision += 1
        ticket.suggestion = None
        ticket.final_classification = None
        ticket.triage_status = TriageStatus.PENDENTE
        ticket.updated_at = datetime.now(timezone.utc)
        session.add(
            TicketEvent(
                ticket_id=ticket.id,
                type="editado",
                content_revision=ticket.content_revision,
                previous_classification=previous,
            )
        )
        session.flush()
        return ticket
