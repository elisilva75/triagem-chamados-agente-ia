"""US08: modo explícito e metadados do provedor; preserva tentativas existentes."""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

PROVIDER_CHECK = (
    "(mode = 'simulated' AND provider IS NULL AND model IS NULL) OR "
    "(mode = 'openai' AND provider = 'openai' AND provider IS NOT NULL "
    "AND model IS NOT NULL AND char_length(trim(model)) BETWEEN 1 AND 200)"
)


def upgrade():
    op.add_column("triage_attempts", sa.Column("provider", sa.String(16), nullable=True))
    op.add_column("triage_attempts", sa.Column("model", sa.String(200), nullable=True))
    op.drop_constraint("ck_attempt_mode", "triage_attempts", type_="check")
    op.create_check_constraint(
        "ck_attempt_mode", "triage_attempts", "mode IN ('simulated','openai')"
    )
    op.create_check_constraint("ck_attempt_provider", "triage_attempts", PROVIDER_CHECK)


def downgrade():
    # Não converte nem apaga tentativas OpenAI: CHECK antigo bloqueia downgrade com esses dados.
    op.drop_constraint("ck_attempt_provider", "triage_attempts", type_="check")
    op.drop_constraint("ck_attempt_mode", "triage_attempts", type_="check")
    op.create_check_constraint("ck_attempt_mode", "triage_attempts", "mode = 'simulated'")
    op.drop_column("triage_attempts", "model")
    op.drop_column("triage_attempts", "provider")
