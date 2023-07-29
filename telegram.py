import os
import requests
import datetime
from dotenv import load_dotenv


load_dotenv()

CHAT_ID_USER_GROUP = os.environ.get("CHAT_ID_USER_GROUP")
CHAT_ID_ADMIN_GROUP = os.environ.get("CHAT_ID_ADMIN_GROUP")
BOT_TOKEN = os.environ.get("BOT_TOKEN_TELEGRAM")


def post_message_to_telegram(msg, post_to_admin_group=False):
    print(f"posting to telegram at {str(datetime.datetime.now())}")
    print(msg)
    chat_id = CHAT_ID_USER_GROUP
    if post_to_admin_group:
        chat_id = CHAT_ID_ADMIN_GROUP

    msg = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={msg}"

    try:
        response = requests.get(msg)
        if response.status_code != 200:
            print("could not forward to telegram")
            print("Error code", response.status_code)
            print("Error text", response.text)
            return False
    except requests.exceptions.RequestException as e:
        print(f"could not forward to telegram{str(e)}")
        print(f"this was the message I tried to send: {msg}")
