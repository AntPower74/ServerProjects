import os
import random
import asyncio
import httpx
import requests
import json
import time
from datetime import datetime
import zoneinfo
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import logging

# Abilita il logging per vedere eventuali errori
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def is_bot_active():
    """Controlla se l'ora attuale è compresa tra le 07:00 e le 21:00 (orario italiano)."""
    tz = zoneinfo.ZoneInfo('Europe/Rome')
    now = datetime.now(tz)
    if now.hour >= 21 or now.hour < 7:
        return False
    return True

# Inserisci qui il tuo Token ottenuto da BotFather
TOKEN = "8924812869:AAHOuXz5EY4Xtt_02X_lVP33J6jFQuN0ZGQ"

# Leggi l'ID del canale salvato, se esiste
FILE_CANALE = "canale_id.txt"
FILE_MESSAGGI = "messaggi_canale.json"
NOME_CANALE = None
if os.path.exists(FILE_CANALE):
    with open(FILE_CANALE, "r") as f:
        NOME_CANALE = f.read().strip()

def salva_messaggio_canale(message_id):
    messaggi = []
    if os.path.exists(FILE_MESSAGGI):
        with open(FILE_MESSAGGI, "r") as f:
            try:
                messaggi = json.load(f)
            except:
                pass
    messaggi.append({"message_id": message_id, "timestamp": time.time()})
    with open(FILE_MESSAGGI, "w") as f:
        json.dump(messaggi, f)

def salva_offerta_sito(titolo, prezzo, negozio, scadenza, image_url, link_volantino):
    file_sito = "/root/sito/offerte.json"
    offerte = []
    if os.path.exists(file_sito):
        with open(file_sito, "r") as f:
            try:
                offerte = json.load(f)
            except:
                pass
    # Crea nuova offerta
    nuova_offerta = {
        "store": negozio,
        "title": titolo,
        "newPrice": str(prezzo),
        "expiration": str(scadenza),
        "image": image_url,
        "link": link_volantino or "https://t.me/+0mC7roUUmYswZjA0"
    }
    # Rimuovi eventuali duplicati
    offerte = [o for o in offerte if o["title"] != titolo]
    # Inserisci all'inizio
    offerte.insert(0, nuova_offerta)
    # Tieni solo le ultime 500
    offerte = offerte[:500]
    
    # Crea la directory se non esiste (sicurezza)
    os.makedirs("/root/sito", exist_ok=True)
    with open(file_sito, "w") as f:
        json.dump(offerte, f, indent=4)

async def cancella_offerte_vecchie(context: ContextTypes.DEFAULT_TYPE):
    """Elimina dal canale i messaggi più vecchi di 5 giorni."""
    if not is_bot_active():
        return
    if not NOME_CANALE or not os.path.exists(FILE_MESSAGGI):
        return
        
    with open(FILE_MESSAGGI, "r") as f:
        try:
            messaggi = json.load(f)
        except:
            return
            
    ora = time.time()
    cinque_giorni_in_sec = 5 * 24 * 60 * 60
    messaggi_da_tenere = []
    
    for msg in messaggi:
        if ora - msg["timestamp"] > cinque_giorni_in_sec:
            try:
                await context.bot.delete_message(chat_id=NOME_CANALE, message_id=msg["message_id"])
            except Exception as e:
                logger.error(f"Errore eliminazione vecchio messaggio {msg['message_id']}: {e}")
        else:
            messaggi_da_tenere.append(msg)
            
    with open(FILE_MESSAGGI, "w") as f:
        json.dump(messaggi_da_tenere, f)

async def cancella_offerte_sito_vecchie(context: ContextTypes.DEFAULT_TYPE):
    """Elimina dal file del sito web le offerte scadute rispetto alla data odierna."""
    file_sito = "/root/sito/offerte.json"
    if not os.path.exists(file_sito):
        return
        
    try:
        with open(file_sito, "r") as f:
            offerte = json.load(f)
            
        today = datetime.now().strftime("%Y-%m-%d")
        valid_offerte = [o for o in offerte if not o.get("expiration") or o.get("expiration") >= today]
        
        if len(valid_offerte) < len(offerte):
            with open(file_sito, "w") as f:
                json.dump(valid_offerte, f, indent=4)
            logger.info(f"Rimosse {len(offerte) - len(valid_offerte)} offerte scadute dal sito.")
    except Exception as e:
        logger.error(f"Errore pulizia offerte sito: {e}")

LINK_BOT = "https://t.me/Second74bot"
keyboard_canale = [[InlineKeyboardButton("🤖 Apri il Bot per altre offerte", url=LINK_BOT)]]
reply_markup_canale = InlineKeyboardMarkup(keyboard_canale)

async def cerca_offerte_api(query, lat=45.0703, lng=7.6869, max_distance=15.0):
    """Cerca offerte tramite l'API di PromoQui per le coordinate (default Torino). Filtra per raggio d'azione."""
    url = f"https://api.promoqui.it/v2/search?q={query}&lat={lat}&lng={lng}"
    headers = {"User-Agent": "PromoQui/5.0"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                risultati = response.json()
                # Filtra solo le offerte con distanza specificata e <= max_distance (per limitare a Torino)
                offerte_locali = []
                for off in risultati:
                    distanza = off.get('distance')
                    if distanza is not None and float(distanza) <= max_distance:
                        offerte_locali.append(off)
                return offerte_locali
    except Exception as e:
        print(f"Errore durante la ricerca: {e}")
    return []

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Risponde al comando /start."""
    welcome_message = (
        "🛒 *Ciao! Sono il tuo bot cerca-offerte per Torino.*\n\n"
        "Scrivimi semplicemente il nome di un prodotto (es. `caffè`, `nutella`, `latte`) "
        "e io cercherò per te in tutti i volantini attivi a Torino per dirti dove costa meno!\n\n"
        "📢 **NOVITÀ**: Abbiamo un canale ufficiale dove inviamo in automatico le 10 migliori "
        "offerte del momento ogni 5 minuti! Unisciti per non perdertene neanche una!\n\n"
        "☕ Se questo bot ti fa risparmiare sulla spesa, considera di offrirmi un caffè con /dona"
    )
    keyboard_start = [[InlineKeyboardButton("📢 Entra nel Canale Offerte", url="https://t.me/+0mC7roUUmYswZjA0")]]
    reply_markup_start = InlineKeyboardMarkup(keyboard_start)
    await update.message.reply_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup_start)

async def dona_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Risponde al comando /dona."""
    testo_donazione = (
        "❤️ Grazie di cuore per voler supportare il mio lavoro!\n\n"
        "Cercami sull'app Satispay oppure [clicca qui per donare direttamente](https://web.satispay.com/download/qrcode/S6Y-CON--500ED62A-5BDF-4775-BD64-3945A8B75CCD?locale=it)."
    )
    await update.message.reply_text(testo_donazione, parse_mode='Markdown')

async def richieste_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Legge il file JSON dei suggerimenti e li invia in privato all'amministratore."""
    file_path = '/root/sito/richieste_clienti.json'
    if not os.path.exists(file_path):
        await update.message.reply_text("Nessuna richiesta ricevuta dal sito al momento.")
        return
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            richieste = json.load(f)
    except Exception as e:
        await update.message.reply_text(f"Errore lettura file: {e}")
        return
        
    if not richieste:
        await update.message.reply_text("La lista richieste è vuota.")
        return
        
    testo = "📥 **Richieste / Suggerimenti dal Sito** 📥\n\n"
    for r in richieste:
        testo += f"📅 {r.get('timestamp', 'N/D')}\n"
        testo += f"👤 Nome: {r.get('name', 'Anonimo')}\n"
        testo += f"💬 Messaggio: {r.get('message', '')}\n"
        testo += "------------------------\n"
        
    # Se il testo è troppo lungo, Telegram potrebbe bloccarlo, spezzettiamolo
    for i in range(0, len(testo), 4000):
        await update.message.reply_text(testo[i:i+4000], parse_mode='Markdown')

async def ordini_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Legge il file JSON degli ordini e li invia in privato all'amministratore."""
    file_path = '/root/sito/ordini.json'
    if not os.path.exists(file_path):
        await update.message.reply_text("Nessun ordine ricevuto dal sito al momento.")
        return
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            ordini = json.load(f)
    except Exception as e:
        await update.message.reply_text(f"Errore lettura file: {e}")
        return
        
    if not ordini:
        await update.message.reply_text("La lista ordini è vuota.")
        return
        
    testo = "🛒 **Nuovi Ordini dallo Shop** 🛒\n\n"
    for r in ordini:
        testo += f"📅 Data: {r.get('timestamp', 'N/D')}\n"
        testo += f"👤 Nome: {r.get('name', 'N/D')}\n"
        testo += f"📍 Indirizzo: {r.get('address', 'N/D')}\n"
        testo += "📦 Carrello:\n"
        for item in r.get('cart', []):
            testo += f"   - {item.get('qty')}x {item.get('name')} (€{item.get('price')})\n"
        testo += f"💶 TOTALE: €{r.get('total', 0):.2f}\n"
        testo += "------------------------\n"
        
    for i in range(0, len(testo), 4000):
        await update.message.reply_text(testo[i:i+4000], parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce i messaggi di testo in arrivo e fa la ricerca."""
    if not is_bot_active():
        await update.message.reply_text("😴 Il bot è attualmente in pausa notturna (dalle 21:00 alle 07:00). A domani!")
        return
        
    if not update.message or not update.message.text:
        return
        
    prodotto = update.message.text
    logger.info(f"Ricevuto messaggio dall'utente {update.effective_user.first_name}: {prodotto}")
    
    await update.message.reply_text(f"🔍 Sto cercando le migliori offerte per *{prodotto}* nei volantini di Torino...", parse_mode='Markdown')
    
    offerte = await cerca_offerte_api(prodotto)
    
    if not offerte:
        await update.message.reply_text("😔 Purtroppo non ho trovato nessuna offerta attiva per questo prodotto.")
        return

    # Filtra quelle senza prezzo e ordina per prezzo più basso (così emergono i discount!)
    offerte_con_prezzo = [o for o in offerte if o.get('price') is not None]
    offerte_ordinate = sorted(offerte_con_prezzo, key=lambda x: float(x['price']))
    
    # Prendiamo le prime 5 offerte più economiche
    risultati = offerte_ordinate[:5]
    
    await update.message.reply_text(f"✅ Ecco le migliori {len(risultati)} offerte per *{prodotto}* a Torino (circuito DoveConviene):")
    
    for off in risultati:
        titolo = off.get('title', 'Prodotto Sconosciuto')
        prezzo = off.get('price', 'N/D')
        negozio = off.get('retailer_name', 'Negozio Sconosciuto')
        scadenza = off.get('expiration_date', 'N/D')
        
        # Estrai l'URL dell'immagine se disponibile
        image_url = off.get('image_large') or off.get('image_big') or off.get('image_thumb')
        
        # Costruisci il link al volantino
        leaflet_slug = off.get('leaflet_slug', '')
        link_volantino = f"https://www.promoqui.it/offerte/{leaflet_slug}" if leaflet_slug else ""
        
        # Invia questa offerta anche al sito web
        salva_offerta_sito(titolo, prezzo, negozio, scadenza, image_url, link_volantino)
        
        didascalia = (
            f"🏪 *{negozio}*\n"
            f"📦 {titolo}\n"
            f"💶 Prezzo: *{prezzo} €*\n"
            f"⏳ Scade il: {scadenza}\n"
        )
        if link_volantino:
            didascalia += f"🔗 [Sfoglia il volantino]({link_volantino})"
        
        try:
            if image_url:
                await update.message.reply_photo(photo=image_url, caption=didascalia, parse_mode='Markdown')
            else:
                await update.message.reply_text(didascalia, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Errore invio foto: {e}")
            await update.message.reply_text(didascalia, parse_mode='Markdown')
            
    # Messaggio finale automatico per la donazione
    messaggio_finale = (
        "☕ Se ti ho aiutato a risparmiare, considera di offrirmi un caffè!\n"
        "👉 [Dona con Satispay cliccando qui](https://web.satispay.com/download/qrcode/S6Y-CON--500ED62A-5BDF-4775-BD64-3945A8B75CCD?locale=it)"
    )
    await update.message.reply_text(messaggio_finale, parse_mode='Markdown', reply_markup=reply_markup_canale)

async def registra_canale(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Quando il bot viene aggiunto a un canale e vede un messaggio, salva il suo ID."""
    if not update.effective_chat or update.effective_chat.type != "channel":
        return
        
    chat_id = str(update.effective_chat.id)
    with open(FILE_CANALE, "w") as f:
        f.write(chat_id)
    global NOME_CANALE
    NOME_CANALE = chat_id
    logger.info(f"Canale registrato con ID: {chat_id}")
    await context.bot.send_message(chat_id=chat_id, text="✅ Bot configurato correttamente per questo canale! Da ora invierò qui le offerte automatiche.")

async def invia_post_facebook(messaggio, image_url):
    """Invia un post sulla pagina Facebook collegata, se configurato."""
    if not os.path.exists("facebook_credentials.json"):
        return
        
    try:
        with open("facebook_credentials.json", "r") as f:
            creds = json.load(f)
            
        page_id = creds.get("page_id")
        access_token = creds.get("access_token")
        
        if not page_id or not access_token:
            return
            
        # Pulisce il messaggio dai markdown di Telegram per Facebook
        testo_pulito = messaggio.replace('*', '').replace('_', '')
        
        if image_url:
            url = f"https://graph.facebook.com/v18.0/{page_id}/photos"
            payload = {
                "url": image_url,
                "message": testo_pulito,
                "access_token": access_token
            }
        else:
            url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
            payload = {
                "message": testo_pulito,
                "access_token": access_token
            }
            
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload)
            if response.status_code != 200:
                logger.error(f"Errore Facebook: {response.text}")
    except Exception as e:
        logger.error(f"Eccezione invio Facebook: {e}")

async def invia_post_instagram(messaggio, image_url):
    """Invia un post sull'account Instagram Business collegato."""
    if not image_url:
        return # Instagram richiede un'immagine
        
    if not os.path.exists("facebook_credentials.json"):
        return
        
    try:
        with open("facebook_credentials.json", "r") as f:
            creds = json.load(f)
            
        ig_user_id = creds.get("ig_user_id")
        access_token = creds.get("access_token")
        
        if not ig_user_id or not access_token:
            return
            
        # Pulisce il messaggio dai markdown di Telegram e aggiunge hashtag
        testo_pulito = messaggio.replace('*', '').replace('_', '')
        caption = testo_pulito + "\n\n#offertetorino #risparmio #supermercato #torino"
        
        # Step 1: Crea il contenitore media
        url_media = f"https://graph.facebook.com/v18.0/{ig_user_id}/media"
        payload_media = {
            "image_url": image_url,
            "caption": caption,
            "access_token": access_token
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            res_media = await client.post(url_media, data=payload_media)
            if res_media.status_code != 200:
                logger.error(f"Errore Instagram Media Container: {res_media.text}")
                return
                
            creation_id = res_media.json().get("id")
            
            # Instagram ha bisogno di qualche secondo per processare l'immagine prima della pubblicazione
            await asyncio.sleep(8)
            
            # Step 2: Pubblica il contenitore
            url_publish = f"https://graph.facebook.com/v18.0/{ig_user_id}/media_publish"
            payload_publish = {
                "creation_id": creation_id,
                "access_token": access_token
            }
            
            res_publish = await client.post(url_publish, data=payload_publish)
            if res_publish.status_code != 200:
                logger.error(f"Errore Instagram Publish: {res_publish.text}")
            else:
                logger.info("Post Instagram pubblicato con successo!")
    except Exception as e:
        logger.error(f"Eccezione invio Instagram: {e}")

async def invia_promo_social(context: ContextTypes.DEFAULT_TYPE = None):
    """Pubblica un post mirato per il sito e il canale Telegram su Instagram e Facebook, ma solo dalle 7 alle 20:59."""
    # Controllo orario: salta se è tra le 21:00 e le 06:59
    import zoneinfo
    ora_corrente = datetime.now(zoneinfo.ZoneInfo('Europe/Rome')).hour
    if ora_corrente >= 21 or ora_corrente < 7:
        logger.info(f"Fuori orario ({ora_corrente}:00), il post promozionale viene saltato.")
        return

    if not os.path.exists("facebook_credentials.json"):
        return
        
    try:
        with open("facebook_credentials.json", "r") as f:
            creds = json.load(f)
            
        ig_user_id = creds.get("ig_user_id")
        page_id = creds.get("page_id")
        access_token = creds.get("access_token")
        
        if not access_token:
            return
            
        caption = (
            "Le migliori offerte sui supermercati di Torino sono già online! 🔥🛒\n"
            "Scopri gli sconti in scadenza e non farti scappare le promozioni del giorno.\n\n"
            "Resta sempre aggiornato e inizia a risparmiare:\n"
            "🌐 Sito: http://217.154.200.184\n"
            "📘 FB: Offerte Spesa Torino\n"
            "✈️ Telegram: https://t.me/risparmiospesato\n\n"
            "#offertetorino #risparmio #supermercato #torino #sconti #spesaintelligente #piemonte"
        )
        
        image_url = "http://217.154.200.184/promo_instagram_links.jpg"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Invio a INSTAGRAM
            if ig_user_id:
                url_media = f"https://graph.facebook.com/v18.0/{ig_user_id}/media"
                payload_media = {
                    "image_url": image_url,
                    "caption": caption,
                    "access_token": access_token
                }
                res_media = await client.post(url_media, data=payload_media)
                if res_media.status_code == 200:
                    creation_id = res_media.json().get("id")
                    await asyncio.sleep(8)
                    url_publish = f"https://graph.facebook.com/v18.0/{ig_user_id}/media_publish"
                    payload_publish = {
                        "creation_id": creation_id,
                        "access_token": access_token
                    }
                    res_publish = await client.post(url_publish, data=payload_publish)
                    if res_publish.status_code == 200:
                        logger.info("Pubblicità mirata Instagram pubblicata con successo (Post)!")
                    else:
                        logger.error(f"Errore Instagram Pubblicità Publish: {res_publish.text}")
                else:
                    logger.error(f"Errore Instagram Post Container: {res_media.text}")
            
            # Invio a FACEBOOK (con link cliccabili nativi)
            if page_id:
                url_fb = f"https://graph.facebook.com/v18.0/{page_id}/photos"
                payload_fb = {
                    "url": image_url,
                    "message": caption,
                    "access_token": access_token
                }
                res_fb = await client.post(url_fb, data=payload_fb)
                if res_fb.status_code == 200:
                    logger.info("Pubblicità mirata Facebook pubblicata con successo!")
                else:
                    logger.error(f"Errore Facebook Promo Post: {res_fb.text}")
                    
    except Exception as e:
        logger.error(f"Eccezione invio pubblicità social: {e}")

async def invia_offerte_canale(context: ContextTypes.DEFAULT_TYPE):
    """Cerca 10 offerte incredibili random e le manda al canale associato."""
    if not is_bot_active():
        return
        
    if not NOME_CANALE:
        return # Non fa nulla finché l'utente non configura il canale
        
    prodotti_popolari = [
        # Alimentari e prima necessità
        "caffè", "latte", "nutella", "biscotti", "pasta", 
        "passata di pomodoro", "carta igienica", "detersivo", "tonno",
        "olio", "zucchero", "uova", "burro", "farina", "pollo",
        "carne", "acqua", "formaggio", "shampoo", "bagnoschiuma",
        "birra", "vino", "coca cola", "patatine", "pizza",
        "prosciutto", "yogurt", "cereali", "croissant", "succo",
        "dentifricio", "sapone", "pannolini", "salumi", "frutta",
        "mele", "banane", "arance", "verdura", "pomodori",
        # Elettronica ed Elettrodomestici
        "televisore", "smartphone", "iphone", "samsung", "lavatrice",
        "frigorifero", "notebook", "pc", "tablet", "aspirapolvere",
        "friggitrice ad aria", "forno a microonde", "macchina da caffè",
        "cuffie", "smartwatch", "scopa elettrica", "climatizzatore",
        "ventilatore", "ferro da stiro", "frullatore", "playstation",
        # Viaggi e Vacanze
        "viaggio", "vacanza", "crociera", "volo", "hotel", 
        "valigia", "trolley", "tenda da campeggio", "bicicletta", "monopattino",
        # Altro (Bricolage, Casa, Animali)
        "trapano", "piscina", "barbecue", "materasso", "divano",
        "armadio", "scarpiera", "cibo per cani", "cibo per gatti"
    ]
    prodotti_scelti = random.sample(prodotti_popolari, 10)
    
    for prodotto in prodotti_scelti:
        offerte = await cerca_offerte_api(prodotto)
        if not offerte:
            continue
            
        offerte_con_prezzo = [o for o in offerte if o.get('price') is not None]
        if not offerte_con_prezzo:
            continue
            
        # Ordina tutte le offerte per prezzo
        offerte_ordinate = sorted(offerte_con_prezzo, key=lambda x: float(x['price']))
        
        # Salva TUTTE le migliori 10 offerte trovate sul sito web (così il sito si popola di più)
        for off in offerte_ordinate[:10]:
            t = off.get('title', 'Prodotto Sconosciuto')
            p = off.get('price', 'N/D')
            n = off.get('retailer_name', 'Negozio Sconosciuto')
            s = off.get('expiration_date', 'N/D')
            img = off.get('image_large') or off.get('image_big') or off.get('image_thumb')
            ls = off.get('leaflet_slug', '')
            lnk = f"https://www.promoqui.it/offerte/{ls}" if ls else ""
            salva_offerta_sito(t, p, n, s, img, lnk)

        # Prendi l'offerta migliore in assoluto per pubblicarla sul Canale Telegram/Facebook
        migliore = offerte_ordinate[0]
        
        titolo = migliore.get('title', 'Prodotto Sconosciuto')
        prezzo = migliore.get('price', 'N/D')
        negozio = migliore.get('retailer_name', 'Negozio Sconosciuto')
        scadenza = migliore.get('expiration_date', 'N/D')
        image_url = migliore.get('image_large') or migliore.get('image_big') or migliore.get('image_thumb')
        leaflet_slug = migliore.get('leaflet_slug', '')
        link_volantino = f"https://www.promoqui.it/offerte/{leaflet_slug}" if leaflet_slug else ""
        
        messaggio = (
            f"🚨 **SUPER OFFERTA IMPERDIBILE** 🚨\n\n"
            f"🛒 *{negozio}*\n"
            f"📦 {titolo}\n"
            f"💶 Prezzo Bomba: *{prezzo} €*\n"
            f"⏳ Scade il: {scadenza}\n"
        )
        if link_volantino:
            messaggio += f"🔗 [Sfoglia il volantino]({link_volantino})\n\n"
            
        messaggio += (
            "💡 _Cerca altre offerte avviando il nostro bot!_\n\n"
            "☕ _Se ti abbiamo aiutato a risparmiare, offrici un caffè!_\n"
            "👉 **[Dona con Satispay cliccando qui](https://web.satispay.com/download/qrcode/S6Y-CON--500ED62A-5BDF-4775-BD64-3945A8B75CCD?locale=it)**"
        )
        
        try:
            if image_url:
                sent_msg = await context.bot.send_photo(chat_id=NOME_CANALE, photo=image_url, caption=messaggio, parse_mode='Markdown', reply_markup=reply_markup_canale)
            else:
                sent_msg = await context.bot.send_message(chat_id=NOME_CANALE, text=messaggio, parse_mode='Markdown', reply_markup=reply_markup_canale)
                
            salva_messaggio_canale(sent_msg.message_id)
            
            # Pubblica solo su Facebook le offerte automatiche
            await invia_post_facebook(messaggio, image_url)
            await invia_post_instagram(messaggio, image_url)
            
            
        except Exception as e:
            logger.error(f"Errore nell'invio al canale: {e}")
            
        # Attendi 3 secondi prima del prossimo invio per evitare blocchi per spam
        await asyncio.sleep(3)

async def invia_buonanotte(context: ContextTypes.DEFAULT_TYPE):
    """Invia il messaggio di buonanotte al canale alle 21:00."""
    if not NOME_CANALE:
        return
    messaggio = "🌙 *Buonanotte a tutti gli iscritti!*\nIl bot va in pausa notturna. Riprenderemo la ricerca delle migliori offerte domani mattina alle 07:00.\n\nA domani!"
    try:
        await context.bot.send_message(chat_id=NOME_CANALE, text=messaggio, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Errore nell'invio della buonanotte: {e}")

async def invia_buongiorno(context: ContextTypes.DEFAULT_TYPE):
    """Invia il messaggio di buongiorno al canale alle 07:00."""
    if not NOME_CANALE:
        return
    messaggio = "☀️ *Buongiorno a tutti!*\nIl bot è di nuovo attivo e pronto a segnalarvi le migliori offerte della giornata.\n\nBuona spesa!"
    try:
        await context.bot.send_message(chat_id=NOME_CANALE, text=messaggio, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Errore nell'invio del buongiorno: {e}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestisce le foto inviate al bot (es. per aggiornare la foto del prodotto sul sito)."""
    try:
        # Prendi la foto con la risoluzione più alta (l'ultima nella lista)
        photo_file = await update.message.photo[-1].get_file()
        file_path = f"/root/sito/tubo_rosso.jpg"
        
        # Scarica e sovrascrivi la foto del prodotto
        await photo_file.download_to_drive(file_path)
        await update.message.reply_text("✅ Foto ricevuta! Ho aggiornato l'immagine del Tubo Multistrato sul sito. Ricarica la pagina web per vederla!")
    except Exception as e:
        await update.message.reply_text(f"❌ Errore durante il salvataggio della foto: {e}")

def main():
    """Avvia il bot."""
    print("Avvio del bot in corso...")
    app = Application.builder().token(TOKEN).build()

    # Comandi
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler("dona", dona_command))
    app.add_handler(CommandHandler("richieste", richieste_command))
    app.add_handler(CommandHandler("ordini", ordini_command))
    app.add_handler(CommandHandler("canale", registra_canale))
    app.add_handler(MessageHandler(filters.PHOTO & ~filters.ChatType.CHANNEL, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.ChatType.CHANNEL, handle_message))

    # Gestisce i messaggi nei canali per autorizzare l'invio
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, registra_canale))

    # Aggiungi i job schedulati
    app.job_queue.run_repeating(invia_offerte_canale, interval=300, first=10) # Ogni 5 minuti
    app.job_queue.run_repeating(cancella_offerte_vecchie, interval=3600, first=60) # Ogni ora
    app.job_queue.run_repeating(cancella_offerte_sito_vecchie, interval=1800, first=30) # Ogni mezz'ora
    
    # Schedulatore buonanotte e buongiorno
    from datetime import time as dt_time
    tz_rome = zoneinfo.ZoneInfo('Europe/Rome')
    app.job_queue.run_daily(invia_buonanotte, time=dt_time(hour=21, minute=0, tzinfo=tz_rome))
    app.job_queue.run_daily(invia_buongiorno, time=dt_time(hour=7, minute=0, tzinfo=tz_rome))
    
    # Pubblicità mirata sui social ogni 2 ore (dalle 7 alle 20:59)
    app.job_queue.run_repeating(invia_promo_social, interval=7200, first=10)

    # Avvio
    print("Bot in ascolto! Vai su Telegram e scrivigli un prodotto.")
    app.run_polling(poll_interval=3)

if __name__ == '__main__':
    main()
