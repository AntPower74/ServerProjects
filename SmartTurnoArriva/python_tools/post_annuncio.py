import asyncio
import json
from telegram import Bot
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "7334707248:AAFw1g8086V2xO5sW8yWJ2iS3sW4nS1b7Gk"
NOME_CANALE = "@risparmiospesato"
IMAGE_URL = "http://217.154.200.184/tubo_rosso.jpg"
MESSAGGIO = """🚨 **NUOVO ARRIVO IN VETRINA!** 🚨

🛒 **Prodotto:** Tubo Multistrato Isocell ∅ 16x2mm Pert-al-pert
📦 **Dettagli:** Rotolo 25m Rivestito Guaina 6mm Rosso. Materiale professionale di altissima qualità!
💶 **Prezzo:** 23,40 €

👉 **Acquistalo subito dal nostro sito web:**
🔗 http://217.154.200.184/#shop

Paga comodamente tramite Satispay, PayPal o PostePay e noi provvederemo subito alla spedizione!
"""

async def main():
    # 1. Telegram
    bot = Bot(token=TOKEN)
    try:
        await bot.send_photo(chat_id=NOME_CANALE, photo=IMAGE_URL, caption=MESSAGGIO, parse_mode='Markdown')
        print("Telegram post inviato con successo!")
    except Exception as e:
        print(f"Errore Telegram: {e}")

    # 2. Facebook & Instagram
    with open("/root/facebook_credentials.json", "r") as f:
        creds = json.load(f)
    access_token = creds.get("access_token")
    page_id = creds.get("page_id")
    ig_user_id = creds.get("ig_user_id")

    msg_fb = MESSAGGIO.replace("**", "")

    async with httpx.AsyncClient() as client:
        # Facebook
        url_fb = f"https://graph.facebook.com/v18.0/{page_id}/photos"
        payload_fb = {
            "url": IMAGE_URL,
            "message": msg_fb,
            "access_token": access_token
        }
        res = await client.post(url_fb, data=payload_fb)
        if res.status_code == 200:
            print("Facebook post inviato!")
        else:
            print(f"Facebook Error: {res.text}")

        # Instagram
        url_ig_media = f"https://graph.facebook.com/v18.0/{ig_user_id}/media"
        payload_ig_media = {
            "image_url": IMAGE_URL,
            "caption": msg_fb,
            "access_token": access_token
        }
        res_ig = await client.post(url_ig_media, data=payload_ig_media)
        if res_ig.status_code == 200:
            creation_id = res_ig.json().get('id')
            await asyncio.sleep(8)
            url_publish = f"https://graph.facebook.com/v18.0/{ig_user_id}/media_publish"
            payload_publish = {
                "creation_id": creation_id,
                "access_token": access_token
            }
            res_pub = await client.post(url_publish, data=payload_publish)
            if res_pub.status_code == 200:
                print("Instagram post inviato!")
            else:
                print(f"Instagram Publish Error: {res_pub.text}")
        else:
            print(f"Instagram Media Error: {res_ig.text}")

if __name__ == "__main__":
    asyncio.run(main())
