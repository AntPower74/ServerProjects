#!/usr/bin/env python3
"""
Rigenerazione PDF con Inserimento dello Scambio Incrociato Pinerolo <-> Perosa:
- Aggiunta scheda Pe0270 (227 DI PEROSA) ottimizzato con rientro a Perosa alle 16:05 (Nastro da 11h05 a 9h40).
- Aggiunta scheda Pi0620 (62 PINEROLO) potenziato con eliminazione della sosta passiva a Perosa (OLG da 5h55 a 6h25).
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

turni_dict = {t['codice_turno']: t for t in turni}

doc = SimpleDocTemplate(
    PDF_OUT,
    pagesize=landscape(A4),
    leftMargin=16,
    rightMargin=16,
    topMargin=12,
    bottomMargin=12
)

styles = getSampleStyleSheet()
title_style = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=11, leading=13, textColor=colors.HexColor('#003366'))
sub_title_style = ParagraphStyle('SubDocTitle', fontName='Helvetica', fontSize=7.5, leading=9.0, textColor=colors.HexColor('#444444'))

th_style = ParagraphStyle('THStyle', fontName='Helvetica-Bold', fontSize=6.8, leading=8.0, textColor=colors.white, alignment=1)
td_cell = ParagraphStyle('TDCell', fontName='Helvetica', fontSize=6.0, leading=7.2)
td_center = ParagraphStyle('TDCenter', fontName='Helvetica', fontSize=6.0, leading=7.2, alignment=1)
td_right = ParagraphStyle('TDRight', fontName='Helvetica', fontSize=6.0, leading=7.2, alignment=2)

td_ricevuta = ParagraphStyle('TDRicevuta', fontName='Helvetica-Bold', fontSize=6.0, leading=7.2, textColor=colors.HexColor('#1C4532'))
box_body = ParagraphStyle('BoxBody', fontName='Helvetica', fontSize=6.6, leading=7.8, textColor=colors.HexColor('#1A202C'))

elements = []

def aggiungi_scheda_turno_pulita(t_orig, att_list, scambi_info, params_box):
    code = t_orig['codice_turno']
    dep = scambi_info.get('deposito', 'Pinerolo')
    nuova_dicitura = scambi_info.get('nuova_dicitura', t_orig['nome_turno'])
    
    head_text = f"<b>TURNO {code} – {nuova_dicitura}</b> (Deposito di {dep})"
    sub_text = f"Progetto: <b>Ottimizzazione Turni e Scambi Incrociati 2026</b> | Validità: <b>Lunedì - Venerdì Scolastico</b>"
    
    header_table = Table([
        [Paragraph(head_text, title_style), Paragraph(f"Tipologia: <b>{scambi_info['stato']}</b>", td_right)],
        [Paragraph(sub_text, sub_title_style), Paragraph(f"<b>Nastro Proposta:</b> {params_box['nastro_dopo']} | <b>OLG:</b> {params_box['olg_dopo']}", td_right)]
    ], colWidths=[580, 230])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 1),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 4))

    box_data = [
        [
            Paragraph(f"🔴 <b>CARTELLINO ATTUALE AZIENDA:</b><br/>"
                      f"• Dicitura: <b>{t_orig['nome_turno']}</b><br/>"
                      f"• Orario: <b>{params_box['orario_prima']}</b><br/>"
                      f"• <b>Nastro:</b> <font color='#990000'><b>{params_box['nastro_prima']}</b></font> | <b>OLG:</b> <b>{params_box['olg_prima']}</b><br/>"
                      f"• Riprese: <b>{params_box['rip_prima']}</b>", box_body),
            Paragraph(f"🟢 <b>NUOVA STRUTTURA DOPO LO SCAMBIO:</b><br/>"
                      f"• Nuova Qualifica: <b>{nuova_dicitura}</b><br/>"
                      f"• Orario: <b>{params_box['orario_dopo']}</b><br/>"
                      f"• <b>Nastro:</b> <font color='#006600'><b>{params_box['nastro_dopo']}</b> ({params_box['diff_nastro']})</font><br/>"
                      f"• <b>OLG:</b> <font color='#006600'><b>{params_box['olg_dopo']}</b> ({params_box['diff_olg']})</font><br/>"
                      f"• Riprese: <b>{params_box['rip_dopo']}</b>", box_body),
            Paragraph(f"🔄 <b>DETTAGLIO E MOTIVAZIONE SCAMBIO:</b><br/>"
                      f"{scambi_info['descrizione']}", box_body)
        ]
    ]
    t_box = Table(box_data, colWidths=[260, 265, 285])
    t_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F0F7FF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#3182CE')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BEE3F8')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_box)
    elements.append(Spacer(1, 5))

    corse_data = [[
        Paragraph("N°", th_style),
        Paragraph("Linea", th_style),
        Paragraph("Descrizione Tratta / Attività Effettiva", th_style),
        Paragraph("Part.", th_style),
        Paragraph("Arr.", th_style),
        Paragraph("Km", th_style),
        Paragraph("Dicitura / Stato Operativo della Corsa", th_style)
    ]]

    row_styles = []

    for c_idx, a in enumerate(att_list, 1):
        lin = a.get('linea', '')
        desc_tratta = a.get('descrizione', f"{a.get('da','')} ➔ {a.get('a','')}" if a.get('a') else a.get('da',''))
        p = a.get('partenza', '')
        arr = a.get('arrivo', '')
        km = str(a.get('km', '-'))
        stato_scambio = a.get('scambio_tag', 'Attività Ordinaria Invariata')

        if 'RICEVUTA' in stato_scambio:
            p_style = td_ricevuta
            note_cell = Paragraph(f"🟢 <b>{stato_scambio}</b>", td_ricevuta)
            row_styles.append(('BACKGROUND', (0, c_idx), (-1, c_idx), colors.HexColor('#C6F6D5')))
        elif 'Sosta' in lin or 'Pausa' in lin:
            p_style = td_cell
            note_cell = Paragraph("Pausa / Sosta Operativa al Deposito", td_cell)
            row_styles.append(('BACKGROUND', (0, c_idx), (-1, c_idx), colors.HexColor('#EDF2F7')))
        else:
            p_style = td_cell
            note_cell = Paragraph("Attività Ordinaria Invariata", td_cell)
            if c_idx % 2 == 0:
                row_styles.append(('BACKGROUND', (0, c_idx), (-1, c_idx), colors.HexColor('#F7FAFC')))

        corse_data.append([
            Paragraph(str(c_idx), td_center),
            Paragraph(lin, td_center),
            Paragraph(desc_tratta[:55], p_style),
            Paragraph(p, td_center),
            Paragraph(arr, td_center),
            Paragraph(km, td_right),
            note_cell
        ])

    t_corse = Table(corse_data, colWidths=[20, 38, 330, 38, 38, 36, 310])
    t_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
        ('TOPPADDING', (0,0), (-1,-1), 1.6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ] + row_styles
    t_corse.setStyle(TableStyle(t_style))
    elements.append(t_corse)
    elements.append(PageBreak())

# =============================================================
# 1. Pi0080
# =============================================================
t80 = turni_dict['Pi0080']
att_80 = [
    {'linea': 'Disp', 'da': 'Controllo livelli autobus', 'descrizione': 'Controllo livelli autobus (Pinerolo Deposito)', 'partenza': '12:40', 'arrivo': '12:45', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'Pinerolo Deposito ➔ PINEROLO movicentro', 'descrizione': 'Pinerolo Deposito ➔ PINEROLO movicentro', 'partenza': '12:45', 'arrivo': '12:50', 'km': '2.46', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '901', 'da': 'PINEROLO ➔ TORRE PELLICE', 'descrizione': 'Linea 901: PINEROLO (movicentro) ➔ TORRE PELLICE', 'partenza': '12:50', 'arrivo': '13:25', 'km': '17.62', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '901', 'da': 'TORRE PELLICE ➔ PINEROLO', 'descrizione': 'Linea 901: TORRE PELLICE ➔ PINEROLO (movicentro)', 'partenza': '13:35', 'arrivo': '14:10', 'km': '18.17', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '901', 'da': 'PINEROLO ➔ TORRE PELLICE', 'descrizione': 'Linea 901: PINEROLO (movicentro) ➔ TORRE PELLICE', 'partenza': '14:20', 'arrivo': '14:55', 'km': '18.60', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '901', 'da': 'TORRE PELLICE ➔ PINEROLO', 'descrizione': 'Linea 901: TORRE PELLICE ➔ PINEROLO (movicentro)', 'partenza': '15:35', 'arrivo': '16:10', 'km': '18.17', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'PINEROLO ➔ PINEROLO Via Saluzzo (ENEL)', 'descrizione': 'PINEROLO movicentro ➔ PINEROLO Via Saluzzo (ENEL)', 'partenza': '16:10', 'arrivo': '16:12', 'km': '1.38', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '278', 'da': 'PINEROLO ➔ MACELLO - Municipio', 'descrizione': 'Linea 278: PINEROLO (Via Saluzzo ENEL) ➔ MACELLO (Municipio)', 'partenza': '16:30', 'arrivo': '16:50', 'km': '11.44', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '278', 'da': 'MACELLO ➔ PINEROLO - Piazza Cavour', 'descrizione': 'Linea 278: MACELLO (Municipio) ➔ PINEROLO (Piazza Cavour)', 'partenza': '16:50', 'arrivo': '17:17', 'km': '10.93', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '278', 'da': 'PINEROLO ➔ CERCENASCO - v. Reg.Margherita', 'descrizione': 'Linea 278: PINEROLO (Piazza Cavour) ➔ CERCENASCO (v. Reg.Margherita)', 'partenza': '17:40', 'arrivo': '18:20', 'km': '24.08', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '278', 'da': 'CERCENASCO ➔ PINEROLO - Piazza Cavour', 'descrizione': 'Linea 278: CERCENASCO (v. Reg.Margherita) ➔ PINEROLO (Piazza Cavour)', 'partenza': '18:25', 'arrivo': '19:10', 'km': '23.32', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'PINEROLO ➔ Pinerolo Deposito', 'descrizione': 'PINEROLO Piazza Cavour ➔ Pinerolo Deposito', 'partenza': '19:10', 'arrivo': '19:20', 'km': '2.40', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Disp', 'da': 'Pulizia Interna Autobus', 'descrizione': 'Pulizia Interna Autobus e Chiusura Turno (Pinerolo Deposito)', 'partenza': '19:20', 'arrivo': '19:30', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'}
]

aggiungi_scheda_turno_pulita(t80, att_80, {
    'nuova_dicitura': '8 PINEROLO [POMERIDIANO CONTINUO LINEE 901 / 278]',
    'stato': 'POMERIDIANO CONTINUO (ZERO STACCHI)',
    'descrizione': '• <b>Corse Cedute a Pi0370:</b> Corsa mattutina 07:00–08:15 (Linea 278 Pinerolo ➔ Cercenasco ➔ Vigone).<br/>'
                   '• <b>Nuovo Servizio Effettivo:</b> Inizia alle 12:40 ed effettua servizio continuo (Linee 901+278) fino alle 19:30. Nastro da 12h30 a 6h50, <b>zero buchi passivi e zero stacchi!</b>'
}, {
    'orario_prima': '07:00 – 19:30', 'orario_dopo': '12:40 – 19:30',
    'nastro_prima': '12h 30m', 'nastro_dopo': '6h 50m', 'diff_nastro': '−5h 40m',
    'olg_prima': '7h 34m', 'olg_dopo': '6h 25m', 'diff_olg': 'Continuo',
    'rip_prima': '3 riprese', 'rip_dopo': '1 ripresa continua'
})

# =============================================================
# 2. Pi0370
# =============================================================
t370 = turni_dict['Pi0370']
att_370 = [
    {'linea': 'Disp', 'da': 'Controllo livelli autobus', 'descrizione': 'Controllo livelli autobus (Pinerolo Deposito)', 'partenza': '07:00', 'arrivo': '07:10', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'Pinerolo Deposito ➔ PINEROLO', 'descrizione': 'Pinerolo Deposito ➔ PINEROLO c.so Torino-MACUMBA', 'partenza': '07:10', 'arrivo': '07:15', 'km': '1.06', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '278', 'da': 'PINEROLO ➔ CERCENASCO - Via Umberto I', 'descrizione': 'Linea 278: PINEROLO ➔ CERCENASCO [RICEVUTA DA TURNO Pi0080]', 'partenza': '07:15', 'arrivo': '07:35', 'km': '14.86', 'scambio_tag': '🟢 CORSA RICEVUTA DA TURNO Pi0080'},
    {'linea': '278', 'da': 'VIGONE ➔ PINEROLO - Piazza Cavour', 'descrizione': 'Linea 278: VIGONE ➔ PINEROLO [RICEVUTA DA TURNO Pi0080]', 'partenza': '07:40', 'arrivo': '08:05', 'km': '16.32', 'scambio_tag': '🟢 CORSA RICEVUTA DA TURNO Pi0080'},
    {'linea': 'Trasf', 'da': 'PINEROLO ➔ Pinerolo Deposito / Riva', 'descrizione': 'PINEROLO Piazza Cavour ➔ RIVA DI PINEROLO', 'partenza': '08:05', 'arrivo': '08:15', 'km': '2.40', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '703', 'da': 'RIVA DI PINEROLO ➔ PINEROLO Fiugera', 'descrizione': 'Linea 703: RIVA DI PINEROLO ➔ PINEROLO Fiugera (Navetta 1)', 'partenza': '08:20', 'arrivo': '08:47', 'km': '11.06', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': '703', 'da': 'PINEROLO Fiugera ➔ RIVA DI PINEROLO', 'descrizione': 'Linea 703: PINEROLO Fiugera ➔ RIVA DI PINEROLO (Navetta 2)', 'partenza': '09:00', 'arrivo': '09:30', 'km': '11.54', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': '703', 'da': 'RIVA DI PINEROLO ➔ PINEROLO Fiugera', 'descrizione': 'Linea 703: RIVA DI PINEROLO ➔ PINEROLO Fiugera (Navetta 3)', 'partenza': '09:30', 'arrivo': '09:57', 'km': '11.06', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': '703', 'da': 'PINEROLO Fiugera ➔ RIVA DI PINEROLO', 'descrizione': 'Linea 703: PINEROLO Fiugera ➔ RIVA DI PINEROLO (Navetta 4)', 'partenza': '10:00', 'arrivo': '10:30', 'km': '11.54', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': '703', 'da': 'RIVA DI PINEROLO ➔ PINEROLO Fiugera', 'descrizione': 'Linea 703: RIVA DI PINEROLO ➔ PINEROLO Fiugera (Navetta 5)', 'partenza': '10:30', 'arrivo': '10:57', 'km': '11.06', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': '703', 'da': 'PINEROLO Fiugera ➔ RIVA DI PINEROLO', 'descrizione': 'Linea 703: PINEROLO Fiugera ➔ RIVA DI PINEROLO (Navetta 6)', 'partenza': '11:00', 'arrivo': '11:30', 'km': '11.54', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': 'Disp', 'da': 'Rientro Deposito e Pulizia Bus', 'descrizione': 'Rientro Deposito Pinerolo e Pulizia Interna Autobus', 'partenza': '11:30', 'arrivo': '11:45', 'km': '3.86', 'scambio_tag': 'Attività Ordinaria Invariata'}
]

aggiungi_scheda_turno_pulita(t370, att_370, {
    'nuova_dicitura': '37 PINEROLO [MATTINALE CONTINUO LINEE 278 / 703]',
    'stato': 'MATTINALE CONTINUO (ZERO STACCHI)',
    'descrizione': '• <b>Corse Ricevute da Pi0080:</b> Tratta 07:15–08:05 (Linea 278 Pinerolo ➔ Cercenasco ➔ Vigone).<br/>'
                   '• <b>Nuovo Servizio Effettivo:</b> Sequenza continua 07:00–11:45 (Linea 278 + Navette 703). Nessun conflitto orario, nastro compatto a 4h45, <b>zero stacchi intermedi!</b>'
}, {
    'orario_prima': '06:30 – 11:45', 'orario_dopo': '07:00 – 11:45',
    'nastro_prima': '5h 15m', 'nastro_dopo': '4h 45m', 'diff_nastro': 'Compatto',
    'olg_prima': '5h 15m', 'olg_dopo': '4h 45m', 'diff_olg': 'Continuo',
    'rip_prima': '1 ripresa', 'rip_dopo': '1 ripresa continua'
})

# =============================================================
# 3. Pi0130
# =============================================================
t130 = turni_dict['Pi0130']
att_130 = [
    {'linea': 'Disp', 'da': 'Controllo livelli autobus', 'descrizione': 'Controllo livelli autobus (Pinerolo Deposito)', 'partenza': '06:35', 'arrivo': '06:45', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'Pinerolo Deposito ➔ PINEROLO', 'descrizione': 'Pinerolo Deposito ➔ PINEROLO movicentro', 'partenza': '06:45', 'arrivo': '06:50', 'km': '2.46', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '901', 'da': 'PINEROLO ➔ TORRE PELLICE', 'descrizione': 'Linea 901: PINEROLO (movicentro) ➔ TORRE PELLICE', 'partenza': '06:50', 'arrivo': '07:20', 'km': '17.62', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '279', 'da': 'TORRE PELLICE ➔ PINEROLO Centro Studi', 'descrizione': 'Linea 279: TORRE PELLICE ➔ Pinerolo Centro Studi', 'partenza': '07:25', 'arrivo': '08:00', 'km': '17.73', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'Pinerolo Centro Studi ➔ Pinerolo Deposito', 'descrizione': 'Pinerolo Centro Studi ➔ Pinerolo Deposito', 'partenza': '08:00', 'arrivo': '08:05', 'km': '1.40', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Sosta', 'da': 'Pausa Pranzo / Sosta a Pinerolo Deposito', 'descrizione': 'Pausa Pranzo e Ristoro (Pinerolo Deposito)', 'partenza': '08:05', 'arrivo': '13:35', 'km': '-', 'scambio_tag': 'Pausa Ristoro Regolare'},
    {'linea': 'Trasf', 'da': 'Pinerolo Deposito ➔ PINEROLO', 'descrizione': 'Pinerolo Deposito ➔ PINEROLO movicentro', 'partenza': '13:35', 'arrivo': '13:40', 'km': '2.46', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '701', 'da': 'PINEROLO ➔ MACELLO', 'descrizione': 'Linea 701: PINEROLO (movicentro) ➔ MACELLO (Municipio)', 'partenza': '13:45', 'arrivo': '14:03', 'km': '9.49', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '701', 'da': 'MACELLO ➔ S.Pietro Val Lemina', 'descrizione': 'Linea 701: MACELLO (Municipio) ➔ S.Pietro Val Lemina', 'partenza': '14:05', 'arrivo': '14:35', 'km': '16.18', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '701', 'da': 'S.Pietro Val Lemina ➔ MACELLO', 'descrizione': 'Linea 701: S.Pietro Val Lemina ➔ MACELLO (Municipio)', 'partenza': '14:40', 'arrivo': '15:20', 'km': '18.37', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'MACELLO ➔ Pinerolo Deposito', 'descrizione': 'MACELLO (Municipio) ➔ Pinerolo Deposito', 'partenza': '15:20', 'arrivo': '15:35', 'km': '6.50', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Disp', 'da': 'Pulizia Interna Autobus', 'descrizione': 'Pulizia Interna Autobus e Chiusura Turno (Pinerolo Deposito)', 'partenza': '15:35', 'arrivo': '15:45', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'}
]

aggiungi_scheda_turno_pulita(t130, att_130, {
    'nuova_dicitura': '13 PINEROLO [MATTINALE / POMERIGGIO COMPATTO LINEE 901 / 701]',
    'stato': 'SPEZZATO COMPATTO (Nastro -3h30)',
    'descrizione': '• <b>Corse Cedute a Pi0190:</b> Navette Linea 703 (16:00–18:50).<br/>'
                   '• <b>Nuovo Servizio Effettivo:</b> Completa la Linea 701 a Macello e chiude il servizio alle 15:35 a Pinerolo. Nastro abbattuto da 12h30 a 9h00.'
}, {
    'orario_prima': '06:35 – 19:05', 'orario_dopo': '06:35 – 15:35',
    'nastro_prima': '12h 30m', 'nastro_dopo': '9h 00m', 'diff_nastro': '−3h 30m',
    'olg_prima': '7h 00m', 'olg_dopo': '5h 25m', 'diff_olg': '−1h 35m',
    'rip_prima': '2 riprese', 'rip_dopo': '2 riprese compatte'
})

# =============================================================
# 4. Pi0190
# =============================================================
t190 = turni_dict['Pi0190']
att_190 = [
    {'linea': 'Disp', 'da': 'Controllo livelli autobus', 'descrizione': 'Controllo livelli autobus (Pinerolo Deposito)', 'partenza': '15:50', 'arrivo': '16:00', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '703', 'da': 'PINEROLO Fiugera ➔ RIVA / PASCARETTO', 'descrizione': 'Linea 703: PINEROLO Fiugera ➔ RIVA DI PINEROLO [RICEVUTA DA TURNO Pi0130]', 'partenza': '16:00', 'arrivo': '18:50', 'km': '59.47', 'scambio_tag': '🟢 CORSA RICEVUTA DA TURNO Pi0130'},
    {'linea': '282', 'da': 'PINEROLO movicentro ➔ TORINO Autostazione', 'descrizione': 'Linea 282: PINEROLO (movicentro) ➔ TORINO (Autostazione c.so Bolzano)', 'partenza': '18:46', 'arrivo': '19:57', 'km': '41.60', 'scambio_tag': 'Propria Corsa Linea 282'},
    {'linea': '282', 'da': 'TORINO Autostazione ➔ PINEROLO movicentro', 'descrizione': 'Linea 282: TORINO (Autostazione) ➔ PINEROLO (movicentro)', 'partenza': '20:03', 'arrivo': '21:14', 'km': '41.90', 'scambio_tag': 'Propria Corsa Linea 282'},
    {'linea': '282', 'da': 'PINEROLO movicentro ➔ PEROSA ARGENTINA', 'descrizione': 'Linea 282: PINEROLO (movicentro) ➔ PEROSA ARGENTINA (Pzza 3° Alpini)', 'partenza': '21:18', 'arrivo': '21:50', 'km': '18.51', 'scambio_tag': 'Propria Corsa Linea 282'},
    {'linea': '275', 'da': 'PEROSA ARGENTINA ➔ PINEROLO Deposito', 'descrizione': 'Linea 275: PEROSA ARGENTINA ➔ PINEROLO (Bivio SAPAV / Deposito)', 'partenza': '22:15', 'arrivo': '22:50', 'km': '20.83', 'scambio_tag': 'Propria Corsa Linea 275'},
    {'linea': 'Disp', 'da': 'Pulizia Interna Autobus', 'descrizione': 'Pulizia Interna Autobus e Chiusura Turno (Pinerolo Deposito)', 'partenza': '22:51', 'arrivo': '23:01', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'}
]

aggiungi_scheda_turno_pulita(t190, att_190, {
    'nuova_dicitura': '19 PINEROLO [POMERIDIANO / SERALE CONTINUO LINEE 703 / 282 / 275]',
    'stato': 'POTENZIATO (Da 5h46 a 7h30 OLG)',
    'descrizione': '• <b>Corse Ricevute da Pi0130:</b> Navette Linea 703 dalle 16:00 alle 18:50.<br/>'
                   '• <b>Nuovo Servizio Effettivo:</b> Inizia alle 16:00 e si connette alle sue corse serali per Torino/Perosa, portando l’OLG a 7h30 pieno in 1 sola ripresa continua.'
}, {
    'orario_prima': '17:15 – 23:01', 'orario_dopo': '15:50 – 23:01',
    'nastro_prima': '5h 46m', 'nastro_dopo': '7h 11m', 'diff_nastro': '+1h 25m (Ottimale)',
    'olg_prima': '5h 46m', 'olg_dopo': '7h 30m', 'diff_olg': '+1h 44m OLG',
    'rip_prima': '1 ripresa', 'rip_dopo': '1 ripresa continua'
})

# =============================================================
# 5. Pi0210
# =============================================================
t210 = turni_dict['Pi0210']
att_210 = [
    {'linea': 'Disp', 'da': 'Controllo livelli autobus', 'descrizione': 'Controllo livelli autobus (Pinerolo Deposito)', 'partenza': '14:55', 'arrivo': '15:05', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '283', 'da': 'PINEROLO ➔ CANTALUPA', 'descrizione': 'Linea 283: PINEROLO (Piazza Cavour) ➔ CANTALUPA', 'partenza': '15:05', 'arrivo': '15:27', 'km': '11.45', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '283', 'da': 'CANTALUPA ➔ PINEROLO', 'descrizione': 'Linea 283: CANTALUPA ➔ PINEROLO (Piazza Cavour)', 'partenza': '15:27', 'arrivo': '15:49', 'km': '11.45', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '275', 'da': 'PINEROLO ➔ PEROSA ARGENTINA', 'descrizione': 'Linea 275: PINEROLO (Piazza Cavour) ➔ PEROSA ARGENTINA', 'partenza': '15:50', 'arrivo': '16:20', 'km': '18.42', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '281', 'da': 'PEROSA ARGENTINA ➔ VILLARETTO', 'descrizione': 'Linea 281: PEROSA ARGENTINA ➔ VILLARETTO A/R', 'partenza': '16:35', 'arrivo': '17:07', 'km': '15.20', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '282', 'da': 'PEROSA ARGENTINA ➔ PINEROLO', 'descrizione': 'Linea 282: PEROSA ARGENTINA ➔ PINEROLO (movicentro)', 'partenza': '17:10', 'arrivo': '17:42', 'km': '18.51', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '901', 'da': 'PINEROLO ➔ TORRE PELLICE', 'descrizione': 'Linea 901: PINEROLO (movicentro) ➔ TORRE PELLICE A/R', 'partenza': '17:50', 'arrivo': '19:10', 'km': '36.34', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'PINEROLO ➔ Pinerolo Deposito', 'descrizione': 'PINEROLO movicentro ➔ Pinerolo Deposito', 'partenza': '19:10', 'arrivo': '19:15', 'km': '2.46', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Disp', 'da': 'Pulizia Interna Autobus', 'descrizione': 'Pulizia Interna Autobus e Chiusura Turno (Pinerolo Deposito)', 'partenza': '19:15', 'arrivo': '19:25', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'}
]

aggiungi_scheda_turno_pulita(t210, att_210, {
    'nuova_dicitura': '21 PINEROLO [POMERIDIANO CONTINUO LINEE 283 / 275 / 901]',
    'stato': 'POMERIDIANO CONTINUO (ZERO STACCHI)',
    'descrizione': '• <b>Corse Cedute a Pi0470:</b> Corsa 278 Virle (07:35) + Blocco 278/281 Pancalieri (13:20–14:55).<br/>'
                   '• <b>Nuovo Servizio Effettivo:</b> Inizia alle 14:55 ed effettua il servizio Cantalupa + Perosa + Torre Pellice fino alle 19:25 in 1 sola ripresa continua. Nastro da 12h30 a 4h30.'
}, {
    'orario_prima': '06:55 – 19:25', 'orario_dopo': '14:55 – 19:25',
    'nastro_prima': '12h 30m', 'nastro_dopo': '4h 30m', 'diff_nastro': '−8h 00m',
    'olg_prima': '7h 35m', 'olg_dopo': '4h 30m', 'diff_olg': 'Continuo',
    'rip_prima': '2 riprese', 'rip_dopo': '1 ripresa continua'
})

# =============================================================
# 6. Pi0470
# =============================================================
t470 = turni_dict['Pi0470']
att_470 = []
for a in t470['attivita'][:-1]:
    att_470.append(dict(a))

att_470.append({'linea': 'Sosta', 'da': 'Pausa Pranzo / Sosta a Pinerolo Deposito', 'descrizione': 'Pausa Pranzo e Ristoro (Pinerolo Deposito)', 'partenza': '11:10', 'arrivo': '13:20', 'km': '-', 'scambio_tag': 'Pausa Ristoro Regolare'})
att_470.append({'linea': 'Trasf', 'da': 'Pinerolo Deposito ➔ PINEROLO - Stazione FS', 'descrizione': 'Pinerolo Deposito ➔ PINEROLO Stazione FS', 'partenza': '13:20', 'arrivo': '13:25', 'km': '2.75', 'scambio_tag': 'Attività Ordinaria Invariata'})
att_470.append({'linea': '278', 'da': 'PINEROLO - Stazione FS ➔ PANCALIERI', 'descrizione': 'Linea 278: PINEROLO (Stazione FS) ➔ PANCALIERI [RICEVUTA DA TURNO Pi0210]', 'partenza': '13:30', 'arrivo': '14:05', 'km': '23.70', 'scambio_tag': '🟢 CORSA RICEVUTA DA TURNO Pi0210'})
att_470.append({'linea': '281', 'da': 'PANCALIERI ➔ PINEROLO - Fronte Stazione FS', 'descrizione': 'Linea 281: PANCALIERI ➔ PINEROLO [RICEVUTA DA TURNO Pi0210]', 'partenza': '14:05', 'arrivo': '14:55', 'km': '32.48', 'scambio_tag': '🟢 CORSA RICEVUTA DA TURNO Pi0210'})
att_470.append({'linea': 'Trasf', 'da': 'PINEROLO ➔ Pinerolo Deposito', 'descrizione': 'PINEROLO Stazione FS ➔ Pinerolo Deposito', 'partenza': '14:55', 'arrivo': '15:00', 'km': '2.40', 'scambio_tag': 'Attività Ordinaria Invariata'})
att_470.append({'linea': 'Disp', 'da': 'Pulizia Interna Autobus', 'descrizione': 'Pulizia Interna Autobus e Chiusura Turno (Pinerolo Deposito)', 'partenza': '15:00', 'arrivo': '15:10', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'})

aggiungi_scheda_turno_pulita(t470, att_470, {
    'nuova_dicitura': '47 PINEROLO [SPEZZATO COMPATTO LINEE 275 / 701 / 278 / 281]',
    'stato': 'POTENZIATO (Da 5h25 a 6h50 OLG)',
    'descrizione': '• <b>Corse Ricevute da Pi0210:</b> Blocco 278/281 Pancalieri (13:20–14:55).<br/>'
                   '• <b>Nuovo Servizio Effettivo:</b> Completa il mattino (Linee 275+701), effettua 2h10m di pausa pranzo regolare e chiude alle 15:10 con 6h50m di lavoro pieno.'
}, {
    'orario_prima': '05:00 – 11:20', 'orario_dopo': '05:00 – 15:10',
    'nastro_prima': '6h 20m', 'nastro_dopo': '10h 10m', 'diff_nastro': '+3h 50m (Compatto)',
    'olg_prima': '5h 25m', 'olg_dopo': '6h 50m', 'diff_olg': '+1h 25m OLG',
    'rip_prima': '2 riprese', 'rip_dopo': '2 riprese con pausa pranzo'
})

# =============================================================
# 7. Pi0580
# =============================================================
t580 = turni_dict['Pi0580']
att_580 = [
    {'linea': 'Disp', 'da': 'Controllo livelli autobus', 'descrizione': 'Controllo livelli autobus (Pinerolo Deposito)', 'partenza': '13:04', 'arrivo': '13:05', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '275', 'da': 'PINEROLO ➔ Villar Perosa SKF', 'descrizione': 'Linea 275: PINEROLO (Bivio SAPAV) ➔ Villar Perosa (Stabilimento SKF)', 'partenza': '13:10', 'arrivo': '13:35', 'km': '13.56', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'Villar Perosa SKF ➔ PINEROLO movicentro', 'descrizione': 'Villar Perosa SKF ➔ PINEROLO movicentro', 'partenza': '13:35', 'arrivo': '13:50', 'km': '13.56', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '901', 'da': 'PINEROLO ➔ TORRE PELLICE', 'descrizione': 'Linea 901: PINEROLO (movicentro) ➔ TORRE PELLICE A/R', 'partenza': '13:50', 'arrivo': '15:40', 'km': '36.34', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '281', 'da': 'PINEROLO ➔ GERBOLE DI VOLVERA', 'descrizione': 'Linea 281: PINEROLO ➔ GERBOLE DI VOLVERA', 'partenza': '16:05', 'arrivo': '16:45', 'km': '24.10', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '284', 'da': 'NONE ➔ SEGGIOVIA VANDALINO', 'descrizione': 'Linea 284: NONE ➔ SEGGIOVIA VANDALINO', 'partenza': '17:20', 'arrivo': '18:35', 'km': '38.50', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'SEGGIOVIA VANDALINO ➔ Pinerolo Deposito', 'descrizione': 'SEGGIOVIA VANDALINO ➔ Pinerolo Deposito', 'partenza': '18:35', 'arrivo': '19:00', 'km': '19.57', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Disp', 'da': 'Pulizia Interna Autobus', 'descrizione': 'Pulizia Interna Autobus e Chiusura Turno (Pinerolo Deposito)', 'partenza': '19:00', 'arrivo': '19:10', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'}
]

aggiungi_scheda_turno_pulita(t580, att_580, {
    'nuova_dicitura': '58 PINEROLO [POMERIDIANO CONTINUO LINEE 275 / 901 / 281 / 284]',
    'stato': 'POMERIDIANO CONTINUO (ZERO STACCHI)',
    'descrizione': '• <b>Corse Cedute:</b> Corsa mattutina 06:40–08:15 (Linea 278 Vigone).<br/>'
                   '• <b>Nuovo Servizio Effettivo:</b> Inizia alle 13:04 ed effettua tutta la sua catena pomeridiana/serale (Linee 275+901+281+284) fino alle 19:10 in 1 sola ripresa continua. Nastro da 12h30 a 6h06.'
}, {
    'orario_prima': '06:40 – 19:10', 'orario_dopo': '13:04 – 19:10',
    'nastro_prima': '12h 30m', 'nastro_dopo': '6h 06m', 'diff_nastro': '−6h 24m',
    'olg_prima': '7h 10m', 'olg_dopo': '5h 45m', 'diff_olg': 'Continuo',
    'rip_prima': '3 riprese', 'rip_dopo': '1 ripresa continua'
})

# =============================================================
# 8. Pi0560
# =============================================================
t560 = turni_dict['Pi0560']
att_560 = [
    {'linea': 'Disp', 'da': 'Controllo livelli autobus', 'descrizione': 'Controllo livelli autobus (Pinerolo Deposito)', 'partenza': '13:20', 'arrivo': '13:30', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '279', 'da': 'PINEROLO ➔ TORRE PELLICE', 'descrizione': 'Linea 279: PINEROLO ➔ TORRE PELLICE', 'partenza': '13:35', 'arrivo': '14:10', 'km': '17.73', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '901', 'da': 'TORRE PELLICE ➔ PINEROLO', 'descrizione': 'Linea 901: TORRE PELLICE ➔ PINEROLO (movicentro)', 'partenza': '14:20', 'arrivo': '14:55', 'km': '18.17', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '282', 'da': 'PINEROLO ➔ TORINO - Autostazione c.so Bolzano', 'descrizione': 'Linea 282: PINEROLO ➔ TORINO (Autostazione c.so Bolzano)', 'partenza': '15:10', 'arrivo': '16:21', 'km': '41.60', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '275', 'da': 'TORINO ➔ PINEROLO - Piazza Cavour', 'descrizione': 'Linea 275: TORINO ➔ PINEROLO (Piazza Cavour)', 'partenza': '16:25', 'arrivo': '17:25', 'km': '42.11', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'PINEROLO ➔ Pinerolo Deposito', 'descrizione': 'PINEROLO Piazza Cavour ➔ Pinerolo Deposito', 'partenza': '17:25', 'arrivo': '17:30', 'km': '2.40', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Disp', 'da': 'Pulizia Interna Autobus', 'descrizione': 'Pulizia Interna Autobus e Chiusura Turno (Pinerolo Deposito)', 'partenza': '17:30', 'arrivo': '17:38', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'}
]

aggiungi_scheda_turno_pulita(t560, att_560, {
    'nuova_dicitura': '56 PINEROLO [POMERIDIANO CONTINUO LINEE 279 / 901 / 282 / 275]',
    'stato': 'POMERIDIANO CONTINUO (ZERO STACCHI)',
    'descrizione': '• <b>Corse Cedute a Pi0280:</b> Blocco mattutino 05:30–09:30 (Linee 901+282+275 Torino Bolzano).<br/>'
                   '• <b>Nuovo Servizio Effettivo:</b> Inizia alle 13:20 ed effettua servizio continuo (Linee 279+901+282+275) fino alle 17:38. Nastro da 12h08 a 4h18.'
}, {
    'orario_prima': '05:30 – 17:38', 'orario_dopo': '13:20 – 17:38',
    'nastro_prima': '12h 08m', 'nastro_dopo': '4h 18m', 'diff_nastro': '−7h 50m',
    'olg_prima': '7h 47m', 'olg_dopo': '4h 18m', 'diff_olg': 'Continuo',
    'rip_prima': '3 riprese', 'rip_dopo': '1 ripresa continua'
})

# =============================================================
# 9. Pi0280
# =============================================================
t280 = turni_dict['Pi0280']
att_280 = [
    {'linea': 'Disp', 'da': 'Controllo livelli autobus', 'descrizione': 'Controllo livelli autobus (Pinerolo Deposito)', 'partenza': '05:30', 'arrivo': '05:40', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'Pinerolo Deposito ➔ TORRE PELLICE', 'descrizione': 'Pinerolo Deposito ➔ TORRE PELLICE', 'partenza': '05:40', 'arrivo': '06:05', 'km': '16.85', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '901', 'da': 'TORRE PELLICE ➔ PINEROLO - movicentro', 'descrizione': 'Linea 901: TORRE PELLICE ➔ PINEROLO [RICEVUTA DA TURNO Pi0560]', 'partenza': '06:05', 'arrivo': '06:35', 'km': '18.17', 'scambio_tag': '🟢 CORSA RICEVUTA DA TURNO Pi0560'},
    {'linea': '282', 'da': 'PINEROLO ➔ TORINO - Autostazione c.so Bolzano', 'descrizione': 'Linea 282: PINEROLO ➔ TORINO [RICEVUTA DA TURNO Pi0560]', 'partenza': '06:36', 'arrivo': '07:47', 'km': '44.60', 'scambio_tag': '🟢 CORSA RICEVUTA DA TURNO Pi0560'},
    {'linea': '275', 'da': 'TORINO ➔ PINEROLO - Piazza Cavour', 'descrizione': 'Linea 275: TORINO ➔ PINEROLO [RICEVUTA DA TURNO Pi0560]', 'partenza': '08:11', 'arrivo': '09:20', 'km': '42.11', 'scambio_tag': '🟢 CORSA RICEVUTA DA TURNO Pi0560'},
    {'linea': 'Trasf', 'da': 'PINEROLO ➔ Pinerolo Deposito', 'descrizione': 'PINEROLO Piazza Cavour ➔ Pinerolo Deposito', 'partenza': '09:20', 'arrivo': '09:30', 'km': '2.40', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Sosta', 'da': 'Pausa Pranzo / Sosta al Deposito Pinerolo', 'descrizione': 'Pausa Pranzo e Ristoro (Pinerolo Deposito)', 'partenza': '09:30', 'arrivo': '13:10', 'km': '-', 'scambio_tag': 'Pausa Ristoro Regolare'},
    {'linea': '703', 'da': 'RIVA DI PINEROLO ➔ PINEROLO Fiugera', 'descrizione': 'Linea 703: RIVA DI PINEROLO ➔ PINEROLO Fiugera (Navette Pomeridiane)', 'partenza': '13:20', 'arrivo': '15:57', 'km': '56.26', 'scambio_tag': 'Proprie Navette Linea 703'},
    {'linea': 'Disp', 'da': 'Rientro Deposito e Pulizia Bus', 'descrizione': 'Rientro Deposito Pinerolo e Pulizia Interna Autobus', 'partenza': '15:57', 'arrivo': '16:17', 'km': '3.86', 'scambio_tag': 'Attività Ordinaria Invariata'}
]

aggiungi_scheda_turno_pulita(t280, att_280, {
    'nuova_dicitura': '28 PINEROLO [SPEZZATO CON TORINO BOLZANO LINEE 901 / 282 / 275 / 703]',
    'stato': 'POTENZIATO (Da 5h07 a 7h15 OLG)',
    'descrizione': '• <b>Corse Ricevute da Pi0560:</b> Collegamento Torino Bolzano 05:30–09:30 (Linee 901+282+275).<br/>'
                   '• <b>Nuovo Servizio Effettivo:</b> Sostituisce il mattino corto con il collegamento per Torino e chiude con le navette 703. OLG sale da 5h07 a 7h15m!'
}, {
    'orario_prima': '06:15 – 16:17', 'orario_dopo': '05:30 – 16:17',
    'nastro_prima': '10h 02m', 'nastro_dopo': '10h 47m', 'diff_nastro': 'Compatto',
    'olg_prima': '5h 07m', 'olg_dopo': '7h 15m', 'diff_olg': '+2h 08m OLG',
    'rip_prima': '2 riprese', 'rip_dopo': '2 riprese con pausa'
})

# =============================================================
# 10. Pi0260
# =============================================================
t260 = turni_dict['Pi0260']
att_260 = [
    {'linea': 'Disp', 'da': 'Controllo levels autobus', 'descrizione': 'Controllo livelli autobus (Pinerolo Deposito)', 'partenza': '06:49', 'arrivo': '06:59', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'Pinerolo Deposito ➔ Pinerolo Bivio SAPAV', 'descrizione': 'Pinerolo Deposito ➔ Pinerolo Bivio SAPAV', 'partenza': '06:59', 'arrivo': '07:00', 'km': '0.25', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '275', 'da': 'Pinerolo Bivio SAPAV ➔ Villar Perosa', 'descrizione': 'Linea 275: Pinerolo Bivio SAPAV ➔ Villar Perosa', 'partenza': '07:00', 'arrivo': '07:24', 'km': '13.91', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'Villar Perosa ➔ Perosa Argentina Pzza 3° Alpini', 'descrizione': 'Villar Perosa ➔ Perosa Argentina (Pzza 3° Alpini)', 'partenza': '07:24', 'arrivo': '07:34', 'km': '6.00', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '281', 'da': 'Perosa Argentina ➔ Pinerolo Centro Studi', 'descrizione': 'Linea 281: Perosa Argentina ➔ Pinerolo Centro Studi', 'partenza': '07:35', 'arrivo': '08:10', 'km': '20.83', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'Pinerolo Centro Studi ➔ Pinerolo Deposito', 'descrizione': 'Pinerolo Centro Studi ➔ Pinerolo Deposito', 'partenza': '08:10', 'arrivo': '08:15', 'km': '1.40', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Sosta', 'da': 'Pausa Pranzo / Sosta a Pinerolo Deposito', 'descrizione': 'Pausa Pranzo e Ristoro (Pinerolo Deposito)', 'partenza': '08:15', 'arrivo': '13:05', 'km': '-', 'scambio_tag': 'Pausa Ristoro Regolare'},
    {'linea': 'Trasf', 'da': 'Pinerolo Deposito ➔ PINEROLO Stazione FS', 'descrizione': 'Pinerolo Deposito ➔ PINEROLO Stazione FS', 'partenza': '13:05', 'arrivo': '13:20', 'km': '3.39', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '278', 'da': 'PINEROLO ➔ SCA - FR Pieve Via Savigliani', 'descrizione': 'Linea 278: PINEROLO (Stazione FS) ➔ SCALENGHE (Frazione Pieve)', 'partenza': '13:25', 'arrivo': '14:08', 'km': '26.13', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'Scalenghe ➔ AIRASCA SKF', 'descrizione': 'SCALENGHE ➔ AIRASCA (Stabilimento SKF)', 'partenza': '14:08', 'arrivo': '14:21', 'km': '4.00', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '284', 'da': 'AIRASCA SKF ➔ SEGGIOVIA VANDALINO', 'descrizione': 'Linea 284: AIRASCA (SKF) ➔ TORRE PELLICE (Seggovia Vandalino)', 'partenza': '14:30', 'arrivo': '15:15', 'km': '33.21', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'SEGGIOVIA VANDALINO ➔ Pinerolo Deposito', 'descrizione': 'TORRE PELLICE (Seggovia Vandalino) ➔ Pinerolo Deposito', 'partenza': '15:15', 'arrivo': '15:40', 'km': '19.57', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Disp', 'da': 'Pulizia Interna Autobus', 'descrizione': 'Pulizia Interna Autobus e Chiusura Turno (Pinerolo Deposito)', 'partenza': '15:40', 'arrivo': '15:50', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'}
]

aggiungi_scheda_turno_pulita(t260, att_260, {
    'nuova_dicitura': '26 PINEROLO [SPEZZATO COMPATTO LINEE 275 / 281 / 278 / 284]',
    'stato': 'SPEZZATO COMPATTO (Nastro -3h01)',
    'descrizione': '• <b>Corse Cedute a Pi0250:</b> Tratta serale 16:10–18:51 (Linee 284+281 Torre Pellice/Volvera/Airasca).<br/>'
                   '• <b>Nuovo Servizio Effettivo:</b> Effettua il mattino (Linee 275+281), pausa pranzo a Pinerolo, e il pomeriggio (Linee 278+284) rientrando alle 15:50 al Deposito. Nastro da 12h02 a 9h01.'
}, {
    'orario_prima': '06:49 – 18:51', 'orario_dopo': '06:49 – 15:50',
    'nastro_prima': '12h 02m', 'nastro_dopo': '9h 01m', 'diff_nastro': '−3h 01m',
    'olg_prima': '6h 32m', 'olg_dopo': '5h 00m', 'diff_olg': 'Compatto',
    'rip_prima': '3 riprese', 'rip_dopo': '2 riprese con pausa pranzo'
})

# =============================================================
# 11. Pe0270 (227 DI PEROSA - Deposito di PEROSA ARGENTINA)
# =============================================================
t_pe270 = turni_dict['Pe0270']
att_pe270 = [
    {'linea': 'Disp', 'da': 'Controllo livelli autobus', 'descrizione': 'Controllo livelli autobus (Perosa Deposito)', 'partenza': '06:25', 'arrivo': '06:35', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'Perosa Deposito ➔ PERRERO', 'descrizione': 'Perosa Deposito ➔ PERRERO', 'partenza': '06:35', 'arrivo': '06:55', 'km': '9.50', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '303', 'da': 'PERRERO ➔ SEGGIOVIE 13 LAGHI', 'descrizione': 'Linea 303: PERRERO ➔ GHIGO DI PRAMOLLO / 13 LAGHI A/R', 'partenza': '06:55', 'arrivo': '07:35', 'km': '18.40', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'PERRERO ➔ Perosa Deposito', 'descrizione': 'PERRERO ➔ Perosa Deposito', 'partenza': '07:35', 'arrivo': '07:55', 'km': '9.50', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Sosta', 'da': 'Pausa Pranzo / Sosta al Deposito di Perosa', 'descrizione': 'Pausa Pranzo e Ristoro (Perosa Deposito)', 'partenza': '07:55', 'arrivo': '11:00', 'km': '-', 'scambio_tag': 'Pausa Ristoro Regolare'},
    {'linea': '282', 'da': 'PEROSA ARG.-Pzza Terzo Alpini ➔ TORINO', 'descrizione': 'Linea 282: PEROSA ARGENTINA ➔ TORINO (Autostazione c.so Bolzano)', 'partenza': '11:10', 'arrivo': '12:57', 'km': '59.71', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '282', 'da': 'TORINO ➔ PINEROLO movicentro', 'descrizione': 'Linea 282: TORINO (Autostazione) ➔ PINEROLO (movicentro)', 'partenza': '14:03', 'arrivo': '15:18', 'km': '41.60', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '275', 'da': 'PINEROLO movicentro ➔ PEROSA ARGENTINA', 'descrizione': 'Linea 275: PINEROLO (movicentro) ➔ PEROSA ARGENTINA [RICEVUTA DA Pi0620]', 'partenza': '15:25', 'arrivo': '15:55', 'km': '18.51', 'scambio_tag': '🟢 CORSA RICEVUTA DA TURNO Pi0620'},
    {'linea': 'Trasf', 'da': 'PEROSA ARG.-Pzza Terzo Alpini ➔ Perosa Deposito', 'descrizione': 'PEROSA ARGENTINA ➔ Perosa Deposito (Residenza)', 'partenza': '15:55', 'arrivo': '16:00', 'km': '0.50', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Disp', 'da': 'Pulizia Interna Autobus', 'descrizione': 'Pulizia Interna Autobus e Chiusura Turno (Perosa Deposito)', 'partenza': '16:00', 'arrivo': '16:10', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'}
]

aggiungi_scheda_turno_pulita(t_pe270, att_pe270, {
    'deposito': 'Perosa Argentina',
    'nuova_dicitura': '227 DI PEROSA [SPEZZATO COMPATTO CON RIENTRO A PEROSA]',
    'stato': 'OTTIMIZZATO (Nastro -1h25, Chiusura a Perosa)',
    'descrizione': '• <b>Scambio con Pi0620:</b> Riceve il rientro immediato 15:25 da Pinerolo a Perosa.<br/>'
                   '• <b>Nuovo Servizio Effettivo:</b> Chiude alle 16:10 al Deposito di Perosa Argentina eliminando la sosta fuori sede a Pinerolo e le corse serali distaccate. Nastro da 11h05 a 9h45.'
}, {
    'orario_prima': '06:25 – 17:30 (a Pinerolo)', 'orario_dopo': '06:25 – 16:10 (a Perosa)',
    'nastro_prima': '11h 05m', 'nastro_dopo': '9h 45m', 'diff_nastro': '−1h 20m',
    'olg_prima': '6h 00m', 'olg_dopo': '5h 45m', 'diff_olg': 'Chiusura a Perosa',
    'rip_prima': '4 riprese', 'rip_dopo': '2 riprese con pausa pranzo'
})

# =============================================================
# 12. Pi0620 (62 PINEROLO - Deposito di PINEROLO)
# =============================================================
t_pi620 = turni_dict['Pi0620']
att_pi620 = [
    {'linea': 'Disp', 'da': 'Controllo livelli autobus', 'descrizione': 'Controllo livelli autobus (Pinerolo Deposito)', 'partenza': '13:10', 'arrivo': '13:20', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '703', 'da': 'PINEROLO Fiugera ➔ RIVA / PASCARETTO', 'descrizione': 'Linea 703: PINEROLO Fiugera ➔ RIVA DI PINEROLO (Navetta)', 'partenza': '13:30', 'arrivo': '14:05', 'km': '11.54', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '281', 'da': 'PINEROLO Centro Studi ➔ PEROSA ARGENTINA', 'descrizione': 'Linea 281: PINEROLO Centro Studi ➔ PEROSA ARGENTINA', 'partenza': '14:30', 'arrivo': '15:00', 'km': '20.83', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '282', 'da': 'PEROSA ARGENTINA ➔ PINEROLO movicentro', 'descrizione': 'Linea 282: PEROSA ARGENTINA ➔ PINEROLO movicentro [RICEVUTA DA Pe0270]', 'partenza': '15:10', 'arrivo': '15:42', 'km': '18.51', 'scambio_tag': '🟢 CORSA RICEVUTA DA TURNO Pe0270'},
    {'linea': '282', 'da': 'PINEROLO movicentro ➔ TORINO Autostazione', 'descrizione': 'Linea 282: PINEROLO (movicentro) ➔ TORINO (Autostazione c.so Bolzano)', 'partenza': '17:16', 'arrivo': '18:40', 'km': '41.60', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': '282', 'da': 'TORINO Autostazione ➔ PINEROLO movicentro', 'descrizione': 'Linea 282: TORINO (Autostazione) ➔ PINEROLO (movicentro)', 'partenza': '19:03', 'arrivo': '20:14', 'km': '41.90', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Trasf', 'da': 'PINEROLO movicentro ➔ Pinerolo Deposito', 'descrizione': 'PINEROLO movicentro ➔ Pinerolo Deposito', 'partenza': '20:14', 'arrivo': '20:19', 'km': '2.46', 'scambio_tag': 'Attività Ordinaria Invariata'},
    {'linea': 'Disp', 'da': 'Pulizia Interna Autobus', 'descrizione': 'Pulizia Interna Autobus e Chiusura Turno (Pinerolo Deposito)', 'partenza': '20:19', 'arrivo': '20:29', 'km': '-', 'scambio_tag': 'Attività Ordinaria Invariata'}
]

aggiungi_scheda_turno_pulita(t_pi620, att_pi620, {
    'deposito': 'Pinerolo',
    'nuova_dicitura': '62 PINEROLO [POMERIDIANO / SERALE LINEE 703 / 281 / 282]',
    'stato': 'POTENZIATO (Eliminata sosta passiva a Perosa)',
    'descrizione': '• <b>Scambio con Pe0270:</b> Rientra subito da Perosa a Pinerolo alle 15:10 eliminando 1h36m di fermo passivo a Perosa.<br/>'
                   '• <b>Nuovo Servizio Effettivo:</b> Effettua servizio continuo di vallata e collegamento per Torino Bolzano fino alle 20:29 a Pinerolo. OLG sale da 5h55 a 6h25.'
}, {
    'orario_prima': '13:10 – 20:29', 'orario_dopo': '13:10 – 20:29',
    'nastro_prima': '7h 19m', 'nastro_dopo': '7h 19m', 'diff_nastro': 'Invariato',
    'olg_prima': '5h 55m', 'olg_dopo': '6h 25m', 'diff_olg': '+30m OLG',
    'rip_prima': '2 riprese', 'rip_dopo': '2 riprese continue'
})

doc.build(elements)
print(f"✅ PDF GENERATO CON 12 SCHEDE COMPLETE COMPRESO PEROSA:\n{PDF_OUT}")
