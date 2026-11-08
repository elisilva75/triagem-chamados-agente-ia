"""US04: tentativas preservadas, uma ativa por chamado."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "triage_attempts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("ticket_id", sa.Uuid(), sa.ForeignKey("tickets.id"), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("content_revision", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("mode", sa.String(16), nullable=False),
        sa.Column("catalog_version", sa.String(16), nullable=False),
        sa.Column("policy_version", sa.String(16), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("suggestion", postgresql.JSONB(none_as_null=True)),
        sa.Column("error_code", sa.String(40)),
        sa.Column("model_calls", sa.Integer(), nullable=False),
        sa.Column("tool_calls", sa.Integer(), nullable=False),
        sa.UniqueConstraint("ticket_id", "attempt_number", name="uq_attempt_number"),
        sa.CheckConstraint("status IN ('em_analise','sucesso','falha')", name="ck_attempt_status"),
        sa.CheckConstraint("mode = 'simulated'", name="ck_attempt_mode"),
        sa.CheckConstraint(
            "attempt_number >= 1 AND content_revision >= 1", name="ck_attempt_numbers"
        ),
        sa.CheckConstraint(
            "model_calls BETWEEN 0 AND 3 AND tool_calls BETWEEN 0 AND 4", name="ck_attempt_calls"
        ),
        sa.CheckConstraint(
            "(status = 'em_analise' AND finished_at IS NULL "
            "AND suggestion IS NULL AND error_code IS NULL) OR "
            "(status = 'sucesso' AND finished_at IS NOT NULL "
            "AND suggestion IS NOT NULL AND error_code IS NULL) OR "
            "(status = 'falha' AND finished_at IS NOT NULL "
            "AND suggestion IS NULL AND error_code IS NOT NULL)",
            name="ck_attempt_result",
        ),
    )
    op.create_index(
        "uq_attempt_active",
        "triage_attempts",
        ["ticket_id"],
        unique=True,
        postgresql_where=sa.text("status = 'em_analise'"),
    )


def downgrade():
    op.drop_table("triage_attempts")
