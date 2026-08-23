import json

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] == 'Su5010':
        print(json.dumps(t, indent=2))
