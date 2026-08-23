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

    # Identifichiamo se c'è già una sosta valida entro 360m
    has_early_sosta = False
    for a in att_opt:
        p = parse_clock(a.get('partenza'))
        t_da_in = p - in_m if p >= in_m else (1440 - in_m + p)
        # se c'è un gap prima di questa corsa
        # ...

print("Validazione rapida...")
