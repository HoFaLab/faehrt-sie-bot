import datetime
import time

from bs4 import BeautifulSoup
from main import find_newer_tweet
from tweets import Tweet
import datetime
from datetime import timedelta
import pytz

with open("fixtures/older_soup.html") as fp:
    older_soup = BeautifulSoup(fp, 'html.parser')

with open("fixtures/newer_soup.html") as fp:
    newer_soup = BeautifulSoup(fp, 'html.parser')


def test_first_tweet():
    latest_tweet = find_newer_tweet(soup=older_soup, known_tweet=None)
    assert type(latest_tweet) == Tweet


def test_no_new_tweet():
    latest_tweet = find_newer_tweet(soup=older_soup, known_tweet=None)
    assert find_newer_tweet(soup=older_soup, known_tweet=latest_tweet) is None


def test_new_tweet():
    older_tweet = find_newer_tweet(soup=older_soup, known_tweet=None)
    newer_tweet = find_newer_tweet(soup=newer_soup, known_tweet=older_tweet)

    assert type(newer_tweet) == Tweet
    assert older_tweet != newer_tweet
    assert newer_tweet.created_at > older_tweet.created_at


def test_tweet_younger_than_2_hours():
    # tweet from html
    newer_tweet = find_newer_tweet(soup=newer_soup, known_tweet=None)
    assert not newer_tweet.is_younger_than_2_hours()


    # test tweet with younger timestamp
    test_tweet_young = Tweet(
        datetime.datetime.now(tz=pytz.timezone("Europe/Berlin")) - timedelta(hours=1),
        "test text"
    )
    assert test_tweet_young.is_younger_than_2_hours()

    # test tweet with older timestamp
    test_tweet_old = Tweet(
        datetime.datetime.now(tz=pytz.timezone("Europe/Berlin")) - timedelta(hours=2, minutes=1),
        "test text"
    )
    assert not test_tweet_old.is_younger_than_2_hours()
