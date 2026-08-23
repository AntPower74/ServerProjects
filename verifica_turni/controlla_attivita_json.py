#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

print(f"Totale turni in turni_data.json: {len(turni)}")
for t in turni[:5]:
    att = t.get('attivita', [])
    print(f"• Turno {t['codice_turno']} ({t['nome_turno']}) -> {len(att)} attività")
    if att:
        print(f"   Es: {att[0]}")
