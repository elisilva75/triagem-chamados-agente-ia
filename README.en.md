# Ticket Triage — simulated MVP

[Português](README.md) · Portfolio by **Eliana Gomes da Silva** · version 0.5.0.

A local API for creating and editing support tickets, producing reproducible suggestions, and recording human decisions. The agent is **entirely simulated**: scripted tool calls consult a local category catalog and priority policy. There is no LLM, API key or paid inference. Real-model integration is deferred to US08.

Features include optimistic version checks, paginated queries, strict suggestion validation, explicit retries, expired-attempt recovery, human review, final classification, resolution and reopening. Effective edits invalidate the current classification while preserving attempts, reviews and classification snapshots. Human decisions remain separate from suggestions.

## Install and run on Windows

Requirements: Python 3.12.x, PostgreSQL 16 command-line tools and Git. Run in PowerShell from the repository root. Use fictitious data and loopback only; there is no authentication.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
.\scripts\start-test-postgres.ps1
# Fresh installation only: create once; skip createdb if the database exists.
$env:PGPASSWORD = 'senha_ficticia_teste'
& 'C:\Program Files\PostgreSQL\16\bin\createdb.exe' -h 127.0.0.1 -p 55432 -U portfolio_test portfolio_chamados_demo
Remove-Item Env:PGPASSWORD
$env:DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_chamados_demo'
$env:AI_MODE = 'simulated'
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000 --no-access-log
```

The PostgreSQL helper preserves an existing cluster and binds to 127.0.0.1:55432. Pass `-PgBin` for another PostgreSQL installation path. Passwords shown are fictitious local defaults. Use a new database and another API port for an independent rehearsal; never reset the demo. Ctrl+C stops the API. Stop the project cluster only when no API/tests use it (`scripts/stop-test-postgres.ps1`). Do not change the global PowerShell execution policy or activate the venv; invoke its Python directly.

Swagger: http://127.0.0.1:8000/docs. Check `/health` and GET `/api/v1/tickets`. POST `/api/v1/tickets` accepts:

```json
{"title":"Demo ticket title","description":"Fictitious issue blocking the demo screen."}
```

Every write to an existing ticket requires `expected_version` from a fresh GET. Relative to `/api/v1/tickets/{ticket_id}`, POST `triage` accepts `{"expected_version":1}` and returns `{ticket,attempt}`. POST `reviews` accepts the current version, category, priority, reason and declared_reviewer; POST `resolve`/`reopen` accept the current version. GET `triage-attempts`/`reviews` expose history. See the [API contract](docs/05-api.md) and [short demo with full bodies](docs/16-demonstracao-e-portfolio.md) (Portuguese).

## Test

```powershell
$env:TEST_DATABASE_URL = 'postgresql+psycopg://portfolio_test:senha_ficticia_teste@127.0.0.1:55432/portfolio_test'
$env:AI_MODE = 'simulated'
$env:APP_ENV = 'test'
.\.venv\Scripts\python.exe scripts/check_quality.py
```

Runs dependency checks, Ruff, unit tests, real PostgreSQL integration, in-process API tests and HTTP tests against a separate Uvicorn process. Each fixture creates a unique disposable database; it never clears the supplied administrative database. The pipeline stops on failure and rejects skipped/empty mandatory suites. JUnit reports remain in ignored reports/. GitHub Actions uses the same runner and a PostgreSQL service with fictitious credentials. Remote execution has not been performed.

## Design and delivery limits

Python/FastAPI, Pydantic, SQLAlchemy, Alembic and PostgreSQL; dependencies pinned in lock files. A modular monolith separates deterministic rules, provider orchestration and persistence. Registration commits before triage; provider calls hold no database transaction. Strict output/tool validation and persisted leases fence stale results. Reviewers are declared, not authenticated. There is no complete historical text reconstruction or legal audit guarantee.

Docker is unavailable on the validation machine. Compose build/start/restart persistence and remote GitHub CI remain **unverified**. Native Windows checks do not certify Linux containers. See [actual evidence and remaining gates](docs/andamento.md), [Windows guide](docs/10-validacao-local.md), [architecture](docs/04-arquitetura.md), [acceptance traceability](docs/03-backlog.md) and [portfolio/demo](docs/16-demonstracao-e-portfolio.md). Detailed documents are in Portuguese. No publication or deployment has been performed.

AI assistance was used to implement, test and document the project under Eliana's product decisions and review. This assistance is distinct from the application's simulated agent. No claim of real-model classification accuracy is made.
