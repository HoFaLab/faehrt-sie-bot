import requests
import datetime
from string import Template
from dataclasses import dataclass 
from typing import Dict

from service_time import during_service_time


data_url = "https://wasserstand-nordsee.bsh.de/data/DE__508P.json"
max_water_level = 720


# get forecasts data
def download_data():
    response = requests.get(data_url)
    
    if not response.status_code == 200:
        print("Could not download data")
        print(response.status_code, response.text)
        
        return None

    return response.json()



def check_for_new_data(old_data_creation_time: datetime.datetime):
    current_data = download_data()
    if current_data:
        current_creation_time = datetime.datetime.fromisoformat(current_data["creation_forecast"])

        return old_data_creation_time < current_creation_time

@dataclass
class DisruptionPeriod:
    start_time: datetime.datetime
    end_time: datetime.datetime


class TideData:
    data: Dict
    forecast_creation_date: datetime.datetime
    forecast_extremes_today: Dict
    forecast_extremes_tmmrw: Dict
    forecast_detailed_values: Dict
    disruption_period: DisruptionPeriod


    def __init__(self):
        self.data = download_data()

        if self.data:
            self.forecast_creation_date = datetime.datetime.fromisoformat(self.data["creation_forecast"])
            self.forecast_extremes_today = self.data["hwnw_forecast"]["data"][0:2]  # todays extremes only
            self.forecast_extremes_tmmrw = self.data["hwnw_forecast"]["data"][2:]  # tomorrows extremes
            self.forecast_detailed_values = self.data["curve_forecast"]["data"]

            if self.check_extremes(self.forecast_extremes_today):
                self.set_disruption_period()



    # get current tide measurement
    def get_current_value(self):
        now = datetime.datetime.now
        for forecast in self.forecast_detailed_values:
            timestamp = datetime.datetime.fromisoformat(forecast["timestamp"])
            if (now-timestamp).total_seconds() / 60 <= 10:
                return forecast["measurement"]

    
    """
    Checks if extremes are outside boundaries
    [{
        "timestamp": "2023-02-18 01:52:00+01:00",
        "value": 812,
        "event": "HW",
        "deviation": 12.5,
        "forecast": "+1,0 m"
    },
    ]
    """
    def check_extremes(self, extremes):
        for extreme in extremes:
            if extreme["event"]  == "HW" and extreme["value"] > max_water_level:
                return True

    
    """
    from when to when is the tide to high / low? 
        -> starting time disruption
        -> end time disruption
    [
        {
        "timestamp": "2023-02-17 08:00:00+01:00",
        "astro": 341,
        "curveforecast": 434,
        "measurement": null
        },
    """
    def set_disruption_period(self):
        start_time, end_time = None, None

        for forecast in self.forecast_detailed_values:
            value = forecast["curveforecast"]
            if value and value > max_water_level:
                start_time = datetime.datetime.fromisoformat(forecast["timestamp"])
                break
        
        for id, forecast in enumerate(self.forecast_detailed_values):
            value = forecast["curveforecast"]
            if value and value >= max_water_level:
                if self.forecast_detailed_values[id + 1]["curveforecast"] < max_water_level:
                    end_time = datetime.datetime.fromisoformat(forecast["timestamp"])
                    break
        
        if start_time and end_time:
            self.disruption_period = DisruptionPeriod(start_time, end_time)

        

    #  returns a service disruption warning message
    def get_disruption_warn_msg(self):
        if not self.disruption_period:
            return None

        start_time = self.disruption_period.start_time
        end_time =  self.disruption_period.end_time

        "Hello, {first} {last}".format(first='Joe')
    
        template = Template(
            """
            *** WASSERSTANDSMELDUNG *** \n
            Zwischen $start_time und $end_time Uhr: \n
            Voraussichtlicher Wasserstand höher als $max_water_level cm über PNP. \n
            In dieser Zeit wird wahrscheinlich nur die Ernst-August-Schleuse angefahren. \n
            $tomorrow_warning
            """
        )

        return template.safe_substitute({
            "max_water_level": max_water_level,
            "start_time": str(start_time.hour) + ":" + str(start_time.minute),
            "end_time": str(end_time.hour) + ":" + str(end_time.minute),
            "tomorrow_warning": self.make_tmrrw_warning()
        })


    def make_tmrrw_warning(self) -> str:
        if self.check_extremes(self.forecast_extremes_tmmrw):
            high_time = filter(lambda e: e["event"] == "HW", self.forecast_extremes_tmmrw)[0]["timestamp"]
            high_time = datetime.datetime.fromisoformat(high_time)

            if during_service_time(high_time):
                return "Erneutes Hochwasser morgen gegen {h}:{m} Uhr. Mehr Infos hier: {link}".format(
                    h=high_time.hour,
                    m=high_time.minute,
                    link="https://wasserstand-nordsee.bsh.de/hamburg_st-pauli"
                )
        
        return ""
