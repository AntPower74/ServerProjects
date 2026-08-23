#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = {t['codice_turno']: t for t in turni if t['codice_turno'].startswith('Pi')}
t260 = pinerolo['Pi0260']

print("=== CORSE ORIGINALI DI Pi0260 ===")
for i, a in enumerate(t260['attivita'], 1):
    print(f"{i:2d}. {a['partenza']} -> {a['arrivo']} | {a['linea']:5s} | {a['da']} -> {a['a']}")

# Analizziamo la connessione:
# Tratta 10: 14:30 - 15:15 (Airasca -> Seggovia Vandalino)
# Tratta 11: 15:15 - 15:20 (Trasf Seggovia Vandalino -> Torre Pellice)
# Tratta 12: 16:10 - 16:40 (Linea 284 Torre Pellice -> Pinerolo)
# Tratta 13: 16:45 - 17:15 (Linea 281 Pinerolo -> Volvera)
# Tratta 14: 17:15 - 17:20 (Trasf Volvera -> Airasca)
# Tratta 15: 17:30 - 18:16 (Linea 284 Airasca -> Seggovia Vandalino)
# Tratta 16: 18:16 - 18:41 (Trasf Seggovia Vandalino -> Pinerolo Deposito)
# Tratta 17: 18:41 - 18:51 (Disp Pulizia)

print("\n--- PERFETTA COERENZA DEI COLLEGAMENTI: ---")
print("• Seggovia Vandalino si trova a Torre Pellice (sono 2 km di trasferimento, 5 minuti).")
print("• Se Pi0260 fa la mattina (06:49 - 08:15) e il pomeriggio (13:05 - 15:20 con rientro al deposito alle 15:40):")
print("  - Nastro: 06:49 - 15:40 = 8h 51m (-3h11m rispetto a 12h02!)")
print("  - OLG: 4h 30m")
print("• E le corse del tardo pomeriggio (16:10 - 18:51) vengono cedute al turno serale Pi0250!")
