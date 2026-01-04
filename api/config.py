"""Application configuration."""

from pathlib import Path


class Settings:
    """Application settings."""
    # Project paths
    TEMPLATES_DIR: Path = Path(__file__).parent.parent / "templates"
    # API configuration
    API_BASE_URL: str = "/api/v1"


settings = Settings()
