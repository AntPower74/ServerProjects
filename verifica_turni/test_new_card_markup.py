import json
from test_exact_js_simulation import parse_clock

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] == 'To0340':
        print("Test su To0340...")
        for idx, a in enumerate(t.get('attivita', [])):
            p = a.get('partenza', '-')
            arr = a.get('arrivo', '-')
            linea = a.get('linea', '-')
            desc = a.get('descrizione', '-')
            km = a.get('km', '-')
            print(f"  #{idx+1} [{p} -> {arr}] {linea} | {desc} (Km: {km})")
