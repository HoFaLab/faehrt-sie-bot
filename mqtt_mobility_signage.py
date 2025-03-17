from datetime import datetime
from typing import List

import paho.mqtt.client as mqtt
import json
import time
import argparse

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

departure_info = {}


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


def get_departures_for_station(all_departure_info:dict, station_main_label: str) -> List[dict]:
    departures = list(filter(
        lambda station: station.get("mainLabel") == station_main_label,
        all_departure_info.get("pubtr")
    ))[0].get("departures")

    for dep in departures:
        dep["day"] = datetime.now().day
        try:
            for delete_me in  [key for key in dep.keys() if key not in ["delay", "delay_0", "cancelled", "datetime", "day"]]:
                # del changing, but unncessary props that make comparison hard
                del dep[delete_me]
        except:
            continue

    return departures

def ferry_start_from_argentina(start_time_ernst_august: str, all_departure_info: dict):
    argentina_departures = get_departures_for_station(all_departure_info, "Argentinienbrücke")

    start_time_ernst_august_dt = datetime.strptime(start_time_ernst_august, "%H:%M")

    for departure in argentina_departures:
        if departure.get("cancelled", False):
            continue
        if abs(
            (
                datetime.strptime(departure.get("datetime"), "%H:%M")
                - start_time_ernst_august_dt
            ).total_seconds()
        ) <= 300:
            return departure.get("datetime")


def warn_delays_or_cancellations(payload):
    departures = get_departures_for_station(payload, "Ernst-August-Schleuse")

    if updated_departures := check_for_depature_updates(departures):
        for update in updated_departures:
            # check for delay
            if update.get("delay", 0) != 0 and int(update.get("delay")) > 0:
                post_message_to_telegram(
                    f"Die Fähre mit Abfahrtszeit um {update.get("datetime")} hat {update.get("delay")} Min. Verspätung"
                )
            # check for cancellation
            if update.get("cancelled", False):
                msg = f"Die Fähre mit Abfahrtszeit um {update.get("datetime")} fährt nicht"
                # check if goes from
                if argentina_start_time := ferry_start_from_argentina(update.get("datetime"), payload):
                    msg = f"{msg} von Ernst-August-Schleuse. Abfahrt Argentinienbrücke: {argentina_start_time}"
                else:
                    msg = f"{msg}! (Fällt komplett aus!)"

                post_message_to_telegram(msg)

    """
    [{'city': 'hamburg', 'datetime': '21:45', 'delay_0': '0', 'destination': 'Landungsbrücken', 'img': './images/73.svg', 'label-1': 'Landungsbrücken', 'line': '73', 'providerName': 'hvv', 'time': 8, 'timeMinForSorting': 8}]
    """

def check_for_depature_updates(received_departures:List[dict]):
    updates = []
    for new_dep_info in received_departures:
        timestr = new_dep_info.get("datetime")
        old_dep_info = departure_info.get(timestr)
        # save new info
        departure_info[timestr] = new_dep_info

        if old_dep_info != new_dep_info:
            updates.append(new_dep_info)

        # return new/changed departures
        return updates


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