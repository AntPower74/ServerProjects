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
    turni_base = json.load(f)

min_lavoro = 390
max_nastro = 630

overlap_count = 0

for t_az in turni_base:
    code = t_az['codice_turno']
    dep = t_az.get('deposito', 'Deposito')
    in_m = parse_clock(t_az.get('inizio_servizio'))
    nastro_az_m = t_az.get('nastro_m', 0)
    
    # 1. Notturno
    if code == 'Pi0070': continue
    # 2. Scorte
    if 'SCORTA' in t_az.get('nome_turno', '').upper() or code in ['To5010', 'To5030', 'To6010', 'To6020', 'To6030', 'Ca6010', 'Ca6020', 'Pe5010', 'Su5010', 'To0090']: continue
    # 3. Bis
    if nastro_az_m <= 240 or code.startswith('FT'): continue

    # 4. Turni di Linea
    att_raw = t_az.get('attivita', [])
    
    # Manteniamo la struttura reale delle attività senza sovrapposizioni
    timeline = []
    for a in att_raw:
        p_a = parse_clock(a.get('partenza'))
        arr_a = parse_clock(a.get('arrivo'))
        delta = arr_a - in_m if arr_a >= in_m else (1440 - in_m + arr_a)
        
        # Filtro max nastro
        if delta <= max_nastro:
            timeline.append(a)
        elif not timeline:
            timeline.append(a)

    # Verifica sovrapposizioni
    for i in range(len(timeline) - 1):
        arr_curr = parse_clock(timeline[i].get('arrivo'))
        p_next = parse_clock(timeline[i+1].get('partenza'))
        if arr_curr > p_next and abs(arr_curr - p_next) < 720:
            print(f"⚠️ SOVRAPPOSIZIONE in {code}: {timeline[i]['linea']} ({timeline[i]['partenza']}->{timeline[i]['arrivo']}) si sovrappone a {timeline[i+1]['linea']} ({timeline[i+1]['partenza']}->{timeline[i+1]['arrivo']})")
            overlap_count += 1

print(f"\nTotale sovrapposizioni trovate: {overlap_count}")
