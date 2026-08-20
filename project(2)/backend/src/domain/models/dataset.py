class Dataset:
    def __init__(self, name, user_id, description=None, status="draft",
                 dataset_id=None, created_at=None):
        self.dataset_id = dataset_id
        self.user_id = user_id
        self.name = name
        self.description = description
        self.status = status
        self.created_at = created_at


class DatasetVersion:
    def __init__(self, dataset_id, version_number, file_path, start_time=None,
                 end_time=None, version_id=None, created_at=None, row_count=0):
        self.version_id = version_id
        self.dataset_id = dataset_id
        self.version_number = version_number
        self.file_path = file_path
        self.start_time = start_time
        self.end_time = end_time
        self.created_at = created_at
        self.row_count = row_count
