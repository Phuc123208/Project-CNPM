from infrastructure.databases.base import Base
from infrastructure.databases.session import engine, SessionLocal, get_session
# Import all ORM models so that Base.metadata is aware of every table
from infrastructure.models import orm_models  # noqa: F401


def init_db(app=None):
    """Create all tables in the connected PostgreSQL (Supabase) database
    if they do not already exist, then seed reference data."""
    Base.metadata.create_all(bind=engine)
    from infrastructure.databases.seed import seed_reference_data
    seed_reference_data()
