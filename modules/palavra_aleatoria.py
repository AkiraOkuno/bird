import requests
import xml.etree.ElementTree as ET
from utils.retry import try_with_retries

API_RANDOM = "https://dicionario-aberto.net/random"
API_WORD = "https://dicionario-aberto.net/word/{}"

def fetch_definition_pt():
    try:
        # Step 1: Get a random word
        res = requests.get(API_RANDOM)
        if res.status_code != 200 or not res.content:
            print(f"[PT] Failed to get random word", flush=True)
            return None

        try:
            word = res.json().get("word")
        except Exception:
            print(f"[PT] Failed to parse JSON from /random", flush=True)
            return None

        print(f"[PT] Trying word: {word}", flush=True)

        # Step 2: Get definition for that word
        res2 = requests.get(API_WORD.format(word))
        if res2.status_code != 200 or not res2.content:
            print(f"[PT] Failed to get definition for: {word}", flush=True)
            return None

        try:
            data = res2.json()
        except Exception:
            print(f"[PT] Failed to parse JSON for word: {word}", flush=True)
            return None

        if not data or "xml" not in data[0]:
            print(f"[PT] No XML content found for: {word}", flush=True)
            return None

        xml = data[0]["xml"]
        root = ET.fromstring(xml)

        # Try to extract the first <def> tag
        definition = root.find(".//def")
        if definition is not None and definition.text and len(definition.text.strip()) > 5:
            return f"📖 **Palavra do Dia:** {word}\n__Definição__: {definition.text.strip()}"
        else:
            print(f"[PT] No definition found in XML for: {word}", flush=True)
            return None

    except Exception as e:
        print(f"[PT] Exception occurred: {e}", flush=True)
        return None


def generate():
    result = try_with_retries(fetch_definition_pt, attempts=10, delay=5)
    return result or "⚠️ Não foi possível encontrar uma definição hoje."
