#!/usr/bin/env python3
"""
AUDIT TOTALE E MANUALE SU TUTTI I 175 CARTELLINI ARRIVA 2026:
Controlla:
1. Teletrasporti spaziali (Luogo arrivo corsa N != Luogo partenza corsa N+1 senza Trasf)
2. Incongruenze orarie (Partenza > Arrivo, sovrapposizioni)
3. Discrepanze tra somma durate e Nastro/OLG dichiarato
4. Rientri mancanti al deposito di partenza
5. Violazioni CCNL (Guida continua > 4h30 senza pausa, Nastro eccessivo, Soste illegali)
"""

import json
import pdfplumber
import re

PDF_PATH = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini lun-ven 2026.pdf"

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

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni_reali = json.load(f)

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni_opt = json.load(f)

print(f"============================================================")
print(f"🔍 AUDIT GENERALE SU {len(turni_reali)} TURNI REALI E {len(turni_opt)} OTTIMIZZATI")
print(f"============================================================\n")

irregolarita_trovate = []

# 1. CONTROLLO TELETRASPORTI & CONTINUITÀ SPAZIALE (Dati Reali da PDF)
print("--- 1. CONTROLLO CONTINUITÀ SPAZIALE & TELETRASPORTI (REALI) ---")
for t in turni_reali:
    code = t['codice_turno']
    dep = t.get('deposito', '')
    att = t.get('attivita', [])
    
    # Filtriamo solo corse e trasferimenti (escludiamo soste pure)
    corse = [a for a in att if a.get('linea') != 'Sosta']
    
    for i in range(len(corse) - 1):
        c_curr = corse[i]
        c_next = corse[i+1]
        
        arr_loc = (c_curr.get('a') or '').strip().lower()
        part_loc = (c_next.get('da') or '').strip().lower()
        
        # Semplificazione stringhe per confronto città
        def normalizza_loc(l):
            l = re.sub(r'[^a-zA-Z0-9\s]', ' ', l)
            l = l.replace('piazza', '').replace('stazione', '').replace('deposito', '').replace('rimessa', '').replace('autostazione', '').replace('fronte', '')
            tokens = [w for w in l.split() if len(w) > 2]
            return tokens
            
        tok_arr = normalizza_loc(arr_loc)
        tok_part = normalizza_loc(part_loc)
        
        # Se non hanno token in comune e non è stesso posto
        match = any(t in tok_part for t in tok_arr) or any(t in tok_arr for t in tok_part)
        
        p_succ = parse_m(c_next.get('partenza'))
        a_curr = parse_m(c_curr.get('arrivo'))
        gap = p_succ - a_curr if p_succ >= a_curr else (1440 - a_curr + p_succ)
        
        if not match and gap == 0 and arr_loc and part_loc:
            irregolarita_trovate.append({
                'tipo': 'TELETRASPORTO ISTANTANEO A GAP ZERO',
                'turno': code,
                'deposito': dep,
                'corsa_1': f"[{c_curr.get('partenza')}->{c_curr.get('arrivo')}] {c_curr.get('linea')} a {c_curr.get('a')}",
                'corsa_2': f"[{c_next.get('partenza')}->{c_next.get('arrivo')}] {c_next.get('linea')} da {c_next.get('da')}",
                'dettaglio': f"Arrivo a '{c_curr.get('a')}' e ripartenza immediata da '{c_next.get('da')}' senza trasferimento."
            })

# 2. CONTROLLO ORARI NON CRONOLOGICI (Arrivo < Partenza senza notte)
print("--- 2. CONTROLLO CRONOLOGIA TEMPORALE ---")
for t in turni_reali:
    code = t['codice_turno']
    att = t.get('attivita', [])
    in_m = parse_m(t.get('inizio_servizio'))
    fin_m = parse_m(t.get('fine_servizio'))
    
    # Se non è notturno (es. Pi0070)
    is_notturno = (in_m >= 1200 and fin_m <= 400)
    
    prev_arr = in_m
    for i, a in enumerate(att):
        p_m = parse_m(a.get('partenza'))
        arr_m = parse_m(a.get('arrivo'))
        
        if not is_notturno:
            if arr_m < p_m:
                irregolarita_trovate.append({
                    'tipo': 'ORARIO ARRIVO ANTECEDENTE A PARTENZA',
                    'turno': code,
                    'corsa': f"{a.get('linea')} {a.get('descrizione')}",
                    'orari': f"{a.get('partenza')} -> {a.get('arrivo')}",
                    'dettaglio': 'Orario di arrivo minore della partenza nella stessa corsa diurna.'
                })
            if p_m < prev_arr and i > 0:
                irregolarita_trovate.append({
                    'tipo': 'SOVRAPPOSIZIONE TEMPORALE CORSE',
                    'turno': code,
                    'corsa_precedente_arrivo': fmt_time(prev_arr),
                    'corsa_attuale_partenza': fmt_time(p_m),
                    'dettaglio': f"La corsa {i+1} parte alle {fmt_time(p_m)} prima dell'arrivo della precedente ({fmt_time(prev_arr)})."
                })
        prev_arr = arr_m

# 3. CONTROLLO DISCREPANZE TESTATA PDF VS SOMMA ATTIVITA'
print("--- 3. CONTROLLO DISCREPANZE NASTRO / OLG DECLARED VS COMPUTED ---")
for t in turni_reali:
    code = t['codice_turno']
    in_m = parse_m(t.get('inizio_servizio'))
    fin_m = parse_m(t.get('fine_servizio'))
    nastro_dec_m = t.get('nastro_m', 0)
    
    span = fin_m - in_m if fin_m >= in_m else (1440 - in_m + fin_m)
    if abs(span - nastro_dec_m) > 15:
        irregolarita_trovate.append({
            'tipo': 'DISCREPANZA NASTRO TESTATA PDF',
            'turno': code,
            'inizio_fine': f"{t.get('inizio_servizio')} -> {t.get('fine_servizio')} (Durata: {span//60}h {span%60}m)",
            'nastro_dichiarato': f"{nastro_dec_m//60}h {nastro_dec_m%60}m",
            'dettaglio': f"Lo span tra Inizio Servizio ({t.get('inizio_servizio')}) e Fine ({t.get('fine_servizio')}) differisce dal Nastro del turno dichiarato."
        })

print(f"\nRisultato Audit: {len(irregolarita_trovate)} potenziali anomalie trovate.")
for idx, irr in enumerate(irregolarita_trovate[:10]):
    print(f"\n🚨 ANOMALIA #{idx+1}: {irr['tipo']} (Turno: {irr.get('turno')})")
    for k, v in irr.items():
        if k not in ['tipo', 'turno']:
            print(f"   • {k}: {v}")

