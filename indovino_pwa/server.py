#!/usr/bin/env python3
import http.server
import socketserver
import urllib.request
import urllib.parse
import json
import re
import time
import os
import threading
from collections import Counter
from datetime import datetime

PORT = 8085
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')
SIGNALS_FILE = os.path.join(BASE_DIR, 'signals_log.json')
ARCHIVE_FILE = os.path.join(BASE_DIR, 'archive', 'full_archive.json')
TELEGRAM_CONFIG_FILE = os.path.join(BASE_DIR, 'telegram_config.json')
SOURCE_URL = 'https://www.10elotto5.com/'

# Lock rientrante: protegge signals_log.json da letture/scritture concorrenti
# tra thread diversi (richieste HTTP, monitor 24/7) che altrimenti possono
# accavallarsi e sovrascriversi a vicenda, azzerando i segnali registrati.
signals_lock = threading.RLock()

cached_draws = []
last_fetch_time = 0
cached_archive = []  # Storico estrazioni passate
last_archive_load = 0

def load_archive():
    """Carica l'archivio storico dal file JSON (massimo 1 ricarica ogni ora)."""
    global cached_archive, last_archive_load
    now = time.time()
    if cached_archive and (now - last_archive_load < 3600):
        return cached_archive
    if os.path.exists(ARCHIVE_FILE):
        try:
            with open(ARCHIVE_FILE, 'r', encoding='utf-8') as f:
                cached_archive = json.load(f)
                last_archive_load = now
                print(f"[*] Archivio storico caricato: {len(cached_archive)} estrazioni")
        except Exception as e:
            print(f"[!] Errore lettura archivio: {e}")
    return cached_archive

def get_draws_with_history(live_draws, max_history=2000):
    """Combina estrazioni live di oggi con lo storico dell'archivio."""
    archive = load_archive()
    if not archive:
        return live_draws
    today = datetime.now().strftime('%Y-%m-%d')
    # Escludi le estrazioni di oggi dall'archivio (le abbiamo live e più aggiornate)
    hist = [d for d in archive if d.get('data') != today]
    # Prendi solo le ultime max_history dal passato + le live di oggi
    combined = hist[-(max_history):] + live_draws
    return combined

def load_telegram_config():
    if os.path.exists(TELEGRAM_CONFIG_FILE):
        try:
            with open(TELEGRAM_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def send_telegram_message(text):
    """Invia una notifica Telegram in background, senza bloccare il chiamante."""
    cfg = load_telegram_config()
    token = cfg.get('bot_token')
    chat_id = cfg.get('chat_id')
    if not token or not chat_id:
        return

    def _send():
        try:
            url = f'https://api.telegram.org/bot{token}/sendMessage'
            data = urllib.parse.urlencode({'chat_id': chat_id, 'text': text}).encode('utf-8')
            req = urllib.request.Request(url, data=data)
            urllib.request.urlopen(req, timeout=10).read()
        except Exception as e:
            print(f"[!] Errore invio notifica Telegram: {e}")

    threading.Thread(target=_send, daemon=True).start()

def load_signals():
    if os.path.exists(SIGNALS_FILE):
        try:
            with open(SIGNALS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_signals(signals):
    try:
        with open(SIGNALS_FILE, 'w', encoding='utf-8') as f:
            json.dump(signals, f, indent=2)
    except Exception as e:
        print(f"[!] Errore salvataggio segnali: {e}")

def _fetch_draws_10elotto5():
    req = urllib.request.Request(
        SOURCE_URL,
        headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
    )
    with urllib.request.urlopen(req, timeout=6) as resp:
        html = resp.read().decode('utf-8', errors='ignore')

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
                    'concorso': int(num),
                    'ora': draw_time,
                    'numeri': main_nums,
                    'extra': extra_nums,
                    'oro': int(oro) if oro.isdigit() else None,
                    'doppio_oro': int(d_oro) if d_oro.isdigit() else None
                })

    draws.sort(key=lambda x: x['concorso'])
    return draws


EL_ID_RE = re.compile(r'<h2 id="(\d+)"')
EL_NUMERI_RE = re.compile(
    r'class="tabella-dati grid grid-cols-5 md:grid-cols-10[^"]*">(.*?)</div></div></div>'
    r'<div class="grid md:grid-cols-2',
    re.DOTALL,
)
EL_NUM_RE = re.compile(r'class="numero bg-[a-z]+-\d+">(\d+)</p>')
EL_ORO_RE = re.compile(r'class="tabella bg-red-500">.*?<p class="numero"> (\d+) </p>', re.DOTALL)
EL_DOPPIO_ORO_RE = re.compile(r'class="tabella bg-red-700">.*?<p class="numero"> (\d+) </p>', re.DOTALL)
EL_EXTRA_RE = re.compile(r'Extra</h3>.*?</div>(.*?)</div></div></div>', re.DOTALL)


def _fetch_draws_estrazionilotto():
    today_str = datetime.now().strftime('%Y-%m-%d')
    url = f'https://www.estrazionilotto.it/10-e-lotto-ogni-5-minuti/archivio-storico/{today_str}/'
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    with urllib.request.urlopen(req, timeout=8) as resp:
        html = resp.read().decode('utf-8', errors='ignore')

    draws = []
    marks = list(EL_ID_RE.finditer(html))
    for i, m in enumerate(marks):
        concorso = int(m.group(1))
        start = m.start()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(html)
        block = html[start:end]

        numeri_block_m = EL_NUMERI_RE.search(block)
        if not numeri_block_m:
            continue
        numeri = [int(n) for n in EL_NUM_RE.findall(numeri_block_m.group(1))]
        if len(numeri) != 20:
            continue

        oro_m = EL_ORO_RE.search(block)
        doro_m = EL_DOPPIO_ORO_RE.search(block)
        if not oro_m or not doro_m:
            continue
        oro = int(oro_m.group(1))
        doppio_oro = int(doro_m.group(1))

        extra_m = EL_EXTRA_RE.search(block)
        extra = [int(n) for n in EL_NUM_RE.findall(extra_m.group(1))] if extra_m else []

        minuti = 5 + (concorso - 1) * 5
        ora = f'{minuti // 60:02d}:{minuti % 60:02d}'

        draws.append({
            'data': today_str,
            'concorso': concorso,
            'ora': ora,
            'numeri': sorted(numeri),
            'extra': extra,
            'oro': oro,
            'doppio_oro': doppio_oro,
        })
    draws.sort(key=lambda d: d['concorso'])
    return draws


def fetch_draws():
    global cached_draws, last_fetch_time
    now = time.time()
    if cached_draws and (now - last_fetch_time < 20):
        return cached_draws

    draws_a = None
    draws_b = None

    try:
        draws_a = _fetch_draws_10elotto5()
    except Exception as e:
        print(f"[!] Errore fonte 10elotto5.com: {e}")

    try:
        draws_b = _fetch_draws_estrazionilotto()
    except Exception as e:
        print(f"[!] Errore fonte estrazionilotto.it: {e}")

    draws = None
    if draws_a and draws_b:
        a_map = {d['concorso']: d for d in draws_a}
        b_map = {d['concorso']: d for d in draws_b}
        common = sorted(set(a_map) & set(b_map))
        if common:
            c = common[-1]  # concorso più recente presente in entrambe le fonti
            da, db = a_map[c], b_map[c]
            concordi = (
                set(da['numeri']) == set(db['numeri'])
                and da['oro'] == db['oro']
                and da['doppio_oro'] == db['doppio_oro']
            )
            if concordi:
                print(f"[*] Confronto fonti OK (concorso #{c})")
            else:
                print(f"[!] DISCREPANZA fonti sul concorso #{c}: 10elotto5.com {da['numeri']} vs estrazionilotto.it {db['numeri']}")
                send_telegram_message(
                    f"⚠️ Discrepanza tra le due fonti dati sul concorso #{c}!\n"
                    f"10elotto5.com: {da['numeri']} (oro {da['oro']}, doppio oro {da['doppio_oro']})\n"
                    f"estrazionilotto.it: {db['numeri']} (oro {db['oro']}, doppio oro {db['doppio_oro']})"
                )
        draws = draws_a
    elif draws_a:
        draws = draws_a
    elif draws_b:
        print("[!] Fonte primaria non disponibile, uso estrazionilotto.it come fallback")
        draws = draws_b

    if draws:
        cached_draws = draws
        last_fetch_time = now
        # Aggiorna il monitoraggio automatico dei segnali
        update_signals_tracker(draws)

    return cached_draws

def analyze_single_spy(draws, spy_num):
    if not draws:
        return None
    indices = [i for i in range(len(draws) - 1) if spy_num in draws[i]['numeri']]
    freq = len(indices)
    if freq == 0:
        return None
        
    post_nums = []
    post_oros = []
    for i in indices:
        post_nums.extend(draws[i+1]['numeri'])
        if draws[i+1]['oro'] is not None:
            post_oros.append(draws[i+1]['oro'])
            
    c_post = Counter(post_nums)
    c_oro = Counter(post_oros)
    top3 = [n for n, c in c_post.most_common(3)]
    top3_set = set(top3)
    
    ambi_post = 0
    terni_post = 0
    oro_hit_post = 0
    for i in indices:
        d_next = draws[i+1]
        hits = len(top3_set.intersection(set(d_next['numeri'])))
        if hits >= 2: ambi_post += 1
        if hits == 3: terni_post += 1
        if d_next['oro'] in top3_set: oro_hit_post += 1
        
    score = (ambi_post * 3.0) + (terni_post * 15.0) + (oro_hit_post * 2.0) + (freq * 0.5)
    top_oro = c_oro.most_common(1)[0][0] if c_oro else (top3[0] if top3 else None)
    
    return {
        'spy': spy_num,
        'freq': freq,
        'total_obs': len(draws),
        'pct_presence': round((freq / len(draws)) * 100, 1),
        'top3': top3,
        'top_oro': top_oro,
        'ambi_post': ambi_post,
        'terni_post': terni_post,
        'score': round(score, 1),
        'ranking_post': [{'num': n, 'count': c, 'pct': round((c/freq)*100, 1)} for n, c in c_post.most_common(15)]
    }

def get_best_spy(draws):
    spies = []
    for s in range(1, 91):
        res = analyze_single_spy(draws, s)
        if res and res['pct_presence'] >= 15.0:
            spies.append(res)
    spies.sort(key=lambda x: x['score'], reverse=True)
    return spies[0] if spies else None

def update_signals_tracker(draws):
    if not draws:
        return
    with signals_lock:
        signals = load_signals()
        latest = draws[-1]
        today_str = datetime.now().strftime('%Y-%m-%d')

        # 1. Rilevamento automatico: se esce la top spia, registriamo il segnale
        best_spy = get_best_spy(draws)
        if best_spy and (best_spy['spy'] in latest['numeri']):
            sig_id = f"sig_{today_str}_{latest['concorso']}_{best_spy['spy']}"
            exists = any(s['id'] == sig_id for s in signals)
            if not exists:
                new_sig = {
                    'id': sig_id,
                    'data': today_str,
                    'ora': latest['ora'],
                    'concorso_spia': latest['concorso'],
                    'spia': best_spy['spy'],
                    'terzina': best_spy['top3'],
                    'oro': best_spy['top_oro'],
                    'power_score': best_spy['score'],
                    'max_colpi': 20,
                    'stato': 'in_corso',
                    'colpi_trascorsi': 0,
                    'max_punti': 0,
                    'primo_ambo_colpo': None,
                    'primo_terno_colpo': None,
                    'oro_centrato': False,
                    'timeline': []
                }
                signals.insert(0, new_sig)
                print(f"[*] Nuovo Segnale Spia Registrato: Concorso #{latest['concorso']} Spia {best_spy['spy']}")

                cfg = load_telegram_config()
                min_score = cfg.get('strong_signal_min_score', 50)
                if best_spy['score'] >= min_score:
                    terzina_str = ' - '.join(str(n) for n in best_spy['top3'])
                    msg = (
                        f"🔮 SEGNALE FORTE 10eLotto (osservazione)\n\n"
                        f"Spia uscita: {best_spy['spy']} (concorso #{latest['concorso']}, ore {latest['ora']})\n"
                        f"Terzina tracciata: {terzina_str}\n"
                        f"Oro: {best_spy['top_oro']}\n"
                        f"Power score: {best_spy['score']}"
                    )
                    send_telegram_message(msg)

        # 2. Aggiornamento timeline di tutti i segnali aperti per le 20 estrazioni successive
        draw_map = {d['concorso']: d for d in draws}

        for s in signals:
            start_conc = s['concorso_spia']
            terzina_set = set(s['terzina'])

            timeline = []
            max_p = 0
            primo_ambo = None
            primo_terno = None
            oro_ok = False

            for step in range(1, s['max_colpi'] + 1):
                target_conc = start_conc + step
                if target_conc in draw_map:
                    d = draw_map[target_conc]
                    hits = len(terzina_set.intersection(set(d['numeri'])))
                    has_oro = (d['oro'] in terzina_set)

                    if hits > max_p: max_p = hits
                    if hits >= 2 and primo_ambo is None: primo_ambo = step
                    if hits == 3 and primo_terno is None: primo_terno = step
                    if has_oro: oro_ok = True

                    timeline.append({
                        'colpo': step,
                        'concorso': target_conc,
                        'ora': d['ora'],
                        'punti': hits,
                        'ha_oro': has_oro,
                        'estratti_presi': sorted(list(terzina_set.intersection(set(d['numeri']))))
                    })

            s['timeline'] = timeline
            s['colpi_trascorsi'] = len(timeline)
            s['max_punti'] = max_p
            s['primo_ambo_colpo'] = primo_ambo
            s['primo_terno_colpo'] = primo_terno
            s['oro_centrato'] = oro_ok

            if primo_terno is not None:
                s['stato'] = 'vinto_terno'
            elif primo_ambo is not None:
                s['stato'] = 'vinto_ambo'
            elif len(timeline) >= s['max_colpi']:
                s['stato'] = 'concluso_vuoto'
            else:
                s['stato'] = 'in_corso'

            if len(timeline) >= 5 and not s.get('notifica_5_colpi_inviata', False):
                s['notifica_5_colpi_inviata'] = True
                primi5 = timeline[:5]
                max_p5 = max(t['punti'] for t in primi5)
                oro5 = any(t['ha_oro'] for t in primi5)
                righe = '\n'.join(
                    f"  #{t['concorso']} (ore {t['ora']}): {t['punti']}/3 punti" + (' 🥇' if t['ha_oro'] else '')
                    for t in primi5
                )
                if max_p5 == 3:
                    esito = 'TERNO ✅'
                elif max_p5 == 2:
                    esito = 'AMBO ✅'
                else:
                    esito = 'nessuna vincita'
                msg = (
                    f"📊 Esito 5 colpi - Spia {s['spia']}\n"
                    f"Terzina giocata: {' - '.join(str(n) for n in s['terzina'])}\n\n"
                    f"{righe}\n\n"
                    f"Risultato: {esito}" + (' + Oro 🥇' if oro5 else '')
                )
                send_telegram_message(msg)

        save_signals(signals)

def get_signals_summary():
    signals = load_signals()
    total = len(signals)
    if total == 0:
        return {'total': 0, 'signals': [], 'stats': {}}
        
    conclusi_o_vinti = [s for s in signals if s['colpi_trascorsi'] >= 5 or s['stato'] in ['vinto_terno', 'vinto_ambo']]
    tot_eval = len(conclusi_o_vinti) if conclusi_o_vinti else total
    
    terni_count = sum(1 for s in signals if s['primo_terno_colpo'] is not None)
    ambi_count = sum(1 for s in signals if s['primo_ambo_colpo'] is not None)
    oro_count = sum(1 for s in signals if s['oro_centrato'])
    
    colpi_ambo = [s['primo_ambo_colpo'] for s in signals if s['primo_ambo_colpo'] is not None]
    colpi_terno = [s['primo_terno_colpo'] for s in signals if s['primo_terno_colpo'] is not None]
    
    media_colpo_ambo = round(sum(colpi_ambo) / len(colpi_ambo), 1) if colpi_ambo else 0
    media_colpo_terno = round(sum(colpi_terno) / len(colpi_terno), 1) if colpi_terno else 0
    
    # Financial calculation per signal & global
    tot_spesa_globale = 0.0
    tot_incasso_globale = 0.0
    tot_spesa_tp_globale = 0.0
    tot_incasso_tp_globale = 0.0
    
    for s in signals:
        timeline = s.get('timeline', [])
        spesa_20 = len(timeline) * 2.0
        incasso_20 = 0.0
        
        # Track cumulative winnings step by step
        running_win = 0.0
        running_cost = 0.0
        
        colpo_terno = s.get('primo_terno_colpo')
        colpo_ambo_oro = None
        colpo_primo_ambo = s.get('primo_ambo_colpo')
        
        win_at_terno = 0.0
        cost_at_terno = 0.0
        
        win_at_ambo_oro = 0.0
        cost_at_ambo_oro = 0.0
        
        for item in timeline:
            step = item['colpo']
            pts = item['punti']
            has_oro = item['ha_oro']
            
            win = 0.0
            if pts == 2:
                win = 25.0 if has_oro else 2.0
                if has_oro and colpo_ambo_oro is None:
                    colpo_ambo_oro = step
            elif pts == 3:
                win = 130.0 if has_oro else 45.0
                
            running_win += win
            running_cost = step * 2.0
            
            if colpo_terno is not None and step == colpo_terno:
                win_at_terno = running_win
                cost_at_terno = running_cost
                
            if colpo_ambo_oro is not None and step == colpo_ambo_oro and win_at_ambo_oro == 0.0:
                win_at_ambo_oro = running_win
                cost_at_ambo_oro = running_cost
                
        incasso_20 = running_win
        s['spesa_totale'] = round(spesa_20, 2)
        s['incasso_totale'] = round(incasso_20, 2)
        s['netto_totale'] = round(incasso_20 - spesa_20, 2)
        
        # Take profit logic: priority Terno > Ambo con Oro > Ambo base > Fine ciclo
        if colpo_terno is not None:
            s['spesa_take_profit'] = round(cost_at_terno, 2)
            s['incasso_take_profit'] = round(win_at_terno, 2)
            s['netto_take_profit'] = round(win_at_terno - cost_at_terno, 2)
            s['colpo_take_profit'] = colpo_terno
            s['tipo_tp'] = 'Terno'
        elif colpo_ambo_oro is not None:
            s['spesa_take_profit'] = round(cost_at_ambo_oro, 2)
            s['incasso_take_profit'] = round(win_at_ambo_oro, 2)
            s['netto_take_profit'] = round(win_at_ambo_oro - cost_at_ambo_oro, 2)
            s['colpo_take_profit'] = colpo_ambo_oro
            s['tipo_tp'] = 'Ambo con Oro'
        elif colpo_primo_ambo is not None:
            # check up to first ambo
            cost_a = colpo_primo_ambo * 2.0
            win_a = 2.0
            # if 20 draws completed and made more ambi, use total
            if incasso_20 > spesa_20:
                s['spesa_take_profit'] = round(spesa_20, 2)
                s['incasso_take_profit'] = round(incasso_20, 2)
                s['netto_take_profit'] = round(incasso_20 - spesa_20, 2)
                s['colpo_take_profit'] = len(timeline)
                s['tipo_tp'] = 'Multi-Ambi'
            else:
                s['spesa_take_profit'] = round(cost_a, 2)
                s['incasso_take_profit'] = round(win_a, 2)
                s['netto_take_profit'] = round(win_a - cost_a, 2)
                s['colpo_take_profit'] = colpo_primo_ambo
                s['tipo_tp'] = 'Ambo'
        else:
            s['spesa_take_profit'] = round(spesa_20, 2)
            s['incasso_take_profit'] = 0.0
            s['netto_take_profit'] = round(-spesa_20, 2)
            s['colpo_take_profit'] = None
            s['tipo_tp'] = 'Nessuna vincita'
            
        tot_spesa_globale += s['spesa_totale']
        tot_incasso_globale += s['incasso_totale']
        tot_spesa_tp_globale += s['spesa_take_profit']
        tot_incasso_tp_globale += s['incasso_take_profit']
        
    stats = {
        'totale_segnali': total,
        'totale_valutati': tot_eval,
        'pct_successo_ambo': round((ambi_count / max(1, tot_eval)) * 100, 1),
        'pct_successo_terno': round((terni_count / max(1, tot_eval)) * 100, 1),
        'pct_con_oro': round((oro_count / max(1, tot_eval)) * 100, 1),
        'media_colpo_ambo': media_colpo_ambo,
        'media_colpo_terno': media_colpo_terno,
        'terni_totali': terni_count,
        'ambi_totali': ambi_count,
        'totale_spesa': round(tot_spesa_globale, 2),
        'totale_incasso': round(tot_incasso_globale, 2),
        'saldo_netto': round(tot_incasso_globale - tot_spesa_globale, 2),
        'totale_spesa_tp': round(tot_spesa_tp_globale, 2),
        'totale_incasso_tp': round(tot_incasso_tp_globale, 2),
        'saldo_netto_tp': round(tot_incasso_tp_globale - tot_spesa_tp_globale, 2)
    }
    
    return {'signals': signals, 'stats': stats}

def get_recent_spy(draws, window=40):
    if not draws or len(draws) < window:
        return None
    sub = draws[-window:]
    spies = []
    for s in range(1, 91):
        res = analyze_single_spy(sub, s)
        if res and res['freq'] >= 5:
            spies.append(res)
    spies.sort(key=lambda x: x['score'], reverse=True)
    return spies[0] if spies else None

def get_radar_analysis(draws):
    if not draws or len(draws) < 10:
        return {}
    latest = draws[-1]
    curr_nums = latest['numeri']
    recent = draws[-10:]
    recent_all = [n for d in recent for n in d['numeri']]
    c_rec = Counter(recent_all)
    
    # 1. Eco candidates
    eco_ranked = sorted(curr_nums, key=lambda x: c_rec[x], reverse=True)[:4]
    
    # 2. Lateral neighbors
    neigh_pool = []
    for n in curr_nums:
        if n > 1 and (n-1) not in curr_nums: neigh_pool.append(n-1)
        if n < 90 and (n+1) not in curr_nums: neigh_pool.append(n+1)
    lateral_ranked = [n for n, c in Counter({x: c_rec[x] for x in neigh_pool}).most_common(4)]
    
    # 3. Baricentro
    bassa = sum(1 for n in curr_nums if 1 <= n <= 30)
    media = sum(1 for n in curr_nums if 31 <= n <= 60)
    alta = sum(1 for n in curr_nums if 61 <= n <= 90)
    
    # 4. Decine e Cadenze
    dec_counts = Counter([n // 10 for n in recent_all])
    cad_counts = Counter([n % 10 for n in recent_all])
    top_dec = dec_counts.most_common(2)
    top_cad = cad_counts.most_common(2)
    
    # Flow Terzina
    cand1 = eco_ranked[0] if eco_ranked else 1
    cand2 = lateral_ranked[0] if lateral_ranked else 2
    best_d = top_dec[0][0]
    pool3 = [n for n in range(best_d*10, min(91, best_d*10+10)) if n not in [cand1, cand2]]
    cand3 = sorted(pool3, key=lambda x: c_rec[x], reverse=True)[0] if pool3 else 3
    terzina_flow = sorted([cand1, cand2, cand3])
    
    return {
        'concorso_attuale': latest['concorso'],
        'ora_attuale': latest['ora'],
        'eco_candidati': eco_ranked,
        'laterali_candidati': lateral_ranked,
        'baricentro': {
            'bassa_1_30': round((bassa / 20) * 100, 1),
            'media_31_60': round((media / 20) * 100, 1),
            'alta_61_90': round((alta / 20) * 100, 1),
        },
        'decine_dominanti': [{'decina': f'{d*10}-{(d*10)+9}', 'uscite': cnt} for d, cnt in top_dec],
        'cadenze_dominanti': [{'cadenza': f'Cadenza {c}', 'uscite': cnt} for c, cnt in top_cad],
        'terzina_flow': terzina_flow,
        'oro_flow': cand1
    }

def get_profiler_100(draws):
    if not draws:
        return {}
    count = len(draws)
    sample_draws = draws[:min(100, count)]
    all_nums = [n for d in sample_draws for n in d['numeri']]
    c = Counter(all_nums)
    
    # Top 5 Hot Numbers
    top5 = [{'num': n, 'freq': cnt, 'pct': round((cnt/len(sample_draws))*100, 1)} for n, cnt in c.most_common(5)]
    
    # Top Decine & Cadenze
    dec_c = Counter([n // 10 for n in all_nums])
    cad_c = Counter([n % 10 for n in all_nums])
    
    top_dec = [{'decina': f'{d*10}-{(d*10)+9}', 'pct': round((cnt/len(all_nums))*100, 1)} for d, cnt in dec_c.most_common(2)]
    top_cad = [{'cadenza': f'Cadenza {k}', 'pct': round((cnt/len(all_nums))*100, 1)} for k, cnt in cad_c.most_common(2)]
    
    # Eco Index
    repeats = [len(set(sample_draws[k]['numeri']).intersection(set(sample_draws[k+1]['numeri']))) for k in range(len(sample_draws)-1)]
    avg_eco = round(sum(repeats) / max(1, len(repeats)), 2) if repeats else 0
    
    # Super-Spy
    spies = []
    for s in range(1, 91):
        res = analyze_single_spy(sample_draws, s)
        if res and res['pct_presence'] >= 18.0:
            spies.append(res)
    spies.sort(key=lambda x: x['score'], reverse=True)
    super_spy = spies[0] if spies else None
    
    # Semaforo
    semaforo = 'VERDE'
    motivo = 'Algoritmo in fase di alta regolarità e concentrazione numerica (Condizioni ottimali).'
    if avg_eco < 3.8 or not super_spy:
        semaforo = 'GIALLO'
        motivo = 'Concentrazione media, giocare solo segnali ad alto punteggio.'
    if count < 50:
        semaforo = 'IN_ATTESA'
        motivo = f'Campione in formazione ({count}/100 estrazioni). Quadro completo dopo le 08:30.'
        
    return {
        'concorsi_analizzati': len(sample_draws),
        'semaforo': semaforo,
        'motivo_semaforo': motivo,
        'indice_eco': avg_eco,
        'top5_guida': top5,
        'decine_canale': top_dec,
        'cadenze_canale': top_cad,
        'super_spy_certificata': super_spy
    }

BUILD_VERSION = 1787349900

def get_full_analysis():
    live_draws = fetch_draws()
    if not live_draws:
        return {'status': 'error', 'message': 'Nessun dato disponibile'}

    # Combina storico archivio + live per analisi più accurate
    draws = get_draws_with_history(live_draws)
    archive_count = len(draws) - len(live_draws)
        
    spies = []
    for s in range(1, 91):
        res = analyze_single_spy(draws, s)
        if res and res['pct_presence'] >= 15.0:
            spies.append(res)
            
    spies.sort(key=lambda x: x['score'], reverse=True)
    best_spy = spies[0] if spies else None
    recent_spy = get_recent_spy(live_draws, 40)  # Radar usa solo live per reattività
    radar = get_radar_analysis(live_draws)
    profiler = get_profiler_100(live_draws)
    
    return {
        'status': 'ok',
        'build_version': BUILD_VERSION,
        'server_time': datetime.now().strftime('%H:%M:%S'),
        'total_draws': len(draws),
        'total_draws_live': len(live_draws),
        'total_draws_archive': archive_count,
        'latest_draw': live_draws[-1] if live_draws else None,
        'best_spy': best_spy,
        'recent_spy': recent_spy,
        'radar': radar,
        'profiler_100': profiler,
        'top_spies': spies[:10],
        'draws': live_draws[::-1][:30]
    }

class PWAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def end_headers(self):
        # Force no-cache on all files so PWA always gets live updates automatically
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/data':
            data = get_full_analysis()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        elif parsed.path == '/api/signals':
            data = get_signals_summary()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        elif parsed.path == '/api/spy':
            params = urllib.parse.parse_qs(parsed.query)
            spy_num = int(params.get('num', [24])[0])
            draws = fetch_draws()
            res = analyze_single_spy(draws, spy_num)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(res or {}).encode('utf-8'))
        elif parsed.path == '/api/all_draws':
            draws = fetch_draws()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(draws[::-1]).encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/add_custom_signal':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            req = json.loads(body.decode('utf-8'))
            
            draws = fetch_draws()
            latest = draws[-1] if draws else {'concorso': 0, 'ora': '--:--'}
            today_str = datetime.now().strftime('%Y-%m-%d')
            
            spy = int(req.get('spy', 30))
            terzina = [int(x) for x in req.get('terzina', [54, 68, 90])]
            oro = int(req.get('oro', terzina[0]))
            
            sig_id = f"custom_{today_str}_{latest['concorso']}_{spy}_{int(time.time())}"
            new_sig = {
                'id': sig_id,
                'data': today_str,
                'ora': latest['ora'],
                'concorso_spia': latest['concorso'],
                'spia': spy,
                'terzina': terzina,
                'oro': oro,
                'power_score': float(req.get('power_score', 100.0)),
                'max_colpi': 20,
                'stato': 'in_corso',
                'colpi_trascorsi': 0,
                'max_punti': 0,
                'primo_ambo_colpo': None,
                'primo_terno_colpo': None,
                'oro_centrato': False,
                'timeline': []
            }
            with signals_lock:
                signals = load_signals()
                signals.insert(0, new_sig)
                save_signals(signals)
            update_signals_tracker(draws)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'signal': new_sig}).encode('utf-8'))
            
        elif parsed.path == '/api/delete_signal':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
                sig_id = data.get('id')
                if not sig_id:
                    self._send_json({'status': 'error', 'message': 'ID mancante'}, status=400)
                    return
                with signals_lock:
                    signals = load_signals()
                    signals = [s for s in signals if s.get('id') != sig_id]
                    save_signals(signals)
                self._send_json({'status': 'ok', 'deleted_id': sig_id})
            except Exception as e:
                self._send_json({'status': 'error', 'message': str(e)}, status=400)
            
        elif parsed.path == '/api/simulate':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            req_data = json.loads(body.decode('utf-8'))
            
            terzina = [int(x) for x in req_data.get('numbers', [59, 74, 84])]
            opt = req_data.get('option', 'oro')
            bet = float(req_data.get('bet', 1.0))
            
            draws = fetch_draws()
            cost_per_draw = bet * (2.0 if opt == 'oro' else (3.0 if opt == 'doppio_oro' else 1.0))
            
            terzina_set = set(terzina)
            tot_spesa = 0.0
            tot_incasso = 0.0
            ambi = 0
            ambi_oro = 0
            terni = 0
            terni_oro = 0
            win_log = []
            
            for d in draws:
                tot_spesa += cost_per_draw
                hits = len(terzina_set.intersection(set(d['numeri'])))
                has_oro1 = (d['oro'] in terzina_set)
                has_oro2 = (d['doppio_oro'] in terzina_set)
                has_any_oro = (has_oro1 or has_oro2) if opt == 'doppio_oro' else has_oro1
                
                win = 0.0
                if hits == 2:
                    ambi += 1
                    if opt in ['oro', 'doppio_oro'] and has_any_oro:
                        ambi_oro += 1
                        win = 25.0 * bet
                    else:
                        win = 2.0 * bet
                elif hits == 3:
                    terni += 1
                    if opt in ['oro', 'doppio_oro'] and has_any_oro:
                        terni_oro += 1
                        win = 130.0 * bet
                    else:
                        win = 45.0 * bet
                        
                tot_incasso += win
                saldo = tot_incasso - tot_spesa
                
                if win > 0:
                    win_log.append({
                        'concorso': d['concorso'],
                        'ora': d['ora'],
                        'punti': hits,
                        'oro': has_any_oro,
                        'vinto': win,
                        'saldo_progressivo': round(saldo, 2)
                    })
                    
            resp = {
                'terzina': terzina,
                'tot_concorsi': len(draws),
                'spesa': round(tot_spesa, 2),
                'incasso': round(tot_incasso, 2),
                'saldo': round(tot_incasso - tot_spesa, 2),
                'ambi': ambi,
                'ambi_oro': ambi_oro,
                'terni': terni,
                'terni_oro': terni_oro,
                'log': win_log[::-1]
            }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def background_monitor_worker():
    """Thread in background che monitora autonomamente 24/7 le estrazioni e registra i segnali."""
    print("🤖 Background Autonomous Monitor avviato con successo.")
    while True:
        try:
            draws = fetch_draws()
            if draws:
                update_signals_tracker(draws)
        except Exception as e:
            print(f"[!] Errore background monitor: {e}")
        time.sleep(45)

if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    
    # Avvio thread autonomo di monitoraggio continuo 24/7
    monitor_thread = threading.Thread(target=background_monitor_worker, daemon=True)
    monitor_thread.start()
    
    with socketserver.TCPServer(("", PORT), PWAHandler) as httpd:
        print(f"🚀 Server PWA Indovino 10eLotto attivo su http://localhost:{PORT}")
        httpd.serve_forever()
