# Quick Start Guide

## Install
```bash
cd weather-challenge
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Test
```bash
pytest -v
```

## Run
```bash
python -m src.scripts.ingest_weather
python -m src.scripts.calculate_stats
python run.py
```

Access API: http://localhost:5000/api/docs

## Examples
```bash
curl http://localhost:5000/api/weather?station_id=USC00110072
curl http://localhost:5000/api/weather/stats?year=1985
```
