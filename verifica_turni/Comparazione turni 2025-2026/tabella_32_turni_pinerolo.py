#!/usr/bin/env python3
import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = {t['codice_turno']: t for t in turni if t['codice_turno'].startswith('Pi')}

def parse_m(t_str):
    if not t_str: return 0
    p = str(t_str).strip().replace('.', ':').replace(',', ':').split(':')
    if len(p) == 1: return int(float(p[0])) * 60
    return int(p[0]) * 60 + int(p[1])

def fmt_hm(m):
    return f"{int(m)//60}h {int(m)%60:02d}m"

# Dati Proposta
proposta = {}
for c, t in pinerolo.items():
    # default invariato
    in_s = t['attivita'][0]['partenza'] if t.get('attivita') else t['inizio_servizio']
    out_s = t['attivita'][-1]['arrivo'] if t.get('attivita') else t['fine_servizio']
    proposta[c] = {
        'orario': f"{in_s} – {out_s}",
        'nastro': parse_m(t['nastro']),
        'olg': parse_m(t['ore_lavoro']),
        'rip': int(float(str(t['num_riprese']).replace(',', '.'))),
        'stato': 'Invariato Regolare'
    }

# Aggiornamento turni modificati/scambiati
modifiche_dettaglio = {
    'Pi0080': {'orario': '12:40 – 19:30', 'nastro': 410, 'olg': 385, 'rip': 1, 'stato': '🟢 Pomeridiano Continuo (-5h40 Nastro)'},
    'Pi0370': {'orario': '07:00 – 11:45', 'nastro': 285, 'olg': 285, 'rip': 1, 'stato': '🟢 Mattinale Continuo (Zero Stacchi)'},
    'Pi0130': {'orario': '06:35 – 15:35', 'nastro': 540, 'olg': 325, 'rip': 2, 'stato': '🟢 Spezzato Compatto (-3h30 Nastro)'},
    'Pi0190': {'orario': '15:50 – 23:01', 'nastro': 431, 'olg': 450, 'rip': 1, 'stato': '🟢 Serale Potenziato (+1h44 OLG)'},
    'Pi0210': {'orario': '14:55 – 19:25', 'nastro': 270, 'olg': 270, 'rip': 1, 'stato': '🟢 Pomeridiano Continuo (-8h00 Nastro)'},
    'Pi0470': {'orario': '05:00 – 15:10', 'nastro': 610, 'olg': 410, 'rip': 2, 'stato': '🟢 Spezzato Compatto (+1h25 OLG)'},
    'Pi0580': {'orario': '13:04 – 19:10', 'nastro': 366, 'olg': 345, 'rip': 1, 'stato': '🟢 Pomeridiano Continuo (-6h24 Nastro)'},
    'Pi0290': {'orario': '05:33 – 14:20', 'nastro': 527, 'olg': 344, 'rip': 3, 'stato': '⚪ Regolare Invariato'},
    'Pi0560': {'orario': '13:20 – 17:38', 'nastro': 258, 'olg': 258, 'rip': 1, 'stato': '🟢 Pomeridiano Continuo (-7h50 Nastro)'},
    'Pi0280': {'orario': '05:30 – 16:17', 'nastro': 647, 'olg': 435, 'rip': 2, 'stato': '🟢 Spezzato Potenziato (+2h08 OLG)'},
    'Pi0260': {'orario': '06:49 – 15:50', 'nastro': 541, 'olg': 300, 'rip': 2, 'stato': '🟢 Spezzato Compatto (-3h01 Nastro)'},
    'Pi0020': {'orario': '05:45 – 14:32', 'nastro': 527, 'olg': 350, 'rip': 3, 'stato': '⚪ Regolare Invariato'}
}

for c, val in modifiche_dettaglio.items():
    proposta[c] = val

print("=== TABELLA CONFRONTO COMPLETO: 32 TURNI PINEROLO ===")
print(f"{'Cod.':6s} | {'Nome Turno Azienda':22s} | {'Nastro Az.':10s} | {'Nastro Prop.':12s} | {'OLG Az.':8s} | {'OLG Prop.':10s} | {'Stato / Note'}")
print("-" * 110)

for c in sorted(pinerolo.keys()):
    t = pinerolo[c]
    p = proposta[c]
    
    n_az = parse_m(t['nastro'])
    n_pr = p['nastro']
    diff_n = n_pr - n_az
    diff_n_str = f"({diff_n:+d}m)" if diff_n != 0 else "="
    
    o_az = parse_m(t['ore_lavoro'])
    o_pr = p['olg']
    diff_o = o_pr - o_az
    diff_o_str = f"({diff_o:+d}m)" if diff_o != 0 else "="
    
    print(f"{c:6s} | {t['nome_turno'][:22]:22s} | {fmt_hm(n_az):10s} | {fmt_hm(n_pr):7s} {diff_n_str:5s} | {fmt_hm(o_az):8s} | {fmt_hm(o_pr):6s} {diff_o_str:5s} | {p['stato']}")
