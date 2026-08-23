#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = {t['codice_turno']: t for t in turni if t['codice_turno'].startswith('Pi')}
perosa = {t['codice_turno']: t for t in turni if t['codice_turno'].startswith('Pe')}

print("=== OPPORTUNITÀ DI SCAMBIO INCROCIATO PINEROLO <---> PEROSA ARGENTINA ===\n")

print("1. CASO CLAMOROSO: Pi0620 (Pinerolo) <---> Pe0270 (Perosa)")
print("   • Pi0620 (Pinerolo):")
print("     - Arriva a Perosa Argentina alle 15:05 e resta FERMO al Deposito di Perosa dalle 15:05 alle 16:41 (1h 36m di fermo passivo a Perosa!).")
print("     - Poi riparte alle 16:42 per Pinerolo e fa Torino, chiudendo alle 20:29.")
print("   • Pe0270 (Perosa Argentina):")
print("     - Arriva a Pinerolo alle 15:23 e resta FERMO al Deposito di Pinerolo dalle 15:23 alle 16:38 (1h 15m di fermo passivo a Pinerolo!).")
print("     - Poi alle 16:48 fa la Linea 275 per Perosa Argentina, ma chiude il turno al Deposito di Pinerolo alle 17:30 (FUORI SEDE!).")
print("   ==> SCAMBIO NATURALE:")
print("     - L'autista di Perosa (Pe0270) alle 15:23 prende subito la corsa di rientro per Perosa e CHIUDE A CASA a Perosa Argentina alle 16:00!")
print("       --> Nastro Pe0270 scende da 11h05 a 9h35 (-1h30m) e chiude nel proprio deposito di residenza!")
print("     - L'autista di Pinerolo (Pi0620) che è a Perosa scambia il rientro e copre il servizio su Torino rientrando a Pinerolo!")

print("\n2. CASO Pi0010 (1 Pinerolo - Nastro 11h39) <---> Pe0220 (Perosa - Nastro 10h46)")
print("   • Pe0220 (Perosa) scende a Pinerolo/Osasio (Linee 278/281) alle 17:00-18:40.")
print("   • Se le corse di bassa pianura (Osasio/Vigone) vengono fatte da Pinerolo (Pi0010 o Pi0060), Pe0220 rimane in Val Chisone!")
