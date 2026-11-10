"""Lote US08 sequencial, habilitado exclusivamente com transporte mockado."""

import json
from pathlib import Path

import httpx

from scripts import us08_groq_pilot as pilot
from tests.agent_helpers import EVALUATION_CASES

MAX_REQUESTS = 72
MAX_PER_CASE = 3
MAX_OUTPUT = 2000
OUTPUT_BUDGET = 144000
BODY_BYTES = 16384
CASES = {
    f"AV{index:02}-R{repetition}": {
        "title": f"AV{index:02} repetição {repetition}",
        "description": description,
        "accepted_categories": {
            1: ["acesso", "infraestrutura"],
            5: ["outros", "defeito"],
            8: ["outros", "duvida"],
        }.get(index, [category]),
        "expected_priority": priority,
        "priority_is_provisional": index == 5,
    }
    for index, (description, category, priority) in enumerate(EVALUATION_CASES, 1)
    for repetition in range(1, 4)
}


def write_json(path, value):
    pilot.write_json(path, value)


class BatchBudget:
    def __init__(
        self, save, *, output_budget=OUTPUT_BUDGET, max_requests=MAX_REQUESTS, case_ids=None
    ):
        if not 0 <= output_budget <= OUTPUT_BUDGET:
            raise ValueError("Orçamento não pode ampliar o teto.")
        if type(max_requests) is not int or not 1 <= max_requests <= MAX_REQUESTS:
            raise ValueError("Limite de envios inválido.")
        self.case_ids = frozenset(CASES if case_ids is None else case_ids)
        if not self.case_ids or not self.case_ids <= CASES.keys():
            raise ValueError("IDs fora dos casos previstos.")
        self.save = save
        self.state = {
            "send_attempts": 0,
            "max_requests": max_requests,
            "reserved_output_tokens": 0,
            "output_budget": output_budget,
            "body_byte_limit": BODY_BYTES,
            "verified_input_token_limit": None,
            "input_token_estimate": None,
            "stopped": False,
            "stop_reason": None,
            "per_case": {},
            "events": [],
        }

    def stop(self, reason):
        self.state.update(stopped=True, stop_reason=reason)
        self.save()

    def reject(self, reason):
        self.stop(reason)
        raise ConnectionError(reason)

    def reserve(self, case_id, request):
        state = self.state
        if state["stopped"]:
            raise ConnectionError("batch_stopped")
        if case_id not in self.case_ids:
            self.reject("unknown_case")
        size = len(request.content)  # Corpo já serializado pelo SDK, sem cabeçalhos.
        if size > BODY_BYTES:
            self.reject("body_byte_limit")
        if str(request.url) != "https://api.groq.com/openai/v1/responses":
            self.reject("unexpected_endpoint")
        try:
            tokens = json.loads(request.content)["max_output_tokens"]
        except (ValueError, KeyError, TypeError):
            self.reject("invalid_request_body")
        if type(tokens) is not int or not 1 <= tokens <= MAX_OUTPUT:
            self.reject("output_request_limit")
        if state["send_attempts"] >= state["max_requests"]:
            self.reject("batch_request_limit")
        if state["per_case"].get(case_id, 0) >= MAX_PER_CASE:
            self.reject("case_request_limit")
        if state["reserved_output_tokens"] + tokens > state["output_budget"]:
            self.reject("output_budget")
        # Reserva e contagem persistidas ANTES do envio; falhas não devolvem saldo.
        state["send_attempts"] += 1
        state["reserved_output_tokens"] += tokens
        state["per_case"][case_id] = state["per_case"].get(case_id, 0) + 1
        state["events"].append(
            {
                "case_id": case_id,
                "body_bytes": size,
                "reserved_output_tokens": tokens,
                "input_token_estimate": None,
            }
        )
        self.save()


class GuardedTransport(httpx.AsyncBaseTransport):
    def __init__(self, budget, case_id, factory):
        self.budget, self.case_id, self.factory = budget, case_id, factory

    async def handle_async_request(self, request):
        await request.aread()
        self.budget.reserve(self.case_id, request)
        try:
            async with self.factory() as transport:
                result = await transport.handle_async_request(request)
                await result.aread()
            if result.status_code != 200:
                self.budget.stop("http_error")
            return result
        except BaseException:
            self.budget.stop("transport_error")
            raise


def execute_batch(output_dir, *, test_admin_url=None, mock_factory=None):
    # Bloqueio antes de ler chave, criar banco, diretório ou enviar requisição.
    if mock_factory is None:
        raise ValueError("Execução real desabilitada: sem teto verificável de tokens de entrada.")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)
    manifest = {
        "kind": "ensaio_automatizado_com_mocks",
        "real_execution_enabled": False,
        "cases": {
            case_id: {**case, "status": "not_executed", "evidence_path": None}
            for case_id, case in CASES.items()
        },
    }

    def save():
        write_json(output_dir / "manifest.json", manifest)

    budget = BatchBudget(save)
    manifest["budget"] = budget.state
    save()

    def mocked_transport(case_id):
        transport = mock_factory(case_id)
        if not isinstance(transport, httpx.MockTransport):
            raise ValueError("Transporte real desabilitado; exige httpx.MockTransport.")
        return transport

    for case_id, case in manifest["cases"].items():
        if budget.state["stopped"]:
            break
        case["status"] = "started"
        path = output_dir / f"{case_id}.json"
        case["evidence_path"] = path.name
        save()
        try:
            code = pilot.execute(
                report_path=path,
                test_admin_url=test_admin_url,
                mock_factory=lambda cid=case_id: GuardedTransport(
                    budget, cid, lambda: mocked_transport(cid)
                ),
                ticket_data={key: case[key] for key in ("title", "description")},
            )
            evidence = json.loads(path.read_text(encoding="utf-8"))
            case.update(
                status=evidence["result"],
                ticket_id=evidence.get("ticket_id"),
                attempt_id=evidence.get("attempt_id")
                or evidence.get("persisted_state", {}).get("attempt_id"),
            )
            if code:
                budget.stop(budget.state["stop_reason"] or "execution_error")
        except BaseException:
            case["status"] = "interrompido"
            budget.stop(budget.state["stop_reason"] or "evidence_or_execution_error")
            raise
        finally:
            save()
    return manifest


if __name__ == "__main__":
    raise SystemExit("Execução real desabilitada. Ensaio somente pelos testes com mocks.")
