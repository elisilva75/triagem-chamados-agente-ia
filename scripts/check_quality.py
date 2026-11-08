"""Pipeline local/CI: interrompe na primeira falha e rejeita suites incompletas."""

import os
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree


def complete_report(path):
    cases = ElementTree.parse(path).findall(".//testcase")
    if not cases or any(case.find("skipped") is not None for case in cases):
        raise ValueError("Suite obrigatoria vazia ou com testes pulados.")


def main():
    if not os.environ.get("TEST_DATABASE_URL") or os.environ.get("AI_MODE") != "simulated":
        print("Defina TEST_DATABASE_URL isolada e AI_MODE=simulated.", file=sys.stderr)
        return 2
    commands = [
        ["pip", "check"],
        ["ruff", "check", "."],
        ["ruff", "format", "--check", "."],
    ]
    suites = {
        "unit": ["tests/unit"],
        "postgres-api": ["tests/integration", "tests/api"],
        "http-real": ["tests/e2e"],
    }
    for name, paths in suites.items():
        commands.append(["pytest", *paths, "-q", f"--junitxml=reports/{name}.xml"])
    for command in commands:
        print("Executando:", " ".join(command), flush=True)
        result = subprocess.run([sys.executable, "-m", *command], check=False)
        if result.returncode:
            return result.returncode
        if command[0] == "pytest":
            complete_report(Path(command[-1].split("=", 1)[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
