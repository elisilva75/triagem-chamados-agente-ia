from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.infrastructure.models import Ticket, TicketEvent


class TicketRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, title: str, description: str) -> Ticket:
        ticket = Ticket(title=title, description=description)
        self.session.add(ticket)
        self.session.flush()
        self.session.add(TicketEvent(ticket_id=ticket.id, type="criado", content_revision=1))
        self.session.flush()
        return ticket

    def get(self, ticket_id: UUID) -> Ticket | None:
        return self.session.get(Ticket, ticket_id)

    def list(self, limit: int, offset: int, status=None, triage_status=None):
        criteria = []
        if status is not None:
            criteria.append(Ticket.status == status)
        if triage_status is not None:
            criteria.append(Ticket.triage_status == triage_status)
        total = self.session.scalar(select(func.count()).select_from(Ticket).where(*criteria))
        items = self.session.scalars(
            select(Ticket)
            .where(*criteria)
            .order_by(Ticket.created_at, Ticket.id)
            .limit(limit)
            .offset(offset)
        ).all()
        return items, total
