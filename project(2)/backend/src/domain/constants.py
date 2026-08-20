class Roles:
    ADMIN = "admin"
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    STUDENT = "student"
    ALL = [ADMIN, RESEARCHER, ANALYST, STUDENT]


class DatasetStatus:
    DRAFT = "draft"
    VALIDATED = "validated"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ExperimentStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ModelType:
    ARIMA = "arima"
    PROPHET = "prophet"


class ReportFormat:
    PDF = "pdf"
    EXCEL = "excel"
