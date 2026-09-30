"""Paramètres centralisés du backend, chargés depuis l'environnement et backend/.env."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Configuration validée du backend, compatible avec le mode démo local."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False

    # Les intégrations restent facultatives pour préserver le démarrage en mode démo.
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_ACCESS_TOKEN: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""

    ML_MODEL_PATH: str = "artifacts/"
    ML_MODEL_VERSION: str = "2.0.0"
    ML_ADMIN_API_KEY: str = ""
    ADMIN_API_KEY: str = ""

    FRONTEND_URL: str = ""
    ALLOWED_ORIGINS: str = ""
    PORT: int = Field(default=8000, ge=1, le=65535)
    ML_MAX_LATENCY_MS: float = Field(default=50.0, gt=0)

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_mode(cls, value: object) -> bool:
        """Interprète aussi les anciens libellés de profil non booléens comme désactivés."""
        if isinstance(value, bool):
            return value
        normalized = str(value).strip().lower()
        if normalized in {"1", "true", "yes", "on", "debug", "development"}:
            return True
        if normalized in {"", "0", "false", "no", "off", "release", "production"}:
            return False
        raise ValueError("DEBUG doit être une valeur booléenne")

    @field_validator("SUPABASE_URL", mode="before")
    @classmethod
    def normalize_supabase_url(cls, value: object) -> str:
        """Accepte une URL HTTPS ou un identifiant de projet Supabase."""
        if value is None:
            return ""
        url = str(value).strip()
        if not url:
            return ""
        if "://" not in url:
            url = f"https://{url}.supabase.co"
        if not url.startswith("https://"):
            raise ValueError("SUPABASE_URL doit commencer par https://")
        return url

    @field_validator("SUPABASE_SERVICE_ROLE_KEY", "GEMINI_API_KEY", mode="before")
    @classmethod
    def validate_optional_secret(cls, value: object) -> str:
        """Valide les clés configurées sans rendre les intégrations obligatoires."""
        secret = "" if value is None else str(value).strip()
        if secret and len(secret) < 20:
            raise ValueError("La clé configurée doit contenir au moins 20 caractères")
        return secret

    @property
    def allowed_origins(self) -> list[str]:
        """Construit la liste CORS à partir des origines locales et configurées."""
        origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
        ]
        if self.FRONTEND_URL.strip():
            origins.append(self.FRONTEND_URL.strip())
        origins.extend(
            origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()
        )
        return list(dict.fromkeys(origins))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Retourne l'instance unique des paramètres."""
    return Settings()


settings = get_settings()
