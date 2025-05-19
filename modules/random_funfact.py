import requests
import os
from telegram_utils import send_telegram_message

API_URL = "https://uselessfacts.jsph.pl/random.json?language=en"

def fetch_fact():
    try:
        res = requests.get(API_URL)
        if res.status_code != 200:
            print(f"[FACT] Failed to fetch: {res.status_code}", flush=True)
            return None

        data = res.json()
        return data.get("text")
    except Exception as e:
        print(f"[FACT] Exception: {e}", flush=True)
        return None

def generate():
    fact = fetch_fact()
    if fact:
        return f"🧠 *Fun fact: *\n_{fact}_"
    else:
        return "⚠️ Não consegui encontrar um fato interessante hoje."
