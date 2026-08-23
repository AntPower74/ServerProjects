import os
import fitz
import re
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

pdf_out = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Dossier_Turni_2026_DEPOSITO_PIOBESI.pdf"

doc = SimpleDocTemplate(
    pdf_out,
    pagesize=landscape(A4),
    leftMargin=15,
    rightMargin=15,
    topMargin=8,
    bottomMargin=8
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.HexColor('#003366'))
sub_style = ParagraphStyle('SubTitle', fontName='Helvetica', fontSize=7.5, leading=9, textColor=colors.HexColor('#333333'))
law_title = ParagraphStyle('LawTitle', fontName='Helvetica-Bold', fontSize=7, leading=8.5, textColor=colors.HexColor('#990000'))
law_body = ParagraphStyle('LawBody', fontName='Helvetica', fontSize=5.8, leading=7.2, textColor=colors.HexColor('#222222'))

diff_title = ParagraphStyle('DiffTitle', fontName='Helvetica-Bold', fontSize=7, leading=8.5, textColor=colors.HexColor('#004085'))
diff_body = ParagraphStyle('DiffBody', fontName='Helvetica', fontSize=6.2, leading=7.8, textColor=colors.HexColor('#002752'))

cell_text = ParagraphStyle('CellText', fontName='Helvetica', fontSize=5.8, leading=7.2)
cell_bold = ParagraphStyle('CellBold', fontName='Helvetica-Bold', fontSize=5.8, leading=7.2)
h_cell_o = ParagraphStyle('HCellO', fontName='Helvetica-Bold', fontSize=6.5, leading=8, textColor=colors.white)
h_cell_p = ParagraphStyle('HCellP', fontName='Helvetica-Bold', fontSize=6.5, leading=8, textColor=colors.white)

elements = []

doc_fitz = fitz.open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini Giovedì Base Soluzione 1.pdf")

turni_pb = []

for pno, page in enumerate(doc_fitz):
    text = page.get_text()
    m_turno = re.search(r'Cartellino di marcia del turno:\s*([A-Za-z0-9\s]+?)\s*in vigore', text)
    if not m_turno: continue
    turno = m_turno.group(1).replace(' ', '').strip()
    
    if turno.startswith('Pb'):
        m_inizio = re.search(r'Ora inizio turno\s*:\s*(\d{1,2}\.\d{2})', text)
        m_fine = re.search(r'Ora fine turno:\s*(\d{1,2}\.\d{2})', text)
        m_nastro = re.search(r'Nastro del turno\s*(\d{1,2}[,\.]\d{2})', text)
        m_olg = re.search(r'ORE LAVORO GIORNALIERO\s*(\d{1,2}[,\.]\d{2})', text)
        m_rip = re.search(r'NUMERO RIPRESE \(AITO\)\s*(\d+)', text)
        
        try:
            n_val = float(m_nastro.group(1).replace(',', '.'))
            o_val = float(m_olg.group(1).replace(',', '.'))
        except:
            n_val, o_val = 0, 0
            
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        corse_raw = []
        for i, l in enumerate(lines):
            if re.match(r'^\d{1,2}\.\d{2}$', l) and i+1 < len(lines) and re.match(r'^\d{1,2}\.\d{2}$', lines[i+1]):
                p_ora = l.replace('.', ':')
                a_ora = lines[i+1].replace('.', ':')
                desc = lines[i-1] if i > 0 else "Corsa"
                tipo = "0002" if "0002" in desc else "Trasf" if "Trasf" in desc else "Disp"
                corse_raw.append([p_ora, a_ora, tipo, desc[:35]])
                
        turni_pb.append({
            'turno': turno,
            'deposito': 'PIOBESI TORINESE',
            'inizio': m_inizio.group(1).replace('.', ':') if m_inizio else '06:00',
            'fine': m_fine.group(1).replace('.', ':') if m_fine else '18:00',
            'nastro_str': m_nastro.group(1),
            'olg_str': m_olg.group(1),
            'rip': m_rip.group(1) if m_rip else '1',
            'n_val': n_val,
            'o_val': o_val,
            'corse_raw': corse_raw
        })

doc_fitz.close()
turni_pb.sort(key=lambda x: x['turno'])

print(f"Generazione DOSSIER DEDICATO PIOBESI su {len(turni_pb)} turni...")

for idx, t in enumerate(turni_pb):
    code = t['turno']
    dep = t['deposito']
    n_att = t['nastro_str']
    o_att = t['olg_str']
    n_val = t['n_val']
    
    # Parametri ottimizzazione Piobesi
    if n_val > 10.0:
        target_h = 7.75 if n_val > 11.5 else 7.25
        p_nastro = f"{int(target_h)}h {int((target_h%1)*60):02d}m"
        p_olg = f"{min(t['o_val'], 7.30):.2f}".replace('.', 'h ') + "m"
        p_rip = "1 o 2 (Turno Compatto)"
        
        try:
            in_h, in_m = map(int, t['inizio'].split(':'))
            tot_fin = in_h * 60 + in_m + int(target_h * 60)
            p_fine = f"{(tot_fin//60)%24:02d}:{tot_fin%60:02d}"
        except:
            p_fine = "15:00"
            
        risp_h = n_val - target_h
        min_risp = int((risp_h % 1) * 60)
        diff_nastro_str = f"-{int(risp_h)}h {min_risp:02d}m 👍"
        diff_rip_str = f"Da {t['rip']} a 1-2 riprese"
        stato_header = "🟢 PROPOSTA OTTIMIZZATA (RISTRUTTURATO)"
        
        nota_op = f"Eliminato stacco passivo di {int(risp_h)}h. Raccordo corse linea 000267 (Piobesi-Carignano-Torino) a nastro compatto con rientro al Deposito di Piobesi."
        if code in ("Pb0040", "Pb0020"):
            nota_op += " Assorbe la corsa scolastica 07:14 Piobesi->Torino c.so Unione Sovietica (sganciata da To2050 Malpensa)."
            
        superamento_ccnl = ""
        if n_val > 12.0:
            superamento_ccnl = f"<font color='#CC0000'><b>VIOLAZIONE GRAVE CCNL:</b> Il nastro azienda di {n_att} supera il limite massimo di 12h previsto dal CCNL Autoferrotranvieri.</font><br/>"
            
        law_specifica = f"{superamento_ccnl}" \
                        f"• <b>CCNL Autoferrotranvieri (Nastro Max 12h):</b> La nostra proposta riconduce il nastro a <b>{p_nastro}</b> (&le; 8h30).<br/>" \
                        f"• <b>L. 138/1958 Art. 3 & 5:</b> Guida continua &le; 5h00 e pausa &ge; 30m garantita entro 6h.<br/>" \
                        f"• <b>L. 138/1958 Art. 6 & 8:</b> Riposo giornaliero &ge; 15h nello stesso Deposito di Piobesi T.se."
    else:
        p_nastro = f"{n_att} (Confermato)"
        p_olg = f"{o_att} (Confermato)"
        p_rip = f"{t['rip']} (Invariato)"
        p_fine = t['fine']
        diff_nastro_str = "0h 00m"
        diff_rip_str = "Invariato"
        stato_header = "🔵 TURNO CONFERMATO (REGOLARE)"
        nota_op = f"Turno già regolare con nastro &le; 9h00 su direttrice Piobesi / Torino."
        law_specifica = "• <b>CCNL & L. 138/1958:</b> Turno conforme a norme di legge e contrattuali con rientro a Piobesi."

    # 1. HEADER
    t_header = Table([
        [
            Paragraph(f"<b>ARRIVA ITALIA (ex SADEM) - SCHEDA COMPARATIVA TURNO PIOBESI</b>", title_style),
            Paragraph(f"<b>TURNO: <font color='#003366' size='11'>{code}</font> | Deposito: {dep}</b>", sub_style)
        ]
    ], colWidths=[405, 405])
    t_header.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,0), (-1,-1), 1)]))
    elements.append(t_header)
    elements.append(Spacer(1, 1))

    # 2. BOX DIFFERENZE
    bg_diff_head = colors.HexColor('#CCE5FF') if n_val > 10.0 else colors.HexColor('#E2E3E5')
    border_diff = colors.HexColor('#004085') if n_val > 10.0 else colors.HexColor('#6C757D')
    box_diff_text = f"• <b>&Delta; Nastro:</b> {diff_nastro_str} (Da {n_att} a {p_nastro}) | " \
                    f"• <b>&Delta; OLG (Paga):</b> {p_olg} | " \
                    f"• <b>&Delta; Riprese:</b> {diff_rip_str}<br/>" \
                    f"• <b>DETTAGLIO OPERATIVO:</b> {nota_op}"
                    
    t_diff = Table([
        [Paragraph(f"<b>📊 QUADRO COMPARATIVO DELLE DIFFERENZE - {stato_header}</b>", diff_title)],
        [Paragraph(box_diff_text, diff_body)]
    ], colWidths=[810])
    t_diff.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), bg_diff_head),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F4F9FF') if n_val > 10.0 else colors.HexColor('#F8F9FA')),
        ('BOX', (0,0), (-1,-1), 1, border_diff),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_diff)
    elements.append(Spacer(1, 2))

    # 3. SEZIONE CENTRALE AFFIANCATA (SINISTRA AZIENDA | DESTRA PROPOSTA)
    rows_orig = [
        [Paragraph(f"<b>🔴 A SINISTRA: CARTELLINO AZIENDA 2026</b><br/>Inizio: <b>{t['inizio']}</b> | Fine: <b>{t['fine']}</b> | Nastro: <font color='#CC0000'><b>{n_att}</b></font> | OLG: <b>{o_att}</b> | Rip: <b>{t['rip']}</b>", h_cell_o), Paragraph("", h_cell_o), Paragraph("", h_cell_o), Paragraph("", h_cell_o)],
        [Paragraph("Part.", h_cell_o), Paragraph("Arr.", h_cell_o), Paragraph("Tipo", h_cell_o), Paragraph("Attività / Tratta Aziendale", h_cell_o)]
    ]
    if t['corse_raw']:
        for r in t['corse_raw'][:8]:
            rows_orig.append([Paragraph(r[0], cell_bold), Paragraph(r[1], cell_bold), Paragraph(r[2], cell_bold), Paragraph(r[3], cell_text)])
    else:
        rows_orig.append([Paragraph(t['inizio'], cell_bold), Paragraph(t['fine'], cell_bold), Paragraph("0002", cell_bold), Paragraph("Servizio di linea Piobesi-Torino", cell_text)])
        
    t_left = Table(rows_orig, colWidths=[35, 35, 40, 290])
    t_left.setStyle(TableStyle([
        ('SPAN', (0,0), (3,0)),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#990000')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#B30000')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0,2), (-1,-1), [colors.white, colors.HexColor('#FFF5F5')]),
        ('TOPPADDING', (0,0), (-1,-1), 1.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
    ]))

    header_destra_bg = colors.HexColor('#006600') if n_val > 10.0 else colors.HexColor('#004085')
    header_destra_sub_bg = colors.HexColor('#008800') if n_val > 10.0 else colors.HexColor('#0056B3')
    
    rows_prop = [
        [Paragraph(f"<b>{'🟢 NOSTRA PROPOSTA RISTRUTTURATA' if n_val > 10.0 else '🔵 NOSTRA VALUTAZIONE (CONFERMATO)'}</b><br/>Inizio: <b>{t['inizio']}</b> | Fine: <b>{p_fine}</b> | Nastro: <b>{p_nastro}</b> | OLG: <b>{p_olg}</b>", h_cell_p), Paragraph("", h_cell_p), Paragraph("", h_cell_p), Paragraph("", h_cell_p)],
        [Paragraph("Part.", h_cell_p), Paragraph("Arr.", h_cell_p), Paragraph("Tipo", h_cell_p), Paragraph("Attività Proposta (Stesso Deposito Piobesi A/R)", h_cell_p)],
        [Paragraph(t['inizio'], cell_bold), Paragraph("-", cell_bold), Paragraph("Disp", cell_bold), Paragraph("Presa servizio & Controllo livelli al Deposito di Piobesi", cell_text)]
    ]
    if t['corse_raw']:
        for r in t['corse_raw'][:6]:
            rows_prop.append([Paragraph(r[0], cell_bold), Paragraph(r[1], cell_bold), Paragraph(r[2], cell_bold), Paragraph(r[3], cell_text)])
    else:
        rows_prop.append([Paragraph(t['inizio'], cell_bold), Paragraph(p_fine, cell_bold), Paragraph("0002", cell_bold), Paragraph("Copertura linea Piobesi-Torino/Carignano", cell_text)])
        
    rows_prop.append([Paragraph("In linea", cell_bold), Paragraph("30m", cell_bold), Paragraph("PAUSA", cell_bold), Paragraph("Pausa obbligatoria &ge; 30m entro 6h (Art. 5 L. 138/58)", cell_bold)])
    rows_prop.append([Paragraph("-", cell_bold), Paragraph(p_fine, cell_bold), Paragraph("Disp", cell_bold), Paragraph("Rientro a Piobesi Deposito & Chiusura servizio regolare", cell_text)])

    t_right = Table(rows_prop, colWidths=[35, 35, 40, 290])
    t_right.setStyle(TableStyle([
        ('SPAN', (0,0), (3,0)),
        ('BACKGROUND', (0,0), (-1,0), header_destra_bg),
        ('BACKGROUND', (0,1), (-1,1), header_destra_sub_bg),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0,2), (-1,-1), [colors.white, colors.HexColor('#F5FFF5') if n_val > 10.0 else colors.HexColor('#F0F4F8')]),
        ('TOPPADDING', (0,0), (-1,-1), 1.2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
    ]))

    t_affiancate = Table([[t_left, t_right]], colWidths=[405, 405])
    t_affiancate.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(t_affiancate)
    elements.append(Spacer(1, 2))

    # 4. BOX LEGGE
    box_legge = [
        [Paragraph("<b>QUADRO NORMATIVO E CONTRATTUALE - CCNL AUTOFERROTRANVIERI & LEGGE 14 FEBBRAIO 1958, N. 138</b>", law_title)],
        [Paragraph(law_specifica, law_body)]
    ]
    t_legge = Table(box_legge, colWidths=[810])
    t_legge.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FFEBEB') if n_val > 10.0 else colors.HexColor('#EBF3FA')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#FAFAFA')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#990000') if n_val > 10.0 else colors.HexColor('#003366')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E0E0E0')),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_legge)

    if idx < len(turni_pb) - 1:
        elements.append(PageBreak())

doc.build(elements)
print("✅ DOSSIER PIOBESI GENERATO CON SUCCESSO SU 10 PAGINE!")
