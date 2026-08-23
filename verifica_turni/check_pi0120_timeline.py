#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] == 'Pi0120':
        print(f"Codice: {t['codice_turno']} | Orario: {t['inizio_servizio']} -> {t['fine_servizio']}")
        for i, a in enumerate(t['attivita']):
            print(f"  {i+1}. [{a.get('partenza')} -> {a.get('arrivo')}] {a.get('linea')} | {a.get('descrizione')}")
