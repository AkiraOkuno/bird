from random_word import RandomWords
from PyDictionary import PyDictionary

def generate():
    r = RandomWords()
    dictionary = PyDictionary()

    for _ in range(10):  # Try up to 10 words
        try:
            word = r.get_random_word()
            if not word:
                continue

            meaning = dictionary.meaning(word)

            if meaning:
                part_of_speech = next(iter(meaning))
                definition = meaning[part_of_speech][0]
                return f"📚 *Word of the Day:* {word}\n_{part_of_speech}_: {definition}"
        except Exception as e:
            continue

    return f"The word is {word}, but ⚠️ could not find definition today."
