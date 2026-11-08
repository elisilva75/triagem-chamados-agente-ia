"""Dados fictícios e preparação comum de revisões; sem chamadas externas."""

REVIEW = {
    "category": "defeito",
    "priority": "alta",
    "reason": "Confirmei o bloqueio no ambiente fictício.",
    "declared_reviewer": "Pessoa Revisora Demo",
}


def suggested(client):
    from tests.api.test_triage import create

    path, _ = create(client)
    response = client.post(path + "/triage", json={"expected_version": 1})
    assert response.status_code == 200, response.text
    return path, response.json()["ticket"]
