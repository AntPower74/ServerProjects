import json

with open("/home/antonio/verifica_turni/DATABASE_CORSE_DA_SHEETS.json", "r", encoding="utf-8") as f:
    db = json.load(f)

# Raccogliamo TUTTE le 32 corse commerciali di Barge assegnate dall'azienda
corse_barge = []
for t in ["Ba3510", "Ba3520", "Ba3530", "Ba3560"]:
    for c in db.get(t, []):
        corse_barge.append(c)

# Ordiniamo tutte le corse per orario di partenza
def get_sec(ora_str):
    p = ora_str.split(':')
    return int(p[0]) * 3600 + int(p[1]) * 60

corse_barge.sort(key=lambda x: get_sec(x['ora_partenza']))

print(f"=== TOTALE CORSE COMMERCIALI DI BARGE DA COPRIRE AL 100%: {len(corse_barge)} ===")
for c in corse_barge:
    print(f"[{c['ora_partenza']:>8} -> {c['ora_arrivo']:>8}] Linea {c['cod_linea']:<4} Corsa {c['cod_corsa']:<6} | {c['partenza'][:28]} -> {c['arrivo'][:28]}")

