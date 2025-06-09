import pandas as pd
import numpy as np
import random
import os
import time
import requests
from telegram_utils import send_image_message

def get_artists_from_country(country_code, limit=100, offset=0):
    """
    Fetches a list of artists from a given ISO 3166-1 alpha-2 country code.
    Returns basic artist info (name + ID).
    """
    url = "https://musicbrainz.org/ws/2/artist"
    params = {
        "query": f"country:{country_code}",
        "fmt": "json",
        "limit": limit,
        "offset": offset
    }
    headers = {
        "User-Agent": "MusicExplorerBot/1.0 (your-email@example.com)"
    }

    print("Start getting random song")

    response = requests.get(url, params=params, headers=headers)
    print(response)
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []

    data = response.json()
    print(data)
    return [{
        "name": artist.get("name"),
        "id": artist.get("id"),
        "disambiguation": artist.get("disambiguation", ""),
        "type": artist.get("type", "")
    } for artist in data.get("artists", [])]


def get_song_from_artist(artist_id):
    headers = {"User-Agent": "MusicExplorerBot/1.0 (your-email@example.com)"}

    # Step 1: Get release-groups
    rg_url = f"https://musicbrainz.org/ws/2/release-group?artist={artist_id}&fmt=json&limit=100"
    rg_resp = requests.get(rg_url, headers=headers)
    release_groups = rg_resp.json().get("release-groups", [])
    if not release_groups:
        return None

    # Step 2: Choose a release group and fetch releases
    random_rg = random.choice(release_groups)
    rg_id = random_rg["id"]

    release_url = f"https://musicbrainz.org/ws/2/release?release-group={rg_id}&fmt=json&limit=10"
    release_resp = requests.get(release_url, headers=headers)
    releases = release_resp.json().get("releases", [])
    if not releases:
        return None

    # Step 3: Choose a release and get recordings
    release = random.choice(releases)
    release_id = release["id"]

    rec_url = f"https://musicbrainz.org/ws/2/recording?release={release_id}&fmt=json&limit=100"
    rec_resp = requests.get(rec_url, headers=headers)
    recordings = rec_resp.json().get("recordings", [])
    if not recordings:
        return None

    # Step 4: Choose a random track
    track = random.choice(recordings)

    # Step 5: Try getting cover art
    cover_url = f"https://coverartarchive.org/release/{release_id}/front"
    cover_resp = requests.get(cover_url, headers=headers)
    cover_image = cover_resp.url if cover_resp.status_code in (200, 307) else None

    return {
        "artist_id": artist_id,
        "track_title": track["title"],
        "release_title": release["title"],
        "release_id": release_id,
        "cover_image": cover_image
    }


def load_artist_df():
    path = "data/full_country_artist_counts.csv"
    df = pd.read_csv(path)
    df = df[df["ArtistCount"] >= 5]
    df = df.sample(frac=1).reset_index(drop=True)
    df["logArtistCount"] = np.log(df["ArtistCount"])
    df["cdf"] = df["logArtistCount"].cumsum() / df["logArtistCount"].sum()
    return df

def choose_country(df):
    unif = random.random()
    row = df[df["cdf"] <= unif].iloc[-1]
    return row

def try_get_valid_song(country_code, artist_count, max_attempts=100, limit=5):
    max_offset = max(1, int(artist_count / limit))
    fallback_artist = None
    fallback_result = None

    for attempt in range(max_attempts):
        offset = int(np.random.triangular(1, 1, max_offset))
        artists = get_artists_from_country(country_code, limit=limit, offset=offset)
        if not artists:
            continue

        artist = random.choice(artists)
        result = get_song_from_artist(artist["id"])
        if not result:
            continue

        # Save first valid song even without image as fallback
        if not fallback_artist:
            fallback_artist = artist
            fallback_result = result

        # Return early if cover image is present
        if result.get("cover_image"):
            return artist, result

        time.sleep(0.1)

    # Return fallback if no song with image was found
    if fallback_artist and fallback_result:
        return fallback_artist, fallback_result

    return None, None

def generate():
    df = load_artist_df()
    row = choose_country(df)

    country_code = row["Code"]
    country_name = row["Country"]
    artist_count = row["ArtistCount"]

    artist, result = try_get_valid_song(country_code, artist_count)

    if not artist or not result:
        return f"🎵 Música do dia\n⚠️ Não foi possível encontrar uma música."

    name = artist["name"]
    track_title = result["track_title"]
    release_title = result["release_title"]
    cover_image = result.get("cover_image")
    print(cover_image)
    
    caption = (
        f"🎵 *Música do dia*\n\n"
        f"👤 Artista: *{name}*\n"
        f"🎧 Faixa: _{track_title}_\n"
        f"💿 Álbum: _{release_title}_\n"
        f"🌍 País de origem: *{country_name}*"
    )
    print(caption)

    chat_ids = os.environ["CHAT_IDS"].split(",")

    for chat_id in chat_ids:
        if result and result.get("cover_image"):
            send_image_message(chat_id.strip(), cover_image, caption)
        else:
            send_telegram_message(caption)

    return None
