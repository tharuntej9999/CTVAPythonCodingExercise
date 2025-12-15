# Weather Data API - Solution

## Complete Solution for Corteva Coding Challenge

### Files Structure
```
weather-challenge/
├── src/
│   ├── models/
│   │   ├── base.py
│   │   └── weather.py
│   ├── scripts/
│   │   ├── ingest_weather.py
│   │   └── calculate_stats.py
│   ├── api/
│   │   ├── app.py
│   │   └── weather.py
│   └── config.py
├── tests/
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_ingestion.py
│   └── test_api.py
├── wx_data/
├── README.md
├── ANSWERS.md
├── QUICKSTART.md
├── PROJECT_SUMMARY.md
├── requirements.txt
└── run.py
```

### Solutions

**Problem 1:** Database models in `src/models/weather.py`
**Problem 2:** Ingestion in `src/scripts/ingest_weather.py`
**Problem 3:** Statistics in `src/scripts/calculate_stats.py`
**Problem 4:** REST API in `src/api/`

### Quick Start
```bash
pip install -r requirements.txt
pytest -v
python -m src.scripts.ingest_weather
python -m src.scripts.calculate_stats
python run.py
```

### Test Results
- 29/29 tests passed
- 61% coverage
- All code formatted and linted

### API Access
http://localhost:5000/api/docs
