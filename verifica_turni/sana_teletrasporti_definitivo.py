#!/usr/bin/env python3
import json

def parse_m(t_str):
    if not t_str: return 0
    t_clean = str(t_str).strip().replace('.', ':').replace(',', ':')
    p = t_clean.split(':')
    if len(p) == 1:
        try: return round(float(p[0]) * 60)
        except: return 0
    return int(p[0]) * 60 + int(p[1])

def fmt_time(m):
    h = (m // 60) % 24
    mins = m % 60
    return f"{h:02d}:{mins:02d}"

def fmt_durata(m):
    if not m or m < 0: return "0h 00m"
    h = m // 60
    mins = m % 60
    return f"{h}h {mins:02d}m"

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    code = t['codice_turno']
    att = t.get('attivita', [])
    dep = t.get('deposito', 'Deposito')
    
    if code in ['Pi0070', 'Bo3020']: continue
    
    # Rimuoviamo attività di chiusura duplicate
    corse_pure = [a for a in att if 'chiusura' not in a.get('descrizione', '').lower() and 'rientro a vuoto' not in a.get('descrizione', '').lower()]
    if not corse_pure: continue
    
    ult = corse_pure[-1]
    loc_fin = (ult.get('a') or ult.get('descrizione') or '').strip()
    arr_fin_m = parse_m(ult.get('arrivo'))
    
    nuova_lista = list(corse_pure)
    
    # 1. Caselle che finisce a Torino
    if code.startswith('Ca') and any(w in loc_fin.lower() for w in ['carlo felice', 'torino', 'porta nuova']):
        nuova_lista.append({
            'linea': 'Trasf',
            'descrizione': 'Rientro a vuoto: Torino ➔ Caselle Deposito (18 km)',
            'da': loc_fin,
            'a': 'Caselle Deposito',
            'partenza': fmt_time(arr_fin_m),
            'arrivo': fmt_time(arr_fin_m + 25),
            'km': '18,00'
        })
        nuova_lista.append({
            'linea': 'Disp',
            'descrizione': 'Controllo finale, rifornimento e chiusura turno – Caselle Deposito',
            'da': 'Caselle Deposito',
            'a': 'Caselle Deposito',
            'partenza': fmt_time(arr_fin_m + 25),
            'arrivo': fmt_time(arr_fin_m + 35),
            'km': '-'
        })
        fin_m = arr_fin_m + 35

    # 2. Perosa che finisce a Pinerolo
    elif code.startswith('Pe') and 'pinerolo' in loc_fin.lower() and 'perosa' not in loc_fin.lower():
        nuova_lista.append({
            'linea': 'Trasf',
            'descrizione': 'Rientro a vuoto SP 23: Pinerolo ➔ Perosa Argentina Deposito (18 km)',
            'da': loc_fin,
            'a': 'Perosa Argentina Deposito',
            'partenza': fmt_time(arr_fin_m),
            'arrivo': fmt_time(arr_fin_m + 20),
            'km': '18,00'
        })
        nuova_lista.append({
            'linea': 'Disp',
            'descrizione': 'Controllo finale e chiusura turno – Perosa Argentina Deposito',
            'da': 'Perosa Argentina Deposito',
            'a': 'Perosa Argentina Deposito',
            'partenza': fmt_time(arr_fin_m + 20),
            'arrivo': fmt_time(arr_fin_m + 30),
            'km': '-'
        })
        fin_m = arr_fin_m + 30

    # 3. Torino che finisce a Caselle
    elif code.startswith('To') and 'caselle' in loc_fin.lower() and 'torino' not in loc_fin.lower():
        nuova_lista.append({
            'linea': 'Trasf',
            'descrizione': 'Rientro a vuoto: Caselle Aeroporto ➔ Torino Deposito (17 km)',
            'da': loc_fin,
            'a': 'Torino Deposito',
            'partenza': fmt_time(arr_fin_m),
            'arrivo': fmt_time(arr_fin_m + 25),
            'km': '17,00'
        })
        nuova_lista.append({
            'linea': 'Disp',
            'descrizione': 'Controllo finale e chiusura turno – Torino Deposito',
            'da': 'Torino Deposito',
            'a': 'Torino Deposito',
            'partenza': fmt_time(arr_fin_m + 25),
            'arrivo': fmt_time(arr_fin_m + 35),
            'km': '-'
        })
        fin_m = arr_fin_m + 35

    else:
        nuova_lista.append({
            'linea': 'Disp',
            'descrizione': f"Rientro deposito e chiusura turno – {dep} Deposito",
            'da': f"{dep} Deposito",
            'a': f"{dep} Deposito",
            'partenza': fmt_time(arr_fin_m),
            'arrivo': fmt_time(arr_fin_m + 10),
            'km': '-'
        })
        fin_m = arr_fin_m + 10

    in_m = parse_m(t['inizio_servizio'])
    nastro_m = fin_m - in_m if fin_m >= in_m else (1440 - in_m + fin_m)

    t['fine_servizio'] = fmt_time(fin_m)
    t['nastro'] = f"{nastro_m/60:.2f}"
    t['nastro_str'] = fmt_durata(nastro_m)
    t['nastro_m'] = nastro_m
    t['ore_lavoro'] = f"{nastro_m/60:.2f}"
    t['olg_str'] = fmt_durata(nastro_m)
    t['olg_m'] = nastro_m
    t['attivita'] = nuova_lista

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ Sanatura completata con precisione assoluta!")
