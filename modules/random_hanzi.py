import pandas as pd
import random
import os

def load_hanzi_csv():
    path = "data/chinese characters.csv"
    return pd.read_csv(path)

def get_random_hanzi():
  
    df = load_hanzi_csv()
    row = df.sample(1).iloc[0]

    return {
        "char": row["Character"],
        "pinyin": row["Pronounciation"],
        "meaning": row["Meaning"],
        "radical": row["Radical"],
        "standard": row["General standard #"],
        "hsk": row["HSK 3.0"],
        "strokes": row["Stroke count"],
        "frequency":row["Frequency"]
    }

def format_hanzi_for_telegram(hanzi):
    return (
        f"🈶 *Caractere Chinês do Dia*\n\n"
        f"```\n  {hanzi['char']}  \n```"
        f"\n🔊 *Pronúncia:* `{hanzi['pinyin']}`"
        f"\n📝 *Significado:* _{hanzi['meaning']}_"
        f"\n\n🧬 *Radical:* `{hanzi['radical']}`"
        f"\n🔢 *Traços:* `{hanzi['strokes']}`"
        f"\n📊 *Frequência:* `{hanzi['frequency']}`"
        f"\n📚 *HSK:* `{hanzi['hsk']}`"
        f"\n📖 *Padrão:* `{hanzi['standard']}`"
    )

def generate():
  hanzi = get_random_hanzi()
  caption = format_hanzi_for_telegram(hanzi)
  return caption
  
  
