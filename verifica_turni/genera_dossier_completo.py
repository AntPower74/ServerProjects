import os
import fitz
import re
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

pdf_out = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Dossier_Comparazione_e_Proposte_Cartellini_2026.pdf"

doc = SimpleDocTemplate(
    pdf_out,
    pagesize=landscape(A4),
    leftMargin=20,
    rightMargin=20,
    topMargin=20,
    bottomMargin=20
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.HexColor('#003366'))
sub_style = ParagraphStyle('SubTitle', fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor('#333333'))
cell_style = ParagraphStyle('CellText', fontName='Helvetica', fontSize=7, leading=8.5)
cell_bold = ParagraphStyle('CellBold', fontName='Helvetica-Bold', fontSize=7, leading=8.5)
header_cell_orig = ParagraphStyle('HCellO', fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=colors.white)
header_cell_prop = ParagraphStyle('HCellP', fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=colors.white)

elements = []

# Analisi e generazione schede a 2 colonne (Originale Azienda vs Proposta Sindacale)
schede = [
    {
        "turno": "Pe0130",
        "deposito": "PEROSA ARGENTINA",
        "desc": "TURNO 213 DI PEROSA",
        "orig_inizio": "06:55", "orig_fine": "18:30", "orig_nastro": "11h 35m", "orig_olg": "7h 11m", "orig_rip": "3",
        "prop_inizio": "12:00", "prop_fine": "18:30", "prop_nastro": "6h 30m (-5h 05m)", "prop_olg": "6h 20m", "prop_rip": "1",
        "motivo": "Corsa mattutina 07:10 (Perosa->Pinerolo) ceduta a Pi0050, eliminando il rientro a vuoto e lo stacco di 4h. Inizio h 12:00 a Perosa, turno unico continuativo.",
        "righe_orig": [
            ["06:55", "07:05", "Disp", "Controllo livelli autobus"],
            ["07:05", "07:10", "Trasf", "Perosa Deposito -> PEROSA P.za Terzo Alpini"],
            ["07:10", "07:40", "000275", "PEROSA -> PINEROLO Movicentro"],
            ["07:40", "08:10", "Trasf", "PINEROLO Movicentro -> Perosa Deposito (Vuoto)"],
            ["---", "---", "STACCO", "STACCO NON PAGATO DI 3h 50m A PEROSA"],
            ["12:00", "12:05", "Trasf", "Perosa Deposito -> PEROSA P.za Terzo Alpini"],
            ["12:10", "12:40", "000282", "PEROSA -> PINEROLO P.za Cavour"],
            ["12:40", "13:57", "000282", "PINEROLO -> TORINO c.so Bolzano (P. Susa)"],
            ["14:41", "15:50", "000275", "TORINO c.so Bolzano -> PINEROLO P.za Cavour"],
            ["16:05", "16:39", "000283", "PINEROLO -> CANTALUPA"],
            ["16:40", "17:00", "000283", "CANTALUPA -> PINEROLO P.za Cavour"],
            ["17:05", "17:15", "000284", "Pinerolo Bivio SAPAV -> AIRASCA SKF"],
            ["17:30", "18:15", "000284", "AIRASCA SKF -> PEROSA P.za Terzo Alpini"],
            ["18:15", "18:30", "Disp", "Rientro & Pulizia Interna Autobus"]
        ],
        "righe_prop": [
            ["12:00", "12:05", "Disp", "Controllo livelli autobus (Perosa Deposito)"],
            ["12:05", "12:10", "Trasf", "Perosa Deposito -> PEROSA P.za Terzo Alpini"],
            ["12:10", "12:40", "000282", "PEROSA -> PINEROLO P.za Cavour (Linea)"],
            ["12:40", "13:57", "000282", "PINEROLO -> TORINO c.so Bolzano (Linea)"],
            ["14:41", "15:50", "000275", "TORINO c.so Bolzano -> PINEROLO (Linea)"],
            ["16:05", "16:39", "000283", "PINEROLO -> CANTALUPA (Linea)"],
            ["16:40", "17:00", "000283", "CANTALUPA -> PINEROLO P.za Cavour"],
            ["17:05", "17:15", "000284", "Pinerolo -> AIRASCA SKF"],
            ["17:30", "18:15", "000284", "AIRASCA SKF -> PEROSA P.za Terzo Alpini"],
            ["18:15", "18:30", "Disp", "Perosa Deposito - Pulizia & Chiusura"],
            ["-", "-", "-", "RISULTATO: Turno Unico Compatto - Zero Vuoti"]
        ]
    },
    {
        "turno": "Pt0030",
        "deposito": "PONT SAINT MARTIN",
        "desc": "CAREMA-TORINO-CAREMA",
        "orig_inizio": "06:28", "orig_fine": "18:33", "orig_nastro": "12h 05m", "orig_olg": "6h 43m", "orig_rip": "3",
        "prop_inizio": "12:40", "prop_fine": "18:33", "prop_nastro": "5h 53m (-6h 12m)", "prop_olg": "5h 45m", "prop_rip": "1",
        "motivo": "Spezzone 06:28-08:33 ceduto a turno mattinale Ivrea/Pont. Inizio a Pont h 12:40, linea Torino/Chivasso/Ivrea e rientro a Pont Rimessa h 18:33 a nastro unico.",
        "righe_orig": [
            ["06:28", "06:43", "Disp/Tr", "Pont Rimessa -> PONT P.za IV Novembre"],
            ["06:43", "07:27", "000265", "PONT S.MARTIN -> STRAMBINO c.so Torino"],
            ["07:30", "08:14", "000265", "STRAMBINO -> PONT S.MARTIN P.za IV Nov."],
            ["08:14", "08:19", "Trasf", "PONT P.za IV Nov. -> Pont Rimessa"],
            ["---", "---", "STACCO", "STACCO NON PAGATO DI 4h 14m A PONT"],
            ["12:47", "12:52", "Trasf", "Pont Rimessa -> PONT P.za IV Novembre"],
            ["12:52", "13:35", "000265", "PONT S.MARTIN -> STRAMBINO c.so Torino"],
            ["13:37", "14:58", "000265", "STRAMBINO -> TORINO c.so Bolzano"],
            ["16:10", "17:06", "000265", "TO Mirafiori FCA -> CHIVASSO Alfa-Lancia"],
            ["17:08", "17:46", "000265", "CHIVASSO -> IVREA Stazione FS"],
            ["17:48", "18:18", "000265", "IVREA -> PONT S.MARTIN P.za IV Nov."],
            ["18:18", "18:33", "Disp", "Rientro Rimessa Pont & Pulizia Autobus"]
        ],
        "righe_prop": [
            ["12:40", "12:52", "Disp/Tr", "Pont Rimessa -> PONT P.za IV Novembre"],
            ["12:52", "13:35", "000265", "PONT S.MARTIN -> STRAMBINO c.so Torino"],
            ["13:37", "14:58", "000265", "STRAMBINO -> TORINO c.so Bolzano"],
            ["16:10", "17:06", "000265", "TO Mirafiori FCA -> CHIVASSO Alfa-Lancia"],
            ["17:08", "17:46", "000265", "CHIVASSO -> IVREA Stazione FS"],
            ["17:48", "18:18", "000265", "IVREA -> PONT S.MARTIN P.za IV Nov."],
            ["18:18", "18:33", "Disp", "Rientro Rimessa Pont & Chiusura Servizio"],
            ["-", "-", "-", "RISULTATO: Nastro ridotto da 12h05 a 5h53!"]
        ]
    },
    {
        "turno": "To0620",
        "deposito": "TORINO (GRUGLIASCO)",
        "desc": "TORINO-PINEROLO-TORINO",
        "orig_inizio": "06:15", "orig_fine": "17:09", "orig_nastro": "10h 54m", "orig_olg": "6h 49m", "orig_rip": "2",
        "prop_inizio": "06:15", "prop_fine": "14:00", "prop_nastro": "7h 45m (-3h 09m)", "prop_olg": "6h 40m", "prop_rip": "1",
        "motivo": "Arrivo a Porta Susa h 09:30: cambio sul posto con auto di servizio aziendale da Grugliasco. Il bus resta in linea a Porta Susa per il secondo autista. ZERO vuoti di bus.",
        "righe_orig": [
            ["06:15", "06:40", "Disp/Tr", "Grugliasco Deposito -> TORINO c.so Bolzano"],
            ["06:45", "07:55", "000266", "TORINO c.so Bolzano -> PINEROLO P.za Cavour"],
            ["08:05", "09:20", "000266", "PINEROLO P.za Cavour -> TORINO c.so Bolzano"],
            ["---", "---", "STACCO", "STACCO NON PAGATO DI QUASI 4h A PORTA SUSA"],
            ["13:45", "14:55", "000268", "TO P.za Carlo Felice -> CASELLE Aeroporto"],
            ["15:15", "16:00", "000268", "CASELLE Aeroporto -> TO P.za Carlo Felice"],
            ["16:00", "17:09", "Disp/Tr", "Rientro a Grugliasco Deposito"]
        ],
        "righe_prop": [
            ["06:15", "06:40", "Disp/Tr", "Grugliasco Deposito -> TORINO c.so Bolzano"],
            ["06:45", "07:55", "000266", "TORINO c.so Bolzano -> PINEROLO P.za Cavour"],
            ["08:05", "09:20", "000266", "PINEROLO P.za Cavour -> TORINO c.so Bolzano"],
            ["09:30", "09:45", "Cambio", "Cambio autista a Porta Susa (auto di servizio)"],
            ["09:45", "10:00", "Trasf", "Rientro a Grugliasco in auto di servizio"],
            ["10:00", "14:00", "Presidio", "Disposizione tecnica a Grugliasco"],
            ["-", "-", "-", "RISULTATO: Nastro compatto 7h45 - Zero vuoti bus"]
        ]
    },
    {
        "turno": "To0280 (40h Comp.)",
        "deposito": "TORINO (GRUGLIASCO)",
        "desc": "TURNO SPECIALE 40h SETTIMANALI (RIPOSO SAB+DOM)",
        "orig_inizio": "05:05", "orig_fine": "12:40", "orig_nastro": "7h 35m", "orig_olg": "7h 35m", "orig_rip": "1",
        "prop_inizio": "05:05", "prop_fine": "13:10", "prop_nastro": "8h 05m", "prop_olg": "8h 00m (40h/sett.)", "prop_rip": "1",
        "motivo": "Turno continuo su navetta Caselle Aeroporto portato a 8h00 piene giornaliere su 5 giorni (Lun-Ven = 40h00) -> Diritto a riposo fisso Sabato e Domenica.",
        "righe_orig": [
            ["05:05", "05:45", "Disp/Tr", "Grugliasco -> TO P.za Carlo Felice"],
            ["05:45", "06:30", "000268", "TO Carlo Felice -> CASELLE Aeroporto"],
            ["07:00", "07:45", "000268", "CASELLE Aeroporto -> TO Carlo Felice"],
            ["08:00", "08:37", "000268", "TO Carlo Felice -> CASELLE Aeroporto"],
            ["09:00", "09:45", "000268", "CASELLE Aeroporto -> TO Carlo Felice"],
            ["10:00", "10:37", "000268", "TO Carlo Felice -> CASELLE Aeroporto"],
            ["11:00", "11:45", "000268", "CASELLE Aeroporto -> TO Carlo Felice"],
            ["12:00", "12:40", "Disp/Tr", "Rientro a Grugliasco Deposito"]
        ],
        "righe_prop": [
            ["05:05", "05:45", "Disp/Tr", "Grugliasco -> TO P.za Carlo Felice"],
            ["05:45", "06:30", "000268", "TO Carlo Felice -> CASELLE Aeroporto"],
            ["07:00", "07:45", "000268", "CASELLE Aeroporto -> TO Carlo Felice"],
            ["08:00", "08:37", "000268", "TO Carlo Felice -> CASELLE Aeroporto"],
            ["09:00", "09:45", "000268", "CASELLE Aeroporto -> TO Carlo Felice"],
            ["10:00", "10:37", "000268", "TO Carlo Felice -> CASELLE Aeroporto"],
            ["11:00", "11:45", "000268", "CASELLE Aeroporto -> TO Carlo Felice"],
            ["12:00", "12:45", "000268", "TO Carlo Felice -> CASELLE Aeroporto"],
            ["12:45", "13:10", "Disp/Tr", "Rientro a Grugliasco & Chiusura (8h00 pagate)"],
            ["-", "-", "-", "DIRITTO RIPOSO COMPENSATIVO: Sabato e Domenica (5+2)"]
        ]
    },
    {
        "turno": "Pi0140 (40h Comp.)",
        "deposito": "PINEROLO",
        "desc": "TURNO SPECIALE 40h SETTIMANALI (RIPOSO SAB+DOM)",
        "orig_inizio": "05:45", "orig_fine": "15:10", "orig_nastro": "9h 25m", "orig_olg": "7h 33m", "orig_rip": "2",
        "prop_inizio": "05:45", "prop_fine": "13:50", "prop_nastro": "8h 05m", "prop_olg": "8h 00m (40h/sett.)", "prop_rip": "1",
        "motivo": "Partenza e rientro a Pinerolo Deposito. Raccordate linee mattinali industriali e scolastiche a nastro unico di 8h05 (40h settimanali -> Riposo Sabato e Domenica).",
        "righe_orig": [
            ["05:45", "06:00", "Disp/Tr", "Pinerolo Deposito -> TN ITALY"],
            ["06:00", "06:30", "000275", "TN ITALY -> PEROSA P.za Terzo Alpini"],
            ["06:30", "07:00", "Trasf", "PEROSA -> FENESTRELLE"],
            ["07:10", "07:40", "000281", "FENESTRELLE -> PEROSA P.za Terzo Alpini"],
            ["07:40", "08:10", "000275", "PEROSA -> PINEROLO P.za Cavour"],
            ["08:10", "09:19", "000275", "PINEROLO -> TORINO c.so Bolzano"],
            ["---", "---", "STACCO", "Stacco di 2h a Torino c.so Bolzano"],
            ["11:30", "12:40", "000275", "TORINO -> PINEROLO Movicentro"],
            ["14:00", "15:10", "000275", "PINEROLO -> Perosa / Pinerolo Deposito"]
        ],
        "righe_prop": [
            ["05:45", "06:00", "Disp/Tr", "Pinerolo Deposito -> TN ITALY"],
            ["06:00", "06:30", "000275", "TN ITALY -> PEROSA P.za Terzo Alpini"],
            ["06:30", "07:00", "Trasf", "PEROSA -> FENESTRELLE"],
            ["07:10", "07:40", "000281", "FENESTRELLE -> PEROSA P.za Terzo Alpini"],
            ["07:40", "08:10", "000275", "PEROSA -> PINEROLO P.za Cavour"],
            ["08:10", "09:19", "000275", "PINEROLO -> TORINO c.so Bolzano"],
            ["09:30", "10:40", "000275", "TORINO -> PINEROLO P.za Cavour (Rientro continuo)"],
            ["11:00", "13:30", "000282", "PINEROLO Servizio integrato di linea"],
            ["13:30", "13:50", "Disp/Tr", "Rientro Pinerolo Deposito & Chiusura (8h00 pagate)"],
            ["-", "-", "-", "DIRITTO RIPOSO COMPENSATIVO: Sabato e Domenica (5+2)"]
        ]
    }
]

for idx, s in enumerate(schede):
    # Header
    head_t = Table([
        [
            Paragraph(f"<b>ARRIVA ITALIA (ex SADEM) - DOSSIER CONFRONTO TURNI</b>", title_style),
            Paragraph(f"<b>TURNO: <font color='#003366' size='11'>{s['turno']}</font> | Residenza: {s['deposito']}</b><br/>{s['desc']}", sub_style)
        ]
    ], colWidths=[380, 380])
    head_t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
    elements.append(head_t)
    elements.append(Spacer(1, 4))
    
    # Motivazione
    elements.append(Paragraph(f"<b>Sintesi Modifica Proposta:</b> {s['motivo']}", sub_style))
    elements.append(Spacer(1, 4))
    
    # Box Indicatori a confronto
    comp_box = Table([
        [
            Paragraph("<b>PROPOSTA ATTUALE AZIENDA</b>", header_cell_orig),
            Paragraph("<b>NUOVA PROPOSTA RISTRUTTURATA (SINDACALE)</b>", header_cell_prop)
        ],
        [
            Paragraph(f"Inizio: <b>{s['orig_inizio']}</b> | Fine: <b>{s['orig_fine']}</b><br/>Nastro: <font color='#CC0000'><b>{s['orig_nastro']}</b></font> | OLG: <b>{s['orig_olg']}</b> | Riprese: <b>{s['orig_rip']}</b>", cell_style),
            Paragraph(f"Inizio: <b>{s['prop_inizio']}</b> | Fine: <b>{s['prop_fine']}</b><br/>Nastro: <font color='#008800'><b>{s['prop_nastro']}</b></font> | OLG: <b>{s['prop_olg']}</b> | Riprese: <b>{s['prop_rip']}</b>", cell_style)
        ]
    ], colWidths=[375, 375])
    comp_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#990000')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#006600')),
        ('BACKGROUND', (0,1), (0,1), colors.HexColor('#FFF2F2')),
        ('BACKGROUND', (1,1), (1,1), colors.HexColor('#F2FFF2')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#666666')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    elements.append(comp_box)
    elements.append(Spacer(1, 4))
    
    # Tabelle affiancate di marcia
    rows_orig_t = [[Paragraph("Part.", header_cell_orig), Paragraph("Arr.", header_cell_orig), Paragraph("Linea", header_cell_orig), Paragraph("Descrizione Tratta Aziendale", header_cell_orig)]]
    for r in s['righe_orig']:
        bg_col = colors.HexColor('#FFDDDD') if r[2] == 'STACCO' else colors.white
        rows_orig_t.append([Paragraph(r[0], cell_bold), Paragraph(r[1], cell_bold), Paragraph(r[2], cell_bold), Paragraph(r[3], cell_style)])
        
    t_orig = Table(rows_orig_t, colWidths=[35, 35, 45, 255])
    t_orig.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#880000')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    
    rows_prop_t = [[Paragraph("Part.", header_cell_prop), Paragraph("Arr.", header_cell_prop), Paragraph("Linea", header_cell_prop), Paragraph("Descrizione Tratta Nuova Proposta", header_cell_prop)]]
    for r in s['righe_prop']:
        rows_prop_t.append([Paragraph(r[0], cell_bold), Paragraph(r[1], cell_bold), Paragraph(r[2], cell_bold), Paragraph(r[3], cell_style)])
        
    t_prop = Table(rows_prop_t, colWidths=[35, 35, 45, 255])
    t_prop.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#006600')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    
    # Affiancamento delle due tabelle
    t_affiancate = Table([[t_orig, t_prop]], colWidths=[375, 375])
    t_affiancate.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(t_affiancate)
    
    if idx < len(schede) - 1:
        elements.append(PageBreak())

doc.build(elements)
print("✅ Dossier PDF completo creato con successo!")
