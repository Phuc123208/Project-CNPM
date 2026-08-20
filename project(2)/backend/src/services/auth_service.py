import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from domain.exceptions import ConflictException, UnauthorizedException, ValidationException
from domain.constants import Roles
from infrastructure.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, repository: UserRepository = None):
        self.repository = repository or UserRepository()

    def register(self, full_name, email, password, role="student"):
        if not full_name or not email or not password:
            raise ValidationException("full_name, email and password are required")
        if role not in Roles.ALL:
            role = Roles.STUDENT
        if self.repository.find_by_email(email):
            raise ConflictException("Email already registered")
        password_hash = generate_password_hash(password)
        user = self.repository.create(full_name, email, password_hash, role)
        return user

    def login(self, email, password):
        user = self.repository.find_by_email(email)
        if not user or not check_password_hash(user.password_hash, password):
            raise UnauthorizedException("Invalid email or password")
        return user

    @staticmethod
    def generate_token(user, secret_key, expire_hours=8):
        payload = {
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role,
            "exp": datetime.utcnow() + timedelta(hours=expire_hours),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, secret_key, algorithm="HS256")

    def change_password(self, user_id, old_password, new_password):
        user = self.repository.find_by_id(user_id)
        if not user or not check_password_hash(user.password_hash, old_password):
            raise UnauthorizedException("Old password is incorrect")
        new_hash = generate_password_hash(new_password)
        return self.repository.update(user_id, password_hash=new_hash)
