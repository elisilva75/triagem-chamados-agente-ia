"""US03: classificação atual e snapshot anterior preservado em evento de edição."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tickets", sa.Column("suggestion", postgresql.JSONB(none_as_null=True)))
    op.add_column("tickets", sa.Column("final_classification", postgresql.JSONB(none_as_null=True)))
    op.add_column(
        "ticket_events", sa.Column("previous_classification", postgresql.JSONB(none_as_null=True))
    )


def downgrade():
    op.drop_column("ticket_events", "previous_classification")
    op.drop_column("tickets", "final_classification")
    op.drop_column("tickets", "suggestion")
