# google_places_utils.py

import requests
import os

API_KEY = os.environ["GOOGLE_API_KEY"]

def get_place_images_for_country(country_name, max_photos=5):
    """
    Search Google Places API for landmarks in the given country and extract up to `max_photos` images.
    """
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    photo_url_template = "https://maps.googleapis.com/maps/api/place/photo"

    params = {
        "query": f"top tourist places in {country_name}",
        "key": API_KEY
    }

    res = requests.get(search_url, params=params)
    if res.status_code != 200:
        print(f"[PLACES] Search failed: {res.status_code} {res.text}")
        return []

    results = res.json().get("results", [])
    if not results:
        print(f"[PLACES] No results for {country_name}")
        return []

    photos = []
    for place in results:
        for photo in place.get("photos", []):
            ref = photo.get("photo_reference")
            if ref:
                url = f"{photo_url_template}?maxwidth=1600&photoreference={ref}&key={API_KEY}"
                photos.append(url)
            if len(photos) >= max_photos:
                return photos

    return photos
