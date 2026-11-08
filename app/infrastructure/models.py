from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.catalog import TicketStatus, TriageStatus
from app.infrastructure.database import Base


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        CheckConstraint("char_length(title) BETWEEN 5 AND 120", name="ck_ticket_title"),
        CheckConstraint(
            "char_length(description) BETWEEN 20 AND 5000", name="ck_ticket_description"
        ),
        CheckConstraint("status IN ('aberto', 'resolvido')", name="ck_ticket_status"),
        CheckConstraint(
            "triage_status IN ('pendente','em_analise','sugerida','falha','revisada')",
            name="ck_ticket_triage_status",
        ),
        CheckConstraint("version >= 1 AND content_revision >= 1", name="ck_ticket_versions"),
        Index("ix_tickets_created_id", "created_at", "id"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default=TicketStatus.ABERTO)
    triage_status: Mapped[str] = mapped_column(String(16), default=TriageStatus.PENDENTE)
    content_revision: Mapped[int] = mapped_column(default=1)
    version: Mapped[int] = mapped_column(default=1)
    suggestion: Mapped[dict | None] = mapped_column(JSONB(none_as_null=True))
    final_classification: Mapped[dict | None] = mapped_column(JSONB(none_as_null=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TicketEvent(Base):
    __tablename__ = "ticket_events"
    __table_args__ = (
        CheckConstraint(
            "type IN ('criado','editado','resolvido','reaberto')", name="ck_event_type"
        ),
        CheckConstraint("content_revision >= 1", name="ck_event_revision"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    ticket_id: Mapped[UUID] = mapped_column(ForeignKey("tickets.id"), index=True)
    type: Mapped[str] = mapped_column(String(16))
    content_revision: Mapped[int]
    previous_classification: Mapped[dict | None] = mapped_column(JSONB(none_as_null=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TriageAttempt(Base):
    __tablename__ = "triage_attempts"
    __table_args__ = (
        UniqueConstraint("ticket_id", "attempt_number", name="uq_attempt_number"),
        Index(
            "uq_attempt_active",
            "ticket_id",
            unique=True,
            postgresql_where=text("status = 'em_analise'"),
        ),
        CheckConstraint("status IN ('em_analise','sucesso','falha')", name="ck_attempt_status"),
        CheckConstraint("mode = 'simulated'", name="ck_attempt_mode"),
        CheckConstraint("attempt_number >= 1 AND content_revision >= 1", name="ck_attempt_numbers"),
        CheckConstraint(
            "model_calls BETWEEN 0 AND 3 AND tool_calls BETWEEN 0 AND 4", name="ck_attempt_calls"
        ),
        CheckConstraint(
            "(status = 'em_analise' AND finished_at IS NULL "
            "AND suggestion IS NULL AND error_code IS NULL) OR "
            "(status = 'sucesso' AND finished_at IS NOT NULL "
            "AND suggestion IS NOT NULL AND error_code IS NULL) OR "
            "(status = 'falha' AND finished_at IS NOT NULL "
            "AND suggestion IS NULL AND error_code IS NOT NULL)",
            name="ck_attempt_result",
        ),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    ticket_id: Mapped[UUID] = mapped_column(ForeignKey("tickets.id"))
    attempt_number: Mapped[int]
    content_revision: Mapped[int]
    status: Mapped[str] = mapped_column(String(16))
    mode: Mapped[str] = mapped_column(String(16), default="simulated")
    catalog_version: Mapped[str] = mapped_column(String(16))
    policy_version: Mapped[str] = mapped_column(String(16))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    deadline_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    suggestion: Mapped[dict | None] = mapped_column(JSONB(none_as_null=True))
    error_code: Mapped[str | None] = mapped_column(String(40))
    model_calls: Mapped[int] = mapped_column(default=0)
    tool_calls: Mapped[int] = mapped_column(default=0)
