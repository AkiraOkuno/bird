import requests
import random
import os
from telegram_utils import send_image_message
from google_places_utils import get_random_tourist_photos, get_random_city_photos, get_random_restaurant_for_country

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
    
    tourist_photo_entries = get_random_tourist_photos(country_name, max_photos=5)
    
    for entry in tourist_photo_entries:
        caption = f"📸 *{entry['place_name']}*\n📍 {entry['address']}"
        if entry.get("trivia"):
            caption += f"\n🧠 {entry['trivia']}"
        if entry.get("maps_url"):
            caption += f"\n🔗 [Ver no Google Maps]({entry['maps_url']})"
        for chat_id in chat_ids:
            send_image_message(chat_id.strip(), entry["image_url"], caption)

    
    random_photos = get_random_city_photos(country_name, max_photos=5)

    for entry in random_photos:
        caption = f"📸 *{entry['place_name']}*\n📍 {entry['address']}"
        if entry.get("trivia"):
            caption += f"\n🧠 {entry['trivia']}"
        if entry.get("maps_url"):
            caption += f"\n🔗 [Ver no Google Maps]({entry['maps_url']})"
        for chat_id in chat_ids:
            send_image_message(chat_id.strip(), entry["image_url"], caption)


    restaurant = get_random_restaurant_for_country(country_name)
    if restaurant:
        caption = (
            f"🍽️ *{restaurant['name']}* (em {restaurant['city']})\n"
            f"📍 {restaurant['address']}\n"
            f"⭐ Avaliação: {restaurant['rating'] or 'Sem nota'}"
        )
        if restaurant.get("maps_url"):
            caption += f"\n🔗 [Ver no Google Maps]({entry['maps_url']})"
    
        for chat_id in chat_ids:
            send_image_message(chat_id.strip(), restaurant["image_url"], caption)
            
    return None











