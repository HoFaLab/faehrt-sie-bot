import tweepy
import os
from dotenv import load_dotenv

load_dotenv()

BEARER_TOKEN = os.environ.get("BEARER_TOKEN")


def get_latest_hadag_tweets():
    print(BEARER_TOKEN)
    
    client = tweepy.Client(BEARER_TOKEN)

    response = client.get_users_tweets(id="1024984536688615424", tweet_fields="created_at")
    tweets = response.data

    for tweet in tweets:
        if "73" in tweet.text:
            print(tweet.text)
            print(tweet.created_at)
            

if __name__ == "__main__":

    get_latest_hadag_tweets()
