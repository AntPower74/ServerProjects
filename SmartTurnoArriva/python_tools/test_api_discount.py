import requests
import json

def search_promoqui_api(query):
    url = f"https://api.promoqui.it/v2/search?q={query}&lat=45.0703&lng=7.6869"
    headers = {"User-Agent": "PromoQui/5.0"}
    r = requests.get(url, headers=headers)
    data = r.json()
    retailers = [item.get('retailer_name') for item in data]
    print(set(retailers))

search_promoqui_api("latte")
search_promoqui_api("pasta")
search_promoqui_api("caffe")
