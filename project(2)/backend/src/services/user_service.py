from werkzeug.security import generate_password_hash
from domain.exceptions import NotFoundException
from infrastructure.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository = None):
        self.repository = repository or UserRepository()

    def get_profile(self, user_id):
        user = self.repository.find_by_id(user_id)
        if not user:
            raise NotFoundException("User not found")
        return user

    def update_profile(self, user_id, full_name=None, email=None):
        user = self.repository.update(user_id, full_name=full_name, email=email)
        if not user:
            raise NotFoundException("User not found")
        return user

    def list_users(self, role=None):
        return self.repository.list_all(role)

    def create_user(self, full_name, email, password, role):
        password_hash = generate_password_hash(password)
        return self.repository.create(full_name, email, password_hash, role)

    def update_user(self, user_id, **fields):
        if fields.get("password"):
            fields["password_hash"] = generate_password_hash(fields.pop("password"))
        user = self.repository.update(user_id, **fields)
        if not user:
            raise NotFoundException("User not found")
        return user

    def delete_user(self, user_id):
        ok = self.repository.delete(user_id)
        if not ok:
            raise NotFoundException("User not found")
        return ok

    def assign_role(self, user_id, role):
        user = self.repository.update(user_id, role=role)
        if not user:
            raise NotFoundException("User not found")
        return user
