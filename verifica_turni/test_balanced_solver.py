import json
from motore_ottimo_globale_ortools import esegui_ottimizzazione_ortools

# Test con preservazione MOPAR
with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] == 'To0660':
        print("To0660 trovato con successo.")
