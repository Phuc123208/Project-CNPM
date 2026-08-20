import os
import uuid
import pandas as pd
from werkzeug.utils import secure_filename
from domain.exceptions import NotFoundException, ValidationException
from infrastructure.repositories.dataset_repository import DatasetRepository
from services.validation_service import validate_dataframe, REQUIRED_COLUMNS


class DatasetService:
    def __init__(self, repository: DatasetRepository = None, upload_folder: str = "uploads"):
        self.repository = repository or DatasetRepository()
        self.upload_folder = upload_folder
        os.makedirs(self.upload_folder, exist_ok=True)

    # ---------------- Dataset CRUD ----------------
    def create_dataset_with_file(self, user_id, name, description, file_storage):
        if not file_storage or file_storage.filename == "":
            raise ValidationException("No file provided")
        if not file_storage.filename.lower().endswith(".csv"):
            raise ValidationException("Only CSV trajectory files are supported")

        dataset = self.repository.create_dataset(name=name, user_id=user_id,
                                                   description=description, status="draft")

        # Save the raw file
        safe_name = secure_filename(file_storage.filename)
        unique_name = f"ds{dataset.dataset_id}_{uuid.uuid4().hex[:8]}_{safe_name}"
        dataset_dir = os.path.join(self.upload_folder, f"dataset_{dataset.dataset_id}")
        os.makedirs(dataset_dir, exist_ok=True)
        file_path = os.path.join(dataset_dir, unique_name)
        file_storage.save(file_path)

        # Read + basic validation (schema)
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise ValidationException(f"Could not parse CSV file: {e}")

        report = validate_dataframe(df)

        parsed_ts = pd.to_datetime(df["timestamp"], errors="coerce") if "timestamp" in df.columns else None
        start_time = parsed_ts.min() if parsed_ts is not None and not parsed_ts.isna().all() else None
        end_time = parsed_ts.max() if parsed_ts is not None and not parsed_ts.isna().all() else None

        versions = self.repository.list_versions(dataset.dataset_id)
        version_number = f"v{len(versions) + 1}"

        version = self.repository.create_version(
            dataset_id=dataset.dataset_id, version_number=version_number, file_path=file_path,
            row_count=len(df), start_time=start_time, end_time=end_time,
            validation_report=report,
        )

        # Register unique road segments found in the data
        if "segment_id" in df.columns:
            for seg_id in df["segment_id"].dropna().unique():
                self.repository.upsert_segment(str(seg_id))

        status = "validated" if report.get("is_valid") else "draft"
        self.repository.update_dataset_status(dataset.dataset_id, status)

        return dataset, version, report

    def upload_new_version(self, dataset_id, file_storage):
        dataset = self.repository.get_dataset(dataset_id)
        if not dataset:
            raise NotFoundException("Dataset not found")
        if not file_storage or not file_storage.filename.lower().endswith(".csv"):
            raise ValidationException("Only CSV trajectory files are supported")

        safe_name = secure_filename(file_storage.filename)
        unique_name = f"ds{dataset_id}_{uuid.uuid4().hex[:8]}_{safe_name}"
        dataset_dir = os.path.join(self.upload_folder, f"dataset_{dataset_id}")
        os.makedirs(dataset_dir, exist_ok=True)
        file_path = os.path.join(dataset_dir, unique_name)
        file_storage.save(file_path)

        df = pd.read_csv(file_path)
        report = validate_dataframe(df)
        parsed_ts = pd.to_datetime(df["timestamp"], errors="coerce") if "timestamp" in df.columns else None
        start_time = parsed_ts.min() if parsed_ts is not None and not parsed_ts.isna().all() else None
        end_time = parsed_ts.max() if parsed_ts is not None and not parsed_ts.isna().all() else None

        versions = self.repository.list_versions(dataset_id)
        version_number = f"v{len(versions) + 1}"
        version = self.repository.create_version(
            dataset_id=dataset_id, version_number=version_number, file_path=file_path,
            row_count=len(df), start_time=start_time, end_time=end_time,
            validation_report=report,
        )
        if "segment_id" in df.columns:
            for seg_id in df["segment_id"].dropna().unique():
                self.repository.upsert_segment(str(seg_id))

        return version, report

    def list_datasets(self, user_id=None, status=None, search=None):
        return self.repository.list_datasets(user_id=user_id, status=status, search=search)

    def get_dataset(self, dataset_id):
        ds = self.repository.get_dataset(dataset_id)
        if not ds:
            raise NotFoundException("Dataset not found")
        return ds

    def list_versions(self, dataset_id):
        self.get_dataset(dataset_id)
        return self.repository.list_versions(dataset_id)

    def preview_version(self, version_id, limit=50):
        version = self.repository.get_version(version_id)
        if not version:
            raise NotFoundException("Dataset version not found")
        df = pd.read_csv(version.file_path)
        return {
            "columns": list(df.columns),
            "rows": df.head(limit).fillna("").to_dict(orient="records"),
            "total_rows": len(df),
        }

    def validate_version(self, version_id):
        version = self.repository.get_version(version_id)
        if not version:
            raise NotFoundException("Dataset version not found")
        df = pd.read_csv(version.file_path)
        report = validate_dataframe(df)
        self.repository.update_version_validation(version_id, report)
        status = "validated" if report.get("is_valid") else "draft"
        self.repository.update_dataset_status(version.dataset_id, status)
        return report

    def archive_dataset(self, dataset_id):
        ds = self.repository.update_dataset_status(dataset_id, "archived")
        if not ds:
            raise NotFoundException("Dataset not found")
        return ds

    def restore_dataset(self, dataset_id):
        ds = self.repository.update_dataset_status(dataset_id, "validated")
        if not ds:
            raise NotFoundException("Dataset not found")
        return ds

    def delete_dataset(self, dataset_id, hard=False):
        ok = self.repository.delete_dataset(dataset_id, hard=hard)
        if not ok:
            raise NotFoundException("Dataset not found")
        return ok
