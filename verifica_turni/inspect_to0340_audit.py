#!/usr/bin/env python3
import json

def parse_m(t_str):
    p = str(t_str).replace('.', ':').split(':')
    return int(p[0]) * 60 + int(p[1])

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] == 'To0340':
        in_m = parse_m(t['inizio_servizio'])
        print(f"Inizio servizio: {t['inizio_servizio']} ({in_m}m)")
        for i, a in enumerate(t['attivita']):
            p_s = parse_m(a['partenza'])
            arr_s = parse_m(a['arrivo'])
            durata = arr_s - p_s if arr_s >= p_s else (1440 - p_s + arr_s)
            tempo_da_in = p_s - in_m if p_s >= in_m else (1440 - in_m + p_s)
            print(f"  {i+1}. {a['linea']} [{a['partenza']} -> {a['arrivo']}] (durata={durata}m, da_inizio={tempo_da_in}m) | {a['descrizione']}")
