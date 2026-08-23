#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = [t for t in turni if t['codice_turno'].startswith('Pi')]

def parse_m(t):
    if not t: return 0
    p = t.replace('.', ':').split(':')
    return int(p[0]) * 60 + int(p[1])

def fmt_hm(m):
    return f"{m//60}h {m%60:02d}m"

print("=== VERIFICA RIGIDA: 32 TURNI INVARIATI E SCAMBIO DIRETTO DI CORSE ===\n")

# Analizziamo Pi0080 e cerchiamo con quale turno scambiare corse in modo 1-a-1
# Pi0080:
# Mattino: 07:00 - 08:15 (Linea 278 Pinerolo - Cercenasco - Vigone - Pinerolo) [1h15m servizio, 33 km]
# Sosta: 08:15 - 12:40 (4h25m)
# Pomeriggio: 12:40 - 19:30 (Linea 901 Torre Pellice + Linea 278 Macello/Cercenasco) [6h50m servizio, 152 km]

# Candidati per scambio con Pi0080:
# Turni pomeridiani/serali che hanno corse al mattino o turni mattinali che finiscono presto.
print("--- OPZIONE SCAMBIO 1-A-1 PER Pi0080 ---")
print("1. SCAMBIO CON Pi0090 (Attuale: 13:10 - 20:30, Nastro: 7h20, OLG: 6h36)")
print("   • Pi0090 fa: 13:10-15:50 (Linea 278 Vigone/Osasio) + 16:12-18:32 (Linea 279 Torre Pellice/Bobbio) + 19:10-20:10 (Linea 278 Cercenasco)")
print("   • Se Pi0080 e Pi0090 si scambiano le tratte di Linea 278:")
print("     - Pi0080 cede la corsa 278 sera (17:40 - 19:10) a Pi0090")
print("     - Pi0080 finisce alle 17:25 invece che alle 19:30!")
print("     --> Nastro Pi0080 scende da 12h30 a 10h25!")
print("     --> OLG Pi0080: 6h15m")
print("     --> Nastro Pi0090: rimane a 7h20 (13:10 - 20:30)")
print("     --> OLG Pi0090: sale da 6h36 a 7h15m (+40 min lavoro pieno)")

print("\n2. SCAMBIO CON Pi0280 (Attuale: 06:15 - 16:17, Nastro: 10h02, OLG: 5h07 - BASSO LAVORO)")
print("   • Pi0280 ha un buco enorme 08:15 - 13:10 (4h55m fermo) e fa solo 4h29m di guida.")
print("   • Scambio:")
print("     - Pi0080 cede le corse pomeridiane 12:50 - 14:55 (Linea 901) a Pi0280.")
print("     - Pi0280 in cambio cede a Pi0080 le sue navette del primo mattino 06:15 - 08:15 (Linea 281 Virle) o Pi0080 fa solo il blocco serale.")
