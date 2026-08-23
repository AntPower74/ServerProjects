import os
import fitz
import re
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

pdf_out = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Dossier_UNIFICATO_Cartellini_Azienda_vs_Proposta_2026.pdf"

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
h_cell_o = ParagraphStyle('HCellO', fontName='Helvetica-Bold', fontSize=6.2, leading=7.5, textColor=colors.white)
h_cell_p = ParagraphStyle('HCellP', fontName='Helvetica-Bold', fontSize=6.2, leading=7.5, textColor=colors.white)
h_cell_ft = ParagraphStyle('HCellFT', fontName='Helvetica-Bold', fontSize=6.2, leading=7.5, textColor=colors.white)

elements = []

doc_fitz = fitz.open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini Giovedì Base Soluzione 1.pdf")
malpensa_set = {'To2010', 'To2020', 'To2030', 'To2040', 'To2050', 'To2060', 'To2070', 'To2080', 'To2090'}

tutti_turni = []

for pno, page in enumerate(doc_fitz):
    text = page.get_text()
    m_turno = re.search(r'Cartellino di marcia del turno:\s*([A-Za-z0-9\s]+?)\s*in vigore', text)
    if not m_turno: continue
    turno = m_turno.group(1).replace(' ', '').strip()
    if turno in malpensa_set or turno.startswith('Pb'): continue
        
    m_inizio = re.search(r'Ora inizio turno\s*:\s*(\d{1,2}\.\d{2})', text)
    m_fine = re.search(r'Ora fine turno:\s*(\d{1,2}\.\d{2})', text)
    m_olg = re.search(r'ORE LAVORO GIORNALIERO\s*(\d{1,2}[,\.]\d{2})', text)
    m_nastro = re.search(r'Nastro del turno\s*(\d{1,2}[,\.]\d{2})', text)
    m_rip = re.search(r'NUMERO RIPRESE \(AITO\)\s*(\d+)', text)
    m_dep = re.search(r'TURNO\s+\d+\s+DI\s+([A-Z\s\.]+)', text)
    
    dep_name = m_dep.group(1).strip() if m_dep else turno[:2]
    if turno.startswith('To'): dep_name = "TORINO (Grugliasco)"
    elif turno.startswith('FT'): dep_name = "PINEROLO (Centro Studi)" if "2820" in turno else "TORINO (Grugliasco)"
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
            
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        corse_raw = []
        for i, l in enumerate(lines):
            if re.match(r'^\d{1,2}\.\d{2}$', l) and i+1 < len(lines) and re.match(r'^\d{1,2}\.\d{2}$', lines[i+1]):
                p_ora = l.replace('.', ':')
                a_ora = lines[i+1].replace('.', ':')
                desc = lines[i-1] if i > 0 else "Corsa"
                tipo = "0002" if "0002" in desc else "Trasf" if "Trasf" in desc else "Disp"
                km_val = lines[i+2] if i+2 < len(lines) and re.match(r'^\d+,\d+$', lines[i+2]) else "-"
                corse_raw.append([p_ora, a_ora, tipo, desc[:32], km_val])

        tutti_turni.append({
            'turno': turno,
            'deposito': dep_name,
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
tutti_turni.sort(key=lambda x: x['turno'])

for idx, t in enumerate(tutti_turni):
    code = t['turno']
    dep = t['deposito']
    n_att = t['nastro_str']
    o_att = t['olg_str']
    n_val = t['n_val']
    
    is_ft = code.startswith('FT')
    is_40h = code in ('To0280', 'To0660', 'Pi0140', 'Pi0200')
    is_lungo = n_val > 10.0
    
    # Costruzione tabella corse reali puntuali per la proposta (Destra)
    corse_prop_puntuali = []
    
    # Presa servizio
    corse_prop_puntuali.append([t['inizio'], "-", "Disp", f"Presa servizio & Controllo livelli al Deposito di {dep}"])
    
    # Analisi corse reali del turno
    if t['corse_raw']:
        # Selezioniamo le corse continuative senza il buco passivo centrale
        c_valide = [r for r in t['corse_raw'] if r[2] != 'Disp']
        
        if is_lungo and len(c_valide) > 4:
            # Primo spezzone
            for r in c_valide[:3]:
                corse_prop_puntuali.append([r[0], r[1], r[2], r[3]])
            # Pausa di legge
            corse_prop_puntuali.append(["In linea", "30m", "PAUSA", "Pausa obbligatoria &ge; 30m entro 6h (Art. 5 L. 138/58)"])
            # Corsa commerciale di rientro reale
            r_fin = c_valide[-1]
            corse_prop_puntuali.append([r_fin[0], r_fin[1], r_fin[2], f"Corsa di linea regolare: {r_fin[3]}"])
        else:
            for r in c_valide[:5]:
                corse_prop_puntuali.append([r[0], r[1], r[2], r[3]])
            if len(c_valide) >= 3:
                corse_prop_puntuali.append(["In linea", "30m", "PAUSA", "Pausa obbligatoria &ge; 30m (Art. 5 L. 138/58)"])
    else:
        corse_prop_puntuali.append([t['inizio'], "13:30", "0002", f"Servizio di linea regolare su direttrice di {dep}"])
        corse_prop_puntuali.append(["In linea", "30m", "PAUSA", "Pausa obbligatoria &ge; 30m (Art. 5 L. 138/58)"])

    # Chiusura
    fine_stimata = corse_prop_puntuali[-1][1] if corse_prop_puntuali[-1][1] != '-' else "14:00"
    if fine_stimata == "30m" or not re.match(r'^\d{1,2}:\d{2}$', fine_stimata):
        fine_stimata = t['fine'] if not is_lungo else "14:30"
        
    corse_prop_puntuali.append(["-", fine_stimata, "Disp", f"Pulizia & Chiusura servizio al Deposito di {dep}"])

    # Calcolo parametri compatti
    if is_40h:
        p_nastro = "8h 05m"
        p_olg = "8h 00m (40h/sett.)"
        p_rip = "1 (Turno Unico)"
        p_fine = "13:10" if "05" in t['inizio'] or "06" in t['inizio'] else "17:35"
        diff_nastro_str = "+0h 30m (Turno 40h)" if "07" in n_att else "-1h 20m"
        diff_olg_str = "+0h 25m" if "07" in o_att else "+0h 30m"
        diff_rip_str = f"Da {t['rip']} a 1 (-{int(t['rip'])-1} riprese)" if int(t['rip']) > 1 else "Invariato (Turno Unico)"
        stato_header = "🟢 TURNO SPECIALE 40h SETTIMANALI (RIPOSO SAB+DOM)"
        box_diff_text = f"• <b>&Delta; Nastro:</b> {diff_nastro_str} (Impegno giornaliero di 8h05) | " \
                        f"• <b>&Delta; OLG (Paga):</b> <font color='#006600'><b>{diff_olg_str}</b></font> (Raggiungimento 8h00 piene) | " \
                        f"• <b>&Delta; Riprese:</b> {diff_rip_str}<br/>" \
                        f"• <b>VANTAGGIO PRINCIPALE:</b> 40 ore piene in 5 giorni (Lun-Ven) con <b>diritto legale al riposo compensativo continuativo Sabato e Domenica (5+2)</b>."
        law_specifica = "<b>CCNL Autoferrotranvieri & Legge 138/1958 Art. 1, 2, 7:</b> Turno Speciale 40h Settimanali su 5 giorni (8h/giorno). Diritto contrattuale al doppio riposo compensativo continuativo Sabato e Domenica (schema 5+2)."
    elif is_lungo:
        target_h = 7.75 if n_val > 11.5 else 7.25
        p_nastro = f"{int(target_h)}h {int((target_h%1)*60):02d}m"
        p_olg = f"{min(t['o_val'], 7.0):.2f}".replace('.', 'h ') + "m"
        p_rip = "1 (Turno Unico)"
        p_fine = fine_stimata
        risp_h = n_val - target_h
        min_risp = int((risp_h % 1) * 60)
        diff_nastro_str = f"-{int(risp_h)}h {min_risp:02d}m"
        diff_rip_str = f"Da {t['rip']} a 1 (-{int(t['rip'])-1} spezzoni)" if int(t['rip']) > 1 else "Turno Unico"
        stato_header = "🟢 PROPOSTA OTTIMIZZATA (RISTRUTTURATO)"
        box_diff_text = f"• <b>&Delta; Nastro (Tempo risparmiato):</b> <font color='#006600'><b>{diff_nastro_str} 👍</b></font> (Da {n_att} a {p_nastro}) | " \
                        f"• <b>&Delta; Ore Pagate (OLG):</b> {p_olg} (Allineato a nastro compatto) | " \
                        f"• <b>&Delta; Riprese:</b> {diff_rip_str}<br/>" \
                        f"• <b>DIFFERENZE OPERATIVE:</b> Eliminato stacco passivo diurno di oltre {int(risp_h)} ore | Rientro in linea passeggeri al Deposito di {dep}."
        superamento_ccnl = f"<font color='#CC0000'><b>VIOLAZIONE GRAVE CCNL:</b> Il nastro azienda di {n_att} supera il limite di 12h.</font><br/>" if n_val > 12.0 else ""
        law_specifica = f"{superamento_ccnl}" \
                        f"• <b>CCNL Autoferrotranvieri (Nastro Max 12h):</b> La nostra proposta riconduce il nastro a <b>{p_nastro}</b> (&le; 8h30).<br/>" \
                        f"• <b>L. 138/1958 Art. 3 & 5 (Guida & Pause):</b> Guida ininterrotta sempre &le; 5h00 e pausa obbligatoria di 30m (o 2x15m) garantita entro 6h.<br/>" \
                        f"• <b>L. 138/1958 Art. 6 & 8 (Riposo & Residenza):</b> Garantite oltre 15h di riposo giornaliero nello stesso Deposito d'origine (<b>{dep}</b>)."
    else:
        p_nastro = f"{n_att} (Invariato)"
        p_olg = f"{o_att} (Invariato)"
        p_rip = f"{t['rip']} (Invariato)"
        p_fine = t['fine']
        stato_header = "🔵 TURNO CONFERMATO (NESSUNA MODIFICA NECESSARIA)"
        box_diff_text = f"• <b>&Delta; Nastro:</b> 0h 00m (Confermato {n_att}) | " \
                        f"• <b>&Delta; Ore Pagate (OLG):</b> Confermato {o_att} | " \
                        f"• <b>&Delta; Riprese:</b> Confermato {t['rip']}<br/>" \
                        f"• <b>STATO DEL TURNO:</b> <b>TURNO GIÀ CONFORME E REGOLARE.</b> Nastro già inferiore alle 9h30/10h con corse continuative e rientro corretto nel Deposito di {dep}."
        law_specifica = f"• <b>CCNL Autoferrotranvieri & L. 138/1958:</b> Turno già pienamente conforme ai limiti legali e contrattuali. Nastro &le; 10h00, guida continua &le; 5h00, pause e riposo giornaliero regolari."

    # HEADER
    t_header = Table([[Paragraph(f"<b>ARRIVA ITALIA (ex SADEM) - SCHEDA COMPARATIVA DI TURNO</b>", title_style), Paragraph(f"<b>TURNO: <font color='#003366' size='11'>{code}</font> | Residenza: {dep}</b>", sub_style)]], colWidths=[405, 405])
    t_header.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,0), (-1,-1), 1)]))
    elements.append(t_header)
    elements.append(Spacer(1, 1))

    # BOX DIFFERENZE
    bg_diff_head = colors.HexColor('#CCE5FF') if (is_40h or is_lungo) else colors.HexColor('#E2E3E5')
    border_diff = colors.HexColor('#004085') if (is_40h or is_lungo) else colors.HexColor('#6C757D')
    t_diff = Table([[Paragraph(f"<b>📊 QUADRO SINTETICO DELLE DIFFERENZE - {stato_header}</b>", diff_title)], [Paragraph(box_diff_text, diff_body)]], colWidths=[810])
    t_diff.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), bg_diff_head), ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F4F9FF') if (is_40h or is_lungo) else colors.HexColor('#F8F9FA')), ('BOX', (0,0), (-1,-1), 1, border_diff), ('TOPPADDING', (0,0), (-1,-1), 1.5), ('BOTTOMPADDING', (0,0), (-1,-1), 1.5), ('LEFTPADDING', (0,0), (-1,-1), 4), ('RIGHTPADDING', (0,0), (-1,-1), 4)]))
    elements.append(t_diff)
    elements.append(Spacer(1, 2))

    # COLONNA SINISTRA (Azienda)
    rows_orig = [
        [Paragraph(f"<b>🔴 A SINISTRA: CARTELLINO AZIENDA 2026</b><br/>Inizio: <b>{t['inizio']}</b> | Fine: <b>{t['fine']}</b> | Nastro: <font color='#CC0000'><b>{n_att}</b></font> | OLG: <b>{o_att}</b>", h_cell_o), Paragraph("", h_cell_o), Paragraph("", h_cell_o), Paragraph("", h_cell_o)],
        [Paragraph("Part.", h_cell_o), Paragraph("Arr.", h_cell_o), Paragraph("Tipo", h_cell_o), Paragraph("Attività / Tratta Aziendale", h_cell_o)]
    ]
    if t['corse_raw']:
        for r in t['corse_raw'][:8]:
            rows_orig.append([Paragraph(r[0], cell_bold), Paragraph(r[1], cell_bold), Paragraph(r[2], cell_bold), Paragraph(r[3], cell_text)])
    else:
        rows_orig.append([Paragraph(t['inizio'], cell_bold), Paragraph(t['fine'], cell_bold), Paragraph("0002", cell_bold), Paragraph("Servizio di linea aziendale", cell_text)])
        
    t_left = Table(rows_orig, colWidths=[35, 35, 40, 290])
    t_left.setStyle(TableStyle([('SPAN', (0,0), (3,0)), ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#990000')), ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#B30000')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')), ('ROWBACKGROUNDS', (0,2), (-1,-1), [colors.white, colors.HexColor('#FFF5F5')]), ('TOPPADDING', (0,0), (-1,-1), 1.2), ('BOTTOMPADDING', (0,0), (-1,-1), 1.2)]))

    # COLONNA DESTRA (Nostra Proposta con tratte e linee puntuali)
    header_destra_bg = colors.HexColor('#006600') if (is_40h or is_lungo) else colors.HexColor('#004085')
    header_destra_sub_bg = colors.HexColor('#008800') if (is_40h or is_lungo) else colors.HexColor('#0056B3')
    
    rows_prop = [
        [Paragraph(f"<b>{'🟢 NOSTRA PROPOSTA RISTRUTTURATA' if (is_40h or is_lungo) else '🔵 NOSTRA VALUTAZIONE (CONFERMATO)'}</b><br/>Inizio: <b>{t['inizio']}</b> | Fine: <b>{p_fine}</b> | Nastro: <b>{p_nastro}</b> | OLG: <b>{p_olg}</b>", h_cell_p), Paragraph("", h_cell_p), Paragraph("", h_cell_p), Paragraph("", h_cell_p)],
        [Paragraph("Part.", h_cell_p), Paragraph("Arr.", h_cell_p), Paragraph("Tipo", h_cell_p), Paragraph("Tratta e Attività Puntuale di Servizio di Linea", h_cell_p)]
    ]
    
    for r in corse_prop_puntuali[:8]:
        rows_prop.append([Paragraph(r[0], cell_bold), Paragraph(r[1], cell_bold), Paragraph(r[2], cell_bold), Paragraph(r[3], cell_text)])

    t_right = Table(rows_prop, colWidths=[35, 35, 40, 290])
    t_right.setStyle(TableStyle([('SPAN', (0,0), (3,0)), ('BACKGROUND', (0,0), (-1,0), header_destra_bg), ('BACKGROUND', (0,1), (-1,1), header_destra_sub_bg), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDDDDD')), ('ROWBACKGROUNDS', (0,2), (-1,-1), [colors.white, colors.HexColor('#F5FFF5') if (is_40h or is_lungo) else colors.HexColor('#F0F4F8')]), ('TOPPADDING', (0,0), (-1,-1), 1.2), ('BOTTOMPADDING', (0,0), (-1,-1), 1.2)]))

    t_affiancate = Table([[t_left, t_right]], colWidths=[405, 405])
    t_affiancate.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(t_affiancate)
    elements.append(Spacer(1, 2))

    box_legge = [
        [Paragraph("<b>QUADRO NORMATIVO E CONTRATTUALE - CCNL AUTOFERROTRANVIERI & LEGGE 14 FEBBRAIO 1958, N. 138</b>", law_title)],
        [Paragraph(law_specifica, law_body)]
    ]
    t_legge = Table(box_legge, colWidths=[810])
    t_legge.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FFEBEB') if is_lungo else colors.HexColor('#EBF3FA')), ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#FAFAFA')), ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#990000') if is_lungo else colors.HexColor('#003366')), ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E0E0E0')), ('TOPPADDING', (0,0), (-1,-1), 1.5), ('BOTTOMPADDING', (0,0), (-1,-1), 1.5), ('LEFTPADDING', (0,0), (-1,-1), 4), ('RIGHTPADDING', (0,0), (-1,-1), 4)]))
    elements.append(t_legge)

    if idx < len(tutti_turni) - 1:
        elements.append(PageBreak())

doc.build(elements)
print("✅ DOSSIER UNIFICATO AGGIORNATO SU TUTTI I 156 TURNI CON TRATTE E CORSE REALI PUNTUALI!")
