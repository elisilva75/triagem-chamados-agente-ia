from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import UUID

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.infrastructure.models import HumanReview, Ticket, TriageAttempt

SQL = (Path(__file__).resolve().parents[2] / "scripts/triage_review_agreement.sql").read_text(
    encoding="utf-8"
)
NOW = datetime(2026, 11, 9, tzinfo=UTC)


def attempt(session, *, status="sucesso", suggestion=None):
    ticket = Ticket(title="Chamado fictício", description="Descrição fictícia para avaliação SQL.")
    session.add(ticket)
    session.flush()
    result = TriageAttempt(
        ticket_id=ticket.id,
        attempt_number=1,
        content_revision=1,
        status=status,
        mode="simulated",
        catalog_version="1",
        policy_version="1",
        started_at=NOW,
        deadline_at=NOW + timedelta(seconds=20),
        finished_at=NOW + timedelta(seconds=1),
        suggestion=(
            suggestion or {"category": "defeito", "priority": "alta"}
            if status == "sucesso"
            else None
        ),
        error_code="ai_timeout" if status == "falha" else None,
    )
    session.add(result)
    session.flush()
    return result


def review(session, target, *, number, category="defeito", priority="alta", created_at=NOW):
    session.add(
        HumanReview(
            id=UUID(int=number),
            ticket_id=target.ticket_id,
            attempt_id=target.id,
            content_revision=1,
            category=category,
            priority=priority,
            reason="Decisão fictícia para validar o cálculo.",
            declared_reviewer="Pessoa Fictícia",
            created_at=created_at,
        )
    )


@pytest.mark.parametrize("scenario", ["empty", "correction", "priority", "exclusions"])
def test_review_agreement(migrated_url, scenario):
    engine = create_engine(migrated_url)
    try:
        with Session(engine) as session:
            if scenario == "correction":
                target = attempt(session)
                # Maior ID antigo não vence a data; empate recente usa o maior ID.
                review(session, target, number=100, category="outros")
                review(
                    session, target, number=1, category="outros", created_at=NOW + timedelta(days=1)
                )
                review(session, target, number=2, created_at=NOW + timedelta(days=1))
            elif scenario == "priority":
                review(session, attempt(session), number=1, priority="baixa")
            elif scenario == "exclusions":
                review(session, attempt(session), number=1)
                attempt(session)  # Sucesso sem revisão.
                failed = attempt(session, status="falha")
                # Fixture SQL deliberada: a API não permite revisar falha.
                review(session, failed, number=2)
                incomplete = attempt(session, suggestion={"category": "defeito"})
                review(session, incomplete, number=3)
                incomplete_category = attempt(session, suggestion={"priority": "alta"})
                review(session, incomplete_category, number=4)
            session.commit()
        with engine.connect() as connection:
            rows = connection.exec_driver_sql(SQL).all()
            if scenario == "empty":
                assert rows == []
            elif scenario == "priority":
                assert rows == [("simulated", 1, 1, Decimal("100.00"), 0, Decimal("0.00"), 0)]
            else:
                assert rows == [("simulated", 1, 1, Decimal("100.00"), 1, Decimal("100.00"), 1)]
    finally:
        engine.dispose()
