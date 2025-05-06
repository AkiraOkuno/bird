import requests
import random
import os

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_IDS = os.environ["CHAT_IDS"].split(",")  # Comma-separated list of chat IDs

num = random.randint(1, 100)
msg = f"🎲 Your daily random number: {num}"

for chat_id in CHAT_IDS:
    requests.get(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        params={"chat_id": chat_id.strip(), "text": msg}
    )
