#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = {t['codice_turno']: t for t in turni if t['codice_turno'].startswith('Pi')}
t260 = pinerolo['Pi0260']

print(f"=== CRONOLOGIA ESATTA AZIENDA: Pi0260 ({t260['nome_turno']}) ===")
for i, a in enumerate(t260['attivita'], 1):
    print(f"{i:2d}. {a['partenza']} -> {a['arrivo']} | {a['linea']:5s} | {a['da']} -> {a['a']} | Km: {a['km']}")
