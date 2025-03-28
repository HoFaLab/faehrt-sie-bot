from datetime import datetime
from datetime import timedelta
from typing import List

import paho.mqtt.client as mqtt
import json
import time
import argparse

from departure_info import DepartureInfo
from telegram import post_message_to_telegram

# MQTT Configuration
# TODO env!
MQTT_BROKER = "mqtt.mobilitysignage.com"
MQTT_PORT = 443
MQTT_USERNAME = "HADAG"
MQTT_PASSWORD = "HADAGHAMBURG8874471"
DEVICE_ID = "HLK6NLWRY8SD37TWXDCHIFHVSDEGTV59LSJAU4NSQDNAOSDV7L-66"
COMPANY_ID = "HADAG"

# Data storage
collected_data = {
    "running_text": None,
    "departure_info": None,
    "water_level": None,
    "map_data": None,
    "media_content": None
}

# Topics to subscribe to
topics = [
    f"/content/runningText/{COMPANY_ID}/{DEVICE_ID}",
    f"/departure/{COMPANY_ID}/{DEVICE_ID}",
    #f"/content/deviceMapData/{COMPANY_ID}/{DEVICE_ID}",
    #f"/content/media/{COMPANY_ID}/{DEVICE_ID}"
]

known_departure_infos: List[DepartureInfo] = {}


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

    for topic in topics:
        client.subscribe(topic)
        print(f"Subscribed to: {topic}")


def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    topic = msg.topic
    print(f"\nReceived message on topic: {topic}")

    if "/content/runningText/" in topic:
        collected_data["running_text"] = payload
        print(f"Running Text Content Updated {payload}")
        forward_running_text_if_relevant(payload)

    elif "/departure/" in topic:
        print("checking for new departure info")
        collected_data["departure_info"] = payload
        if payload and "pubtr" in payload:
            warn_delays_or_cancellations(payload)

    return


def get_departures_for_station(all_departure_info:dict, station_main_label: str) -> List[DepartureInfo]:
    departures = list(filter(
        lambda station: station.get("mainLabel") == station_main_label,
        all_departure_info.get("pubtr")
    ))[0].get("departures")

    for dep in departures:
        dep["station"] = station_main_label
        try:
            for delete_me in  [key for key in dep.keys() if key not in ["delay", "destination", "cancelled", "datetime", "station"]]:
                # del changing, but unncessary props that make comparison hard
                del dep[delete_me]
        except:
            continue

        

    return [DepartureInfo(**dep) for dep in departures]


def warn_delays_or_cancellations(payload):
    # debug print
    print("no updates", datetime.now(), get_departures_for_station(payload, "Ernst-August-Schleuse"))

    if updated_departures := check_for_depature_updates(payload):
        for update in updated_departures:
            # check for delay
            if update.effective_delay_min >= 5 and int(update.delay) >= 3:  # update.delay -> delay since last communicated delay
                post_message_to_telegram(
                    f"Die Fähre mit Abfahrtszeit um {update.schedule_departure_time_str} hat {update.effective_delay_min} Min. Verspätung"
                )
            # check for cancellation
            if update.cancelled:
                msg = f"Die Fähre mit planm. Abfahrtszeit um {update.schedule_departure_time_str} fährt nicht von Ernst-August-Schleuse."
                
                if update.matching_argentina_dep:
                    if update.matching_argentina_dep.cancelled:
                        msg = f"{msg} Auch nicht von Argentinienbrücke. (Fällt komplett aus!)"
                    else:
                        msg = f"{msg} Abfahrt Argentinienbrücke: {update.matching_argentina_dep.effective_dep_time_str}"
                post_message_to_telegram(msg)

            else:
                # previously cancelled, but now running.
                msg = f"Die Fähre mit planm. Abfahrtszeit um {update.schedule_departure_time_str} fährt jetzt doch von Ernst-August! Um {update.effective_dep_time_str}"
                post_message_to_telegram(msg)

    """
    [{'city': 'hamburg', 'datetime': '21:45', 'delay_0': '0', 'destination': 'Landungsbrücken', 'img': './images/73.svg', 'label-1': 'Landungsbrücken', 'line': '73', 'providerName': 'hvv', 'time': 8, 'timeMinForSorting': 8}]
    """

def find_matching_argentina_departure(ernst_dep: DepartureInfo, argentina_deps: List[DepartureInfo]) -> DepartureInfo|None:
    for argentina_dep in argentina_deps:
        if 0 < (argentina_dep.effective_dep_time - ernst_dep.effective_dep_time).total_seconds() <= 300:
            return argentina_dep


def check_for_depature_updates(payload: dict) -> List[DepartureInfo]:
    received_departures_ernst :List[DepartureInfo] = get_departures_for_station(payload, "Ernst-August-Schleuse")
    received_departures_argentinien : List[DepartureInfo] = get_departures_for_station(payload, "Argentinienbrücke")
    updates_to_communicate = []

    # datetime is changing. 
    # iterate over all known departures and replace? 

    for new_dep_info in received_departures_ernst:
        # first try to find matching argentina departures
        new_dep_info.matching_argentina_dep = find_matching_argentina_departure(new_dep_info, received_departures_argentinien)

    for new_dep_info in received_departures_ernst:
        timestr = new_dep_info.schedule_departure_time_str
        fallback_timestr = (new_dep_info.effective_dep_time - timedelta(minutes=1)).strftime("%H:%M")  # sometimes is set as a minute later, i dont know why
        # try to find know info to check for relevant updates to that info
        old_dep_info: DepartureInfo|None = known_departure_infos.get(timestr, known_departure_infos.get(fallback_timestr, None))
        
        if not old_dep_info:
            if not new_dep_info.cancelled and new_dep_info.effective_delay_min < 5:
                # irrelevant depature info
                continue

            elif not new_dep_info.matching_argentina_dep:
                # wait for argentinienbrücken info. it will be communicated in a few min.
                continue 

        else:
            # relevant update to a known delayed/cancelled departure?
            if (new_dep_info.effective_dep_time - old_dep_info.effective_dep_time).total_seconds() < 180:
                if old_dep_info.cancelled == new_dep_info.cancelled:
                    # no news on the actual departure, 
                    # check if we got news, whether the ferry goes from argentinienbrücke:
                    if old_dep_info.matching_argentina_dep == new_dep_info.matching_argentina_dep:
                        # also no updates on whether the ferry goes from argentinienbrücke instead
                        continue

            # updated argentina info.
            if (new_dep_info.matching_argentina_dep.effective_delay_min - old_dep_info.matching_argentina_dep.effective_delay_min) < 5 \
            and new_dep_info.matching_argentina_dep.cancelled == old_dep_info.matching_argentina_dep.cancelled:
                # irrelevant update
                continue

        # save and communicate updated info
        known_departure_infos[timestr] = new_dep_info
        updates_to_communicate.append(new_dep_info)

    # return new/changed departures
    return updates_to_communicate


def forward_running_text_if_relevant(payload):
    """
    Running Text Content Updated [{'id': 578, 'company_id': 6, 'user_id': 12, 'text': 'Aufgrund eines Rettungseinsatzes, kann der Fähranleger Dockland bis auf Weiteres nicht angelaufen werden!', 'start_date': '2025-01-20T00:00:00.000', 'end_date': '2025-01-20T13:59:00.000', 'enable_undefined_end_date': False, 'display_criteria': '', 'selected_lines': '', 'status': 'archive', 'created_at': '2025-01-20 08:03:17.514512+00:00', 'week_days': 'monday'}, {'id': 607, 'company_id': 6, 'user_id': 148, 'text': 'Achtung +++ Aufgrund des Streiks bei der HADAG ab Donnerstag, den 13. März 2025, 04:00 Uhr bis Samstag, den 15. März 2025 04:00 Uhr, müssen wir aktuell davon ausgehen, dass der Fährbetrieb nicht aufgenommen werden kann +++', 'start_date': '2025-03-12T12:10:00.000', 'end_date': '2025-03-15T03:59:00.000', 'enable_undefined_end_date': False, 'display_criteria': '', 'selected_lines': '', 'status': 'archive', 'created_at': '2025-02-25 17:11:54.461988+00:00', 'week_days': 'sunday,monday,tuesday,wednesday,thursday,friday,saturday'}]
    """
    for run_text in payload:
        if datetime.strptime(run_text.get("end_date"), "%Y-%m-%dT%H:%M:%S.%f") < datetime.now():
            # post outdated
            continue

        if not datetime.now().strftime("%A").lower() in [day.lower() for day in run_text.get("week_days").split(",")]:
            # not valid for current weekday
            continue

        text = run_text.get("text")
        if not any(sub for sub in ["73", "ernst", "argentinien", "hadag", "streik"] if sub in text.lower()):
            # Text not for ferry 73
            print("irrelevant: " , text)
            continue

        # check if text already known
        with open("known_status_text.json", "r") as f:
            known_texts = json.load(f)
            f.close()

        if text not in known_texts:
            # post it to telegram
            post_message_to_telegram(f"HADAG Meldung: {text}")
            # add dict to array of dicts and save it
            known_texts.append(text)
            with open("known_status_text.json", "w") as fp:
                json.dump(known_texts, fp)


def mqtt_client_loop():
    # Set up MQTT client
    client = mqtt.Client(transport="websockets")
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.tls_set()
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"Connecting to {MQTT_BROKER}:{MQTT_PORT}...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    try:
        while True:
            # Start the loop
            client.loop_start()

            # Wait for data collection
            print(f"Waiting for {60} seconds to collect data...")
            time.sleep(60)
    except Exception as e:
        post_message_to_telegram(
            f"Error while checking mqtt: {e}", post_to_admin_group=True
        )


if __name__ == "__main__":
    mqtt_client_loop()