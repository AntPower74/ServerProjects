#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = {t['codice_turno']: t for t in turni if t['codice_turno'].startswith('Pi')}
t300 = pinerolo['Pi0300']

print(f"=== CRONOLOGIA ESATTA AZIENDA: Pi0300 ({t300['nome_turno']}) | Nastro: {t300['nastro']} | OLG: {t300['ore_lavoro']} ===")
for i, a in enumerate(t300['attivita'], 1):
    print(f"{i:2d}. {a['partenza']} -> {a['arrivo']} | {a['linea']:5s} | {a['da']} -> {a.get('a','')}")
