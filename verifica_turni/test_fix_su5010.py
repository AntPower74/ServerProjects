import json
from test_exact_js_simulation import parse_clock

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] == 'Su5010':
        print("Su5010:")
        print("  Inizio:", t.get('inizio_servizio'))
        print("  Fine:", t.get('fine_servizio'))
        print("  Nastro:", t.get('nastro_m'))
