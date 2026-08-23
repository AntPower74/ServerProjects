import requests
import json

def search_promoqui_api(query):
    url = f"https://api.promoqui.it/v2/search?q={query}&lat=45.0703&lng=7.6869" # Turin coords
    headers = {"User-Agent": "PromoQui/5.0"}
    r = requests.get(url, headers=headers)
    print(json.dumps(r.json()[:2], indent=2))

search_promoqui_api("caffe")
