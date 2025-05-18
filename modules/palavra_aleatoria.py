import requests
import random
from utils.retry import try_with_retries

WORDS_URL = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/pt/pt_50k.txt"

def load_random_word():
    try:
        res = requests.get(WORDS_URL)
        words = [line.split()[0] for line in res.text.splitlines() if line]
        return random.choice(words)
    except Exception as e:
        print(f"[PT] Failed to load word list: {e}", flush=True)
        return None

def fetch_definition_pt():
    word = load_random_word()
    if not word:
        return None

    print(f"[PT] Trying word: {word}", flush=True)

    url = "https://pt.wiktionary.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "titles": word,
        "exintro": True,
        "explaintext": True,
        "redirects": 1
    }

    try:
        res = requests.get(url, params=params)
        data = res.json().get("query", {}).get("pages", {})
        extract = next(iter(data.values())).get("extract", "").strip()

        if extract and len(extract) >= 10:
            first_line = extract.split("\n")[0].strip()
            return f"📖 **Palavra do Dia:** {word}\n__Definição__: {first_line}"

        print(f"[PT] No extract for {word}", flush=True)
        return None
    except Exception as e:
        print(f"[PT] Exception fetching definition: {e}", flush=True)
        return None

def generate():
    result = try_with_retries(fetch_definition_pt, attempts=10, delay=5)
    return result or "⚠️ Não foi possível encontrar uma definição hoje."
