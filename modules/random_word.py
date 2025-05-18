from random_word import RandomWords
from PyDictionary import PyDictionary

def generate():
    r = RandomWords()
    dictionary = PyDictionary()

    try:
        word = r.get_random_word()
        meaning = dictionary.meaning(word)

        if meaning:
            # Just grab the first definition of the first part of speech
            part_of_speech = next(iter(meaning))
            definition = meaning[part_of_speech][0]
            return f"📚 *Word of the Day:* {word}\n_{part_of_speech}_: {definition}"
        else:
            return "⚠️ Could not find a definition for the random word."
    except Exception as e:
        return f"❌ Error getting word of the day: {e}"
