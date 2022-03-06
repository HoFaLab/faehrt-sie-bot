import requests
import csv
from time import sleep
from WaterLevelData import WaterLevelData
from WeatherData import WeatherData



def get_current_water_level()  -> WaterLevelData:
    download_url = "https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations/5952050/W/currentmeasurement.json"
    response = requests.get(download_url)

    if not response.status_code == 200:
        print("error in getting water level data", response.status_code, response.error)

    return WaterLevelData.from_current_measurement_dict(response.json())

def get_current_weather_data()  -> WeatherData:
    download_url = "https://api.openweathermap.org/data/2.5/weather?q=Hamburg,de&APPID=1a535be72b10f3c678749359a8a35050"
    response = requests.get(download_url)

    if not response.status_code == 200:
        print("error in getting wind data", response.status_code, response.error)
    
    return WeatherData.from_current_measurement_dict(response.json())
 
    
def create_dict_for_row(water_data: WaterLevelData, weather_data: WeatherData):
        return {
            "timestamp": water_data.timestamp,
            "value": water_data.value,
            "trend": water_data.trend,
            "wind_speed": weather_data.wind_speed,
            "wind_direction": weather_data.wind_direction,
            "wind_gust": weather_data.wind_gust,
            "weather_code": weather_data.weather_code,
        }

if __name__ == "__main__":

    while True:
        current_water_level_data = get_current_water_level()
        print(vars(current_water_level_data))
        
        current_wind_data = get_current_weather_data()
        print(vars(current_wind_data))

        data_dict = create_dict_for_row(current_water_level_data, current_wind_data)
    
        # add row to CSV file
        with open("data" + "/" + "live_measurements.csv", "a", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data_dict.keys())
            writer.writerow(data_dict)

        print("Added row to file")
        sleep(10*60)

