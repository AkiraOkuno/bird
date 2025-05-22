import requests
import random
import os
from bs4 import BeautifulSoup
from telegram_utils import send_image_message
from google_places_utils import (
    get_random_tourist_photos,
    get_random_city_photos,
    get_random_restaurant_for_country,
    get_random_cities_for_country,
    get_city_photos_from_name
)

API_URL = "https://restcountries.com/v3.1/all"

def fetch_country():
    try:
        res = requests.get(API_URL)
        if res.status_code != 200:
            print(f"[COUNTRY] API failed: {res.status_code}", flush=True)
            return None, None, None

        countries = res.json()
        country = random.choice(countries)

        name = country.get("name", {}).get("common", "Desconhecido")
        capital = country.get("capital", ["Desconhecida"])[0]
        population_raw = country.get("population", 0)
        area = country.get("area", 0)
        region = country.get("region", "Desconhecida")
        languages = ", ".join(country.get("languages", {}).values()) or "Desconhecido"

        currencies_data = country.get("currencies", {})
        currencies = []
        for code, data in currencies_data.items():
            currencies.append(f"{data.get('name', 'Moeda')} ({code})")
        currencies_str = ", ".join(currencies) if currencies else "Desconhecida"

        flag_url = country.get("flags", {}).get("png")

        # === Extra data via Wikidata ===
        wikidata_id = get_wikidata_id(name)
        extra = get_wikidata_government_info(wikidata_id, country_name=name)

        # Compose main message
        caption = (
            f"🌍 *País do Dia:* {name}\n"
            f"🏙️ Capital: {capital}\n"
            f"👥 População: {int(extra['population']):,} (em {extra['populationDate'][:10]})\n"
            f"📏 Área: {int(area):,} km²\n"
            f"🗣️ Idioma(s): {languages}\n"
            f"💰 Moeda(s): {currencies_str}\n"
            f"🏛️ Tipo de governo: {extra['governmentType']}\n"
            f"🧑‍⚖️ {extra['stateTitle']}: {extra['head_of_state'] or 'Desconhecido'}"
        )

        print(f"[COUNTRY] Selected: {name}")
        return flag_url, caption, extra["stateImage"]

    except Exception as e:
        print(f"[COUNTRY] Exception: {e}", flush=True)
        return None, None, None

def get_wikidata_id(country):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": country,
        "prop": "pageprops",
        "ppprop": "wikibase_item"
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    pages = resp.json()["query"]["pages"]
    page = next(iter(pages.values()))
    return page.get("pageprops", {}).get("wikibase_item")

def get_wikidata_government_info(wikidata_id, country_name):
    session = requests.Session()
    sparql = f"""
    SELECT ?pop ?popDate ?personLabel ?img WHERE {{
      wd:{wikidata_id} p:P1082 ?stmt.
      ?stmt ps:P1082 ?pop; pq:P585 ?popDate.
      OPTIONAL {{
        wd:{wikidata_id} wdt:P35 ?person.
        ?person rdfs:label ?personLabel FILTER(LANG(?personLabel)="en").
        OPTIONAL {{ ?person wdt:P18 ?img. }}
      }}
    }}
    ORDER BY DESC(?popDate)
    LIMIT 1
    """
    data = session.get(
        "https://query.wikidata.org/sparql",
        params={"query": sparql, "format": "json"},
        headers={"Accept": "application/sparql-results+json"}
    )
    data.raise_for_status()
    results = data.json()["results"]["bindings"]
    entry = results[0] if results else {}

    pop = entry.get("pop", {}).get("value", 0)
    pop_date = entry.get("popDate", {}).get("value", "unknown")
    head_name = entry.get("personLabel", {}).get("value")
    image_url = entry.get("img", {}).get("value")

    # Scrape Wikipedia infobox
    url = f"https://en.wikipedia.org/wiki/{country_name.replace(' ', '_')}"
    html = session.get(url).text
    soup = BeautifulSoup(html, "lxml")
    infobox = soup.find("table", class_="infobox")

    state_title = "Head of state"
    gov_type = "Unknown"
    if infobox:
        if head_name:
            for row in infobox.find_all("tr"):
                th = row.find("th")
                td = row.find("td")
                if th and td and head_name in td.get_text():
                    state_title = th.get_text().strip("•·.- ").strip()
                    break
        gov_row = infobox.find("th", string=lambda t: t and "Government" in t)
        if gov_row:
            gov_td = gov_row.find_next_sibling("td")
            if gov_td:
                gov_type = " ".join(gov_td.get_text(separator=" ", strip=True).split())

    return {
        "population": int(float(pop)),
        "populationDate": pop_date,
        "head_of_state": head_name,
        "stateImage": image_url,
        "stateTitle": state_title,
        "governmentType": gov_type
    }


def generate():
    flag_url, caption = fetch_country()
    if not flag_url or not caption:
        return "⚠️ Não foi possível carregar o país do dia."

    chat_ids = os.environ["CHAT_IDS"].split(",")

    # Send flag and country info
    for chat_id in chat_ids:
        print(f"[SEND] Flag to {chat_id.strip()} -> {flag_url}")
        send_image_message(chat_id.strip(), flag_url, caption)

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
