import pytest
from pydantic import TypeAdapter, ValidationError

from app.api.schemas import TicketCreate
from app.config import Settings
from app.domain.catalog import Category, Priority


@pytest.mark.parametrize("title_length,description_length", [(5, 20), (120, 5000)])
def test_us02_ca3_accept_boundaries_and_trim(title_length, description_length):
    body = TicketCreate(
        title="  " + "á" * title_length + "  ", description="\n" + "ç" * description_length + "\n"
    )
    assert len(body.title) == title_length
    assert len(body.description) == description_length


@pytest.mark.parametrize(
    "patch",
    [
        {"title": "a" * 4},
        {"title": "a" * 121},
        {"description": "a" * 19},
        {"description": "a" * 5001},
        {"title": "   "},
        {"title": 12345},
        {"description": None},
        {"unknown": True},
        {"status": "resolvido"},
    ],
)
def test_us02_ca2_ca3_reject_invalid(patch):
    with pytest.raises(ValidationError):
        TicketCreate.model_validate({"title": "Título válido", "description": "d" * 20, **patch})


@pytest.mark.parametrize("enum,value", [(Category, "financeiro"), (Priority, "urgente")])
def test_approved_catalog_rejects_external_values(enum, value):
    with pytest.raises(ValidationError):
        TypeAdapter(enum).validate_python(value)


def test_configuration_only_allows_simulation():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, ai_mode="real")
    with pytest.raises(ValidationError):
        Settings(_env_file=None, database_url="sqlite://")
