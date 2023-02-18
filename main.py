from string import Template
import time
import datetime
from forecasts import TideData, check_for_new_data
from telegram import post_message_to_telegram
from tweets import get_latest_hadag_tweet_today
from service_time import during_service_time


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
    post_message_to_telegram("started")


    first_run = True
    last_twitter_message = None
    end_time_last_disruption = None
    
    tide_data = TideData()
    
    while True:
        # during ferry times: check if tide is too high
        if during_service_time(datetime.datetime.now()):
            if check_for_new_data(tide_data.forecast_creation_date) or first_run:
                if hasattr(tide_data, 'disruption_period') \
                   and during_service_time(tide_data.disruption_period.start_time):
                    if first_run:
                        post_message_to_telegram(tide_data.get_disruption_warn_msg())
                    else:
                        if end_time_last_disruption < tide_data.disruption_period.end_time:
                            post_message_to_telegram(tide_data.get_disruption_warn_msg())

                    end_time_last_disruption = tide_data.disruption_period.end_time
                
        # check tweets
        try:
            latest_tweet = get_latest_hadag_tweet_today()
            if last_twitter_message != latest_tweet:
                post_message_to_telegram(latest_tweet)
                last_twitter_message = latest_tweet
        except Exception as e:
            print(e)
            pass
      
        time.sleep(60)