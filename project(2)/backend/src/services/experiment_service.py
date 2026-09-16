"""Module 5 - Experiment Management. Ties dataset version + model
configuration + parameters + evaluation metrics together for reproducibility
(RQ3, Reproducibility non-functional requirement)."""
from datetime import datetime
from domain.exceptions import NotFoundException, ValidationException
from infrastructure.repositories.experiment_repository import ExperimentRepository
from infrastructure.models.orm_models import ForecastResultModel
from services.forecasting_service import ForecastingService


class ExperimentService:
    def __init__(self, repository: ExperimentRepository = None,
                 forecasting_service: ForecastingService = None):
        self.repository = repository or ExperimentRepository()
        self.forecasting_service = forecasting_service or ForecastingService()

    def create_experiment(self, user_id, version_id, name, model_type, parameters=None):
        if model_type not in ("arima", "prophet"):
            raise ValidationException("model_type must be 'arima' or 'prophet'")
        return self.repository.create(user_id, version_id, name, model_type, parameters)

    def run_experiment(self, experiment_id, segment_id, horizon=4, test_size=4):
        exp = self.repository.get(experiment_id)
        if not exp:
            raise NotFoundException("Experiment not found")

        self.repository.update_status(experiment_id, "running")
        try:
            result = self.forecasting_service.run_forecast(
                version_id=exp.version_id, segment_id=segment_id, model_type=exp.model_type,
                horizon=horizon, test_size=test_size, params=exp.parameters or {},
            )
            self.repository.clear_forecast_results(experiment_id)
            forecast_rows = [
                ForecastResultModel(
                    experiment_id=experiment_id,
                    segment_id=segment_id,
                    forecast_time=datetime.fromisoformat(str(f["timestamp"])[:19]),
                    predicted_density=f["predicted_density"],
                    lower_bound=f["lower_bound"],
                    upper_bound=f["upper_bound"],
                )
                for f in result["forecast"]
            ]
            self.repository.save_forecast_results(forecast_rows)
            evaluation_metrics = {
                **result["metrics"],
                "_test_actual": result["test_actual"],
                "_test_predicted": result["test_predicted"],
                "_test_index": result["test_index"],
            }
            self.repository.update_status(experiment_id, "completed", evaluation_metrics)
            result["experiment_id"] = experiment_id
            result["segment_id"] = segment_id
            return result
        except Exception as e:
            self.repository.update_status(experiment_id, "failed", {"error": str(e)})
            raise

    def compare_experiments(self, experiment_ids):
        experiments = [self.repository.get(eid) for eid in experiment_ids]
        experiments = [e for e in experiments if e]
        return [{
            "experiment_id": e.experiment_id,
            "name": e.name,
            "model_type": e.model_type,
            "status": e.status,
            "evaluation_metrics": e.evaluation_metrics,
            "parameters": e.parameters,
        } for e in experiments]

    def list_experiments(self, user_id=None, version_id=None):
        return self.repository.list(user_id=user_id, version_id=version_id)

    def get_experiment(self, experiment_id):
        exp = self.repository.get(experiment_id)
        if not exp:
            raise NotFoundException("Experiment not found")
        return exp

    def get_forecast_results(self, experiment_id):
        self.get_experiment(experiment_id)
        return self.repository.get_forecast_results(experiment_id)
