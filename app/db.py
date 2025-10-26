import os
from sqlmodel import SQLModel, create_engine, Session

# Where to store the SQLite file. In Docker we’ll mount /data; in local dev you
# can override with DB_PATH=./app.db or leave default.
DB_PATH = os.getenv("DB_PATH", "/data/app.db")

# SQLAlchemy URL. For SQLite, it's sqlite:/// + absolute/relative path.
DATABASE_URL = f"sqlite:///{DB_PATH}"

# check_same_thread=False lets multiple threads share the same connection pool
# (FastAPI uses multiple worker threads). Safe for SQLite in this context.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def init_db() -> None:
    """
    Create all tables if they don't exist.
    Call this once on app startup (see app.main).
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    FastAPI dependency that yields a short-lived DB session per request.
    Guaranteed cleanup thanks to 'yield' + 'with'.
    """
    with Session(engine) as session:
        yield session
