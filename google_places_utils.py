# google_places_utils.py

import requests
import os
import random

API_KEY = os.environ["GOOGLE_API_KEY"]

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
        trivia = get_wikipedia_summary(name)

        for photo in place.get("photos", []):
            ref = photo.get("photo_reference")
            if ref:
                image_url = f"{photo_url_template}?maxwidth=1600&photoreference={ref}&key={API_KEY}"
                selected_photos.append({
                    "image_url": image_url,
                    "place_name": name,
                    "address": address,
                    "trivia": trivia
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
        trivia = get_wikipedia_summary(name)

        for photo in place.get("photos", []):
            ref = photo.get("photo_reference")
            if ref:
                image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=1600&photoreference={ref}&key={API_KEY}"
                selected_photos.append({
                    "image_url": image_url,
                    "place_name": name,
                    "address": address,
                    "trivia": trivia
                })
                break  # one photo per city/town
        if len(selected_photos) >= max_photos:
            break

    return selected_photos

