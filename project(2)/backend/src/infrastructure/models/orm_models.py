"""SQLAlchemy ORM models mapped 1-1 to the ERD provided for the Urban Traffic
Analytics Platform (see database_design.png / ERD.png).
"""
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean, Float, DateTime,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from infrastructure.databases.base import Base


class UserModel(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    # admin | researcher | analyst | student
    role = Column(String(20), nullable=False, default="student")
    created_at = Column(DateTime, default=datetime.utcnow)

    datasets = relationship("DatasetModel", back_populates="owner")
    experiments = relationship("ExperimentModel", back_populates="owner")
    reports = relationship("ReportModel", back_populates="owner")
    audit_logs = relationship("AuditLogModel", back_populates="user")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class DatasetModel(Base):
    __tablename__ = "datasets"

    dataset_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    # draft | validated | archived | deleted
    status = Column(String(20), nullable=False, default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("UserModel", back_populates="datasets")
    versions = relationship("DatasetVersionModel", back_populates="dataset",
                             cascade="all, delete-orphan")


class DatasetVersionModel(Base):
    __tablename__ = "dataset_versions"

    version_id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.dataset_id"), nullable=False)
    version_number = Column(String(20), nullable=False)
    file_path = Column(String(500), nullable=False)
    row_count = Column(Integer, default=0)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    validation_report = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    dataset = relationship("DatasetModel", back_populates="versions")
    traffic_features = relationship("TrafficFeatureModel", back_populates="version",
                                     cascade="all, delete-orphan")
    experiments = relationship("ExperimentModel", back_populates="version")

    __table_args__ = (UniqueConstraint("dataset_id", "version_number", name="uq_dataset_version"),)


class RoadSegmentModel(Base):
    __tablename__ = "road_segments"

    segment_id = Column(String(50), primary_key=True)
    segment_name = Column(String(150))
    coordinates = Column(JSONB, nullable=True)  # {lat, lon} or list of points

    traffic_features = relationship("TrafficFeatureModel", back_populates="segment")


class TrafficFeatureModel(Base):
    __tablename__ = "traffic_features"

    feature_id = Column(Integer, primary_key=True, autoincrement=True)
    version_id = Column(Integer, ForeignKey("dataset_versions.version_id"), nullable=False)
    segment_id = Column(String(50), ForeignKey("road_segments.segment_id"), nullable=False)
    timestamp_val = Column(DateTime, nullable=False)
    vehicle_count = Column(Integer, default=0)
    avg_speed = Column(Float, default=0)
    traffic_density = Column(Float, default=0)
    is_peak_hour = Column(Boolean, default=False)

    version = relationship("DatasetVersionModel", back_populates="traffic_features")
    segment = relationship("RoadSegmentModel", back_populates="traffic_features")

    __table_args__ = (
        UniqueConstraint("version_id", "segment_id", "timestamp_val", name="uq_feature_point"),
    )


class ExperimentModel(Base):
    __tablename__ = "experiments"

    experiment_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    version_id = Column(Integer, ForeignKey("dataset_versions.version_id"), nullable=False)
    name = Column(String(200), nullable=False)
    # arima | prophet
    model_type = Column(String(20), nullable=False)
    parameters = Column(JSONB, nullable=True)
    evaluation_metrics = Column(JSONB, nullable=True)
    # pending | running | completed | failed
    status = Column(String(20), nullable=False, default="pending")
    random_seed = Column(Integer, default=42)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("UserModel", back_populates="experiments")
    version = relationship("DatasetVersionModel", back_populates="experiments")
    forecast_results = relationship("ForecastResultModel", back_populates="experiment",
                                     cascade="all, delete-orphan")
    reports = relationship("ReportModel", back_populates="experiment")


class ForecastResultModel(Base):
    __tablename__ = "forecast_results"

    result_id = Column(Integer, primary_key=True, autoincrement=True)
    experiment_id = Column(Integer, ForeignKey("experiments.experiment_id"), nullable=False)
    segment_id = Column(String(50), ForeignKey("road_segments.segment_id"), nullable=False)
    forecast_time = Column(DateTime, nullable=False)
    predicted_density = Column(Float)
    lower_bound = Column(Float)
    upper_bound = Column(Float)

    experiment = relationship("ExperimentModel", back_populates="forecast_results")


class ReportModel(Base):
    __tablename__ = "reports"

    report_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    experiment_id = Column(Integer, ForeignKey("experiments.experiment_id"), nullable=True)
    report_name = Column(String(200), nullable=False)
    # pdf | excel
    format = Column(String(10), nullable=False)
    file_url = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("UserModel", back_populates="reports")
    experiment = relationship("ExperimentModel", back_populates="reports")


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(50))
    details = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("UserModel", back_populates="audit_logs")
