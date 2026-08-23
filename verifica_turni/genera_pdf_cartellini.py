import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

pdf_out = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Proposta_Nuovi_Cartellini_2026_Ottimizzati.pdf"

doc = SimpleDocTemplate(
    pdf_out,
    pagesize=landscape(A4),
    leftMargin=20,
    rightMargin=20,
    topMargin=20,
    bottomMargin=20
)

styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=13,
    leading=15,
    textColor=colors.HexColor('#003366')
)
sub_style = ParagraphStyle(
    'SubTitle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=8.5,
    leading=10,
    textColor=colors.HexColor('#444444')
)
cell_style = ParagraphStyle(
    'CellText',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=7.5,
    leading=9
)
cell_bold = ParagraphStyle(
    'CellBold',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=7.5,
    leading=9
)
header_cell = ParagraphStyle(
    'HCell',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=8,
    leading=10,
    textColor=colors.white
)

elements = []

cartellini_proposti = [
    {
        "turno": "Pe0130",
        "deposito": "PEROSA ARGENTINA",
        "desc": "TURNO 213 DI PEROSA (PROPOSTA OTTIMIZZATA)",
        "inizio": "12:00",
        "fine": "18:30",
        "nastro": "6h 30m (Attuale: 11h 35m -> Risparmio 5h 05m)",
        "olg": "6h 20m",
        "note": "Corsa mattutina 07:10 ceduta a Pinerolo (Pi0050). Inizio a Perosa h 12:00, linea Torino Bolzano/SKF/Cantalupa e rientro a Perosa h 18:30. Zero stacchi a vuoto.",
        "righe": [
            ["12:00", "12:05", "Disp", "Controllo livelli autobus", "-", "0:05", "Perosa Deposito"],
            ["12:05", "12:10", "Trasf", "Perosa Deposito -> PEROSA P.za Terzo Alpini", "-", "0:05", "1,17 km"],
            ["12:10", "12:40", "000282", "PEROSA P.za Terzo Alpini -> PINEROLO P.za Cavour", "0:30", "-", "17,85 km"],
            ["12:40", "13:57", "000282", "PINEROLO P.za Cavour -> TORINO c.so Bolzano (P. Susa)", "1:17", "-", "42,27 km"],
            ["14:41", "15:50", "000275", "TORINO c.so Bolzano -> PINEROLO P.za Cavour", "1:09", "-", "42,11 km"],
            ["15:50", "15:55", "Trasf", "PINEROLO P.za Cavour -> PINEROLO Via Saluzzo (ENEL)", "-", "0:05", "0,73 km"],
            ["16:05", "16:39", "000283", "PINEROLO Via Saluzzo -> CANTALUPA", "0:34", "-", "18,24 km"],
            ["16:40", "17:00", "000283", "CANTALUPA -> PINEROLO P.za Cavour", "0:20", "-", "10,61 km"],
            ["17:00", "17:05", "Trasf", "PINEROLO P.za Cavour -> Pinerolo Bivio SAPAV", "-", "0:05", "2,42 km"],
            ["17:05", "17:15", "000284", "Pinerolo Bivio SAPAV -> AIRASCA SKF", "0:10", "-", "10,24 km"],
            ["17:30", "18:15", "000284", "AIRASCA SKF -> PEROSA P.za Terzo Alpini", "0:45", "-", "30,09 km"],
            ["18:15", "18:20", "Trasf", "PEROSA P.za Terzo Alpini -> Perosa Deposito", "-", "0:05", "1,17 km"],
            ["18:20", "18:30", "Disp", "Pulizia Interna Autobus & Chiusura Servizio", "-", "0:10", "Perosa Deposito"]
        ]
    },
    {
        "turno": "Pt0030",
        "deposito": "PONT SAINT MARTIN",
        "desc": "CAREMA-TORINO-CAREMA (PROPOSTA OTTIMIZZATA)",
        "inizio": "12:40",
        "fine": "18:33",
        "nastro": "5h 53m (Attuale: 12h 05m -> Risparmio 6h 12m)",
        "olg": "5h 45m",
        "note": "Spezzone isolato 06:28 ceduto a Pt0060/Ivrea. Inizio a Pont h 12:40, linea Torino Bolzano/Chivasso/Ivrea e rientro a Pont Deposito h 18:33 a Nastro Unico.",
        "righe": [
            ["12:40", "12:47", "Disp", "Controllo livelli autobus", "-", "0:07", "Pont Rimessa"],
            ["12:47", "12:52", "Trasf", "PONT Rimessa -> PONT P.za IV Novembre", "-", "0:05", "2,10 km"],
            ["12:52", "13:35", "000265", "PONT P.za IV Novembre -> STRAMBINO c.so Torino", "0:43", "-", "29,63 km"],
            ["13:37", "14:58", "000265", "STRAMBINO c.so Torino -> TORINO c.so Bolzano", "1:21", "-", "49,10 km"],
            ["16:10", "17:06", "000265", "TO P.za Cattaneo Mirafiori FCA -> CHIVASSO Alfa-Lancia", "0:56", "-", "45,22 km"],
            ["17:08", "17:46", "000265", "CHIVASSO Alfa-Lancia -> IVREA Stazione FS", "0:38", "-", "31,68 km"],
            ["17:48", "18:18", "000265", "IVREA Stazione FS -> PONT S.MARTIN P.za IV Nov.", "0:30", "-", "22,11 km"],
            ["18:18", "18:23", "Trasf", "PONT P.za IV Nov. -> PONT Rimessa", "-", "0:05", "2,10 km"],
            ["18:23", "18:33", "Disp", "Pulizia Interna Autobus & Chiusura Servizio", "-", "0:10", "Pont Rimessa"]
        ]
    },
    {
        "turno": "To0620",
        "deposito": "TORINO (GRUGLIASCO)",
        "desc": "TORINO-PINEROLO-TORINO (PROPOSTA OTTIMIZZATA)",
        "inizio": "06:15",
        "fine": "14:00",
        "nastro": "7h 45m (Attuale: 10h 54m -> Risparmio 3h 09m)",
        "olg": "6h 40m",
        "note": "Uscita da Grugliasco h 06:15. Arrivo a Porta Susa h 09:30: cambio turno sul posto con auto di servizio aziendale. Il bus resta in linea a Porta Susa. ZERO vuoti di bus.",
        "righe": [
            ["06:15", "06:25", "Disp", "Presa servizio & Controllo livelli", "-", "0:10", "Grugliasco Dep."],
            ["06:25", "06:40", "Trasf", "Grugliasco Deposito -> TORINO c.so Bolzano", "-", "0:15", "8,50 km"],
            ["06:45", "07:55", "000266", "TORINO c.so Bolzano -> PINEROLO P.za Cavour", "1:10", "-", "38,50 km"],
            ["08:05", "09:20", "000266", "PINEROLO P.za Cavour -> TORINO c.so Bolzano", "1:15", "-", "38,50 km"],
            ["09:30", "09:45", "Servizio", "Cambio autista sul posto a Porta Susa (auto di servizio)", "-", "0:15", "Auto aziendale"],
            ["09:45", "10:00", "Trasf", "Rientro a Grugliasco Deposito in auto di servizio", "-", "0:15", "8,50 km (Auto)"],
            ["10:00", "14:00", "Presidio", "Disposizione / presidio tecnico a Grugliasco", "-", "4:00", "Grugliasco Dep."]
        ]
    },
    {
        "turno": "To0130",
        "deposito": "TORINO (GRUGLIASCO)",
        "desc": "TORINO-IVREA-TORINO (PROPOSTA OTTIMIZZATA)",
        "inizio": "13:45",
        "fine": "19:55",
        "nastro": "6h 10m (Attuale: 9h 34m -> Risparmio 3h 24m)",
        "olg": "6h 00m",
        "note": "Eliminata l'ultima corsa notturna isolata delle 21:00 per Caselle. Fine linea h 19:36 a Porta Nuova, rientro a Grugliasco h 19:55 a Turno Unico.",
        "righe": [
            ["13:45", "13:55", "Disp", "Controllo livelli autobus", "-", "0:10", "Grugliasco Dep."],
            ["13:55", "14:25", "Trasf", "Grugliasco Deposito -> TO P.za Carlo Felice", "-", "0:30", "9,15 km"],
            ["14:30", "15:07", "000268", "TO P.za Carlo Felice -> CASELLE Aeroporto", "0:37", "-", "19,49 km"],
            ["15:30", "16:15", "000268", "CASELLE Aeroporto -> TO P.za Carlo Felice", "0:45", "-", "17,49 km"],
            ["16:15", "16:18", "Trasf", "TO P.za Carlo Felice -> TORINO c.so Bolzano", "-", "0:03", "1,96 km"],
            ["17:16", "18:17", "000265", "TORINO c.so Bolzano -> IVREA loc. Banchette", "1:01", "-", "50,19 km"],
            ["18:41", "19:36", "000265", "IVREA loc. Banchette -> TORINO c.so Bolzano", "0:55", "-", "50,14 km"],
            ["19:36", "19:55", "Trasf", "TORINO c.so Bolzano -> Grugliasco Deposito", "-", "0:19", "8,50 km"],
            ["19:55", "20:05", "Disp", "Pulizia Interna Autobus & Chiusura Servizio", "-", "0:10", "Grugliasco Dep."]
        ]
    },
    {
        "turno": "Pi0050",
        "deposito": "PINEROLO",
        "desc": "TURNO 5 DI PINEROLO (PROPOSTA OTTIMIZZATA)",
        "inizio": "04:50",
        "fine": "11:50",
        "nastro": "7h 00m (Attuale: 10h 55m -> Risparmio 3h 55m)",
        "olg": "6h 30m (Recupero Paga +0h 40m)",
        "note": "Assorbe la corsa mattutina 07:10 Perosa->Pinerolo. Chiusura a turno unico a Pinerolo Deposito alle 11:50 senza stacco pomeridiano.",
        "righe": [
            ["04:50", "05:00", "Disp", "Controllo livelli autobus", "-", "0:10", "Pinerolo Dep."],
            ["05:00", "05:10", "Trasf", "Pinerolo Deposito -> PINEROLO P.za Cavour", "-", "0:10", "2,40 km"],
            ["05:10", "06:15", "000275", "PINEROLO P.za Cavour -> SESTRIERE", "1:05", "-", "42,00 km"],
            ["06:20", "07:05", "000275", "SESTRIERE -> PEROSA P.za Terzo Alpini", "0:45", "-", "30,00 km"],
            ["07:10", "07:40", "000275", "PEROSA P.za Terzo Alpini -> PINEROLO Movicentro", "0:30", "-", "18,51 km"],
            ["07:45", "08:45", "000282", "PINEROLO Movicentro -> VIGONE / PANCALIERI", "1:00", "-", "25,00 km"],
            ["08:50", "09:40", "000278", "PANCALIERI -> PINEROLO P.za Cavour", "0:50", "-", "22,00 km"],
            ["09:40", "11:40", "000283", "PINEROLO Servizio locale / Cantalupa / Frazione", "2:00", "-", "35,00 km"],
            ["11:40", "11:50", "Trasf", "PINEROLO P.za Cavour -> Pinerolo Deposito", "-", "0:10", "2,40 km"]
        ]
    }
]

for idx, c in enumerate(cartellini_proposti):
    header_data = [
        [
            Paragraph(f"<b>ARRIVA ITALIA (ex SADEM)</b><br/><b>PROPOSTA SINDACALE / RISTRUTTURAZIONE TURNI 2026</b>", title_style),
            Paragraph(f"<b>CARTELLINO DI MARCIA DEL TURNO:</b> <font color='#003366' size='12'><b>{c['turno']}</b></font><br/><b>Residenza/Deposito:</b> {c['deposito']}<br/><b>Progetto di Servizio:</b> Soluzione 1 Ottimizzata (Max Nastro 10h)", sub_style)
        ]
    ]
    t_head = Table(header_data, colWidths=[380, 380])
    t_head.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_head)
    elements.append(Spacer(1, 4))

    box_data = [
        [
            Paragraph(f"<b>Inizio Servizio:</b> {c['inizio']}", cell_bold),
            Paragraph(f"<b>Fine Servizio:</b> {c['fine']}", cell_bold),
            Paragraph(f"<b>Nuovo Nastro:</b> <font color='#008800'><b>{c['nastro']}</b></font>", cell_bold),
            Paragraph(f"<b>Nuovo OLG:</b> <b>{c['olg']}</b>", cell_bold),
            Paragraph(f"<b>Deposito A/R:</b> <font color='#003366'><b>{c['deposito']}</b></font>", cell_bold),
        ]
    ]
    t_box = Table(box_data, colWidths=[100, 100, 260, 100, 200])
    t_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EBF3FA')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#003366')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBDDEE')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(t_box)
    elements.append(Spacer(1, 3))
    
    elements.append(Paragraph(f"<b>Specifiche e Scambi Corse:</b> {c['note']}", sub_style))
    elements.append(Spacer(1, 4))

    table_rows = [
        [
            Paragraph("Partenza", header_cell),
            Paragraph("Arrivo", header_cell),
            Paragraph("Linea / Tipo", header_cell),
            Paragraph("Descrizione Tratta / Attività", header_cell),
            Paragraph("Guida", header_cell),
            Paragraph("Non Guida", header_cell),
            Paragraph("Note / Km", header_cell)
        ]
    ]

    for r in c['righe']:
        table_rows.append([
            Paragraph(r[0], cell_bold),
            Paragraph(r[1], cell_bold),
            Paragraph(r[2], cell_bold),
            Paragraph(r[3], cell_style),
            Paragraph(r[4], cell_style),
            Paragraph(r[5], cell_style),
            Paragraph(r[6], cell_style)
        ])

    t_corse = Table(table_rows, colWidths=[50, 50, 70, 360, 45, 55, 130])
    t_corse.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8F9FA')]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    elements.append(t_corse)
    
    if idx < len(cartellini_proposti) - 1:
        elements.append(PageBreak())

doc.build(elements)
print("PDF creato!")
