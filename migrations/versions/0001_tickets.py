"""US01/US02: chamados e histórico inicial; esquema independente dos modelos futuros."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tickets",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("triage_status", sa.String(16), nullable=False),
        sa.Column("content_revision", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint("char_length(title) BETWEEN 5 AND 120", name="ck_ticket_title"),
        sa.CheckConstraint(
            "char_length(description) BETWEEN 20 AND 5000", name="ck_ticket_description"
        ),
        sa.CheckConstraint("status IN ('aberto', 'resolvido')", name="ck_ticket_status"),
        sa.CheckConstraint(
            "triage_status IN ('pendente','em_analise','sugerida','falha','revisada')",
            name="ck_ticket_triage_status",
        ),
        sa.CheckConstraint("version >= 1 AND content_revision >= 1", name="ck_ticket_versions"),
    )
    op.create_index("ix_tickets_created_id", "tickets", ["created_at", "id"])
    op.create_table(
        "ticket_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("ticket_id", sa.Uuid(), sa.ForeignKey("tickets.id"), nullable=False),
        sa.Column("type", sa.String(16), nullable=False),
        sa.Column("content_revision", sa.Integer(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.CheckConstraint(
            "type IN ('criado','editado','resolvido','reaberto')", name="ck_event_type"
        ),
        sa.CheckConstraint("content_revision >= 1", name="ck_event_revision"),
    )
    op.create_index("ix_ticket_events_ticket_id", "ticket_events", ["ticket_id"])


def downgrade():
    op.drop_table("ticket_events")
    op.drop_table("tickets")
