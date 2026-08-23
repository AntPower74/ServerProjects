import requests

def search_promoqui_api(query):
    url = f"https://api.promoqui.it/v2/search?q={query}&lat=45.0703&lng=7.6869" # Turin coords
    headers = {"User-Agent": "PromoQui/5.0"}
    try:
        r = requests.get(url, headers=headers)
        print("PromoQui API Status:", r.status_code)
        print(r.text[:300])
    except Exception as e:
        print(e)

search_promoqui_api("caffe")
