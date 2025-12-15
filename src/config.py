"""Configuration module for the application."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration class."""

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///weather.db")

    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    TESTING = False

    API_TITLE = os.getenv("API_TITLE", "Weather Data API")
    API_VERSION = os.getenv("API_VERSION", "1.0")
    API_DESCRIPTION = os.getenv("API_DESCRIPTION", "REST API for weather data and statistics")

    DEFAULT_PAGE_SIZE = 100
    MAX_PAGE_SIZE = 1000

    BASE_DIR = Path(__file__).parent.parent
    WX_DATA_DIR = BASE_DIR / "wx_data"
    YLD_DATA_DIR = BASE_DIR / "yld_data"

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s"


class TestConfig(Config):
    """Configuration for testing."""

    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"
