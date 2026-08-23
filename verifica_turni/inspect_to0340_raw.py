#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] == 'To0340':
        print(f"--- To0340 in turni_data.json ---")
        print(f"Orario: {t['inizio_servizio']} -> {t['fine_servizio']}")
        for i, a in enumerate(t['attivita']):
            print(f"  {i+1}. [{a.get('partenza')} -> {a.get('arrivo')}] {a.get('linea')} | {a.get('da')} ➔ {a.get('a')} | {a.get('descrizione')}")
