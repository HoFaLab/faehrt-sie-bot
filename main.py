import time
from forecasts import TideData, check_for_new_data
from telegram import post_message_to_telegram
from tweets import get_latest_hadag_tweet_today


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
    post_message_to_telegram("started")  # todo post to some admin group only

    last_twitter_message = None
    end_time_last_disruption = None
    tide_data = None
    
    while True:
        if not tide_data or check_for_new_data(tide_data.forecast_creation_date):
            tide_data = TideData()
            if hasattr(tide_data, 'disruption_period') \
                and tide_data.disruption_period.disruption_during_service_time(): 
                # check disruption period is already known.
                if not end_time_last_disruption \
                    or end_time_last_disruption < tide_data.disruption_period.end_time:
                    post_message_to_telegram(tide_data.get_disruption_warn_msg())
                
                if tide_data.is_time_to_remind() and not tide_data.reminder_sent():
                    post_message_to_telegram(tide_data.get_reminder_msg())
                    tide_data.reminder_sent = True

                end_time_last_disruption = tide_data.disruption_period.end_time
            
        # check tweets
        try:
            latest_tweet = get_latest_hadag_tweet_today()
            if last_twitter_message != latest_tweet:
                post_message_to_telegram(latest_tweet)
                last_twitter_message = latest_tweet
        except Exception as e:
            print(e)
            # post_message_to_telegram("Error while checking twitter", e)
            pass
      
        time.sleep(60)