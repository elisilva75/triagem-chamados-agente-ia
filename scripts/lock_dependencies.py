"""Registra versões instaladas; executar somente após resolver e testar a .venv.

Inclui dependências transitivas ativas em Windows e Linux/Python 3.12.
Não faz downloads e não altera o ambiente. Os locks não incluem hashes.
"""

import importlib.metadata as metadata
import tomllib
from pathlib import Path

from packaging.markers import default_environment
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOT = Path(__file__).resolve().parents[1]
project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]


def resolve(roots):
    resolved = {}
    visited = set()
    pending = [Requirement(item) for item in roots]
    while pending:
        requirement = pending.pop()
        name = canonicalize_name(requirement.name)
        key = (name, tuple(sorted(requirement.extras)))
        if key in visited:
            continue
        visited.add(key)
        package = metadata.distribution(name)
        if not requirement.specifier.contains(package.version):
            raise RuntimeError(f"Versão instalada fora da faixa: {name}")
        resolved[name] = package.version
        for raw in package.requires or []:
            child = Requirement(raw)
            environments = []
            for platform in ("win32", "linux"):
                for extra in {"", *requirement.extras}:
                    env = default_environment()
                    env.update(
                        sys_platform=platform,
                        os_name="nt" if platform == "win32" else "posix",
                        platform_system="Windows" if platform == "win32" else "Linux",
                        extra=extra,
                    )
                    environments.append(env)
            if child.marker is None or any(child.marker.evaluate(env) for env in environments):
                pending.append(child)
    return "# Python 3.12; versões resolvidas e fixadas; Windows/Linux.\n" + "".join(
        f"{name}=={version}\n" for name, version in sorted(resolved.items())
    )


if __name__ == "__main__":
    dependencies = project["dependencies"]
    (ROOT / "requirements.lock").write_text(resolve(dependencies), encoding="utf-8")
    (ROOT / "requirements-dev.lock").write_text(
        resolve(dependencies + project["optional-dependencies"]["dev"]), encoding="utf-8"
    )
