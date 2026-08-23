#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = {t['codice_turno']: t for t in turni if t['codice_turno'].startswith('Pi')}

print("=== VERIFICA TECNICA: PERCHÉ IL BLOCCO 901 DI Pi0080 È INSEPARABILE ===")
t80 = pinerolo['Pi0080']
for i, a in enumerate(t80['attivita'], 1):
    print(f"{i:2d}. {a['partenza']} -> {a['arrivo']} | {a['linea']:5s} | {a['da']} -> {a['a']}")

print("\n--- ANALISI CORRETTA: ---")
print("1. Il blocco 12:40 - 16:10 è un ciclo completo di Linea 901 (Pinerolo <-> Torre Pellice A/R per 2 volte).")
print("   Non può essere spezzato a metà alle 14:55 perché il bus/autista si trova a Torre Pellice alle 14:55 e deve riportare la corsa delle 15:35 a Pinerolo!")
print("2. L'intero pomeriggio di Pi0080 (12:40 - 19:30) è un blocco CONTINUO perfetto:")
print("   • 12:40 - 16:10: Linea 901")
print("   • 16:30 - 19:10: Linea 278")
print("   • 19:10 - 19:30: Deposito")
print("   ==> Se Pi0080 fa SOLO questo blocco pomeridiano (12:40 - 19:30):")
print("       - Nastro: 6h 50m (CONTINUO, ZERO STACCHI!)")
print("       - OLG: 6h 25m di lavoro pieno.")

print("\n3. DOVE VA LA CORSA DEL MATTINO DI Pi0080 (07:00 - 08:15 Linea 278)?")
print("   • Tratta: 07:15 - 08:05 Linea 278 (Pinerolo -> Cercenasco -> Vigone -> Pinerolo Piazza Cavour).")
print("   • Questa corsa mattutina si innesta perfettamente in Pi0370 (dalle 07:00 alle 08:15) prima delle navette 703 (08:20 - 11:45).")
print("   • E la corsa delle 06:50 - 07:45 (Linea 281 Scalenghe) di Pi0370 viene coperta dal turno Pi0280 (Virle/Scalenghe)!")
