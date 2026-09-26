
"""
MedExplain AI - Database Initialization

Creates all registered database tables.
"""

from app.database.base import Base
from app.database.session import engine

# Import every model so SQLAlchemy knows about the tables.
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.prediction import Prediction
from app.models.report import Report


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables initialized successfully.")
