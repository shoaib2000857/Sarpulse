from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

API_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Runtime settings, read from environment / .env (prefix SARPULSE_)."""

    model_config = SettingsConfigDict(env_prefix="SARPULSE_", env_file=".env", extra="ignore")

    data_dir: Path = API_ROOT / "fixtures"
    cors_origins: list[str] = ["http://localhost:5173"]

    def resolved_data_dir(self) -> Path:
        return self.data_dir if self.data_dir.is_absolute() else API_ROOT / self.data_dir


settings = Settings()
