"""Tests for database models."""

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from src.models import WeatherRecord, WeatherStats


class TestWeatherRecord:
    """Test cases for WeatherRecord model."""

    def test_create_weather_record(self, db_session):
        """Test creating a weather record."""
        record = WeatherRecord(
            station_id="USC00110072",
            date=date(1985, 1, 1),
            max_temp=-22,
            min_temp=-128,
            precipitation=94,
        )
        db_session.add(record)
        db_session.commit()

        assert record.id is not None
        assert record.station_id == "USC00110072"
        assert record.date == date(1985, 1, 1)
        assert record.max_temp == -22
        assert record.min_temp == -128
        assert record.precipitation == 94

    def test_weather_record_with_missing_values(self, db_session):
        """Test creating a weather record with missing values."""
        record = WeatherRecord(
            station_id="USC00110072",
            date=date(1985, 1, 1),
            max_temp=None,
            min_temp=None,
            precipitation=None,
        )
        db_session.add(record)
        db_session.commit()

        assert record.max_temp is None
        assert record.min_temp is None
        assert record.precipitation is None

    def test_duplicate_record_constraint(self, db_session):
        """Test that duplicate records are prevented."""
        record1 = WeatherRecord(
            station_id="USC00110072",
            date=date(1985, 1, 1),
            max_temp=-22,
            min_temp=-128,
            precipitation=94,
        )
        db_session.add(record1)
        db_session.commit()

        record2 = WeatherRecord(
            station_id="USC00110072",
            date=date(1985, 1, 1),
            max_temp=-22,
            min_temp=-128,
            precipitation=94,
        )
        db_session.add(record2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_to_dict_conversion(self, db_session):
        """Test converting record to dictionary."""
        record = WeatherRecord(
            station_id="USC00110072",
            date=date(1985, 1, 1),
            max_temp=-22,
            min_temp=-128,
            precipitation=94,
        )
        db_session.add(record)
        db_session.commit()

        data = record.to_dict()
        assert data["station_id"] == "USC00110072"
        assert data["date"] == "1985-01-01"
        assert data["max_temp"] == -2.2
        assert data["min_temp"] == -12.8
        assert data["precipitation"] == 9.4


class TestWeatherStats:
    """Test cases for WeatherStats model."""

    def test_create_weather_stats(self, db_session):
        """Test creating weather statistics."""
        stats = WeatherStats(
            station_id="USC00110072",
            year=1985,
            avg_max_temp=-8.33,
            avg_min_temp=-19.63,
            total_precipitation=0.94,
        )
        db_session.add(stats)
        db_session.commit()

        assert stats.id is not None
        assert stats.station_id == "USC00110072"
        assert stats.year == 1985
        assert abs(stats.avg_max_temp - (-8.33)) < 0.01
        assert abs(stats.avg_min_temp - (-19.63)) < 0.01
        assert abs(stats.total_precipitation - 0.94) < 0.01

    def test_stats_with_null_values(self, db_session):
        """Test creating stats with NULL values."""
        stats = WeatherStats(
            station_id="USC00110072",
            year=1985,
            avg_max_temp=None,
            avg_min_temp=None,
            total_precipitation=None,
        )
        db_session.add(stats)
        db_session.commit()

        assert stats.avg_max_temp is None
        assert stats.avg_min_temp is None
        assert stats.total_precipitation is None

    def test_duplicate_stats_constraint(self, db_session):
        """Test that duplicate stats are prevented."""
        stats1 = WeatherStats(
            station_id="USC00110072",
            year=1985,
            avg_max_temp=-8.33,
            avg_min_temp=-19.63,
            total_precipitation=0.94,
        )
        db_session.add(stats1)
        db_session.commit()

        stats2 = WeatherStats(
            station_id="USC00110072",
            year=1985,
            avg_max_temp=-8.33,
            avg_min_temp=-19.63,
            total_precipitation=0.94,
        )
        db_session.add(stats2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_to_dict_conversion(self, db_session):
        """Test converting stats to dictionary."""
        stats = WeatherStats(
            station_id="USC00110072",
            year=1985,
            avg_max_temp=-8.333333,
            avg_min_temp=-19.6285,
            total_precipitation=0.9444,
        )
        db_session.add(stats)
        db_session.commit()

        data = stats.to_dict()
        assert data["station_id"] == "USC00110072"
        assert data["year"] == 1985

        assert data["avg_max_temp"] == -8.33
        assert data["avg_min_temp"] == -19.63
        assert data["total_precipitation"] == 0.94
