import os
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup
import json
import datetime

from string import Template
from dataclasses import dataclass
from typing import List


load_dotenv()

BEARER_TOKEN_TWITTER = os.environ.get("BEARER_TOKEN_TWITTER")
latest_tweet = None


@dataclass
class Tweet:
    created_at: str
    full_text: str
    hashtags: List[str]

    def get_timestamp_as_datetime(self):
        return datetime.datetime.strptime(self.created_at, "%a %b %d %H:%M:%S %z %Y")

    def format_tweet_msg_for_telegram(self):
        msg_template = Template(
            """🐦🐦🐦 HADAG twittert um $tweet_time 🐦🐦🐦 \n
            $tweet_text \n
            """
        )

        return msg_template.safe_substitute(
            {
                "tweet_time": self.get_timestamp_as_datetime().strftime("%Y-%m-%d %H:%M:%S"),
                "tweet_text": self.full_text.replace("#", ""),
            }
        )


def get_latest_tweet_for_line73() -> Tweet:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Accept": "text/json,application/json,application/json;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "de-DE,en;q=0.5",
        # 'Accept-Encoding': 'gzip, deflate, br',
        "Connection": "keep-alive",
    }

    params = {
        "showReplies": "true",
    }
    response = requests.get(
        "https://syndication.twitter.com/srv/timeline-profile/screen-name/hadag_info?showReplies=true",
        params=params,
        headers=headers,
    )

    soup = BeautifulSoup(response.text, features="html.parser")
    try:
        data = json.loads(soup.find("script", id="__NEXT_DATA__").text)
    except Exception:
        print("cannot read twitter stream")
        return None

    entries = data["props"]["pageProps"]["timeline"]["entries"]
    for entry in entries:
        if entry["type"] == "tweet":
            tweet = entry["content"]["tweet"]
            hashtags = [hashtag["text"] for hashtag in tweet["entities"]["hashtags"]]

            if "Linie73" in hashtags:
                return Tweet(
                    full_text=tweet["full_text"],
                    created_at=tweet["created_at"],
                    hashtags=hashtags,
                )


if __name__ == "__main__":
    print(BEARER_TOKEN_TWITTER)
    print(get_latest_tweet_for_line73().get_timestamp_as_datetime())
