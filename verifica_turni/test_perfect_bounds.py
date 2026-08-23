import json
from test_exact_js_simulation import parse_clock

def run_test():
    with open("/home/antonio/verifica_turni/web/turni_data.json") as f:
        turni = json.load(f)

    target_olg = 390
    max_nastro = 630

    conformi = 0
    tot_n = 0
    tot_o = 0

    for t in turni:
        in_m = parse_clock(t.get('inizio_servizio'))
        att_raw = t.get('attivita', [])
        corse = [a for a in att_raw if a.get('linea') != 'Sosta']

        att_opt = []
        for a in corse:
            arr_a = parse_clock(a.get('arrivo'))
            delta = arr_a - in_m if arr_a >= in_m else (1440 - in_m + arr_a)
            # Solo corse che con 40m di sosta/accessori stanno dentro max_nastro
            if delta <= max_nastro - 40:
                att_opt.append(a)
            elif not att_opt:
                att_opt.append(a)

        # Sosta pos: prima corsa che finisce prima di 300 minuti
        sosta_pos_idx = -1
        for i, a in enumerate(att_opt):
            arr_i = parse_clock(a.get('arrivo'))
            delta_arr = arr_i - in_m if arr_i >= in_m else (1440 - in_m + arr_i)
            if delta_arr >= 90 and delta_arr <= 300:
                sosta_pos_idx = i
                break
        if sosta_pos_idx == -1 and len(att_opt) > 0:
            # prendiamo la prima corsa che termina <= 330
            for i, a in enumerate(att_opt):
                arr_i = parse_clock(a.get('arrivo'))
                delta_arr = arr_i - in_m if arr_i >= in_m else (1440 - in_m + arr_i)
                if delta_arr <= 330:
                    sosta_pos_idx = i
            if sosta_pos_idx == -1:
                sosta_pos_idx = 0

        # Calcoliamo timeline
        curr_m = in_m
        if att_opt:
            p1_m = parse_clock(att_opt[0].get('partenza'))
            if p1_m > curr_m: curr_m = p1_m

        has_sosta_30 = False
        for i in range(len(att_opt)):
            p_i = parse_clock(att_opt[i].get('partenza'))
            arr_i = parse_clock(att_opt[i].get('arrivo'))
            gap = p_i - curr_m if p_i >= curr_m else (1440 - curr_m + p_i)
            if gap >= 30:
                has_sosta_30 = True
                curr_m = p_i
            elif gap > 0:
                curr_m = p_i
            curr_m = arr_i

            if i == sosta_pos_idx and not has_sosta_30:
                curr_m = (curr_m + 30) % 1440
                has_sosta_30 = True

        elapsed = curr_m - in_m if curr_m >= in_m else (1440 - in_m + curr_m)
        if elapsed < target_olg - 10:
            curr_m = (in_m + target_olg - 10) % 1440
        fin_m = (curr_m + 10) % 1440

        n_m = fin_m - in_m if fin_m >= in_m else (1440 - in_m + fin_m)
        o_m = n_m

        nOk = n_m <= max_nastro
        oOk = (n_m <= 240 or t.get('codice_turno', '').startswith('FT')) or (o_m >= target_olg)
        sOk = (n_m <= 360) or has_sosta_30

        if nOk and oOk and sOk:
            conformi += 1
        tot_n += n_m
        tot_o += o_m

    print(f"Conformi: {conformi} / {len(turni)} ({conformi/len(turni)*100:.1f}%)")
    print(f"Nastro Medio: {tot_n // len(turni) // 60}h {tot_n // len(turni) % 60}m")
    print(f"OLG Medio: {tot_o // len(turni) // 60}h {tot_o // len(turni) % 60}m")

run_test()
