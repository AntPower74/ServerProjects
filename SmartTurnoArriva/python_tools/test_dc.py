import requests

def search_dc(query):
    # Let's try some typical API endpoints for DoveConviene
    # Since they are ShopFully, maybe the API is similar
    url = f"https://api.doveconviene.it/v2/search?q={query}&lat=45.0703&lng=7.6869"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(url, headers=headers)
        print("DoveConviene API Status:", r.status_code)
    except Exception as e:
        print(e)
        
search_dc("latte")
