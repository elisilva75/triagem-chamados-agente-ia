"""US08: aceita Groq sem reescrever dados existentes."""

from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def constraints(modes):
    op.drop_constraint("ck_attempt_provider", "triage_attempts", type_="check")
    op.drop_constraint("ck_attempt_mode", "triage_attempts", type_="check")
    op.create_check_constraint("ck_attempt_mode", "triage_attempts", f"mode IN ({modes})")
    op.create_check_constraint(
        "ck_attempt_provider",
        "triage_attempts",
        "(mode = 'simulated' AND provider IS NULL AND model IS NULL) OR "
        "(mode IN ('openai','groq') AND provider = mode AND provider IS NOT NULL "
        "AND model IS NOT NULL AND char_length(trim(model)) BETWEEN 1 AND 200)",
    )


def upgrade():
    constraints("'simulated','openai','groq'")


def downgrade():
    # O CHECK bloqueia o downgrade se houver Groq; transação preserva os dados.
    constraints("'simulated','openai'")
