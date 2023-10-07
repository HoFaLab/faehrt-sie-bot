from bs4 import BeautifulSoup
from main import find_newer_tweet
from tweets import Tweet

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
    newer_tweet = find_newer_tweet(soup=newer_soup, known_tweet=None)

    assert not newer_tweet.is_younger_than_2_hours()

