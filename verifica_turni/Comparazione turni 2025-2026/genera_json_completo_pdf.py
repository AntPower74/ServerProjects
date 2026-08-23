#!/usr/bin/env python3
import fitz
import re
import json

PDF_PATH = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini lun-ven 2026.pdf"
JSON_OUT = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json"

DEP_CORRETTO = {
    'CA': 'Caselle Aeroporto (Parcheggio P7)',
    'BA': 'Barge (BAG - PARCHEGGIO)',
    'BO': 'Bobbio Pellice Deposito',
    'PI': 'Pinerolo Deposito',
    'PE': 'Perosa Deposito',
    'TO': 'Torino (Grugliasco / Rimessa)',
    'SU': 'Susa Deposito',
    'SA': 'Salbertrand / Saluzzo Deposito',
    'PT': 'Pont Saint Martin Deposito',
    'IV': 'Ivrea Deposito',
    'LU': 'Luserna S.Giovanni Deposito',
    'PB': 'Piobesi / Torino De Cristoforis',
    'FT': 'Torino Rimessa / Pinerolo'
}

doc = fitz.open(PDF_PATH)
turni = []

for page_idx in range(len(doc)):
    txt = doc[page_idx].get_text()
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    
    m_code = re.search(r'Cartellino di marcia del turno:\s*\n\s*([A-Za-z0-9_]+)', txt)
    code = m_code.group(1) if m_code else f"Turno_{page_idx+1}"
    
    m_name = re.search(r'TURNO\s+([^\n]+)', txt)
    name = m_name.group(1) if m_name else ''
    
    m_in = re.search(r'Ora inizio turno\s*:\s*\n\s*(\d{1,2}[.:]\d{2})', txt)
    m_out = re.search(r'Ora fine turno\s*:\s*\n\s*(\d{1,2}[.:]\d{2})', txt)
    
    in_s = m_in.group(1).replace('.', ':') if m_in else ''
    out_s = m_out.group(1).replace('.', ':') if m_out else ''
    
    # Parametri CCNL
    nastro = ""
    ore_lav = ""
    ore_guida = ""
    sosta_100 = "0,00"
    sosta_12 = "0,00"
    riprese = "1,00"
    
    for i, l in enumerate(lines):
        if 'ORE LAVORO GIORNALIERO' in l and i+1 < len(lines):
            ore_lav = lines[i+1].replace('.', ':')
        elif 'Nastro del turno' in l and i+1 < len(lines):
            nastro = lines[i+1].replace('.', ':')
        elif 'ORE DI GUIDA COMPLESSIVA' in l and i+1 < len(lines):
            ore_guida = lines[i+1].replace('.', ':')
        elif 'Sosta al 100%' in l and i+1 < len(lines):
            sosta_100 = lines[i+1]
        elif 'Sosta al 12%' in l and i+1 < len(lines):
            sosta_12 = lines[i+1]
        elif 'NUMERO RIPRESE' in l and i+1 < len(lines):
            riprese = lines[i+1]

    # Parsing attività
    attivita = []
    # Usiamo blocchi o regex per estrarre le corse
    # Ciascuna riga nel cartellino ha: Descrizione, Partenza, Arrivo, Km, Linea, Guida, Trasf
    # Cerchiamo pattern di orari consecutivi
    for i in range(len(lines)):
        l = lines[i]
        # Se troviamo una descrizione di tratta o attività
        if ' - ' in l or 'Controllo livelli' in l or 'Pulizia Interna' in l or 'Disponibilità' in l:
            # cerca orari partenza e arrivo nelle righe successive
            p_time = ""
            a_time = ""
            km_val = ""
            lin_val = ""
            g_val = ""
            tr_val = ""
            
            for k in range(i+1, min(len(lines), i+8)):
                candidate = lines[k]
                m_time = re.match(r'^\s*(\d{1,2})[.:](\d{2})\s*$', candidate)
                if m_time:
                    hh = int(m_time.group(1))
                    mm = int(m_time.group(2))
                    t_str = f"{hh:02d}:{mm:02d}"
                    if not p_time:
                        p_time = t_str
                    elif not a_time:
                        a_time = t_str
                elif re.match(r'^\s*\d+[,\.]\d+\s*$', candidate) and not km_val:
                    km_val = candidate
                elif re.match(r'^(Disp|Trasf|\d{1,6}|[A-Z0-9_-]+)$', candidate) and not lin_val:
                    lin_val = candidate

            if p_time and a_time:
                da = l.split(' - ')[0].strip() if ' - ' in l else l
                a_loc = l.split(' - ')[1].strip() if ' - ' in l else ''
                
                if 'Controllo livelli' in l:
                    lin_val = 'Disp'
                elif 'Pulizia Interna' in l:
                    lin_val = 'Disp'
                elif not lin_val and 'Trasf' in txt:
                    lin_val = 'Trasf'
                
                # Normalizza codice linea
                if lin_val.startswith('000'):
                    lin_val = str(int(lin_val))
                elif lin_val.startswith('00'):
                    lin_val = str(int(lin_val))

                attivita.append({
                    'linea': lin_val or 'Linea',
                    'descrizione': l,
                    'da': da,
                    'a': a_loc,
                    'partenza': p_time,
                    'arrivo': a_time,
                    'guida': '',
                    'trasf': '',
                    'km': km_val or '-'
                })

    dep_pfx = code[:2].upper()
    dep_name = DEP_CORRETTO.get(dep_pfx, 'Pinerolo Deposito')

    turni.append({
        'pagina': page_idx + 1,
        'codice_turno': code,
        'nome_turno': name,
        'deposito': dep_name,
        'inizio_servizio': in_s,
        'fine_servizio': out_s,
        'nastro': nastro,
        'ore_lavoro': ore_lav,
        'ore_guida': ore_guida,
        'sosta_100': sosta_100,
        'sosta_12': sosta_12,
        'num_riprese': riprese,
        'attivita': attivita
    })

with open(JSON_OUT, 'w', encoding='utf-8') as f:
    json.dump(turni, f, indent=2, ensure_ascii=False)

print(f"✅ Estratti con successo {len(turni)} turni in {JSON_OUT}")
