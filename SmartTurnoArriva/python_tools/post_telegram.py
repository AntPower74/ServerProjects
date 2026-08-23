import asyncio
from telegram import Bot
import httpx
import logging

TOKEN = "8924812869:AAHOuXz5EY4Xtt_02X_lVP33J6jFQuN0ZGQ"
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
    bot = Bot(token=TOKEN)
    try:
        # Download the image first because telegram sometimes struggles with remote URLs
        async with httpx.AsyncClient() as client:
            r = await client.get(IMAGE_URL)
            if r.status_code == 200:
                await bot.send_photo(chat_id=NOME_CANALE, photo=r.content, caption=MESSAGGIO, parse_mode='Markdown')
                print("Telegram post inviato con successo!")
            else:
                print("Failed to download image")
    except Exception as e:
        print(f"Errore Telegram: {e}")

if __name__ == "__main__":
    asyncio.run(main())
