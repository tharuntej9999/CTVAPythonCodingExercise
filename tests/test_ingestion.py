"""Tests for weather data ingestion."""

from datetime import date

import pytest

from src.scripts.ingest_weather import ingest_weather_file, parse_weather_line


class TestParseWeatherLine:
    """Test cases for parsing weather data lines."""

    def test_parse_valid_line(self):
        """Test parsing a valid weather data line."""
        line = "19850101\t  -22\t -128\t   94"
        data = parse_weather_line(line, "USC00110072")

        assert data["station_id"] == "USC00110072"
        assert data["date"] == date(1985, 1, 1)
        assert data["max_temp"] == -22
        assert data["min_temp"] == -128
        assert data["precipitation"] == 94

    def test_parse_line_with_missing_values(self):
        """Test parsing line with missing values (-9999)."""
        line = "19850103\t-9999\t-9999\t-9999"
        data = parse_weather_line(line, "USC00110072")

        assert data["date"] == date(1985, 1, 3)
        assert data["max_temp"] is None
        assert data["min_temp"] is None
        assert data["precipitation"] is None

    def test_parse_line_partial_missing(self):
        """Test parsing line with some missing values."""
        line = "19850103\t -106\t -244\t-9999"
        data = parse_weather_line(line, "USC00110072")

        assert data["max_temp"] == -106
        assert data["min_temp"] == -244
        assert data["precipitation"] is None

    def test_parse_invalid_line_format(self):
        """Test that invalid line format raises ValueError."""
        line = "invalid\tdata"

        with pytest.raises(ValueError):
            parse_weather_line(line, "USC00110072")


class TestIngestWeatherFile:
    """Test cases for file ingestion."""

    def test_ingest_file(self, db_session, temp_weather_file):
        """Test ingesting a weather data file."""
        import logging

        logger = logging.getLogger(__name__)

        inserted, skipped, failed = ingest_weather_file(temp_weather_file, db_session, logger)

        assert inserted == 3
        assert skipped == 0
        assert failed == 0

    def test_ingest_file_duplicate_handling(self, db_session, temp_weather_file):
        """Test that duplicate records are skipped."""
        import logging

        logger = logging.getLogger(__name__)

        inserted1, skipped1, failed1 = ingest_weather_file(temp_weather_file, db_session, logger)
        db_session.commit()

        inserted2, skipped2, failed2 = ingest_weather_file(temp_weather_file, db_session, logger)

        assert inserted1 == 3
        assert skipped1 == 0
        assert inserted2 == 0
        assert skipped2 == 3
