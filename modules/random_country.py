import requests
import random
import os
from telegram_utils import send_image_message
from google_places_utils import (
    get_random_tourist_photos,
    get_random_city_photos,
    get_random_restaurant_for_country,
    get_random_cities_for_country,
    get_city_photos_from_name
)
from wiki_utils import get_country_data

API_URL = "https://restcountries.com/v3.1/all"

def fetch_country():
    try:
        res = requests.get(API_URL)
        if res.status_code != 200:
            print(f"[COUNTRY] API failed: {res.status_code}", flush=True)
            return None, None

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

        additional_wiki_data = get_country_data(name)

        head_url = None
        
        head_of_state = additional_wiki_data["head_of_state"]
        title = additional_wiki_data["stateTitle"]
        head_url = additional_wiki_data["stateImage"]
        gov_type = additional_wiki_data["governmentType"]

        print(additional_wiki_data)
        
        caption = (
            f"🌍 *País do Dia:* {name}\n"
            f"🏙️ Capital: {capital}\n"
            f"👥 População: {population:,}\n"
            f"📏 Área: {int(area):,} km²\n"
            f"🗣️ Idioma(s): {languages}\n"
            f"💰 Moeda(s): {currencies_str}"
        )

        # only add these lines if the value is not None or empty
        if head_of_state:
            caption += f"\n👤 Chefe de Estado: {head_of_state}"
            if title:
                caption += f"\n🏷️ Título: {title}"
        if gov_type:
            caption += f"\n🏛️ Tipo de Governo: {gov_type}"

        print(f"[COUNTRY] Selected country: {name}")
        return flag_url, head_url, caption

    except Exception as e:
        print(f"[COUNTRY] Exception: {e}", flush=True)
        return None, None

def generate():
    flag_url, head_url, caption = fetch_country()
    if not flag_url or not caption:
        return "⚠️ Não foi possível carregar o país do dia."

    chat_ids = os.environ["CHAT_IDS"].split(",")

    # Send flag and country info
    for chat_id in chat_ids:
        print(f"[SEND] Flag to {chat_id.strip()} -> {flag_url}")
        send_image_message(chat_id.strip(), flag_url, caption)
        if head_url:
            send_image_message(chat_id.strip(), head_url, "👤 Head of State of the Country")

    country_name = caption.split("*País do Dia:*")[-1].split("\n")[0].strip()

    # Tourist places
    tourist_photo_entries = get_random_tourist_photos(country_name, max_photos=2)
    for entry in tourist_photo_entries:
        caption = f"📸 *{entry['place_name']}*\n📍 {entry['address']}"
        if entry.get("trivia"):
            caption += f"\n🧠 {entry['trivia']}"
        if entry.get("maps_url"):
            caption += f"\n🔗 [Ver no Google Maps]({entry['maps_url']})"
        for chat_id in chat_ids:
            print(f"[SEND] Tourist photo to {chat_id.strip()} -> {entry['image_url']}")
            send_image_message(chat_id.strip(), entry["image_url"], caption)

    # Random cities from curated list
    curated_photos = []
    cities = get_random_cities_for_country(country_name, max_results=100)  # Increase max to allow more tries
    found_cities = 0
    
    if cities:
        print(f"[CITIES] Using curated cities: {cities}")
        for city in cities:
            photos = get_city_photos_from_name(country_name, city_name=city, max_photos=1)
            if photos:
                curated_photos += photos
                found_cities += 1
                print(f"[CITIES] Found {len(photos)} photos for {city}")
            else:
                print(f"[CITIES] No photos for {city}")
            if found_cities >= 2:
                break
    
    # Fallback if still less than 5 photos
    if len(curated_photos) < 2:
        needed = 2 - len(curated_photos)
        fallback = get_random_city_photos(country_name, max_photos=needed)
        print(f"[CITIES] Using {len(fallback)} fallback photos")
        curated_photos += fallback
    
    # Now send photos
    for entry in curated_photos:
        caption = f"📸 *{entry['place_name']}*\n📍 {entry['address']}"
        if entry.get("trivia"):
            caption += f"\n🧠 {entry['trivia']}"
        if entry.get("maps_url"):
            caption += f"\n🔗 [Ver no Google Maps]({entry['maps_url']})"
        for chat_id in chat_ids:
            send_image_message(chat_id.strip(), entry["image_url"], caption)

    # Restaurant
    restaurant = get_random_restaurant_for_country(country_name)
    if restaurant:
        caption = (
            f"🍽️ *{restaurant['name']}* (em {restaurant['city']})\n"
            f"📍 {restaurant['address']}\n"
            f"⭐ Avaliação: {restaurant['rating'] or 'Sem nota'}"
        )
        if restaurant.get("maps_url"):
            caption += f"\n🔗 [Ver no Google Maps]({restaurant['maps_url']})"

        for chat_id in chat_ids:
            print(f"[SEND] Restaurant to {chat_id.strip()} -> {restaurant['image_url']}")
            send_image_message(chat_id.strip(), restaurant["image_url"], caption)

    return None
