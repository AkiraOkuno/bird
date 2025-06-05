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
        res = requests.get(API_URL, timeout=10)
        if res.status_code != 200:
            print(f"[COUNTRY] API failed: {res.status_code}", flush=True)
            # Always return three values
            return None, None, None

        countries = res.json()
        country = random.choice(countries)

        # 1) Country names
        name = country.get("name", {}).get("common", "Desconhecido")

        # 2) Safe native name extraction
        native_name_dicts = list(country.get("nativeName", {}).values())
        if native_name_dicts:
            native = native_name_dicts[0]
            official_name = native.get("official", "Desconhecido")
            common_name  = native.get("common",  "Desconhecido")
        else:
            official_name = "Desconhecido"
            common_name   = "Desconhecido"

        # 3) Capital, population, area, region, languages
        capital    = country.get("capital", ["Desconhecida"])
        capital    = capital[0] if capital else "Desconhecida"
        population = country.get("population", 0)
        area       = country.get("area", 0)
        region     = country.get("region", "Desconhecida")
        langs      = country.get("languages", {}) or {}
        languages  = ", ".join(langs.values()) if langs else "Desconhecido"

        # 4) Currencies
        currencies_data = country.get("currencies", {}) or {}
        currencies = []
        for code, data in currencies_data.items():
            # some entries may be missing "name"
            curr_name = data.get("name", "Moeda")
            currencies.append(f"{curr_name} ({code})")
        currencies_str = ", ".join(currencies) if currencies else "Desconhecida"

        # 5) Flag URL
        flag_url = country.get("flags", {}).get("png")

        # 6) Wiki data
        additional_wiki_data = get_country_data(name)
        head_url      = None
        head_of_state = additional_wiki_data.get("head_of_state")
        title         = additional_wiki_data.get("stateTitle")
        head_url      = additional_wiki_data.get("stateImage")
        gov_type      = additional_wiki_data.get("governmentType")

        # 7) Build the caption
        caption = (
            f"🗺️ *País do Dia:* {name}\n"
            f"🗣️ *Nome local (comum):* {common_name}\n"
            f"🏛️ *Nome local (oficial):* {official_name}\n"
            f"🏙️ Capital: {capital}\n"
            f"👥 População: {population:,}\n"
            f"📏 Área: {int(area):,} km²\n"
            f"🗣️ Idioma(s): {languages}\n"
            f"💰 Moeda(s): {currencies_str}"
        )
        if head_of_state:
            caption += f"\n👤 Chefe de Estado: {head_of_state}"
            if title:
                caption += f"\n🏷️ Título: {title}"
        if gov_type:
            caption += f"\n🏛️ Tipo de Governo: {gov_type}"

        print(f"[COUNTRY] Selected country: {name}")
        print(f"[COUNTRY] flag_url = {flag_url}, head_url = {head_url}")
        print(f"[COUNTRY] Caption:\n{caption}")

        return flag_url, head_url, caption

    except Exception as e:
        print(f"[COUNTRY] Exception: {e}", flush=True)
        # Always return exactly three values, even on exception
        return None, None, None


def generate():
    flag_url, head_url, caption = fetch_country()

    if not flag_url or not caption:
        # We couldn’t get three valid values, so return an error message
        return "⚠️ Não foi possível carregar o país do dia."

    chat_ids = os.environ.get("CHAT_IDS", "").split(",")

    # Send flag and country info
    for chat_id in chat_ids:
        chat_id = chat_id.strip()
        if not chat_id:
            continue
        print(f"[SEND] Flag to {chat_id} -> {flag_url}")
        send_image_message(chat_id, flag_url, caption)
        if head_url:
            print(f"[SEND] Head of state to {chat_id} -> {head_url}")
            send_image_message(chat_id, head_url, "👤 Chefe de Estado do País")

    # Extract country name from caption to pass to Google Places
    # (we know it's after “*País do Dia:* ” in the first line)
    country_name = caption.split("*País do Dia:*")[-1].split("\n")[0].strip()

    # ─── Tourist places ───────────────────────────────────────────
    try:
        tourist_photo_entries = get_random_tourist_photos(country_name, max_photos=2)
    except Exception as e:
        print(f"[CITIES] Error fetching tourist photos: {e}", flush=True)
        tourist_photo_entries = []

    for entry in tourist_photo_entries:
        place_name = entry.get("place_name", "Destino")
        address    = entry.get("address",   "Endereço desconhecido")
        entry_caption = f"📸 *{place_name}*\n📍 {address}"
        if entry.get("trivia"):
            entry_caption += f"\n🧠 {entry['trivia']}"
        if entry.get("maps_url"):
            entry_caption += f"\n🔗 [Ver no Google Maps]({entry['maps_url']})"

        for chat_id in chat_ids:
            chat_id = chat_id.strip()
            if not chat_id:
                continue
            print(f"[SEND] Tourist photo to {chat_id} -> {entry.get('image_url')}")
            send_image_message(chat_id, entry.get("image_url"), entry_caption)

    # ─── City photos ──────────────────────────────────────────────
    curated_photos = []
    found_cities   = 0

    try:
        cities = get_random_cities_for_country(country_name, max_results=100)
    except Exception as e:
        print(f"[CITIES] Error fetching cities list: {e}", flush=True)
        cities = []

    if cities:
        print(f"[CITIES] Trying curated cities: {cities}")
        for city in cities:
            try:
                photos = get_city_photos_from_name(country_name, city_name=city, max_photos=1)
            except Exception as e:
                print(f"[CITIES] Error fetching photos for {city}: {e}", flush=True)
                photos = []

            if photos:
                curated_photos += photos
                found_cities += 1
                print(f"[CITIES] Found {len(photos)} photos for {city}")
            else:
                print(f"[CITIES] No photos for {city}")

            if found_cities >= 2:
                break

    # Fallback if fewer than 2 curated photos found
    if len(curated_photos) < 2:
        needed   = 2 - len(curated_photos)
        try:
            fallback = get_random_city_photos(country_name, max_photos=needed)
        except Exception as e:
            print(f"[CITIES] Error fetching fallback city photos: {e}", flush=True)
            fallback = []

        print(f"[CITIES] Using {len(fallback)} fallback photos")
        curated_photos += fallback

    for entry in curated_photos:
        place_name = entry.get("place_name", "Destino")
        address    = entry.get("address",   "Endereço desconhecido")
        entry_caption = f"📸 *{place_name}*\n📍 {address}"
        if entry.get("trivia"):
            entry_caption += f"\n🧠 {entry['trivia']}"
        if entry.get("maps_url"):
            entry_caption += f"\n🔗 [Ver no Google Maps]({entry['maps_url']})"

        for chat_id in chat_ids:
            chat_id = chat_id.strip()
            if not chat_id:
                continue
            send_image_message(chat_id, entry.get("image_url"), entry_caption)

    # ─── Restaurant ────────────────────────────────────────────────
    try:
        restaurant = get_random_restaurant_for_country(country_name)
    except Exception as e:
        print(f"[RESTAURANT] Error fetching restaurant: {e}", flush=True)
        restaurant = None

    if restaurant:
        rest_name = restaurant.get("name",    "Restaurante")
        rest_city = restaurant.get("city",    "Cidade desconhecida")
        rest_addr = restaurant.get("address", "Endereço desconhecido")
        rating    = restaurant.get("rating")
        entry_caption = (
            f"🍽️ *{rest_name}* (em {rest_city})\n"
            f"📍 {rest_addr}\n"
            f"⭐ Avaliação: {rating if rating else 'Sem nota'}"
        )
        if restaurant.get("maps_url"):
            entry_caption += f"\n🔗 [Ver no Google Maps]({restaurant['maps_url']})"

        for chat_id in chat_ids:
            chat_id = chat_id.strip()
            if not chat_id:
                continue
            print(f"[SEND] Restaurant to {chat_id} -> {restaurant.get('image_url')}")
            send_image_message(chat_id, restaurant.get("image_url"), entry_caption)

    return None
