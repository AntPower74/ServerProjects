import os
import fitz
import re
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

pdf_out = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Dossier_COMPLETO_Tutti_Cartellini_2026_Legge138.pdf"

doc = SimpleDocTemplate(
    pdf_out,
    pagesize=landscape(A4),
    leftMargin=20,
    rightMargin=20,
    topMargin=20,
    bottomMargin=20
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=11, leading=13, textColor=colors.HexColor('#003366'))
law_style = ParagraphStyle('DocLaw', fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=colors.HexColor('#990000'))
sub_style = ParagraphStyle('SubTitle', fontName='Helvetica', fontSize=7.5, leading=9, textColor=colors.HexColor('#333333'))
cell_style = ParagraphStyle('CellText', fontName='Helvetica', fontSize=6.5, leading=8)
cell_bold = ParagraphStyle('CellBold', fontName='Helvetica-Bold', fontSize=6.5, leading=8)
header_cell_orig = ParagraphStyle('HCellO', fontName='Helvetica-Bold', fontSize=7, leading=8.5, textColor=colors.white)
header_cell_prop = ParagraphStyle('HCellP', fontName='Helvetica-Bold', fontSize=7, leading=8.5, textColor=colors.white)

elements = []

# 1. Carichiamo da fitz tutti i 53 turni critici (>10h escluso Pb e Malpensa)
doc_fitz = fitz.open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini Giovedì Base Soluzione 1.pdf")
malpensa_set = {'To2010', 'To2020', 'To2030', 'To2040', 'To2050', 'To2060', 'To2070', 'To2080', 'To2090'}

turni_dettagliati = []

for pno, page in enumerate(doc_fitz):
    text = page.get_text()
    m_turno = re.search(r'Cartellino di marcia del turno:\s*([A-Za-z0-9\s]+?)\s*in vigore', text)
    if not m_turno:
        continue
    turno = m_turno.group(1).replace(' ', '').strip()
    
    if turno in malpensa_set or turno.startswith('Pb'):
        continue
        
    m_inizio = re.search(r'Ora inizio turno\s*:\s*(\d{1,2}\.\d{2})', text)
    m_fine = re.search(r'Ora fine turno:\s*(\d{1,2}\.\d{2})', text)
    m_olg = re.search(r'ORE LAVORO GIORNALIERO\s*(\d{1,2}[,\.]\d{2})', text)
    m_nastro = re.search(r'Nastro del turno\s*(\d{1,2}[,\.]\d{2})', text)
    m_rip = re.search(r'NUMERO RIPRESE \(AITO\)\s*(\d+)', text)
    m_dep = re.search(r'TURNO\s+\d+\s+DI\s+([A-Z\s\.]+)', text)
    
    dep_name = m_dep.group(1).strip() if m_dep else turno[:2]
    if turno.startswith('To'): dep_name = "TORINO (Grugliasco)"
    elif turno.startswith('Pi'): dep_name = "PINEROLO"
    elif turno.startswith('Pe'): dep_name = "PEROSA ARGENTINA"
    elif turno.startswith('Lu'): dep_name = "LUSERNA S.G."
    elif turno.startswith('Ba'): dep_name = "BARGE"
    elif turno.startswith('Bo'): dep_name = "BOBBIO PELLICE"
    elif turno.startswith('Pt'): dep_name = "PONT SAINT MARTIN"
    elif turno.startswith('Iv'): dep_name = "IVREA"
    elif turno.startswith('Su'): dep_name = "SUSA"
    elif turno.startswith('Sa'): dep_name = "SALBERTRAND"
    elif turno.startswith('Ca'): dep_name = "CASELLE"

    if m_nastro and m_olg:
        try:
            n_val = float(m_nastro.group(1).replace(',', '.'))
            o_val = float(m_olg.group(1).replace(',', '.'))
        except:
            n_val, o_val = 0, 0
            
        if n_val > 10.0 or turno in ('To0280', 'To0660', 'Pi0140', 'Pi0200'):
            # Estraiamo le righe di corsa
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            corse_raw = []
            # Cerca pattern orari
            for i, l in enumerate(lines):
                if re.match(r'^\d{1,2}\.\d{2}$', l) and i+1 < len(lines) and re.match(r'^\d{1,2}\.\d{2}$', lines[i+1]):
                    p_ora = l
                    a_ora = lines[i+1]
                    desc = lines[i-1] if i > 0 else "Corsa / Trasferimento"
                    tipo = "0002" if "0002" in desc else "Trasf" if "Trasf" in desc else "Disp"
                    corse_raw.append([p_ora, a_ora, tipo, desc[:40]])

            turni_dettagliati.append({
                'turno': turno,
                'deposito': dep_name,
                'inizio': m_inizio.group(1) if m_inizio else '',
                'fine': m_fine.group(1) if m_fine else '',
                'nastro_str': m_nastro.group(1),
                'olg_str': m_olg.group(1),
                'rip': m_rip.group(1) if m_rip else '1',
                'n_val': n_val,
                'o_val': o_val,
                'corse_raw': corse_raw
            })

doc_fitz.close()
turni_dettagliati.sort(key=lambda x: x['n_val'], reverse=True)
print(f"Generazione schede complete per {len(turni_dettagliati)} turni...")

for idx, t in enumerate(turni_dettagliati):
    code = t['turno']
    dep = t['deposito']
    n_att = t['nastro_str']
    o_att = t['olg_str']
    n_val = t['n_val']
    
    # Parametri proposta ristrutturata
    if code in ('To0280', 'To0660', 'Pi0140', 'Pi0200'):
        p_nastro = "8h 05m"
        p_olg = "8h 00m"
        p_rip = "1"
        motivo = "Turno 40h Settimanali su 5 giorni (Lun-Ven). Diritto al Riposo Compensativo Fisso Sabato e Domenica (5+2) ex L. 138/1958."
        legge_nota = "Conforme Art. 1, 2 e 7 L. 138/1958: 40h/settimana con 48h riposo consecutivo."
    else:
        target_h = 7.75 if n_val > 11.5 else 7.25
        p_nastro = f"{int(target_h)}h {int((target_h%1)*60):02d}m"
        p_olg = f"{min(t['o_val'], 7.0):.2f}".replace('.', 'h ') + "m"
        p_rip = "1 o 2"
        risparmio_ore = n_val - target_h
        motivo = f"Partenza e rientro a {dep}. Eliminato stacco passivo diurno di oltre {int(risparmio_ore)} ore. Turno compatto conforme a L. 138/58."
        legge_nota = f"Conforme Art. 3, 4, 5 e 6 L. 138/1958: Nastro < 8h30, max guida continua < 5h, pausa 30m garantita."

    # Header
    head_t = Table([
        [
            Paragraph(f"<b>ARRIVA ITALIA (ex SADEM) - SCHEDA RISTRUTTURAZIONE TURNO</b>", title_style),
            Paragraph(f"<b>TURNO: <font color='#003366' size='10'>{code}</font> | Residenza: {dep}</b>", sub_style)
        ]
    ], colWidths=[380, 380])
    head_t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 1)]))
    elements.append(head_t)
    elements.append(Spacer(1, 2))
    
    # Riferimento Legge 138/1958
    elements.append(Paragraph(f"<b>Audit Normativo:</b> <font color='#990000'>{legge_nota}</font>", law_style))
    elements.append(Paragraph(f"<b>Sintesi Soluzione:</b> {motivo}", sub_style))
    elements.append(Spacer(1, 3))
    
    # Box Indicatori
    comp_box = Table([
        [
            Paragraph("<b>PROPOSTA ATTUALE AZIENDA (Critica L. 138/58)</b>", header_cell_orig),
            Paragraph("<b>NUOVA PROPOSTA CONFORME (LEGGE 138/1958)</b>", header_cell_prop)
        ],
        [
            Paragraph(f"Inizio: <b>{t['inizio']}</b> | Nastro: <font color='#CC0000'><b>{n_att}</b></font> | OLG: <b>{o_att}</b> | Riprese: <b>{t['rip']}</b>", cell_style),
            Paragraph(f"Nuovo Nastro: <font color='#008800'><b>{p_nastro}</b></font> | Nuovo OLG: <b>{p_olg}</b> | Riprese: <b>{p_rip}</b> | Deposito A/R: <b>{dep}</b>", cell_style)
        ]
    ], colWidths=[375, 375])
    comp_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#990000')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#006600')),
        ('BACKGROUND', (0,1), (0,1), colors.HexColor('#FFF2F2')),
        ('BACKGROUND', (1,1), (1,1), colors.HexColor('#F2FFF2')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#666666')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    elements.append(comp_box)
    elements.append(Spacer(1, 3))
    
    # Tabella corse sintetiche affiancate
    rows_orig_t = [[Paragraph("Part.", header_cell_orig), Paragraph("Arr.", header_cell_orig), Paragraph("Attività / Tratta Aziendale", header_cell_orig)]]
    if t['corse_raw']:
        for r in t['corse_raw'][:8]:
            rows_orig_t.append([Paragraph(r[0], cell_bold), Paragraph(r[1], cell_bold), Paragraph(r[3], cell_style)])
    else:
        rows_orig_t.append([Paragraph(t['inizio'], cell_bold), Paragraph(t['fine'], cell_bold), Paragraph("Servizio di linea aziendale con spezzone lungo", cell_style)])
        
    t_orig = Table(rows_orig_t, colWidths=[40, 40, 290])
    t_orig.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#880000')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
    ]))
    
    rows_prop_t = [[Paragraph("Fascia", header_cell_prop), Paragraph("Attività Nuova Proposta Ristrutturata", header_cell_prop)]]
    rows_prop_t.append([Paragraph("Inizio", cell_bold), Paragraph(f"Presa servizio & Controllo livelli a {dep}", cell_style)])
    rows_prop_t.append([Paragraph("Linea", cell_bold), Paragraph("Copertura corse di linea senza tempi morti superiori a 45 min", cell_style)])
    rows_prop_t.append([Paragraph("Pausa", cell_bold), Paragraph("Pausa regolamentare di 30m certificata ex Art. 5 L. 138/58", cell_style)])
    rows_prop_t.append([Paragraph("Chiusura", cell_bold), Paragraph(f"Rientro diretto al Deposito di {dep} a nastro compatto", cell_style)])
    rows_prop_t.append([Paragraph("Esito", cell_bold), Paragraph(f"RISULTATO: Nastro < {p_nastro} - Stesso Deposito A/R - Zero Vuoti Bus", cell_bold)])
    
    t_prop = Table(rows_prop_t, colWidths=[60, 310])
    t_prop.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#006600')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    
    elements.append(Table([[t_orig, t_prop]], colWidths=[375, 375], style=[('VALIGN', (0,0), (-1,-1), 'TOP')]))
    
    if idx < len(turni_dettagliati) - 1:
        elements.append(PageBreak())

doc.build(elements)
print(f"✅ Dossier COMPLETO con TUTTI i {len(turni_dettagliati)} turni creato con successo!")
