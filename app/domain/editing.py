from app.domain.catalog import TicketStatus, TriageStatus


class TicketError(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status = status
        self.code = code
        self.message = message


def check_edit(ticket, expected_version: int, changes: dict) -> bool:
    """RN11/RN16: verificar precondições inclusive em alterações sem efeito."""
    if ticket.version != expected_version:
        raise TicketError(409, "version_conflict", "Consulte a versão atual do chamado.")
    if ticket.status != TicketStatus.ABERTO or ticket.triage_status == TriageStatus.EM_ANALISE:
        raise TicketError(409, "invalid_transition", "O chamado não permite edição neste estado.")
    return any(getattr(ticket, field) != value for field, value in changes.items())
