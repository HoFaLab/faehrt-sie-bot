from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
import time
from typing import List
from string import Template

def set_up_driver():
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


def get_latest_hadag_tweet() -> List[str]:
    driver = set_up_driver()
    target_url = "https://twitter.com/hadag_info"
    driver.get(target_url)
    time.sleep(2)

    resp = driver.page_source
    driver.quit()

    soup=BeautifulSoup(resp,'html.parser')
    tweet_divs = soup.find_all("div",{"data-testid": "tweetText"})

    newest_tweet = [tweet.text for tweet in tweet_divs if "#Linie73" in tweet.text or "Linie 73" in tweet.text][0]
    
    msg_template = Template(
        """🐦🐦🐦 HADAG twittert um ca. $tweet_time 🐦🐦🐦 \n
        $tweet_text $tweet_link \n
        """
    )

    return msg_template.safe_substitute({
        "tweet_time": datetime.now().strftime("%H:%M"),
        "tweet_text": newest_tweet.replace('#', ''),
        "tweet_link": "twitter.com/hadag_info"
    })
    

if __name__ == "__main__":

    print(get_latest_hadag_tweet())
