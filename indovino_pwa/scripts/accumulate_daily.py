#!/usr/bin/env python3
"""
Script di Accumulo Automatico Giornaliero
Scarica le estrazioni di ieri e le aggiunge all'archivio permanente.
Da eseguire ogni giorno automaticamente via cron alle 01:00.
"""
import urllib.request
import json
import re
import os
import time
import sys
from datetime import datetime, timedelta

ARCHIVE_DIR = '/home/antonio/indovino_pwa/archive'
ARCHIVE_FILE = os.path.join(ARCHIVE_DIR, 'full_archive.json')
LOG_FILE = os.path.join(ARCHIVE_DIR, 'accumulo.log')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

os.makedirs(ARCHIVE_DIR, exist_ok=True)

def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        log(f"[!] Errore fetch {url}: {e}")
        return None

def parse_draws(html, date_str):
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
    draws = []
    for r in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', r, re.DOTALL)
        if len(cells) >= 5:
            num = re.sub(r'<[^>]+>', '', cells[0]).strip()
            draw_time = re.sub(r'<[^>]+>', '', cells[1]).strip()
            nums_raw = cells[2]
            extra_match = re.search(r'Extra:(.*)', nums_raw, re.DOTALL | re.IGNORECASE)
            main_raw = nums_raw[:extra_match.start()] if extra_match else nums_raw
            extra_raw = extra_match.group(1) if extra_match else ''
            main_nums = [int(x) for x in re.findall(r'\b\d{1,2}\b', re.sub(r'<[^>]+>', ' ', main_raw))]
            extra_nums = [int(x) for x in re.findall(r'\b\d{1,2}\b', re.sub(r'<[^>]+>', ' ', extra_raw))]
            oro = re.sub(r'<[^>]+>', '', cells[3]).strip()
            d_oro = re.sub(r'<[^>]+>', '', cells[4]).strip()
            if num.isdigit() and len(main_nums) == 20:
                draws.append({
                    'data': date_str,
                    'concorso': int(num),
                    'ora': draw_time,
                    'numeri': main_nums,
                    'extra': extra_nums,
                    'oro': int(oro) if oro.isdigit() else None,
                    'doppio_oro': int(d_oro) if d_oro.isdigit() else None
                })
    draws.sort(key=lambda x: x['concorso'])
    return draws

def load_archive():
    if os.path.exists(ARCHIVE_FILE):
        try:
            with open(ARCHIVE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_archive(draws):
    with open(ARCHIVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(draws, f, indent=2, ensure_ascii=False)

def run_accumulation():
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)

    yesterday_str = yesterday.strftime('%Y-%m-%d')
    two_days_ago_str = two_days_ago.strftime('%Y-%m-%d')

    log(f"=== Avvio Accumulo Giornaliero ===")
    
    # Carica archivio esistente
    existing = load_archive()
    existing_keys = {f"{d['data']}_{d['concorso']}" for d in existing}
    log(f"Archivio esistente: {len(existing)} estrazioni")
    
    # Mappa per merge rapido
    archive_map = {f"{d['data']}_{d['concorso']}": d for d in existing}
    new_count = 0

    # Scarica ieri (fonte primaria: /ieri)
    sources = [
        ('https://www.10elotto5.com/ieri', yesterday_str),
        ('https://www.10elotto5.com/2-giorni-fa', two_days_ago_str),
    ]

    for url, date_str in sources:
        # Controlla se abbiamo già dati completi per quel giorno
        existing_for_day = [d for d in existing if d['data'] == date_str]
        if len(existing_for_day) >= 285:
            log(f"✓ {date_str}: già {len(existing_for_day)} estrazioni archiviate, skip.")
            continue

        log(f"⬇️ Scaricamento {date_str} da {url}...")
        html = fetch_url(url)
        if not html:
            continue

        draws = parse_draws(html, date_str)
        log(f"   -> Trovate {len(draws)} estrazioni")

        added = 0
        for d in draws:
            key = f"{d['data']}_{d['concorso']}"
            if key not in existing_keys:
                archive_map[key] = d
                existing_keys.add(key)
                added += 1
                new_count += 1
        log(f"   -> Aggiunte {added} nuove estrazioni (tot giorno: {len(draws)})")
        time.sleep(1)

    # Salva archivio aggiornato
    consolidated = sorted(list(archive_map.values()), key=lambda x: (x['data'], x['concorso']))
    save_archive(consolidated)

    # Report finale
    log(f"")
    log(f"✅ Accumulo completato!")
    log(f"📊 Totale archivio: {len(consolidated)} estrazioni")
    log(f"🆕 Nuove estrazioni aggiunte oggi: {new_count}")
    
    # Statistiche per giorno
    days_count = {}
    for d in consolidated:
        days_count[d['data']] = days_count.get(d['data'], 0) + 1
    for dt, cnt in sorted(days_count.items())[-7:]:
        log(f"   - {dt}: {cnt} estrazioni")
    
    return len(consolidated)

if __name__ == '__main__':
    total = run_accumulation()
    sys.exit(0)
