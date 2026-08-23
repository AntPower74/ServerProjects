#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

caselle = [t for t in turni if t['codice_turno'].startswith('Ca')]

print(f"🏢 ANALISI DETTAGLIATA DEPOSITO CASELLE ({len(caselle)} Turni):")
print("-" * 90)
print(f"{'Codice':8s} | {'Nome Turno':26s} | {'Orario':13s} | {'Nastro':8s} | {'OLG':8s} | {'Riprese':8s} | {'N° Corse'}")
print("-" * 90)

for t in caselle:
    att = t.get('attivita', [])
    print(f"{t['codice_turno']:8s} | {t['nome_turno'][:26]:26s} | {t['inizio_servizio']} - {t['fine_servizio']:5s} | {t['nastro']:8s} | {t['ore_lavoro']:8s} | {str(t.get('num_riprese','1,00')):8s} | {len(att):2d} corse")
    if att:
        print(f"   Tratte: {att[0]['partenza']} {att[0]['descrizione'][:35]} ➔ ... ➔ {att[-1]['arrivo']} {att[-1]['descrizione'][:35]}")

print("-" * 90)
