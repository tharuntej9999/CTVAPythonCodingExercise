"""Weather data models.

This module defines the ORM models for weather data storage:
- WeatherRecord: Raw weather data from weather stations
- WeatherStats: Calculated annual statistics per station
"""

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    Float,
    Index,
    Integer,
    String,
    UniqueConstraint,
)

from src.models.base import Base


class WeatherRecord(Base):
    """Model for individual weather data records.

    Represents daily weather measurements from a specific weather station.
    Temperatures are stored in tenths of degrees Celsius.
    Precipitation is stored in tenths of millimeters.
    Missing values (-9999 in raw data) are stored as NULL.

    Attributes:
        id: Primary key
        station_id: Weather station identifier (e.g., 'USC00110072')
        date: Date of measurement (YYYY-MM-DD)
        max_temp: Maximum temperature in tenths of degrees Celsius (NULL if missing)
        min_temp: Minimum temperature in tenths of degrees Celsius (NULL if missing)
        precipitation: Precipitation in tenths of millimeters (NULL if missing)
    """

    __tablename__ = "weather_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String(50), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    max_temp = Column(Integer, nullable=True)
    min_temp = Column(Integer, nullable=True)
    precipitation = Column(Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("station_id", "date", name="uq_station_date"),
        Index("ix_station_date", "station_id", "date"),
    )

    def __repr__(self):
        return (
            f"<WeatherRecord(station_id='{self.station_id}', "
            f"date={self.date}, max_temp={self.max_temp})>"
        )

    def to_dict(self):
        """Convert record to dictionary for API responses.

        Returns:
            dict: Dictionary representation with temperatures in degrees Celsius
                  and precipitation in millimeters
        """
        return {
            "id": self.id,
            "station_id": self.station_id,
            "date": self.date.isoformat(),
            "max_temp": self.max_temp / 10.0 if self.max_temp is not None else None,
            "min_temp": self.min_temp / 10.0 if self.min_temp is not None else None,
            "precipitation": (
                self.precipitation / 10.0 if self.precipitation is not None else None
            ),
        }


class WeatherStats(Base):
    """Model for calculated annual weather statistics per station.

    Stores yearly aggregated statistics for each weather station.
    All statistics ignore missing values (NULL) in the source data.

    Attributes:
        id: Primary key
        station_id: Weather station identifier
        year: Year for which statistics are calculated
        avg_max_temp: Average maximum temperature in degrees Celsius (NULL if no data)
        avg_min_temp: Average minimum temperature in degrees Celsius (NULL if no data)
        total_precipitation: Total precipitation in centimeters (NULL if no data)
    """

    __tablename__ = "weather_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(String(50), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    avg_max_temp = Column(Float, nullable=True)
    avg_min_temp = Column(Float, nullable=True)
    total_precipitation = Column(Float, nullable=True)

    __table_args__ = (
        UniqueConstraint("station_id", "year", name="uq_station_year"),
        Index("ix_station_year", "station_id", "year"),
        CheckConstraint("year >= 1900 AND year <= 2100", name="ck_year_range"),
    )

    def __repr__(self):
        return (
            f"<WeatherStats(station_id='{self.station_id}', "
            f"year={self.year}, avg_max_temp={self.avg_max_temp})>"
        )

    def to_dict(self):
        """Convert stats to dictionary for API responses.

        Returns:
            dict: Dictionary representation of statistics
        """
        return {
            "id": self.id,
            "station_id": self.station_id,
            "year": self.year,
            "avg_max_temp": (
                round(self.avg_max_temp, 2) if self.avg_max_temp is not None else None
            ),
            "avg_min_temp": (
                round(self.avg_min_temp, 2) if self.avg_min_temp is not None else None
            ),
            "total_precipitation": (
                round(self.total_precipitation, 2) if self.total_precipitation is not None else None
            ),
        }
