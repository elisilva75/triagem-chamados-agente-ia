from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.api.schemas import (
    AttemptPage,
    ReviewCreate,
    ReviewPage,
    ReviewRead,
    ReviewResponse,
    TicketCreate,
    TicketPage,
    TicketPatch,
    TicketRead,
    TriageRequest,
    TriageResponse,
    VersionRequest,
)
from app.application.reviews import change_ticket_status, review_ticket
from app.application.tickets import edit_ticket, register_ticket
from app.application.triage import triage_ticket
from app.domain.catalog import TicketStatus, TriageStatus
from app.infrastructure.models import HumanReview, TriageAttempt
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


@router.patch("/api/v1/tickets/{ticket_id}", response_model=TicketRead)
def patch_ticket(ticket_id: UUID, body: TicketPatch, session: SessionDep):
    changes = body.model_dump(exclude_unset=True, exclude={"expected_version"})
    return edit_ticket(session, ticket_id, body.expected_version, changes)


@router.post("/api/v1/tickets/{ticket_id}/triage", response_model=TriageResponse)
def post_triage(ticket_id: UUID, body: TriageRequest, request: Request):
    return triage_ticket(
        request.app.state.sessions, ticket_id, body.expected_version, request.app.state.provider
    )


@router.get("/api/v1/tickets/{ticket_id}/triage-attempts", response_model=AttemptPage)
def list_attempts(
    ticket_id: UUID,
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    if TicketRepository(session).get(ticket_id) is None:
        raise HTTPException(404)
    condition = TriageAttempt.ticket_id == ticket_id
    items = session.scalars(
        select(TriageAttempt)
        .where(condition)
        .order_by(TriageAttempt.started_at, TriageAttempt.id)
        .limit(limit)
        .offset(offset)
    ).all()
    total = session.scalar(select(func.count()).select_from(TriageAttempt).where(condition))
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.post("/api/v1/tickets/{ticket_id}/reviews", response_model=ReviewResponse, status_code=201)
def post_review(ticket_id: UUID, body: ReviewCreate, response: Response, session: SessionDep):
    result = review_ticket(
        session, ticket_id, body.expected_version, body.model_dump(exclude={"expected_version"})
    )
    response.headers["Location"] = f"/api/v1/tickets/{ticket_id}/reviews/{result['review'].id}"
    return result


@router.get("/api/v1/tickets/{ticket_id}/reviews", response_model=ReviewPage)
def list_reviews(
    ticket_id: UUID,
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    if TicketRepository(session).get(ticket_id) is None:
        raise HTTPException(404)
    condition = HumanReview.ticket_id == ticket_id
    items = session.scalars(
        select(HumanReview)
        .where(condition)
        .order_by(HumanReview.created_at, HumanReview.id)
        .limit(limit)
        .offset(offset)
    ).all()
    total = session.scalar(select(func.count()).select_from(HumanReview).where(condition))
    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.get("/api/v1/tickets/{ticket_id}/reviews/{review_id}", response_model=ReviewRead)
def get_review(ticket_id: UUID, review_id: UUID, session: SessionDep):
    review = session.scalar(
        select(HumanReview).where(HumanReview.id == review_id, HumanReview.ticket_id == ticket_id)
    )
    if review is None:
        raise HTTPException(404)
    return review


@router.post("/api/v1/tickets/{ticket_id}/resolve", response_model=TicketRead)
def resolve_ticket(ticket_id: UUID, body: VersionRequest, session: SessionDep):
    return change_ticket_status(session, ticket_id, body.expected_version, resolve=True)


@router.post("/api/v1/tickets/{ticket_id}/reopen", response_model=TicketRead)
def reopen_ticket(ticket_id: UUID, body: VersionRequest, session: SessionDep):
    return change_ticket_status(session, ticket_id, body.expected_version, resolve=False)
