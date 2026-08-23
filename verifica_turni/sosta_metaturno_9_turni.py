#!/usr/bin/env python3
import json

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

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    code = t['codice_turno']
    if code in ['Ba3510', 'Ca0070', 'Pe0240', 'To0340', 'To0350', 'To0360', 'To0640', 'To0660', 'To0680']:
        in_m = parse_m(t['inizio_servizio'])
        att = t['attivita']
        corse = [a for a in att if a.get('linea') != 'Sosta' and 'chiusura' not in a.get('descrizione', '').lower() and 'disponibilità' not in a.get('descrizione', '').lower()]
        
        timeline = []
        curr_m = in_m
        
        # Presa servizio
        if corse:
            p1_m = parse_m(corse[0].get('partenza'))
            if p1_m > curr_m:
                timeline.append({
                    'linea': 'Disp',
                    'descrizione': f"Presa servizio e controllo livelli – {t.get('deposito')} Deposito",
                    'da': f"{t.get('deposito')} Deposito",
                    'a': f"{t.get('deposito')} Deposito",
                    'partenza': fmt_time(curr_m),
                    'arrivo': fmt_time(p1_m),
                    'km': '-'
                })
                curr_m = p1_m
                
        # Inserimento corse con sosta a metà turno (dopo la 1ª o 2ª corsa)
        sosta_fatta = False
        for i in range(len(corse)):
            p_i = parse_m(corse[i].get('partenza'))
            arr_i = parse_m(corse[i].get('arrivo'))
            
            if p_i > curr_m:
                gap = p_i - curr_m
                if gap >= 30 and not sosta_fatta:
                    timeline.append({
                        'linea': 'Sosta',
                        'descrizione': f"☕ Sosta Obbligatoria CCNL (30 min) – Capolinea / Deposito",
                        'da': timeline[-1].get('a') if timeline else 'Deposito',
                        'a': timeline[-1].get('a') if timeline else 'Deposito',
                        'partenza': fmt_time(curr_m),
                        'arrivo': fmt_time(curr_m + 30),
                        'km': '-',
                        'durata_sosta_m': 30,
                        'is_sosta_deposito': True
                    })
                    curr_m += 30
                    sosta_fatta = True
                    gap -= 30
                    
                if gap > 0:
                    timeline.append({
                        'linea': 'Sosta',
                        'descrizione': f"☕ Sosta / Stacco al Deposito ({gap}m)",
                        'da': timeline[-1].get('a') if timeline else 'Deposito',
                        'a': timeline[-1].get('a') if timeline else 'Deposito',
                        'partenza': fmt_time(curr_m),
                        'arrivo': fmt_time(p_i),
                        'km': '-',
                        'durata_sosta_m': gap,
                        'is_sosta_deposito': True
                    })
                    
            timeline.append(corse[i])
            curr_m = arr_i
            
            # Se dopo la 1ª corsa c'è arrivo al capolinea e non abbiamo ancora fatto sosta
            if not sosta_fatta and (curr_m - in_m) <= 240:
                timeline.append({
                    'linea': 'Sosta',
                    'descrizione': f"☕ Sosta Obbligatoria CCNL (30 min) – Capolinea / Deposito",
                    'da': corse[i].get('a') or 'Deposito',
                    'a': corse[i].get('a') or 'Deposito',
                    'partenza': fmt_time(curr_m),
                    'arrivo': fmt_time(curr_m + 30),
                    'km': '-',
                    'durata_sosta_m': 30,
                    'is_sosta_deposito': True
                })
                curr_m += 30
                sosta_fatta = True

        target_fin_m = in_m + 390
        if curr_m < target_fin_m - 10:
            timeline.append({
                'linea': 'Disp',
                'descrizione': f"Presenza e disponibilità operativa – {t.get('deposito')} Deposito",
                'da': f"{t.get('deposito')} Deposito",
                'a': f"{t.get('deposito')} Deposito",
                'partenza': fmt_time(curr_m),
                'arrivo': fmt_time(target_fin_m - 10),
                'km': '-'
            })
            curr_m = target_fin_m - 10
            
        fin_m = curr_m + 10
        timeline.append({
            'linea': 'Disp',
            'descrizione': f"Chiusura turno continuo – {t.get('deposito')} Deposito",
            'da': f"{t.get('deposito')} Deposito",
            'a': f"{t.get('deposito')} Deposito",
            'partenza': fmt_time(curr_m),
            'arrivo': fmt_time(fin_m),
            'km': '-'
        })
        
        n_m = fin_m - in_m if fin_m >= in_m else (1440 - in_m + fin_m)
        t['fine_servizio'] = fmt_time(fin_m)
        t['nastro'] = f"{n_m/60:.2f}"
        t['nastro_str'] = fmt_durata(n_m)
        t['nastro_m'] = n_m
        t['ore_lavoro'] = f"{n_m/60:.2f}"
        t['olg_str'] = fmt_durata(n_m)
        t['olg_m'] = n_m
        t['attivita'] = timeline

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ Soste a metà turno inserite su tutti i turni!")
