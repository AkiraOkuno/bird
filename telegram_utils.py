import requests
import os

def send_telegram_message(text):
    token = os.environ["TELEGRAM_TOKEN"]
    chat_ids = os.environ["CHAT_IDS"].split(",")

    for chat_id in chat_ids:
        response = requests.get(
            f"https://api.telegram.org/bot{token}/sendMessage",
            params={
                "chat_id": chat_id.strip(),
                "text": text,
                "parse_mode": "Markdown"  # ✅ THIS is what enables **bold**, __italic__, etc.
            }
        )
        print(f"Sent to {chat_id.strip()}: {response.status_code}, {response.text}")
