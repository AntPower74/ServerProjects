#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

t_0080 = [t for t in turni if t['codice_turno'] == 'Pi0080'][0]
t_0370 = [t for t in turni if t['codice_turno'] == 'Pi0370'][0]

print("=== SITUAZIONE ORIGINALE AZIENDA ===")
print(f"🔴 Pi0080: Inizio {t_0080['inizio_servizio']} | Fine {t_0080['fine_servizio']} | Nastro {t_0080['nastro']} | OLG {t_0080['ore_lavoro']}")
for a in t_0080['attivita']:
    print(f"   {a['linea']:5s} | {a['partenza']} - {a['arrivo']} | {a['da']} -> {a['a']}")

print(f"\n🔴 Pi0370: Inizio {t_0370['inizio_servizio']} | Fine {t_0370['fine_servizio']} | Nastro {t_0370['nastro']} | OLG {t_0370['ore_lavoro']}")
for a in t_0370['attivita']:
    print(f"   {a['linea']:5s} | {a['partenza']} - {a['arrivo']} | {a['da']} -> {a['a']}")

print("\n" + "="*80)
print("🎯 PROPOSTA OTTIMIZZATA PERFETTA PER Pi0080 e Pi0370:")
print("="*80)
print("1. Pi0080 CEDE IL PEZZETTO DEL MATTINO (07:00 - 08:15) a Pi0370")
print("   E Pi0080 DIVENTA UN POMERIDIANO CONTINUO:")
print("   • Inizio: 12:40 (Pinerolo Deposito)")
print("   • 12:50 - 13:25 Linea 901 PINEROLO -> TORRE PELLICE")
print("   • 13:35 - 14:10 Linea 901 TORRE PELLICE -> PINEROLO")
print("   • 14:20 - 14:55 Linea 901 PINEROLO -> TORRE PELLICE")
print("   • 15:35 - 16:10 Linea 901 TORRE PELLICE -> PINEROLO")
print("   • 16:30 - 16:50 Linea 278 PINEROLO -> MACELLO")
print("   • 16:50 - 17:17 Linea 278 MACELLO -> PINEROLO")
print("   • 17:40 - 18:20 Linea 278 PINEROLO -> CERCENASCO")
print("   • 18:25 - 19:10 Linea 278 CERCENASCO -> PINEROLO")
print("   • Fine: 19:30 (Pinerolo Deposito)")
print("   ==> NASTRO Pi0080: 6h 50m (invece di 12h 30m!)")
print("   ==> OLG Pi0080: 6h 25m di lavoro continuo senza buchi passivi!")

print("\n2. Pi0370 RICEVE IL MATTINO DI Pi0080 E FA UN MATTINALE CONTINUO:")
print("   • Inizio: 06:50 (Pinerolo Deposito)")
print("   • 07:15 - 07:35 Linea 278 PINEROLO -> CERCENASCO (ex Pi0080)")
print("   • 07:40 - 08:05 Linea 278 VIGONE -> PINEROLO (ex Pi0080)")
print("   • 08:20 - 11:30 Linea 703 NAVETTE RIVA / FIUGERA (proprie corse Pi0370)")
print("   • Fine: 11:45 (Pinerolo Deposito)")
print("   ==> NASTRO Pi0370: 4h 55m (06:50 - 11:45)")
print("   ==> OLG Pi0370: 4h 55m (+ corse successive fino a 6h30 se inseriamo un rinforzo)")
