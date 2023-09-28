import requests
import datetime
from string import Template
from dataclasses import dataclass
from typing import Dict

from service_time import during_service_time


data_url = "https://wasserstand-nordsee.bsh.de/data/DE__508P.json"
max_water_level = 750


# get forecasts data
def download_data():
    response = requests.get(data_url)

    if response.status_code != 200:
        print("Could not download data")
        print(response.status_code, response.text)

        return None

    return response.json()


def check_for_new_data(old_data_creation_time: datetime.datetime):
    if current_data := download_data():
        current_creation_time = datetime.datetime.fromisoformat(
            current_data["creation_forecast"]
        )

        return old_data_creation_time < current_creation_time


@dataclass
class DisruptionPeriod:
    start_time: datetime.datetime
    end_time: datetime.datetime

    def disruption_during_service_time(self):
        return during_service_time(self.start_time) or during_service_time(
            self.end_time
        )
    
    def get_disruption_length_minutes(self):
        return (self.end_time - self.start_time).total_seconds() / 60


class TideData:
    data: Dict
    forecast_creation_date: datetime.datetime
    forecast_extremes_today: Dict
    forecast_extremes_tmmrw: Dict
    forecast_detailed_values: Dict
    disruption_period: DisruptionPeriod
    reminder_sent: bool = False

    def __init__(self):
        self.data = download_data()

        if self.data == download_data():
            self.forecast_creation_date = datetime.datetime.fromisoformat(
                self.data["creation_forecast"]
            )
            self.forecast_extremes_today = self.data["hwnw_forecast"]["data"][:2]
            self.forecast_extremes_tmmrw = self.data["hwnw_forecast"]["data"][
                2:
            ]  # tomorrows extremes
            self.forecast_detailed_values = self.data["curve_forecast"]["data"]

            if self.check_extremes(self.forecast_extremes_today):
                self.set_disruption_period()

    # get current tide measurement
    def get_current_value(self):  # sourcery skip: simplify-numeric-comparison
        now = datetime.datetime.now
        for forecast in self.forecast_detailed_values:
            timestamp = datetime.datetime.fromisoformat(forecast["timestamp"])
            if (now - timestamp).total_seconds() / 60 <= 10:
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
            if extreme["event"] == "HW" and extreme["value"] > max_water_level:
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
            if (
                value
                and value >= max_water_level
                and (
                    self.forecast_detailed_values[id + 1]["curveforecast"]
                    < max_water_level
                )
            ):
                end_time = datetime.datetime.fromisoformat(forecast["timestamp"])
                break

        if start_time and end_time:
            self.disruption_period = DisruptionPeriod(start_time, end_time)

    #  returns a service disruption warning message
    def get_disruption_warn_msg(self):
        if not self.disruption_period:
            return None

        return self.make_msg(
            """
            🌊🌊🌊 WASSERSTANDSMELDUNG 🌊🌊🌊 \n
            Zwischen $start_time und $end_time Uhr: \n
            In dieser Zeit wird wahrscheinlich nur die Argentinienbrücke angefahren. \n
            $tomorrow_warning
            """
        )

    #  returns a service disruption warning message
    def get_reminder_msg(self):
        return self.make_msg(
            """
            ⏰⏰⏰ Erinnerung In 2h startet Hochwasser 🌊🌊🌊 \n
            Zwischen $start_time und $end_time Uhr. Checkt auch Twitter. \n
            $tomorrow_warning
            """
        )

    # TODO Rename this here and in `get_disruption_warn_msg` and `get_reminder_msg`
    def make_msg(self, template_txt: str):
        start_time = self.disruption_period.start_time
        end_time = self.disruption_period.end_time
        template = Template(template_txt)
        return template.safe_substitute(
            {
                "max_water_level": max_water_level,
                "start_time": f"{str(start_time.hour)}:{str(start_time.minute)}",
                "end_time": f"{str(end_time.hour)}:{str(end_time.minute)}",
                "tomorrow_warning": self.make_tmrrw_warning(),
            }
        )

    def make_tmrrw_warning(self) -> str:
        if self.check_extremes(self.forecast_extremes_tmmrw):
            high_time = next(
                filter(lambda e: e["event"] == "HW", self.forecast_extremes_tmmrw)
            )["timestamp"]
            high_time = datetime.datetime.fromisoformat(high_time)

            if during_service_time(
                high_time - datetime.timedelta(hours=1)
            ) or +during_service_time(high_time + datetime.timedelta(hours=1)):
                return "Erneutes Hochwasser morgen gegen {h}:{m} Uhr. Mehr Infos hier: {link}".format(
                    h=high_time.hour,
                    m=high_time.minute,
                    link="https://wasserstand-nordsee.bsh.de/hamburg_st-pauli",
                )

        return ""

    def is_time_to_remind(self):
        return bool(
            (
                # is disruption and is it during service times?
                self.disruption_period
                and self.disruption_period.disruption_during_service_time()
            )
            and (
                # is it within the next 2 hours?
                datetime.timedelta(hours=2) + datetime.datetime.now(self.disruption_period.start_time.tzinfo)
                > self.disruption_period.start_time
            )
        )
