import tweepy
import os
from dotenv import load_dotenv
from string import Template
import datetime

load_dotenv()

BEARER_TOKEN_TWITTER = os.environ.get("BEARER_TOKEN_TWITTER")


def get_latest_hadag_tweet_today():
    client = tweepy.Client(BEARER_TOKEN_TWITTER)

    response = client.get_users_tweets(id="1024984536688615424", tweet_fields="created_at")
    tweets = response.data
    last_tweet_time = None

    for tweet in tweets:
        if "73" in tweet.text:
            if not last_tweet_time:
                last_tweet_time = tweet.created_at

            if tweet.created_at >= last_tweet_time:
                last_tweet_time = tweet.created_at
                newest_tweet = tweet

    
    if datetime.datetime.today().day == newest_tweet.created_at.day:
        msg_template = Template(
            """🐦🐦🐦 HADAG twittert um $tweet_time 🐦🐦🐦 \n
            $tweet_text $tweet_link \n
            """
        )

        return msg_template.safe_substitute({
            "tweet_time": newest_tweet.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "tweet_text": newest_tweet.text.replace('#', ''),
            "tweet_link": "twitter.com/hadag_info"
        })
    
    return None

            

if __name__ == "__main__":
    print(BEARER_TOKEN_TWITTER)
    print(get_latest_hadag_tweet_today())
