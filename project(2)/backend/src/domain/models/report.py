class Report:
    def __init__(self, user_id, report_name, format, file_url, experiment_id=None,
                 report_id=None, created_at=None):
        self.report_id = report_id
        self.user_id = user_id
        self.experiment_id = experiment_id
        self.report_name = report_name
        self.format = format
        self.file_url = file_url
        self.created_at = created_at
