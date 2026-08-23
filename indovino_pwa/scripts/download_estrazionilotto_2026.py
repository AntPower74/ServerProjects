#!/usr/bin/env python3
"""
Scarica l'archivio storico 10eLotto ogni 5 minuti da estrazionilotto.it,
giorno per giorno, limitato all'anno 2026 (dal 1 gennaio a oggi).
Fonte corretta: gioco "ogni 5 minuti" (non il Lotto bi-settimanale).
"""
import urllib.request
import re
import json
import os
import time
from datetime import date, timedelta

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
BASE_URL = 'https://www.estrazionilotto.it/10-e-lotto-ogni-5-minuti/archivio-storico/{day}/'
ARCHIVE_DIR = '/home/antonio/indovino_pwa/archive'
OUT_FILE = os.path.join(ARCHIVE_DIR, 'estrazionilotto_2026.json')
LOG_FILE = os.path.join(ARCHIVE_DIR, 'estrazionilotto_2026.log')

ID_RE = re.compile(r'<h2 id="(\d+)"')
NUMERI_RE = re.compile(
    r'class="tabella-dati grid grid-cols-5 md:grid-cols-10[^"]*">(.*?)</div></div></div>'
    r'<div class="grid md:grid-cols-2',
    re.DOTALL,
)
NUM_RE = re.compile(r'class="numero bg-[a-z]+-\d+">(\d+)</p>')
ORO_RE = re.compile(r'class="tabella bg-red-500">.*?<p class="numero"> (\d+) </p>', re.DOTALL)
DOPPIO_ORO_RE = re.compile(r'class="tabella bg-red-700">.*?<p class="numero"> (\d+) </p>', re.DOTALL)
EXTRA_RE = re.compile(r'Extra</h3>.*?</div>(.*?)</div></div></div>', re.DOTALL)


def parse_day(html, day_str):
    draws = []
    marks = list(ID_RE.finditer(html))
    for i, m in enumerate(marks):
        concorso = int(m.group(1))
        start = m.start()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(html)
        block = html[start:end]

        numeri_block_m = NUMERI_RE.search(block)
        if not numeri_block_m:
            continue
        numeri = [int(n) for n in NUM_RE.findall(numeri_block_m.group(1))]
        if len(numeri) != 20:
            continue

        oro_m = ORO_RE.search(block)
        doro_m = DOPPIO_ORO_RE.search(block)
        if not oro_m or not doro_m:
            continue
        oro = int(oro_m.group(1))
        doppio_oro = int(doro_m.group(1))

        extra_m = EXTRA_RE.search(block)
        extra = [int(n) for n in NUM_RE.findall(extra_m.group(1))] if extra_m else []

        minuti = 5 + (concorso - 1) * 5
        ora = f'{minuti // 60:02d}:{minuti % 60:02d}'

        draws.append({
            'data': day_str,
            'concorso': concorso,
            'ora': ora,
            'numeri': sorted(numeri),
            'extra': extra,
            'oro': oro,
            'doppio_oro': doppio_oro,
        })
    draws.sort(key=lambda d: d['concorso'])
    return draws


def fetch_day(day_str):
    url = BASE_URL.format(day=day_str)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=12) as resp:
        return resp.read().decode('utf-8', errors='ignore')


def main():
    start = date(2026, 1, 1)
    end = date.today()

    all_draws = []
    log_lines = [f'=== Download estrazionilotto.it 2026 ({start} -> {end}) ===']

    d = start
    while d <= end:
        day_str = d.isoformat()
        try:
            html = fetch_day(day_str)
            draws = parse_day(html, day_str)
            all_draws.extend(draws)
            msg = f'{day_str}: {len(draws)} estrazioni'
        except Exception as e:
            msg = f'{day_str}: ERRORE {e}'
        print(msg)
        log_lines.append(msg)
        time.sleep(0.4)
        d += timedelta(days=1)

    all_draws.sort(key=lambda x: (x['data'], x['concorso']))
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_draws, f, indent=2, ensure_ascii=False)

    summary = f'\nTotale: {len(all_draws)} estrazioni salvate in {OUT_FILE}'
    print(summary)
    log_lines.append(summary)
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(log_lines) + '\n')


if __name__ == '__main__':
    main()
