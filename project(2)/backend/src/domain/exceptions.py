class CustomException(Exception):
    pass


class NotFoundException(CustomException):
    def __init__(self, message="Resource not found"):
        self.message = message
        super().__init__(self.message)


class ValidationException(CustomException):
    def __init__(self, message="Validation error"):
        self.message = message
        super().__init__(self.message)


class UnauthorizedException(CustomException):
    def __init__(self, message="Unauthorized access"):
        self.message = message
        super().__init__(self.message)


class ForbiddenException(CustomException):
    def __init__(self, message="You do not have permission to perform this action"):
        self.message = message
        super().__init__(self.message)


class ConflictException(CustomException):
    def __init__(self, message="Conflict occurred"):
        self.message = message
        super().__init__(self.message)
