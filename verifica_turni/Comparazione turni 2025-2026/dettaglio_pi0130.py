#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = [t for t in turni if t['codice_turno'].startswith('Pi')]
t130 = [x for x in pinerolo if x['codice_turno'] == 'Pi0130'][0]

print(f"=== DETTAGLIO CARTELLINO AZIENDA: {t130['codice_turno']} ({t130['nome_turno']}) ===")
print(f"• Inizio: {t130['inizio_servizio']} | Fine: {t130['fine_servizio']} | Nastro: {t130['nastro']} | OLG: {t130['ore_lavoro']}")
print(f"• Guida: {t130['ore_guida']} | Sosta 100%: {t130['sosta_100']} | Sosta 12%: {t130['sosta_12']} | Riprese: {t130['num_riprese']}\n")

for i, a in enumerate(t130['attivita'], 1):
    print(f"{i:2d}. [{a['linea']:5s}] {a['partenza']} -> {a['arrivo']} | {a['da']:35s} -> {a['a']:30s} | Km: {a['km']}")

print("\n--- CANDIDATI PER SCAMBIO COMPATIBILE CON Pi0130 ---")
# Cerchiamo turni con basso OLG o turni pomeridiani
# Pi0130 ha:
# Blocco 1 (06:35 - 08:05, 1h30m, 39 km): Linee 901 e 279
# Blocco 2 (13:35 - 19:05, 5h30m, 98 km): Linea 701 (13:45-15:20) + Linea 703 (16:00-18:50)

# Opzione A: Pi0130 cede a Pi0370 o Pi0280 (che fa la Linea 703) le navette 703 delle 16:00-18:50
# Oppure Pi0130 cede il mattino (06:35-08:05) e riceve altre corse pomeridiane diventando continuo (13:00 - 19:05, 6h05 nastro)
# Oppure Pi0130 scambia con Pi0190 (17:15 - 23:01, Nastro 5h46, OLG 5h46) o Pi0230 (15:00 - 23:05, OLG 6h10)
# Pi0230 fa Linea 701 Macello dalle 15:20 alle 19:40!
for t in pinerolo:
    if t['codice_turno'] in ['Pi0230', 'Pi0190', 'Pi0280', 'Pi0370', 'Pi0470']:
        print(f"• {t['codice_turno']:6s} ({t['nome_turno'][:20]:20s}) | Servizio: {t['inizio_servizio']} - {t['fine_servizio']} | Nastro: {t['nastro']} | OLG: {t['ore_lavoro']}")
