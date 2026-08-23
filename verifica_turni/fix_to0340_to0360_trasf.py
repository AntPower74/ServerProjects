#!/usr/bin/env python3
import json

def parse_m(t_str):
    p = str(t_str).replace('.', ':').split(':')
    return int(p[0]) * 60 + int(p[1])

def fmt_time(m):
    h = (m // 60) % 24
    mins = m % 60
    return f"{h:02d}:{mins:02d}"

def fmt_durata(m):
    h = m // 60
    mins = m % 60
    return f"{h}h {mins:02d}m"

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] in ['To0340', 'To0360']:
        att = t['attivita']
        corse = [a for a in att if 'chiusura' not in a.get('descrizione', '').lower() and a.get('linea') != 'Sosta']
        
        arr_caselle_m = parse_m(corse[-1].get('arrivo'))
        trasf_end_m = arr_caselle_m + 25
        
        nuova = list(corse)
        nuova.append({
            'linea': 'Trasf',
            'descrizione': 'Rientro a vuoto raccordo: Caselle Aeroporto ➔ Torino Deposito (17 km)',
            'da': 'Caselle Aeroporto',
            'a': 'Torino Deposito',
            'partenza': fmt_time(arr_caselle_m),
            'arrivo': fmt_time(trasf_end_m),
            'km': '17,00'
        })
        nuova.append({
            'linea': 'Sosta',
            'descrizione': '☕ Sosta Obbligatoria CCNL (30 min) – Torino Deposito',
            'da': 'Torino Deposito',
            'a': 'Torino Deposito',
            'partenza': fmt_time(trasf_end_m),
            'arrivo': fmt_time(trasf_end_m + 30),
            'km': '-',
            'durata_sosta_m': 30,
            'is_sosta_deposito': True
        })
        nuova.append({
            'linea': 'Disp',
            'descrizione': 'Controllo finale e chiusura turno continuo – Torino Deposito',
            'da': 'Torino Deposito',
            'a': 'Torino Deposito',
            'partenza': fmt_time(trasf_end_m + 30),
            'arrivo': fmt_time(trasf_end_m + 40),
            'km': '-'
        })
        
        in_m = parse_m(t['inizio_servizio'])
        fin_m = trasf_end_m + 40
        n_m = fin_m - in_m if fin_m >= in_m else (1440 - in_m + fin_m)
        
        t['fine_servizio'] = fmt_time(fin_m)
        t['nastro'] = f"{n_m/60:.2f}"
        t['nastro_str'] = fmt_durata(n_m)
        t['nastro_m'] = n_m
        t['ore_lavoro'] = f"{n_m/60:.2f}"
        t['olg_str'] = fmt_durata(n_m)
        t['olg_m'] = n_m
        t['attivita'] = nuova

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ To0340 e To0360 rientri inseriti!")
