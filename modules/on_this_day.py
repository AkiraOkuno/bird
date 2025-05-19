import requests
import random
from datetime import datetime

def fetch_event():
    today = datetime.utcnow()
    month = today.month
    day = today.day

    url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"

    try:
        res = requests.get(url, headers={"User-Agent": "DailyBot/1.0"})
        if res.status_code != 200:
            print(f"[HISTORY] API failed: {res.status_code}", flush=True)
            return None

        events = res.json().get("events", [])
        if not events:
            return None

        event = random.choice(events)
        year = event.get("year")
        text = event.get("text")

        return f"📜 *Neste dia (em {year}):*\n_{text}_"
    except Exception as e:
        print(f"[HISTORY] Exception: {e}", flush=True)
        return None

def generate():
    result = fetch_event()
    return result or "⚠️ Não consegui encontrar um evento histórico hoje."
