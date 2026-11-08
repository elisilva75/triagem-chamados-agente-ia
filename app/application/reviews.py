from datetime import datetime, timezone
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import select

from app.domain.classification import FinalClassification, Suggestion
from app.domain.editing import TicketError
from app.infrastructure.models import HumanReview, Ticket, TicketEvent, TriageAttempt


def _invalid():
    return TicketError(409, "invalid_transition", "O chamado não permite essa operação.")


def _locked_ticket(session, ticket_id, expected_version):
    ticket = session.scalar(select(Ticket).where(Ticket.id == ticket_id).with_for_update())
    if ticket is None:
        raise TicketError(404, "not_found", "Chamado não encontrado.")
    if ticket.version != expected_version:
        raise TicketError(409, "version_conflict", "Consulte a versão atual do chamado.")
    return ticket


def _current_review(session, ticket):
    try:
        final = FinalClassification.model_validate(ticket.final_classification)
    except ValidationError:
        raise _invalid() from None
    review = session.scalar(
        select(HumanReview).where(
            HumanReview.id == final.review_id,
            HumanReview.ticket_id == ticket.id,
            HumanReview.content_revision == ticket.content_revision,
        )
    )
    if review is None or (review.category, review.priority) != (final.category, final.priority):
        raise _invalid()
    return review


def review_ticket(session, ticket_id, expected_version, values):
    """Decisão humana, sem provedor; revisão e projeção atual confirmadas juntas."""
    with session.begin():
        ticket = _locked_ticket(session, ticket_id, expected_version)
        if ticket.status != "aberto" or ticket.triage_status not in ("sugerida", "revisada"):
            raise _invalid()
        try:
            suggestion = Suggestion.model_validate(ticket.suggestion)
        except ValidationError:
            raise _invalid() from None
        attempt = session.scalar(
            select(TriageAttempt).where(
                TriageAttempt.id == suggestion.attempt_id,
                TriageAttempt.ticket_id == ticket.id,
                TriageAttempt.content_revision == ticket.content_revision,
                TriageAttempt.status == "sucesso",
            )
        )
        if attempt is None or attempt.suggestion != suggestion.model_dump(mode="json"):
            raise _invalid()
        if ticket.triage_status == "revisada":
            _current_review(session, ticket)
        review = HumanReview(
            ticket_id=ticket.id,
            attempt_id=attempt.id,
            content_revision=ticket.content_revision,
            **values,
        )
        session.add(review)
        session.flush()
        ticket.final_classification = FinalClassification(
            review_id=review.id, category=review.category, priority=review.priority
        ).model_dump(mode="json")
        ticket.triage_status = "revisada"
        ticket.version += 1
        ticket.updated_at = datetime.now(timezone.utc)
        session.flush()
        return {"ticket": ticket, "review": review}


def change_ticket_status(session, ticket_id: UUID, expected_version: int, *, resolve: bool):
    with session.begin():
        ticket = _locked_ticket(session, ticket_id, expected_version)
        source, target, event_type = (
            ("aberto", "resolvido", "resolvido") if resolve else ("resolvido", "aberto", "reaberto")
        )
        if ticket.status != source or ticket.triage_status != "revisada":
            raise _invalid()
        _current_review(session, ticket)
        ticket.status = target
        ticket.version += 1
        ticket.updated_at = datetime.now(timezone.utc)
        session.add(
            TicketEvent(
                ticket_id=ticket.id,
                type=event_type,
                content_revision=ticket.content_revision,
            )
        )
        session.flush()
        return ticket
