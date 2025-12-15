"""Weather API endpoints.

Provides REST endpoints for accessing weather data and statistics:
- GET /api/weather - Raw weather records
- GET /api/weather/stats - Calculated statistics

Both endpoints support filtering by date and station_id, plus pagination.
"""

from datetime import datetime

from flask import request
from flask_restx import Namespace, Resource, fields

from src.config import Config
from src.models import WeatherRecord, WeatherStats, get_session

api = Namespace("weather", description="Weather data operations")


weather_record_model = api.model(
    "WeatherRecord",
    {
        "id": fields.Integer(description="Record ID"),
        "station_id": fields.String(description="Weather station ID"),
        "date": fields.String(description="Date (YYYY-MM-DD)"),
        "max_temp": fields.Float(description="Maximum temperature (°C)", allow_null=True),
        "min_temp": fields.Float(description="Minimum temperature (°C)", allow_null=True),
        "precipitation": fields.Float(description="Precipitation (mm)", allow_null=True),
    },
)

weather_stats_model = api.model(
    "WeatherStats",
    {
        "id": fields.Integer(description="Stats ID"),
        "station_id": fields.String(description="Weather station ID"),
        "year": fields.Integer(description="Year"),
        "avg_max_temp": fields.Float(
            description="Average maximum temperature (°C)", allow_null=True
        ),
        "avg_min_temp": fields.Float(
            description="Average minimum temperature (°C)", allow_null=True
        ),
        "total_precipitation": fields.Float(
            description="Total precipitation (cm)", allow_null=True
        ),
    },
)

pagination_model = api.model(
    "Pagination",
    {
        "page": fields.Integer(description="Current page number"),
        "page_size": fields.Integer(description="Number of items per page"),
        "total_records": fields.Integer(description="Total number of records"),
        "total_pages": fields.Integer(description="Total number of pages"),
    },
)


def parse_date(date_str: str) -> datetime.date:
    """Parse date string in YYYY-MM-DD format.

    Args:
        date_str: Date string

    Returns:
        date: Parsed date object

    Raises:
        ValueError: If date format is invalid
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format")


def get_pagination_params():
    """Extract and validate pagination parameters from request.

    Returns:
        tuple: (page, page_size)
    """
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", Config.DEFAULT_PAGE_SIZE, type=int)

    if page < 1:
        page = 1
    if page_size < 1:
        page_size = Config.DEFAULT_PAGE_SIZE
    if page_size > Config.MAX_PAGE_SIZE:
        page_size = Config.MAX_PAGE_SIZE

    return page, page_size


def create_paginated_response(records, total_count, page, page_size):
    """Create a paginated response dictionary.

    Args:
        records: List of record dictionaries
        total_count: Total number of records
        page: Current page number
        page_size: Number of items per page

    Returns:
        dict: Paginated response
    """
    total_pages = (total_count + page_size - 1) // page_size

    return {
        "data": records,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_records": total_count,
            "total_pages": total_pages,
        },
    }


@api.route("")
class WeatherList(Resource):
    """Weather records endpoint."""

    @api.doc(
        params={
            "station_id": "Filter by weather station ID",
            "date": "Filter by specific date (YYYY-MM-DD)",
            "start_date": "Filter by start date (YYYY-MM-DD)",
            "end_date": "Filter by end date (YYYY-MM-DD)",
            "page": "Page number (default: 1)",
            "page_size": f"Number of records per page (default: {Config.DEFAULT_PAGE_SIZE}, "
            f"max: {Config.MAX_PAGE_SIZE})",
        }
    )
    def get(self):
        """Get weather records with optional filtering and pagination.

        Returns:
            JSON response with weather records and pagination info
        """

        page, page_size = get_pagination_params()

        station_id = request.args.get("station_id")
        date_str = request.args.get("date")
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")

        with get_session() as session:
            query = session.query(WeatherRecord)

            if station_id:
                query = query.filter(WeatherRecord.station_id == station_id)

            if date_str:
                try:
                    date_obj = parse_date(date_str)
                    query = query.filter(WeatherRecord.date == date_obj)
                except ValueError as e:
                    return {"error": str(e)}, 400

            if start_date_str:
                try:
                    start_date = parse_date(start_date_str)
                    query = query.filter(WeatherRecord.date >= start_date)
                except ValueError as e:
                    return {"error": str(e)}, 400

            if end_date_str:
                try:
                    end_date = parse_date(end_date_str)
                    query = query.filter(WeatherRecord.date <= end_date)
                except ValueError as e:
                    return {"error": str(e)}, 400

            query = query.order_by(WeatherRecord.date, WeatherRecord.station_id)

            total_count = query.count()

            offset = (page - 1) * page_size
            records = query.offset(offset).limit(page_size).all()

            records_data = [record.to_dict() for record in records]

            response = create_paginated_response(records_data, total_count, page, page_size)

            return response


@api.route("/stats")
class WeatherStatsList(Resource):
    """Weather statistics endpoint."""

    @api.doc(
        params={
            "station_id": "Filter by weather station ID",
            "year": "Filter by specific year",
            "start_year": "Filter by start year",
            "end_year": "Filter by end year",
            "page": "Page number (default: 1)",
            "page_size": f"Number of records per page (default: {Config.DEFAULT_PAGE_SIZE}, "
            f"max: {Config.MAX_PAGE_SIZE})",
        }
    )
    def get(self):
        """Get weather statistics with optional filtering and pagination.

        Returns:
            JSON response with weather statistics and pagination info
        """

        page, page_size = get_pagination_params()

        station_id = request.args.get("station_id")
        year = request.args.get("year", type=int)
        start_year = request.args.get("start_year", type=int)
        end_year = request.args.get("end_year", type=int)

        with get_session() as session:
            query = session.query(WeatherStats)

            if station_id:
                query = query.filter(WeatherStats.station_id == station_id)

            if year:
                query = query.filter(WeatherStats.year == year)

            if start_year:
                query = query.filter(WeatherStats.year >= start_year)

            if end_year:
                query = query.filter(WeatherStats.year <= end_year)

            query = query.order_by(WeatherStats.year, WeatherStats.station_id)

            total_count = query.count()

            offset = (page - 1) * page_size
            stats = query.offset(offset).limit(page_size).all()

            stats_data = [stat.to_dict() for stat in stats]

            response = create_paginated_response(stats_data, total_count, page, page_size)

            return response
