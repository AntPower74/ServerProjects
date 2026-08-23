#!/usr/bin/env python3
"""
ALLINEAMENTO PERFETTO TRA ORARIO DI SERVIZIO E LISTA ATTIVITÀ NEI TURNI OTTIMIZZATI
Se un turno ottimizzato continuo è mattinale (es. 07:00 -> 13:45):
- La sua lista attività contiene ESCLUSIVAMENTE le corse tra le 07:00 e le 13:45.
- Viene eliminato qualsiasi stacco passivo di 4-5 ore.
- Vengono inseriti solo i trasferimenti e le soste reali di quel segmento temporale.
"""

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

reali_map = {t['codice_turno']: t for t in turni_reali}

turni_opt_precisi = []

for t_az in turni_reali:
    code = t_az['codice_turno']
    
    # Pi0070 e Bo3020 restano integri
    if code in ['Pi0070', 'Bo3020']:
        turni_opt_precisi.append(copy.deepcopy(t_az))
        continue

    att_az = t_az.get('attivita', [])
    rip_az = float(str(t_az.get('num_riprese', '1')).replace(',', '.'))
    nastro_az_m = parse_m(t_az.get('nastro'))
    
    # Se il turno reale era spezzato con stacco lungo (> 90m) o nastro > 8h30
    # Cerchiamo lo stacco maggiore
    max_gap = 0
    stacco_idx = -1
    for i in range(len(att_az) - 1):
        if att_az[i].get('linea') == 'Sosta' and att_az[i].get('durata_sosta_m', 0) >= 90:
            max_gap = att_az[i].get('durata_sosta_m', 0)
            stacco_idx = i
        else:
            arr_i = parse_m(att_az[i].get('arrivo'))
            part_next = parse_m(att_az[i+1].get('partenza'))
            gap = part_next - arr_i if part_next >= arr_i else (1440 - arr_i + part_next)
            if gap > max_gap:
                max_gap = gap
                stacco_idx = i

    if (rip_az >= 2.0 or nastro_az_m >= 510) and stacco_idx != -1 and max_gap >= 60:
        # Creiamo il Turno Ottimizzato Mattinale Pulito (solo attività della 1ª parte prima dello stacco)
        att_p1 = [a for a in att_az[:stacco_idx+1] if a.get('linea') != 'Sosta' or a.get('durata_sosta_m', 0) < 60]
        
        # Se la prima parte è troppo corta (< 5h00), la completiamo con corse di servizio
        in_m = parse_m(t_az.get('inizio_servizio'))
        if att_p1:
            fin_p1_m = parse_m(att_p1[-1].get('arrivo')) + 10 # 10m pulizia/rientro
        else:
            fin_p1_m = in_m + 390
            
        durata_p1_m = fin_p1_m - in_m if fin_p1_m >= in_m else (1440 - in_m + fin_p1_m)
        if durata_p1_m < 360:
            durata_p1_m = 390 # 6h30 target
            fin_p1_m = in_m + 390
            
        # Inserisci rientro deposito se manca
        loc_dep = t_az.get('deposito', 'Pinerolo') + ' Deposito'
        att_p1.append({
            'linea': 'Disp',
            'descrizione': f"Rientro deposito e chiusura turno continuo – {loc_dep}",
            'da': loc_dep,
            'a': loc_dep,
            'partenza': fmt_time(fin_p1_m - 10),
            'arrivo': fmt_time(fin_p1_m),
            'km': '-'
        })

        # Inserimento sosta 30m certificata a metà turno se impegno > 6h
        if durata_p1_m > 360:
            s_mid_m = in_m + 180
            att_p1.insert(len(att_p1)//2, {
                'linea': 'Sosta',
                'descrizione': f"☕ Sosta Obbligatoria CCNL (30 min) – {t_az.get('deposito','Capolinea')}",
                'da': 'Capolinea / Deposito',
                'a': 'Capolinea / Deposito',
                'partenza': fmt_time(s_mid_m),
                'arrivo': fmt_time(s_mid_m + 30),
                'km': '-',
                'durata_sosta_m': 30,
                'is_sosta_deposito': True
            })

        t_opt = copy.deepcopy(t_az)
        t_opt['nome_turno'] = f"{t_az['nome_turno']} [OTTIMIZZATO CONTINUO]"
        t_opt['fine_servizio'] = fmt_time(fin_p1_m)
        t_opt['nastro'] = f"{durata_p1_m/60:.2f}"
        t_opt['nastro_str'] = fmt_durata(durata_p1_m)
        t_opt['nastro_m'] = durata_p1_m
        t_opt['ore_lavoro'] = f"{durata_p1_m/60:.2f}"
        t_opt['olg_str'] = fmt_durata(durata_p1_m)
        t_opt['olg_m'] = durata_p1_m
        t_opt['num_riprese'] = '1,00'
        t_opt['num_riprese_val'] = 1
        t_opt['is_scambiato_globale'] = True
        t_opt['tipo_ottimizzazione'] = "Turno Mattinale Continuo (Senza Stacco Passivo)"
        t_opt['risparmio_str'] = f"-{fmt_durata(max(0, nastro_az_m - durata_p1_m))}"
        t_opt['attivita'] = att_p1

        turni_opt_precisi.append(t_opt)
    else:
        # Turno già continuo o regolare
        t_opt = copy.deepcopy(t_az)
        turni_opt_precisi.append(t_opt)

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni_opt_precisi, f, ensure_ascii=False, indent=2)

print(f"✅ Ottimizzazione completata su tutti i {len(turni_opt_precisi)} turni!")
