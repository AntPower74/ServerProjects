#!/usr/bin/env python3
"""
CORREZIONE MATEMATICA: OLG <= NASTRO PER TUTTI I TURNI
In un turno continuo (1 sola ripresa), OLG = Nastro.
In un turno spezzato, OLG = Nastro - Stacco passivo non retribuito.
In nessun caso OLG può essere maggiore del Nastro.
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

def fmt_durata(m):
    if not m or m < 0: return "0h 00m"
    h = m // 60
    mins = m % 60
    return f"{h}h {mins:02d}m"

def correggi_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        turni = json.load(f)

    corretti = 0
    for t in turni:
        n_m = t.get('nastro_m', parse_m(t.get('nastro')))
        o_m = t.get('olg_m', parse_m(t.get('ore_lavoro')))
        rip = float(str(t.get('num_riprese', '1')).replace(',', '.'))
        
        # Se OLG > Nastro, correggiamo immediatamente
        if o_m > n_m or (rip == 1.0 and o_m != n_m):
            # In turno continuo OLG = Nastro
            if rip == 1.0:
                o_m = n_m
            else:
                o_m = min(n_m, o_m)
            
            t['olg_m'] = o_m
            t['olg_str'] = fmt_durata(o_m)
            t['ore_lavoro'] = f"{o_m/60:.2f}"
            corretti += 1

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(turni, f, ensure_ascii=False, indent=2)

    print(f"✅ File {filepath}: corretti {corretti} turni con coerenza matematica OLG <= Nastro!")

correggi_file("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json")
correggi_file("/home/antonio/verifica_turni/web/turni_data.json")
correggi_file("/home/antonio/verifica_turni/web/turni_generati_da_zero.json")
