import requests
import random
from bs4 import BeautifulSoup
from utils.retry import try_with_retries

WORDS_URL = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/pt/pt_full.txt"
word_list = []

def load_word_list():
    global word_list
    if word_list:
        return
    try:
        res = requests.get(WORDS_URL)
        words = [line.split()[0] for line in res.text.splitlines() if line]
        word_list = [w for w in words if w.isalpha() and len(w) > 3]
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

    url = f"https://pt.wiktionary.org/wiki/{word}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f"[PT] Page not found: {url}", flush=True)
            return None

        soup = BeautifulSoup(res.text, "html.parser")

        # Find first paragraph after first section heading
        content_div = soup.find("div", {"id": "mw-content-text"})
        paragraphs = content_div.find_all("p")

        for p in paragraphs:
            text = p.get_text(strip=True)
            if text and len(text) > 20:
                return f"📖 **Palavra do Dia:** {word}\n__Definição__: {text}"

        print(f"[PT] No good definition found on page.", flush=True)
        return None

    except Exception as e:
        print(f"[PT] Exception fetching page: {e}", flush=True)
        return None

def generate():
    result = try_with_retries(fetch_definition_pt, attempts=10, delay=5)
    return result or "⚠️ Não foi possível encontrar uma definição hoje."

