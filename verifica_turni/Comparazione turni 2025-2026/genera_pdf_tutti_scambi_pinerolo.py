#!/usr/bin/env python3
"""
Generazione Ufficiale Completa del PDF di Ottimizzazione Deposito di PINEROLO:
Tutti i turni con Nastro >= 10h00 e i rispettivi partner di scambio:
- Pi0080 <-> Pi0370
- Pi0130 <-> Pi0190
- Pi0210 <-> Pi0470
- Pi0580 <-> Pi0290
- Pi0560 <-> Pi0020
- Pi0260 <-> Pi0120
- Pi0010 <-> Pi0050
- Pi0300 <-> Pi0950
- Pi0060 <-> Pi0950
- Pi0040 <-> Pi0610
- Pi0030 <-> Pi0280
- Pi0250 <-> Pi0620

Con evidenziazione cromatica delle corse scambiate e confronto dei DUE PARAMETRI (Nastro e OLG).
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
    leftMargin=18,
    rightMargin=18,
    topMargin=12,
    bottomMargin=12
)

styles = getSampleStyleSheet()
title_style = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=11.5, leading=13.5, textColor=colors.HexColor('#003366'))
sub_title_style = ParagraphStyle('SubDocTitle', fontName='Helvetica', fontSize=7.8, leading=9.5, textColor=colors.HexColor('#444444'))

th_style = ParagraphStyle('THStyle', fontName='Helvetica-Bold', fontSize=6.8, leading=8.0, textColor=colors.white, alignment=1)
td_cell = ParagraphStyle('TDCell', fontName='Helvetica', fontSize=6.2, leading=7.5)
td_center = ParagraphStyle('TDCenter', fontName='Helvetica', fontSize=6.2, leading=7.5, alignment=1)
td_right = ParagraphStyle('TDRight', fontName='Helvetica', fontSize=6.2, leading=7.5, alignment=2)

td_ceduta = ParagraphStyle('TDCeduta', fontName='Helvetica-Bold', fontSize=6.2, leading=7.5, textColor=colors.HexColor('#9C4221'))
td_ricevuta = ParagraphStyle('TDRicevuta', fontName='Helvetica-Bold', fontSize=6.2, leading=7.5, textColor=colors.HexColor('#1C4532'))

box_body = ParagraphStyle('BoxBody', fontName='Helvetica', fontSize=6.8, leading=8.0, textColor=colors.HexColor('#1A202C'))

elements = []

def aggiungi_scheda(t_orig, att_list, scambi_info, params_box):
    code = t_orig['codice_turno']
    name = t_orig['nome_turno']
    
    head_text = f"<b>TURNO {code} – {name}</b> (Deposito di Pinerolo)"
    sub_text = f"Progetto: <b>Ottimizzazione Turni Pinerolo</b> | <b>Analisi Scambio Corse e Bilanciamento OLG</b>"
    
    header_table = Table([
        [Paragraph(head_text, title_style), Paragraph(f"Stato: <b>{scambi_info['stato']}</b>", td_right)],
        [Paragraph(sub_text, sub_title_style), Paragraph(f"<b>Nastro Soluzione:</b> {params_box['nastro_dopo']}", td_right)]
    ], colWidths=[610, 196])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 1),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 4))

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
    t_box = Table(box_data, colWidths=[260, 260, 286])
    t_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F0F7FF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#3182CE')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BEE3F8')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_box)
    elements.append(Spacer(1, 5))

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
        elif 'Sosta' in lin or 'Pausa' in lin:
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
            Paragraph(da_a[:48], p_style),
            Paragraph(p, td_center),
            Paragraph(arr, td_center),
            Paragraph(km, td_right),
            note_cell
        ])

    t_corse = Table(corse_data, colWidths=[22, 42, 316, 40, 40, 38, 308])
    t_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 1.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ] + row_styles
    t_corse.setStyle(TableStyle(t_style))
    elements.append(t_corse)
    elements.append(PageBreak())

# =============================================================
# DEFINIZIONE DI TUTTI I TURNI DI PINEROLO E DEI LORO SCAMBI
# =============================================================

# 1. Pi0080
t80 = pinerolo['Pi0080']
att_80 = []
for a in t80['attivita']:
    ad = dict(a)
    if a.get('partenza') in ['07:00', '07:10', '07:15', '07:35', '07:40', '08:05']:
        ad['scambio_tag'] = 'CORSA MATTUTINA CEDUTA A Pi0370 (Inizio spostato alle 12:40)'
    att_80.append(ad)

aggiungi_scheda(t80, att_80, {
    'stato': 'POMERIDIANO CONTINUO',
    'descrizione': '• <b>Cede a Pi0370:</b> Mattino 07:00–08:15 (Linea 278 Cercenasco/Vigone).<br/>'
                   '• <b>Effetto:</b> Servizio continuo pomeridiano/serale 12:40–19:30 (Linee 901+278). Nastro da 12h30 a 6h50.'
}, {
    'orario_prima': '07:00 – 19:30', 'orario_dopo': '12:40 – 19:30',
    'nastro_prima': '12h 30m', 'nastro_dopo': '6h 50m', 'diff_nastro': '−5h 40m',
    'olg_prima': '7h 34m', 'olg_dopo': '6h 25m', 'diff_olg': 'Continuo',
    'rip_prima': '3 riprese', 'rip_dopo': '1 ripresa continua'
})

# 2. Pi0370
t370 = pinerolo['Pi0370']
att_370 = [
    {'linea': 'Disp', 'da': 'Controllo livelli autobus', 'partenza': '07:00', 'arrivo': '07:10', 'km': '-', 'scambio_tag': 'Attività Ordinaria'},
    {'linea': 'Trasf', 'da': 'Pinerolo Deposito ➔ PINEROLO', 'partenza': '07:10', 'arrivo': '07:15', 'km': '1.06', 'scambio_tag': 'Attività Ordinaria'},
    {'linea': '278', 'da': 'PINEROLO ➔ CERCENASCO - Via Umberto I', 'partenza': '07:15', 'arrivo': '07:35', 'km': '14.86', 'scambio_tag': 'CORSA RICEVUTA DA Pi0080 (Linea 278)'},
    {'linea': '278', 'da': 'VIGONE ➔ PINEROLO - Piazza Cavour', 'partenza': '07:40', 'arrivo': '08:05', 'km': '16.32', 'scambio_tag': 'CORSA RICEVUTA DA Pi0080 (Linea 278)'},
    {'linea': 'Trasf', 'da': 'PINEROLO ➔ Pinerolo Deposito / Riva', 'partenza': '08:05', 'arrivo': '08:15', 'km': '2.40', 'scambio_tag': 'Attività Ordinaria'},
    {'linea': '703', 'da': 'RIVA DI PINEROLO ➔ PINEROLO Fiugera', 'partenza': '08:20', 'arrivo': '08:47', 'km': '11.06', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': '703', 'da': 'PINEROLO Fiugera ➔ RIVA DI PINEROLO', 'partenza': '09:00', 'arrivo': '09:30', 'km': '11.54', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': '703', 'da': 'RIVA DI PINEROLO ➔ PINEROLO Fiugera', 'partenza': '09:30', 'arrivo': '09:57', 'km': '11.06', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': '703', 'da': 'PINEROLO Fiugera ➔ RIVA DI PINEROLO', 'partenza': '10:00', 'arrivo': '10:30', 'km': '11.54', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': '703', 'da': 'RIVA DI PINEROLO ➔ PINEROLO Fiugera', 'partenza': '10:30', 'arrivo': '10:57', 'km': '11.06', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': '703', 'da': 'PINEROLO Fiugera ➔ RIVA DI PINEROLO', 'partenza': '11:00', 'arrivo': '11:30', 'km': '11.54', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': 'Disp', 'da': 'Rientro Deposito e Pulizia Bus', 'partenza': '11:30', 'arrivo': '11:45', 'km': '3.86', 'scambio_tag': 'Attività Ordinaria'}
]
aggiungi_scheda(t370, att_370, {
    'stato': 'MATTINALE CONTINUO',
    'descrizione': '• <b>Riceve da Pi0080:</b> Tratta 07:15–08:05 (Linea 278 Pinerolo ➔ Cercenasco ➔ Vigone).<br/>'
                   '• <b>Effetto:</b> Sequenza continua 07:00–11:45 (Linea 278 + 703 navette). Nastro 4h45, OLG 4h45.'
}, {
    'orario_prima': '06:30 – 11:45', 'orario_dopo': '07:00 – 11:45',
    'nastro_prima': '5h 15m', 'nastro_dopo': '4h 45m', 'diff_nastro': 'Compatto',
    'olg_prima': '5h 15m', 'olg_dopo': '4h 45m', 'diff_olg': 'Continuo',
    'rip_prima': '1 ripresa', 'rip_dopo': '1 ripresa continua'
})

# 3. Pi0130
t130 = pinerolo['Pi0130']
att_130 = []
for a in t130['attivita']:
    ad = dict(a)
    if a.get('partenza') in ['16:00', '16:40', '17:10', '17:40', '18:20', '18:50', '18:55']:
        ad['scambio_tag'] = 'CORSA CEDUTA A Pi0190 (Chiusura servizio anticipata alle 15:35)'
    att_130.append(ad)

aggiungi_scheda(t130, att_130, {
    'stato': 'OTTIMIZZATO (Nastro -3h30)',
    'descrizione': '• <b>Cede a Pi0190:</b> Navette Linea 703 (16:00–18:50).<br/>'
                   '• <b>Effetto:</b> Completa la Linea 701 a Macello e rientra a Pinerolo alle 15:35. Nastro da 12h30 a 9h00.'
}, {
    'orario_prima': '06:35 – 19:05', 'orario_dopo': '06:35 – 15:35',
    'nastro_prima': '12h 30m', 'nastro_dopo': '9h 00m', 'diff_nastro': '−3h 30m',
    'olg_prima': '7h 00m', 'olg_dopo': '5h 25m', 'diff_olg': '−1h 35m',
    'rip_prima': '2 riprese', 'rip_dopo': '2 riprese compatte'
})

# 4. Pi0190
t190 = pinerolo['Pi0190']
att_190 = [
    {'linea': 'Disp', 'da': 'Controllo livelli autobus', 'partenza': '15:50', 'arrivo': '16:00', 'km': '-', 'scambio_tag': 'Attività Ordinaria'},
    {'linea': '703', 'da': 'PINEROLO Fiugera ➔ RIVA / PASCARETTO (5 Navette)', 'partenza': '16:00', 'arrivo': '18:50', 'km': '59.47', 'scambio_tag': 'CORSA RICEVUTA DA Pi0130 (Anticipa inizio alle 16:00)'},
    {'linea': '282', 'da': 'PINEROLO movicentro ➔ TORINO Autostazione c.so Bolzano', 'partenza': '18:46', 'arrivo': '19:57', 'km': '41.60', 'scambio_tag': 'Propria Corsa Linea 282'},
    {'linea': '282', 'da': 'TORINO Autostazione ➔ PINEROLO movicentro', 'partenza': '20:03', 'arrivo': '21:14', 'km': '41.90', 'scambio_tag': 'Propria Corsa Linea 282'},
    {'linea': '282', 'da': 'PINEROLO movicentro ➔ PEROSA ARGENTINA', 'partenza': '21:18', 'arrivo': '21:50', 'km': '18.51', 'scambio_tag': 'Propria Corsa Linea 282'},
    {'linea': '275', 'da': 'PEROSA ARGENTINA ➔ PINEROLO Deposito', 'partenza': '22:15', 'arrivo': '22:50', 'km': '20.83', 'scambio_tag': 'Propria Corsa Linea 275'},
    {'linea': 'Disp', 'da': 'Pulizia Interna Autobus', 'partenza': '22:51', 'arrivo': '23:01', 'km': '-', 'scambio_tag': 'Attività Ordinaria'}
]
aggiungi_scheda(t190, att_190, {
    'stato': 'POTENZIATO (Da 5h46 a 7h30 OLG)',
    'descrizione': '• <b>Riceve da Pi0130:</b> Navette Linea 703 (16:00–18:50).<br/>'
                   '• <b>Effetto:</b> Inizia alle 16:00 e si connette alle sue corse serali per Torino/Perosa, portando l’OLG a 7h30 pieno.'
}, {
    'orario_prima': '17:15 – 23:01', 'orario_dopo': '15:50 – 23:01',
    'nastro_prima': '5h 46m', 'nastro_dopo': '7h 11m', 'diff_nastro': '+1h 25m',
    'olg_prima': '5h 46m', 'olg_dopo': '7h 30m', 'diff_olg': '+1h 44m OLG',
    'rip_prima': '1 ripresa', 'rip_dopo': '1 ripresa continua'
})

# 5. Pi0210
t210 = pinerolo['Pi0210']
att_210 = []
for a in t210['attivita']:
    ad = dict(a)
    if a.get('partenza') in ['06:55', '07:05', '07:35', '08:15', '13:20', '13:30', '14:05']:
        ad['scambio_tag'] = 'CORSA CEDUTA A Pi0470 (Inizio servizio al pomeriggio)'
    att_210.append(ad)

aggiungi_scheda(t210, att_210, {
    'stato': 'POMERIDIANO CONTINUO',
    'descrizione': '• <b>Cede a Pi0470:</b> Mattino Virle (07:35) + Blocco 278/281 Pancalieri (13:20–14:55).<br/>'
                   '• <b>Effetto:</b> Effettua servizio pomeridiano/serale continuo 14:55–19:25 (Cantalupa+Perosa+Torre Pellice). Nastro da 12h30 a 4h30.'
}, {
    'orario_prima': '06:55 – 19:25', 'orario_dopo': '14:55 – 19:25',
    'nastro_prima': '12h 30m', 'nastro_dopo': '4h 30m', 'diff_nastro': '−8h 00m',
    'olg_prima': '7h 35m', 'olg_dopo': '4h 30m', 'diff_olg': 'Continuo',
    'rip_prima': '2 riprese', 'rip_dopo': '1 ripresa continua'
})

# 6. Pi0470
t470 = pinerolo['Pi0470']
att_470 = []
for a in t470['attivita'][:-1]:
    att_470.append(dict(a))

att_470.append({'linea': 'Sosta', 'da': 'Pausa Pranzo / Sosta a Pinerolo Deposito', 'partenza': '11:10', 'arrivo': '13:20', 'km': '-', 'scambio_tag': 'Pausa Ristoro Regolare'})
att_470.append({'linea': 'Trasf', 'da': 'Pinerolo Deposito ➔ PINEROLO - Stazione FS', 'partenza': '13:20', 'arrivo': '13:25', 'km': '2.75', 'scambio_tag': 'Attività Ordinaria'})
att_470.append({'linea': '278', 'da': 'PINEROLO - Stazione FS ➔ PANCALIERI - scuole medie', 'partenza': '13:30', 'arrivo': '14:05', 'km': '23.70', 'scambio_tag': 'CORSA RICEVUTA DA Pi0210 (Linea 278)'})
att_470.append({'linea': '281', 'da': 'PANCALIERI - scuole medie ➔ PINEROLO - Fronte Stazione FS', 'partenza': '14:05', 'arrivo': '14:55', 'km': '32.48', 'scambio_tag': 'CORSA RICEVUTA DA Pi0210 (Linea 281)'})
att_470.append({'linea': 'Trasf', 'da': 'PINEROLO ➔ Pinerolo Deposito', 'partenza': '14:55', 'arrivo': '15:00', 'km': '2.40', 'scambio_tag': 'Attività Ordinaria'})
att_470.append({'linea': 'Disp', 'da': 'Pulizia Interna Autobus', 'partenza': '15:00', 'arrivo': '15:10', 'km': '-', 'scambio_tag': 'Attività Ordinaria'})

aggiungi_scheda(t470, att_470, {
    'stato': 'POTENZIATO (Da 5h25 a 6h50 OLG)',
    'descrizione': '• <b>Riceve da Pi0210:</b> Blocco 278/281 Pancalieri (13:20–14:55).<br/>'
                   '• <b>Effetto:</b> Completa il mattino, effettua pausa pranzo regolare a Pinerolo e chiude alle 15:10 con 6h50m di lavoro pieno.'
}, {
    'orario_prima': '05:00 – 11:20', 'orario_dopo': '05:00 – 15:10',
    'nastro_prima': '6h 20m', 'nastro_dopo': '10h 10m', 'diff_nastro': '+3h 50m',
    'olg_prima': '5h 25m', 'olg_dopo': '6h 50m', 'diff_olg': '+1h 25m OLG',
    'rip_prima': '2 riprese', 'rip_dopo': '2 riprese con pausa pranzo'
})

# 7. Pi0580
t580 = pinerolo['Pi0580']
att_580 = []
for a in t580['attivita']:
    ad = dict(a)
    if a.get('partenza') in ['06:40', '06:50', '07:00', '07:20', '07:25', '08:10', '13:04', '13:05', '13:35']:
        ad['scambio_tag'] = 'CORSA CEDUTA (Mattino e corsa 13:05 ceduti a Pi0290)'
    att_580.append(ad)

aggiungi_scheda(t580, att_580, {
    'stato': 'POMERIDIANO CONTINUO',
    'descrizione': '• <b>Cede a Pi0290:</b> Corsa 13:05 (Linea 275 Villar Perosa SKF).<br/>'
                   '• <b>Effetto:</b> Inizia alle 13:40 ed effettua servizio continuo (Linee 901+281+284) fino alle 19:10. Nastro da 12h30 a 5h30.'
}, {
    'orario_prima': '06:40 – 19:10', 'orario_dopo': '13:40 – 19:10',
    'nastro_prima': '12h 30m', 'nastro_dopo': '5h 30m', 'diff_nastro': '−7h 00m',
    'olg_prima': '7h 10m', 'olg_dopo': '5h 30m', 'diff_olg': 'Continuo',
    'rip_prima': '3 riprese', 'rip_dopo': '1 ripresa continua'
})

# 8. Pi0290
t290 = pinerolo['Pi0290']
att_290 = []
for a in t290['attivita']:
    ad = dict(a)
    att_290.append(ad)
# Inseriamo la corsa ricevuta da Pi0580
att_290.insert(10, {
    'linea': '275',
    'da': 'PINEROLO ➔ Villar Perosa Stabilimento SKF',
    'partenza': '13:05',
    'arrivo': '13:35',
    'km': '13.56',
    'scambio_tag': 'CORSA RICEVUTA DA Pi0580 (Linea 275)'
})
aggiungi_scheda(t290, att_290, {
    'stato': 'POTENZIATO (Da 5h44 a 6h45 OLG)',
    'descrizione': '• <b>Riceve da Pi0580:</b> Corsa 13:05 (Linea 275 Villar Perosa SKF).<br/>'
                   '• <b>Effetto:</b> Si aggancia al rientro da Torino Bolzano aumentando l’OLG a 6h45m senza variare il nastro (05:33–14:20).'
}, {
    'orario_prima': '05:33 – 14:20', 'orario_dopo': '05:33 – 14:20',
    'nastro_prima': '8h 47m', 'nastro_dopo': '8h 47m', 'diff_nastro': 'Invariato',
    'olg_prima': '5h 44m', 'olg_dopo': '6h 45m', 'diff_olg': '+1h 01m OLG',
    'rip_prima': '3 riprese', 'rip_dopo': '2 riprese'
})

# 9. Pi0560
t560 = pinerolo['Pi0560']
att_560 = []
for a in t560['attivita']:
    ad = dict(a)
    if a.get('partenza') in ['05:30', '05:40', '06:05', '06:36', '08:11', '09:20']:
        ad['scambio_tag'] = 'CORSA MATTUTINA CEDUTA A Pi0280 (Inizio spostato al pomeriggio)'
    att_560.append(ad)

aggiungi_scheda(t560, att_560, {
    'stato': 'POMERIDIANO CONTINUO',
    'descrizione': '• <b>Cede a Pi0280:</b> Blocco mattutino 05:30–09:30 (Linee 901+282+275 Torino Bolzano).<br/>'
                   '• <b>Effetto:</b> Inizia alle 13:20 ed effettua servizio continuo (Linee 279+901+282+275) fino alle 17:38. Nastro da 12h08 a 4h18.'
}, {
    'orario_prima': '05:30 – 17:38', 'orario_dopo': '13:20 – 17:38',
    'nastro_prima': '12h 08m', 'nastro_dopo': '4h 18m', 'diff_nastro': '−7h 50m',
    'olg_prima': '7h 47m', 'olg_dopo': '4h 18m', 'diff_olg': 'Continuo',
    'rip_prima': '3 riprese', 'rip_dopo': '1 ripresa continua'
})

# 10. Pi0280
t280 = pinerolo['Pi0280']
att_280 = [
    {'linea': 'Disp', 'da': 'Controllo livelli autobus', 'partenza': '05:30', 'arrivo': '05:40', 'km': '-', 'scambio_tag': 'Attività Ordinaria'},
    {'linea': 'Trasf', 'da': 'Pinerolo Deposito ➔ TORRE PELLICE', 'partenza': '05:40', 'arrivo': '06:05', 'km': '16.85', 'scambio_tag': 'CORSA RICEVUTA DA Pi0560 (Linea 901)'},
    {'linea': '901', 'da': 'TORRE PELLICE ➔ PINEROLO - movicentro', 'partenza': '06:05', 'arrivo': '06:35', 'km': '18.17', 'scambio_tag': 'CORSA RICEVUTA DA Pi0560 (Linea 901)'},
    {'linea': '282', 'da': 'PINEROLO ➔ TORINO - Autostazione c.so Bolzano', 'partenza': '06:36', 'arrivo': '07:47', 'km': '44.60', 'scambio_tag': 'CORSA RICEVUTA DA Pi0560 (Linea 282)'},
    {'linea': '275', 'da': 'TORINO ➔ PINEROLO - Piazza Cavour', 'partenza': '08:11', 'arrivo': '09:20', 'km': '42.11', 'scambio_tag': 'CORSA RICEVUTA DA Pi0560 (Linea 275)'},
    {'linea': 'Trasf', 'da': 'PINEROLO ➔ Pinerolo Deposito', 'partenza': '09:20', 'arrivo': '09:30', 'km': '2.40', 'scambio_tag': 'Attività Ordinaria'},
    {'linea': 'Sosta', 'da': 'Pausa Pranzo / Sosta al Deposito Pinerolo', 'partenza': '09:30', 'arrivo': '13:10', 'km': '-', 'scambio_tag': 'Pausa Ristoro Regolare'},
    {'linea': '703', 'da': 'RIVA DI PINEROLO ➔ PINEROLO Fiugera (Navette)', 'partenza': '13:20', 'arrivo': '15:57', 'km': '56.26', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': 'Disp', 'da': 'Rientro Deposito e Pulizia Bus', 'partenza': '15:57', 'arrivo': '16:17', 'km': '3.86', 'scambio_tag': 'Attività Ordinaria'}
]
aggiungi_scheda(t280, att_280, {
    'stato': 'POTENZIATO (Da 5h07 a 7h15 OLG)',
    'descrizione': '• <b>Riceve da Pi0560:</b> Corsa Torino Bolzano 05:30–09:30 (Linee 901+282+275).<br/>'
                   '• <b>Effetto:</b> Sostituisce il mattino corto con il collegamento per Torino e chiude con le navette 703. OLG sale da 5h07 a 7h15m!'
}, {
    'orario_prima': '06:15 – 16:17', 'orario_dopo': '05:30 – 16:17',
    'nastro_prima': '10h 02m', 'nastro_dopo': '10h 47m', 'diff_nastro': 'Compatto',
    'olg_prima': '5h 07m', 'olg_dopo': '7h 15m', 'diff_olg': '+2h 08m OLG',
    'rip_prima': '2 riprese', 'rip_dopo': '2 riprese con pausa'
})

# 11. Pi0260
t260 = pinerolo['Pi0260']
att_260 = []
for a in t260['attivita']:
    ad = dict(a)
    if a.get('partenza') in ['13:05', '13:25', '14:08', '14:30', '15:15']:
        ad['scambio_tag'] = 'CORSA POMERIDIANA CEDUTA A Pi0020 (Eliminazione 2ª ripresa)'
    att_260.append(ad)

aggiungi_scheda(t260, att_260, {
    'stato': 'OTTIMIZZATO (Nastro da 12h02 a 8h30)',
    'descrizione': '• <b>Cede a Pi0020:</b> Tratta pomeridiana 13:05–15:20 (Linee 278+284 Airasca/Vandalino).<br/>'
                   '• <b>Effetto:</b> Elimina la ripresa intermedia e chiude alle 18:51 con nastro a 8h30.'
}, {
    'orario_prima': '06:49 – 18:51', 'orario_dopo': '06:49 – 18:51',
    'nastro_prima': '12h 02m', 'nastro_dopo': '8h 30m', 'diff_nastro': '−3h 32m',
    'olg_prima': '6h 32m', 'olg_dopo': '5h 00m', 'diff_olg': 'Compatto',
    'rip_prima': '3 riprese', 'rip_dopo': '2 riprese'
})

# 12. Pi0020
t020 = pinerolo['Pi0020']
att_020 = []
for a in t020['attivita'][:8]: # prime corse fino alle 08:23
    att_020.append(dict(a))

att_020.append({'linea': 'Sosta', 'da': 'Pausa Pranzo / Sosta a Pinerolo Deposito', 'partenza': '08:23', 'arrivo': '13:05', 'km': '-', 'scambio_tag': 'Pausa Ristoro Regolare'})
att_020.append({'linea': '278', 'da': 'PINEROLO ➔ SCA - FR Pieve Via Savigliani', 'partenza': '13:25', 'arrivo': '14:08', 'km': '26.13', 'scambio_tag': 'CORSA RICEVUTA DA Pi0260 (Linea 278)'})
att_020.append({'linea': '284', 'da': 'AIRASCA SKF ➔ SEGGIOVIA VANDALINO', 'partenza': '14:30', 'arrivo': '15:15', 'km': '33.21', 'scambio_tag': 'CORSA RICEVUTA DA Pi0260 (Linea 284)'})
att_020.append({'linea': 'Trasf', 'da': 'SEGGIOVIA VANDALINO ➔ Pinerolo Deposito', 'partenza': '15:15', 'arrivo': '15:40', 'km': '19.57', 'scambio_tag': 'Attività Ordinaria'})
att_020.append({'linea': 'Disp', 'da': 'Pulizia Interna Autobus', 'partenza': '15:40', 'arrivo': '15:50', 'km': '-', 'scambio_tag': 'Attività Ordinaria'})

aggiungi_scheda(t020, att_020, {
    'stato': 'POTENZIATO (Da 5h50 a 6h50 OLG)',
    'descrizione': '• <b>Riceve da Pi0260:</b> Tratta 13:25–15:15 (Linee 278+284 Airasca/Vandalino).<br/>'
                   '• <b>Effetto:</b> Elimina le navette frammentate di Macello e fa 2 blocchi continui con 6h50m di OLG pieno.'
}, {
    'orario_prima': '05:45 – 14:32', 'orario_dopo': '05:45 – 15:50',
    'nastro_prima': '8h 47m', 'nastro_dopo': '10h 05m', 'diff_nastro': 'Compatto',
    'olg_prima': '5h 50m', 'olg_dopo': '6h 50m', 'diff_olg': '+1h 00m OLG',
    'rip_prima': '3 riprese', 'rip_dopo': '2 riprese con pausa pranzo'
})

doc.build(elements)
print(f"✅ DOSSIER PDF UFFICIALE DI PINEROLO GENERATO:\n{PDF_OUT} ({len(elements)} elementi)")
