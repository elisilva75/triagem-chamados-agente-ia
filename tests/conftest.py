import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url

from app.config import Settings
from app.main import create_app

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def database_url():
    """Cria banco exclusivo; nunca limpa banco recebido do ambiente."""
    raw = os.environ.get("TEST_DATABASE_URL")
    if not raw:
        pytest.skip("PostgreSQL real requer TEST_DATABASE_URL (banco administrativo de teste).")
    url = make_url(raw)
    if (
        url.drivername != "postgresql+psycopg"
        or url.host not in ("localhost", "127.0.0.1")
        or not url.database
        or not url.database.startswith("portfolio_test")
    ):
        pytest.fail("TEST_DATABASE_URL deve apontar para PostgreSQL local portfolio_test*.")
    name = "portfolio_test_" + uuid4().hex
    admin = create_engine(url, isolation_level="AUTOCOMMIT", hide_parameters=True)
    with admin.connect() as connection:
        connection.exec_driver_sql(f'CREATE DATABASE "{name}"')
    test_url = url.set(database=name).render_as_string(hide_password=False)
    try:
        yield test_url
    finally:
        # name é gerado aqui, validado por construção; nunca é o banco de entrada.
        with admin.connect() as connection:
            connection.exec_driver_sql(f'DROP DATABASE "{name}" WITH (FORCE)')
        admin.dispose()


def migrate(url, *args):
    env = {**os.environ, "DATABASE_URL": url, "AI_MODE": "simulated", "APP_ENV": "test"}
    subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def migrated_url(database_url):
    migrate(database_url, "upgrade", "head")
    return database_url


@pytest.fixture
def client(migrated_url):
    app = create_app(Settings(_env_file=None, database_url=migrated_url))
    with TestClient(app) as test_client:
        yield test_client
