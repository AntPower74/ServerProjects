import json
from collections import defaultdict

with open("/home/antonio/verifica_turni/DATABASE_CORSE_DA_SHEETS.json", "r", encoding="utf-8") as f:
    db = json.load(f)

# Analizziamo le corse per ciascun deposito:
# 1. PEROSA ARGENTINA (Pe*)
# 2. LUSERNA S.G. (Lu*)
# 3. BOBBIO PELLICE (Bo*)
# 4. SALBERTRAND (Sa*)
# 5. SUSA (Su*)
# 6. PONT SAINT MARTIN (Pt*)
# 7. PINEROLO (Pi*)

depositi_corse = defaultdict(list)
for turno, corse in db.items():
    dep = "ALTRO"
    if turno.startswith('To'): dep = "TORINO"
    elif turno.startswith('Pi'): dep = "PINEROLO"
    elif turno.startswith('Pe'): dep = "PEROSA"
    elif turno.startswith('Lu'): dep = "LUSERNA"
    elif turno.startswith('Ba'): dep = "BARGE"
    elif turno.startswith('Bo'): dep = "BOBBIO"
    elif turno.startswith('Pt'): dep = "PONT"
    elif turno.startswith('Iv'): dep = "IVREA"
    elif turno.startswith('Su'): dep = "SUSA"
    elif turno.startswith('Sa'): dep = "SALBERTRAND"
    elif turno.startswith('Ca'): dep = "CASELLE"
    elif turno.startswith('Pb'): dep = "PIOBESI"
    
    for c in corse:
        depositi_corse[dep].append((turno, c))

print("=== DISTRIBUZIONE CORSE COMMERCIALI DA RISTRUTTURARE PER DEPOSITO ===")
for d, c_list in sorted(depositi_corse.items()):
    print(f"• Deposito {d:<15}: {len(c_list):>3} corse commerciali")

