import json
from test_exact_js_simulation import parse_clock

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] == 'To0660':
        in_m = parse_clock(t.get('inizio_servizio'))
        max_nastro = 630
        print(f"in_m: {in_m} ({t.get('inizio_servizio')}), max_nastro: {max_nastro}")
        
        att_raw = t.get('attivita', [])
        for idx, a in enumerate(att_raw):
            p_a = parse_clock(a.get('partenza'))
            arr_a = parse_clock(a.get('arrivo'))
            delta = arr_a - in_m if arr_a >= in_m else (1440 - in_m + arr_a)
            included = delta <= max_nastro
            print(f"  {idx+1}. [{a.get('partenza')} -> {a.get('arrivo')}] {a.get('linea')} | arr_a={arr_a}, delta={delta} ({delta//60}h {delta%60}m) | included={included}")
