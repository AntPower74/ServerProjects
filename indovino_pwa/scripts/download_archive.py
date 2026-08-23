#!/usr/bin/env python3
import urllib.request
import json
import re
import os
import time
from datetime import datetime, timedelta

ARCHIVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'archive')
os.makedirs(ARCHIVE_DIR, exist_ok=True)
ARCHIVE_FILE = os.path.join(ARCHIVE_DIR, 'full_archive.json')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}

def parse_html_table(html, date_str):
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
    draws = []
    for r in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', r, re.DOTALL)
        if len(cells) >= 5:
            num = re.sub(r'<[^>]+>', '', cells[0]).strip()
            draw_time = re.sub(r'<[^>]+>', '', cells[1]).strip()
            nums_raw = cells[2]
            
            extra_match = re.search(r'Extra:(.*)', nums_raw, re.DOTALL | re.IGNORECASE)
            if extra_match:
                main_raw = nums_raw[:extra_match.start()]
                extra_raw = extra_match.group(1)
            else:
                main_raw = nums_raw
                extra_raw = ''
                
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

def fetch_url(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[!] Errore fetch {url}: {e}")
        return None

def download_all():
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)
    
    today_str = today.strftime('%Y-%m-%d')
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    two_days_ago_str = two_days_ago.strftime('%Y-%m-%d')
    
    all_draws_map = {}
    
    if os.path.exists(ARCHIVE_FILE):
        try:
            with open(ARCHIVE_FILE, 'r', encoding='utf-8') as f:
                old = json.load(f)
                for d in old:
                    key = f"{d.get('data')}_{d.get('concorso')}"
                    all_draws_map[key] = d
            print(f"[*] Caricate {len(all_draws_map)} estrazioni esistenti dall'archivio locale.")
        except Exception as e:
            print(f"[!] Errore lettura archivio esistente: {e}")

    sources = [
        ('https://www.10elotto5.com/', today_str, 'Oggi (in corso)'),
        ('https://www.10elotto5.com/ieri', yesterday_str, 'Ieri'),
        ('https://www.10elotto5.com/2-giorni-fa', two_days_ago_str, '2 Giorni fa')
    ]
    
    for url, date_label, desc in sources:
        print(f"⬇️ Scaricamento {desc} ({date_label}) da {url}...")
        html = fetch_url(url)
        if html:
            draws = parse_html_table(html, date_label)
            print(f"   -> Estratte {len(draws)} estrazioni valide.")
            for d in draws:
                key = f"{d['data']}_{d['concorso']}"
                all_draws_map[key] = d
        time.sleep(1)
        
    consolidated = sorted(list(all_draws_map.values()), key=lambda x: (x['data'], x['concorso']))
    
    with open(ARCHIVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(consolidated, f, indent=2)
        
    print(f"\n✅ ARCHIVIO COMPLETATO E SALVATO IN: {ARCHIVE_FILE}")
    print(f"📊 Totale Estrazioni Archiviate: {len(consolidated)}")
    
    dates_counter = {}
    for d in consolidated:
        dates_counter[d['data']] = dates_counter.get(d['data'], 0) + 1
    for dt, cnt in sorted(dates_counter.items()):
        print(f"   - {dt}: {cnt} estrazioni")
        
    return consolidated

if __name__ == '__main__':
    download_all()
