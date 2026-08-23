import json
from test_exact_js_simulation import parse_clock

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

for t in turni[:15]:
    code = t['codice_turno']
    dep = t.get('deposito', '')
    nastro_m = t.get('nastro_m', 0)
    olg_orig = t.get('olg_m', 0)
    
    tot_retrib = 0
    for a in t.get('attivita', []):
        p = parse_clock(a.get('partenza'))
        arr = parse_clock(a.get('arrivo'))
        dur = arr - p if arr >= p else (1440 - p + arr)
        linea = a.get('linea')
        is_sosta = (linea == 'Sosta') or a.get('is_sosta_deposito')
        
        if not is_sosta:
            tot_retrib += dur
        else:
            desc = ((a.get('descrizione') or '') + ' ' + (a.get('da') or '')).lower()
            is_in_residenza = False
            if dep and dep.lower() in desc:
                is_in_residenza = True
            elif 'residenza' in desc:
                is_in_residenza = True
                
            if dur <= 30:
                tot_retrib += dur
            else:
                if is_in_residenza:
                    tot_retrib += 0
                else:
                    tot_retrib += dur * 0.12
                    
    diff = round(tot_retrib) - olg_orig
    print(f"Turno {code:7s} ({dep:14s}) | Nastro: {nastro_m:3d}m | OLG Orig: {olg_orig:3d}m | OLG 12% Whole: {round(tot_retrib):3d}m | Diff: {diff:2d}m")
