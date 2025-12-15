# Coding Challenge Answers

## Problem 1 - Data Modeling

**Database:** SQLite (PostgreSQL supported via config)
**ORM:** SQLAlchemy

### WeatherRecord Model
```python
class WeatherRecord(Base):
    __tablename__ = "weather_records"
    id = Column(Integer, primary_key=True)
    station_id = Column(String(50), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    max_temp = Column(Integer, nullable=True)
    min_temp = Column(Integer, nullable=True)
    precipitation = Column(Integer, nullable=True)
    __table_args__ = (UniqueConstraint("station_id", "date"),)
```

### WeatherStats Model
```python
class WeatherStats(Base):
    __tablename__ = "weather_stats"
    id = Column(Integer, primary_key=True)
    station_id = Column(String(50), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    avg_max_temp = Column(Float, nullable=True)
    avg_min_temp = Column(Float, nullable=True)
    total_precipitation = Column(Float, nullable=True)
    __table_args__ = (UniqueConstraint("station_id", "year"),)
```

## Problem 2 - Ingestion

**File:** `src/scripts/ingest_weather.py`

- Processes 167 weather station files
- Converts -9999 to NULL
- Duplicate detection via unique constraints
- Comprehensive logging with timestamps
- Idempotent execution

**Run:** `python -m src.scripts.ingest_weather`

## Problem 3 - Data Analysis

**File:** `src/scripts/calculate_stats.py`

- Calculates annual averages and totals per station
- Handles NULL values in aggregations
- Unit conversions (tenths → standard units)

**Run:** `python -m src.scripts.calculate_stats`

## Problem 4 - REST API

**Files:** `src/api/app.py`, `src/api/weather.py`

- Flask + Flask-RESTX framework
- GET /api/weather - Records endpoint
- GET /api/weather/stats - Statistics endpoint
- GET /api/docs - Swagger documentation
- Filtering by station_id, date, year
- Pagination support

**Run:** `python run.py`

## Testing

29 tests, 61% coverage

```bash
pytest -v --cov=src
```
