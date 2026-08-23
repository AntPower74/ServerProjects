import json
from test_exact_js_simulation import parse_clock

def test_solver(min_lavoro=390, max_nastro=630):
    with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
        turni_base = json.load(f)

    conformi = 0
    tot_nastro = 0
    tot_olg = 0

    for t_az in turni_base:
        code = t_az['codice_turno']
        nome_az = t_az.get('nome_turno', code)
        in_m = parse_clock(t_az.get('inizio_servizio'))
        nastro_az_m = t_az.get('nastro_m', 0)

        # 1. Notturno
        if code == 'Pi0070':
            dur_nott = max(min_lavoro, min(max_nastro, 450))
            conformi += 1
            tot_nastro += dur_nott
            tot_olg += dur_nott
            continue

        # 2. Scorte
        if 'SCORTA' in nome_az.upper() or code in ['To5010', 'To5030', 'To6010', 'To6020', 'To6030', 'Ca6010', 'Ca6020', 'Pe5010', 'Su5010', 'To0090']:
            dur_scorta = max(min_lavoro, min(max_nastro, t_az.get('nastro_m', 420)))
            conformi += 1
            tot_nastro += dur_scorta
            tot_olg += dur_scorta
            continue

        # 3. Bis / FT
        if nastro_az_m <= 240 or code.startswith('FT'):
            conformi += 1
            tot_nastro += nastro_az_m
            tot_olg += nastro_az_m
            continue

        # 4. Turni di Linea
        att_raw = t_az.get('attivita', [])
        corse = [a for a in att_raw if a.get('linea') != 'Sosta']

        att_opt = []
        for a in corse:
            arr_a = parse_clock(a.get('arrivo'))
            delta = arr_a - in_m if arr_a >= in_m else (1440 - in_m + arr_a)
            if delta <= max_nastro - 40:
                att_opt.append(a)
            elif not att_opt:
                att_opt.append(a)

        curr_m = in_m
        if att_opt:
            p1_m = parse_clock(att_opt[0].get('partenza'))
            if p1_m > curr_m:
                curr_m = p1_m

        has_sosta_30 = False
        pause_15 = 0

        for i in range(len(att_opt)):
            p_i = parse_clock(att_opt[i].get('partenza'))
            arr_i = parse_clock(att_opt[i].get('arrivo'))
            gap = p_i - curr_m if p_i >= curr_m else (1440 - curr_m + p_i)
            t_da_in = p_i - in_m if p_i >= in_m else (1440 - in_m + p_i)
            
            if gap > 0 and gap <= 180:
                if t_da_in <= 360:
                    if gap >= 30: has_sosta_30 = True
                    elif gap >= 15: pause_15 += 1
                curr_m = p_i
                
            curr_m = arr_i

        # Se sotto il minimo contrattuale, top-up al minimo
        elapsed = curr_m - in_m if curr_m >= in_m else (1440 - in_m + curr_m)
        if elapsed < min_lavoro - 10:
            curr_m = (in_m + min_lavoro - 10) % 1440

        fin_m = (curr_m + 10) % 1440
        n_m = fin_m - in_m if fin_m >= in_m else (1440 - in_m + fin_m)
        o_m = n_m

        nOk = n_m <= max_nastro
        oOk = (n_m <= 240 or code.startswith('FT')) or (o_m >= min_lavoro)
        sOk = (n_m <= 360) or has_sosta_30 or (pause_15 >= 2)

        if nOk and oOk and sOk:
            conformi += 1
        tot_nastro += n_m
        tot_olg += o_m

    print(f"Min: {min_lavoro//60}h {min_lavoro%60:02d}m | Max: {max_nastro//60}h {max_nastro%60:02d}m -> Conformi: {conformi}/{len(turni_base)} ({conformi/len(turni_base)*100:.1f}%) | Nastro Medio: {tot_nastro//len(turni_base)//60}h {tot_nastro//len(turni_base)%60:02d}m")

test_solver(390, 630)
test_solver(360, 600)
test_solver(420, 660)
