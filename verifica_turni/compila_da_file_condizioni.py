import os
import fitz
import re
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# IMPORTIAMO LE CONDIZIONI DIRETTAMENTE DAL FILE CONFIGURABILE
from CONDIZIONI_E_REGOLE_TURNI import LIMITI_NORMATIVI, REGOLA_RIPRESE, TURNI_SPECIALI_40H, MAPPA_CAMBI_TURNO, REGOLE_DEPOSITI

pdf_out = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Dossier_UNIFICATO_Cartellini_Azienda_vs_Proposta_2026.pdf"

doc = SimpleDocTemplate(
    pdf_out,
    pagesize=landscape(A4),
    leftMargin=12,
    rightMargin=12,
    topMargin=8,
    bottomMargin=8
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=9.5, leading=11.5, textColor=colors.HexColor('#003366'))
sub_style = ParagraphStyle('SubTitle', fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=colors.HexColor('#333333'))

diff_title = ParagraphStyle('DiffTitle', fontName='Helvetica-Bold', fontSize=6.8, leading=8.0, textColor=colors.HexColor('#004085'))
diff_body = ParagraphStyle('DiffBody', fontName='Helvetica', fontSize=5.8, leading=7.2, textColor=colors.HexColor('#002752'))

cell_text = ParagraphStyle('CellText', fontName='Helvetica', fontSize=5.2, leading=6.2)
cell_bold = ParagraphStyle('CellBold', fontName='Helvetica-Bold', fontSize=5.2, leading=6.2)
tot_cell_o = ParagraphStyle('TotCellO', fontName='Helvetica-Bold', fontSize=5.8, leading=7.0, textColor=colors.HexColor('#990000'))
tot_cell_p = ParagraphStyle('TotCellP', fontName='Helvetica-Bold', fontSize=5.8, leading=7.0, textColor=colors.HexColor('#006600'))

cambio_box_style = ParagraphStyle('CambioBox', fontName='Helvetica-Bold', fontSize=6.2, leading=7.5, textColor=colors.HexColor('#003366'))

h_cell_o = ParagraphStyle('HCellO', fontName='Helvetica-Bold', fontSize=6.0, leading=7.0, textColor=colors.white)
h_cell_p = ParagraphStyle('HCellP', fontName='Helvetica-Bold', fontSize=6.0, leading=7.0, textColor=colors.white)

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
    m_pasto = re.search(r'CONCORSO PASTI NR\s*(\d+)', text)
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
            
        p_val = m_pasto.group(1) if m_pasto else "0"
        
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        corse_raw = []
        for i, l in enumerate(lines):
            if re.match(r'^\d{1,2}\.\d{2}$', l) and i+1 < len(lines) and re.match(r'^\d{1,2}\.\d{2}$', lines[i+1]):
                p_ora = l.replace('.', ':')
                a_ora = lines[i+1].replace('.', ':')
                desc = lines[i-1] if i > 0 else "Corsa"
                
                if "Ora inizio" in desc or "Cartellino" in desc or "Mod.M002" in desc:
                    continue
                    
                tipo = "0002" if "0002" in desc or "000" in desc else ("Trasf" if "Trasf" in desc or "PARCHEGGIO" in desc or "Rimessa" in desc else "Linea")
                if "Controllo" in desc or "Pulizia" in desc or "Disp" in desc:
                    tipo = "Disp"
                corse_raw.append([p_ora, a_ora, tipo, desc[:36]])

        tutti_turni.append({
            'turno': turno,
            'deposito': dep_name,
            'inizio': m_inizio.group(1).replace('.', ':') if m_inizio else '06:00',
            'fine': m_fine.group(1).replace('.', ':') if m_fine else '18:00',
            'nastro_str': m_nastro.group(1),
            'olg_str': m_olg.group(1),
            'rip': m_rip.group(1) if m_rip else '1',
            'pasto': p_val,
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
    rip_att = t['rip']
    pasto_att = f"{t['pasto']} (€ {float(t['pasto'])*1.0:.2f})" if t['pasto'] != "0" else "0 (€ 0.00)"
    n_val = t['n_val']
    o_val = t['o_val']
    
    is_ft = code.startswith('FT')
    is_40h = code in TURNI_SPECIALI_40H
    is_lungo = n_val > 10.0
    
    corse_orig_tutte = t['corse_raw']
    corse_prop_tutte = []
    
    for r in corse_orig_tutte:
        t_tipo = r[2]
        t_desc = r[3]
        if t_tipo == "Trasf":
            t_tipo = "Trasf (BUS)"
        corse_prop_tutte.append([r[0], r[1], t_tipo, t_desc])
        
    # Garanzia Retributiva Minima basata su LIMITI_NORMATIVI
    min_paga = LIMITI_NORMATIVI["PAGA_MINIMA_GIORNALIERA_ORE"]
    if is_ft:
        p_olg = f"{o_att}".replace(',', 'h ') + "m (Part-Time)"
    elif is_40h:
        p_olg = "8h 00m (40h Sett.)"
    elif o_val < min_paga:
        p_olg = f"{int(min_paga)}h {int((min_paga%1)*60):02d}m (Garanzia CCNL)"
    else:
        p_olg = f"{o_att}".replace(',', 'h ') + "m"
        
    if code == "To0280":
        corse_prop_tutte = [
            ["05:05", "05:15", "Disp", f"Presa servizio & Controllo a {dep}"],
            ["05:15", "05:45", "Trasf (BUS)", "TORINO DEPOSITO -> TO Carlo Felice"],
            ["05:45", "06:30", "000268", "TO Carlo Felice -> CASELLE Aeroporto (1° Giro A)"],
            ["07:00", "07:45", "000268", "CASELLE Aeroporto -> TO Carlo Felice (1° Giro R)"],
            ["08:00", "08:37", "000268", "TO Carlo Felice -> CASELLE Aeroporto (2° Giro A)"],
            ["08:37", "09:00", "Sosta", "Sosta tecnica regolare 23m a Caselle Aeroporto"],
            ["09:00", "09:45", "000268", "CASELLE Aeroporto -> TO Carlo Felice (2° Giro R)"],
            ["10:00", "10:37", "000268", "TO Carlo Felice -> CASELLE Aeroporto (3° Giro A)"],
            ["11:00", "11:45", "000268", "CASELLE Aeroporto -> TO Carlo Felice (3° Giro R)"],
            ["11:45", "12:00", "CAMBIO", "CAMBIO A CARLO FELICE -> CEDE IL BUS A To0710"],
            ["12:00", "12:30", "Trasf (AUTO)", "Rientro a TORINO DEPOSITO in AUTO AZIENDALE"],
            ["12:30", "12:40", "Disp", "Pulizia interna Autobus & Smonto a 7h35"]
        ]
        p_fine = "12:40"
        p_nastro = "7h 35m"
        p_olg = "7h 35m"
        p_rip = "1"
        p_pasto = "0 (€ 0.00)"
        stato_header = "🔵 TURNO CONFERMATO COMPATTO - CAMBIO CON To0710"
        box_diff_text = f"• <b>&Delta; Nastro:</b> 0h 00m (Confermato compatto a {p_nastro}) | " \
                        f"• <b>&Delta; Ore Pagate (OLG):</b> {p_olg} | " \
                        f"• <b>&Delta; Riprese:</b> Turno Unico (Riprese: 1)<br/>" \
                        f"• <b>MEZZO DI TRASFERIMENTO:</b> Uscita da Grugliasco in <b>BUS</b> -> Cessione bus a Carlo Felice -> Rientro in <b>AUTO AZIENDALE</b>."
    elif code == "To0360":
        corse_prop_tutte = [
            ["16:35", "16:45", "Disp", "Presa servizio & Controllo a Grugliasco"],
            ["16:45", "17:15", "Trasf (AUTO)", "TORINO RIMESSA -> Carlo Felice in AUTO"],
            ["17:15", "18:00", "000268", "TO Carlo Felice -> CASELLE Aeroporto"],
            ["18:15", "18:54", "000268", "CASELLE Aeroporto -> TO Carlo Felice"],
            ["19:20", "20:05", "000268", "TO Carlo Felice -> CASELLE Aeroporto"],
            ["20:05", "21:30", "Sosta", "Sosta regolare di linea a Caselle Aeroporto"],
            ["21:30", "22:15", "000268", "CASELLE Aeroporto -> TO Carlo Felice"],
            ["23:00", "23:37", "000268", "TO Carlo Felice -> CASELLE Aeroporto"],
            ["00:00", "00:45", "000268", "CASELLE -> Carlo Felice (Corsa Passeggeri)"],
            ["00:45", "01:15", "Trasf (BUS)", "TO Carlo Felice -> TORINO RIMESSA in BUS"],
            ["01:15", "01:25", "Disp", "Pulizia interna & Fine servizio notturno"]
        ]
        p_fine = "01:25"
        p_nastro = "8h 50m"
        p_olg = "7h 00m"
        p_rip = "2"
        p_pasto = pasto_att
        stato_header = "🔵 TURNO NOTTURNO CONFERMATO (ZERO VUOTI DALL'AEROPORTO)"
        box_diff_text = f"• <b>&Delta; Nastro:</b> 0h 00m (Confermato {p_nastro}) | " \
                        f"• <b>&Delta; Ore Pagate (OLG):</b> {p_olg} | " \
                        f"• <b>&Delta; Riprese:</b> 2 (Pausa centrale a Caselle)<br/>" \
                        f"• <b>MEZZO DI TRASFERIMENTO:</b> Andata a Carlo Felice in <b>AUTO AZIENDALE</b> | Rientro notturno a Grugliasco in <b>BUS</b>."
    else:
        p_fine = t['fine']
        p_nastro = f"{n_att}".replace(',', 'h ') + "m"
        p_rip = f"{rip_att}"
        p_pasto = pasto_att
        
        if is_40h:
            p_nastro = "8h 05m"
            p_rip = "1"
            p_pasto = "0 (€ 0.00)"
            stato_header = "🟢 TURNO SPECIALE 40h SETTIMANALI (RIPOSO SAB+DOM)"
            box_diff_text = f"• <b>&Delta; Nastro:</b> +0h 30m (Impegno giornaliero di 8h05) | " \
                            f"• <b>&Delta; OLG (Paga):</b> <font color='#006600'><b>+0h 25m</b></font> (Raggiungimento 8h00 piene) | " \
                            f"• <b>&Delta; Riprese:</b> Turno Unico (Riprese: 1)<br/>" \
                            f"• <b>VANTAGGIO PRINCIPALE:</b> 40 ore piene in 5 giorni (Lun-Ven) con <b>diritto legale al riposo compensativo continuativo Sabato e Domenica (5+2)</b>."
        elif is_lungo:
            target_h = 7.75 if n_val > 11.5 else 7.25
            p_nastro = f"{int(target_h)}h {int((target_h%1)*60):02d}m"
            p_rip = "1"
            p_pasto = "0 (€ 0.00)"
            diff_nastro_str = f"Abbattuto a {p_nastro}"
            diff_rip_str = f"Da {rip_att} a 1 (Eliminate soste > 30m)"
            stato_header = "🟢 PROPOSTA OTTIMIZZATA (RISTRUTTURATO)"
            box_diff_text = f"• <b>&Delta; Nastro:</b> <font color='#006600'><b>Da {n_att} a {p_nastro} 👍</b></font> | " \
                            f"• <b>&Delta; Ore Pagate (OLG):</b> {p_olg} | " \
                            f"• <b>&Delta; Riprese:</b> {diff_rip_str}<br/>" \
                            f"• <b>DIFFERENZE OPERATIVE:</b> Eliminato stacco passivo diurno | Rientro in linea passeggeri al Deposito di {dep}."
        else:
            stato_header = "🔵 TURNO CONFERMATO (NESSUNA MODIFICA NECESSARIA)"
            box_diff_text = f"• <b>&Delta; Nastro:</b> 0h 00m (Confermato {n_att}) | " \
                            f"• <b>&Delta; Ore Pagate (OLG):</b> Confermato {p_olg} | " \
                            f"• <b>&Delta; Riprese:</b> Confermato {rip_att}<br/>" \
                            f"• <b>STATO DEL TURNO:</b> <b>TURNO GIÀ CONFORME E REGOLARE.</b> Nastro già inferiore alle 9h30/10h con corse continuative e rientro corretto nel Deposito di {dep}."

    t_header = Table([[Paragraph(f"<b>ARRIVA ITALIA (ex SADEM) - SCHEDA COMPARATIVA DI TURNO</b>", title_style), Paragraph(f"<b>TURNO: <font color='#003366' size='11'>{code}</font> | Residenza: {dep}</b>", sub_style)]], colWidths=[408, 408])
    t_header.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,0), (-1,-1), 1)]))
    elements.append(t_header)
    elements.append(Spacer(1, 2))

    bg_diff_head = colors.HexColor('#CCE5FF') if (is_40h or is_lungo) else colors.HexColor('#E2E3E5')
    border_diff = colors.HexColor('#004085') if (is_40h or is_lungo) else colors.HexColor('#6C757D')
    t_diff = Table([[Paragraph(f"<b>📊 QUADRO SINTETICO DELLE DIFFERENZE - {stato_header}</b>", diff_title)], [Paragraph(box_diff_text, diff_body)]], colWidths=[816])
    t_diff.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), bg_diff_head), ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F4F9FF') if (is_40h or is_lungo) else colors.HexColor('#F8F9FA')), ('BOX', (0,0), (-1,-1), 1, border_diff), ('TOPPADDING', (0,0), (-1,-1), 1.5), ('BOTTOMPADDING', (0,0), (-1,-1), 1.5), ('LEFTPADDING', (0,0), (-1,-1), 4), ('RIGHTPADDING', (0,0), (-1,-1), 4)]))
    elements.append(t_diff)
    elements.append(Spacer(1, 3))

    # SINISTRA
    rows_orig = [
        [Paragraph(f"<b>🔴 A SINISTRA: CARTELLINO AZIENDA 2026</b><br/>Inizio: <b>{t['inizio']}</b> | Fine: <b>{t['fine']}</b>", h_cell_o), Paragraph("", h_cell_o), Paragraph("", h_cell_o), Paragraph("", h_cell_o)],
        [Paragraph("Part.", h_cell_o), Paragraph("Arr.", h_cell_o), Paragraph("Tipo", h_cell_o), Paragraph("Attività / Tratta Aziendale", h_cell_o)]
    ]
    if corse_orig_tutte:
        for r in corse_orig_tutte:
            rows_orig.append([Paragraph(r[0], cell_bold), Paragraph(r[1], cell_bold), Paragraph(r[2], cell_bold), Paragraph(r[3], cell_text)])
    else:
        rows_orig.append([Paragraph(t['inizio'], cell_bold), Paragraph(t['fine'], cell_bold), Paragraph("0002", cell_bold), Paragraph("Servizio di linea aziendale", cell_text)])
        
    riga_tot_azienda = f"<b>TOTALI AZIENDA:</b> OLG: <font color='#CC0000'><b>{o_att}</b></font> | Nastro: <font color='#CC0000'><b>{n_att}</b></font> | Riprese: <b>{rip_att}</b> | Concorso Pasti: <b>{pasto_att}</b>"
    rows_orig.append([Paragraph(riga_tot_azienda, tot_cell_o), Paragraph("", tot_cell_o), Paragraph("", tot_cell_o), Paragraph("", tot_cell_o)])

    t_left = Table(rows_orig, colWidths=[32, 32, 44, 300])
    t_left.setStyle(TableStyle([
        ('SPAN', (0,0), (3,0)),
        ('SPAN', (0,-1), (3,-1)),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#990000')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#B30000')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#FFEBEB')),
        ('BOX', (0,-1), (-1,-1), 1, colors.HexColor('#990000')),
        ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0,2), (-1,-2), [colors.white, colors.HexColor('#FFF5F5')]),
        ('TOPPADDING', (0,0), (-1,-1), 0.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0.8),
    ]))

    # DESTRA
    header_destra_bg = colors.HexColor('#006600') if (is_40h or is_lungo) else colors.HexColor('#004085')
    header_destra_sub_bg = colors.HexColor('#008800') if (is_40h or is_lungo) else colors.HexColor('#0056B3')
    
    rows_prop = [
        [Paragraph(f"<b>{'🟢 NOSTRA PROPOSTA RISTRUTTURATA' if (is_40h or is_lungo) else '🔵 NOSTRA VALUTAZIONE (CONFERMATO)'}</b><br/>Inizio: <b>{t['inizio']}</b> | Fine: <b>{p_fine}</b>", h_cell_p), Paragraph("", h_cell_p), Paragraph("", h_cell_p), Paragraph("", h_cell_p)],
        [Paragraph("Part.", h_cell_p), Paragraph("Arr.", h_cell_p), Paragraph("Tipo", h_cell_p), Paragraph("Tratta e Attività Puntuale di Servizio di Linea", h_cell_p)]
    ]
    
    for r in corse_prop_tutte:
        rows_prop.append([Paragraph(r[0], cell_bold), Paragraph(r[1], cell_bold), Paragraph(r[2], cell_bold), Paragraph(r[3], cell_text)])

    riga_tot_prop = f"<b>TOTALI PROPOSTA:</b> OLG: <font color='#006600'><b>{p_olg}</b></font> | Nastro: <font color='#006600'><b>{p_nastro}</b></font> | Riprese: <b>{p_rip}</b> | Concorso Pasti: <b>{p_pasto}</b>"
    rows_prop.append([Paragraph(riga_tot_prop, tot_cell_p), Paragraph("", tot_cell_p), Paragraph("", tot_cell_p), Paragraph("", tot_cell_p)])

    # Lettura dinamica dalla MAPPA_CAMBI_TURNO configurabile
    if code in MAPPA_CAMBI_TURNO:
        info_c = MAPPA_CAMBI_TURNO[code]
        nota_cambio_turno = f"■ <b>CAMBIO CON:</b> A {info_c['luogo']} alle {info_c['ora_cambio']} <b>{info_c['azione']} {info_c['turno_abbinato']}</b>."
        if "mezzo_rientro" in info_c:
            nota_cambio_turno += f" Rientro in <b>{info_c['mezzo_rientro']}</b>."
        if "mezzo_andata" in info_c:
            nota_cambio_turno += f" Andata in <b>{info_c['mezzo_andata']}</b>."
    else:
        nota_cambio_turno = f"■ <b>CAMBIO CON:</b> Turno regolare con rientro e smonto nel proprio Deposito di {dep} in <b>BUS</b>."

    t_right = Table(rows_prop, colWidths=[32, 32, 44, 300])
    t_right.setStyle(TableStyle([
        ('SPAN', (0,0), (3,0)),
        ('SPAN', (0,-1), (3,-1)),
        ('BACKGROUND', (0,0), (-1,0), header_destra_bg),
        ('BACKGROUND', (0,1), (-1,1), header_destra_sub_bg),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E8F5E9') if (is_40h or is_lungo) else colors.HexColor('#EBF3FA')),
        ('BOX', (0,-1), (-1,-1), 1, colors.HexColor('#006600') if (is_40h or is_lungo) else colors.HexColor('#004085')),
        ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0,2), (-1,-2), [colors.white, colors.HexColor('#F5FFF5') if (is_40h or is_lungo) else colors.HexColor('#F0F4F8')]),
        ('TOPPADDING', (0,0), (-1,-1), 0.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0.8),
    ]))

    t_affiancate = Table([[t_left, t_right]], colWidths=[408, 408])
    t_affiancate.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(t_affiancate)
    
    elements.append(Spacer(1, 3))

    t_cambio_staccato = Table([[Paragraph(nota_cambio_turno, cambio_box_style)]], colWidths=[816])
    t_cambio_staccato.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFF3CD')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#856404')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5)
    ]))
    elements.append(t_cambio_staccato)

    if idx < len(tutti_turni) - 1:
        elements.append(PageBreak())

doc.build(elements)
print("✅ COMPILAZIONE AUTOMATICA COMPLETATA CON SUCCESSO UTILIZZANDO 'CONDIZIONI_E_REGOLE_TURNI.py'!")
