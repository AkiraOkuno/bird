import requests
import os
import random
import json
from urllib.parse import quote_plus

API_KEY = os.environ["GOOGLE_API_KEY"]
CITIES_PATH = "data/countries+cities.json"

def get_wikipedia_summary(title):
    try:
        res = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{title.replace(' ', '_')}", timeout=3)
        if res.status_code == 200:
            data = res.json()
            return data.get("extract")
    except Exception as e:
        print(f"[WIKI] {title} → {e}")
    return None

def get_random_tourist_photos(country_name, max_photos=5, max_results=50):
    """
    Fetch up to `max_photos` random tourist spot photos from top `max_results` Google Places results.
    Includes Wikipedia trivia if available.
    """
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    photo_url_template = "https://maps.googleapis.com/maps/api/place/photo"

    # Use a random query template to avoid repetition
    query_templates = [
        "famous tourist places in {}",
        "popular attractions in {}",
        "top things to see in {}",
        "sightseeing in {}",
        "historic landmarks in {}"
    ]
    query = random.choice(query_templates).format(country_name)

    res = requests.get(search_url, params={"query": query, "key": API_KEY})
    if res.status_code != 200:
        print(f"[PLACES] Query failed: {res.status_code}")
        return []

    results = res.json().get("results", [])
    if not results:
        print(f"[PLACES] No places found for {country_name}")
        return []

    # Shuffle and limit to top N
    random.shuffle(results)
    results = results[:max_results]

    selected_photos = []
    for place in results:
        name = place.get("name", "Lugar desconhecido")
        address = place.get("formatted_address", "")
        place_id = place.get("place_id")
        query = quote_plus(name)
        maps_url = (
            f"https://www.google.com/maps/search/?api=1"
            f"&query={query}&query_place_id={place_id}"
            if place_id else None
        )
        trivia = get_wikipedia_summary(name)

        for photo in place.get("photos", []):
            ref = photo.get("photo_reference")
            if ref:
                image_url = f"{photo_url_template}?maxwidth=1600&photoreference={ref}&key={API_KEY}"
                selected_photos.append({
                    "image_url": image_url,
                    "place_name": name,
                    "address": address,
                    "trivia": trivia,
                    "maps_url": maps_url
                })
                break  # one photo per place
        if len(selected_photos) >= max_photos:
            break

    return selected_photos

def get_random_city_photos(country_name, max_photos=5, max_results=50):
    """
    Fetch up to `max_photos` random city or town photos from within the given country.
    Includes Wikipedia trivia if available.
    """
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    photo_url_template = "https://maps.googleapis.com/maps/api/place/photo"

    query_templates = [
        "cities in {}",
        "towns in {}",
        "urban areas in {}",
        "districts in {}",
        "regions in {}"
    ]
    query = random.choice(query_templates).format(country_name)

    res = requests.get(search_url, params={"query": query, "key": API_KEY})
    if res.status_code != 200:
        print(f"[PLACES] City query failed: {res.status_code}")
        return []

    results = res.json().get("results", [])
    if not results:
        print(f"[PLACES] No cities found for {country_name}")
        return []

    random.shuffle(results)
    results = results[:max_results]

    selected_photos = []
    for place in results:
        name = place.get("name", "Cidade desconhecida")
        address = place.get("formatted_address", "")
        place_id = place.get("place_id")
        query = quote_plus(name)
        maps_url = (
            f"https://www.google.com/maps/search/?api=1"
            f"&query={query}&query_place_id={place_id}"
            if place_id else None
        )
        trivia = get_wikipedia_summary(f"{name}, {country_name}")

        for photo in place.get("photos", []):
            ref = photo.get("photo_reference")
            if ref:
                image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=1600&photoreference={ref}&key={API_KEY}"
                selected_photos.append({
                    "image_url": image_url,
                    "place_name": name,
                    "address": address,
                    "trivia": trivia,
                    "maps_url": maps_url
                })
                break  # one photo per city/town
        if len(selected_photos) >= max_photos:
            break

    return selected_photos

def get_random_restaurant_for_country(country_name):
    """
    Choose a random city in the country and return a random restaurant with photo, rating, and map link.
    """
    # Step 1: Pick a random city
    city_photos = get_random_city_photos(country_name, max_photos=1)
    if not city_photos:
        return None

    city_name = city_photos[0]["place_name"]

    # Step 2: Search for restaurants in that city
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": f"restaurant in {city_name}, {country_name}",
        "key": API_KEY
    }

    res = requests.get(search_url, params=params)
    results = res.json().get("results", [])
    if not results:
        return None

    # Step 3: Pick a random restaurant with a photo
    random.shuffle(results)
    for place in results:
        if "photos" not in place:
            continue

        name = place.get("name", "Restaurante desconhecido")
        address = place.get("formatted_address", "")
        rating = place.get("rating")
        place_id = place.get("place_id")
        query = quote_plus(name)
        maps_url = (
            f"https://www.google.com/maps/search/?api=1"
            f"&query={query}&query_place_id={place_id}"
            if place_id else None
        )
        photo_ref = place["photos"][0]["photo_reference"]
        photo_url = (
            f"https://maps.googleapis.com/maps/api/place/photo"
            f"?maxwidth=1600&photoreference={photo_ref}&key={API_KEY}"
        )

        return {
            "name": name,
            "address": address,
            "rating": rating,
            "image_url": photo_url,
            "maps_url": maps_url,
            "city": city_name
        }

    return None

def get_city_photos_from_name(country_name, city_name, max_photos=3):
    """
    Search for photo(s) of a specific city by name within the given country.
    Returns up to `max_photos`, including image URLs and trivia.
    """
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    photo_url_template = "https://maps.googleapis.com/maps/api/place/photo"

    query = f"{city_name}, {country_name}"
    res = requests.get(search_url, params={"query": query, "key": API_KEY})

    if res.status_code != 200:
        print(f"[PLACES] City lookup failed: {res.status_code}")
        return []

    results = res.json().get("results", [])
    if not results:
        print(f"[PLACES] No city found: {city_name}, {country_name}")
        return []

    selected_photos = []
    for place in results:
        name = place.get("name", city_name)
        address = place.get("formatted_address", "")
        place_id = place.get("place_id")
        maps_url = (
            f"https://www.google.com/maps/search/?api=1"
            f"&query={quote_plus(name)}&query_place_id={place_id}"
            if place_id else None
        )
        trivia = get_wikipedia_summary(f"{name}, {country_name}")

        for photo in place.get("photos", []):
            ref = photo.get("photo_reference")
            if ref:
                image_url = f"{photo_url_template}?maxwidth=1600&photoreference={ref}&key={API_KEY}"
                selected_photos.append({
                    "image_url": image_url,
                    "place_name": name,
                    "address": address,
                    "trivia": trivia,
                    "maps_url": maps_url
                })
                if len(selected_photos) >= max_photos:
                    return selected_photos

    return selected_photos

@lru_cache(maxsize=1)
def _load_city_data():
    with open("data/countries_cities.json", encoding="utf-8") as f:
        return json.load(f)

def get_random_cities_for_country(country_name, max_results=1):
    city_data = _load_city_data()
    for entry in city_data:
        if entry["name"].lower() == country_name.lower():
            cities = entry.get("cities", [])
            if not cities:
                return None
            sample = random.sample(cities, min(max_results, len(cities)))
            return sample[0] if max_results == 1 else sample
    return None
