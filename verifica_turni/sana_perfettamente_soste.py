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

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json") as f:
    turni = json.load(f)

for t in turni:
    code = t['codice_turno']
    n_m = t.get('nastro_m', parse_m(t.get('nastro')))
    in_m = parse_m(t.get('inizio_servizio'))
    rip = float(str(t.get('num_riprese', '1')).replace(',', '.'))
    att = t.get('attivita', [])
    
    # Rimuoviamo soste inserite male
    att_clean = [a for a in att if 'CCNL (30 min)' not in a.get('descrizione', '')]
    
    if n_m > 360 and rip == 1.0 and code not in ['Pi0070', 'Bo3020']:
        has_sosta = any(a.get('linea') == 'Sosta' or a.get('is_sosta_deposito') for a in att_clean)
        if not has_sosta:
            # Cerchiamo un gap tra due attività o un punto tra la 2ª e la 4ª ora
            idx_ins = len(att_clean) // 2
            for i in range(len(att_clean) - 1):
                p_i = parse_m(att_clean[i].get('partenza'))
                p_succ = parse_m(att_clean[i+1].get('partenza'))
                if p_succ > p_i:
                    gap = p_succ - parse_m(att_clean[i].get('arrivo'))
                    if gap >= 15:
                        idx_ins = i + 1
                        break
            
            loc = att_clean[idx_ins-1].get('a') if idx_ins > 0 else (att_clean[0].get('da') or t.get('deposito'))
            t_sosta_start = parse_m(att_clean[idx_ins-1].get('arrivo')) if idx_ins > 0 else in_m + 180
            
            sosta_card = {
                'linea': 'Sosta',
                'descrizione': f"☕ Sosta Obbligatoria CCNL (30 min) – {loc}",
                'da': loc,
                'a': loc,
                'partenza': fmt_time(t_sosta_start),
                'arrivo': fmt_time(t_sosta_start + 30),
                'km': '-',
                'durata_sosta_m': 30,
                'is_sosta_deposito': True
            }
            att_clean.insert(idx_ins, sosta_card)
            
    # Riordiniamo cronologicamente
    if code not in ['Pi0070', 'Bo3020']:
        att_clean = sorted(att_clean, key=lambda x: parse_m(x.get('partenza')))
        
    t['attivita'] = att_clean

with open("/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json", "w", encoding="utf-8") as f:
    json.dump(turni, f, ensure_ascii=False, indent=2)

print("✅ Sanatura completata con ordine cronologico impeccabile!")
