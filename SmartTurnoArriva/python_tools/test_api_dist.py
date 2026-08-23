import requests

def search_promoqui_api(query):
    url = f"https://api.promoqui.it/v2/search?q={query}&lat=45.0703&lng=7.6869"
    headers = {"User-Agent": "PromoQui/5.0"}
    r = requests.get(url, headers=headers)
    data = r.json()
    for item in data[:5]:
        print(f"{item.get('retailer_name')} - Dist: {item.get('distance')} km - {item.get('title')}")

search_promoqui_api("latte")
