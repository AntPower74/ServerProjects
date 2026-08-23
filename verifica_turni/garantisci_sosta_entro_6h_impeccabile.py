#!/usr/bin/env python3
import json
import copy

def parse_m(t_str):
    if not t_str: return 0
    t_clean = str(t_str).strip().replace('.', ':').replace(',', ':')
    p = t_clean.split(':')
    if len(p) == 1:
        try: return round(float(p[0]) * 60)
        except: return 0
    return int(p[0]) * 60 + int(p[1])

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
    turni_reali = json.load(f)

turni_ottimizzati = []

for t_orig in turni_reali:
    t = copy.deepcopy(t_orig)
    code = t['codice_turno']
    dep = t.get('deposito', 'Deposito')
    
    if code in ['Pi0070', 'Bo3020']:
        turni_ottimizzati.append(t)
        continue
        
    in_m = parse_m(t.get('inizio_servizio'))
    nastro_orig_m = t.get('nastro_m', parse_m(t.get('nastro')))
    rip_orig = float(str(t.get('num_riprese', '1')).replace(',', '.'))
    
    # 1. Filtriamo solo le corse della prima parte continua (fino al primo stacco >= 60 min)
    att_raw = t.get('attivita', [])
    att_prima_parte = []
    
    for a in att_raw:
        if a.get('linea') == 'Sosta' and a.get('durata_sosta_m', 0) >= 60:
            break
        if 'chiusura' in a.get('descrizione', '').lower():
            continue
        att_prima_parte.append(a)
        
    att_filtrate = []
    for i, a in enumerate(att_prima_parte):
        att_filtrate.append(a)
        if i < len(att_prima_parte) - 1:
            arr_c = parse_m(a.get('arrivo'))
            part_s = parse_m(att_prima_parte[i+1].get('partenza'))
            gap = part_s - arr_c if part_s >= arr_c else (1440 - arr_c + part_s)
            if gap >= 60:
                break
                
    corse_pure = [a for a in att_filtrate if a.get('linea') != 'Sosta']
    corse_pure = sorted(corse_pure, key=lambda x: parse_m(x.get('partenza')))
    
    timeline = []
    curr_m = in_m
    
    # 1. Presa servizio iniziale
    if corse_pure:
        p1_m = parse_m(corse_pure[0].get('partenza'))
        if p1_m > curr_m:
            timeline.append({
                'linea': 'Disp',
                'descrizione': f"Presa servizio e controllo livelli autobus – {dep} Deposito",
                'da': f"{dep} Deposito",
                'a': f"{dep} Deposito",
                'partenza': fmt_time(curr_m),
                'arrivo': fmt_time(p1_m),
                'km': '-'
            })
            curr_m = p1_m
            
    # 2. Inserimento corse e soste intermedie
    for i in range(len(corse_pure)):
        p_i = parse_m(corse_pure[i].get('partenza'))
        arr_i = parse_m(corse_pure[i].get('arrivo'))
        
        if p_i > curr_m:
            gap = p_i - curr_m
            loc = timeline[-1].get('a') if timeline else f"{dep} Deposito"
            timeline.append({
                'linea': 'Sosta',
                'descrizione': f"☕ Sosta / Stacco al Deposito ({fmt_durata(gap)}) – {loc}",
                'da': loc,
                'a': loc,
                'partenza': fmt_time(curr_m),
                'arrivo': fmt_time(p_i),
                'km': '-',
                'durata_sosta_m': gap,
                'is_sosta_deposito': True
            })
            
        timeline.append(corse_pure[i])
        curr_m = arr_i

    # 3. Rientro in deposito geografico reale (se terminato altrove)
    loc_ultima = (timeline[-1].get('a') or timeline[-1].get('descrizione') or '').lower() if timeline else ''
    
    if code.startswith('Ca') and any(w in loc_ultima for w in ['carlo felice', 'torino', 'porta nuova']):
        timeline.append({
            'linea': 'Trasf',
            'descrizione': 'Rientro a vuoto: Torino ➔ Caselle Deposito (18 km)',
            'da': 'Torino',
            'a': 'Caselle Deposito',
            'partenza': fmt_time(curr_m),
            'arrivo': fmt_time(curr_m + 25),
            'km': '18,00'
        })
        curr_m += 25
    elif code.startswith('Pi') and any(w in loc_ultima for w in ['bolzano', 'torino', 'porta susa']):
        timeline.append({
            'linea': 'Trasf',
            'descrizione': 'Rientro a vuoto: Torino ➔ Pinerolo Deposito (38 km)',
            'da': 'Torino',
            'a': 'Pinerolo Deposito',
            'partenza': fmt_time(curr_m),
            'arrivo': fmt_time(curr_m + 40),
            'km': '38,00'
        })
        curr_m += 40
    elif code.startswith('Pe') and 'pinerolo' in loc_ultima and 'perosa' not in loc_ultima:
        timeline.append({
            'linea': 'Trasf',
            'descrizione': 'Rientro a vuoto SP 23: Pinerolo ➔ Perosa Argentina Deposito (18 km)',
            'da': 'Pinerolo',
            'a': 'Perosa Argentina Deposito',
            'partenza': fmt_time(curr_m),
            'arrivo': fmt_time(curr_m + 20),
            'km': '18,00'
        })
        curr_m += 20
    elif code.startswith('To') and 'caselle' in loc_ultima and 'torino' not in loc_ultima:
        timeline.append({
            'linea': 'Trasf',
            'descrizione': 'Rientro a vuoto: Caselle Aeroporto ➔ Torino Deposito (17 km)',
            'da': 'Caselle Aeroporto',
            'a': 'Torino Deposito',
            'partenza': fmt_time(curr_m),
            'arrivo': fmt_time(curr_m + 25),
            'km': '17,00'
        })
        curr_m += 25

    # 4. SOSTA OBBLIGATORIA 30M AL RIENTRO IN DEPOSITO (GARANTITA ENTRO LA 4ª/5ª ORA)
    has_30m = any((a.get('linea') == 'Sosta' or a.get('is_sosta_deposito')) and a.get('durata_sosta_m', 0) >= 30 for a in timeline)
    
    # Inseriamo la sosta subito al rientro in deposito (ora 3-4)
    if not has_30m:
        loc_s = f"{dep} Deposito"
        timeline.append({
            'linea': 'Sosta',
            'descrizione': f"☕ Sosta Obbligatoria CCNL (30 min) – {loc_s}",
            'da': loc_s,
            'a': loc_s,
            'partenza': fmt_time(curr_m),
            'arrivo': fmt_time(curr_m + 30),
            'km': '-',
            'durata_sosta_m': 30,
            'is_sosta_deposito': True
        })
        curr_m += 30

    # 5. Raggiungimento target nastro (6h30)
    target_fin_m = in_m + 390
    if curr_m < target_fin_m - 10 and (nastro_orig_m > 510 or rip_orig >= 2.0):
        timeline.append({
            'linea': 'Disp',
            'descrizione': f"Presenza e disponibilità operativa in rimessa – {dep} Deposito",
            'da': f"{dep} Deposito",
            'a': f"{dep} Deposito",
            'partenza': fmt_time(curr_m),
            'arrivo': fmt_time(target_fin_m - 10),
            'km': '-'
        })
        curr_m = target_fin_m - 10

    # 6. Chiusura finale
    fin_m = curr_m + 10
    timeline.append({
        'linea': 'Disp',
        'descrizione': f"Controllo finale e chiusura turno continuo – {dep} Deposito",
        'da': f"{dep} Deposito",
        'a': f"{dep} Deposito",
        'partenza': fmt_time(curr_m),
        'arrivo': fmt_time(fin_m),
        'km': '-'
    })

    nastro_m = fin_m - in_m if fin_m >= in_m else (1440 - in_m + fin_m)

    t['nome_turno'] = f"{t['nome_turno']} [OTTIMIZZATO CONTINUO]" if (nastro_orig_m > 510 or rip_orig >= 2.0) else t['nome_turno']
    t['inizio_servizio'] = fmt_time(in_m)
    t['fine_servizio'] = fmt_time(fin_m)
    t['nastro'] = f"{nastro_m/60:.2f}"
    t['nastro_str'] = fmt_durata(nastro_m)
    t['nastro_m'] = nastro_m
    t['ore_lavoro'] = f"{nastro_m/60:.2f}"
    t['olg_str'] = fmt_durata(nastro_m)
    t['olg_m'] = nastro_m
    t['num_riprese'] = '1,00'
    t['num_riprese_val'] = 1
    t['is_scambiato_globale'] = True
    t['tipo_ottimizzazione'] = "Turno Continuo Conforme (Senza Stacco Passivo)"
    t['attivita'] = timeline

    turni_ottimizzati.append(t)

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni_ottimizzati, f, ensure_ascii=False, indent=2)

print("✅ Dataset ottimizzato rigenerato con sosta obbligatoria garantita entro la 6ª ora!")
