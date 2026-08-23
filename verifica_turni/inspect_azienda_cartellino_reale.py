#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] in ['Ca0030', 'Pi0060', 'Pe0030', 'To0340']:
        print(f"==================================================")
        print(f"🏢 CARTELLINO ORIGINALE AZIENDA: {t['codice_turno']} ({t.get('nome_turno')})")
        print(f"Orario: {t['inizio_servizio']} -> {t['fine_servizio']} | Nastro: {t['nastro']} | OLG: {t['ore_lavoro']}")
        for i, a in enumerate(t['attivita']):
            print(f"  {i+1}. [{a.get('partenza')} -> {a.get('arrivo')}] {a.get('linea')} | {a.get('da')} ➔ {a.get('a')} | {a.get('descrizione')}")
