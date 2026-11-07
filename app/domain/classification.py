"""Contratos dos snapshots; produção de sugestões/revisões continua futura."""

from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from app.domain.catalog import Category, Priority


class Classification(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: Category
    priority: Priority


class Suggestion(Classification):
    attempt_id: UUID
    mode: Literal["simulated"]
    rationale: Annotated[str, StringConstraints(strict=True, min_length=10, max_length=500)]
    missing_fields: Annotated[
        list[Literal["ambiente", "passos_reproducao", "impacto", "inicio_ocorrencia"]],
        Field(max_length=4),
    ]


class FinalClassification(Classification):
    review_id: UUID
