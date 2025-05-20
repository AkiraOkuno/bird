import requests
import random
import os
from telegram_utils import send_image_message

API_URL = "https://restcountries.com/v3.1/all"

def fetch_country():
    try:
        res = requests.get(API_URL)
        if res.status_code != 200:
            print(f"[COUNTRY] API failed: {res.status_code}", flush=True)
            return None

        countries = res.json()
        country = random.choice(countries)

        name = country.get("name", {}).get("common", "Desconhecido")
        capital = country.get("capital", ["Desconhecida"])[0]
        population = country.get("population", 0)
        area = country.get("area", 0)
        region = country.get("region", "Desconhecida")
        languages = ", ".join(country.get("languages", {}).values()) or "Desconhecido"

        currencies_data = country.get("currencies", {})
        currencies = []
        for code, data in currencies_data.items():
            currencies.append(f"{data.get('name', 'Moeda')} ({code})")
        currencies_str = ", ".join(currencies) if currencies else "Desconhecida"

        flag_url = country.get("flags", {}).get("png")

        caption = (
            f"🌍 *País do Dia:* {name}\n"
            f"🏙️ Capital: {capital}\n"
            f"👥 População: {population:,}\n"
            f"📏 Área: {int(area):,} km²\n"
            f"🗣️ Idioma(s): {languages}\n"
            f"💰 Moeda(s): {currencies_str}"
        )

        return flag_url, caption

    except Exception as e:
        print(f"[COUNTRY] Exception: {e}", flush=True)
        return None, None

def generate():
    flag_url, caption = fetch_country()
    if not flag_url or not caption:
        return "⚠️ Não foi possível carregar o país do dia."

    chat_ids = os.environ["CHAT_IDS"].split(",")
    for chat_id in chat_ids:
        send_image_message(chat_id.strip(), flag_url, caption)

    # 2. Send photos of tourist spots in that country
    country_name = caption.split("*País do Dia:*")[-1].split("\n")[0].strip()
    photo_urls = get_place_images_for_country(country_name, max_photos=5)

    for url in photo_urls:
        for chat_id in chat_ids:
            send_image_message(chat_id.strip(), url, f"📸 Imagem de {country_name}")

    return None











