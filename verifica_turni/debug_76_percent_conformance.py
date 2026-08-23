#!/usr/bin/env python3
import json

def parse_m(t_str):
    if not t_str: return 0
    t_clean = str(t_str).strip().replace('.', ':').replace(',', ':')
    p = t_clean.split(':')
    if len(p) == 1:
        try: return round(float(p[0]) * 60)
        except: return 0
    return int(p[0]) * 60 + int(p[1])

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

maxNastro = 630 # 10h30
targetOLG = 390 # 6h30
maxRipreseVal = '2'

non_conformi = []

for t in turni:
    code = t['codice_turno']
    nastroM = parse_m(t.get('nastro'))
    olgM = parse_m(t.get('ore_lavoro'))
    ripNum = float(str(t.get('num_riprese', '1')).replace(',', '.'))
    
    nastroOk = nastroM <= maxNastro
    olgOk = olgM >= targetOLG
    ripreseOk = (maxRipreseVal == 'ALL') or (ripNum <= float(maxRipreseVal))
    
    # Sosta
    att = t.get('attivita', [])
    sostaOk = False
    if nastroM <= 360:
        sostaOk = True
    else:
        inServizioM = parse_m(t.get('inizio_servizio'))
        pausa30 = False
        pause15 = 0
        for a in att:
            if a.get('linea') == 'Sosta' or a.get('is_sosta_deposito'):
                p_s = parse_m(a.get('partenza'))
                arr_s = parse_m(a.get('arrivo'))
                durata = arr_s - p_s if arr_s >= p_s else (1440 - p_s + arr_s)
                tempoDaIn = p_s - inServizioM if p_s >= inServizioM else (1440 - inServizioM + p_s)
                if tempoDaIn <= 360:
                    if durata >= 30: pausa30 = True
                    elif durata >= 15: pause15 += 1
        if pausa30 or pause15 >= 2 or ripNum >= 2:
            sostaOk = True
            
    conforme = nastroOk and olgOk and ripreseOk and sostaOk
    if not conforme:
        motivi = []
        if not nastroOk: motivi.append(f"Nastro {nastroM}m > {maxNastro}m")
        if not olgOk: motivi.append(f"OLG {olgM}m < {targetOLG}m")
        if not ripreseOk: motivi.append(f"Riprese {ripNum} > {maxRipreseVal}")
        if not sostaOk: motivi.append("Manca sosta 30m entro 6h")
        non_conformi.append((code, ", ".join(motivi)))

print(f"Totale turni: {len(turni)}")
print(f"Conformi: {len(turni) - len(non_conformi)} / {len(turni)} ({((len(turni) - len(non_conformi))/len(turni))*100:.1f}%)")
print(f"Non conformi: {len(non_conformi)}")
for nc in non_conformi[:15]:
    print(f"  • {nc[0]}: {nc[1]}")
