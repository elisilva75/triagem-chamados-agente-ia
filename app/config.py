from typing import Literal

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", hide_input_in_errors=True)

    app_env: Literal["local", "test"] = "local"
    ai_mode: Literal["simulated"] = "simulated"
    database_url: SecretStr = SecretStr(
        "postgresql+psycopg://portfolio_user:senha_ficticia@localhost:5432/portfolio_chamados"
    )

    @field_validator("database_url")
    @classmethod
    def postgres_only(cls, value: SecretStr) -> SecretStr:
        try:
            url = make_url(value.get_secret_value())
            if url.drivername != "postgresql+psycopg" or not url.database:
                raise ValueError
        except Exception:
            raise ValueError("Configure uma URL PostgreSQL com o driver psycopg.") from None
        return value
