import json

def parse_clock(t_str):
    if not t_str: return 0
    clean = str(t_str).strip().replace('.', ':')
    p = clean.split(':')
    if len(p) == 2:
        return int(p[0]) * 60 + int(p[1])
    return 0

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

tot_nastro = 0
tot_olg = 0
conformi = 0

for t in turni:
    nM = t.get('nastro_m') or 0
    oM = t.get('olg_m') or 0
    tot_nastro += nM
    tot_olg += oM
    
    nOk = nM <= 630
    rVal = float(str(t.get('num_riprese', '1')).replace(',', '.'))
    rOk = rVal <= 2
    
    # Sosta entro 6h
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
            
    if nOk and rOk and sOk:
        conformi += 1

print(f"Totale: {len(turni)}")
print(f"Nastro Medio: {tot_nastro // len(turni) // 60}h {tot_nastro // len(turni) % 60}m")
print(f"OLG Medio: {tot_olg // len(turni) // 60}h {tot_olg // len(turni) % 60}m")
print(f"Conformi (Nastro <= 10h30 & Soste CCNL): {conformi} / {len(turni)} ({conformi/len(turni)*100:.1f}%)")
