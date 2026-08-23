import os
import fitz
import re
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

pdf_out = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini_Operativi_Nostra_Proposta_2026.pdf"

doc = SimpleDocTemplate(
    pdf_out,
    pagesize=landscape(A4),
    leftMargin=18,
    rightMargin=18,
    topMargin=15,
    bottomMargin=15
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=12, leading=14, textColor=colors.HexColor('#003366'))
sub_style = ParagraphStyle('SubTitle', fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor('#333333'))
cell_text = ParagraphStyle('CellText', fontName='Helvetica', fontSize=7, leading=8.5)
cell_bold = ParagraphStyle('CellBold', fontName='Helvetica-Bold', fontSize=7, leading=8.5)
header_cell = ParagraphStyle('HCell', fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=colors.white)
law_style = ParagraphStyle('LawStyle', fontName='Helvetica', fontSize=6.5, leading=8, textColor=colors.HexColor('#222222'))

elements = []

# Schede analitiche con tabella oraria esatta corsa per corsa per i turni ristrutturati
schede_analitiche = [
    {
        "turno": "Pe0130",
        "deposito": "PEROSA ARGENTINA",
        "desc": "TURNO 213 DI PEROSA - PROPOSTA RISTRUTTURATA",
        "inizio": "12:00", "fine": "18:30", "nastro": "6h 30m (Azienda: 11h 35m -> Risparmio 5h 05m)", "olg": "6h 20m", "rip": "1 (Turno Unico)",
        "legge": "<b>Conformità L. 138/58 & CCNL:</b> Guida continua max 1h47 (&le; 5h00) | Pausa 44 min continuativi a Torino Bolzano h 13:57-14:41 (&ge; 30m entro 6h) | Nastro 6h30 (&le; 12h) | Riposo giornaliero 17h30 (&ge; 11h) a Perosa Deposito.",
        "corse": [
            ["12:00", "12:05", "Disp", "Controllo livelli autobus", "-", "0:05", "-", "Perosa Deposito"],
            ["12:05", "12:10", "Trasf", "Perosa Deposito -> PEROSA P.za Terzo Alpini", "-", "0:05", "1,17 km", "Trasferimento"],
            ["12:10", "12:40", "000282", "PEROSA P.za Terzo Alpini -> PINEROLO P.za Cavour", "0:30", "-", "17,85 km", "Corsa di Linea"],
            ["12:40", "13:57", "000282", "PINEROLO P.za Cavour -> TORINO c.so Bolzano (P. Susa)", "1:17", "-", "42,27 km", "Corsa di Linea"],
            ["13:57", "14:41", "PAUSA", "PAUSA TECNICA & RIPOSO EX ART. 5 L. 138/58", "-", "0:44", "-", "Torino c.so Bolzano"],
            ["14:41", "15:50", "000275", "TORINO c.so Bolzano -> PINEROLO P.za Cavour", "1:09", "-", "42,11 km", "Corsa di Linea"],
            ["15:50", "15:55", "Trasf", "PINEROLO P.za Cavour -> PINEROLO Via Saluzzo (ENEL)", "-", "0:05", "0,73 km", "Trasferimento"],
            ["16:05", "16:39", "000283", "PINEROLO Via Saluzzo -> CANTALUPA", "0:34", "-", "18,24 km", "Corsa di Linea"],
            ["16:40", "17:00", "000283", "CANTALUPA -> PINEROLO P.za Cavour", "0:20", "-", "10,61 km", "Corsa di Linea"],
            ["17:00", "17:05", "Trasf", "PINEROLO P.za Cavour -> Pinerolo Bivio SAPAV", "-", "0:05", "2,42 km", "Trasferimento"],
            ["17:05", "17:15", "000284", "Pinerolo Bivio SAPAV -> AIRASCA SKF", "0:10", "-", "10,24 km", "Corsa di Linea"],
            ["17:30", "18:15", "000284", "AIRASCA SKF -> PEROSA P.za Terzo Alpini", "0:45", "-", "30,09 km", "Corsa di Linea"],
            ["18:15", "18:20", "Trasf", "PEROSA P.za Terzo Alpini -> Perosa Deposito", "-", "0:05", "1,17 km", "Trasferimento"],
            ["18:20", "18:30", "Disp", "Pulizia Interna Autobus & Chiusura Servizio", "-", "0:10", "-", "Perosa Deposito"]
        ]
    },
    {
        "turno": "Pt0030",
        "deposito": "PONT SAINT MARTIN",
        "desc": "CAREMA-TORINO-CAREMA - PROPOSTA RISTRUTTURATA",
        "inizio": "12:40", "fine": "18:33", "nastro": "5h 53m (Azienda: 12h 05m -> Risparmio 6h 12m)", "olg": "5h 45m", "rip": "1 (Turno Unico)",
        "legge": "<b>Conformità L. 138/58 & CCNL:</b> Guida continua max 2h08 (&le; 5h00) | Pausa 1h12 continuativi a Torino h 14:58-16:10 (&ge; 30m entro 6h) | Nastro 5h53 (&le; 12h) | Riposo giornaliero 18h07 (&ge; 11h) a Pont Rimessa.",
        "corse": [
            ["12:40", "12:47", "Disp", "Controllo livelli autobus", "-", "0:07", "-", "Pont Rimessa"],
            ["12:47", "12:52", "Trasf", "PONT Rimessa -> PONT P.za IV Novembre", "-", "0:05", "2,10 km", "Trasferimento"],
            ["12:52", "13:35", "000265", "PONT P.za IV Novembre -> STRAMBINO c.so Torino", "0:43", "-", "29,63 km", "Corsa di Linea"],
            ["13:37", "14:58", "000265", "STRAMBINO c.so Torino -> TORINO c.so Bolzano", "1:21", "-", "49,10 km", "Corsa di Linea"],
            ["14:58", "16:10", "PAUSA", "PAUSA TECNICA & RIPOSO EX ART. 5 L. 138/58", "-", "1:12", "-", "Torino c.so Bolzano"],
            ["16:10", "17:06", "000265", "TO P.za Cattaneo Mirafiori FCA -> CHIVASSO Alfa-Lancia", "0:56", "-", "45,22 km", "Corsa di Linea"],
            ["17:08", "17:46", "000265", "CHIVASSO Alfa-Lancia -> IVREA Stazione FS", "0:38", "-", "31,68 km", "Corsa di Linea"],
            ["17:48", "18:18", "000265", "IVREA Stazione FS -> PONT S.MARTIN P.za IV Nov.", "0:30", "-", "22,11 km", "Corsa di Linea"],
            ["18:18", "18:23", "Trasf", "PONT P.za IV Nov. -> PONT Rimessa", "-", "0:05", "2,10 km", "Trasferimento"],
            ["18:23", "18:33", "Disp", "Pulizia Interna Autobus & Chiusura Servizio", "-", "0:10", "-", "Pont Rimessa"]
        ]
    },
    {
        "turno": "To0620",
        "deposito": "TORINO (GRUGLIASCO)",
        "desc": "TORINO-PINEROLO-TORINO - PROPOSTA RISTRUTTURATA",
        "inizio": "06:15", "fine": "14:00", "nastro": "7h 45m (Azienda: 10h 54m -> Risparmio 3h 09m)", "olg": "6h 40m", "rip": "1 (Turno Unico)",
        "legge": "<b>Conformità L. 138/58 & CCNL:</b> Guida continua 2h35 (&le; 5h00) | Cambio autista a Porta Susa con auto aziendale h 09:30 (zero vuoti bus) | Presidio Grugliasco | Nastro 7h45 (&le; 12h) | Riposo giornaliero 16h15 (&ge; 11h).",
        "corse": [
            ["06:15", "06:25", "Disp", "Presa servizio & Controllo livelli autobus", "-", "0:10", "-", "Grugliasco Dep."],
            ["06:25", "06:40", "Trasf", "Grugliasco Deposito -> TORINO c.so Bolzano", "-", "0:15", "8,50 km", "Trasferimento"],
            ["06:45", "07:55", "000266", "TORINO c.so Bolzano -> PINEROLO P.za Cavour", "1:10", "-", "38,50 km", "Corsa di Linea"],
            ["08:05", "09:20", "000266", "PINEROLO P.za Cavour -> TORINO c.so Bolzano", "1:15", "-", "38,50 km", "Corsa di Linea"],
            ["09:20", "09:30", "Sosta", "Sosta Porta Susa - Consegna bus a secondo autista montante", "-", "0:10", "-", "Bus resta in linea"],
            ["09:30", "09:45", "Servizio", "Rientro a Grugliasco Deposito con auto di servizio aziendale", "-", "0:15", "8,50 km", "Auto aziendale"],
            ["09:45", "10:00", "PAUSA", "Pausa regolamentare caffè / ristoro a Grugliasco", "-", "0:15", "-", "Grugliasco Dep."],
            ["10:00", "13:50", "Presidio", "Disposizione tecnica / presidio operativo deposito", "-", "3:50", "-", "Grugliasco Dep."],
            ["13:50", "14:00", "Disp", "Chiusura turno e smonto servizio", "-", "0:10", "-", "Grugliasco Dep."]
        ]
    },
    {
        "turno": "To0280 (40h Comp.)",
        "deposito": "TORINO (GRUGLIASCO)",
        "desc": "TURNO SPECIALE 40h SETTIMANALI (RIPOSO FISSO SAB+DOM)",
        "inizio": "05:05", "fine": "13:10", "nastro": "8h 05m", "olg": "8h 00m (40h/settimana)", "rip": "1 (Turno Unico)",
        "legge": "<b>Conformità L. 138/58 & CCNL:</b> 8h00 giornaliere x 5 gg (Lun-Ven) = 40h00 piene. Diritto ex Art. 1, 2 e 7 L. 138/58 al doppio riposo compensativo continuativo di 48 ore nel fine settimana (Sabato e Domenica).",
        "corse": [
            ["05:05", "05:15", "Disp", "Controllo livelli autobus", "-", "0:10", "-", "Grugliasco Dep."],
            ["05:15", "05:45", "Trasf", "Grugliasco Deposito -> TO P.za Carlo Felice", "-", "0:30", "8,49 km", "Trasferimento"],
            ["05:45", "06:30", "000268", "TO P.za Carlo Felice -> CASELLE Aeroporto", "0:45", "-", "16,80 km", "Navetta Caselle"],
            ["07:00", "07:45", "000268", "CASELLE Aeroporto -> TO P.za Carlo Felice", "0:45", "-", "17,49 km", "Navetta Caselle"],
            ["07:45", "08:00", "PAUSA", "1ª FRAZIONE PAUSA REGOLAMENTARE A PORTA NUOVA", "-", "0:15", "-", "TO Carlo Felice"],
            ["08:00", "08:37", "000268", "TO P.za Carlo Felice -> CASELLE Aeroporto", "0:37", "-", "19,49 km", "Navetta Caselle"],
            ["09:00", "09:45", "000268", "CASELLE Aeroporto -> TO P.za Carlo Felice", "0:45", "-", "17,49 km", "Navetta Caselle"],
            ["09:45", "10:00", "PAUSA", "2ª FRAZIONE PAUSA REGOLAMENTARE A PORTA NUOVA", "-", "0:15", "-", "TO Carlo Felice"],
            ["10:00", "10:37", "000268", "TO P.za Carlo Felice -> CASELLE Aeroporto", "0:37", "-", "19,49 km", "Navetta Caselle"],
            ["11:00", "11:45", "000268", "CASELLE Aeroporto -> TO P.za Carlo Felice", "0:45", "-", "17,49 km", "Navetta Caselle"],
            ["11:45", "12:00", "PAUSA", "3ª FRAZIONE PAUSA REGOLAMENTARE A PORTA NUOVA", "-", "0:15", "-", "TO Carlo Felice"],
            ["12:00", "12:45", "000268", "TO P.za Carlo Felice -> CASELLE Aeroporto", "0:45", "-", "17,49 km", "Navetta Caselle"],
            ["12:45", "13:00", "000268", "Rientro in linea / Navetta", "0:15", "-", "8,50 km", "Corsa Linea"],
            ["13:00", "13:10", "Disp", "Rientro a Grugliasco Deposito & Chiusura", "-", "0:10", "-", "Grugliasco Dep."]
        ]
    },
    {
        "turno": "Pi0140 (40h Comp.)",
        "deposito": "PINEROLO",
        "desc": "TURNO SPECIALE 40h SETTIMANALI (RIPOSO FISSO SAB+DOM)",
        "inizio": "05:45", "fine": "13:50", "nastro": "8h 05m", "olg": "8h 00m (40h/settimana)", "rip": "1 (Turno Unico)",
        "legge": "<b>Conformità L. 138/58 & CCNL:</b> 8h00 giornaliere x 5 gg (Lun-Ven) = 40h00 piene. Diritto ex Art. 1, 2 e 7 L. 138/58 al doppio riposo compensativo continuativo di 48 ore nel fine settimana (Sabato e Domenica).",
        "corse": [
            ["05:45", "05:55", "Disp", "Controllo livelli autobus", "-", "0:10", "-", "Pinerolo Dep."],
            ["05:55", "06:00", "Trasf", "Pinerolo Deposito -> TN ITALY", "-", "0:05", "0,92 km", "Trasferimento"],
            ["06:00", "06:30", "000275", "TN ITALY -> PEROSA P.za Terzo Alpini", "0:30", "-", "19,63 km", "Corsa Industriale"],
            ["06:30", "07:00", "Trasf", "PEROSA P.za Terzo Alpini -> FENESTRELLE", "-", "0:30", "16,41 km", "Trasferimento"],
            ["07:10", "07:40", "000281", "FENESTRELLE -> PEROSA P.za Terzo Alpini", "0:30", "-", "16,65 km", "Corsa Scolastica"],
            ["07:40", "08:10", "000275", "PEROSA P.za Terzo Alpini -> PINEROLO P.za Cavour", "0:30", "-", "17,85 km", "Corsa di Linea"],
            ["08:10", "09:19", "000275", "PINEROLO P.za Cavour -> TORINO c.so Bolzano (P. Susa)", "1:09", "-", "41,77 km", "Corsa di Linea"],
            ["09:19", "09:35", "PAUSA", "1ª FRAZIONE PAUSA REGOLAMENTARE A PORTA SUSA", "-", "0:16", "-", "Torino c.so Bolzano"],
            ["09:35", "10:45", "000275", "TORINO c.so Bolzano -> PINEROLO P.za Cavour", "1:10", "-", "41,77 km", "Corsa di Linea"],
            ["10:45", "11:05", "PAUSA", "2ª FRAZIONE PAUSA REGOLAMENTARE A PINEROLO", "-", "0:20", "-", "PINEROLO P.za Cavour"],
            ["11:05", "13:30", "000282", "PINEROLO Servizio integrato di linea locale", "2:25", "-", "40,00 km", "Corsa di Linea"],
            ["13:30", "13:40", "Trasf", "PINEROLO P.za Cavour -> Pinerolo Deposito", "-", "0:10", "2,40 km", "Trasferimento"],
            ["13:40", "13:50", "Disp", "Pulizia Interna Autobus & Chiusura Servizio", "-", "0:10", "-", "Pinerolo Deposito"]
        ]
    },
    {
        "turno": "Pe0120",
        "deposito": "PEROSA ARGENTINA",
        "desc": "TURNO 212 DI PEROSA - PROPOSTA RISTRUTTURATA",
        "inizio": "06:55", "fine": "15:10", "nastro": "8h 15m (Azienda: 12h 10m -> Risparmio 3h 55m)", "olg": "7h 15m", "rip": "1 (Turno Unico)",
        "legge": "<b>Conformità L. 138/58 & CCNL:</b> Guida continua max 2h30 (&le; 5h00) | Pausa 35 min a Pinerolo h 11:20-11:55 | [NOTA VUOTO NECESSARIO]: Rientro serale a vuoto Pinerolo->Perosa (16 km) per chiusura a Perosa.",
        "corse": [
            ["06:55", "07:05", "Disp", "Controllo livelli autobus", "-", "0:10", "-", "Perosa Deposito"],
            ["07:05", "07:10", "Trasf", "Perosa Deposito -> PEROSA P.za Terzo Alpini", "-", "0:05", "1,17 km", "Trasferimento"],
            ["07:10", "07:45", "000275", "PEROSA -> PINEROLO P.za Cavour", "0:35", "-", "18,51 km", "Corsa Scolastica"],
            ["07:45", "08:55", "000282", "PINEROLO -> VIGONE / PANCALIERI", "1:10", "-", "28,00 km", "Corsa di Linea"],
            ["09:00", "10:10", "000282", "PANCALIERI -> PINEROLO P.za Cavour", "1:10", "-", "28,00 km", "Corsa di Linea"],
            ["10:15", "11:20", "000275", "PINEROLO -> PEROSA P.za Terzo Alpini", "1:05", "-", "18,51 km", "Corsa di Linea"],
            ["11:20", "11:55", "PAUSA", "PAUSA REGOLAMENTARE EX ART. 5 L. 138/58 A PEROSA", "-", "0:35", "-", "Perosa P.za Terzo Alpini"],
            ["11:55", "13:00", "000275", "PEROSA -> PINEROLO Movicentro", "1:05", "-", "18,51 km", "Corsa di Linea"],
            ["13:05", "14:35", "000275", "PINEROLO -> PEROSA P.za Terzo Alpini", "1:30", "-", "25,00 km", "Corsa di Linea"],
            ["14:40", "15:05", "Trasf", "PEROSA -> Perosa Deposito (Rientro a vuoto)", "-", "0:25", "16,00 km", "Rientro Vuoto Necessario"],
            ["15:05", "15:10", "Disp", "Chiusura servizio a Perosa Deposito", "-", "0:05", "-", "Perosa Deposito"]
        ]
    },
    {
        "turno": "Pi0050",
        "deposito": "PINEROLO",
        "desc": "TURNO 5 DI PINEROLO - PROPOSTA RISTRUTTURATA",
        "inizio": "04:50", "fine": "11:50", "nastro": "7h 00m (Azienda: 10h 55m -> Risparmio 3h 55m)", "olg": "6h 30m (Recupero OLG +40m)", "rip": "1 (Turno Unico)",
        "legge": "<b>Conformità L. 138/58 & CCNL:</b> Assorbe la corsa mattutina 07:10 Perosa->Pinerolo. Chiusura a turno unico a Pinerolo Deposito alle 11:50 senza stacco pomeridiano.",
        "corse": [
            ["04:50", "05:00", "Disp", "Controllo livelli autobus", "-", "0:10", "-", "Pinerolo Dep."],
            ["05:00", "05:10", "Trasf", "Pinerolo Deposito -> PINEROLO P.za Cavour", "-", "0:10", "2,40 km", "Trasferimento"],
            ["05:10", "06:15", "000275", "PINEROLO P.za Cavour -> SESTRIERE", "1:05", "-", "42,00 km", "Corsa di Linea"],
            ["06:20", "07:05", "000275", "SESTRIERE -> PEROSA P.za Terzo Alpini", "0:45", "-", "30,00 km", "Corsa di Linea"],
            ["07:10", "07:40", "000275", "PEROSA P.za Terzo Alpini -> PINEROLO Movicentro", "0:30", "-", "18,51 km", "Corsa assorbita da Pe0130"],
            ["07:45", "08:15", "PAUSA", "PAUSA REGOLAMENTARE A PINEROLO MOVICENTRO", "-", "0:30", "-", "Pinerolo Movicentro"],
            ["08:15", "09:40", "000282", "PINEROLO -> VIGONE / PANCALIERI -> PINEROLO", "1:25", "-", "35,00 km", "Corsa di Linea"],
            ["09:45", "11:40", "000283", "PINEROLO Servizio integrato di linea locale", "1:55", "-", "30,00 km", "Corsa di Linea"],
            ["11:40", "11:50", "Disp", "Rientro a Pinerolo Deposito & Chiusura", "-", "0:10", "2,40 km", "Pinerolo Deposito"]
        ]
    }
]

for idx, s in enumerate(schede_analitiche):
    # Header
    head_t = Table([
        [
            Paragraph(f"<b>ARRIVA ITALIA (ex SADEM) - CARTELLINO DI MARCIA DI PROPOSTA</b>", title_style),
            Paragraph(f"<b>TURNO: <font color='#003366' size='11'>{s['turno']}</font> | Deposito: {s['deposito']}</b><br/>{s['desc']}", sub_style)
        ]
    ], colWidths=[405, 405])
    head_t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,0), (-1,-1), 1)]))
    elements.append(head_t)
    elements.append(Spacer(1, 2))

    # Box Indicatori
    box_data = [
        [
            Paragraph(f"Inizio: <b>{s['inizio']}</b>", cell_bold),
            Paragraph(f"Fine: <b>{s['fine']}</b>", cell_bold),
            Paragraph(f"Nastro: <font color='#008800'><b>{s['nastro']}</b></font>", cell_bold),
            Paragraph(f"OLG (Ore Pagate): <b>{s['olg']}</b>", cell_bold),
            Paragraph(f"Riprese: <b>{s['rip']}</b>", cell_bold),
            Paragraph(f"Deposito A/R: <b>{s['deposito']}</b>", cell_bold)
        ]
    ]
    t_box = Table(box_data, colWidths=[80, 80, 240, 130, 110, 170])
    t_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EBF3FA')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#003366')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBDDEE')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    elements.append(t_box)
    elements.append(Spacer(1, 3))

    # Tabella oraria esatta corsa per corsa
    rows_corse = [
        [
            Paragraph("Partenza", header_cell),
            Paragraph("Arrivo", header_cell),
            Paragraph("Linea / Tipo", header_cell),
            Paragraph("Descrizione Tratta / Attività di Servizio", header_cell),
            Paragraph("Guida", header_cell),
            Paragraph("Non Guida", header_cell),
            Paragraph("Km", header_cell),
            Paragraph("Note Operative", header_cell)
        ]
    ]

    for r in s['corse']:
        is_pausa = r[2] == 'PAUSA'
        bg = colors.HexColor('#FFF2E6') if is_pausa else colors.white
        rows_corse.append([
            Paragraph(r[0], cell_bold),
            Paragraph(r[1], cell_bold),
            Paragraph(r[2], cell_bold),
            Paragraph(r[3], cell_text),
            Paragraph(r[4], cell_text),
            Paragraph(r[5], cell_text),
            Paragraph(r[6], cell_text),
            Paragraph(r[7], cell_text)
        ])

    t_table = Table(rows_corse, colWidths=[42, 42, 65, 305, 42, 50, 65, 199])
    t_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8F9FA')]),
        ('TOPPADDING', (0,0), (-1,-1), 1.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(t_table)
    elements.append(Spacer(1, 3))

    # Box Legge in calce alla scheda
    box_law = [
        [
            Paragraph(s['legge'], law_style)
        ]
    ]
    t_law = Table(box_law, colWidths=[810])
    t_law.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F5F5F5')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#999999')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_law)

    if idx < len(schede_analitiche) - 1:
        elements.append(PageBreak())

doc.build(elements)
print("✅ PDF Cartellini Operativi Nostra Proposta generato con successo!")
