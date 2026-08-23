#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = {t['codice_turno']: t for t in turni if t['codice_turno'].startswith('Pi')}

print("=== TRACCIAMENTO CORSE: DOVE VANNO E DA DOVE VENGONO ===")

t370_orig = pinerolo['Pi0370']
print(f"\n🔴 Pi0370 ORIGINALE AZIENDA (06:30 - 11:45):")
for a in t370_orig['attivita']:
    print(f"   {a['partenza']} - {a['arrivo']} | {a['linea']:5s} | {a['da']} -> {a['a']}")

print("\n--- OPZIONE 1: Pi0370 TIENE TUTTO IL SUO MATTINO E RICEVE IL POMERIGGIO DA Pi0080 ---")
print("• Mattino Pi0370 (Invariato): 06:30 - 11:45 (Linea 281 Scalenghe + Linea 703 Navette)")
print("• Sosta Pranzo: 11:45 - 12:45 (1h a Pinerolo Deposito)")
print("• Pomeriggio: 12:50 - 14:55 (Linea 901 Pinerolo <-> Torre Pellice A/R) [RICEVUTA DA Pi0080]")
print("==> RISULTATO Pi0370:")
print("   • Inizio: 06:30 | Fine: 15:05")
print("   • Nastro: 8h 35m (06:30 - 15:05)")
print("   • OLG: 7h 20m (da 5h15 a 7h20, +2h05m di lavoro pieno!)")
print("   • Riprese: 2 riprese con pausa pranzo di 1 ora a Pinerolo.")

print("\n--- OPZIONE 2: SE Pi0370 CEDE LA LINEA 281 (06:50 - 07:45), DOVE VA? ---")
print("• La corsa Linea 281 Scalenghe (06:50 - 07:45) va al Turno Pi0470 o Pi0280:")
print("  - Nel PDF deve comparire: '🔴 Linea 281 Scalenghe (06:50-07:45) CEDUTA AL TURNO Pi0470'")
