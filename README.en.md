# Ticket Triage — simulated MVP

US08: [experimental optional Groq adapter](docs/23-adaptador-groq.md), with mocked
HTTP tests and an exploratory evaluation of eight fictitious scenarios reviewed
by Eliana. Simulation remains the default; further calls and the real 24-run batch are paused.

[Português](README.md) · Portfolio by **Eliana Gomes da Silva** · version 0.5.0.

A local API for recording support tickets, suggesting classifications and supporting traceable human decisions. **Simulation is the default:** reproducible scripts consult two local tools (category catalog and priority policy). US08 adds optional OpenAI and Groq Responses API adapters. Groq explicitly requires `AI_MODE=groq`, `GROQ_API_KEY` and `GROQ_MODEL`; incomplete configuration fails without fallback. Keep `AI_MODE=simulated` locally and never commit the key. [OpenAI pilot history](docs/21-resultado-piloto-us08.md) and [Groq configuration](docs/23-adaptador-groq.md) (Portuguese).

In the exploratory evaluation with `openai/gpt-oss-20b`, all eight scenarios received at least one valid, human-reviewed suggestion across separate stages. The first round had seven successes and an HTTP 429 `rate_limit_exceeded` for AV08, preserved as a failure. Revalidating AV01/AV05/AV06 improved AV01 missing fields, but AV05 changed from provisional `media` to `baixa`, a divergence with no definitive human priority. A later AV08 run had `duvida / baixa` and an empty list accepted; “no blocking reported” does not establish “no impact”. Missing-field quality issues remain, and full injection resistance for AV06 is inconclusive. **Consistency across 24 controlled runs (three per scenario under the same instructions) has not been evaluated**; the real batch remains disabled. [Results, denominators and limitations](docs/andamento.md) (Portuguese).

Executor usage is separate from billing: 16,426 known/partial tokens in the first round, 10,924 in revalidation and 3,227 in the later AV08 run. The dashboard was reported as showing **no charge observed on the Free plan**, with a USD 0.01 monthly projection for the Default project, without stage-specific costs. Billing for the latest AV08 remains **unconfirmed**. Raw reports in `reports/` stay local and Git-ignored; documentation preserves the reviewed summary.

Features: registration, paginated queries, optimistic version checks, validated suggestions, explicit retries, expired-attempt recovery, human review, final classification, resolution and reopening. Effective edits invalidate the current classification while preserving previous attempts, reviews and classification snapshots. Registration works without triage; a human decides the final classification.

Architecture: modular monolith with FastAPI/Pydantic → application services and domain rules → SQLAlchemy/PostgreSQL repositories; Alembic migrations. A separate orchestrator uses AIProvider with simulation by default and optional OpenAI/Groq adapters. Attempts are persisted before execution; provider calls hold no database transaction. Tool/output validation happens outside the provider. [Architecture and decisions](docs/04-arquitetura.md) (Portuguese).

## Get the project

Repository: [elisilva75/triagem-chamados-agente-ia](https://github.com/elisilva75/triagem-chamados-agente-ia), default branch **main**. To contribute, fork on GitHub and clone your fork. To run only, clone the original:

```powershell
git clone "https://github.com/elisilva75/triagem-chamados-agente-ia.git"
Set-Location triagem-chamados-agente-ia
```

No remote setup or publication is required to run a local copy.

## Prerequisites and native installation (Windows/PowerShell)

Install Python **3.12.x** from the [official Windows distributions](https://www.python.org/downloads/windows/), PostgreSQL **16** with command-line tools from the [official site](https://www.postgresql.org/download/windows/) and [Git for Windows](https://git-scm.com/downloads/win). Add Python to PATH and locate the PostgreSQL binaries. Actual tested versions are listed below; other patches/operating systems have not been certified. You do not need to start a global PostgreSQL service or install pgAdmin for this guide.

From the repository root, preferably outside a synchronized folder:

```powershell
python --version
git --version
& 'C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe' --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
.\.venv\Scripts\python.exe -m pip check
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

Keep APP_ENV=local and AI_MODE=simulated in .env. For native execution, **replace the example DATABASE_URL** with the value below. The template uses the Compose port/user, which differ from the native cluster.

| Variable | Native local value |
|---|---|
| APP_ENV | local |
| AI_MODE | simulated |
| DATABASE_URL | postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_chamados_demo |

These are fictitious development credentials, not production secrets. .env is Git-ignored; do not add real keys. PowerShell environment variables override .env. The commands below set them explicitly to avoid another connection. Do not change global execution policy or activate the venv; invoke its Python directly.

## Start using the rehearsed native path

```powershell
.\scripts\start-test-postgres.ps1
# First run only: skip createdb if the database already exists.
$env:PGPASSWORD = 'senha_ficticia_teste'
& 'C:\Program Files\PostgreSQL\16\bin\createdb.exe' -h 127.0.0.1 -p 55432 -U portfolio_test portfolio_chamados_demo
Remove-Item Env:PGPASSWORD
$env:APP_ENV = 'local'
$env:AI_MODE = 'simulated'
$env:DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_chamados_demo'
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --no-access-log
```

The helper starts/reuses .local/pgdata on **127.0.0.1:55432**, preserves data and sets TEST_DATABASE_URL in the current session. Pass `-PgBin 'C:\path\PostgreSQL\16\bin'` for another binary location. The local cluster role can create test databases. Never use an employer or production database. If createdb/migration fails, resolve it before starting the API; do not delete the database.

In another terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/tickets
```

Complement health 200 with a real query. Swagger: **http://127.0.0.1:8000/docs**; OpenAPI: /openapi.json. Local migration head is 0006; requests never apply migrations. The existing demo was not migrated in this delivery; explicitly upgrade it before running this version against it.

## Stop and restart without deleting data

First press Ctrl+C in the API terminal. Stop the cluster only when no API or test suite is using it. To restart only the API, leave PostgreSQL running and repeat only the environment variables and Uvicorn command.

```powershell
# API: Ctrl+C
.\scripts\stop-test-postgres.ps1
# Full restart: reuse cluster/database; do not run createdb again.
.\scripts\start-test-postgres.ps1
$env:APP_ENV = 'local'
$env:AI_MODE = 'simulated'
$env:DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_chamados_demo'
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --no-access-log
```

When updating code, stop the API, keep the cluster running, run `alembic upgrade head` with the venv Python and correct connection, then restart Uvicorn. Never repeat initdb, downgrade the demo, delete .local/pgdata or clear the demo database.

## Docker Compose — alternative not validated yet

Docker was unavailable locally. **Compose build/start and restart persistence have not been executed**. Install/start [Docker Desktop with Linux containers and Compose](https://docs.docker.com/desktop/setup/install/windows-install/) following its official prerequisites. CI checks the application on a Linux runner with a PostgreSQL service; it does not validate the API image or Compose flow.

Default published ports: **127.0.0.1:5432** (database) and **127.0.0.1:8000** (API). Stop your native API first or follow the [isolated project/alternative ports guide](docs/10-validacao-local.md). Do not stop unrelated services to free ports. Compose defines its own internal DATABASE_URL at db:5432 and fictitious YAML credentials; it does not use the native database or the DATABASE_URL from .env.

```powershell
docker version
docker compose version
docker compose -p portfolio-local config --quiet
docker compose -p portfolio-local up --build -d
docker compose -p portfolio-local ps -a
docker compose -p portfolio-local logs --tail 50 migrate api
```

Require a healthy db and migrate exited(0) before the API. Then repeat health, a real query and the Swagger example. Always use the same project name and checkout to reuse the volume.

```powershell
docker compose -p portfolio-local stop
docker compose -p portfolio-local up -d
docker compose -p portfolio-local restart db api
docker compose -p portfolio-local down
```

These are alternatives: stop pauses; up -d resumes; restart restarts existing services; down removes containers/network while **preserving the named volume**. Wait for health and compare GET for the same ticket after restarting. **Never add -v to down**, remove volumes or switch project names expecting the same data. For code/image updates, run up --build -d again. These commands remain untested.

## Complete Swagger example

Use a new fictitious ticket. In /docs execute POST **/api/v1/tickets** (Portuguese text/enum values are part of the business example):

```json
{"title":"Erro ao salvar cadastro fictício","description":"No ambiente fictício, salvar o cadastro retorna erro para todos os usuários."}
```

Expected: 201, ID, aberto/pendente, version=1, content_revision=1. Save the ID. GET /api/v1/tickets/{ticket_id}; copy version into POST /api/v1/tickets/{ticket_id}/triage:

```json
{"expected_version":1}
```

Expected: 200, {ticket,attempt}, suggestion mode=simulated, triage_status=sugerida, version=3/content_revision=1. GET again and use the current version in POST /api/v1/tickets/{ticket_id}/reviews:

```json
{"expected_version":3,"category":"defeito","priority":"alta","reason":"Confirmei o bloqueio no ambiente fictício.","declared_reviewer":"Pessoa Revisora Demo"}
```

Expected: 201, {ticket,review}, version=4, triage_status=revisada and final classification. GET and POST /api/v1/tickets/{ticket_id}/resolve:

```json
{"expected_version":4}
```

Expected: 200, status=resolvido, version=5/content_revision=1. GET confirms persistence; GET triage-attempts and GET reviews preserve the records. These versions assume only this sequence: **GET before every write to an existing ticket**, including no-ops. [API contract](docs/05-api.md); [failure/retry demo and portfolio](docs/16-demonstracao-e-portfolio.md) (Portuguese). Demonstrations are optional; no repeated manual acceptance is required.

## Automated tests with isolated databases

Start the cluster with the helper, preserving the demo. From the root:

```powershell
$env:TEST_DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
$env:AI_MODE = 'simulated'
$env:APP_ENV = 'test'
.\.venv\Scripts\python.exe scripts/check_quality.py
```

Pipeline: pip check, Ruff check/format, unit tests, PostgreSQL integration/in-process API tests and HTTP/TCP against a separate Uvicorn process. Fixtures create/migrate/drop only unique portfolio_test_<uuid> databases; they never clear the supplied administrative database. Do not use the demo DATABASE_URL as TEST_DATABASE_URL. The administrative URL must target loopback with the portfolio_test prefix and permission to create databases.

The pipeline stops on the first failure and rejects empty/skipped mandatory suites. Git-ignored JUnit reports go to reports/. Partial check: `.\.venv\Scripts\python.exe -m pytest tests/unit -q`. Outside the pipeline, missing TEST_DATABASE_URL skips PostgreSQL tests; this does not prove they pass. Actions uses the same runner on Ubuntu with a PostgreSQL service and no paid key; [remote CI passed: 177 tests](https://github.com/elisilva75/triagem-chamados-agente-ia/actions/runs/42507831040).

## Troubleshooting

| Symptom | Check / fix while preserving data |
|---|---|
| Missing/wrong Python | Check python --version: this project requires 3.12.x. Correct PATH/select installation before creating the venv; do not replace global packages. |
| Port 8000/5432 occupied | `Get-NetTCPConnection -State Listen -LocalPort 8000,5432,55432 -ErrorAction SilentlyContinue`; identify the service. Use Uvicorn --port 18000 or the isolated Compose guide. Do not kill processes by the generic Python name. |
| PostgreSQL connection refused / health 503 | `& 'C:\Program Files\PostgreSQL\16\bin\pg_isready.exe' -h 127.0.0.1 -p 55432`; start/reuse the helper cluster. Check database name, port, session variables and .env. Do not print credentials in reports. |
| Missing relation / outdated migration | With the correct connection, run `.\.venv\Scripts\python.exe -m alembic current`, `-m alembic heads` and `-m alembic upgrade head`. Never downgrade/reset the demo. Create a missing database once with createdb; Alembic does not create the database itself. |
| pg_ctl permission failure / blocked script | Use the same user that started the cluster; check binaries and machine policy. Codex's restricted token failed to recognize an existing process; authorized execution outside that restriction worked. Do not delete postmaster.pid or change global execution policy as a shortcut. |
| 409 version_conflict / triage_in_progress | GET and review version/state. An unexpired active attempt blocks another triage; recovery is explicit after its deadline. Do not clear data to unblock it. |
| Compose migrate service failed | Inspect ps -a and logs migrate. Correct connection/migration before retrying; do not remove the volume. Compose remains unvalidated. |

## Actual versions and latest executed validation

| Component | Version |
|---|---|
| Application / local migration head | 0.5.0 / 0006 |
| Python / pip / Git | 3.12.6 / 24.2 / 2.46.2.windows.1 |
| PowerShell | 5.1.26100.9818 |
| PostgreSQL native | 16.4 |
| FastAPI / Starlette / Uvicorn | 0.162.2 / 1.10.0 / 0.54.0 |
| Pydantic / pydantic-settings | 2.14.3 / 2.16.2 |
| SQLAlchemy / Alembic / psycopg | 2.0.57 / 1.20.1 / 3.3.8 |
| pytest / HTTPX / Ruff | 9.2.0 / 0.28.1 / 0.17.4 |

Windows 11 build 26300, PowerShell and native PostgreSQL. Complete pins: requirements.lock and requirements-dev.lock. These are the versions actually used, **not a promise for other patches/OSs**. The API image python:3.12-slim has not been build-tested; the CI postgres:16 service ran PostgreSQL 16.15 according to its logs. [Sources and compatibility](docs/09-ambiente-e-versoes.md).

Previous local validation on **2026-11-08**: venv Python with `scripts/check_quality.py` and the variables above, **177 passed**, no failures/errors/skips (98 unit, 77 integration/API, 2 real HTTP). Dependency/Ruff checks passed. The known TestClient/HTTPX warning remains visible. Isolated installation/native API restart passed and the demo was preserved.

**GitHub CI passed on 2026-11-08**, commit `c7c3331`: `python scripts/check_quality.py`, the same **177 tests**, zero failures/errors/skips in all three JUnit reports. Log-observed environment: Ubuntu 26.04, Python 3.12.16, PostgreSQL 16.15 and the same locks. The subsequent documentation-only commit uses `[skip ci]` to avoid repeating the full suite without functional changes; it does not claim a new execution for that documentation commit. Compose/API image remain unvalidated. [Evidence and limits](docs/andamento.md).

## Limitations, license and publication

**Loopback only, fictitious data, no authentication.** Do not expose publicly or use employer data. Reviewer identity is declared, not authenticated. No complete historical text reconstruction, legal audit guarantee or distributed worker. The small real evaluation is exploratory; it does not establish general model quality, consistency or full security. The 16 KiB body limit is a byte limit, not a verifiable input-token ceiling.

Licensed under [MIT](LICENSE), copyright 2026 Eliana Gomes da Silva. Public publication of main was authorized by the author, with her confirmed GitHub noreply address in commit metadata. Publication/CI results and the audit are documented in the review linked below and delivery log. Docker Compose validation remains pending. No deployment or paid call has been performed.

AI assistance (Codex) supported implementation, review, testing and documentation under Eliana's product decisions and review. This is distinct from the application's simulator.

[Product](docs/01-produto.md) · [Rules](docs/02-regras-e-fluxos.md) · [Backlog/traceability](docs/03-backlog.md) · [Tests](docs/06-testes.md) · [DoD/delivery](docs/07-entregas.md) · [Windows guide](docs/10-validacao-local.md) · [Publication review](docs/17-revisao-publicacao.md) (detailed documents in Portuguese).
