"""Module 2 - Traffic Pattern Analysis.
Transforms raw UAV vehicle-trajectory records into a traffic-density time
series per road segment (answers RQ1), and exposes analytics used by the
Visualization Dashboard (Module 4).
"""
import pandas as pd
from domain.exceptions import NotFoundException, ValidationException
from infrastructure.repositories.dataset_repository import DatasetRepository
from infrastructure.models.orm_models import TrafficFeatureModel


class AnalysisService:
    def __init__(self, repository: DatasetRepository = None):
        self.repository = repository or DatasetRepository()

    def compute_features(self, version_id, interval_minutes=1, peak_percentile=75):
        """RQ1 + RQ2: build a traffic-density time series from trajectories,
        using a configurable temporal aggregation interval."""
        if interval_minutes < 1:
            raise ValidationException("interval_minutes must be at least 1")
        version = self.repository.get_version(version_id)
        if not version:
            raise NotFoundException("Dataset version not found")

        df = pd.read_csv(version.file_path)
        required = {"vehicle_id", "timestamp", "segment_id", "speed"}
        if not required.issubset(df.columns):
            raise ValidationException(f"Dataset is missing required columns: {required - set(df.columns)}")

        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df = df.dropna(subset=["timestamp", "segment_id"])
        df["speed"] = pd.to_numeric(df["speed"], errors="coerce").fillna(0)

        df["time_bucket"] = df["timestamp"].dt.floor(f"{interval_minutes}min")

        grouped = df.groupby(["segment_id", "time_bucket"]).agg(
            vehicle_count=("vehicle_id", "nunique"),
            avg_speed=("speed", "mean"),
        ).reset_index()

        interval_hours = interval_minutes / 60.0
        # Flow (veh/h) = vehicle_count / interval_hours; Density (veh/km) = Flow / Speed
        grouped["flow"] = grouped["vehicle_count"] / interval_hours
        grouped["traffic_density"] = grouped.apply(
            lambda r: (r["flow"] / r["avg_speed"]) if r["avg_speed"] > 0 else r["flow"], axis=1
        )

        threshold = grouped["vehicle_count"].quantile(peak_percentile / 100.0)
        grouped["is_peak_hour"] = grouped["vehicle_count"] >= threshold

        # Persist: register segments + replace features for this version
        for seg_id in grouped["segment_id"].unique():
            self.repository.upsert_segment(str(seg_id))
        self.repository.clear_features(version_id)

        features = [
            TrafficFeatureModel(
                version_id=version_id,
                segment_id=str(row.segment_id),
                timestamp_val=row.time_bucket.to_pydatetime(),
                vehicle_count=int(row.vehicle_count),
                avg_speed=float(round(row.avg_speed, 3)),
                traffic_density=float(round(row.traffic_density, 3)),
                is_peak_hour=bool(row.is_peak_hour),
            )
            for row in grouped.itertuples()
        ]
        self.repository.bulk_insert_features(features)

        return {
            "version_id": version_id,
            "interval_minutes": interval_minutes,
            "points_generated": len(features),
            "segments": sorted(grouped["segment_id"].unique().tolist()),
        }

    def _features_df(self, version_id, segment_id=None):
        rows = self.repository.get_features(version_id, segment_id)
        if not rows:
            return pd.DataFrame(columns=["segment_id", "timestamp_val", "vehicle_count",
                                          "avg_speed", "traffic_density", "is_peak_hour"])
        return pd.DataFrame([{
            "segment_id": r.segment_id,
            "timestamp_val": r.timestamp_val,
            "vehicle_count": r.vehicle_count,
            "avg_speed": r.avg_speed,
            "traffic_density": r.traffic_density,
            "is_peak_hour": r.is_peak_hour,
        } for r in rows])

    def get_kpis(self, version_id):
        df = self._features_df(version_id)
        if df.empty:
            return {"vehicle_count_total": 0, "avg_speed": 0, "avg_density": 0,
                    "peak_points": 0, "segments": 0}
        return {
            "vehicle_count_total": int(df["vehicle_count"].sum()),
            "avg_speed": float(round(df["avg_speed"].mean(), 2)),
            "avg_density": float(round(df["traffic_density"].mean(), 2)),
            "peak_points": int(df["is_peak_hour"].sum()),
            "segments": int(df["segment_id"].nunique()),
        }

    def get_trend(self, version_id, segment_id=None):
        df = self._features_df(version_id, segment_id)
        if df.empty:
            return []
        df = df.sort_values("timestamp_val")
        return [{
            "timestamp": row.timestamp_val.isoformat(),
            "segment_id": row.segment_id,
            "vehicle_count": row.vehicle_count,
            "avg_speed": row.avg_speed,
            "traffic_density": row.traffic_density,
            "is_peak_hour": bool(row.is_peak_hour),
        } for row in df.itertuples()]

    def get_heatmap(self, version_id):
        """Segment x hour-of-day average density matrix, for a heatmap chart."""
        df = self._features_df(version_id)
        if df.empty:
            return []
        df["hour"] = pd.to_datetime(df["timestamp_val"]).dt.hour
        pivot = df.groupby(["segment_id", "hour"])["traffic_density"].mean().reset_index()
        return pivot.to_dict(orient="records")

    def get_speed_distribution(self, version_id, bins=10):
        df = self._features_df(version_id)
        if df.empty:
            return []
        counts, edges = pd.cut(df["avg_speed"], bins=bins, retbins=True)
        dist = counts.value_counts().sort_index()
        return [{"range": str(interval), "count": int(count)} for interval, count in dist.items()]

    def get_peak_hours(self, version_id):
        df = self._features_df(version_id)
        if df.empty:
            return []
        df["hour"] = pd.to_datetime(df["timestamp_val"]).dt.hour
        agg = df.groupby("hour").agg(avg_vehicle_count=("vehicle_count", "mean")).reset_index()
        threshold = agg["avg_vehicle_count"].quantile(0.75)
        agg["is_peak"] = agg["avg_vehicle_count"] >= threshold
        return agg.sort_values("hour").to_dict(orient="records")

    def get_hotspots(self, version_id, top_n=5):
        df = self._features_df(version_id)
        if df.empty:
            return []
        agg = df.groupby("segment_id").agg(
            avg_density=("traffic_density", "mean"),
            avg_speed=("avg_speed", "mean"),
            total_vehicle_count=("vehicle_count", "sum"),
        ).reset_index()
        agg = agg.sort_values("avg_density", ascending=False).head(top_n)
        return agg.to_dict(orient="records")
