#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = {t['codice_turno']: t for t in turni if t['codice_turno'].startswith('Pi')}

print("=== CHI SI TROVA A PINEROLO TRA LE 12:30 E LE 13:30? ===")
for code, t in sorted(pinerolo.items()):
    att = t.get('attivita', [])
    for a in att:
        p = a.get('partenza', '')
        arr = a.get('arrivo', '')
        da = a.get('da', '')
        if '12:30' <= p <= '13:30' or '12:30' <= arr <= '13:30' or ('PINEROLO' in da and '12:30' <= p <= '13:30'):
            print(f"• {code:6s} ({t['nome_turno'][:15]:15s}) | {p} - {arr} | {a['linea']:5s} | {da} -> {a.get('a','')}")
