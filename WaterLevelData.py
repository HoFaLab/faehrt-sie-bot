class WaterLevelData:
    def __init__(self, timestamp, value, trend):
        self.timestamp = timestamp
        self.value = value
        self.trend = trend

    @classmethod
    def from_current_measurement_dict(cls, response_json):
        timestamp = response_json['timestamp']
        value = response_json['value']
        trend = response_json['trend']
        return cls(timestamp, value, trend)


