"""
Application configuration settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "Contract Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/contract_db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # DocuSign (optional for Phase 1)
    DOCUSIGN_INTEGRATION_KEY: Optional[str] = None
    DOCUSIGN_USER_ID: Optional[str] = None
    DOCUSIGN_ACCOUNT_ID: Optional[str] = None
    DOCUSIGN_PRIVATE_KEY_PATH: Optional[str] = None
    DOCUSIGN_BASE_PATH: str = "https://demo.docusign.net/restapi"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="allow"
    )


settings = Settings()
