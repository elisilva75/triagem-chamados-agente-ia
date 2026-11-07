from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from app.domain.catalog import TicketStatus, TriageStatus
from app.domain.classification import FinalClassification, Suggestion

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


class TicketPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: Annotated[int, Field(strict=True, ge=1)]
    title: Title | None = None
    description: Description | None = None

    @model_validator(mode="after")
    def require_content(self):
        provided = self.model_fields_set & {"title", "description"}
        if not provided:
            raise ValueError("Informe title e/ou description.")
        if any(getattr(self, field) is None for field in provided):
            raise ValueError("Campos fornecidos não podem ser null.")
        return self


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    description: str
    status: TicketStatus
    triage_status: TriageStatus
    content_revision: int
    version: int
    suggestion: Suggestion | None = None
    final_classification: FinalClassification | None = None
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at")
    @classmethod
    def timestamps_in_utc(cls, value: datetime) -> datetime:
        return value.astimezone(timezone.utc)


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
