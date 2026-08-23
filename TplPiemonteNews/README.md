# Bot Telegram TPL Piemonte 🚌📰 (`TplPiemonteNews`)

Questo script in Python monitora in automatico le fonti di notizie ed avvisi sul Trasporto Pubblico Locale (TPL) in Piemonte e pubblica i nuovi aggiornamenti sul tuo Canale Telegram:

1. **GTT Torino** (Avvisi ufficiali e news)
2. **AMP** (Agenzia della Mobilità Piemontese)
3. **Arriva Italia Torino** (Avvisi di servizio)
4. **La Stampa** (Notizie su trasporti, bus, metro, scioperi)
5. **TorinoCronaca** (Cronaca e trasporti locali)
6. **Fonti Personalizzate Dinamiche** (Inviate direttamente via chat Telegram al bot)

---

## ⚡ Nuova Funzionalità: Aggiunta Dinamica delle Fonti
Puoi aggiungere **qualsiasi nuovo sito o feed RSS** direttamente da Telegram:
1. Apri la chat privata con il bot: **`@TPLPiemonteNewsbot`**
2. Invagli semplicemente un link (es. `https://sito-notizie-trasporti.it/rss` o `https://comune.torino.it/news`)
3. Il bot salverà automaticamente il link in `custom_sources.json`, ti risponderà con un messaggio di conferma `✅ Nuova fonte aggiunta con successo!` ed includerà la nuova fonte nelle scansioni periodiche!

---

## 📁 Posizione Progetto
Cartella: `/home/antonio/TplPiemonteNews/`

---

## 🕒 Regole di Programmazione
- **Frequenza:** Ogni 30 minuti.
- **Orari attivi:** Dalle 06:00 alle 22:00 (Pausa notturna 22:00 -> 06:00).
- **Crontab Attivo:** Configurato ed attivo automaticamente al boot del sistema.
