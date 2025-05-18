import requests
import random
from utils.retry import try_with_retries

WORDS_URL = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/pt/pt_full.txt"
word_list = []

def load_word_list():
    global word_list
    if word_list:
        return
    try:
        res = requests.get(WORDS_URL)
        word_list = [line.split()[0] for line in res.text.splitlines() if line]
        word_list = [w for w in word_list if w.isalpha() and len(w) > 3]  # filter out junk
        print(f"[PT] Loaded {len(word_list)} words.", flush=True)
    except Exception as e:
        print(f"[PT] Failed to load word list: {e}", flush=True)
        word_list = []

def get_random_word():
    if not word_list:
        return None
    return random.choice(word_list)

def fetch_definition_pt():
    load_word_list()
    word = get_random_word()
    if not word:
        return None

    print(f"[PT] Trying word: {word}", flush=True)

    api_url = f"https://api-dicionario-ptbr.fly.dev/{word}"
    try:
        res = requests.get(api_url)
        if res.status_code != 200 or not res.content:
            print(f"[PT] No result for {word}", flush=True)
            return None

        data = res.json()
        if not data or "significado" not in data[0]:
            return None

        definition = data[0]["significado"].strip()
        if not definition or len(definition) < 5:
            return None

        return f"📖 **Palavra do Dia:** {word}\n__Definição__: {definition}"
    except Exception as e:
        print(f"[PT] Exception fetching definition: {e}", flush=True)
        return None

def generate():
    result = try_with_retries(fetch_definition_pt, attempts=10, delay=5)
    return result or "⚠️ Não foi possível encontrar uma definição hoje."

