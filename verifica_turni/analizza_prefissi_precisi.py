#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

for pref in ['Pt', 'Sa', 'Pb', 'Lu', 'FT']:
    sub = [t for t in turni if t['codice_turno'].startswith(pref)]
    print(f"\n🔍 PREFISSO '{pref}' ({len(sub)} turni):")
    for t in sub[:3]:
        att0 = t['attivita'][0]['descrizione'] if t.get('attivita') else ""
        print(f"  • {t['codice_turno']} | Nome: {t['nome_turno']} | Tratta: {att0}")

