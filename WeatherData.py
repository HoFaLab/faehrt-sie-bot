class WeatherData:
    def __init__(self, wind_speed, wind_direction, wind_gust, weather_code):
        self.wind_speed = wind_speed
        self.wind_direction = wind_direction
        self.wind_gust = wind_gust
        self.weather_code = weather_code

    @classmethod
    def from_current_measurement_dict(cls, response_json):
        wind_speed = response_json['wind']['speed']
        wind_direction = response_json['wind']['deg']
        weather_code = response_json['weather'][0]['id']
       
        # gusts are not always part of the response
        try:
            wind_gust = response_json['wind']['gust']
        except KeyError:
            wind_gust = 0

        return cls(wind_speed, wind_direction, wind_gust, weather_code)