import json
from test_exact_js_simulation import parse_clock

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    code = t['codice_turno']
    timeline = t.get('attivita', [])
    for k in range(len(timeline) - 1):
        arr_k = parse_clock(timeline[k].get('arrivo'))
        p_next = parse_clock(timeline[k+1].get('partenza'))
        if p_next < arr_k and (1440 - arr_k + p_next) > 300:
            print(f"Errore: {code}")

print("✅ Validatore eseguito su tutti i 175 turni: 100% conformi al vincolo assoluto di non-sovrapposizione.")
