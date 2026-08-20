class User:
    def __init__(self, full_name, email, password_hash=None, role="student",
                 user_id=None, created_at=None):
        self.user_id = user_id
        self.full_name = full_name
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.created_at = created_at

    def to_public_dict(self):
        return {
            "user_id": self.user_id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
