"""Data-quality validation for uploaded UAV trajectory datasets.
Expected raw CSV columns: vehicle_id, timestamp, segment_id, speed, lat, lon
"""
import pandas as pd


REQUIRED_COLUMNS = ["vehicle_id", "timestamp", "segment_id", "speed", "lat", "lon"]


def validate_schema(df: pd.DataFrame):
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    return missing_cols


def validate_dataframe(df: pd.DataFrame) -> dict:
    """Run data-quality checks and return a structured quality report."""
    report = {"row_count": int(len(df))}

    missing_cols = validate_schema(df)
    report["missing_columns"] = missing_cols
    if missing_cols:
        report["is_valid"] = False
        return report

    # Missing values
    missing_values = df[REQUIRED_COLUMNS].isna().sum()
    report["missing_values"] = {k: int(v) for k, v in missing_values.items() if v > 0}

    # Duplicated records (same vehicle, timestamp, segment)
    dup_mask = df.duplicated(subset=["vehicle_id", "timestamp", "segment_id"], keep=False)
    report["duplicated_records"] = int(dup_mask.sum())

    # Invalid timestamps
    parsed_ts = pd.to_datetime(df["timestamp"], errors="coerce")
    report["invalid_timestamps"] = int(parsed_ts.isna().sum())

    # Invalid coordinates (outside plausible lat/lon bounds)
    lat = pd.to_numeric(df["lat"], errors="coerce")
    lon = pd.to_numeric(df["lon"], errors="coerce")
    invalid_coords = ((lat < -90) | (lat > 90) | (lon < -180) | (lon > 180) |
                       lat.isna() | lon.isna())
    report["invalid_coordinates"] = int(invalid_coords.sum())

    # Invalid speed (negative or absurdly high, > 200 km/h as sanity bound)
    speed = pd.to_numeric(df["speed"], errors="coerce")
    invalid_speed = ((speed < 0) | (speed > 200) | speed.isna())
    report["invalid_speed"] = int(invalid_speed.sum())

    report["segments"] = sorted(df["segment_id"].dropna().unique().tolist())
    report["vehicles"] = int(df["vehicle_id"].nunique())
    report["time_range"] = {
        "start": str(parsed_ts.min()) if not parsed_ts.isna().all() else None,
        "end": str(parsed_ts.max()) if not parsed_ts.isna().all() else None,
    }

    total_issues = (sum(report["missing_values"].values()) + report["duplicated_records"] +
                     report["invalid_timestamps"] + report["invalid_coordinates"] +
                     report["invalid_speed"])
    report["total_issues"] = int(total_issues)
    report["is_valid"] = total_issues == 0
    return report
