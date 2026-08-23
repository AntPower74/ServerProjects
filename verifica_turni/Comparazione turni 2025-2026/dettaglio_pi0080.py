#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

t = [x for x in turni if x['codice_turno'] == 'Pi0080'][0]
print(f"=== DETTAGLIO CARTELLINO AZIENDA: {t['codice_turno']} ({t['nome_turno']}) ===")
print(f"• Inizio: {t['inizio_servizio']} | Fine: {t['fine_servizio']} | Nastro: {t['nastro']} | OLG: {t['ore_lavoro']}")
print(f"• Guida: {t['ore_guida']} | Sosta 100%: {t['sosta_100']} | Sosta 12%: {t['sosta_12']} | Riprese: {t['num_riprese']}\n")

for i, a in enumerate(t['attivita'], 1):
    print(f"{i:2d}. [{a['linea']:5s}] {a['partenza']} -> {a['arrivo']} | {a['da']:35s} -> {a['a']:30s} | Km: {a['km']}")
