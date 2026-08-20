class Experiment:
    def __init__(self, user_id, version_id, name, model_type, parameters=None,
                 status="pending", evaluation_metrics=None, experiment_id=None,
                 created_at=None):
        self.experiment_id = experiment_id
        self.user_id = user_id
        self.version_id = version_id
        self.name = name
        self.model_type = model_type
        self.parameters = parameters or {}
        self.status = status
        self.evaluation_metrics = evaluation_metrics or {}
        self.created_at = created_at
