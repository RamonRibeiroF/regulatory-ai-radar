from sqlalchemy.orm import DeclarativeBase


# Step 1: define the base class inherited by all database models.
class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""