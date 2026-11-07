from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints

from app.domain.catalog import TicketStatus, TriageStatus

Title = Annotated[
    str, StringConstraints(strict=True, strip_whitespace=True, min_length=5, max_length=120)
]
Description = Annotated[
    str, StringConstraints(strict=True, strip_whitespace=True, min_length=20, max_length=5000)
]


class TicketCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: Title
    description: Description


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    description: str
    status: TicketStatus
    triage_status: TriageStatus
    content_revision: int
    version: int
    suggestion: None = None
    final_classification: None = None
    created_at: datetime
    updated_at: datetime


class TicketPage(BaseModel):
    items: list[TicketRead]
    total: int
    limit: int
    offset: int


class ErrorDetail(BaseModel):
    field: str
    code: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail]
    request_id: UUID


class ErrorResponse(BaseModel):
    error: ErrorBody
