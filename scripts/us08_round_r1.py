"""Escopo autorizado exclusivo AV01-R1…AV08-R1; não habilita o lote de 24."""

import argparse
import json
from pathlib import Path

import httpx
from dotenv import dotenv_values
from pydantic import SecretStr

from app.agent.openai_provider import verified_tls_context
from app.agent.tools import POLICY_VERSION
from scripts import us08_groq_pilot as pilot
from scripts.us08_batch import CASES, BatchBudget, GuardedTransport, write_json
from scripts.us08_confirmation import validate_confirmation

ROUND_IDS = tuple(case_id for case_id in CASES if case_id.endswith("-R1"))
REAL_DIR = Path("reports/us08/groq-r1-authorized-2026-11-10")
REVALIDATION_IDS = ("AV01-R1", "AV05-R1", "AV06-R1")
REVALIDATION_DIR = Path("reports/us08/groq-revalidation-fields-v2-2026-11-10")
AV08_DIR = Path("reports/us08/groq-av08-revised-2026-11-10")
ADMIN_URL = (
    "postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test"
)


def run_round(
    output_dir, *, mock_factory=None, test_admin_url=ADMIN_URL, confirmation=None, profile="r1"
):
    if profile not in {"r1", "revalidate-fields-v2", "av08-revised"}:
        raise ValueError("Escopo não autorizado.")
    revalidation = profile == "revalidate-fields-v2"
    ids = REVALIDATION_IDS if revalidation else ROUND_IDS
    max_requests, output_budget = (9, 18000) if revalidation else (24, 48000)
    real_dir = REVALIDATION_DIR if revalidation else REAL_DIR
    if profile == "av08-revised":
        ids = ("AV08-R1",)
        max_requests, output_budget = 3, 6000
        real_dir = AV08_DIR
    real = mock_factory is None
    if real:
        # Conferência humana do painel, sem usar a chave para testar autenticação.
        validate_confirmation(confirmation)
        if revalidation and confirmation.get("scope") != "AV01_AV05_AV06_once_after_policy_v2":
            raise ValueError("Confirmação não corresponde à revalidação de três casos.")
        if profile == "av08-revised" and confirmation.get("scope") != "AV08_once_revised":
            raise ValueError("Confirmação não corresponde ao AV08 revisado.")
        if Path(output_dir).resolve() != real_dir.resolve():
            raise ValueError("Rodada real exige diretório exclusivo da autorização.")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)  # Sem retomada/repetição automática.
    manifest = {
        "kind": ("revalidacao_real_campos_v2" if revalidation else "rodada_real_r1")
        if real
        else "ensaio_com_mocks",
        "profile": profile,
        "policy_version": POLICY_VERSION,
        "model": pilot.MODEL,
        "scope": list(ids),
        "full_24_real_enabled": False,
        "authorization": "only_three_revalidation_once" if revalidation else "only_eight_r1_once",
        "confirmation": confirmation,
        "input_policy": "16KiB_body_accepted_input_tokens_measured_after_response",
        "dashboard_billing": {"status": "nao_confirmado", "usd": None},
        "cases": {
            cid: {**CASES[cid], "status": "not_executed", "review": "pending"} for cid in ids
        },
    }
    if profile == "av08-revised":
        manifest["kind"] = "av08_instrucoes_revisadas_real" if real else "ensaio_com_mocks"
        manifest["authorization"] = "only_av08_revised_once"

    def save():
        write_json(output_dir / "manifest.json", manifest)

    budget = BatchBudget(save, max_requests=max_requests, output_budget=output_budget, case_ids=ids)
    manifest["budget"] = budget.state
    save()
    key = None
    if real:
        # Somente depois dos testes offline e da conferência externa registrada.
        raw_key = dotenv_values(".env").get("GROQ_API_KEY") or ""
        if not raw_key.strip():
            budget.stop("missing_key")
            return manifest
        key = SecretStr(raw_key)

    def inner_factory(case_id):
        if real:
            return httpx.AsyncHTTPTransport(
                verify=verified_tls_context(), retries=0, trust_env=False
            )
        transport = mock_factory(case_id)
        if not isinstance(transport, httpx.MockTransport):
            raise ValueError("Ensaio exige httpx.MockTransport.")
        return transport

    for case_id, case in manifest["cases"].items():
        if budget.state["stopped"]:
            break
        path = output_dir / f"{case_id}.json"
        case.update(status="started", evidence_path=path.name)
        save()
        try:
            result = pilot.execute(
                report_path=path,
                test_admin_url=test_admin_url,
                approved_key=key,
                mock_factory=lambda cid=case_id: GuardedTransport(
                    budget, cid, lambda: inner_factory(cid)
                ),
                ticket_data={name: case[name] for name in ("title", "description")},
            )
            evidence = json.loads(path.read_text(encoding="utf-8"))
            case.update(
                status=evidence["result"],
                ticket_id=evidence.get("ticket_id"),
                attempt_id=evidence.get("attempt_id")
                or evidence.get("persisted_state", {}).get("attempt_id"),
            )
            if "operational_status" in evidence:
                case["operational_status"] = evidence["operational_status"]
            if "cleanup_error" in evidence:
                case["cleanup_error"] = evidence["cleanup_error"]
            if result:
                reason = (
                    "database_cleanup_error" if evidence.get("cleanup_error") else "execution_error"
                )
                budget.stop(budget.state["stop_reason"] or reason)
        except (Exception, KeyboardInterrupt) as exc:
            case["status"] = "interrompido"
            case.setdefault("execution_error", pilot.error_metadata(exc))
            budget.stop(budget.state["stop_reason"] or "execution_or_evidence_error")
        finally:
            save()
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--execute-approved-r1", action="store_true")
    group.add_argument("--execute-approved-revalidation", action="store_true")
    group.add_argument("--execute-approved-av08", action="store_true")
    parser.add_argument("--confirmation", type=Path)
    args = parser.parse_args()
    if (
        not (
            args.execute_approved_r1
            or args.execute_approved_revalidation
            or args.execute_approved_av08
        )
        or args.confirmation is None
    ):
        print("Preparação somente; sem chave, banco ou rede.")
        return 0
    profile = "revalidate-fields-v2" if args.execute_approved_revalidation else "r1"
    directory = REVALIDATION_DIR if args.execute_approved_revalidation else REAL_DIR
    if args.execute_approved_av08:
        profile, directory = "av08-revised", AV08_DIR
    if directory.exists():
        print("Autorização já registrada; não repetir.")
        return 1
    manifest = run_round(
        directory,
        confirmation=json.loads(args.confirmation.read_text(encoding="utf-8")),
        profile=profile,
    )
    print(
        json.dumps(
            {
                "manifest": str(directory / "manifest.json"),
                "budget": manifest["budget"],
                "cases": {cid: row["status"] for cid, row in manifest["cases"].items()},
            },
            ensure_ascii=True,
        )
    )
    if manifest["budget"]["stop_reason"] == "database_cleanup_error":
        return 2
    return int(manifest["budget"]["stopped"])


if __name__ == "__main__":
    raise SystemExit(main())
