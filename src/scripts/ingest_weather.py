"""Weather data ingestion script.

This script ingests weather data from text files in the wx_data directory
into the database. It handles duplicate detection, missing values, and
provides detailed logging of the ingestion process.

Usage:
    python -m src.scripts.ingest_weather
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

import colorlog
from sqlalchemy import exc

from src.config import Config
from src.models import WeatherRecord, get_session, init_db


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


def parse_weather_line(line: str, station_id: str) -> dict:
    """Parse a single line of weather data.

    Args:
        line: Tab-separated line with date, max_temp, min_temp, precipitation
        station_id: Station identifier from filename

    Returns:
        dict: Parsed weather data with None for missing values

    Raises:
        ValueError: If line cannot be parsed
    """
    parts = line.strip().split("\t")
    if len(parts) != 4:
        raise ValueError(f"Expected 4 fields, got {len(parts)}")

    date_str, max_temp_str, min_temp_str, precip_str = parts

    date_obj = datetime.strptime(date_str, "%Y%m%d").date()

    def parse_value(value_str: str) -> int:
        value = int(value_str.strip())
        return None if value == -9999 else value

    max_temp = parse_value(max_temp_str)
    min_temp = parse_value(min_temp_str)
    precipitation = parse_value(precip_str)

    return {
        "station_id": station_id,
        "date": date_obj,
        "max_temp": max_temp,
        "min_temp": min_temp,
        "precipitation": precipitation,
    }


def ingest_weather_file(file_path: Path, session, logger: logging.Logger) -> tuple:
    """Ingest weather data from a single file.

    Args:
        file_path: Path to weather data file
        session: Database session
        logger: Logger instance

    Returns:
        tuple: (records_inserted, records_skipped, records_failed)
    """

    station_id = file_path.stem

    inserted = 0
    skipped = 0
    failed = 0

    logger.debug(f"Processing file: {file_path.name}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                if not line.strip():
                    continue

                try:
                    data = parse_weather_line(line, station_id)
                    record = WeatherRecord(**data)

                    session.add(record)
                    session.flush()
                    inserted += 1

                except exc.IntegrityError:
                    session.rollback()
                    skipped += 1

                except ValueError as e:
                    logger.warning(f"Skipping invalid line {line_num} in {file_path.name}: {e}")
                    failed += 1
                    continue

    except Exception as e:
        logger.error(f"Error processing file {file_path.name}: {e}")
        raise

    return inserted, skipped, failed


def ingest_all_weather_data(data_dir: Path = None):
    """Ingest all weather data files from the wx_data directory.

    Args:
        data_dir: Directory containing weather data files.
                  If None, uses Config.WX_DATA_DIR
    """
    logger = logging.getLogger(__name__)

    data_dir = data_dir or Config.WX_DATA_DIR

    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        sys.exit(1)

    weather_files = sorted(data_dir.glob("*.txt"))

    if not weather_files:
        logger.warning(f"No weather data files found in {data_dir}")
        return

    logger.info(f"Found {len(weather_files)} weather data files to process")
    logger.info("=" * 80)

    start_time = datetime.now()
    logger.info(f"Ingestion started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    total_inserted = 0
    total_skipped = 0
    total_failed = 0

    with get_session() as session:
        for file_path in weather_files:
            try:
                inserted, skipped, failed = ingest_weather_file(file_path, session, logger)
                total_inserted += inserted
                total_skipped += skipped
                total_failed += failed

                if inserted > 0:
                    logger.debug(
                        f"  {file_path.name}: {inserted} inserted, "
                        f"{skipped} skipped (duplicates), {failed} failed"
                    )

                session.commit()

            except Exception as e:
                logger.error(f"Failed to process {file_path.name}: {e}")
                session.rollback()
                continue

    end_time = datetime.now()
    duration = end_time - start_time

    logger.info("=" * 80)
    logger.info(f"Ingestion completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Duration: {duration}")
    logger.info(f"Total records inserted: {total_inserted:,}")
    logger.info(f"Total records skipped (duplicates): {total_skipped:,}")
    logger.info(f"Total records failed: {total_failed:,}")
    logger.info(f"Total files processed: {len(weather_files)}")
    logger.info("=" * 80)

    if total_failed > 0:
        logger.warning(f"{total_failed} records failed to process - check logs above")


def main():
    """Main entry point for the ingestion script."""
    setup_logging(Config.LOG_LEVEL)
    logger = logging.getLogger(__name__)

    logger.info("Initializing database...")
    init_db()

    logger.info("Starting weather data ingestion...")
    ingest_all_weather_data()

    logger.info("Ingestion process complete!")


if __name__ == "__main__":
    main()
