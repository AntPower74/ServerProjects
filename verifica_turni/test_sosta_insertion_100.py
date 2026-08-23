import json
from motore_ottimo_globale_ortools import parse_clock, fmt_time, fmt_durata

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

for t in turni:
    code = t['codice_turno']
    in_m = parse_clock(t.get('inizio_servizio'))
    att_raw = t.get('attivita', [])
    corse = [a for a in att_raw if a.get('linea') != 'Sosta']

    att_opt = []
    for a in corse:
        p_a = parse_clock(a.get('partenza'))
        arr_a = parse_clock(a.get('arrivo'))
        delta = arr_a - in_m if arr_a >= in_m else (1440 - in_m + arr_a)
        if delta <= 630 - 40:
            att_opt.append(a)
        elif not att_opt:
            att_opt.append(a)

    # Verifichiamo se ci sono già buchi >= 15m entro 360m
    gaps_15 = 0
    curr = in_m
    if att_opt:
        p1 = parse_clock(att_opt[0].get('partenza'))
        if p1 > curr: curr = p1
    for a in att_opt:
        p = parse_clock(a.get('partenza'))
        arr = parse_clock(a.get('arrivo'))
        g = p - curr if p >= curr else (1440 - curr + p)
        t_da_in = p - in_m if p >= in_m else (1440 - in_m + p)
        if t_da_in <= 360:
            if g >= 30: gaps_15 += 2
            elif g >= 15: gaps_15 += 1
        curr = arr

    if gaps_15 < 2 and len(att_opt) > 1:
        # Se non ci sono 2 soste da 15m, troviamo la corsa ideale dove inserire la sosta da 30m
        pass

print("Test completato.")
