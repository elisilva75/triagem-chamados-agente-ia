"""Ensaia o roteiro ficticio em uma API local explicitamente escolhida."""

import argparse
from urllib.parse import urlsplit

import httpx


def demonstrate(base_url):
    url = urlsplit(base_url)
    if url.scheme != "http" or url.hostname not in ("127.0.0.1", "localhost"):
        raise ValueError("A demonstracao exige HTTP em loopback.")
    with httpx.Client(base_url=base_url, timeout=25, trust_env=False) as client:
        created = client.post(
            "/api/v1/tickets",
            json={
                "title": "[SIMULADO:saida-invalida]",
                "description": "No ambiente ficticio, salvar o cadastro retorna erro para todos.",
            },
        )
        assert created.status_code == 201, created.text
        path = created.headers["location"]

        def write(suffix, body, status, method="post"):
            current = client.get(path)
            current.raise_for_status()
            response = client.request(
                method, path + suffix, json={"expected_version": current.json()["version"], **body}
            )
            assert response.status_code == status, response.text
            print(method.upper(), suffix or "ticket", response.status_code, flush=True)
            return response

        for _ in range(2):
            failed = write("/triage", {}, 502)
            assert failed.json()["error"]["code"] == "invalid_ai_response"
        write("", {"title": "Erro ao salvar cadastro ficticio"}, 200, "patch")
        triaged = write("/triage", {}, 200).json()
        assert triaged["ticket"]["suggestion"]["mode"] == "simulated"
        write(
            "/reviews",
            {
                "category": "defeito",
                "priority": "alta",
                "reason": "Confirmei o bloqueio no ambiente ficticio.",
                "declared_reviewer": "Pessoa Revisora Demo",
            },
            201,
        )
        resolved = write("/resolve", {}, 200).json()
        assert resolved["status"] == "resolvido"
        assert resolved["version"] == 10 and resolved["content_revision"] == 2
        assert client.get(path + "/triage-attempts").json()["total"] == 3
        assert client.get(path + "/reviews").json()["total"] == 1
        print("Chamado ficticio preservado:", resolved["id"], flush=True)
        return resolved


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url", required=True, help="API isolada; cria um chamado ficticio novo"
    )
    demonstrate(parser.parse_args().base_url)
