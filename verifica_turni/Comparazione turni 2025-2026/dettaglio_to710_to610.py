#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

torino_dict = {t['codice_turno']: t for t in turni if t['codice_turno'].startswith('To')}

for code in ['To0710', 'To0610', 'To0700', 'To0760']:
    if code in torino_dict:
        t = torino_dict[code]
        print(f"\n==================================================")
        print(f"🔹 {code} ({t['nome_turno']}) | Nastro: {t['nastro']} | OLG: {t['ore_lavoro']}")
        print(f"==================================================")
        for i, a in enumerate(t.get('attivita', []), 1):
            print(f"{i:2d}. {a['partenza']} -> {a['arrivo']} | {a['linea']:5s} | {a['da']} -> {a.get('a','')}")
