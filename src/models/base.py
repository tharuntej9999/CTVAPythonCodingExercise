"""Database base configuration and session management."""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import Config

Base = declarative_base()


_engine = None
_SessionLocal = None


def init_db(database_url: str = None):
    """Initialize the database engine and session factory.

    Args:
        database_url: Database URL. If None, uses Config.DATABASE_URL
    """
    global _engine, _SessionLocal

    url = database_url or Config.DATABASE_URL
    _engine = create_engine(url, echo=Config.DEBUG)
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

    from src.models import weather  # noqa: F401

    Base.metadata.create_all(bind=_engine)


def get_engine():
    """Get the database engine."""
    if _engine is None:
        init_db()
    return _engine


def get_session_factory():
    """Get the session factory."""
    if _SessionLocal is None:
        init_db()
    return _SessionLocal


@contextmanager
def get_session():
    """Context manager for database sessions.

    Yields:
        Session: SQLAlchemy session

    Example:
        with get_session() as session:
            records = session.query(WeatherRecord).all()
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
        if session.is_active:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
