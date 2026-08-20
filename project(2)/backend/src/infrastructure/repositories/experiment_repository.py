from infrastructure.databases.session import get_session
from infrastructure.models.orm_models import ExperimentModel, ForecastResultModel


class ExperimentRepository:
    def __init__(self):
        self.session = get_session()

    def create(self, user_id, version_id, name, model_type, parameters=None, random_seed=42):
        exp = ExperimentModel(
            user_id=user_id, version_id=version_id, name=name, model_type=model_type,
            parameters=parameters or {}, status="pending", random_seed=random_seed,
        )
        self.session.add(exp)
        self.session.commit()
        self.session.refresh(exp)
        return exp

    def get(self, experiment_id):
        return self.session.query(ExperimentModel).filter_by(experiment_id=experiment_id).first()

    def list(self, user_id=None, version_id=None):
        q = self.session.query(ExperimentModel)
        if user_id:
            q = q.filter_by(user_id=user_id)
        if version_id:
            q = q.filter_by(version_id=version_id)
        return q.order_by(ExperimentModel.created_at.desc()).all()

    def update_status(self, experiment_id, status, evaluation_metrics=None):
        exp = self.get(experiment_id)
        if not exp:
            return None
        exp.status = status
        if evaluation_metrics is not None:
            exp.evaluation_metrics = evaluation_metrics
        self.session.commit()
        self.session.refresh(exp)
        return exp

    def save_forecast_results(self, results):
        for r in results:
            self.session.add(r)
        self.session.commit()

    def get_forecast_results(self, experiment_id):
        return (self.session.query(ForecastResultModel)
                .filter_by(experiment_id=experiment_id)
                .order_by(ForecastResultModel.forecast_time).all())

    def clear_forecast_results(self, experiment_id):
        self.session.query(ForecastResultModel).filter_by(experiment_id=experiment_id).delete()
        self.session.commit()
