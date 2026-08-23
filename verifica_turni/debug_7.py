import json
from test_exact_js_simulation import parse_clock

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

for t in turni:
    code = t['codice_turno']
    in_m = parse_clock(t.get('inizio_servizio'))
    att_raw = t.get('attivita', [])
    corse = [a for a in att_raw if a.get('linea') != 'Sosta']
    
    # cerchiamo la prima corsa che termina <= 300
    has_run_under_300 = any((parse_clock(a.get('arrivo')) - in_m if parse_clock(a.get('arrivo')) >= in_m else (1440 - in_m + parse_clock(a.get('arrivo')))) <= 330 for a in corse)
    if not has_run_under_300 and len(corse) > 0:
        first_arr = parse_clock(corse[0].get('arrivo'))
        delta = first_arr - in_m if first_arr >= in_m else (1440 - in_m + first_arr)
        print(f"Turno senza corse <= 330m: {code} (Prima corsa termina dopo {delta}m = {delta//60}h {delta%60}m)")
