#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

pt_turni = [t for t in turni if t['codice_turno'].startswith('Pt')]
for t in pt_turni[:5]:
    print(f"\n• Turno {t['codice_turno']}:")
    for a in t.get('attivita', [])[:4]:
        print(f"   {a.get('linea')} | {a.get('partenza')} - {a.get('arrivo')} | {a.get('descrizione')}")
