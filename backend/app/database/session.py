"""
MedExplain AI - Database Session

Creates the SQLAlchemy engine and database session factory.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """
    Provide a database session for FastAPI endpoints.

    The session is automatically closed after the request.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()