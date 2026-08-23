import json
from test_exact_js_simulation import parse_clock

def fmt_durata(m):
    if not m or m < 0: return "0h 00m"
    h = int(m) // 60
    mins = int(round(m)) % 60
    return f"{h}h {mins:02d}m"

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni[:10]:
    code = t['codice_turno']
    dep = t.get('deposito', '')
    
    tot_guida = 0
    tot_trasf = 0
    tot_disp = 0
    tot_soste_100 = 0
    tot_soste_12 = 0
    tot_soste_0 = 0
    
    for a in t.get('attivita', []):
        p = parse_clock(a.get('partenza'))
        arr = parse_clock(a.get('arrivo'))
        dur = arr - p if arr >= p else (1440 - p + arr)
        linea = a.get('linea')
        is_sosta = (linea == 'Sosta') or a.get('is_sosta_deposito')
        
        if not is_sosta:
            if linea == 'Trasf': tot_trasf += dur
            elif linea == 'Disp': tot_disp += dur
            else: tot_guida += dur
        else:
            desc = ((a.get('descrizione') or '') + ' ' + (a.get('da') or '')).lower()
            is_in_residenza = False
            if dep and dep.lower() in desc:
                is_in_residenza = True
            elif 'residenza' in desc:
                is_in_residenza = True
                
            if dur <= 30:
                tot_soste_100 += dur
            else:
                tot_soste_100 += 30
                ecc = dur - 30
                if is_in_residenza:
                    tot_soste_0 += ecc
                else:
                    tot_soste_12 += ecc * 0.12
                    
    olg_tot = tot_guida + tot_trasf + tot_disp + tot_soste_100 + tot_soste_12
    print(f"Turno {code} ({dep}) | Nastro: {t.get('nastro_str')} | OLG Retribuito: {fmt_durata(olg_tot)} | (Guida/Trasf/Disp: {tot_guida+tot_trasf+tot_disp}m, Soste retribuite: {tot_soste_100+tot_soste_12:.1f}m)")
