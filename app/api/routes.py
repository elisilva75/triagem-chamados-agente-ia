from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.schemas import TicketCreate, TicketPage, TicketRead
from app.application.tickets import register_ticket
from app.domain.catalog import TicketStatus, TriageStatus
from app.infrastructure.repositories import TicketRepository

router = APIRouter()


def get_session(request: Request):
    with request.app.state.sessions() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/health")
def health(session: SessionDep):
    session.execute(text("SELECT 1"))
    return {"status": "ok"}


@router.post("/api/v1/tickets", response_model=TicketRead, status_code=201)
def create_ticket(body: TicketCreate, response: Response, session: SessionDep):
    ticket = register_ticket(session, body.title, body.description)
    response.headers["Location"] = f"/api/v1/tickets/{ticket.id}"
    return ticket


@router.get("/api/v1/tickets", response_model=TicketPage)
def list_tickets(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    status: TicketStatus | None = None,
    triage_status: TriageStatus | None = None,
):
    items, total = TicketRepository(session).list(limit, offset, status, triage_status)
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/api/v1/tickets/{ticket_id}", response_model=TicketRead)
def get_ticket(ticket_id: UUID, session: SessionDep):
    ticket = TicketRepository(session).get(ticket_id)
    if ticket is None:
        raise HTTPException(404)
    return ticket
