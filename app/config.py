from typing import Literal

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", hide_input_in_errors=True)

    app_env: Literal["local", "test"] = "local"
    ai_mode: Literal["simulated", "openai", "groq"] = "simulated"
    openai_api_key: SecretStr | None = None
    openai_model: str | None = None
    groq_api_key: SecretStr | None = None
    groq_model: str | None = None

    @model_validator(mode="after")
    def explicit_provider(self):
        if self.ai_mode == "openai" and (
            not self.openai_api_key
            or not self.openai_api_key.get_secret_value().strip()
            or not self.openai_model
            or not self.openai_model.strip()
        ):
            raise ValueError("AI_MODE=openai exige OPENAI_API_KEY e OPENAI_MODEL não vazios.")
        if self.openai_model is not None:
            self.openai_model = self.openai_model.strip()
            if len(self.openai_model) > 200:
                raise ValueError("OPENAI_MODEL deve ter até 200 caracteres.")
        if self.groq_model is not None:
            self.groq_model = self.groq_model.strip()
            if len(self.groq_model) > 200:
                raise ValueError("GROQ_MODEL deve ter até 200 caracteres.")
        if self.ai_mode == "groq" and (
            not self.groq_api_key
            or not self.groq_api_key.get_secret_value().strip()
            or not self.groq_model
        ):
            raise ValueError("AI_MODE=groq exige GROQ_API_KEY e GROQ_MODEL não vazios.")
        return self

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
