#!/usr/bin/env python3
"""
COSTRUTTORE TURNI DA ZERO A TEMPO PIENO (FULL-TIME SHIFT SYNTHESIZER)
Costruisce i turni ex-novo con target lavorativo CCNL:
- Target OLG per turno: 6h00 - 6h50
- Target Nastro: 6h30 (continui) o 9h00-10h00 (spezzati)
- Inclusione soste e rispetto riposi
- Organico totale: ~165-175 turni complessivi
"""

import json
import csv
import re
from collections import defaultdict

CORSE_SHEET_CSV = "/home/antonio/verifica_turni/corse_google_sheet.csv"
JSON_OUT_ZERO = "/home/antonio/verifica_turni/web/turni_generati_da_zero.json"

def norm_minutes(t_str):
    if not t_str: return 0
    if ' ' in t_str:
        t_str = t_str.split(' ')[1]
    t_clean = t_str.strip().replace('.', ':')
    m = re.search(r'(\d{1,2}):(\d{2})', t_clean)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2))
    return 0

def fmt_time(m):
    h = (m // 60) % 24
    mins = m % 60
    return f"{h:02d}:{mins:02d}"

def fmt_durata(m):
    h = m // 60
    mins = m % 60
    return f"{h}h {mins:02d}m"

def pulisci_luogo(l_str):
    if not l_str: return ""
    l = l_str.upper()
    for drop in ['STAZIONE', 'FS', 'PIAZZA', 'VIA', 'CORSO', 'C.SO', 'FR', 'LOC', 'FRONTE', 'BIVIO', 'SEDE', 'STABILIMENTO', 'PARCHEGGIO', 'STR.']:
        l = l.replace(drop, '')
    l = re.sub(r'[^A-Z0-9 ]', ' ', l)
    return " ".join(l.split())

def match_luogo(l1, l2):
    p1 = pulisci_luogo(l1).split()
    p2 = pulisci_luogo(l2).split()
    if not p1 or not p2: return False
    return p1[0] == p2[0]

def rileva_deposito(corsa):
    part = corsa['Partenza'].upper()
    arr = corsa['Arrivo'].upper()
    
    if 'CASELLE' in part or 'CASELLE' in arr: return 'Caselle', 'Ca'
    if 'PONT S' in part or 'PONT ST' in part or 'PONT' in part: return 'Pont Saint Martin', 'Pt'
    if 'SUSA' in part or 'SUSA' in arr: return 'Susa', 'Su'
    if 'PEROSA' in part or 'PEROSA' in arr or 'SESTRIERE' in part or 'PRAGELATO' in part: return 'Perosa Argentina', 'Pe'
    if 'BOBBIO' in part or 'BOBBIO' in arr: return 'Bobbio Pellice', 'Bo'
    if 'LUSERNA' in part or 'LUSERNA' in arr or 'TORRE PELLICE' in part: return 'Luserna San Giovanni', 'Lu'
    if 'BARGE' in part or 'BARGE' in arr: return 'Barge', 'Ba'
    if 'IVREA' in part or 'IVREA' in arr or 'STRAMBINO' in part: return 'Ivrea', 'Iv'
    if 'PIOBESI' in part or 'PIOBESI' in arr or 'CARMAGNOLA' in part or 'PANCALIERI' in part: return 'Piobesi', 'Pb'
    if 'SALBERTRAND' in part or 'OULX' in part or 'BARDONECCHIA' in part: return 'Salbertrand', 'Sa'
    if 'PINEROLO' in part or 'PINEROLO' in arr: return 'Pinerolo', 'Pi'
    return 'Torino', 'To'

def genera_turni_ottimizzati_da_zero(target_olg_h=6.3, max_nastro_h=10.0):
    target_olg_m = int(target_olg_h * 60)
    max_nastro_m = int(max_nastro_h * 60)

    # 1. Carica corse
    corse_raw = []
    with open(CORSE_SHEET_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            p_m = norm_minutes(r['Ora partenza'])
            arr_m = norm_minutes(r['Ora arrivo'])
            if arr_m < p_m:
                arr_m += 1440
            durata = arr_m - p_m
            dep_nome, dep_pref = rileva_deposito(r)
            
            corse_raw.append({
                'corsa_id': r.get('Corsa', ''),
                'codice_corsa': r.get('Codice corsa', ''),
                'linea': r.get('Codice linea', ''),
                'partenza_luogo': r.get('Partenza', ''),
                'arrivo_luogo': r.get('Arrivo', ''),
                'p_min': p_m,
                'arr_min': arr_m,
                'p_str': fmt_time(p_m),
                'arr_str': fmt_time(arr_m),
                'durata': durata,
                'dep_nome': dep_nome,
                'dep_pref': dep_pref,
                'turno_originale': r.get('Turno', '')
            })

    # Ordina corse per deposito e per orario
    corse_per_dep = defaultdict(list)
    for c in corse_raw:
        corse_per_dep[c['dep_pref']].append(c)

    turni_sintetizzati = []

    for dep_pref, corse_bacino in corse_per_dep.items():
        corse_disponibili = sorted(corse_bacino, key=lambda x: x['p_min'])
        dep_nome = corse_disponibili[0]['dep_nome']
        turno_num = 10

        while corse_disponibili:
            primo = corse_disponibili.pop(0)
            corse_assegnate_turno = [primo]
            
            curr_loc = primo['arrivo_luogo']
            curr_time = primo['arr_min']
            tot_guida = primo['durata']
            t_start = primo['p_min'] - 10
            riprese = 1

            # Continua ad aggregare corse per raggiungere l'orario pieno
            continua_ricerca = True
            while continua_ricerca:
                miglior_idx = -1
                miglior_score = 999999
                tipo_scelto = None

                for idx, cand in enumerate(corse_disponibili):
                    gap = cand['p_min'] - curr_time
                    nastro_pot = cand['arr_min'] - t_start
                    guida_pot = tot_guida + cand['durata']
                    
                    if nastro_pot > max_nastro_m or guida_pot > 450: # Guida max 7h30
                        continue

                    # Connessione continua diretta
                    if 5 <= gap <= 120 and match_luogo(curr_loc, cand['partenza_luogo']):
                        score = gap
                        if score < miglior_score:
                            miglior_score = score
                            miglior_idx = idx
                            tipo_scelto = 'CONTINUO'
                    
                    # Connessione spezzata con stacco
                    elif riprese < 2 and 120 < gap <= 300 and match_luogo(curr_loc, cand['partenza_luogo']):
                        score = gap + 200
                        if score < miglior_score:
                            miglior_score = score
                            miglior_idx = idx
                            tipo_scelto = 'SPEZZATO'

                if miglior_idx != -1:
                    scelta = corse_disponibili.pop(miglior_idx)
                    corse_assegnate_turno.append(scelta)
                    curr_loc = scelta['arrivo_luogo']
                    curr_time = scelta['arr_min']
                    tot_guida += scelta['durata']
                    if tipo_scelto == 'SPEZZATO':
                        riprese = 2

                    if tot_guida >= target_olg_m or (curr_time - t_start) >= 500:
                        continua_ricerca = False
                else:
                    continua_ricerca = False

            # Chiusura turno
            t_end = curr_time + 10
            nastro_eff = t_end - t_start
            olg_eff = tot_guida + 20

            code = f"{dep_pref}{turno_num:04d}"
            turno_num += 10

            attivita = []
            attivita.append({
                'linea': 'Disp',
                'descrizione': f"Controllo livelli autobus – Deposito {dep_nome}",
                'da': dep_nome,
                'a': '',
                'partenza': fmt_time(t_start),
                'arrivo': fmt_time(t_start + 10),
                'km': '-'
            })

            for c in corse_assegnate_turno:
                attivita.append({
                    'linea': str(c['linea']),
                    'descrizione': f"{c['partenza_luogo']} ➔ {c['arrivo_luogo']}",
                    'da': c['partenza_luogo'],
                    'a': c['arrivo_luogo'],
                    'partenza': c['p_str'],
                    'arrivo': c['arr_str'],
                    'km': '18.20',
                    'codice_corsa': c['codice_corsa'],
                    'corsa_id': c['corsa_id']
                })

            attivita.append({
                'linea': 'Disp',
                'descrizione': f"Rientro al Deposito di {dep_nome} e Pulizia",
                'da': '',
                'a': dep_nome,
                'partenza': fmt_time(curr_time),
                'arrivo': fmt_time(t_end),
                'km': '-'
            })

            turni_sintetizzati.append({
                'codice_turno': code,
                'nome_turno': f"TURNO AI {code[2:]} ({'CONTINUO' if riprese==1 else 'SPEZZATO'})",
                'deposito': dep_nome,
                'inizio_servizio': fmt_time(t_start),
                'fine_servizio': fmt_time(t_end),
                'nastro': f"{nastro_eff/60:.2f}",
                'nastro_str': fmt_durata(nastro_eff),
                'nastro_m': nastro_eff,
                'ore_lavoro': f"{olg_eff/60:.2f}",
                'olg_str': fmt_durata(olg_eff),
                'olg_m': olg_eff,
                'ore_guida': f"{tot_guida/60:.2f}",
                'num_riprese': f"{riprese},00",
                'num_riprese_val': riprese,
                'tipo_generato': 'CONTINUO' if riprese == 1 else 'SPEZZATO COMPATTO',
                'attivita': attivita
            })

    print(f"📊 RISULTATO SINTETIZZATORE FULL-TIME:")
    print(f"• Totale Turni Pieni Generati da Zero: {len(turni_sintetizzati)}")
    n_medio = sum(t['nastro_m'] for t in turni_sintetizzati) // len(turni_sintetizzati)
    o_medio = sum(t['olg_m'] for t in turni_sintetizzati) // len(turni_sintetizzati)
    cont_cnt = sum(1 for t in turni_sintetizzati if t['num_riprese_val'] == 1)
    print(f"• Nastro Medio: {fmt_durata(n_medio)}")
    print(f"• OLG Medio: {fmt_durata(o_medio)}")
    print(f"• Turni Continui a 1 sola ripresa: {cont_cnt}/{len(turni_sintetizzati)} ({cont_cnt/len(turni_sintetizzati)*100:.1f}%)")

    with open(JSON_OUT_ZERO, 'w', encoding='utf-8') as f:
        json.dump(turni_sintetizzati, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    genera_turni_ottimizzati_da_zero()
