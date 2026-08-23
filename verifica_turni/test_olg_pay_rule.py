import json
from test_exact_js_simulation import parse_clock

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

def calcola_olg_retribuito(t):
    dep_turno = (t.get('deposito') or '').lower()
    in_m = parse_clock(t.get('inizio_servizio'))
    fin_m = parse_clock(t.get('fine_servizio'))
    
    # Calcolo attività per attività
    minuti_retribuiti = 0
    
    for a in t.get('attivita', []):
        p = parse_clock(a.get('partenza'))
        arr = parse_clock(a.get('arrivo'))
        dur = arr - p if arr >= p else (1440 - p + arr)
        
        linea = a.get('linea')
        is_sosta = (linea == 'Sosta') or a.get('is_sosta_deposito')
        
        if not is_sosta:
            # Guida, Trasferimento, Disposizione: 100% retribuiti
            minuti_retribuiti += dur
        else:
            # Regola utente:
            # Soste fino a 30 min: 100%
            # Oltre 30 min:
            #   - in deposito di residenza: 0%
            #   - fuori residenza: 12%
            desc = (a.get('descrizione') or '') + ' ' + (a.get('da') or '') + ' ' + (a.get('a') or '')
            desc_low = desc.lower()
            
            # Verifica se è nel deposito di residenza
            is_in_residenza = False
            if dep_turno and dep_turno in desc_low:
                is_in_residenza = True
            elif 'residenza' in desc_low or (t.get('codice_turno', '')[:2].lower() == 'to' and 'torino' in desc_low):
                is_in_residenza = True
                
            if dur <= 30:
                minuti_retribuiti += dur
            else:
                # Primi 30 min al 100%
                minuti_retribuiti += 30
                eccedenza = dur - 30
                if is_in_residenza:
                    minuti_retribuiti += 0 # 0% in residenza
                else:
                    minuti_retribuiti += eccedenza * 0.12 # 12% fuori residenza
                    
    return round(minuti_retribuiti)

for t in turni[:15]:
    code = t['codice_turno']
    n_m = t.get('nastro_m', 0)
    olg_orig = t.get('olg_m', 0)
    olg_calc = calcola_olg_retribuito(t)
    print(f"Turno {code:7s} | Nastro: {n_m:3d}m | OLG Orig: {olg_orig:3d}m | OLG Calc: {olg_calc:3d}m | Diff: {olg_calc - olg_orig:2d}m")
