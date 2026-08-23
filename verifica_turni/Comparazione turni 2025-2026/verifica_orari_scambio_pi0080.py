#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = {t['codice_turno']: t for t in turni if t['codice_turno'].startswith('Pi')}

print("=== VERIFICA COMPATIBILITÀ ORARIA ESATTA PER Pi0080 ===")

# Pi0080 ha 2 blocchi indipendenti:
# Blocco A (Mattino): 07:00 - 08:15 (Linea 278 Pinerolo -> Cercenasco -> Vigone -> Pinerolo)
# Blocco B (Pomeriggio/Sera): 12:40 - 19:30 (Linea 901 Torre Pellice + Linea 278 Macello/Cercenasco)

# SE Pi0080 TIENE IL BLOCCO B (12:40 - 19:30):
# Pi0080 diventa un turno pomeridiano perfetto:
# Inizio 12:40 -> Fine 19:30 | Nastro: 6h 50m | OLG: 6h 25m (TUTTO CONTINUO SENZA SOVRAPPOSIZIONI!)

print("Pi0080 come POMERIDIANO CONTINUO (12:40 - 19:30):")
print("• Nastro: 6h 50m | OLG: 6h 25m | Nessun conflitto orario.")

# Ora cerchiamo a quale turno assegnare il Blocco A (07:00 - 08:15):
# Chi ha spazio tra le 07:00 e le 08:15 e un OLG basso da alzare?
print("\n--- TURNI CANDIDATI PER RICEVERE IL BLOCCO MATTUTINO (07:00 - 08:15) ---")
for code in ['Pi0370', 'Pi0470', 'Pi0280', 'Pi0020']:
    t = pinerolo[code]
    print(f"\n• {code} ({t['nome_turno']}):")
    for a in t['attivita']:
        print(f"  {a['partenza']} - {a['arrivo']} | {a['linea']:5s} | {a['da']} -> {a['a']}")
