class TrafficFeature:
    def __init__(self, version_id, segment_id, timestamp_val, vehicle_count,
                 avg_speed, traffic_density, is_peak_hour=False, feature_id=None):
        self.feature_id = feature_id
        self.version_id = version_id
        self.segment_id = segment_id
        self.timestamp_val = timestamp_val
        self.vehicle_count = vehicle_count
        self.avg_speed = avg_speed
        self.traffic_density = traffic_density
        self.is_peak_hour = is_peak_hour
