import json
from test_exact_js_simulation import parse_clock

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    nM = t.get('nastro_m') or 0
    rVal = float(str(t.get('num_riprese', '1')).replace(',', '.'))
    
    nOk = nM <= 630
    rOk = rVal <= 2
    
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
        if pausa30 or pause15 >= 2 or rVal >= 2:
            sOk = True

    if not (nOk and rOk and sOk):
        print(f"Turno non conforme trovato: {t['codice_turno']} | nM={nM} | nOk={nOk}, rOk={rOk}, sOk={sOk} | in={t.get('inizio_servizio')} -> fine={t.get('fine_servizio')}")
        for a in t.get('attivita', []):
            if a.get('linea') == 'Sosta':
                print(f"   Sosta: {a.get('partenza')} -> {a.get('arrivo')} ({a.get('descrizione')})")
