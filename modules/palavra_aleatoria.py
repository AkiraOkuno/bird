import requests
import random
import string
from utils.retry import try_with_retries

def fetch_definition_pt():
    
    letter = random.choice(string.ascii_lowercase)
    print(f"[PT] Trying words starting with: {letter}")

    url = "https://pt.wiktionary.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "allpages",
        "apnamespace": 0,
        "aplimit": 500,
        "apprefix": letter
    }

    try:
        res = requests.get(url, params=params)
        pages = res.json()["query"]["allpages"]
        if not pages:
            print("[PT] No pages found")
            return None

        word = random.choice(pages)["title"]
        print(f"[PT] Trying word: {word}")

        extract_params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "titles": word,
            "exintro": True,
            "explaintext": True,
            "redirects": 1
        }

        res2 = requests.get(url, params=extract_params)
        data = res2.json()["query"]["pages"]
        extract = next(iter(data.values())).get("extract")

        if not extract or len(extract) < 20:
            print(f"[PT] No good extract for word: {word}")
            return None

        first_line = extract.split("\n")[0].strip()
        return f"📖 **Palavra do Dia:** {word}\n__Definição__: {first_line}"
        
    except Exception as e:
        print(f"[PT] Exception occurred: {e}")
        return None

def generate():
    return try_with_retries(fetch_definition_pt, attempts=2, delay=5)
