import os
import requests
import datetime
from dotenv import load_dotenv


load_dotenv()

CHAT_ID = os.environ.get("CHAT_ID_TELEGRAM")
BOT_TOKEN = os.environ.get("BOT_TOKEN_TELEGRAM")


def post_message_to_telegram(msg):
    print("posting to telegram at " + str(datetime.datetime.now()))
    print(msg)

    msg = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage?chat_id=' + CHAT_ID + '&text=' + msg

    try:
        response = requests.get(msg)
        if not response.status_code == 200:
            print("could not forward to telegram")
            print("Error code", response.status_code)
            return False
    except requests.exceptions.RequestException as e:
        print("could not forward to telegram" + str(e))
        print("this was the message I tried to send: " + msg)
