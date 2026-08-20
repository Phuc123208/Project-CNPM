class AuditLog:
    def __init__(self, user_id, action, resource_type=None, resource_id=None,
                 details=None, log_id=None, created_at=None):
        self.log_id = log_id
        self.user_id = user_id
        self.action = action
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.details = details or {}
        self.created_at = created_at
