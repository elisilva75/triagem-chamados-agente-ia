"""Pré-condições humanas compartilhadas; não lê credenciais nem acessa rede/banco."""

from datetime import date

SINGLE_PILOT_SCOPE = "groq_single_pilot_once"


def validate_confirmation(confirmation, *, expected_scope=None):
    if (
        not isinstance(confirmation, dict)
        or confirmation.get("plan") != "Livre"
        or confirmation.get("active") is not True
    ):
        raise ValueError("Exige confirmação atual de plano Livre e chave ativa.")
    try:
        checked = date.fromisoformat(confirmation["checked_on"])
        expires = date.fromisoformat(confirmation["expires_on"])
    except (KeyError, TypeError, ValueError):
        raise ValueError("Confirmação exige datas válidas de conferência e validade.") from None
    if checked != date.today() or expires <= date.today():
        raise ValueError("Conferência não atual ou chave fora da validade nominal.")
    if expected_scope is not None and confirmation.get("scope") != expected_scope:
        raise ValueError("Confirmação não corresponde ao escopo autorizado.")
    # Não copia campos livres nem qualquer chave que o arquivo possa conter.
    return {
        "plan": "Livre",
        "active": True,
        "checked_on": checked.isoformat(),
        "expires_on": expires.isoformat(),
        "scope": expected_scope,
    }
