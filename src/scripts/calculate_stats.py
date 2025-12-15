"""Weather statistics calculation script.

This script calculates annual weather statistics for each weather station:
- Average maximum temperature (degrees Celsius)
- Average minimum temperature (degrees Celsius)
- Total accumulated precipitation (centimeters)

Missing values are ignored when calculating statistics.

Usage:
    python -m src.scripts.calculate_stats
"""

import logging
from datetime import datetime

import colorlog
from sqlalchemy import extract, func

from src.config import Config
from src.models import WeatherRecord, WeatherStats, get_session, init_db


def setup_logging(log_level: str = "INFO"):
    """Configure colored logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
    )

    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(log_level)


def calculate_weather_stats():
    """Calculate annual weather statistics for all stations.

    For each year and station combination:
    - Calculates average maximum temperature (Celsius)
    - Calculates average minimum temperature (Celsius)
    - Calculates total precipitation (centimeters)

    Missing values (NULL) are ignored in calculations.
    If no valid data exists for a metric, NULL is stored.
    """
    logger = logging.getLogger(__name__)

    start_time = datetime.now()
    logger.info("=" * 80)
    logger.info(f"Statistics calculation started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    stats_inserted = 0
    stats_updated = 0

    with get_session() as session:
        station_years = (
            session.query(
                WeatherRecord.station_id, extract("year", WeatherRecord.date).label("year")
            )
            .distinct()
            .order_by(WeatherRecord.station_id, "year")
            .all()
        )

        logger.info(f"Found {len(station_years)} station-year combinations to process")

        for station_id, year in station_years:
            year = int(year)

            stats = (
                session.query(
                    func.avg(WeatherRecord.max_temp).label("avg_max_temp"),
                    func.avg(WeatherRecord.min_temp).label("avg_min_temp"),
                    func.sum(WeatherRecord.precipitation).label("total_precipitation"),
                )
                .filter(
                    WeatherRecord.station_id == station_id,
                    extract("year", WeatherRecord.date) == year,
                )
                .first()
            )

            avg_max_temp = stats.avg_max_temp / 10.0 if stats.avg_max_temp is not None else None
            avg_min_temp = stats.avg_min_temp / 10.0 if stats.avg_min_temp is not None else None

            total_precipitation = (
                stats.total_precipitation / 100.0 if stats.total_precipitation is not None else None
            )

            existing_stat = (
                session.query(WeatherStats)
                .filter(WeatherStats.station_id == station_id, WeatherStats.year == year)
                .first()
            )

            if existing_stat:
                existing_stat.avg_max_temp = avg_max_temp
                existing_stat.avg_min_temp = avg_min_temp
                existing_stat.total_precipitation = total_precipitation
                stats_updated += 1
            else:
                new_stat = WeatherStats(
                    station_id=station_id,
                    year=year,
                    avg_max_temp=avg_max_temp,
                    avg_min_temp=avg_min_temp,
                    total_precipitation=total_precipitation,
                )
                session.add(new_stat)
                stats_inserted += 1

            if (stats_inserted + stats_updated) % 100 == 0:
                session.commit()
                logger.debug(
                    f"Progress: {stats_inserted + stats_updated} stats processed "
                    f"({stats_inserted} inserted, {stats_updated} updated)"
                )

        session.commit()

    end_time = datetime.now()
    duration = end_time - start_time

    logger.info("=" * 80)
    logger.info(f"Statistics calculation completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Duration: {duration}")
    logger.info(f"Total statistics inserted: {stats_inserted:,}")
    logger.info(f"Total statistics updated: {stats_updated:,}")
    logger.info(f"Total statistics processed: {stats_inserted + stats_updated:,}")
    logger.info("=" * 80)


def main():
    """Main entry point for the statistics calculation script."""
    setup_logging(Config.LOG_LEVEL)
    logger = logging.getLogger(__name__)

    logger.info("Initializing database...")
    init_db()

    logger.info("Starting weather statistics calculation...")
    calculate_weather_stats()

    logger.info("Statistics calculation complete!")


if __name__ == "__main__":
    main()
