"""Pytest configuration and fixtures."""

import os
import tempfile
from datetime import date
from pathlib import Path

import pytest

from src.api import create_app
from src.config import TestConfig
from src.models import WeatherRecord, WeatherStats, get_session, init_db


@pytest.fixture(scope="function")
def app():
    """Create and configure a test Flask application."""
    app = create_app(TestConfig)
    app.config["TESTING"] = True

    yield app


@pytest.fixture(scope="function")
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture(scope="function")
def db_session():
    """Create a clean database session for testing."""

    init_db(TestConfig.DATABASE_URL)

    with get_session() as session:
        yield session


@pytest.fixture
def sample_weather_data(db_session):
    """Insert sample weather data for testing."""
    records = [
        WeatherRecord(
            station_id="USC00110072",
            date=date(1985, 1, 1),
            max_temp=-22,
            min_temp=-128,
            precipitation=94,
        ),
        WeatherRecord(
            station_id="USC00110072",
            date=date(1985, 1, 2),
            max_temp=-122,
            min_temp=-217,
            precipitation=0,
        ),
        WeatherRecord(
            station_id="USC00110072",
            date=date(1985, 1, 3),
            max_temp=-106,
            min_temp=-244,
            precipitation=None,
        ),
        WeatherRecord(
            station_id="USC00110187",
            date=date(1985, 1, 1),
            max_temp=50,
            min_temp=-50,
            precipitation=100,
        ),
        WeatherRecord(
            station_id="USC00110187",
            date=date(1986, 1, 1),
            max_temp=60,
            min_temp=-40,
            precipitation=120,
        ),
    ]

    for record in records:
        db_session.add(record)
    db_session.commit()

    return records


@pytest.fixture
def sample_weather_stats(db_session):
    """Insert sample weather stats for testing."""
    stats = [
        WeatherStats(
            station_id="USC00110072",
            year=1985,
            avg_max_temp=-8.33,
            avg_min_temp=-19.63,
            total_precipitation=0.94,
        ),
        WeatherStats(
            station_id="USC00110187",
            year=1985,
            avg_max_temp=5.0,
            avg_min_temp=-5.0,
            total_precipitation=1.0,
        ),
        WeatherStats(
            station_id="USC00110187",
            year=1986,
            avg_max_temp=6.0,
            avg_min_temp=-4.0,
            total_precipitation=1.2,
        ),
    ]

    for stat in stats:
        db_session.add(stat)
    db_session.commit()

    return stats


@pytest.fixture
def temp_weather_file():
    """Create a temporary weather data file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("19850101\t  -22\t -128\t   94\n")
        f.write("19850102\t -122\t -217\t    0\n")
        f.write("19850103\t -106\t -244\t-9999\n")
        temp_path = f.name

    yield Path(temp_path)

    os.unlink(temp_path)
