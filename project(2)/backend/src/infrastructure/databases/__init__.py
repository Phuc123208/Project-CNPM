from infrastructure.databases.base import Base
from infrastructure.databases.session import engine, SessionLocal, get_session
# Import all ORM models so that Base.metadata is aware of every table
from infrastructure.models import orm_models  # noqa: F401


def init_db(app=None, seed=False):
    """Explicitly create tables and optionally seed reference data.

    Database mutation is deliberately opt-in. Application startup should pass
    the environment-controlled flag rather than calling this unconditionally.
    """
    Base.metadata.create_all(bind=engine)
    if seed:
        from infrastructure.databases.seed import seed_reference_data
        seed_reference_data()

