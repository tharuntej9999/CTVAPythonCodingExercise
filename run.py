"""Application entry point.

Run the Flask application with:
    python run.py

The API will be available at:
    - API endpoints: http://localhost:5000/api/
    - Swagger documentation: http://localhost:5000/api/docs
"""

from src.api import create_app
from src.config import Config

app = create_app(Config)

if __name__ == "__main__":
    print("=" * 80)
    print("Weather Data API Starting...")
    print("API Documentation: http://localhost:5000/api/docs")
    print("Weather Endpoint: http://localhost:5000/api/weather")
    print("Stats Endpoint: http://localhost:5000/api/weather/stats")
    print("=" * 80)
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)
