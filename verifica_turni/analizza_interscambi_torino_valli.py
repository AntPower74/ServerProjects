import json

with open("/home/antonio/verifica_turni/DATABASE_CORSE_DA_SHEETS.json", "r", encoding="utf-8") as f:
    db = json.load(f)

# Cerchiamo le corse che collegano Torino con Pinerolo, Val Susa e Aosta
corse_torino_radiali = []
for t, corse in db.items():
    for c in corse:
        p = c['partenza'].upper()
        a = c['arrivo'].upper()
        if "TORINO" in p or "TORINO" in a:
            corse_torino_radiali.append((t, c))

print(f"=== TOTALE CORSE CON ORIGINE O DESTINAZIONE TORINO: {len(corse_torino_radiali)} ===")
print("Esempi di linee radiali su cui scambiare vetture/autisti con Grugliasco:")
linee_viste = set()
for t, c in corse_torino_radiali:
    l_key = f"Linea {c['cod_linea']} ({c['partenza'][:20]} <-> {c['arrivo'][:20]})"
    if l_key not in linee_viste:
        linee_viste.add(l_key)
        print(f"- {l_key} | Assegnata attualmente al Turno {t}")

