#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

torino_dict = {t['codice_turno']: t for t in turni if t['codice_turno'].startswith('To')}
pinerolo_dict = {t['codice_turno']: t for t in turni if t['codice_turno'].startswith('Pi')}

print("=== OPPORTUNITÀ DI SCAMBIO TORINO <---> PINEROLO / PEROSA ===\n")

print("1. CASO Pi0300 (30 Pinerolo - Nastro 11h30) <---> To0710 (710 Torino - Nastro 11h20)")
print("   • Pi0300 (Pinerolo):")
print("     - Al mattino fa Pinerolo (06:00 - 08:15).")
print("     - Alle 10:23 sale a Torino con la 275 e fa linee urbane/interurbane di Torino (119+277) fino alle 13:55.")
print("     - Poi torna a Pinerolo e fa Virle alle 16:05 - 17:30 (3 riprese, nastro 11h30).")
print("   • To0710 (Torino):")
print("     - Scende a Pinerolo alle 06:10, sta fermo al Deposito di Pinerolo 46 min, poi fa la 275 per Torino alle 07:06.")
print("     - Sta fermo al Deposito di Torino per 3h16m (08:39 - 11:55) e poi fa il pomeriggio (119+277).")
print("   ==> SCAMBIO NATURALE:")
print("     - La corsa 275 del mattino (07:06 Pinerolo -> Torino) viene assegnata a un turno di Pinerolo.")
print("     - L'anello pomeridiano di Torino (10:23 - 13:55 Linee 275+119+277) viene interamente coperto da Torino (To0710), che diventa un turno continuativo mattino/pranzo.")
print("     - Pi0300 si concentra sul nodo di Pinerolo/Virle eliminando il viaggio isolato su Torino!")

