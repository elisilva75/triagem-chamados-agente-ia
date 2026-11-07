from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.api.schemas import TicketPatch
from app.domain.editing import TicketError, check_edit


@pytest.mark.parametrize(
    "state,triage,version,code",
    [
        ("resolvido", "revisada", 1, "invalid_transition"),
        ("aberto", "em_analise", 1, "invalid_transition"),
        ("aberto", "pendente", 2, "version_conflict"),
    ],
)
def test_us03_ca2_edit_guards(state, triage, version, code):
    ticket = SimpleNamespace(status=state, triage_status=triage, version=version, title="Título")
    with pytest.raises(TicketError) as exc:
        check_edit(ticket, 1, {"title": "Título"})
    assert exc.value.status == 409 and exc.value.code == code


def test_us03_ca3_noop_vs_effective_change():
    ticket = SimpleNamespace(status="aberto", triage_status="revisada", version=3, title="Título")
    assert not check_edit(ticket, 3, {"title": "Título"})
    assert check_edit(ticket, 3, {"title": "Outro título"})


def test_ticket_response_normalizes_database_timezone_to_utc():
    from datetime import datetime, timedelta, timezone
    from uuid import uuid4

    from app.api.schemas import TicketRead

    local = datetime(2026, 11, 7, 12, tzinfo=timezone(timedelta(hours=-3)))
    ticket = TicketRead(
        id=uuid4(),
        title="Título",
        description="d" * 20,
        status="aberto",
        triage_status="pendente",
        content_revision=1,
        version=1,
        created_at=local,
        updated_at=local,
    )
    assert ticket.model_dump(mode="json")["updated_at"] == "2026-11-07T15:00:00Z"


@pytest.mark.parametrize(
    "patch",
    [
        {},
        {"expected_version": 1},
        {"expected_version": 0, "title": "Título"},
        {"expected_version": True, "title": "Título"},
        {"expected_version": "1", "title": "Título"},
        {"expected_version": 1, "title": None},
        {"expected_version": 1, "description": None},
        {"expected_version": 1, "title": "a" * 4},
        {"expected_version": 1, "title": "a" * 121},
        {"expected_version": 1, "description": "d" * 19},
        {"expected_version": 1, "description": "d" * 5001},
        {"expected_version": 1, "title": 12345},
        {"expected_version": 1, "title": "Título", "status": "resolvido"},
        {"expected_version": 1, "title": "Título", "suggestion": {}},
    ],
)
def test_us03_ca2_ca3_patch_rejects_invalid(patch):
    with pytest.raises(ValidationError):
        TicketPatch.model_validate(patch)


@pytest.mark.parametrize("title,description", [(5, 20), (120, 5000)])
def test_us03_ca3_patch_accepts_trim_and_boundaries(title, description):
    patch = TicketPatch(
        expected_version=1,
        title=" " + "á" * title + " ",
        description="\n" + "ç" * description + "\n",
    )
    assert len(patch.title) == title and len(patch.description) == description
