import asyncio, json, httpx

async def main():
    with open("/root/facebook_credentials.json", "r") as f:
        creds = json.load(f)
    ig_id = creds.get("ig_user_id")
    token = creds.get("access_token")
    
    img = "https://images.unsplash.com/photo-1542838132-92c53300491e?w=600&q=80"
    caption = "Benvenuti sul nostro account Instagram ufficiale! 🚀\nDa oggi pubblicheremo qui le migliori offerte dei supermercati di Torino.\n#offertetorino #risparmio #supermercato #torino"
    
    print("Creazione container...")
    url_media = f"https://graph.facebook.com/v18.0/{ig_id}/media"
    res = httpx.post(url_media, data={"image_url": img, "caption": caption, "access_token": token}, timeout=30.0)
    print(res.text)
    
    if res.status_code == 200:
        creation_id = res.json().get("id")
        print("Attesa di 8 secondi affinché Instagram processi l'immagine...")
        await asyncio.sleep(8)
        print("Pubblicazione...")
        url_pub = f"https://graph.facebook.com/v18.0/{ig_id}/media_publish"
        res2 = httpx.post(url_pub, data={"creation_id": creation_id, "access_token": token}, timeout=30.0)
        print(res2.text)

asyncio.run(main())
