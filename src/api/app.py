"""Flask application factory and API setup."""

from flask import Flask
from flask_restx import Api

from src.config import Config
from src.models import init_db


def create_app(config_class=Config):
    """Create and configure the Flask application.

    Args:
        config_class: Configuration class to use

    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_db(config_class.DATABASE_URL)

    api = Api(
        app,
        version=config_class.API_VERSION,
        title=config_class.API_TITLE,
        description=config_class.API_DESCRIPTION,
        doc="/api/docs",
        prefix="/api",
    )

    from src.api.weather import api as weather_ns

    api.add_namespace(weather_ns)

    return app
