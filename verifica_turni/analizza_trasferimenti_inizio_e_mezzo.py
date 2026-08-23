#!/usr/bin/env python3
"""
ANALISI TRASFERIMENTI A VUOTO SU TUTTE LE 3 FASI DEL TURNO:
1. INIZIO TURNO: Uscita dal Deposito -> Partenza Prima Corsa Commerciale.
2. A METÀ TURNO: Tra l'arrivo di una corsa e la partenza della successiva.
3. FINE TURNO: Dalla fine dell'ultima corsa al rientro in Deposito.
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

def estrai_citta(loc):
    loc_l = str(loc).lower()
    if 'pinerolo' in loc_l: return 'PINEROLO'
    if 'torino' in loc_l or 'carlo felice' in loc_l or 'bolzano' in loc_l or 'porta susa' in loc_l or 'porta nuova' in loc_l or 'mirafiori' in loc_l:
        return 'TORINO'
    if 'caselle' in loc_l or 'aeroporto' in loc_l: return 'CASELLE'
    if 'susa' in loc_l: return 'SUSA'
    if 'salbertrand' in loc_l or 'bardonecchia' in loc_l or 'ouls' in loc_l or 'cesana' in loc_l: return 'ALTA_VALLE_SUSA'
    if 'perosa' in loc_l or 'pomaretto' in loc_l or 'fenestrelle' in loc_l: return 'PEROSA'
    if 'pont' in loc_l or 'saint martin' in loc_l: return 'PONT_ST_MARTIN'
    if 'aosta' in loc_l: return 'AOSTA'
    if 'ivrea' in loc_l: return 'IVREA'
    if 'piobesi' in loc_l or 'carignano' in loc_l or 'castagnole' in loc_l: return 'PIOBESI'
    if 'luserna' in loc_l or 'torre pellice' in loc_l or 'bobbio' in loc_l: return 'VAL_PELLICE'
    if 'barge' in loc_l or 'cavour' in loc_l or 'saluzzo' in loc_l: return 'AREA_SALUZZO_BARGE'
    return loc_l.strip()

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

problemi_inizio = []
problemi_mezzo = []
problemi_fine = []

for t in turni:
    code = t['codice_turno']
    dep = t.get('deposito', '')
    citta_dep = estrai_citta(dep)
    att = t.get('attivita', [])
    if code in ['Pi0070', 'Bo3020']: continue
    
    corse_linea = [a for a in att if a.get('linea') not in ['Disp', 'Sosta']]
    if not corse_linea: continue
    
    # 1. VERIFICA INIZIO TURNO
    prima_corsa = corse_linea[0]
    loc_part_1 = prima_corsa.get('da') or prima_corsa.get('descrizione') or ''
    citta_part_1 = estrai_citta(loc_part_1)
    
    # Verifichiamo se prima della prima corsa c'è il Trasf necessario
    if citta_part_1 != citta_dep and citta_part_1 != '':
        has_trasf_in = any(a.get('linea') == 'Trasf' and parse_m(a.get('partenza')) <= parse_m(prima_corsa.get('partenza')) for a in att)
        if not has_trasf_in:
            problemi_inizio.append((code, f"Parte da {loc_part_1} ({citta_part_1}) ma il deposito è {dep} ({citta_dep}) senza trasferimento"))

    # 2. VERIFICA A METÀ TURNO (TRA CORSE CONSECUTIVE)
    for i in range(len(corse_linea) - 1):
        c1 = corse_linea[i]
        c2 = corse_linea[i+1]
        loc_arr = c1.get('a') or c1.get('descrizione') or ''
        loc_part = c2.get('da') or c2.get('descrizione') or ''
        cit_arr = estrai_citta(loc_arr)
        cit_part = estrai_citta(loc_part)
        gap = parse_m(c2.get('partenza')) - parse_m(c1.get('arrivo'))
        if gap < 0: gap += 1440
        
        if cit_arr != cit_part and cit_arr != '' and cit_part != '':
            coppia = {cit_arr, cit_part}
            if coppia == {'TORINO', 'PINEROLO'} and gap < 25:
                problemi_mezzo.append((code, f"Corsa finisce a {loc_arr} ({cit_arr}) e successiva parte da {loc_part} ({cit_part}) con gap {gap}m"))
            elif coppia == {'TORINO', 'CASELLE'} and gap < 15 and c2.get('linea') != '268':
                problemi_mezzo.append((code, f"Corsa finisce a {loc_arr} ({cit_arr}) e successiva parte da {loc_part} ({cit_part}) con gap {gap}m"))
            elif coppia == {'PINEROLO', 'PEROSA'} and gap < 15 and c2.get('linea') != '275':
                problemi_mezzo.append((code, f"Corsa finisce a {loc_arr} ({cit_arr}) e successiva parte da {loc_part} ({cit_part}) con gap {gap}m"))

print("================================================================================")
print("📊 REPORT ANALISI TRASFERIMENTI SULLE 3 FASI (INIZIO / METÀ / FINE):")
print("================================================================================")
print(f"• Problemi riscontrati all'INIZIO turno (Uscita Deposito -> 1ª Corsa): {len(problemi_inizio)}")
for p in problemi_inizio: print(f"   ↳ {p[0]}: {p[1]}")
print(f"• Problemi riscontrati a METÀ turno (Tra corse consecutive): {len(problemi_mezzo)}")
for p in problemi_mezzo: print(f"   ↳ {p[0]}: {p[1]}")
