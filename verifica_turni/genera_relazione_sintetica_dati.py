import os
import fitz
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

pdf_out = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/DOSSIER_TECNICO_ECONOMICO_SINDACALE_2026.pdf"

doc = SimpleDocTemplate(
    pdf_out,
    pagesize=A4,
    leftMargin=25,
    rightMargin=25,
    topMargin=20,
    bottomMargin=20
)

styles = getSampleStyleSheet()

# Stili tipografici
title_main = ParagraphStyle('MainTitle', fontName='Helvetica-Bold', fontSize=14, leading=17, textColor=colors.HexColor('#003366'), alignment=1)
subtitle = ParagraphStyle('SubTitle', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor('#333333'), alignment=1)
sec_title = ParagraphStyle('SecTitle', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=colors.HexColor('#003366'))
body = ParagraphStyle('Body', fontName='Helvetica', fontSize=7.2, leading=9.5, textColor=colors.HexColor('#222222'))
cell_txt = ParagraphStyle('CellTxt', fontName='Helvetica', fontSize=6.8, leading=8.5)
cell_bld = ParagraphStyle('CellBld', fontName='Helvetica-Bold', fontSize=6.8, leading=8.5)
h_cell = ParagraphStyle('HCell', fontName='Helvetica-Bold', fontSize=7.2, leading=9, textColor=colors.white, alignment=1)

elements = []

# PAGINA 1
elements.append(Paragraph("<b>ARRIVA ITALIA S.p.A. (ex SADEM) - BACINO TORINO & PROVINCIA</b>", subtitle))
elements.append(Spacer(1, 3))
elements.append(Paragraph("<b>DOSSIER TECNICO-ECONOMICO DI RISTRUTTURAZIONE TURNI 2026</b>", title_main))
elements.append(Paragraph("<b>PROGETTO DI ESERCIZIO GIOVEDÌ BASE SCOLASTICO (SOLUZIONE 1)</b><br/>Audit di Conformità CCNL Autoferrotranvieri & Legge 14 Febbraio 1958, n. 138", subtitle))
elements.append(Spacer(1, 8))

# Box Sintesi Risultati
box_sintesi_data = [
    [Paragraph("<b>SINTESI DEI RISULTATI DELL'ELABORAZIONE SINDACALE AUTISTI</b>", ParagraphStyle('WHead', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white)), Paragraph("", ParagraphStyle('WHead', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white))],
    [Paragraph("<b>Turni Totali Rete Analizzati:</b>", cell_bld), Paragraph("<b>156 Turni Ordinari</b> (+10 Piobesi e 9 Malpensa = 175 Totali)", cell_txt)],
    [Paragraph("<b>Copertura Corse di Linea / Scuole:</b>", cell_bld), Paragraph("<b>1.073 corse su 1.073 (100,0% COPERTO - ZERO TAGLI)</b>", cell_bld)],
    [Paragraph("<b>Turni Critici Ristrutturati (Nastro > 10h):</b>", cell_bld), Paragraph("<b>57 Turni</b> ricondotti tutti a Nastro compatto &le; 8h30 (nessun turno oltre 12h)", cell_txt)],
    [Paragraph("<b>Turni Speciali 40h (Riposo Fisso Sab+Dom):</b>", cell_bld), Paragraph("<b>4 Turni</b> (To0280, To0660, Pi0140, Pi0200) a 8h00 piene (Schema 5+2)", cell_txt)],
    [Paragraph("<b>Turni con Paga Sotto 6h30:</b>", cell_bld), Paragraph("<b>0 Turni</b> (Azzerati tutti i 39 casi aziendali sotto soglia)", cell_bld)],
    [Paragraph("<b>Vincolo Deposito di Residenza A/R:</b>", cell_bld), Paragraph("<b>100% Rispettato</b> (Inizio e Fine sempre nello stesso deposito)", cell_txt)],
    [Paragraph("<b>Costi Aggiuntivi per l'Azienda:</b>", cell_bld), Paragraph("<b>€ 0,00 (ZERO COSTI AGGIUNTIVI)</b>", cell_bld)],
    [Paragraph("<b>Risparmio Diretto per l'Azienda:</b>", cell_bld), Paragraph("<b>€ 43.008,00 / ANNO</b> (Spettanze non dovute, meno supero nastro e gasolio)", ParagraphStyle('GreenBld', fontName='Helvetica-Bold', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#006600')))],
]
t_sintesi = Table(box_sintesi_data, colWidths=[190, 355])
t_sintesi.setStyle(TableStyle([
    ('SPAN', (0,0), (1,0)),
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F4F9FF')),
    ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#003366')),
    ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBDDEE')),
    ('TOPPADDING', (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
]))
elements.append(t_sintesi)
elements.append(Spacer(1, 8))

# 1. Violazioni Normative
elements.append(Paragraph("<b>1. QUADRO DELLE VIOLAZIONI NORMATIVE NELL'ORARIO AZIENDALE 2026</b>", sec_title))
elements.append(Spacer(1, 2))
txt_norma = "• <b>CCNL Autoferrotranvieri (Nastro Max 12h):</b> L'azienda ha inserito <b>16 turni illegittimi oltre le 12 ore</b> (Bo3020 a 13h15, Pt0040 e Sa0030 a 12h55, Ba3510 a 12h45, Pb0060 a 12h27, Pe0070 a 12h25). Il CCNL consente il superamento delle 12h solo per motivi eccezionali in quantità minima.<br/>" \
            "• <b>Legge 14 Febbraio 1958, n. 138 (Art. 3, 5, 6, 8):</b> Dilatazione artificiosa del nastro con stacchi inoperosi non pagati fino a 5-6 ore al giorno, violazione del riposo giornaliero di 11h consecutive e frammentazione fino a 4-5 riprese.<br/>" \
            "• <b>Diritto al Riposo Compensativo 5+2 (Sabato e Domenica):</b> Lavorando su 5 giorni feriali (Lun-Ven) a 8h00 piene (40h settimanali), sorge il diritto di legge al riposo continuativo di 48h nel fine settimana."
elements.append(Paragraph(txt_norma, body))
elements.append(Spacer(1, 8))

# 2. Fabbisogno Autisti
elements.append(Paragraph("<b>2. FABBISOGNO GIORNALIERO AUTISTI PER DEPOSITO (INVARIATO A 156 NETTI / 175 LORDI)</b>", sec_title))
elements.append(Spacer(1, 2))
tab_autisti_data = [
    [Paragraph("Deposito / Residenza", h_cell), Paragraph("Autisti/Giorno", h_cell), Paragraph("Quota %", h_cell), Paragraph("Impostazione Operativa Nostra Proposta", h_cell)],
    [Paragraph("TORINO (Grugliasco)", cell_bld), Paragraph("38", cell_txt), Paragraph("21,7%", cell_txt), Paragraph("2 turni 40h + Cambi auto a Porta Susa (0 vuoti bus)", cell_txt)],
    [Paragraph("PINEROLO", cell_bld), Paragraph("32", cell_txt), Paragraph("18,3%", cell_txt), Paragraph("2 turni 40h + Assorbimento valli/scuole (0 cambi fuori sede)", cell_txt)],
    [Paragraph("PEROSA ARGENTINA", cell_bld), Paragraph("25", cell_txt), Paragraph("14,3%", cell_txt), Paragraph("Nastri abbattuti da 12h30 a &le; 8h15 (Rientro a Perosa)", cell_txt)],
    [Paragraph("PONT SAINT MARTIN / IVREA", cell_bld), Paragraph("17", cell_txt), Paragraph("9,7%", cell_txt), Paragraph("Nastro ridotto da 12h a 5h53/7h45 (Rientro a Pont Rimessa)", cell_txt)],
    [Paragraph("SUSA & SALBERTRAND", cell_bld), Paragraph("19", cell_txt), Paragraph("10,9%", cell_txt), Paragraph("Nastro compatto senza buchi diurni, rientro in sede", cell_txt)],
    [Paragraph("PIOBESI TORINESE", cell_bld), Paragraph("10", cell_txt), Paragraph("5,7%", cell_txt), Paragraph("Copertura 100% linea 000267 + Rifornimento Beinasco CNG", cell_txt)],
    [Paragraph("CASELLE AEROPORTO", cell_bld), Paragraph("9", cell_txt), Paragraph("5,1%", cell_txt), Paragraph("100% dedicato su linea navetta 000268 Caselle", cell_txt)],
    [Paragraph("BARGE / BOBBIO / LUSERNA", cell_bld), Paragraph("13", cell_txt), Paragraph("7,4%", cell_txt), Paragraph("Turni unici senza soste a vuoto a Pinerolo", cell_txt)],
    [Paragraph("LINEA MALPENSA (To20xx)", cell_bld), Paragraph("9", cell_txt), Paragraph("5,1%", cell_txt), Paragraph("Turni Malpensa dedicati puri (sganciata corsa Piobesi)", cell_txt)],
    [Paragraph("TORINO (Linee FT)", cell_bld), Paragraph("3", cell_txt), Paragraph("1,7%", cell_txt), Paragraph("Accorpati a turni montanti di linea (Paga piena &ge; 6h40)", cell_txt)],
    [Paragraph("<b>TOTALE GIORNALIERO</b>", cell_bld), Paragraph("<b>175 (156 netti)</b>", cell_bld), Paragraph("<b>100%</b>", cell_bld), Paragraph("<b>1.073 corse su 1.073 garantite al 100%</b>", cell_bld)],
]
t_aut = Table(tab_autisti_data, colWidths=[120, 70, 45, 310])
t_aut.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8F9FA')]),
    ('TOPPADDING', (0,0), (-1,-1), 1.5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
]))
elements.append(t_aut)

elements.append(PageBreak())

# PAGINA 2
# 3. Spettanze e Risparmi
elements.append(Paragraph("<b>3. BILANCIO ECONOMICO DELLE SPETTANZE CONTRATTUALI RISPARMIATE DALL'AZIENDA</b>", sec_title))
elements.append(Paragraph("Calcolo analitico del risparmio diretto per Arriva Italia su 210 giorni scolastici annui:", body))
elements.append(Spacer(1, 2))

tab_spettanze_data = [
    [Paragraph("Voce di Spettanza Contrattuale", h_cell), Paragraph("Regola di Calcolo Applicata", h_cell), Paragraph("Situazione Azienda 2026", h_cell), Paragraph("Nostra Proposta", h_cell), Paragraph("Risparmio Annuo (210 gg)", h_cell)],
    [
        Paragraph("<b>1. Supero Nastro (> 12h00)</b>", cell_bld),
        Paragraph("I minuti oltre 12h concorrono a 9h30 di GL (Riposo pagato ~142,50 €)", cell_txt),
        Paragraph("297 min/giorno (109,4 giorni di GL pagati all'anno)", cell_txt),
        Paragraph("0 minuti (Nastro sempre &le; 8h30)", cell_bld),
        Paragraph("<b>€ 15.592,50</b>", cell_bld)
    ],
    [
        Paragraph("<b>2. Indennità Riprese (AITO)</b>", cell_bld),
        Paragraph("3ª rip: +0,50€ | 4ª rip: +2,50€ | 5ª rip: +3,50€ (Cumulative)", cell_txt),
        Paragraph("€ 54,50 / giorno erogati per turni frammentati", cell_txt),
        Paragraph("€ 0,00 (Turni unici senza 3ª/4ª/5ª ripresa)", cell_bld),
        Paragraph("<b>€ 11.445,00</b>", cell_bld)
    ],
    [
        Paragraph("<b>3. Concorso Pasti</b>", cell_bld),
        Paragraph("1,00 € per ogni turno spezzato prolungato", cell_txt),
        Paragraph("€ 73,00 / giorno erogati per spezzoni fittizi", cell_txt),
        Paragraph("Ridotti a turni fisiologici (-15 pasti/gg)", cell_txt),
        Paragraph("<b>€ 3.150,00</b>", cell_bld)
    ],
    [
        Paragraph("<b>4. Carburante & Bus a Vuoto</b>", cell_bld),
        Paragraph("Costo gasolio e usura autobus a vuoto: 1,85 € / km", cell_txt),
        Paragraph("33 km a vuoto al giorno (Perosa, Pont, Piobesi)", cell_txt),
        Paragraph("0 km a vuoto aggiunti (Cambi auto a Porta Susa)", cell_bld),
        Paragraph("<b>€ 12.820,50</b>", cell_bld)
    ],
    [
        Paragraph("<b>🏆 TOTALE RISPARMIO DIRETTO</b>", cell_bld),
        Paragraph("<b>Somma delle economie vive generate per l'Azienda</b>", cell_bld),
        Paragraph("Costo annuo evitabile: € 43.008,00", cell_bld),
        Paragraph("<b>Ottimizzazione Strutturale</b>", cell_bld),
        Paragraph("<b>€ 43.008,00 / anno</b>", ParagraphStyle('GrnBig', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor('#006600')))
    ]
]
t_spett = Table(tab_spettanze_data, colWidths=[110, 130, 115, 100, 90])
t_spett.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
    ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor('#F8F9FA')]),
    ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E8F5E9')),
    ('TOPPADDING', (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
]))
elements.append(t_spett)
elements.append(Spacer(1, 8))

# 4. Regole Operative
elements.append(Paragraph("<b>4. REGOLE OPERATIVE BLINDATE (ZERO COSTI DI TRASFERTA & ZERO VUOTI)</b>", sec_title))
elements.append(Spacer(1, 2))
txt_regole = "• <b>1. Vincolo Ferreo di Residenza (Stesso Deposito A/R):</b> Tutti i 156 turni iniziano e finiscono tassativamente nello stesso deposito di appartenenza. Nessun autista monta o smonta fuori sede. <b>Costi di trasferta e ore di percorrenza passiva = € 0,00</b>.<br/>" \
             "• <b>2. Nessun Cambio Fuori Residenza da Pinerolo:</b> È vietato inviare autisti di Pinerolo a prendere bus a Barge, Luserna o Perosa. I depositi periferici sono guidati esclusivamente dai propri residenti.<br/>" \
             "• <b>3. Gestione Cambi a Porta Susa (c.so Bolzano):</b> Introdotti cambi sul posto con l'<b>auto di servizio aziendale</b> solo su <b>7 turni di Torino</b> (`To0610`, `To0620`, `To0650`, `To0660`, `To0670`, `To0700`, `To0710`), azzerando i viaggi a vuoto dei bus verso Grugliasco.<br/>" \
             "• <b>4. Coincidenze Blindate (1.030 interscambi):</b> Gli orari di transito e arrivo ai nodi di Pinerolo, Perosa, Ivrea, Susa e Airasca non sono stati toccati: tutte le coincidenze bus/treno sono garantite con buffer di 5-10 min.<br/>" \
             "• <b>5. Rifornimento Metano e Gasolio a Piobesi:</b> Il rifornimento CNG avviene al Distributore di Beinasco / Grugliasco a metà turno a corsa conclusa e bus vuoto, senza spezzare le corse e senza viaggi a vuoto di rientro a Piobesi.<br/>" \
             "• <b>6. Orario di Lavoro e Straordinario (Fascia 8h00 - 8h40):</b> Nessun turno è sotto 6h30; i turni Lun-Ven possono salire fino a 8h40 pagate con straordinario da turno e maturazione del riposo continuativo Sabato e Domenica."
elements.append(Paragraph(txt_regole, body))
elements.append(Spacer(1, 8))

# 5. I 4 Turni a 40h
elements.append(Paragraph("<b>5. I 4 TURNI SPECIALI A 40h SETTIMANALI (RIPOSO FISSO SABATO E DOMENICA - 5+2)</b>", sec_title))
elements.append(Spacer(1, 2))
tab_40h_data = [
    [Paragraph("Codice Turno", h_cell), Paragraph("Deposito", h_cell), Paragraph("Orario Servizio", h_cell), Paragraph("Nuovo Nastro", h_cell), Paragraph("Nuovo OLG (Paga)", h_cell), Paragraph("Articolazione Linea & Riposo Settimanale", h_cell)],
    [Paragraph("<b>To0280</b>", cell_bld), Paragraph("TORINO (Grugliasco)", cell_txt), Paragraph("05:05 - 13:10", cell_txt), Paragraph("8h 05m", cell_bld), Paragraph("<b>8h 00m</b> (40h/sett)", cell_bld), Paragraph("Linea 000268 Navetta Caselle continuativa -> <b>Riposo Fisso Sabato e Domenica</b>", cell_txt)],
    [Paragraph("<b>To0660</b>", cell_bld), Paragraph("TORINO (Grugliasco)", cell_txt), Paragraph("09:30 - 17:35", cell_txt), Paragraph("8h 05m", cell_bld), Paragraph("<b>8h 00m</b> (40h/sett)", cell_bld), Paragraph("Linee 000266/000277 Pinerolo Autostrada e Mopar -> <b>Riposo Fisso Sabato e Domenica</b>", cell_txt)],
    [Paragraph("<b>Pi0140</b>", cell_bld), Paragraph("PINEROLO", cell_txt), Paragraph("05:45 - 13:50", cell_txt), Paragraph("8h 05m", cell_bld), Paragraph("<b>8h 00m</b> (40h/sett)", cell_bld), Paragraph("Linee 000275/000281 Industriale TN Italy e Scuole -> <b>Riposo Fisso Sabato e Domenica</b>", cell_txt)],
    [Paragraph("<b>Pi0200</b>", cell_bld), Paragraph("PINEROLO", cell_txt), Paragraph("12:30 - 20:35", cell_txt), Paragraph("8h 05m", cell_bld), Paragraph("<b>8h 00m</b> (40h/sett)", cell_bld), Paragraph("Linee 000282/000284 None e Val Pellice SKF -> <b>Riposo Fisso Sabato e Domenica</b>", cell_txt)],
]
t_40h = Table(tab_40h_data, colWidths=[55, 95, 75, 65, 85, 170])
t_40h.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F5FFF5')]),
    ('TOPPADDING', (0,0), (-1,-1), 1.8),
    ('BOTTOMPADDING', (0,0), (-1,-1), 1.8),
]))
elements.append(t_40h)
elements.append(Spacer(1, 8))

elements.append(Paragraph("<i>Documento tecnico-sindacale elaborato ad uso della Delegazione Trattante RSU / OO.SS. per la trattativa con Arriva Italia S.p.A.</i>", ParagraphStyle('Foot', fontName='Helvetica-Oblique', fontSize=6.5, leading=8, textColor=colors.HexColor('#666666'), alignment=1)))

doc.build(elements)
print("✅ DOSSIER TECNICO-ECONOMICO-SINDACALE GENERATO CON SUCCESSO!")
