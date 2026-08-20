"""Single source of truth for the SQLAlchemy engine/session connected to
Supabase PostgreSQL."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from config import ActiveConfig

engine = create_engine(
    ActiveConfig.DATABASE_URI,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def get_session():
    return SessionLocal()
