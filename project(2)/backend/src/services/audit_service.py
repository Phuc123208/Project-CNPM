from infrastructure.repositories.audit_repository import AuditRepository


class AuditService:
    def __init__(self, repository: AuditRepository = None):
        self.repository = repository or AuditRepository()

    def log(self, user_id, action, resource_type=None, resource_id=None, details=None):
        try:
            return self.repository.log(user_id, action, resource_type, resource_id, details)
        except Exception as e:
            # Auditing must never break the main request flow
            print(f"[audit] failed to log '{action}': {e}")
            return None

    def list_logs(self, limit=200):
        return self.repository.list(limit=limit)
