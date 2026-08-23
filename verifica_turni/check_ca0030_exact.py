#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] == 'Ca0030':
        print(f"==================================================")
        print(f"🏢 VERIFICA CA0030 DOPO PARSING UFFICIALE:")
        print(f"Turno: {t['codice_turno']} – {t['nome_turno']}")
        print(f"Deposito: {t['deposito']} | Orario: {t['inizio_servizio']} ➔ {t['fine_servizio']}")
        print(f"Nastro: {t['nastro_str']} | OLG: {t['olg_str']} | Km: {t['km_totali']}")
        print(f"Attività ({len(t['attivita'])} totali):")
        for i, a in enumerate(t['attivita']):
            print(f"  {i+1:2d}. [{a.get('partenza')} -> {a.get('arrivo')}] {a.get('linea'):6s} | {a.get('descrizione')} (Km: {a.get('km')})")
