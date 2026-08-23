import json

with open("/home/antonio/verifica_turni/DATABASE_CORSE_DA_SHEETS.json", "r", encoding="utf-8") as f:
    db = json.load(f)

# Analizziamo tutte le corse di Barge (Ba3510, Ba3520, Ba3530, Ba3560)
corse_barge = []
for t in ["Ba3510", "Ba3520", "Ba3530", "Ba3560"]:
    for c in db.get(t, []):
        corse_barge.append((t, c))

print("=== TUTTE LE CORSE ASSEGNATE A BARGE DALL'AZIENDA ===")
for t, c in corse_barge:
    print(f"Turno {t} | Corsa {c['cod_corsa']:<6} | Linea {c['cod_linea']:<4} | {c['ora_partenza']:>8} ({c['partenza'][:25]}) -> {c['ora_arrivo']:>8} ({c['arrivo'][:25]})")

