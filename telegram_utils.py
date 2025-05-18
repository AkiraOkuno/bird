import requests
import os

def send_telegram_message(text):
    token = os.environ["TELEGRAM_TOKEN"]
    chat_ids = os.environ["CHAT_IDS"].split(",")

    for chat_id in chat_ids:
        res = requests.get(
            f"https://api.telegram.org/bot{token}/sendMessage",
            params={"chat_id": chat_id.strip(), "text": text}
        )
        print(f"Sent to {chat_id.strip()}: {res.status_code}, {res.text}")
