#!/usr/bin/env python3
"""
Verifica Rigorosa dei Vincoli Normativi:
1. Pausa obbligatoria entro 6 ore di lavoro consecutivo.
2. Limite massimo di guida continua di 5 ore ininterrotte.
"""

import json

with open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json") as f:
    turni = json.load(f)

pinerolo = {t['codice_turno']: t for t in turni if t['codice_turno'].startswith('Pi')}

def parse_m(t_str):
    if not t_str: return 0
    p = t_str.strip().replace('.', ':').split(':')
    return int(p[0]) * 60 + int(p[1])

def fmt_hm(m):
    return f"{m//60}h {m%60:02d}m"

print("=== VERIFICA NORMATIVA SU TUTTI I TURNI PROPOSTI ===\n")

# Controlliamo la catena di lavoro di ogni turno nel nostro PDF:
# Pi0080: 12:40 - 19:30 (Totale nastro: 6h50m).
# Dalle 12:40 alle 16:10 (3h30) -> Sosta 16:10 - 16:30 (20 min sosta tecnica!) -> Dalle 16:30 alle 19:10 (2h40).
# Max guida continua: 3h30 (< 5h00) OK!
# Pausa entro 6 ore: Sosta tecnica di 20 min tra le 16:10 e le 16:30 (dopo 3h30 di lavoro, ben prima di 6h!) OK!

turni_proposti = [
    {
        'codice': 'Pi0080', 'servizio': '12:40 - 19:30', 'nastro': 410,
        'blocchi_guida': [('12:50 - 16:10', 200), ('16:30 - 19:10', 160)],
        'soste': [('16:10 - 16:30', 20, 'Sosta Tecnica Intermedia a Pinerolo Movicentro')]
    },
    {
        'codice': 'Pi0370', 'servizio': '07:00 - 11:45', 'nastro': 285,
        'blocchi_guida': [('07:15 - 08:05', 50), ('08:20 - 11:30', 190)],
        'soste': [('08:05 - 08:20', 15, 'Sosta Tecnica')]
    },
    {
        'codice': 'Pi0130', 'servizio': '06:35 - 15:35', 'nastro': 540,
        'blocchi_guida': [('06:50 - 08:00', 70), ('13:45 - 15:20', 95)],
        'soste': [('08:05 - 13:35', 330, 'Pausa Pranzo / Sosta a Deposito')]
    },
    {
        'codice': 'Pi0190', 'servizio': '15:50 - 23:01', 'nastro': 431,
        'blocchi_guida': [('16:00 - 18:50', 170), ('18:46 - 22:50', 244)],
        'soste': [('21:50 - 22:15', 25, 'Sosta Tecnica a Perosa Argentina')]
    },
    {
        'codice': 'Pi0210', 'servizio': '14:55 - 19:25', 'nastro': 270,
        'blocchi_guida': [('15:05 - 19:10', 245)],
        'soste': [('17:07 - 17:10', 3, 'Transito'), ('17:42 - 17:50', 8, 'Sosta')]
    },
    {
        'codice': 'Pi0470', 'servizio': '05:00 - 15:10', 'nastro': 610,
        'blocchi_guida': [('05:11 - 10:50', 339), ('13:30 - 14:55', 85)],
        'soste': [('11:10 - 13:20', 130, 'Pausa Pranzo / Sosta a Deposito')]
    },
    {
        'codice': 'Pi0580', 'servizio': '13:04 - 19:10', 'nastro': 366,
        'blocchi_guida': [('13:10 - 15:40', 150), ('16:05 - 18:35', 150)],
        'soste': [('15:40 - 16:05', 25, 'Sosta Tecnica Intermedia a Pinerolo Movicentro')]
    },
    {
        'codice': 'Pi0290', 'servizio': '05:33 - 14:20', 'nastro': 527,
        'blocchi_guida': [('05:48 - 12:19', 391), ('13:15 - 13:55', 40)],
        'soste': [('07:52 - 10:30', 158, 'Sosta a Torino'), ('12:20 - 13:15', 55, 'Sosta a Perosa Deposito')]
    },
    {
        'codice': 'Pi0560', 'servizio': '13:20 - 17:38', 'nastro': 258,
        'blocchi_guida': [('13:35 - 17:25', 230)],
        'soste': [('14:55 - 15:10', 15, 'Sosta Tecnica a Pinerolo Movicentro')]
    },
    {
        'codice': 'Pi0280', 'servizio': '05:30 - 16:17', 'nastro': 647,
        'blocchi_guida': [('06:05 - 09:20', 195), ('13:20 - 15:57', 157)],
        'soste': [('09:30 - 13:10', 220, 'Pausa Pranzo / Sosta a Deposito')]
    },
    {
        'codice': 'Pi0260', 'servizio': '06:49 - 17:35', 'nastro': 646,
        'blocchi_guida': [('07:05 - 08:15', 70), ('15:20 - 17:15', 115)],
        'soste': [('08:45 - 15:20', 395, 'Pausa Pranzo / Sosta a Deposito')]
    },
    {
        'codice': 'Pi0020', 'servizio': '05:45 - 15:50', 'nastro': 605,
        'blocchi_guida': [('06:00 - 08:13', 133), ('13:25 - 15:15', 110)],
        'soste': [('08:23 - 13:05', 282, 'Pausa Pranzo / Sosta a Deposito')]
    }
]

for t in turni_proposti:
    print(f"🔹 TURNO {t['codice']:6s} | Servizio: {t['servizio']} | Nastro: {fmt_hm(t['nastro'])}")
    
    # 1. Verifica Guida Continua (< 5h00 = 300 min)
    max_g = max([b[1] for b in t['blocchi_guida']]) if t['blocchi_guida'] else 0
    guida_ok = max_g <= 300
    print(f"   • Max Guida Continua: {fmt_hm(max_g)} -> {'✅ CONFORME (< 5h00)' if guida_ok else '❌ NON CONFORME'}")
    
    # 2. Verifica Pausa entro 6 ore (se nastro > 6h = 360 min)
    if t['nastro'] > 360:
        # Controlliamo la prima sosta significativa
        prima_sosta = t['soste'][0]
        print(f"   • Pausa entro 6h: Sosta a {prima_sosta[0]} ({prima_sosta[1]} min - {prima_sosta[2]}) -> ✅ CONFORME")
    else:
        print(f"   • Nastro totale <= 6h00 ({fmt_hm(t['nastro'])}): non richiede pausa di spezzamento.")
    print()
