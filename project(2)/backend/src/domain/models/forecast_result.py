class ForecastResult:
    def __init__(self, experiment_id, segment_id, forecast_time, predicted_density,
                 lower_bound=None, upper_bound=None, result_id=None):
        self.result_id = result_id
        self.experiment_id = experiment_id
        self.segment_id = segment_id
        self.forecast_time = forecast_time
        self.predicted_density = predicted_density
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
