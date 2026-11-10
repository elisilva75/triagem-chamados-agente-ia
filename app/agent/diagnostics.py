"""Metadados técnicos permitidos; nunca mensagem/corpo bruto do provedor."""

import re

# Lista fechada: respostas remotas não podem injetar texto livre nos logs.
ERROR_CODES = frozenset(
    {
        "insufficient_quota",
        "rate_limit_exceeded",
        "slow_down",
        "credit_balance_exhausted",
        "organization_spend_limit_exceeded",
        "project_spend_limit_exceeded",
        "organization_usage_limit_exceeded",
    }
)
ERROR_TYPES = frozenset(
    {
        "insufficient_quota",
        "rate_limit_error",
        "rate_limit_exceeded",
        "requests",
        "tokens",
        "invalid_request_error",
    }
)
REDACTED = "[redacted]"


def sanitized_429(response, *, secret=""):
    def sanitize(value, allowed=None):
        if value is None:
            return None
        if (
            type(value) is not str
            or (secret and secret in value)
            or (allowed is not None and value not in allowed)
        ):
            return REDACTED
        if allowed is None and (
            not re.fullmatch(r"req_[A-Za-z0-9_-]{1,128}", value) or "sk-" in value.lower()
        ):
            return REDACTED
        return value

    try:
        data = response.json()
    except (ValueError, UnicodeError):
        data = {}
    error = data.get("error") if isinstance(data, dict) else None
    error = error if isinstance(error, dict) else {}
    return {
        "http_status": 429,
        "error": {
            "code": sanitize(error.get("code"), ERROR_CODES),
            "type": sanitize(error.get("type"), ERROR_TYPES),
        },
        "x-request-id": sanitize(response.headers.get("x-request-id")),
    }
