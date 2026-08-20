from infrastructure.databases.session import get_session
from infrastructure.models.orm_models import ReportModel


class ReportRepository:
    def __init__(self):
        self.session = get_session()

    def create(self, user_id, report_name, format, file_url, experiment_id=None):
        r = ReportModel(user_id=user_id, report_name=report_name, format=format,
                         file_url=file_url, experiment_id=experiment_id)
        self.session.add(r)
        self.session.commit()
        self.session.refresh(r)
        return r

    def list(self, user_id=None):
        q = self.session.query(ReportModel)
        if user_id:
            q = q.filter_by(user_id=user_id)
        return q.order_by(ReportModel.created_at.desc()).all()

    def get(self, report_id):
        return self.session.query(ReportModel).filter_by(report_id=report_id).first()
