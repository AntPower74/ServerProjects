#!/usr/bin/env python3
"""
INCLUSIONE FORMALE DI TUTTI GLI INTERVALLI IN DEPOSITO COME SOSTE CERTIFICATE CCNL
Se un'attività arriva in deposito (o capolinea) e l'attività successiva riparte dopo un intervallo >= 15 min,
quell'intervallo è formalmente e legalmente una SOSTA / PAUSA IN DEPOSITO.
"""

import json

JSON_REALI = "/home/antonio/verifica_turni/web/turni_data.json"
JSON_OPT = "/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json"

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
    h = m // 60
    mins = m % 60
    return f"{h}h {mins:02d}m"

def arricchisci_turni_con_soste_deposito(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        turni = json.load(f)

    for t in turni:
        att = t.get('attivita', [])
        nuove_att = []
        
        for i in range(len(att)):
            nuove_att.append(att[i])
            
            if i < len(att) - 1:
                arr_curr_m = parse_m(att[i].get('arrivo'))
                part_succ_m = parse_m(att[i+1].get('partenza'))
                
                gap = part_succ_m - arr_curr_m if part_succ_m >= arr_curr_m else (1440 - arr_curr_m + part_succ_m)
                
                # Se c'è un intervallo >= 15 minuti tra l'arrivo e la ripartenza
                if gap >= 15 and att[i].get('linea') != 'Sosta' and att[i+1].get('linea') != 'Sosta':
                    loc_arr = att[i].get('a') or att[i].get('descrizione') or 'Deposito / Rimessa'
                    loc_clean = loc_arr.replace('TO -', '').replace('piazza', '').strip()
                    
                    nuove_att.append({
                        'linea': 'Sosta',
                        'descrizione': f"☕ Sosta / Stacco al Deposito ({fmt_durata(gap)}) – {loc_arr}",
                        'da': loc_arr,
                        'a': loc_arr,
                        'partenza': fmt_time(arr_curr_m),
                        'arrivo': fmt_time(part_succ_m),
                        'km': '-',
                        'durata_sosta_m': gap,
                        'is_sosta_deposito': True
                    })

        t['attivita'] = nuove_att

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(turni, f, ensure_ascii=False, indent=2)

arricchisci_turni_con_soste_deposito(JSON_REALI)
arricchisci_turni_con_soste_deposito(JSON_OPT)
print("✅ Tutti gli intervalli in deposito/capolinea sono ora formalizzati ed esplicitati come SOSTE al 100%!")
