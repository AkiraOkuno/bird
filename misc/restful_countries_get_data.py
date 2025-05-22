import requests
import json

API_KEY = ""
API_URL = "https://restfulcountries.com/storage/images/presidents/muhammadu-buharipxpjw98lcj.jpg"

# Your API call
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
    }
url = "https://restfulcountries.com/api/v1/countries"

response = requests.get(url, headers=headers)
data = response.json()

# Save the data to a JSON file
with open("countries_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
