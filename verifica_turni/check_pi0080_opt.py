#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] == 'Pi0080':
        print(f"Codice: {t['codice_turno']}")
        print(f"Nome: {t['nome_turno']}")
        print(f"Orario: {t['inizio_servizio']} -> {t['fine_servizio']}")
        print(f"Nastro: {t['nastro_str']} | OLG: {t['olg_str']} | Riprese: {t['num_riprese']}")
        print(f"Attività ({len(t['attivita'])} totali):")
        for i, a in enumerate(t['attivita']):
            print(f"  {i+1}. {a.get('linea')} | {a.get('partenza')} -> {a.get('arrivo')} | {a.get('descrizione')}")
