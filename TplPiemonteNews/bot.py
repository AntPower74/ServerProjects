#!/usr/bin/env python3
"""
TPL Piemonte News Bot (Telegram + WhatsApp)
Filtra e pubblica ESCLUSIVAMENTE notizie riguardanti il Trasporto Pubblico Locale (TPL),
bus, autobus, linee, fermate e sciopero.

Fonti Predefinite:
1. GTT Torino
2. AMP - Agenzia Mobilità Piemontese
3. Arriva Italia Torino
4. La Stampa (Sezione Torino / Trasporti)
5. TorinoCronaca

+ Fonti Dinamiche (es. TorinoToday) inviate in chat al Bot Telegram @TPLPiemonteNewsbot
"""

import os
import json
import logging
import urllib.parse
import re
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import feedparser

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "published_news.json")
CUSTOM_SOURCES_FILE = os.path.join(BASE_DIR, "custom_sources.json")
STATE_FILE = os.path.join(BASE_DIR, "bot_state.json")

# Parole chiave RIGIDE sul TPL e Bus/Autobus
TPL_BUS_KEYWORDS = [
    "tpl", "trasporto pubblico", "trasporti pubblici", "trasporto locale",
    "bus", "autobus", "pullman", "navetta", "gtt", "arriva", "autolinea", "autolinee",
    "capolinea", "corsia riservata", "fermata", "deviazione linea", "cambio percorso",
    "sciopero", "biglietto", "abbonamento", "tram", "metro", "metropolitana",
    "trenitalia", "sfm", "servizio urbano", "servizio extraurbano", "muoversi a torino",
    "agenzia mobilità", "viabilità bus", "linea bus", "deposito nizza"
]

def is_tpl_bus_related(title, summary=""):
    """Verifica in modo rigido che la notizia parli di TPL, Bus o Trasporti Pubblici."""
    full_text = f"{title} {summary}".lower()
    return any(kw in full_text for kw in TPL_BUS_KEYWORDS)

def load_json(filepath, default_value):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Errore lettura {filepath}: {e}")
    return default_value

def save_json(filepath, data):
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Errore scrittura {filepath}: {e}")

# --- INVIO TELEGRAM ---
def send_telegram_post(token, chat_id, text, image_url=None):
    if image_url:
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": image_url,
            "caption": text,
            "parse_mode": "HTML"
        }
        try:
            res = requests.post(url, json=payload, timeout=10)
            res_data = res.json()
            if res_data.get("ok"):
                return True
            else:
                logging.warning(f"Invio foto Telegram fallito, riprovo come testo semplice: {res_data}")
        except Exception as e:
            logging.warning(f"Eccezione durante invio foto: {e}")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        res_data = res.json()
        if not res_data.get("ok"):
            logging.error(f"Errore invio testo Telegram ({chat_id}): {res_data}")
            return False
        return True
    except Exception as e:
        logging.error(f"Eccezione invio Telegram: {e}")
        return False

# --- INVIO WHATSAPP ---
def send_whatsapp_post(api_url, token, channel_id, text, image_url=None):
    if not api_url or not channel_id:
        return False

    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = {
        "to": channel_id,
        "chatId": channel_id,
        "body": text,
        "caption": text,
        "message": text,
        "text": text
    }
    if image_url:
        payload["media"] = image_url
        payload["mediaUrl"] = image_url
        payload["image"] = image_url

    try:
        res = requests.post(api_url, json=payload, headers=headers, timeout=10)
        return res.status_code in [200, 201]
    except Exception as e:
        logging.error(f"Eccezione durante l'invio WhatsApp: {e}")
        return False

def clean_html(raw_html):
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ").strip()
    return " ".join(text.split())

def extract_image_from_url(article_url):
    try:
        res = requests.get(article_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            og_img = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"})
            if og_img and og_img.get("content"):
                img_src = og_img["content"]
                if not img_src.startswith("http"):
                    img_src = urllib.parse.urljoin(article_url, img_src)
                return img_src
            
            img = soup.find("img", src=True)
            if img and img.get("src"):
                img_src = img["src"]
                if not img_src.startswith("http"):
                    img_src = urllib.parse.urljoin(article_url, img_src)
                if not any(skip in img_src.lower() for skip in ["logo", "icon", "banner-ad", "pixel", "avatar"]):
                    return img_src
    except Exception as e:
        pass
    return None

def extract_image_from_rss_entry(entry):
    if "media_content" in entry:
        for media in entry.media_content:
            if media.get("medium") == "image" or "image" in media.get("type", ""):
                return media.get("url")
            if media.get("url"):
                return media.get("url")

    if "media_thumbnail" in entry and entry.media_thumbnail:
        return entry.media_thumbnail[0].get("url")

    if "enclosures" in entry:
        for enc in entry.enclosures:
            if "image" in enc.get("type", ""):
                return enc.get("href")

    summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
    if summary:
        soup = BeautifulSoup(summary, "html.parser")
        img = soup.find("img")
        if img and img.get("src"):
            return img["src"]

    return None

def process_telegram_updates(token):
    state = load_json(STATE_FILE, {"last_update_id": 0})
    last_id = state.get("last_update_id", 0)
    
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    params = {"offset": last_id + 1, "timeout": 5}
    
    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        if not data.get("ok"):
            return
        
        custom_sources = load_json(CUSTOM_SOURCES_FILE, [])

        for update in data.get("result", []):
            update_id = update["update_id"]
            if update_id > last_id:
                last_id = update_id
                
            message = update.get("message")
            if not message or "text" not in message:
                continue
                
            sender_id = message["chat"]["id"]
            text = message["text"].strip()
            
            urls_found = re.findall(r'https?://[^\s]+', text)
            if urls_found:
                new_added = []
                for new_url in urls_found:
                    if new_url not in custom_sources:
                        custom_sources.append(new_url)
                        new_added.append(new_url)
                        
                if new_added:
                    save_json(CUSTOM_SOURCES_FILE, custom_sources)
                    reply_text = f"✅ <b>Nuova fonte aggiunta!</b>\n\nFiltrerò i seguenti link pubblicando solo notizie su <b>TPL e Bus</b>:\n"
                    reply_text += "\n".join([f"• <code>{u}</code>" for u in new_added])
                    send_telegram_post(token, sender_id, reply_text)
                    logging.info(f"Nuova fonte registrata da Telegram: {new_added}")
                else:
                    send_telegram_post(token, sender_id, "ℹ️ Questo link è già presente tra le fonti monitorate.")
            elif text.startswith("/start") or text.startswith("/help"):
                welcome = (
                    "👋 <b>Benvenuto nel Bot TPL Piemonte News!</b>\n\n"
                    "Invia qui qualsiasi link: lo monitorerò ed estrarrò **esclusivamente le notizie su TPL, Bus ed Autobus** per il canale!"
                )
                send_telegram_post(token, sender_id, welcome)

        state["last_update_id"] = last_id
        save_json(STATE_FILE, state)

    except Exception as e:
        logging.warning(f"Errore controllo getUpdates Telegram: {e}")

# --- SCRAPERS RIGIDI ---

def fetch_gtt_news():
    articles = []
    url = "https://www.gtt.to.it/cms/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            seen_urls = set()
            for a in soup.find_all("a", href=True):
                href = a["href"]
                title = a.get_text(strip=True)
                if ("//avvisi-e-informazioni-di-servizio/" in href or "/notizie-eventi-e-informazioni/" in href) and len(title) > 15:
                    full_url = urllib.parse.urljoin(url, href)
                    if full_url not in seen_urls and is_tpl_bus_related(title):
                        seen_urls.add(full_url)
                        img_url = extract_image_from_url(full_url)
                        articles.append({
                            "id": full_url,
                            "title": title,
                            "summary": "Avviso o comunicazione ufficiale GTT Torino.",
                            "url": full_url,
                            "image_url": img_url,
                            "source": "GTT Torino"
                        })
    except Exception as e:
        logging.warning(f"Errore scraping GTT: {e}")
    return articles

def fetch_amp_news():
    articles = []
    url = "https://mtm.torino.it/it/notizie/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            seen_urls = set()
            for a in soup.select("article a, .entry-title a, h2.entry-title a"):
                title = a.get_text(strip=True)
                href = a.get("href")
                if title and href and "category" not in href and href not in seen_urls and len(title) > 15:
                    if is_tpl_bus_related(title):
                        seen_urls.add(href)
                        img_url = extract_image_from_url(href)
                        articles.append({
                            "id": href,
                            "title": title,
                            "summary": "Comunicato ufficiale dell'Agenzia della Mobilità Piemontese (AMP).",
                            "url": href,
                            "image_url": img_url,
                            "source": "AMP Piemonte"
                        })
    except Exception as e:
        logging.warning(f"Errore scraping AMP: {e}")
    return articles

def fetch_arriva_news():
    articles = []
    url = "https://torino.arriva.it/notice/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            seen_urls = set()
            for a in soup.find_all("a", href=True):
                href = a["href"]
                title = a.get_text(strip=True)
                if "notice/" in href and href != "https://torino.arriva.it/notice/" and len(title) > 15:
                    if href not in seen_urls and is_tpl_bus_related(title):
                        seen_urls.add(href)
                        articles.append({
                            "id": href,
                            "title": title,
                            "summary": "Avviso al pubblico per le linee extraurbane Arriva Italia (Torino e Provincia).",
                            "url": href,
                            "image_url": None,
                            "source": "Arriva Italia Torino"
                        })
    except Exception as e:
        logging.warning(f"Errore scraping Arriva Torino: {e}")
    return articles

def fetch_lastampa_news():
    articles = []
    rss_urls = ["https://www.lastampa.it/rss/torino.xml", "https://www.lastampa.it/rss/cronaca.xml"]
    for feed_url in rss_urls:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:
                title = entry.title
                link = entry.link
                summary = clean_html(getattr(entry, "summary", ""))
                if is_tpl_bus_related(title, summary):
                    img_url = extract_image_from_rss_entry(entry) or extract_image_from_url(link)
                    articles.append({
                        "id": link,
                        "title": title,
                        "summary": summary[:200] + "..." if len(summary) > 200 else summary,
                        "url": link,
                        "image_url": img_url,
                        "source": "La Stampa"
                    })
        except Exception as e:
            logging.warning(f"Errore RSS La Stampa ({feed_url}): {e}")
    return articles

def fetch_torinocronaca_news():
    articles = []
    url = "https://www.torinocronaca.it/rss"
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            title = entry.title
            link = entry.link
            summary = clean_html(getattr(entry, "summary", ""))
            if is_tpl_bus_related(title, summary):
                img_url = extract_image_from_rss_entry(entry) or extract_image_from_url(link)
                articles.append({
                    "id": link,
                    "title": title,
                    "summary": summary[:200] + "..." if len(summary) > 200 else summary,
                    "url": link,
                    "image_url": img_url,
                    "source": "TorinoCronaca"
                })
    except Exception as e:
        logging.warning(f"Errore RSS TorinoCronaca: {e}")
    return articles

def fetch_custom_source_news(target_url):
    """Estrazione con filtro RIGIDO su TPL e Bus per siti generici (es. TorinoToday)."""
    articles = []
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        feed = feedparser.parse(target_url)
        if feed.entries:
            for entry in feed.entries[:10]:
                title = entry.title
                link = getattr(entry, "link", target_url)
                summary = clean_html(getattr(entry, "summary", ""))
                if is_tpl_bus_related(title, summary):
                    img_url = extract_image_from_rss_entry(entry) or extract_image_from_url(link)
                    domain = urllib.parse.urlparse(target_url).netloc
                    articles.append({
                        "id": link,
                        "title": title,
                        "summary": summary[:200] + "..." if len(summary) > 200 else summary,
                        "url": link,
                        "image_url": img_url,
                        "source": domain
                    })
            return articles

        res = requests.get(target_url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            domain = urllib.parse.urlparse(target_url).netloc
            seen_urls = set()
            for a in soup.find_all("a", href=True):
                href = a["href"]
                title = a.get_text(strip=True)
                if len(title) > 15 and is_tpl_bus_related(title):
                    full_url = urllib.parse.urljoin(target_url, href)
                    if full_url not in seen_urls and full_url != target_url:
                        seen_urls.add(full_url)
                        img_url = extract_image_from_url(full_url)
                        articles.append({
                            "id": full_url,
                            "title": title,
                            "summary": f"Notizia TPL/Bus estratta da {domain}.",
                            "url": full_url,
                            "image_url": img_url,
                            "source": domain
                        })
    except Exception as e:
        logging.warning(f"Errore scraping fonte personalizzata ({target_url}): {e}")
    return articles

def format_post(article, is_whatsapp=False):
    source_emoji = {
        "GTT Torino": "🚌",
        "AMP Piemonte": "🏛️",
        "Arriva Italia Torino": "🚍",
        "La Stampa": "📰",
        "TorinoCronaca": "🗞️"
    }.get(article['source'], "🚌")

    if is_whatsapp:
        text = f"{source_emoji} *{article['source']}*\n\n"
        text += f"*{article['title']}*\n\n"
        if article.get('summary'):
            text += f"{article['summary']}\n\n"
        text += f"🔗 {article['url']}\n\n"
        text += "#TPLPiemonte #Autobus #GTT #Infomobilità"
    else:
        text = f"<b>{source_emoji} {article['source']}</b>\n\n"
        text += f"<b>{article['title']}</b>\n\n"
        if article.get('summary'):
            text += f"{article['summary']}\n\n"
        text += f"🔗 <a href='{article['url']}'>Leggi la notizia completa</a>\n\n"
        text += "#TPLPiemonte #Autobus #GTT #Infomobilità"
    return text

def main():
    tg_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    tg_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    wa_api_url = os.getenv("WHATSAPP_API_URL")
    wa_token = os.getenv("WHATSAPP_TOKEN")
    wa_channel_id = os.getenv("WHATSAPP_CHANNEL_ID")

    if not tg_bot_token or not tg_chat_id:
        logging.error("TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID non configurati!")
        return

    process_telegram_updates(tg_bot_token)

    sent_ids = set(load_json(DB_FILE, []))
    new_sent = 0

    all_articles = []
    built_in_fetchers = [
        fetch_gtt_news,
        fetch_amp_news,
        fetch_arriva_news,
        fetch_lastampa_news,
        fetch_torinocronaca_news
    ]

    for fetcher in built_in_fetchers:
        all_articles.extend(fetcher())

    custom_sources = load_json(CUSTOM_SOURCES_FILE, [])
    for custom_url in custom_sources:
        all_articles.extend(fetch_custom_source_news(custom_url))

    for art in all_articles:
        art_id = art["id"]
        if art_id not in sent_ids:
            logging.info(f"Invio notizia filtrata TPL/Bus ({art['source']}): {art['title']}")
            
            tg_text = format_post(art, is_whatsapp=False)
            img_url = art.get("image_url")
            
            tg_success = send_telegram_post(tg_bot_token, tg_chat_id, tg_text, image_url=img_url)
            
            if wa_api_url and wa_channel_id:
                wa_text = format_post(art, is_whatsapp=True)
                send_whatsapp_post(wa_api_url, wa_token, wa_channel_id, wa_text, image_url=img_url)

            if tg_success:
                sent_ids.add(art_id)
                new_sent += 1
                time.sleep(1)

    save_json(DB_FILE, list(sent_ids))
    logging.info(f"Esecuzione completata. Nuove notizie inviate: {new_sent}")

if __name__ == "__main__":
    main()
