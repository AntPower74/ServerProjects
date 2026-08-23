import json
from motore_ottimo_globale_ortools import esegui_ottimizzazione_ortools, parse_m

esegui_ottimizzazione_ortools(390, 630)

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

print(f"Totale turni in file: {len(turni)}")

tot_nastro = 0
tot_olg = 0
for t in turni:
    tot_nastro += parse_m(t.get('nastro'))
    tot_olg += parse_m(t.get('ore_lavoro'))

print(f"Nastro medio calcolato da file: {tot_nastro / len(turni) / 60:.2f}h ({tot_nastro // len(turni)}m)")
print(f"OLG medio calcolato da file: {tot_olg / len(turni) / 60:.2f}h ({tot_olg // len(turni)}m)")

def verifica_soste(t):
    nastroM = parse_m(t.get('nastro'))
    if nastroM <= 360:
        return True
    inServizioM = parse_m(t.get('inizio_servizio'))
    att = t.get('attivita', [])
    pausa30 = False
    pause15 = 0
    for a in att:
        if a.get('linea') == 'Sosta' or a.get('is_sosta_deposito'):
            pM = parse_m(a.get('partenza'))
            arrM = parse_m(a.get('arrivo'))
            dur = (arrM - pM) if arrM >= pM else (1440 - pM + arrM)
            tempoDaIn = (pM - inServizioM) if pM >= inServizioM else (1440 - inServizioM + pM)
            if tempoDaIn <= 360:
                if dur >= 30: pausa30 = True
                elif dur >= 15: pause15 += 1
    ripVal = float(str(t.get('num_riprese', '1')).replace(',', '.'))
    return pausa30 or pause15 >= 2 or ripVal >= 2

conformi = 0
non_conformi = []
for t in turni:
    nM = parse_m(t.get('nastro'))
    oM = parse_m(t.get('ore_lavoro'))
    rVal = float(str(t.get('num_riprese', '1')).replace(',', '.'))
    nOk = nM <= 630
    oOk = (nM <= 240 or t.get('codice_turno', '').startswith('FT')) or (oM >= 390)
    rOk = rVal <= 2
    sOk = verifica_soste(t)
    if nOk and oOk and rOk and sOk:
        conformi += 1
    else:
        non_conformi.append((t.get('codice_turno'), f"nOk={nOk}", f"oOk={oOk}", f"rOk={rOk}", f"sOk={sOk}", f"nM={nM}", f"oM={oM}", f"rVal={rVal}"))

print(f"Conformi: {conformi} / {len(turni)} ({conformi/len(turni)*100:.1f}%)")
print(f"Non conformi ({len(non_conformi)}):")
for nc in non_conformi:
    print(" ", nc)
