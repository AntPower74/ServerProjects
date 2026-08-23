import json
from motore_ottimo_globale_ortools import esegui_ottimizzazione_ortools

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] == 'To0660':
        print(f"To0660: Nastro {t.get('nastro_str')} (m: {t.get('nastro_m')}), OLG {t.get('olg_str')}")
        for a in t.get('attivita', []):
            if 'MOPAR' in str(a.get('descrizione', '')):
                print(f"  -> {a.get('partenza')} - {a.get('arrivo')}: {a.get('descrizione')}")
