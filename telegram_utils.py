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

def send_image_message(chat_id, image_url, caption=None):
    token = os.environ["TELEGRAM_TOKEN"]
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    print(f"[Image] Sent to {chat_id}: {response.status_code}")

def send_image_message_v2(chat_id, image_url, caption=None):
    token = os.environ["TELEGRAM_TOKEN"]
    telegram_url = f"https://api.telegram.org/bot{token}/sendPhoto"

    try:
        image_res = requests.get(image_url)
        if image_res.status_code != 200:
            print(f"[Image] Failed to fetch image: {image_res.status_code}")
            return

        files = {"photo": ("image.jpg", image_res.content)}
        data = {"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"}
        response = requests.post(telegram_url, data=data, files=files)
        print(f"[Image] Sent to {chat_id}: {response.status_code}")
        print(response.text)
    except Exception as e:
        print(f"[Image] Error: {e}")

def send_telegram_audio(link):
    token = os.environ["TELEGRAM_TOKEN"]
    chat_ids = os.environ["CHAT_IDS"].split(",")

    try:
        for chat_id in chat_ids:
            with open(f'xeno/{link}', 'rb') as audio:
                payload = {
                    'chat_id': chat_id,
                    #'title': link,
                    'parse_mode': 'HTML'
                }
                files = {
                    #'audio': audio.read(),
                    'audio': audio,
                }
                response = requests.post(
                    f"https://api.telegram.org/bot{token}/sendAudio",
                    data=payload, files=files).json()
    
            print(f"Sent to {chat_id.strip()}")
    except Exception as e:
        print(f"[Audio] Error: {e}")
