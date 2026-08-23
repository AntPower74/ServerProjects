#!/usr/bin/env python3
import json
from collections import Counter

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

depositi_cnt = Counter()
prefissi_cnt = Counter()

for t in turni:
    code = t['codice_turno']
    dep = t.get('deposito', 'Altro')
    pref = code[:2]
    depositi_cnt[dep] += 1
    prefissi_cnt[(pref, dep)] += 1

print(f"📊 Totale Turni nel Sistema: {len(turni)}")
print("\n🏢 ELENCO COMPLETO DI TUTTI I DEPOSITI NEL DATABASE:")
for (pref, dep), count in sorted(prefissi_cnt.items(), key=lambda x: -x[1]):
    print(f"  • Deposito: {dep:20s} | Prefisso: {pref:3s} | N° Turni: {count:2d}")

