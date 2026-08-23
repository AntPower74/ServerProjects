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

print("================================================================================")
print("🔬 VERIFICA STRESS-TEST GEOGRAFICO FINALE SUI 175 TURNI")
print("================================================================================\n")

errori_trovati = []

def estrai_citta(loc):
    loc_l = loc.lower()
    if 'pinerolo' in loc_l: return 'PINEROLO'
    if 'torino' in loc_l or 'carlo felice' in loc_l or 'bolzano' in loc_l or 'porta susa' in loc_l or 'porta nuova' in loc_l or 'mirafiori' in loc_l:
        return 'TORINO'
    if 'caselle' in loc_l or 'aeroporto' in loc_l: return 'CASELLE'
    if 'susa' in loc_l: return 'SUSA'
    if 'salbertrand' in loc_l or 'bardonecchia' in loc_l or 'ouls' in loc_l or 'cesana' in loc_l: return 'ALTA_VALLE_SUSA'
    if 'perosa' in loc_l or 'pomaretto' in loc_l or 'fenestrelle' in loc_l: return 'PEROSA'
    if 'pont' in loc_l or 'saint martin' in loc_l: return 'PONT_ST_MARTIN'
    if 'aosta' in loc_l: return 'AOSTA'
    if 'ivrea' in loc_l: return 'IVREA'
    if 'piobesi' in loc_l or 'carignano' in loc_l or 'castagnole' in loc_l: return 'PIOBESI'
    if 'luserna' in loc_l or 'torre pellice' in loc_l or 'bobbio' in loc_l: return 'VAL_PELLICE'
    if 'barge' in loc_l or 'cavour' in loc_l or 'saluzzo' in loc_l: return 'AREA_SALUZZO_BARGE'
    return loc.strip()

for t in turni:
    code = t['codice_turno']
    att = t.get('attivita', [])
    if code in ['Pi0070', 'Bo3020']: continue
    
    for i in range(len(att) - 1):
        a1 = att[i]
        a2 = att[i+1]
        arr1_m = parse_m(a1.get('arrivo'))
        part2_m = parse_m(a2.get('partenza'))
        loc_arr1 = a1.get('a') or a1.get('descrizione') or ''
        loc_part2 = a2.get('da') or a2.get('descrizione') or ''
        
        citta1 = estrai_citta(loc_arr1)
        citta2 = estrai_citta(loc_part2)
        gap = part2_m - arr1_m if part2_m >= arr1_m else (1440 - arr1_m + part2_m)
        
        if citta1 != citta2 and citta1 != '' and citta2 != '':
            coppia = {citta1, citta2}
            if coppia == {'TORINO', 'PINEROLO'} and gap < 25:
                err = f"[TELETRASPORTO TO-PINEROLO] {code}: Attività {i+1} finisce a {loc_arr1} ({citta1}) alle {a1.get('arrivo')} e Attività {i+2} parte da {loc_part2} ({citta2}) alle {a2.get('partenza')} con solo {gap} min!"
                errori_trovati.append((code, err))
                print(f"❌ {err}")
            if coppia == {'TORINO', 'CASELLE'} and gap < 15 and a2.get('linea') != '268':
                err = f"[TELETRASPORTO TO-CASELLE] {code}: Attività {i+1} a {loc_arr1} alle {a1.get('arrivo')} -> Attività {i+2} a {loc_part2} alle {a2.get('partenza')} (gap {gap} min)!"
                errori_trovati.append((code, err))
                print(f"❌ {err}")
            if coppia == {'PINEROLO', 'PEROSA'} and gap < 15 and a2.get('linea') != '275':
                err = f"[TELETRASPORTO PINEROLO-PEROSA] {code}: Attività {i+1} a {loc_arr1} alle {a1.get('arrivo')} -> Attività {i+2} a {loc_part2} alle {a2.get('partenza')} (gap {gap} min)!"
                errori_trovati.append((code, err))
                print(f"❌ {err}")

print(f"Totale anomalie geografiche trovate: {len(errori_trovati)}")
