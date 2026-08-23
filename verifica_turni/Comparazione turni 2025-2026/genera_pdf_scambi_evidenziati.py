#!/usr/bin/env python3
"""
Generazione PDF dei Turni con CORSE DI SCAMBIO EVIDENZIATE:
- Visualizzazione chiara dei turni coinvolti negli scambi
- Evidenziazione cromatica (giallo/arancione/verde) delle righe delle corse scambiate
- Etichetta esplicita: [CORSA CEDUTA A ...] oppure [CORSA RICEVUTA DA ...]
- Riquadro con i DUE PARAMETRI (Nastro e OLG) Prima vs Dopo.
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

box_title = ParagraphStyle('BoxTitle', fontName='Helvetica-Bold', fontSize=8.0, leading=9.5, textColor=colors.HexColor('#003366'))
box_body = ParagraphStyle('BoxBody', fontName='Helvetica', fontSize=7.0, leading=8.2, textColor=colors.HexColor('#1A202C'))

elements = []

def genera_scheda_turno_scambio(t_orig, att_modificate, scambi_info, params_box):
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

    # Box Confronto Due Parametri
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

    for c_idx, a in enumerate(att_modificate, 1):
        lin = a.get('linea', '')
        da_a = f"{a.get('da','')} ➔ {a.get('a','')}" if a.get('a') else a.get('descrizione', a.get('da',''))
        p = a.get('partenza', '')
        arr = a.get('arrivo', '')
        km = str(a.get('km', '-'))
        stato_scambio = a.get('scambio_tag', 'Regolare')

        if 'CEDUTA' in stato_scambio:
            p_style = td_ceduta
            note_cell = Paragraph(f"🔴 <b>{stato_scambio}</b>", td_ceduta)
            row_styles.append(('BACKGROUND', (0, c_idx), (-1, c_idx), colors.HexColor('#FEEBC8'))) # Arancio chiaro
        elif 'RICEVUTA' in stato_scambio:
            p_style = td_ricevuta
            note_cell = Paragraph(f"🟢 <b>{stato_scambio}</b>", td_ricevuta)
            row_styles.append(('BACKGROUND', (0, c_idx), (-1, c_idx), colors.HexColor('#C6F6D5'))) # Verde chiaro
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
# DEFINIZIONE DEGLI SCAMBI PERFETTI
# -------------------------------------------------------------

# 1. Pi0080
t80_orig = pinerolo['Pi0080']
att_80 = []
for a in t80_orig['attivita']:
    a_dict = dict(a)
    p = a.get('partenza', '')
    if p in ['17:40', '18:25', '19:10', '19:20']:
        a_dict['scambio_tag'] = 'CORSA CEDUTA A Pi0090 (Rientro anticipato alle 17:25)'
    att_80.append(a_dict)

genera_scheda_turno_scambio(
    t80_orig,
    att_80,
    scambi_info={
        'stato': 'OTTIMIZZATO (Nastro compattato)',
        'descrizione': '• <b>Cede a Pi0090:</b> Tratta serale 17:40–19:10 (Linea 278 Cercenasco A/R).<br/>'
                       '• <b>Effetto:</b> Il turno chiude a Pinerolo alle 17:25 invece che alle 19:30, eliminando 2 ore di nastro inutile.'
    },
    params_box={
        'orario_prima': '07:00 – 19:30',
        'orario_dopo': '07:00 – 17:25',
        'nastro_prima': '12h 30m',
        'nastro_dopo': '10h 25m',
        'diff_nastro': '−2h 05m',
        'olg_prima': '7h 34m',
        'olg_dopo': '6h 15m',
        'diff_olg': '−1h 19m',
        'rip_prima': '3 riprese',
        'rip_dopo': '2 riprese'
    }
)

# 2. Pi0090
t90_orig = pinerolo['Pi0090']
att_90 = []
for a in t90_orig['attivita']:
    att_90.append(dict(a))

# Inseriamo la corsa ricevuta da Pi0080
att_90.insert(10, {
    'linea': '278',
    'da': 'PINEROLO ➔ CERCENASCO - v. Reg.Margherita (A/R)',
    'a': '',
    'partenza': '17:40',
    'arrivo': '19:10',
    'km': '47.40',
    'scambio_tag': 'CORSA RICEVUTA DA Pi0080 (Riempie la sosta e aumenta OLG)'
})

genera_scheda_turno_scambio(
    t90_orig,
    att_90,
    scambi_info={
        'stato': 'POTENZIATO (OLG incrementato)',
        'descrizione': '• <b>Riceve da Pi0080:</b> Tratta 17:40–19:10 (Linea 278 Cercenasco A/R).<br/>'
                       '• <b>Effetto:</b> Riempie il tempo di sosta pomeridiano aumentando il lavoro effettivo (+39m OLG) senza allungare il nastro.'
    },
    params_box={
        'orario_prima': '13:10 – 20:30',
        'orario_dopo': '13:10 – 20:30',
        'nastro_prima': '7h 20m',
        'nastro_dopo': '7h 20m',
        'diff_nastro': 'Invariato',
        'olg_prima': '6h 36m',
        'olg_dopo': '7h 15m',
        'diff_olg': '+39m OLG',
        'rip_prima': '2 riprese',
        'rip_dopo': '2 riprese'
    }
)

# 3. Pi0130
t130_orig = pinerolo['Pi0130']
att_130 = []
for a in t130_orig['attivita']:
    a_dict = dict(a)
    p = a.get('partenza', '')
    if p in ['16:00', '16:40', '17:10', '17:40', '18:20', '18:50', '18:55']:
        a_dict['scambio_tag'] = 'CORSA CEDUTA A Pi0190 (Chiusura servizio anticipata alle 15:35)'
    att_130.append(a_dict)

genera_scheda_turno_scambio(
    t130_orig,
    att_130,
    scambi_info={
        'stato': 'OTTIMIZZATO (Nastro ridotto di 3h30)',
        'descrizione': '• <b>Cede a Pi0190:</b> Blocco Navette Linea 703 dalle 16:00 alle 18:50.<br/>'
                       '• <b>Effetto:</b> Completa la Linea 701 e chiude alle 15:35, eliminando 3h30 di nastro dilatato.'
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
        'rip_dopo': '2 riprese'
    }
)

# 4. Pi0190
t190_orig = pinerolo['Pi0190']
att_190 = []
att_190.append({
    'linea': '703',
    'da': 'PINEROLO Fiugera ➔ RIVA / PASCARETTO (5 Navette)',
    'a': '',
    'partenza': '16:00',
    'arrivo': '18:50',
    'km': '59.47',
    'scambio_tag': 'CORSA RICEVUTA DA Pi0130 (Anticipa inizio alle 16:00)'
})
for a in t190_orig['attivita']:
    att_190.append(dict(a))

genera_scheda_turno_scambio(
    t190_orig,
    att_190,
    scambi_info={
        'stato': 'POTENZIATO (Da turno corto a turno serale pieno)',
        'descrizione': '• <b>Riceve da Pi0130:</b> Navette Linea 703 dalle 16:00 alle 18:50.<br/>'
                       '• <b>Effetto:</b> Inizia alle 16:00 e si connette alle sue corse serali per Torino/Perosa, portando l’OLG a 7h30 pieno.'
    },
    params_box={
        'orario_prima': '17:15 – 23:01',
        'orario_dopo': '16:00 – 23:01',
        'nastro_prima': '5h 46m',
        'nastro_dopo': '7h 01m',
        'diff_nastro': '+1h 15m (Ottimale)',
        'olg_prima': '5h 46m',
        'olg_dopo': '7h 30m',
        'diff_olg': '+1h 44m OLG',
        'rip_prima': '1 ripresa',
        'rip_dopo': '1 ripresa continua'
    }
)

doc.build(elements)
print(f"✅ PDF GENERATO CON SUCCESSO:\n{PDF_OUT}")
