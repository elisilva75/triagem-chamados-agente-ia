from uuid import UUID, uuid4

import pytest

pytestmark = pytest.mark.postgres
BODY = {"title": "Erro de demonstração", "description": "Descrição fictícia do erro na tela."}


def test_us01_ca1_us02_ca1_create_read_list(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/api/v1/tickets").json() == {
        "items": [],
        "total": 0,
        "limit": 20,
        "offset": 0,
    }
    response = client.post("/api/v1/tickets", json=BODY)
    assert response.status_code == 201
    ticket = response.json()
    assert UUID(ticket["id"])
    assert response.headers["location"] == "/api/v1/tickets/" + ticket["id"]
    assert ticket["status"] == "aberto" and ticket["triage_status"] == "pendente"
    assert ticket["version"] == ticket["content_revision"] == 1
    assert ticket["suggestion"] is ticket["final_classification"] is None
    assert client.get(response.headers["location"]).json() == ticket
    assert client.get("/api/v1/tickets?status=resolvido").json()["total"] == 0
    assert client.get("/api/v1/tickets?triage_status=pendente").json()["total"] == 1
    # Cadastro/edição não dependem de provedor; US04 acrescenta rotas separadas.
    paths = client.get("/openapi.json").json()["paths"]
    assert set(paths) == {
        "/health",
        "/api/v1/tickets",
        "/api/v1/tickets/{ticket_id}",
        "/api/v1/tickets/{ticket_id}/triage",
        "/api/v1/tickets/{ticket_id}/triage-attempts",
    }
    assert paths["/api/v1/tickets"]["post"]["responses"]["422"]["content"]["application/json"][
        "schema"
    ]["$ref"].endswith("ErrorResponse")


@pytest.mark.parametrize(
    "patch",
    [
        {"title": "   "},
        {"title": 12345},
        {"description": None},
        {"extra": "segredo"},
        {"title": "a" * 4},
        {"title": "a" * 121},
        {"description": "d" * 19},
        {"description": "d" * 5001},
    ],
)
def test_us02_ca2_ca3_invalid_not_persisted(client, patch):
    response = client.post("/api/v1/tickets", json={**BODY, **patch})
    assert response.status_code == 422
    assert "input" not in response.json()["error"]["details"][0]
    assert client.get("/api/v1/tickets").json()["total"] == 0


@pytest.mark.parametrize("lengths", [(5, 20), (120, 5000)])
def test_us02_ca3_http_boundaries(client, lengths):
    title, description = lengths
    response = client.post(
        "/api/v1/tickets",
        json={"title": "  " + "á" * title + "  ", "description": "\n" + "ç" * description + "\n"},
    )
    assert response.status_code == 201
    assert len(response.json()["title"]) == title


@pytest.mark.parametrize(
    "query",
    ["limit=0", "limit=101", "offset=-1", "status=novo", "triage_status=invalido", "limit=x"],
)
def test_us02_ca4_invalid_pagination_filters(client, query):
    assert client.get("/api/v1/tickets?" + query).status_code == 422


def test_us02_ca2_ca4_not_found_and_stable_pagination(client):
    assert client.get(f"/api/v1/tickets/{uuid4()}").status_code == 404
    assert client.get("/api/v1/tickets/not-a-uuid").status_code == 422
    for _ in range(3):
        assert client.post("/api/v1/tickets", json=BODY).status_code == 201
    whole = client.get("/api/v1/tickets?limit=100").json()
    pages = [client.get(f"/api/v1/tickets?limit=1&offset={i}").json()["items"][0] for i in range(3)]
    assert pages == whole["items"]
    assert whole["total"] == 3
    assert client.get("/api/v1/tickets?offset=3").json()["items"] == []
