import json
from test_exact_js_simulation import parse_clock

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

min_lavoro = 390 # 6h 30m
max_nastro = 630 # 10h 30m

non_conformi = []
for t in turni:
    code = t['codice_turno']
    nM = t.get('nastro_m', 0)
    oM = t.get('olg_m', 0)
    
    nOk = nM <= max_nastro
    minOk = (nM <= 240 or code.startswith('FT')) or (oM >= min_lavoro)
    
    # Sosta
    sOk = False
    if nM <= 360:
        sOk = True
    else:
        inM = parse_clock(t.get('inizio_servizio'))
        pausa30 = False
        pause15 = 0
        for a in t.get('attivita', []):
            if a.get('linea') == 'Sosta' or a.get('is_sosta_deposito'):
                pM = parse_clock(a.get('partenza'))
                arrM = parse_clock(a.get('arrivo'))
                dur = arrM - pM if arrM >= pM else (1440 - pM + arrM)
                t_in = pM - inM if pM >= inM else (1440 - inM + pM)
                if t_in <= 360:
                    if dur >= 30: pausa30 = True
                    elif dur >= 15: pause15 += 1
        if pausa30 or pause15 >= 2:
            sOk = True
            
    if not (nOk and minOk and sOk):
        non_conformi.append((code, nOk, minOk, sOk, nM, oM))
        print(f"Non conforme: {code} | nOk={nOk} (nM={nM}) | minOk={minOk} (oM={oM}) | sOk={sOk} | in={t.get('inizio_servizio')} -> fine={t.get('fine_servizio')}")

print(f"\nTotale non conformi: {len(non_conformi)}")
