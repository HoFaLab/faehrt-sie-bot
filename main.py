import datetime
import time

import pytz
from bs4 import BeautifulSoup

from forecasts import TideData, check_for_new_data
from nitter_soup import get_nitter_soup
from telegram import post_message_to_telegram
from tweets import Tweet, find_latest_tweet_for_line_73_in_soup
from typing import Optional


def find_newer_tweet(soup: BeautifulSoup, known_tweet: Optional[Tweet]) -> Tweet:
    """
    returns any tweet newer than the latest known tweet
    """
    if tweet_now := find_latest_tweet_for_line_73_in_soup(soup):
        # latest_tweet == None -> bot was likely restarted
        if not known_tweet:
            # do not send outdated tweets
            return tweet_now
        if tweet_now.created_at > known_tweet.created_at:
            # found a tweet newer than the latest known
            return tweet_now

        # tweet already known
        print(datetime.datetime.now(tz=pytz.timezone("Europe/Berlin")).strftime("%Y-%m-%d %H:%M:%S"))
        print("Tweet already known")
        print(f" known_tweet {known_tweet}")
        print(f" tweet_now {tweet_now}")
            


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

    latest_known_tweet = None
    end_time_last_disruption = None
    tide_data = None

    while True:
        # check tide
        try:
            if not tide_data or check_for_new_data(tide_data.forecast_creation_date):
                tide_data = TideData()
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

        # check tweets
        try:
            soup = get_nitter_soup()
            if newer_tweet := find_newer_tweet(soup, latest_known_tweet):
                if newer_tweet.is_younger_than_2_hours():
                    post_message_to_telegram(newer_tweet.format_tweet_msg_for_telegram())
                latest_known_tweet = newer_tweet
        except Exception as e:
            print(e)
            post_message_to_telegram(
                f"Error while checking twitter: {e}", post_to_admin_group=True
            )

        time.sleep(180)
