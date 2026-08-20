from infrastructure.databases.session import get_session
from infrastructure.models.orm_models import AuditLogModel


class AuditRepository:
    def __init__(self):
        self.session = get_session()

    def log(self, user_id, action, resource_type=None, resource_id=None, details=None):
        entry = AuditLogModel(user_id=user_id, action=action, resource_type=resource_type,
                               resource_id=str(resource_id) if resource_id is not None else None,
                               details=details or {})
        self.session.add(entry)
        self.session.commit()
        return entry

    def list(self, limit=200):
        return (self.session.query(AuditLogModel)
                .order_by(AuditLogModel.created_at.desc()).limit(limit).all())
