from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from regulatory_ai_radar.database import models  # noqa: F401
from regulatory_ai_radar.database.base import Base


# Step 1: locate the project root from this file.
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Step 2: define the local data directory and database file.
DATA_DIRECTORY = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIRECTORY / "regulatory_ai_radar.db"

# Step 3: create the SQLite connection URL.
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

# Step 4: configure the SQLAlchemy engine.
engine = create_engine(
    DATABASE_URL,
    echo=False,
)

# Step 5: configure the database session factory.
SessionFactory = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def initialize_database() -> None:
    """Create the data directory and all registered database tables."""

    # Step 6: create the local data directory when necessary.
    DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Step 7: create any tables that do not exist yet.
    Base.metadata.create_all(
        bind=engine,
    )