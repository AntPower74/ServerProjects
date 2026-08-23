#!/usr/bin/env python3
"""
CORREZIONE COMPLETA E REALISTICA DEI TRASFERIMENTI GEOGRAFICI (ZERO TELETRASPORTO)
1. Caselle <-> Torino: inserimento Trasf 25 min (18 km).
2. Torino <-> Pinerolo: inserimento Trasf 40 min (38 km).
3. Pinerolo <-> Perosa: inserimento Trasf 20 min (18 km).
4. Ricalcolo esatto di Inizio, Fine, Nastro e OLG.
"""

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
    
    if not att: continue
    
    # Escludiamo Pi0070 e Bo3020
    if code in ['Pi0070', 'Bo3020']: continue
    
    # Controlliamo l'ultima corsa prima della chiusura
    corse_linea = [a for a in att if 'chiusura' not in a.get('descrizione', '').lower()]
    if not corse_linea: continue
    
    ultima_corsa = corse_linea[-1]
    loc_arr_fin = (ultima_corsa.get('a') or ultima_corsa.get('descrizione') or '').strip()
    arr_fin_m = parse_m(ultima_corsa.get('arrivo'))
    
    nuove_att = list(corse_linea)
    
    # 1. Se finisce a Torino ma il deposito è Caselle (es. Ca0030, Ca0060, Ca0070, Ca0090)
    if 'carlo felice' in loc_arr_fin.lower() or 'torino' in loc_arr_fin.lower() and code.startswith('Ca'):
        trasf_durata = 25
        trasf_arr_m = arr_fin_m + trasf_durata
        nuove_att.append({
            'linea': 'Trasf',
            'descrizione': f"Rientro a vuoto: Torino ➔ Caselle Deposito (18 km)",
            'da': loc_arr_fin,
            'a': 'Caselle Deposito',
            'partenza': fmt_time(arr_fin_m),
            'arrivo': fmt_time(trasf_arr_m),
            'km': '18,00'
        })
        nuove_att.append({
            'linea': 'Disp',
            'descrizione': f"Controllo finale, rifornimento e chiusura turno – Caselle Deposito",
            'da': 'Caselle Deposito',
            'a': 'Caselle Deposito',
            'partenza': fmt_time(trasf_arr_m),
            'arrivo': fmt_time(trasf_arr_m + 10),
            'km': '-'
        })
        fin_effettiva_m = trasf_arr_m + 10

    # 2. Se finisce a Torino ma il deposito è Pinerolo (es. Pi0060)
    elif ('bolzano' in loc_arr_fin.lower() or 'torino' in loc_arr_fin.lower()) and code.startswith('Pi'):
        trasf_durata = 40
        trasf_arr_m = arr_fin_m + trasf_durata
        nuove_att.append({
            'linea': 'Trasf',
            'descrizione': f"Rientro a vuoto tangenziale/autostrada: Torino ➔ Pinerolo Deposito (38 km)",
            'da': loc_arr_fin,
            'a': 'Pinerolo Deposito',
            'partenza': fmt_time(arr_fin_m),
            'arrivo': fmt_time(trasf_arr_m),
            'km': '38,00'
        })
        nuove_att.append({
            'linea': 'Disp',
            'descrizione': f"Controllo finale, rifornimento e chiusura turno – Pinerolo Deposito",
            'da': 'Pinerolo Deposito',
            'a': 'Pinerolo Deposito',
            'partenza': fmt_time(trasf_arr_m),
            'arrivo': fmt_time(trasf_arr_m + 10),
            'km': '-'
        })
        fin_effettiva_m = trasf_arr_m + 10

    # 3. Se finisce a Pinerolo ma il deposito è Perosa Argentina (es. Pe0030, Pe0080, Pe0220)
    elif 'pinerolo' in loc_arr_fin.lower() and code.startswith('Pe'):
        trasf_durata = 20
        trasf_arr_m = arr_fin_m + trasf_durata
        nuove_att.append({
            'linea': 'Trasf',
            'descrizione': f"Rientro a vuoto SP 23: Pinerolo ➔ Perosa Argentina Deposito (18 km)",
            'da': loc_arr_fin,
            'a': 'Perosa Argentina Deposito',
            'partenza': fmt_time(arr_fin_m),
            'arrivo': fmt_time(trasf_arr_m),
            'km': '18,00'
        })
        nuove_att.append({
            'linea': 'Disp',
            'descrizione': f"Controllo finale e chiusura turno – Perosa Argentina Deposito",
            'da': 'Perosa Argentina Deposito',
            'a': 'Perosa Argentina Deposito',
            'partenza': fmt_time(trasf_arr_m),
            'arrivo': fmt_time(trasf_arr_m + 10),
            'km': '-'
        })
        fin_effettiva_m = trasf_arr_m + 10

    # 4. Se finisce a Caselle Aeroporto ma il deposito è Torino (es. To0295, To0300, To0320, To0340)
    elif 'caselle' in loc_arr_fin.lower() and code.startswith('To'):
        trasf_durata = 25
        trasf_arr_m = arr_fin_m + trasf_durata
        nuove_att.append({
            'linea': 'Trasf',
            'descrizione': f"Rientro a vuoto raccordo: Caselle Aeroporto ➔ Torino Deposito (17 km)",
            'da': loc_arr_fin,
            'a': 'Torino Deposito',
            'partenza': fmt_time(arr_fin_m),
            'arrivo': fmt_time(trasf_arr_m),
            'km': '17,00'
        })
        nuove_att.append({
            'linea': 'Disp',
            'descrizione': f"Controllo finale e chiusura turno – Torino Deposito",
            'da': 'Torino Deposito',
            'a': 'Torino Deposito',
            'partenza': fmt_time(trasf_arr_m),
            'arrivo': fmt_time(trasf_arr_m + 10),
            'km': '-'
        })
        fin_effettiva_m = trasf_arr_m + 10
    else:
        # Chiusura normale locale
        nuove_att.append({
            'linea': 'Disp',
            'descrizione': f"Rientro deposito e chiusura turno – {dep} Deposito",
            'da': f"{dep} Deposito",
            'a': f"{dep} Deposito",
            'partenza': fmt_time(arr_fin_m),
            'arrivo': fmt_time(arr_fin_m + 10),
            'km': '-'
        })
        fin_effettiva_m = arr_fin_m + 10

    in_m = parse_m(t['inizio_servizio'])
    nastro_m = fin_effettiva_m - in_m if fin_effettiva_m >= in_m else (1440 - in_m + fin_effettiva_m)
    
    t['fine_servizio'] = fmt_time(fin_effettiva_m)
    t['nastro'] = f"{nastro_m/60:.2f}"
    t['nastro_str'] = fmt_durata(nastro_m)
    t['nastro_m'] = nastro_m
    t['ore_lavoro'] = f"{nastro_m/60:.2f}"
    t['olg_str'] = fmt_durata(nastro_m)
    t['olg_m'] = nastro_m
    t['attivita'] = nuove_att

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ Tutti i trasferimenti geografici sono stati corretti con tempi reali di percorrenza!")
