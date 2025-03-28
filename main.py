import threading
import time

from forecasts import TideData, check_for_new_data
from mqtt_mobility_signage import mqtt_client_loop
from telegram import post_message_to_telegram




"""
from when to when is the tide to high / low? 
    -> starting time disruption
    -> end time disruption

     check if hwnw values are outside boudaries 
        if so , iterate over array of forecasts.
        -> save first time and value outside boundaries
        -> save last time and value outside boundaries
                    -> by checking if successor value is below boundaries

    foward all tweets
        add timeframe to tweet, if timeframe exists

"""
if __name__ == "__main__":
    post_message_to_telegram(
        "started", post_to_admin_group=True
    )  # todo post to some admin group only

    # Start mqtt connection for HADAG updates in separate thread
    mqtt_monitor = threading.Thread(target=mqtt_client_loop, daemon=True)
    mqtt_monitor.start()

    # Monitor tides
    end_time_last_disruption = None
    tide_data = TideData()

    while True:
        # check tide
        try:
            if check_for_new_data(tide_data.forecast_creation_date):
                if (
                        hasattr(tide_data, "disruption_period")
                        and tide_data.disruption_period.disruption_during_service_time()
                        and tide_data.disruption_period.get_disruption_length_minutes() > 30
                ):
                    # check disruption period is already known.
                    if (
                            not end_time_last_disruption
                            or end_time_last_disruption
                            < tide_data.disruption_period.end_time
                    ):
                        post_message_to_telegram(tide_data.get_disruption_warn_msg())

                    if tide_data.is_time_to_remind() and not tide_data.reminder_sent:
                        post_message_to_telegram(tide_data.get_reminder_msg())
                        tide_data.reminder_sent = True

                    end_time_last_disruption = tide_data.disruption_period.end_time
        except Exception as e:
            print(e)
            post_message_to_telegram(
                f"Error while checking tide: {e}", post_to_admin_group=True
            )

            time.sleep(180)
