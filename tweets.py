from bs4 import BeautifulSoup, Tag
import datetime
from pytz import timezone

from string import Template
from dataclasses import dataclass
from typing import Optional


@dataclass
class Tweet:
    created_at: datetime.datetime
    full_text: str

    def format_tweet_msg_for_telegram(self):
        msg_template = Template(
            """🐦🐦🐦 HADAG twittert um $tweet_time 🐦🐦🐦 \n
            $tweet_text \n
            """
        )

        return msg_template.safe_substitute(
            {
                "tweet_time": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "tweet_text": self.full_text.replace("#", ""),
            }
        )

    def is_younger_than_2_hours(self):
        return self.created_at + datetime.timedelta(hours=2) > datetime.datetime.now(tz=timezone("Europe/Berlin"))


def get_tweet_time_from_tag(tweet: Tag) -> datetime.datetime:
    date_string = tweet.find(class_="tweet-date").find("a").get("title")
    tweet_time = datetime.datetime.strptime(date_string, "%b %d, %Y · %I:%M %p %Z")
    tweet_time = tweet_time.replace(tzinfo=timezone("UTC"))

    return tweet_time.astimezone(timezone('Europe/Berlin'))


def find_latest_tweet_for_line_73_in_soup(soup: BeautifulSoup) -> Optional[Tweet]:
    tweets = soup.find_all(class_="tweet-body")

    for tweet in tweets:
        tweet_text_div = tweet.find(class_="tweet-content media-body")
        tweet_text = tweet_text_div.text

        if "73" in tweet_text:
            tweet_time = get_tweet_time_from_tag(tweet)

            return Tweet(tweet_time, tweet_text)
