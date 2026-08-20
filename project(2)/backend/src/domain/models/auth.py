class Auth:
    def __init__(self, email: str, password: str, full_name: str = None, role: str = "student"):
        self.email = email
        self.password = password
        self.full_name = full_name
        self.role = role
        self.user_id = None
