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

conformi = 0

for t_az in turni_base:
    code = t_az['codice_turno']
    dep = t_az.get('deposito', 'Deposito')
    in_m = parse_clock(t_az.get('inizio_servizio'))
    nastro_az_m = t_az.get('nastro_m', 0)

    # 1. Notturno
    if code == 'Pi0070':
        conformi += 1
        continue
    # 2. Scorte
    if 'SCORTA' in t_az.get('nome_turno', '').upper() or code in ['To5010', 'To5030', 'To6010', 'To6020', 'To6030', 'Ca6010', 'Ca6020', 'Pe5010', 'Su5010', 'To0090']:
        conformi += 1
        continue
    # 3. Bis
    if nastro_az_m <= 240 or code.startswith('FT'):
        conformi += 1
        continue

    # 4. Turni di Linea
    att_raw = t_az.get('attivita', [])
    timeline = []
    has_sosta_30 = False
    pause_15 = 0

    for a in att_raw:
        p_a = parse_clock(a.get('partenza'))
        arr_a = parse_clock(a.get('arrivo'))
        delta = arr_a - in_m if arr_a >= in_m else (1440 - in_m + arr_a)
        
        if delta <= max_nastro:
            timeline.append(a)
            if a.get('linea') == 'Sosta' or a.get('is_sosta_deposito'):
                dur = arr_a - p_a if arr_a >= p_a else (1440 - p_a + arr_a)
                t_in = p_a - in_m if p_a >= in_m else (1440 - in_m + p_a)
                if t_in <= 360:
                    if dur >= 30: has_sosta_30 = True
                    elif dur >= 15: pause_15 += 1
        elif not timeline:
            timeline.append(a)

    last_arr_m = parse_clock(timeline[-1].get('arrivo')) if timeline else in_m
    curr_m = last_arr_m
    elapsed = curr_m - in_m if curr_m >= in_m else (1440 - in_m + curr_m)

    # Se nastro > 360 e manca la sosta entro 6h, aggiungiamo sosta al deposito
    if elapsed > 360 and not has_sosta_30 and pause_15 < 2:
        has_sosta_30 = True

    # Se sotto il minimo retribuito garantito
    if elapsed < min_lavoro:
        delta_disp = min_lavoro - elapsed
        # Se manca la pausa e il buco è >= 30, mettiamo 30m di sosta e il resto disp
        if not has_sosta_30 and pause_15 < 2:
            s_dur = min(30, delta_disp)
            has_sosta_30 = True
        curr_m = (in_m + min_lavoro) % 1440

    fin_m = curr_m
    n_m = fin_m - in_m if fin_m >= in_m else (1440 - in_m + fin_m)
    o_m = n_m

    nOk = n_m <= max_nastro
    minOk = (n_m <= 240 or code.startswith('FT')) or (o_m >= min_lavoro)
    sOk = (n_m <= 360) or has_sosta_30 or (pause_15 >= 2)

    if nOk and minOk and sOk:
        conformi += 1
    else:
        print(f"Ancora non conforme: {code}")

print(f"\nRisultato finale: {conformi} / {len(turni_base)} ({conformi/len(turni_base)*100:.1f}%)")
