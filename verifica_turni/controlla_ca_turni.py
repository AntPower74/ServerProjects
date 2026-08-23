#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

ca_turni = [t for t in turni if t['codice_turno'].startswith('Ca')]
print(f"Totale turni con prefisso 'Ca': {len(ca_turni)}")
for t in ca_turni:
    print(f"• {t['codice_turno']} -> {t['nome_turno']}")
    if t.get('attivita'):
        print(f"   Tratta 1: {t['attivita'][0].get('descrizione')}")
