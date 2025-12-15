# Weather Data API

REST API for weather data ingestion, analysis, and retrieval built with Flask, SQLAlchemy, and SQLite/PostgreSQL.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

## Usage

### Ingest Data
```bash
python -m src.scripts.ingest_weather
```

### Calculate Statistics
```bash
python -m src.scripts.calculate_stats
```

### Start API
```bash
python run.py
```
Access Swagger UI: http://localhost:5000/api/docs

## API Endpoints

**GET /api/weather** - Weather records with filtering (station_id, date, start_date, end_date) and pagination

**GET /api/weather/stats** - Statistics with filtering (station_id, year, start_year, end_year) and pagination

## Database Schema

### WeatherRecord
- station_id, date, max_temp, min_temp, precipitation
- Unique constraint on (station_id, date)

### WeatherStats
- station_id, year, avg_max_temp, avg_min_temp, total_precipitation
- Unique constraint on (station_id, year)

## Testing

```bash
pytest --cov=src --cov-report=html
```

## Code Quality

```bash
black src/ tests/
flake8 src/ tests/
isort src/ tests/
```
