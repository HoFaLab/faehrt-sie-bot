import os
from dotenv import load_dotenv

import requests
from bs4 import BeautifulSoup
import json
import datetime
import time

from string import Template
from dataclasses import dataclass
from typing import List
from selenium import webdriver


def set_up_selenium_driver() -> webdriver:
    """Start web driver"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    
    return driver


def get_twitter_content_json(driver: webdriver) -> dict:
    target_url = "https://syndication.twitter.com/srv/timeline-profile/screen-name/hadag_info?showReplies=true"
    driver.get(target_url)
    time.sleep(2)

    response = driver.page_source
    
    soup = BeautifulSoup(response, "html.parser")

    try:
        data = json.loads(soup.find("script", id="__NEXT_DATA__").text)
    except Exception:
        print("cannot read twitter stream")
        return None
    
    return data


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


def get_latest_tweet_for_line73(twitter_content_json: dict) -> Tweet:
    entries = twitter_content_json["props"]["pageProps"]["timeline"]["entries"]
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

    driver = set_up_selenium_driver()
    while True:

        twitter_content_json = get_twitter_content_json(driver)
        if tweet := get_latest_tweet_for_line73(twitter_content_json):
            print(tweet.get_timestamp_as_datetime())
        else:
            print(twitter_content_json)
            print(twitter_content_json["props"]["pageProps"]["timeline"]["entries"])
        time.sleep(5)
