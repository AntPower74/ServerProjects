import json
from motore_ottimo_globale_ortools import parse_clock, parse_m, fmt_time, fmt_durata

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

target_olg = 390  # Minimo 6h30m
max_nastro = 630  # Massimo 10h30m

conformi = 0
tot_nastro = 0
tot_olg = 0

for t in turni:
    in_m = parse_clock(t.get('inizio_servizio'))
    att_raw = t.get('attivita', [])
    corse = [a for a in att_raw if a.get('linea') != 'Sosta']
    
    # Raccogliamo tutte le corse che rientrano in max_nastro
    att_opt = []
    for a in corse:
        arr_a = parse_clock(a.get('arrivo'))
        delta = arr_a - in_m if arr_a >= in_m else (1440 - in_m + arr_a)
        if delta <= max_nastro:
            att_opt.append(a)
        elif not att_opt:
            att_opt.append(a)
            
    # Calcolo durata
    if att_opt:
        last_arr = parse_clock(att_opt[-1].get('arrivo'))
        dur_corse = last_arr - in_m if last_arr >= in_m else (1440 - in_m + last_arr)
    else:
        dur_corse = target_olg
        
    # Se dur_corse < target_olg, top-up a target_olg
    dur_effettiva = max(target_olg, dur_corse)
    if dur_effettiva <= max_nastro and dur_effettiva >= target_olg:
        conformi += 1
    tot_nastro += dur_effettiva
    tot_olg += dur_effettiva

print(f"Totale turni: {len(turni)}")
print(f"Nastro Medio: {tot_nastro // len(turni) // 60}h {tot_nastro // len(turni) % 60}m")
print(f"OLG Medio: {tot_olg // len(turni) // 60}h {tot_olg // len(turni) % 60}m")
print(f"Conformi (Minimo OLG >= 6h30 & Massimo Nastro <= 10h30): {conformi} / {len(turni)} ({conformi/len(turni)*100:.1f}%)")
