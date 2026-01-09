"""Application configuration."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings."""
    # Project paths
    TEMPLATES_DIR: Path = Path(__file__).parent.parent / "templates"
    # API configuration
    API_BASE_URL: str = "/api/v1"
    
    # Analytics configuration
    PLAUSIBLE_DOMAIN: str = os.getenv("PLAUSIBLE_DOMAIN", "")
    PLAUSIBLE_API_TOKEN: str = os.getenv("PLAUSIBLE_API_TOKEN", "")


settings = Settings()
