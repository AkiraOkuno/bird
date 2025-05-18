import requests
from random_word import RandomWords

def generate():
    r = RandomWords()

    for _ in range(5):  # Try up to 5 random words
        word = r.get_random_word()
        if not word:
            continue

        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        try:
            res = requests.get(url)
            if res.status_code != 200:
                continue

            data = res.json()
            meaning = data[0]["meanings"][0]
            part_of_speech = meaning["partOfSpeech"]
            definition = meaning["definitions"][0]["definition"]

            # Format using Markdown (not MarkdownV2)
            return f"📚 **Word of the Day:** {word}\n(__{part_of_speech}__): {definition}"
        except Exception:
            continue

    return "⚠️ Could not find a usable word with a definition today."
