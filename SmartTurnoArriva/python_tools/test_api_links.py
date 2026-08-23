import requests
import json

def search_promoqui_api(query):
    url = f"https://api.promoqui.it/v2/search?q={query}&lat=45.0703&lng=7.6869"
    headers = {"User-Agent": "PromoQui/5.0"}
    r = requests.get(url, headers=headers)
    data = r.json()
    for item in data[:2]:
        print(f"Retailer: {item.get('retailer_name')}")
        print(f"Leaflet Slug: {item.get('leaflet_slug')}")
        print(f"Partner Link: {item.get('partner_link')}")
        print(f"Partner URL: {item.get('partner_link_url')}")

search_promoqui_api("latte")
