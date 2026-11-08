"""US06: decisões humanas imutáveis vinculadas ao chamado, tentativa e revisão."""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint(
        "uq_attempt_identity", "triage_attempts", ["id", "ticket_id", "content_revision"]
    )
    op.create_table(
        "human_reviews",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("ticket_id", sa.Uuid(), sa.ForeignKey("tickets.id"), nullable=False),
        sa.Column("attempt_id", sa.Uuid(), nullable=False),
        sa.Column("content_revision", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(16), nullable=False),
        sa.Column("priority", sa.String(16), nullable=False),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("declared_reviewer", sa.String(80), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["attempt_id", "ticket_id", "content_revision"],
            ["triage_attempts.id", "triage_attempts.ticket_id", "triage_attempts.content_revision"],
            name="fk_review_attempt_content",
        ),
        sa.CheckConstraint("content_revision >= 1", name="ck_review_revision"),
        sa.CheckConstraint(
            "category IN ('acesso','defeito','infraestrutura','duvida','outros')",
            name="ck_review_category",
        ),
        sa.CheckConstraint(
            "priority IN ('baixa','media','alta','critica')", name="ck_review_priority"
        ),
        sa.CheckConstraint("char_length(reason) BETWEEN 10 AND 500", name="ck_review_reason"),
        sa.CheckConstraint(
            "char_length(declared_reviewer) BETWEEN 2 AND 80", name="ck_review_reviewer"
        ),
    )
    op.create_index("ix_review_ticket_created", "human_reviews", ["ticket_id", "created_at", "id"])


def downgrade():
    op.drop_table("human_reviews")
    op.drop_constraint("uq_attempt_identity", "triage_attempts", type_="unique")
