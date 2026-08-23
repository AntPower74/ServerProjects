#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] == 'Pi0060':
        print(f"--- Pi0060 ---")
        for i, a in enumerate(t['attivita']):
            print(f"  {i+1}. [{a.get('partenza')} -> {a.get('arrivo')}] {a.get('linea')} | {a.get('da')} ➔ {a.get('a')} | {a.get('descrizione')}")
