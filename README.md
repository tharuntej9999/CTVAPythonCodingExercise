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

# Deployment Approach 
Here is my step by step deployment plan 
1. Database Layeer : using the Amazon RDB and i will enable the automate the backups and Multi-AZ for the high availability
2. API Deployment : Using the AWS Elastic Beanstalk or ECS fragrate and Auto Scaling based on the traffic and application load balancer for the distribution
3. Data Ingestion Pipeline : AWS Lambda for the Injestion Code and Event Bridge for the Scheduling
4. Storage : Using S3 for storing the RAW files
5. Security : Secret Manager for Database Credintails and VPC with private subnets for RDS and IAM roles with least privilege
6. Monitoring : Cloud Watch for the Logs and Metrics
7. CI/CD Pipeline : Using Github Actions and using the blue green deployment stratergy
8. Caching Layer : ElastiCache for frequent queries
9. COST Optimization : using the RDS Reserved Instances
