from infrastructure.databases.session import get_session
from infrastructure.models.orm_models import UserModel


class UserRepository:
    def __init__(self):
        self.session = get_session()

    def find_by_email(self, email):
        return self.session.query(UserModel).filter_by(email=email).first()

    def find_by_id(self, user_id):
        return self.session.query(UserModel).filter_by(user_id=user_id).first()

    def create(self, full_name, email, password_hash, role="student"):
        user = UserModel(full_name=full_name, email=email,
                          password_hash=password_hash, role=role)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def list_all(self, role=None):
        q = self.session.query(UserModel)
        if role:
            q = q.filter_by(role=role)
        return q.order_by(UserModel.user_id).all()

    def update(self, user_id, **fields):
        user = self.find_by_id(user_id)
        if not user:
            return None
        for k, v in fields.items():
            if v is not None and hasattr(user, k):
                setattr(user, k, v)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, user_id):
        user = self.find_by_id(user_id)
        if not user:
            return False
        self.session.delete(user)
        self.session.commit()
        return True
