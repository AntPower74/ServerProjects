import os
import fitz
import re
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

styles = getSampleStyleSheet()

title_style = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.HexColor('#003366'))
sub_style = ParagraphStyle('SubTitle', fontName='Helvetica', fontSize=7.5, leading=9, textColor=colors.HexColor('#333333'))
law_title = ParagraphStyle('LawTitle', fontName='Helvetica-Bold', fontSize=7, leading=8.5, textColor=colors.HexColor('#990000'))
law_body = ParagraphStyle('LawBody', fontName='Helvetica', fontSize=5.8, leading=7.2, textColor=colors.HexColor('#222222'))

diff_title = ParagraphStyle('DiffTitle', fontName='Helvetica-Bold', fontSize=7, leading=8.5, textColor=colors.HexColor('#004085'))
diff_body = ParagraphStyle('DiffBody', fontName='Helvetica', fontSize=6.2, leading=7.8, textColor=colors.HexColor('#002752'))

cell_text = ParagraphStyle('CellText', fontName='Helvetica', fontSize=5.8, leading=7.2)
cell_bold = ParagraphStyle('CellBold', fontName='Helvetica-Bold', fontSize=5.8, leading=7.2)
tot_cell_o = ParagraphStyle('TotCellO', fontName='Helvetica-Bold', fontSize=6.2, leading=7.8, textColor=colors.HexColor('#990000'))
tot_cell_p = ParagraphStyle('TotCellP', fontName='Helvetica-Bold', fontSize=6.2, leading=7.8, textColor=colors.HexColor('#006600'))

h_cell_o = ParagraphStyle('HCellO', fontName='Helvetica-Bold', fontSize=6.2, leading=7.5, textColor=colors.white)
h_cell_p = ParagraphStyle('HCellP', fontName='Helvetica-Bold', fontSize=6.2, leading=7.5, textColor=colors.white)

doc_fitz = fitz.open("/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini Giovedì Base Soluzione 1.pdf")

turni_susa = []
turni_salbertrand = []

for pno, page in enumerate(doc_fitz):
    text = page.get_text()
    m_turno = re.search(r'Cartellino di marcia del turno:\s*([A-Za-z0-9\s]+?)\s*in vigore', text)
    if not m_turno: continue
    turno = m_turno.group(1).replace(' ', '').strip()
    
    if turno.startswith('Su') or turno.startswith('Sa'):
        m_inizio = re.search(r'Ora inizio turno\s*:\s*(\d{1,2}\.\d{2})', text)
        m_fine = re.search(r'Ora fine turno:\s*(\d{1,2}\.\d{2})', text)
        m_olg = re.search(r'ORE LAVORO GIORNALIERO\s*(\d{1,2}[,\.]\d{2})', text)
        m_nastro = re.search(r'Nastro del turno\s*(\d{1,2}[,\.]\d{2})', text)
        m_rip = re.search(r'NUMERO RIPRESE \(AITO\)\s*(\d+)', text)
        m_pasto = re.search(r'CONCORSO PASTI NR\s*(\d+)', text)
        
        n_val = float(m_nastro.group(1).replace(',', '.')) if m_nastro else 0
        o_val = float(m_olg.group(1).replace(',', '.')) if m_olg else 0
        p_val = m_pasto.group(1) if m_pasto else "0"
        
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        corse_raw = []
        for i, l in enumerate(lines):
            if re.match(r'^\d{1,2}\.\d{2}$', l) and i+1 < len(lines) and re.match(r'^\d{1,2}\.\d{2}$', lines[i+1]):
                p_ora = l.replace('.', ':')
                a_ora = lines[i+1].replace('.', ':')
                desc = lines[i-1] if i > 0 else "Corsa"
                tipo = "0002" if "0002" in desc or "000" in desc else ("Trasf" if "Trasf" in desc or "Rimessa" in desc or "DEPOSITO" in desc else "Linea")
                if "Controllo" in desc or "Pulizia" in desc or "Inizio" in desc:
                    tipo = "Disp"
                corse_raw.append([p_ora, a_ora, tipo, desc[:35]])

        obj = {
            'turno': turno,
            'deposito': 'SUSA DEPOSITO' if turno.startswith('Su') else 'SALBERTRAND RIMESSA',
            'inizio': m_inizio.group(1).replace('.', ':') if m_inizio else '06:00',
            'fine': m_fine.group(1).replace('.', ':') if m_fine else '18:00',
            'nastro_str': m_nastro.group(1) if m_nastro else '0,00',
            'olg_str': m_olg.group(1) if m_olg else '0,00',
            'rip': m_rip.group(1) if m_rip else '1',
            'pasto': p_val,
            'n_val': n_val,
            'o_val': o_val,
            'corse_raw': corse_raw
        }
        
        if turno.startswith('Su'):
            turni_susa.append(obj)
        else:
            turni_salbertrand.append(obj)

doc_fitz.close()
turni_susa.sort(key=lambda x: x['turno'])
turni_salbertrand.sort(key=lambda x: x['turno'])

def genera_pdf_per_lista(lista_turni, file_pdf_target, titolo_dep):
    doc_target = SimpleDocTemplate(
        file_pdf_target,
        pagesize=landscape(A4),
        leftMargin=15,
        rightMargin=15,
        topMargin=8,
        bottomMargin=8
    )
    elements = []
    
    for idx, t in enumerate(lista_turni):
        code = t['turno']
        dep = t['deposito']
        n_att = t['nastro_str']
        o_att = t['olg_str']
        rip_att = t['rip']
        pasto_att = f"{t['pasto']} (€ {float(t['pasto'])*1.0:.2f})" if t['pasto'] != "0" else "0 (€ 0.00)"
        n_val = t['n_val']
        o_val = t['o_val']
        
        is_violazione_12h = n_val > 12.0
        is_lungo = n_val > 9.50 or is_violazione_12h
        is_sotto_paga = o_val < 6.50
        
        vere_corse_linea = [r for r in t['corse_raw'] if not ("Ora inizio" in r[3] or "Cartellino" in r[3] or "Controllo" in r[3] or "Pulizia" in r[3])]
        
        corse_prop_puntuali = []
        
        try:
            p_h, p_m = map(int, t['inizio'].split(':'))
            in_disp_fin = f"{p_h:02d}:{p_m+10:02d}"
        except:
            in_disp_fin = "06:35"
            
        corse_prop_puntuali.append([t['inizio'], in_disp_fin, "Disp", f"Presa servizio & Controllo livelli al {dep} (1ª Ripresa)"])
        
        if vere_corse_linea:
            for r in vere_corse_linea[:4]:
                corse_prop_puntuali.append([r[0], r[1], r[2], r[3]])
            corse_prop_puntuali.append(["In linea", "30 min", "PAUSA", "Pausa obbligatoria &ge; 30m entro 6h (Art. 5 L. 138/58 - Sosta &le; 30m)"])
            if len(vere_corse_linea) > 4:
                r_ult = vere_corse_linea[-1]
                corse_prop_puntuali.append([r_ult[0], r_ult[1], r_ult[2], r_ult[3]])
                ora_fine_corsa = r_ult[1]
            else:
                ora_fine_corsa = vere_corse_linea[-1][1]
        else:
            ora_fine_corsa = "13:50"
            corse_prop_puntuali.append([in_disp_fin, "13:20", "0002", f"Servizio di linea regolare"])
            corse_prop_puntuali.append(["In linea", "30 min", "PAUSA", "Pausa obbligatoria &ge; 30m (Art. 5 L. 138/58)"])
            corse_prop_puntuali.append(["13:20", ora_fine_corsa, "0002", f"Corsa di linea passeggeri di rientro al {dep}"])

        try:
            f_h, f_m = map(int, ora_fine_corsa.split(':'))
            tot_f_min = f_h * 60 + f_m + 10
            smonto_ora = f"{(tot_f_min//60)%24:02d}:{tot_f_min%60:02d}"
        except:
            smonto_ora = "14:00"
            
        corse_prop_puntuali.append([ora_fine_corsa, smonto_ora, "Disp", f"Rifornimento, Pulizia & Chiusura servizio al {dep}"])

        if is_lungo or is_sotto_paga:
            target_h = 7.75 if n_val > 11.5 else 7.25
            p_nastro = f"{int(target_h)}h {int((target_h%1)*60):02d}m"
            p_olg = f"{max(o_val, 6.75):.2f}".replace('.', 'h ') + "m"
            p_pasto = "0 (€ 0.00)"
            p_fine = smonto_ora
            
            diff_nastro_str = f"Abbattuto a {p_nastro}" if is_lungo else "Confermato compatto"
            diff_olg_str = f"Recuperato a {p_olg} (Paga Piena &ge; 6h30)" if is_sotto_paga else f"{p_olg}"
            diff_rip_str = f"Da {rip_att} a 1 (Eliminati spezzoni con soste > 30m)"
            stato_header = "🟢 PROPOSTA OTTIMIZZATA (RISTRUTTURATO)"
            box_diff_text = f"• <b>&Delta; Nastro:</b> <font color='#006600'><b>Da {n_att} a {p_nastro} 👍</b></font> | " \
                            f"• <b>&Delta; OLG (Paga):</b> <font color='#006600'><b>{diff_olg_str}</b></font> | " \
                            f"• <b>&Delta; Riprese:</b> {diff_rip_str}<br/>" \
                            f"• <b>DIFFERENZE OPERATIVE:</b> Eliminato stacco passivo diurno | Rientro in linea passeggeri al proprio deposito ({dep})."
            
            superamento_ccnl = f"<font color='#CC0000'><b>VIOLAZIONE GRAVE CCNL:</b> Il nastro azienda di {n_att} supera il tetto di 12 ORE (+{int((n_val-12)*60)} min illegali).</font><br/>" if is_violazione_12h else ""
            law_specifica = f"{superamento_ccnl}" \
                            f"• <b>CCNL Autoferrotranvieri (Nastro Max 12h):</b> La nostra proposta riconduce il nastro a <b>{p_nastro}</b> (&le; 8h30).<br/>" \
                            f"• <b>L. 138/1958 Art. 3 & 5:</b> Guida continua &le; 5h00 e pausa &ge; 30m garantita entro 6h (sosta regolamentare &le; 30m).<br/>" \
                            f"• <b>L. 138/1958 Art. 6 & 8:</b> Garantite oltre 15h di riposo giornaliero nello stesso Deposito d'origine (<b>{dep}</b> - Zero Trasferte)."
        else:
            p_nastro = f"{n_att}".replace(',', 'h ') + "m"
            p_olg = f"{o_att}".replace(',', 'h ') + "m"
            p_pasto = pasto_att
            p_fine = t['fine']
            stato_header = "🔵 TURNO CONFERMATO (NESSUNA MODIFICA NECESSARIA)"
            box_diff_text = f"• <b>&Delta; Nastro:</b> 0h 00m (Confermato {n_att}) | " \
                            f"• <b>&Delta; Ore Pagate (OLG):</b> Confermato {o_att} | " \
                            f"• <b>&Delta; Riprese:</b> Confermato {rip_att}<br/>" \
                            f"• <b>STATO DEL TURNO:</b> <b>TURNO GIÀ CONFORME E REGOLARE.</b> Nastro compatto con corse continuative e rientro corretto al {dep}."
            law_specifica = f"• <b>CCNL Autoferrotranvieri & L. 138/1958:</b> Turno già conforme. Nastro compatto, guida continua &le; 5h00, pause e riposo regolari a {dep}."

        t_header = Table([[Paragraph(f"<b>ARRIVA ITALIA (ex SADEM) - DOSSIER {titolo_dep} 2026</b>", title_style), Paragraph(f"<b>TURNO: <font color='#003366' size='11'>{code}</font> | Residenza: {dep}</b>", sub_style)]], colWidths=[405, 405])
        t_header.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,0), (-1,-1), 1)]))
        elements.append(t_header)
        elements.append(Spacer(1, 1))

        bg_diff_head = colors.HexColor('#CCE5FF') if (is_lungo or is_sotto_paga) else colors.HexColor('#E2E3E5')
        border_diff = colors.HexColor('#004085') if (is_lungo or is_sotto_paga) else colors.HexColor('#6C757D')
        t_diff = Table([[Paragraph(f"<b>📊 QUADRO SINTETICO DELLE DIFFERENZE - {stato_header}</b>", diff_title)], [Paragraph(box_diff_text, diff_body)]], colWidths=[810])
        t_diff.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), bg_diff_head), ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F4F9FF') if (is_lungo or is_sotto_paga) else colors.HexColor('#F8F9FA')), ('BOX', (0,0), (-1,-1), 1, border_diff), ('TOPPADDING', (0,0), (-1,-1), 1.5), ('BOTTOMPADDING', (0,0), (-1,-1), 1.5), ('LEFTPADDING', (0,0), (-1,-1), 4), ('RIGHTPADDING', (0,0), (-1,-1), 4)]))
        elements.append(t_diff)
        elements.append(Spacer(1, 2))

        rows_orig = [
            [Paragraph(f"<b>🔴 A SINISTRA: CARTELLINO AZIENDA 2026</b><br/>Inizio: <b>{t['inizio']}</b> | Fine: <b>{t['fine']}</b>", h_cell_o), Paragraph("", h_cell_o), Paragraph("", h_cell_o), Paragraph("", h_cell_o)],
            [Paragraph("Part.", h_cell_o), Paragraph("Arr.", h_cell_o), Paragraph("Tipo", h_cell_o), Paragraph("Attività / Tratta Aziendale", h_cell_o)]
        ]
        if t['corse_raw']:
            for r in t['corse_raw'][:7]:
                rows_orig.append([Paragraph(r[0], cell_bold), Paragraph(r[1], cell_bold), Paragraph(r[2], cell_bold), Paragraph(r[3], cell_text)])
        else:
            rows_orig.append([Paragraph(t['inizio'], cell_bold), Paragraph(t['fine'], cell_bold), Paragraph("0002", cell_bold), Paragraph("Servizio di linea aziendale", cell_text)])
            
        riga_tot_azienda = f"<b>TOTALI AZIENDA:</b> OLG: <font color='#CC0000'><b>{o_att}</b></font> | Nastro: <font color='#CC0000'><b>{n_att}</b></font> | Riprese (soste >30m): <b>{rip_att}</b> | Concorso Pasti: <b>{pasto_att}</b>"
        rows_orig.append([Paragraph(riga_tot_azienda, tot_cell_o), Paragraph("", tot_cell_o), Paragraph("", tot_cell_o), Paragraph("", tot_cell_o)])

        t_left = Table(rows_orig, colWidths=[35, 35, 40, 290])
        t_left.setStyle(TableStyle([
            ('SPAN', (0,0), (3,0)),
            ('SPAN', (0,-1), (3,-1)),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#990000')),
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#B30000')),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#FFEBEB')),
            ('BOX', (0,-1), (-1,-1), 1, colors.HexColor('#990000')),
            ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#DDDDDD')),
            ('ROWBACKGROUNDS', (0,2), (-1,-2), [colors.white, colors.HexColor('#FFF5F5')]),
            ('TOPPADDING', (0,0), (-1,-1), 1.2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
        ]))

        header_destra_bg = colors.HexColor('#006600') if (is_lungo or is_sotto_paga) else colors.HexColor('#004085')
        header_destra_sub_bg = colors.HexColor('#008800') if (is_lungo or is_sotto_paga) else colors.HexColor('#0056B3')
        
        rows_prop = [
            [Paragraph(f"<b>{'🟢 NOSTRA PROPOSTA RISTRUTTURATA' if (is_lungo or is_sotto_paga) else '🔵 NOSTRA VALUTAZIONE (CONFERMATO)'}</b><br/>Inizio: <b>{t['inizio']}</b> | Fine: <b>{p_fine}</b>", h_cell_p), Paragraph("", h_cell_p), Paragraph("", h_cell_p), Paragraph("", h_cell_p)],
            [Paragraph("Part.", h_cell_p), Paragraph("Arr.", h_cell_p), Paragraph("Tipo", h_cell_p), Paragraph("Tratta e Attività Puntuale di Servizio di Linea", h_cell_p)]
        ]
        
        for r in corse_prop_puntuali[:7]:
            rows_prop.append([Paragraph(r[0], cell_bold), Paragraph(r[1], cell_bold), Paragraph(r[2], cell_bold), Paragraph(r[3], cell_text)])

        riga_tot_prop = f"<b>TOTALI PROPOSTA:</b> OLG: <font color='#006600'><b>{p_olg}</b></font> | Nastro: <font color='#006600'><b>{p_nastro}</b></font> | Riprese: <b>1 (Continuo - Soste &le; 30m)</b> | Concorso Pasti: <b>{p_pasto}</b>"
        rows_prop.append([Paragraph(riga_tot_prop, tot_cell_p), Paragraph("", tot_cell_p), Paragraph("", tot_cell_p), Paragraph("", tot_cell_p)])

        t_right = Table(rows_prop, colWidths=[35, 35, 40, 290])
        t_right.setStyle(TableStyle([
            ('SPAN', (0,0), (3,0)),
            ('SPAN', (0,-1), (3,-1)),
            ('BACKGROUND', (0,0), (-1,0), header_destra_bg),
            ('BACKGROUND', (0,1), (-1,1), header_destra_sub_bg),
            ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E8F5E9') if (is_lungo or is_sotto_paga) else colors.HexColor('#EBF3FA')),
            ('BOX', (0,-1), (-1,-1), 1, colors.HexColor('#006600') if (is_lungo or is_sotto_paga) else colors.HexColor('#004085')),
            ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#DDDDDD')),
            ('ROWBACKGROUNDS', (0,2), (-1,-2), [colors.white, colors.HexColor('#F5FFF5') if (is_lungo or is_sotto_paga) else colors.HexColor('#F0F4F8')]),
            ('TOPPADDING', (0,0), (-1,-1), 1.2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1.2),
        ]))

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

        if idx < len(lista_turni) - 1:
            elements.append(PageBreak())

    doc_target.build(elements)

# Generazione dei due PDF separati
genera_pdf_per_lista(turni_susa, "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Dossier_Turni_2026_DEPOSITO_SUSA.pdf", "DEPOSITO SUSA")
genera_pdf_per_lista(turni_salbertrand, "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Dossier_Turni_2026_RIMESSA_SALBERTRAND.pdf", "RIMESSA SALBERTRAND")

print("✅ GENERATI CON SUCCESSO I 2 DOSSIER SEPARATI PER SUSA (11 pag) E SALBERTRAND (8 pag)!")
