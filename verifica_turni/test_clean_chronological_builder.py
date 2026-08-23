import json
from test_exact_js_simulation import parse_clock

def fmt_time(m):
    h = (m // 60) % 24
    mins = m % 60
    return f"{h:02d}:{mins:02d}"

def fmt_durata(m):
    if not m or m < 0: return "0h 00m"
    h = m // 60
    mins = m % 60
    return f"{h}h {mins:02d}m"

with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
    turni = json.load(f)

for t in turni:
    if t['codice_turno'] == 'To0660':
        print("Test su To0660...")
        att_raw = t.get('attivita', [])
        # Filtriamo solo se non supera max_nastro
        timeline = []
        for a in att_raw:
            timeline.append(a)
        
        for idx, a in enumerate(timeline):
            print(f"  {idx+1}. [{a.get('partenza')} -> {a.get('arrivo')}] {a.get('linea')} : {a.get('descrizione', '')}")
