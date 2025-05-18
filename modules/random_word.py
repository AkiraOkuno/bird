import requests
from random_word import RandomWords
from utils.retry import try_with_retries

def fetch_definition():
    r = RandomWords()
    word = r.get_random_word()
    if not word:
        return None

    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            return None

        data = res.json()
        meaning = data[0]["meanings"][0]
        part_of_speech = meaning["partOfSpeech"]
        definition = meaning["definitions"][0]["definition"]

        return f"📚 **Word of the Day:** {word}\n(__{part_of_speech}__): {definition}"
    except Exception:
        return None

def generate():
    return try_with_retries(fetch_definition, attempts=10, delay=10)
