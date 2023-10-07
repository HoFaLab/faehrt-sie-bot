import requests
from bs4 import BeautifulSoup, Tag
import random

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

urls = [
    "https://nitter.cz/search?f=tweets&q=hadag_info",
    "https://nitter.unixfox.eu/search?f=tweets&q=Hadag_info",
    "https://nitter.privacydev.net/search?f=tweets&q=hadag_info",
    # "https://nitter.salastil.com/search?f=tweets&q=hadag_info",
    "https://nitter.perennialte.ch/search?f=tweets&q=hadag_info",
    "https://nitter.services.woodland.cafe/search?f=tweets&q=hadag_info",
    "https://nitter.d420.de/search?f=tweets&q=hadag_info",
    "https://nitter.privacydev.net/search?f=tweets&q=hadag_info"
]


def get_nitter_soup() -> BeautifulSoup:
    # randomly distribute requests to avoid blocking
    url = random.choice(urls)
    print(f"checking nitter url {url}")

    response = requests.get(url, headers=headers)

    return BeautifulSoup(response.content, "html.parser")
