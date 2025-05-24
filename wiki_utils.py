import requests
from bs4 import BeautifulSoup
import hashlib

def get_country_data(country):
    """
    Fetches:
      - Latest population and its date (via Wikidata SPARQL)
      - Head of state’s name and portrait image URL (via Wikidata SPARQL)
      - Head of state’s official title as it appears in the Wikipedia infobox
      - Government type from the Wikipedia infobox
    """
    session = requests.Session()
    session.headers.update({
        "User-Agent": "CountryInfoBot/1.0 (contact@example.com)"
    })

    # 1. Get Wikidata ID from Wikipedia API
    wiki_api = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": country,
        "prop": "pageprops",
        "ppprop": "wikibase_item"
    }
    resp = session.get(wiki_api, params=params)
    resp.raise_for_status()
    pages = resp.json()["query"]["pages"]
    page = next(iter(pages.values()))
    wikidata_id = page.get("pageprops", {}).get("wikibase_item")
    if not wikidata_id:
        raise ValueError(f"No Wikidata item for '{country}'")

    # 2. SPARQL: population + head_of_state + image
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
    sparql_url = "https://query.wikidata.org/sparql"
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "CountryInfoBot/1.0 (contact@example.com)"
    }
    data = session.get(sparql_url, params={"query": sparql, "format": "json"}, headers=headers)
    data.raise_for_status()
    results = data.json()["results"]["bindings"]
    if not results:
        raise ValueError("No population or head of state data found.")

    entry = results[0]
    population = entry["pop"]["value"]
    pop_date = entry["popDate"]["value"]
    head_name = entry.get("personLabel", {}).get("value")
    head_image = entry.get("img", {}).get("value")

    # 3. Scrape infobox for head-of-state title and government type
    wiki_url = "https://en.wikipedia.org/wiki/" + country.replace(" ", "_")
    html = session.get(wiki_url).text
    soup = BeautifulSoup(html, "lxml")
    infobox = soup.find("table", class_="infobox")
    
    state_title = None
    gov_type = None
    if infobox:
        # Head of state title
        if head_name:
            for row in infobox.find_all("tr"):
                th = row.find("th")
                td = row.find("td")
                if th and td and head_name in td.get_text():
                    raw = th.get_text().strip()
                    state_title = raw.lstrip("•·.- ").strip()
                    break
        # Government type
        gov_row = infobox.find("th", string=lambda t: t and "Government" in t)
        if gov_row:
            gov_td = gov_row.find_next_sibling("td")
            if gov_td:
                # collapse newlines and bullets into spaces
                gov_type = " ".join(gov_td.get_text(separator=" ", strip=True).split())

    return {
        "population": population,
        "populationDate": pop_date,
        "head_of_state": head_name,
        "stateTitle": state_title or "Head of state",
        "stateImage": head_image,
        "governmentType": gov_type or "Unknown"
    }

def get_image_from_wikidata(wikidata_id):
    """
    Recebe um Wikidata ID (ex.: 'Q17592') e retorna a URL da imagem principal (P18)
    """
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
    res = requests.get(url)
    res.raise_for_status()
    entity = res.json()["entities"][wikidata_id]

    try:
        image_filename = entity["claims"]["P18"][0]["mainsnak"]["datavalue"]["value"]
    except KeyError:
        raise ValueError("Imagem (P18) não encontrada para esse item no Wikidata")

    # Constrói a URL da imagem no Wikimedia Commons
    filename = image_filename.replace(" ", "_")
    md5_hash = hashlib.md5(filename.encode('utf-8')).hexdigest()
    url_image = f"https://upload.wikimedia.org/wikipedia/commons/{md5_hash[0]}/{md5_hash[0]}{md5_hash[1]}/{filename}"
    return url_image
