import telebot
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import os
import threading

TELEGRAM_TOKEN = "8880281317:AAG2LUBFBDFf9cw2vWzmyfj-A7Wtkc8beLA"
CHAT_ID = "910932633"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ==========================================
# FUNZIONI DI RICERCA
# ==========================================

def salva_su_sito(nuovi_codici):
    if not nuovi_codici: return
    file_sito = '/home/antonio/sitoofferte/coupon_live.json'
    dati_esistenti = []
    if os.path.exists(file_sito):
        try:
            with open(file_sito, 'r') as f:
                dati_esistenti = json.load(f)
        except: pass
        
    # Aggiungi in testa i nuovi codici per mostrarli per primi
    dati_esistenti = nuovi_codici + dati_esistenti
    
    with open(file_sito, 'w') as f:
        json.dump(dati_esistenti, f, indent=4)

def analizza_testo(testo, sorgente):
    """Estrae i codici da un blocco di testo"""
    codici_trovati = []
    # Cerca "codice" o "coupon" o "sconto" seguito da testo in MAIUSCOLO o Numeri (min 4 caratteri)
    regex_codice = re.compile(r'(?:codice|coupon|sconto)[\s:]*([A-Z0-9]{4,20})', re.IGNORECASE)
    
    for match in regex_codice.finditer(testo):
        codice = match.group(1).upper()
        # Filtro falsi positivi comuni
        if codice not in ["SCONTO", "ESCLUSIVO", "AMAZON", "SOLO", "AGGIUNTIVO", "ALLA", "DEL"]:
            # Prendi un pezzettino di testo intorno al codice per dare contesto
            start = max(0, match.start() - 30)
            end = min(len(testo), match.end() + 60)
            contesto = testo[start:end].replace('\n', ' ').strip()
            
            # Evita duplicati nella stessa passata
            if non_presente(codice, codici_trovati):
                codici_trovati.append({
                    "canale": sorgente,
                    "codice": codice,
                    "testo_originale": f"...{contesto}..."
                })
    return codici_trovati

def non_presente(cod, lista):
    for item in lista:
        if item['codice'] == cod: return False
    return True

def scrape_telegram_channel(channel_name):
    url = f"https://t.me/s/{channel_name}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200: return []
        soup = BeautifulSoup(response.text, 'html.parser')
        messages = soup.find_all('div', class_='tgme_widget_message_text')
        
        risultati = []
        for msg in messages:
            testo = msg.get_text(separator=' ')
            trovati = analizza_testo(testo, channel_name)
            risultati.extend(trovati)
        return risultati
    except Exception as e:
        return []

def scrape_url_generico(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        # Molti siti richiedono un user agent valido per non bloccare la richiesta
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Rimuove javascript e CSS
        for script in soup(["script", "style"]):
            script.extract()
        
        testo_pulito = soup.get_text(separator=' ')
        
        # Nome del sito per la vetrina
        sito_nome = url.split('/')[2].replace('www.', '') if '//' in url else "Link Esterno"
        
        return analizza_testo(testo_pulito, sito_nome)
    except Exception as e:
        print(f"Errore URL: {e}")
        return None

# ==========================================
# LOOP AUTOMATICO (In Background)
# ==========================================

def loop_automatico():
    canali = ['scontianonimi', 'affaridanerd', 'offerte', 'scontiamazon']
    while True:
        try:
            print("Avvio scansione automatica background...")
            tutti_i_codici = []
            for canale in canali:
                tutti_i_codici.extend(scrape_telegram_channel(canale))
                time.sleep(1)
            
            if tutti_i_codici:
                salva_su_sito(tutti_i_codici)
                # Invia notifica solo del primo trovato per non spammare durante il cron
                bot.send_message(CHAT_ID, f"🔄 <b>Scansione automatica completata.</b> Trovati {len(tutti_i_codici)} codici totali.\nHanno aggiornato la vetrina del sito!", parse_mode="HTML")
            
        except Exception as e:
            print(f"Errore nel loop automatico: {e}")
            
        # Attende 60 minuti prima di rifarlo
        time.sleep(3600)

# ==========================================
# BOT TELEGRAM (Gestione Messaggi)
# ==========================================

@bot.message_handler(commands=['start', 'aiuto'])
def invia_benvenuto(message):
    testo = "👋 Ciao! Sono il tuo assistente Sconti.\n\nIncolla qui **qualsiasi link** di un sito o articolo (es. Discoup, Amazon, eBay) e io cercherò al suo interno dei codici sconto per te.\n\nSe trovo qualcosa, te lo invio subito e lo pubblico in automatico sul tuo sito web!"
    bot.reply_to(message, testo, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def analizza_messaggio(message):
    testo = message.text
    
    # Se il testo contiene un link (http o www)
    if "http" in testo or "www." in testo:
        # Estrai il link usando una regex basilare
        link_trovati = re.findall(r'(https?://[^\s]+)', testo)
        
        if link_trovati:
            url = link_trovati[0]
            bot.reply_to(message, f"🔍 Sto analizzando il link:\n{url}\n\nAttendi un attimo...")
            
            codici = scrape_url_generico(url)
            
            if codici is None:
                bot.reply_to(message, "❌ Non sono riuscito ad accedere a quel sito. Forse ha una protezione anti-bot o il link non è valido.")
            elif len(codici) == 0:
                bot.reply_to(message, "😔 Non ho trovato nessun codice sconto in quella pagina.")
            else:
                salva_su_sito(codici)
                risposta = f"🎉 <b>HO TROVATO {len(codici)} CODICI!</b> (Già pubblicati sul sito)\n\n"
                for item in codici:
                    risposta += f"✂️ Codice: <code>{item['codice']}</code>\n📝 {item['testo_originale']}\n\n"
                bot.reply_to(message, risposta, parse_mode="HTML")
        else:
            bot.reply_to(message, "Non ho trovato un link valido in questo messaggio.")
    else:
        bot.reply_to(message, "Incolla un link (es. https://www.discoup.com/...) per farmelo analizzare!")

if __name__ == "__main__":
    print("Avvio del Thread automatico...")
    # Avvia il loop in background per scansionare telegram ogni 60 min
    t = threading.Thread(target=loop_automatico)
    t.daemon = True
    t.start()
    
    print("Avvio del bot Telegram in polling...")
    # Avvia la ricezione dei messaggi istantanei
    bot.infinity_polling()
