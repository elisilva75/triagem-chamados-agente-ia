from app.infrastructure.repositories import TicketRepository


def register_ticket(session, title: str, description: str):
    """US02: ticket e evento confirmados juntos; nenhum provedor de IA é utilizado."""
    with session.begin():
        return TicketRepository(session).add(title, description)
