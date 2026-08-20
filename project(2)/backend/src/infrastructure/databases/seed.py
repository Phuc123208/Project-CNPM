"""Seed reference/demo data: one account per role so the grader can log in
immediately (email / password shown below)."""
from werkzeug.security import generate_password_hash
from infrastructure.databases.session import get_session
from infrastructure.models.orm_models import UserModel

DEFAULT_ACCOUNTS = [
    ("Administrator", "admin@traffic.edu.vn", "Admin@123", "admin"),
    ("Nguyen Researcher", "researcher@traffic.edu.vn", "Research@123", "researcher"),
    ("Tran Analyst", "analyst@traffic.edu.vn", "Analyst@123", "analyst"),
    ("Le Student", "student@traffic.edu.vn", "Student@123", "student"),
]


def seed_reference_data():
    session = get_session()
    try:
        for full_name, email, password, role in DEFAULT_ACCOUNTS:
            existing = session.query(UserModel).filter_by(email=email).first()
            if not existing:
                user = UserModel(
                    full_name=full_name,
                    email=email,
                    password_hash=generate_password_hash(password),
                    role=role,
                )
                session.add(user)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"[seed] Warning: could not seed reference data: {e}")
    finally:
        session.close()
