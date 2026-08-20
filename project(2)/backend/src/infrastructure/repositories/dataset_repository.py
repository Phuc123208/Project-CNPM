from infrastructure.databases.session import get_session
from infrastructure.models.orm_models import (
    DatasetModel, DatasetVersionModel, RoadSegmentModel, TrafficFeatureModel
)


class DatasetRepository:
    def __init__(self):
        self.session = get_session()

    # ---- Dataset ----
    def create_dataset(self, name, user_id, description=None, status="draft"):
        ds = DatasetModel(name=name, user_id=user_id, description=description, status=status)
        self.session.add(ds)
        self.session.commit()
        self.session.refresh(ds)
        return ds

    def get_dataset(self, dataset_id):
        return self.session.query(DatasetModel).filter_by(dataset_id=dataset_id).first()

    def list_datasets(self, user_id=None, status=None, search=None):
        q = self.session.query(DatasetModel)
        if user_id:
            q = q.filter_by(user_id=user_id)
        if status:
            q = q.filter_by(status=status)
        else:
            q = q.filter(DatasetModel.status != "deleted")
        if search:
            q = q.filter(DatasetModel.name.ilike(f"%{search}%"))
        return q.order_by(DatasetModel.created_at.desc()).all()

    def update_dataset_status(self, dataset_id, status):
        ds = self.get_dataset(dataset_id)
        if not ds:
            return None
        ds.status = status
        self.session.commit()
        self.session.refresh(ds)
        return ds

    def delete_dataset(self, dataset_id, hard=False):
        ds = self.get_dataset(dataset_id)
        if not ds:
            return False
        if hard:
            self.session.delete(ds)
        else:
            ds.status = "deleted"
        self.session.commit()
        return True

    # ---- Dataset version ----
    def create_version(self, dataset_id, version_number, file_path, row_count=0,
                        start_time=None, end_time=None, validation_report=None):
        v = DatasetVersionModel(
            dataset_id=dataset_id, version_number=version_number, file_path=file_path,
            row_count=row_count, start_time=start_time, end_time=end_time,
            validation_report=validation_report,
        )
        self.session.add(v)
        self.session.commit()
        self.session.refresh(v)
        return v

    def get_version(self, version_id):
        return self.session.query(DatasetVersionModel).filter_by(version_id=version_id).first()

    def list_versions(self, dataset_id):
        return (self.session.query(DatasetVersionModel)
                .filter_by(dataset_id=dataset_id)
                .order_by(DatasetVersionModel.created_at.desc()).all())

    def update_version_validation(self, version_id, validation_report):
        v = self.get_version(version_id)
        if not v:
            return None
        v.validation_report = validation_report
        self.session.commit()
        self.session.refresh(v)
        return v

    # ---- Road segments ----
    def upsert_segment(self, segment_id, segment_name=None, coordinates=None):
        seg = self.session.query(RoadSegmentModel).filter_by(segment_id=segment_id).first()
        if not seg:
            seg = RoadSegmentModel(segment_id=segment_id, segment_name=segment_name or segment_id,
                                    coordinates=coordinates)
            self.session.add(seg)
            self.session.commit()
        return seg

    def list_segments(self):
        return self.session.query(RoadSegmentModel).all()

    # ---- Traffic features ----
    def bulk_insert_features(self, features):
        for f in features:
            self.session.add(f)
        self.session.commit()

    def get_features(self, version_id, segment_id=None):
        q = self.session.query(TrafficFeatureModel).filter_by(version_id=version_id)
        if segment_id:
            q = q.filter_by(segment_id=segment_id)
        return q.order_by(TrafficFeatureModel.timestamp_val).all()

    def clear_features(self, version_id):
        self.session.query(TrafficFeatureModel).filter_by(version_id=version_id).delete()
        self.session.commit()
