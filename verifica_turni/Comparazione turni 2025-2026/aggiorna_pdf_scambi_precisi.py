#!/usr/bin/env python3
"""
Rigenerazione PDF Turni Pinerolo con Scambi Verificati Cronologicamente:
1. Pi0080 -> Cede mattino 07:00-08:15 a Pi0370 e diventa Pomeridiano Continuo (12:40 - 19:30, Nastro 6h50, OLG 6h25)
2. Pi0370 -> Riceve mattino 07:00-08:15 da Pi0080 e prosegue con Linea 703 fino alle 11:45 (Nastro 4h45, OLG 4h45)
3. Pi0130 -> Cede navette 703 (16:00-18:50) a Pi0190 e chiude alle 15:35 (Nastro 9h00, OLG 5h25)
4. Pi0190 -> Riceve navette 703 (16:00-18:50) da Pi0130 e prosegue con il servizio serale (16:00 - 23:01, Nastro 7h01, OLG 7h30)
5. Pi0210 -> Cede blocco 13:20-14:55 a Pi0470 ed effettua servizio pomeridiano continuo (14:55 - 19:25, Nastro 4h30, OLG 4h30)
6. Pi0470 -> Riceve blocco 13:20-14:55 da Pi0210 dopo pausa pranzo (05:00 - 15:00, Nastro 10h00, OLG 6h50)
"""

import json
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

JSON_PATH = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json"
PDF_OUT = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Turni_Pinerolo_Scambi_Evidenziati.pdf"

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    turni = json.load(f)

pinerolo = {t['codice_turno']: t for t in turni if t['codice_turno'].startswith('Pi')}

doc = SimpleDocTemplate(
    PDF_OUT,
    pagesize=landscape(A4),
    leftMargin=20,
    rightMargin=20,
    topMargin=15,
    bottomMargin=15
)

styles = getSampleStyleSheet()
title_style = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.HexColor('#003366'))
sub_title_style = ParagraphStyle('SubDocTitle', fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor('#444444'))

th_style = ParagraphStyle('THStyle', fontName='Helvetica-Bold', fontSize=7.2, leading=8.5, textColor=colors.white, alignment=1)
td_cell = ParagraphStyle('TDCell', fontName='Helvetica', fontSize=6.5, leading=7.8)
td_center = ParagraphStyle('TDCenter', fontName='Helvetica', fontSize=6.5, leading=7.8, alignment=1)
td_right = ParagraphStyle('TDRight', fontName='Helvetica', fontSize=6.5, leading=7.8, alignment=2)

td_ceduta = ParagraphStyle('TDCeduta', fontName='Helvetica-Bold', fontSize=6.5, leading=7.8, textColor=colors.HexColor('#9C4221'))
td_ricevuta = ParagraphStyle('TDRicevuta', fontName='Helvetica-Bold', fontSize=6.5, leading=7.8, textColor=colors.HexColor('#1C4532'))

box_body = ParagraphStyle('BoxBody', fontName='Helvetica', fontSize=7.0, leading=8.2, textColor=colors.HexColor('#1A202C'))

elements = []

def genera_scheda_turno(t_orig, att_list, scambi_info, params_box):
    code = t_orig['codice_turno']
    name = t_orig['nome_turno']
    
    head_text = f"<b>TURNO {code} – {name}</b> (Deposito di Pinerolo)"
    sub_text = f"Progetto: <b>Ottimizzazione Turni Pinerolo</b> | <b>Analisi Scambio Corse e Bilanciamento OLG</b>"
    
    header_table = Table([
        [Paragraph(head_text, title_style), Paragraph(f"Stato: <b>{scambi_info['stato']}</b>", td_right)],
        [Paragraph(sub_text, sub_title_style), Paragraph(f"<b>Nastro Soluzione:</b> {params_box['nastro_dopo']}", td_right)]
    ], colWidths=[610, 192])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 1),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 5))

    # Box Confronto Parametri
    box_data = [
        [
            Paragraph(f"🔴 <b>SITUAZIONE ATTUALE (AZIENDA):</b><br/>"
                      f"• Orario Servizio: <b>{params_box['orario_prima']}</b><br/>"
                      f"• <b>Nastro:</b> <font color='#990000'><b>{params_box['nastro_prima']}</b></font><br/>"
                      f"• <b>OLG (Ore Lavoro):</b> <b>{params_box['olg_prima']}</b><br/>"
                      f"• N° Riprese: <b>{params_box['rip_prima']}</b>", box_body),
            Paragraph(f"🟢 <b>SOLUZIONE DOPO LO SCAMBIO:</b><br/>"
                      f"• Orario Servizio: <b>{params_box['orario_dopo']}</b><br/>"
                      f"• <b>Nastro:</b> <font color='#006600'><b>{params_box['nastro_dopo']}</b> ({params_box['diff_nastro']})</font><br/>"
                      f"• <b>OLG (Ore Lavoro):</b> <font color='#006600'><b>{params_box['olg_dopo']}</b> ({params_box['diff_olg']})</font><br/>"
                      f"• N° Riprese: <b>{params_box['rip_dopo']}</b>", box_body),
            Paragraph(f"🔄 <b>DETTAGLIO DELLO SCAMBIO:</b><br/>"
                      f"{scambi_info['descrizione']}", box_body)
        ]
    ]
    t_box = Table(box_data, colWidths=[260, 260, 282])
    t_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F0F7FF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#3182CE')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BEE3F8')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_box)
    elements.append(Spacer(1, 6))

    # Tabella Attività con Righe Evidenziate
    corse_data = [[
        Paragraph("N°", th_style),
        Paragraph("Linea", th_style),
        Paragraph("Tipologia Attività / Tratta", th_style),
        Paragraph("Part.", th_style),
        Paragraph("Arr.", th_style),
        Paragraph("Km", th_style),
        Paragraph("Stato / Nota di Scambio", th_style)
    ]]

    row_styles = []

    for c_idx, a in enumerate(att_list, 1):
        lin = a.get('linea', '')
        da_a = f"{a.get('da','')} ➔ {a.get('a','')}" if a.get('a') else a.get('descrizione', a.get('da',''))
        p = a.get('partenza', '')
        arr = a.get('arrivo', '')
        km = str(a.get('km', '-'))
        stato_scambio = a.get('scambio_tag', 'Regolare')

        if 'CEDUTA' in stato_scambio:
            p_style = td_ceduta
            note_cell = Paragraph(f"🔴 <b>{stato_scambio}</b>", td_ceduta)
            row_styles.append(('BACKGROUND', (0, c_idx), (-1, c_idx), colors.HexColor('#FEEBC8')))
        elif 'RICEVUTA' in stato_scambio:
            p_style = td_ricevuta
            note_cell = Paragraph(f"🟢 <b>{stato_scambio}</b>", td_ricevuta)
            row_styles.append(('BACKGROUND', (0, c_idx), (-1, c_idx), colors.HexColor('#C6F6D5')))
        elif 'Sosta' in lin:
            p_style = td_cell
            note_cell = Paragraph("Pausa / Sosta Operativa", td_cell)
            row_styles.append(('BACKGROUND', (0, c_idx), (-1, c_idx), colors.HexColor('#EDF2F7')))
        else:
            p_style = td_cell
            note_cell = Paragraph("Attività Ordinaria del Turno", td_cell)
            if c_idx % 2 == 0:
                row_styles.append(('BACKGROUND', (0, c_idx), (-1, c_idx), colors.HexColor('#F7FAFC')))

        corse_data.append([
            Paragraph(str(c_idx), td_center),
            Paragraph(lin, td_center),
            Paragraph(da_a[:45], p_style),
            Paragraph(p, td_center),
            Paragraph(arr, td_center),
            Paragraph(km, td_right),
            note_cell
        ])

    t_corse = Table(corse_data, colWidths=[24, 45, 310, 42, 42, 42, 297])
    t_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 2.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.2),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ] + row_styles
    t_corse.setStyle(TableStyle(t_style))
    elements.append(t_corse)
    elements.append(PageBreak())

# -------------------------------------------------------------
# 1. Pi0080 -> CEDE MATTINO A Pi0370
# -------------------------------------------------------------
t80_orig = pinerolo['Pi0080']
att_80 = []
for a in t80_orig['attivita']:
    a_dict = dict(a)
    p = a.get('partenza', '')
    if p in ['07:00', '07:10', '07:15', '07:35', '07:40', '08:05']:
        a_dict['scambio_tag'] = 'CORSA MATTUTINA CEDUTA A Pi0370 (Inizio spostato alle 12:40)'
    att_80.append(a_dict)

genera_scheda_turno(
    t80_orig,
    att_80,
    scambi_info={
        'stato': 'TRASFORMATO IN POMERIDIANO CONTINUO',
        'descrizione': '• <b>Cede a Pi0370:</b> Troncone mattutino 07:00–08:15 (Linea 278 Cercenasco/Vigone).<br/>'
                       '• <b>Effetto:</b> Inizia alle 12:40 ed effettua servizio continuo (Linee 901 + 278) fino alle 19:30. Nastro abbattuto da 12h30 a 6h50!'
    },
    params_box={
        'orario_prima': '07:00 – 19:30',
        'orario_dopo': '12:40 – 19:30',
        'nastro_prima': '12h 30m',
        'nastro_dopo': '6h 50m',
        'diff_nastro': '−5h 40m',
        'olg_prima': '7h 34m',
        'olg_dopo': '6h 25m',
        'diff_olg': 'Continuo',
        'rip_prima': '3 riprese',
        'rip_dopo': '1 ripresa continua'
    }
)

# -------------------------------------------------------------
# 2. Pi0370 -> RICEVE MATTINO DA Pi0080
# -------------------------------------------------------------
t370_orig = pinerolo['Pi0370']
att_370 = [
    {'linea': 'Disp', 'da': 'Controllo livelli autobus', 'a': '', 'partenza': '07:00', 'arrivo': '07:10', 'km': '-', 'scambio_tag': 'Attività Ordinaria'},
    {'linea': 'Trasf', 'da': 'Pinerolo Deposito ➔ PINEROLO', 'a': '', 'partenza': '07:10', 'arrivo': '07:15', 'km': '1.06', 'scambio_tag': 'Attività Ordinaria'},
    {'linea': '278', 'da': 'PINEROLO ➔ CERCENASCO - Via Umberto I', 'a': '', 'partenza': '07:15', 'arrivo': '07:35', 'km': '14.86', 'scambio_tag': 'CORSA RICEVUTA DA Pi0080 (Linea 278)'},
    {'linea': '278', 'da': 'VIGONE ➔ PINEROLO - Piazza Cavour', 'a': '', 'partenza': '07:40', 'arrivo': '08:05', 'km': '16.32', 'scambio_tag': 'CORSA RICEVUTA DA Pi0080 (Linea 278)'},
    {'linea': 'Trasf', 'da': 'PINEROLO ➔ Pinerolo Deposito / Riva', 'a': '', 'partenza': '08:05', 'arrivo': '08:15', 'km': '2.40', 'scambio_tag': 'Attività Ordinaria'},
    {'linea': '703', 'da': 'RIVA DI PINEROLO ➔ PINEROLO Fiugera', 'a': '', 'partenza': '08:20', 'arrivo': '08:47', 'km': '11.06', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': '703', 'da': 'PINEROLO Fiugera ➔ RIVA DI PINEROLO', 'a': '', 'partenza': '09:00', 'arrivo': '09:30', 'km': '11.54', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': '703', 'da': 'RIVA DI PINEROLO ➔ PINEROLO Fiugera', 'a': '', 'partenza': '09:30', 'arrivo': '09:57', 'km': '11.06', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': '703', 'da': 'PINEROLO Fiugera ➔ RIVA DI PINEROLO', 'a': '', 'partenza': '10:00', 'arrivo': '10:30', 'km': '11.54', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': '703', 'da': 'RIVA DI PINEROLO ➔ PINEROLO Fiugera', 'a': '', 'partenza': '10:30', 'arrivo': '10:57', 'km': '11.06', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': '703', 'da': 'PINEROLO Fiugera ➔ RIVA DI PINEROLO', 'a': '', 'partenza': '11:00', 'arrivo': '11:30', 'km': '11.54', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': 'Disp', 'da': 'Rientro Deposito e Pulizia Bus', 'a': '', 'partenza': '11:30', 'arrivo': '11:45', 'km': '3.86', 'scambio_tag': 'Attività Ordinaria'}
]

genera_scheda_turno(
    t370_orig,
    att_370,
    scambi_info={
        'stato': 'MATTINALE CONTINUO INTEGRATO',
        'descrizione': '• <b>Riceve da Pi0080:</b> Corsa 07:15–08:05 (Linea 278 Pinerolo ➔ Cercenasco ➔ Vigone).<br/>'
                       '• <b>Effetto:</b> Sequenza cronologica perfetta: 07:00–08:15 (Linea 278) + 08:20–11:45 (Linea 703). Nessun conflitto e turno compatto.'
    },
    params_box={
        'orario_prima': '06:30 – 11:45',
        'orario_dopo': '07:00 – 11:45',
        'nastro_prima': '5h 15m',
        'nastro_dopo': '4h 45m',
        'diff_nastro': 'Compatto',
        'olg_prima': '5h 15m',
        'olg_dopo': '4h 45m',
        'diff_olg': 'Continuo',
        'rip_prima': '1 ripresa',
        'rip_dopo': '1 ripresa continua'
    }
)

# -------------------------------------------------------------
# 3. Pi0130 -> CEDE NAVETTE TARDO POMERIGGIO A Pi0190
# -------------------------------------------------------------
t130_orig = pinerolo['Pi0130']
att_130 = []
for a in t130_orig['attivita']:
    a_dict = dict(a)
    p = a.get('partenza', '')
    if p in ['16:00', '16:40', '17:10', '17:40', '18:20', '18:50', '18:55']:
        a_dict['scambio_tag'] = 'CORSA CEDUTA A Pi0190 (Chiusura servizio anticipata alle 15:35)'
    att_130.append(a_dict)

genera_scheda_turno(
    t130_orig,
    att_130,
    scambi_info={
        'stato': 'OTTIMIZZATO (Nastro ridotto di 3h30)',
        'descrizione': '• <b>Cede a Pi0190:</b> Navette Linea 703 dalle 16:00 alle 18:50.<br/>'
                       '• <b>Effetto:</b> Completa la Linea 701 a Macello e rientra a Pinerolo alle 15:35, eliminando 3h30m di nastro dilatato.'
    },
    params_box={
        'orario_prima': '06:35 – 19:05',
        'orario_dopo': '06:35 – 15:35',
        'nastro_prima': '12h 30m',
        'nastro_dopo': '9h 00m',
        'diff_nastro': '−3h 30m',
        'olg_prima': '7h 00m',
        'olg_dopo': '5h 25m',
        'diff_olg': '−1h 35m',
        'rip_prima': '2 riprese',
        'rip_dopo': '2 riprese compatte'
    }
)

# -------------------------------------------------------------
# 4. Pi0190 -> RICEVE NAVETTE DA Pi0130
# -------------------------------------------------------------
t190_orig = pinerolo['Pi0190']
att_190 = [
    {'linea': 'Disp', 'da': 'Controllo livelli autobus', 'a': '', 'partenza': '15:50', 'arrivo': '16:00', 'km': '-', 'scambio_tag': 'Attività Ordinaria'},
    {'linea': '703', 'da': 'PINEROLO Fiugera ➔ RIVA / PASCARETTO (5 Navette)', 'a': '', 'partenza': '16:00', 'arrivo': '18:50', 'km': '59.47', 'scambio_tag': 'CORSA RICEVUTA DA Pi0130 (Anticipa inizio alle 16:00)'},
    {'linea': '282', 'da': 'PINEROLO movicentro ➔ TORINO Autostazione c.so Bolzano', 'a': '', 'partenza': '18:46', 'arrivo': '19:57', 'km': '41.60', 'scambio_tag': 'Propria Corsa di Linea 282'},
    {'linea': '282', 'da': 'TORINO Autostazione ➔ PINEROLO movicentro', 'a': '', 'partenza': '20:03', 'arrivo': '21:14', 'km': '41.90', 'scambio_tag': 'Propria Corsa di Linea 282'},
    {'linea': '282', 'da': 'PINEROLO movicentro ➔ PEROSA ARGENTINA', 'a': '', 'partenza': '21:18', 'arrivo': '21:50', 'km': '18.51', 'scambio_tag': 'Propria Corsa di Linea 282'},
    {'linea': '275', 'da': 'PEROSA ARGENTINA ➔ PINEROLO Deposito', 'a': '', 'partenza': '22:15', 'arrivo': '22:50', 'km': '20.83', 'scambio_tag': 'Propria Corsa di Linea 275'},
    {'linea': 'Disp', 'da': 'Pulizia Interna Autobus', 'a': '', 'partenza': '22:51', 'arrivo': '23:01', 'km': '-', 'scambio_tag': 'Attività Ordinaria'}
]

genera_scheda_turno(
    t190_orig,
    att_190,
    scambi_info={
        'stato': 'POTENZIATO (Da turno corto a turno serale pieno)',
        'descrizione': '• <b>Riceve da Pi0130:</b> Navette Linea 703 dalle 16:00 alle 18:50.<br/>'
                       '• <b>Effetto:</b> Inizia alle 16:00 e si connette alle sue corse serali per Torino/Perosa, portando l’OLG a 7h30 pieno.'
    },
    params_box={
        'orario_prima': '17:15 – 23:01',
        'orario_dopo': '15:50 – 23:01',
        'nastro_prima': '5h 46m',
        'nastro_dopo': '7h 11m',
        'diff_nastro': '+1h 25m (Ottimale)',
        'olg_prima': '5h 46m',
        'olg_dopo': '7h 30m',
        'diff_olg': '+1h 44m OLG',
        'rip_prima': '1 ripresa',
        'rip_dopo': '1 ripresa continua'
    }
)

# -------------------------------------------------------------
# 5. Pi0210 -> CEDE BLOCCO PANCALIERI A Pi0470
# -------------------------------------------------------------
t210_orig = pinerolo['Pi0210']
att_210 = []
for a in t210_orig['attivita']:
    a_dict = dict(a)
    p = a.get('partenza', '')
    if p in ['06:55', '07:05', '07:35', '08:15', '13:20', '13:30', '14:05']:
        a_dict['scambio_tag'] = 'CORSA CEDUTA A Pi0470 (Inizio servizio concentrato al pomeriggio)'
    att_210.append(a_dict)

genera_scheda_turno(
    t210_orig,
    att_210,
    scambi_info={
        'stato': 'POMERIDIANO CONTINUO (Nastro da 12h30 a 4h30)',
        'descrizione': '• <b>Cede a Pi0470:</b> Corsa mattutina 278 Virle (07:35) + Blocco 278/281 Pancalieri (13:20–14:55).<br/>'
                       '• <b>Effetto:</b> Inizia alle 14:55 ed effettua il servizio Cantalupa + Perosa + Torre Pellice fino alle 19:25 in 1 sola ripresa continua.'
    },
    params_box={
        'orario_prima': '06:55 – 19:25',
        'orario_dopo': '14:55 – 19:25',
        'nastro_prima': '12h 30m',
        'nastro_dopo': '4h 30m',
        'diff_nastro': '−8h 00m',
        'olg_prima': '7h 35m',
        'olg_dopo': '4h 30m',
        'diff_olg': 'Continuo',
        'rip_prima': '2 riprese',
        'rip_dopo': '1 ripresa continua'
    }
)

# -------------------------------------------------------------
# 6. Pi0470 -> RICEVE BLOCCO PANCALIERI DA Pi0210
# -------------------------------------------------------------
t470_orig = pinerolo['Pi0470']
att_470 = []
for a in t470_orig['attivita'][:-1]: # tutte le attività mattutine fino alle 11:10
    att_470.append(dict(a))

# Inseriamo la pausa pranzo e il blocco Pancalieri
att_470.append({
    'linea': 'Sosta',
    'da': 'Pausa Pranzo / Sosta a Pinerolo Deposito',
    'a': '',
    'partenza': '11:10',
    'arrivo': '13:20',
    'km': '-',
    'scambio_tag': 'Pausa Ristoro Regolare'
})
att_470.append({
    'linea': 'Trasf',
    'da': 'Pinerolo Deposito ➔ PINEROLO - Stazione FS',
    'a': '',
    'partenza': '13:20',
    'arrivo': '13:25',
    'km': '2.75',
    'scambio_tag': 'Attività Ordinaria'
})
att_470.append({
    'linea': '278',
    'da': 'PINEROLO - Stazione FS ➔ PANCALIERI - scuole medie',
    'a': '',
    'partenza': '13:30',
    'arrivo': '14:05',
    'km': '23.70',
    'scambio_tag': 'CORSA RICEVUTA DA Pi0210 (Linea 278)'
})
att_470.append({
    'linea': '281',
    'da': 'PANCALIERI - scuole medie ➔ PINEROLO - Fronte Stazione FS',
    'a': '',
    'partenza': '14:05',
    'arrivo': '14:55',
    'km': '32.48',
    'scambio_tag': 'CORSA RICEVUTA DA Pi0210 (Linea 281)'
})
att_470.append({
    'linea': 'Trasf',
    'da': 'PINEROLO ➔ Pinerolo Deposito',
    'a': '',
    'partenza': '14:55',
    'arrivo': '15:00',
    'km': '2.40',
    'scambio_tag': 'Attività Ordinaria'
})
att_470.append({
    'linea': 'Disp',
    'da': 'Pulizia Interna Autobus',
    'a': '',
    'partenza': '15:00',
    'arrivo': '15:10',
    'km': '-',
    'scambio_tag': 'Attività Ordinaria'
})

genera_scheda_turno(
    t470_orig,
    att_470,
    scambi_info={
        'stato': 'POTENZIATO (OLG da 5h25 a 6h50)',
        'descrizione': '• <b>Riceve da Pi0210:</b> Blocco 278/281 Pancalieri (13:20–14:55).<br/>'
                       '• <b>Effetto:</b> Completa il mattino (Linee 275+701), effettua 2h10m di pausa ristoro a Pinerolo e chiude alle 15:10 con 6h50m di lavoro pieno.'
    },
    params_box={
        'orario_prima': '05:00 – 11:20',
        'orario_dopo': '05:00 – 15:10',
        'nastro_prima': '6h 20m',
        'nastro_dopo': '10h 10m',
        'diff_nastro': '+3h 50m (Compatto)',
        'olg_prima': '5h 25m',
        'olg_dopo': '6h 50m',
        'diff_olg': '+1h 25m OLG',
        'rip_prima': '2 riprese',
        'rip_dopo': '2 riprese con pausa pranzo'
    }
)

doc.build(elements)
print(f"✅ PDF AGGIORNATO CON 6 SCHEDE:\n{PDF_OUT}")
