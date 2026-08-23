#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

print(f"✅ Totale turni estratti da PDF: {len(turni)}")

for t in turni:
    if t['codice_turno'] in ['Ca0030', 'Ba3510', 'Pe0030', 'Pi0060', 'To0340']:
        print(f"\n==================================================")
        print(f"🏢 TURNO ESTRATTO DAL PDF: {t['codice_turno']} – {t['nome_turno']}")
        print(f"Deposito: {t['deposito']} | Orario: {t['inizio_servizio']} ➔ {t['fine_servizio']}")
        print(f"Nastro: {t['nastro_str']} | OLG: {t['olg_str']} | Riprese: {t['num_riprese']} | Km: {t['km_totali']}")
        print(f"Attività ({len(t['attivita'])} totali):")
        for i, a in enumerate(t['attivita']):
            print(f"  {i+1}. [{a.get('partenza')} -> {a.get('arrivo')}] {a.get('linea')} | {a.get('descrizione')} (Km: {a.get('km')})")
