import json
from test_exact_js_simulation import parse_clock

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

for t in turni[:15]:
    code = t['codice_turno']
    dep = t.get('deposito', '')
    nastro_m = t.get('nastro_m', 0)
    olg_m = t.get('olg_m', 0)
    ore_guida = float(t.get('ore_guida', 0) or 0) * 60
    
    print(f"--- {code} (Dep: {dep}) | Nastro: {nastro_m}m | OLG: {olg_m}m | Guida: {ore_guida:.0f}m ---")
    for a in t.get('attivita', []):
        p = parse_clock(a.get('partenza'))
        arr = parse_clock(a.get('arrivo'))
        dur = arr - p if arr >= p else (1440 - p + arr)
        linea = a.get('linea')
        desc = a.get('descrizione', '')
        if linea in ['Sosta', 'Trasf', 'Disp'] or a.get('is_sosta_deposito'):
            print(f"    [{a.get('partenza')}->{a.get('arrivo')}] ({dur}m) {linea}: {desc}")
