import requests
from bs4 import BeautifulSoup
import datetime

from string import Template
from dataclasses import dataclass


@dataclass
class Tweet:
    created_at: str
    full_text: str

    def format_tweet_msg_for_telegram(self):
        msg_template = Template(
            """🐦🐦🐦 HADAG twittert um $tweet_time 🐦🐦🐦 \n
            $tweet_text \n
            """
        )

        return msg_template.safe_substitute(
            {
                "tweet_time": self.created_at.strftime("%H:%M"),
                "tweet_text": self.full_text.replace("#", ""),
            }
        )


def get_latest_tweet() -> Tweet:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        # 'Accept-Encoding': 'gzip, deflate, br',
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }

    response = requests.get("https://nitter.net/Hadag_info", headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    tweets = soup.find_all(class_="tweet-content media-body")

    def tweet_contains_73(tweet):
        return "73" in tweet.text

    relevants_tweets = [tweet for tweet in tweets if tweet_contains_73(tweet)]
    
    if relevants_tweets:
        newest_tweet = relevants_tweets[0]
        return Tweet(datetime.datetime.now(), newest_tweet.text)


if __name__ == "__main__":
    print(get_latest_tweet().full_text)
