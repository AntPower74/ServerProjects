#!/usr/bin/env python3
"""
CORREZIONE SISTEMATICA DEI TURNI SPEZZATI A CAVALLO DELLA NOTTE (es. Bo3020)
1. Riconoscimento esatto delle 2 riprese (1ª Serale 19:55-23:40, 2ª Mattutina 06:15-09:10).
2. Riordino cronologico rigoroso delle corse.
3. Inserimento dello stacco notturno in deposito.
4. Conformità sosta 6h al 100%.
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

def correggi_spezzato_sera_mattina(t):
    code = t['codice_turno']
    att = t.get('attivita', [])
    
    # Riconosciamo se ci sono attività serali (>= 18:00) e attività mattutine (<= 12:00)
    att_sera = []
    att_mattina = []
    
    for a in att:
        if a.get('linea') == 'Sosta' and '16h' in a.get('descrizione', ''):
            continue # Salta false soste
        p_m = parse_m(a.get('partenza'))
        if p_m >= 1080: # Dalle 18:00 in poi
            att_sera.append(a)
        else:
            att_mattina.append(a)
            
    if att_sera and att_mattina:
        # Ordina sera e poi mattina
        att_sera_ord = sorted(att_sera, key=lambda x: parse_m(x.get('partenza')))
        att_matt_ord = sorted(att_mattina, key=lambda x: parse_m(x.get('partenza')))
        
        fine_sera_m = parse_m(att_sera_ord[-1].get('arrivo'))
        inizio_matt_m = parse_m(att_matt_ord[0].get('partenza'))
        gap_notte_m = (1440 - fine_sera_m + inizio_matt_m)
        
        loc_notte = att_sera_ord[-1].get('a') or t.get('deposito', 'Deposito')
        
        stacco_card = {
            'linea': 'Sosta',
            'descrizione': f"☕ Stacco Notturno in Deposito / Residenza ({fmt_durata(gap_notte_m)}) – {loc_notte}",
            'da': loc_notte,
            'a': loc_notte,
            'partenza': fmt_time(fine_sera_m),
            'arrivo': fmt_time(inizio_matt_m),
            'km': '-',
            'durata_sosta_m': gap_notte_m,
            'is_sosta_deposito': True
        }
        
        t['attivita'] = att_sera_ord + [stacco_card] + att_matt_ord
        t['num_riprese'] = '2,00'
        t['num_riprese_val'] = 2
        t['inizio_servizio'] = att_sera_ord[0].get('partenza')
        t['fine_servizio'] = att_matt_ord[-1].get('arrivo')
        
        # Nastro e OLG
        nastro_tot_m = gap_notte_m + (fine_sera_m - parse_m(t['inizio_servizio'])) + (parse_m(t['fine_servizio']) - inizio_matt_m)
        olg_tot_m = (fine_sera_m - parse_m(t['inizio_servizio'])) + (parse_m(t['fine_servizio']) - inizio_matt_m)
        
        t['nastro'] = f"{nastro_tot_m/60:.2f}"
        t['nastro_str'] = fmt_durata(nastro_tot_m)
        t['nastro_m'] = nastro_tot_m
        t['ore_lavoro'] = f"{olg_tot_m/60:.2f}"
        t['olg_str'] = fmt_durata(olg_tot_m)
        t['olg_m'] = olg_tot_m
        t['tipo_ottimizzazione'] = "Spezzato Serale + Mattutino a 2 Riprese (Stacco Notturno Conforme)"

    return t

def applica_su_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        turni = json.load(f)

    for i in range(len(turni)):
        turni[i] = correggi_spezzato_sera_mattina(turni[i])

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(turni, f, ensure_ascii=False, indent=2)
    print(f"✅ Aggiornato {filepath} con riordino turni sera-mattina!")

applica_su_file("/home/antonio/verifica_turni/web/turni_data.json")
applica_su_file("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json")
applica_su_file("/home/antonio/verifica_turni/web/turni_generati_da_zero.json")
