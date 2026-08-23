#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = {t['codice_turno']: t for t in turni if t['codice_turno'].startswith('Pi')}

print("=== CRONOLOGIA ESATTA Pi0080 ===")
for i, a in enumerate(pinerolo['Pi0080']['attivita'], 1):
    print(f"{i:2d}. {a['partenza']} -> {a['arrivo']} | {a['linea']:5s} | {a['da']} -> {a['a']}")

print("\n=== CRONOLOGIA ESATTA Pi0090 ===")
for i, a in enumerate(pinerolo['Pi0090']['attivita'], 1):
    print(f"{i:2d}. {a['partenza']} -> {a['arrivo']} | {a['linea']:5s} | {a['da']} -> {a['a']}")

print("\n=== CERCHIAMO TUTTI I TURNI LIBERI TRA LE 17:30 E LE 19:30 A PINEROLO ===")
for code, t in sorted(pinerolo.items()):
    att = t.get('attivita', [])
    if not att: continue
    in_s = att[0]['partenza']
    out_s = att[-1]['arrivo']
    
    # Controlla se il turno finisce prima delle 17:30 o inizia dopo le 17:30 o ha un buco 17:30-19:30
    print(f"• {code:6s} ({t['nome_turno'][:20]:20s}) | Servizio: {in_s} - {out_s} | Nastro: {t['nastro']} | OLG: {t['ore_lavoro']}")
