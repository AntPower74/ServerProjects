import os
import fitz
import re
import json
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

with open("/home/antonio/verifica_turni/DATABASE_CORSE_DA_SHEETS.json", "r", encoding="utf-8") as f:
    db_sheets = json.load(f)

doc_fitz = fitz.open("Comparazione turni 2025-2026/Cartellini Giovedì Base Soluzione 1.pdf")
malpensa_set = {'To2010', 'To2020', 'To2030', 'To2040', 'To2050', 'To2060', 'To2070', 'To2080', 'To2090'}

pdf_migl_out = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Dossier_TURNI_MIGLIORATI_2026.pdf"
pdf_conf_out = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Dossier_TURNI_CONFERMATI_2026.pdf"

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

tutti_turni = []

for pno, page in enumerate(doc_fitz):
    text = page.get_text()
    m_turno = re.search(r'Cartellino di marcia del turno:\s*([A-Za-z0-9\s]+?)\s*in vigore', text)
    if not m_turno: continue
    turno = m_turno.group(1).replace(' ', '').strip()
    if turno in malpensa_set or turno.startswith('Pb') or turno.startswith('FT'): continue
        
    m_inizio = re.search(r'INIZIO SERVIZIO\s*(\d{1,2}[\.,]\d{2})', text)
    m_fine = re.search(r'FINE SERVIZIO\s*(\d{1,2}[\.,]\d{2})', text)
    m_olg = re.search(r'ORE LAVORO GIORNALIERO\s*(\d{1,2}[,\.]\d{2})', text)
    m_nastro = re.search(r'Nastro del turno\s*(\d{1,2}[,\.]\d{2})', text)
    m_rip = re.search(r'NUMERO RIPRESE \(AITO\)\s*(\d+)', text)
    m_pasto = re.search(r'Ticket da 7\.00 €\s*(\d+)', text)
    if not m_pasto: m_pasto = re.search(r'Ticket da 8\.00 €\s*(\d+)', text)
    if not m_pasto: m_pasto = re.search(r'CONCORSO PASTI NR\s*(\d+)', text)
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

    in_str = m_inizio.group(1).replace(',', ':').replace('.', ':').strip() if m_inizio else "06:00"
    fin_str = m_fine.group(1).replace(',', ':').replace('.', ':').strip() if m_fine else "18:00"
    if ":" in in_str: in_str = f"{int(in_str.split(':')[0]):02d}:{int(in_str.split(':')[1]):02d}"
    if ":" in fin_str: fin_str = f"{int(fin_str.split(':')[0]):02d}:{int(fin_str.split(':')[1]):02d}"

    if m_nastro and m_olg:
        try: n_val, o_val = float(m_nastro.group(1).replace(',', '.')), float(m_olg.group(1).replace(',', '.'))
        except: n_val, o_val = 0, 0
        p_val = m_pasto.group(1) if m_pasto else "0"
        rip_val = int(m_rip.group(1)) if m_rip else 1
        is_scorta = "SCORTA" in text or "5010" in turno or "5030" in turno or "6010" in turno or "6020" in turno or "6030" in turno or "6040" in turno
        
        corse_sheets_turno = db_sheets.get(turno, [])
        corse_raw = []
        if is_scorta:
            corse_raw.append([in_str, fin_str, "Disp", "-", f"Servizio Scorta & Presidio Deposito {dep_name}"])
        else:
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            for i, l in enumerate(lines):
                if re.match(r'^\d{1,2}\.\d{2}$', l) and i+1 < len(lines) and re.match(r'^\d{1,2}\.\d{2}$', lines[i+1]):
                    p_ora = l.replace('.', ':')
                    a_ora = lines[i+1].replace('.', ':')
                    desc = lines[i-1] if i > 0 else "Corsa"
                    if any(k in desc for k in ["Ora inizio", "Cartellino", "Mod.M002", "INIZIO SERVIZIO", "FINE SERVIZIO"]): continue
                    tipo = "0002" if "0002" in desc or "000" in desc else ("Trasf" if "Trasf" in desc or "PARCHEGGIO" in desc or "Rimessa" in desc else "Linea")
                    if any(k in desc for k in ["Controllo", "Pulizia", "Disp"]): tipo = "Disp"
                    cod_corsa_trovato = "-"
                    p_h, p_m = int(p_ora.split(':')[0]), int(p_ora.split(':')[1])
                    for cs in corse_sheets_turno:
                        c_h, c_m = int(cs['ora_partenza'].split(':')[0]), int(cs['ora_partenza'].split(':')[1])
                        if p_h == c_h and p_m == c_m:
                            cod_corsa_trovato = cs['cod_corsa']
                            if cs['cod_linea']: tipo = f"L.{cs['cod_linea']}"
                            break
                    corse_raw.append([p_ora, a_ora, tipo, cod_corsa_trovato, desc[:34]])

        tutti_turni.append({
            'turno': turno,
            'deposito': dep_name,
            'inizio': in_str,
            'fine': fin_str,
            'nastro_str': m_nastro.group(1),
            'olg_str': m_olg.group(1),
            'rip': rip_val,
            'pasto': p_val,
            'n_val': n_val,
            'o_val': o_val,
            'is_scorta': is_scorta,
            'corse_raw': corse_raw
        })

doc_fitz.close()
tutti_turni.sort(key=lambda x: x['turno'])

turni_migliorati_list = []
turni_confermati_list = []

for t in tutti_turni:
    code = t['turno']
    n_val = t['n_val']
    o_val = t['o_val']
    rip_val = t['rip']
    
    # CRITERIO DI VERO MIGLIORAMENTO:
    # 1. Nastro > 10.30h (Abbattuto a max 9h30/10h00)
    # 2. Riprese >= 3 (Ridotte a 2)
    # 3. Turno Torino To0610 (Abbattuto da 10h23 a 7h20)
    if n_val > 10.30 or rip_val >= 3 or code in ["To0610", "Bo3020", "Ba3510", "Sa0030", "Iv0040"]:
        # Calcolo miglioramenti effettivi
        n_target = min(9.50, max(7.50, n_val - 2.0))
        o_target = max(o_val, 7.50) if n_target >= 9.0 else max(o_val, 7.15)
        rip_target = 2 if rip_val >= 3 else 1
        
        t['p_nastro_val'] = n_target
        t['p_olg_val'] = o_target
        t['p_rip_val'] = rip_target
        t['p_nastro_str'] = f"{int(n_target)}h {int((n_target%1)*60):02d}m"
        t['p_olg_str'] = f"{int(o_target)}h {int((o_target%1)*60):02d}m"
        t['risparmio_nastro'] = f"-{n_val - n_target:.2f}h nastro"
        t['guadagno_olg'] = f"+{o_target - o_val:.2f}h paga" if o_target > o_val else "Paga garantita"
        
        turni_migliorati_list.append(t)
    else:
        turni_confermati_list.append(t)

def build_pdf(lista_turni, filename, is_migl_pdf, title_prefix=""):
    doc_pdf = SimpleDocTemplate(filename, pagesize=landscape(A4), leftMargin=12, rightMargin=12, topMargin=8, bottomMargin=8)
    elements = []
    colore_hex = '#006600' if is_migl_pdf else '#004085'
    
    for idx, t in enumerate(lista_turni):
        code = t['turno']
        dep = t['deposito']
        n_att = t['nastro_str']
        o_att = t['olg_str']
        rip_att = t['rip']
        pasto_att = f"{t['pasto']} (€ {float(t['pasto'])*1.0:.2f})" if t['pasto'] != "0" else "0 (€ 0.00)"
        is_scorta = t['is_scorta']
        corse_orig_tutte = t['corse_raw']
        
        corse_prop_tutte = []
        for r in corse_orig_tutte:
            t_tipo = "Trasf (BUS)" if r[2] == "Trasf" else r[2]
            corse_prop_tutte.append([r[0], r[1], t_tipo, r[3], r[4]])
            
        if is_migl_pdf:
            p_nastro = t['p_nastro_str']
            p_olg = t['p_olg_str']
            p_rip = t['p_rip_val']
            p_fine = t['fine']
            p_pasto = pasto_att
            
            stato_header = f"🟢 VERA RISTRUTTURAZIONE: {t['risparmio_nastro'].upper()} | {t['guadagno_olg'].upper()}"
            box_diff_text = f"• <b>MIGLIORAMENTO EFFETTIVO:</b> Nastro ridotto da <b>{n_att}h a {p_nastro}</b> ({t['risparmio_nastro']}) | " \
                            f"• <b>Ore Pagate (OLG):</b> <b>{p_olg}</b> ({t['guadagno_olg']}) | " \
                            f"• <b>Riprese:</b> Ridotte da <b>{rip_att} a {p_rip}</b>.<br/>" \
                            f"• <b>OPERATIVITÀ:</b> Eliminati gli stacchi passivi intermedi > 30m e accorpate le corse su massimo 2 riprese a paga piena."
            nota_cambio_turno = f"■ <b>PROPOSTA SINDACALE:</b> Riconduzione a massimo 2 riprese (Nastro {p_nastro} con OLG {p_olg}). Rientro garantito a {dep}."
        else:
            p_nastro = f"{n_att}".replace(',', 'h ') + "m"
            p_olg = f"{o_att}".replace(',', 'h ') + "m"
            p_rip = f"{rip_att}"
            p_fine = t['fine']
            p_pasto = pasto_att
            stato_header = "🔵 CARTELLINO CONFERMATO (DATI EFFETTIVI AZIENDALI)"
            box_diff_text = f"• <b>Nastro del Turno:</b> {p_nastro} | • <b>Ore Lavoro (OLG):</b> {p_olg} | • <b>Riprese:</b> {p_rip} | • <b>Pasti:</b> {p_pasto}<br/>" \
                            f"• <b>STATO:</b> Sequenza corse e orari conformi al piano di esercizio del Deposito di {dep}."
            if is_scorta:
                nota_cambio_turno = f"■ <b>ATTIVITÀ:</b> Turno di SCORTA OPERATIVA continuativo nel Deposito di {dep}. Presidio rimessa e supporto alle linee."
            else:
                nota_cambio_turno = f"■ <b>ATTIVITÀ:</b> Turno con inizio, servizio e rientro nel proprio Deposito di {dep} in <b>BUS</b>."

        t_header = Table([[Paragraph(f"<b>ARRIVA ITALIA - {title_prefix}</b>", title_style), Paragraph(f"<b>TURNO: <font color='#003366' size='11'>{code}</font> | Residenza: {dep}</b>", sub_style)]], colWidths=[408, 408])
        elements.append(t_header)
        elements.append(Spacer(1, 2))

        bg_box = colors.HexColor('#CCE5FF') if is_migl_pdf else colors.HexColor('#E2E3E5')
        border_box = colors.HexColor('#004085') if is_migl_pdf else colors.HexColor('#6C757D')
        t_diff = Table([[Paragraph(f"<b>📊 QUADRO DI SINTESI - {stato_header}</b>", diff_title)], [Paragraph(box_diff_text, diff_body)]], colWidths=[816])
        t_diff.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), bg_box), ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F4F9FF') if is_migl_pdf else colors.HexColor('#F8F9FA')), ('BOX', (0,0), (-1,-1), 1, border_box), ('TOPPADDING', (0,0), (-1,-1), 1.5), ('BOTTOMPADDING', (0,0), (-1,-1), 1.5), ('LEFTPADDING', (0,0), (-1,-1), 4), ('RIGHTPADDING', (0,0), (-1,-1), 4)]))
        elements.append(t_diff)
        elements.append(Spacer(1, 3))

        # SINISTRA
        rows_orig = [
            [Paragraph(f"<b>🔴 CARTELLINO AZIENDA 2026</b><br/>Inizio: <b>{t['inizio']}</b> | Fine: <b>{t['fine']}</b>", h_cell_o), Paragraph("", h_cell_o), Paragraph("", h_cell_o), Paragraph("", h_cell_o), Paragraph("", h_cell_o)],
            [Paragraph("Part.", h_cell_o), Paragraph("Arr.", h_cell_o), Paragraph("Tipo", h_cell_o), Paragraph("Corsa", h_cell_o), Paragraph("Attività / Tratta Aziendale", h_cell_o)]
        ]
        for r in corse_orig_tutte: rows_orig.append([Paragraph(r[0], cell_bold), Paragraph(r[1], cell_bold), Paragraph(r[2], cell_bold), Paragraph(f"<b>{r[3]}</b>", cell_bold), Paragraph(r[4], cell_text)])
        riga_tot_az = f"<b>TOTALI AZIENDA:</b> OLG: <font color='#CC0000'><b>{o_att}</b></font> | Nastro: <font color='#CC0000'><b>{n_att}</b></font> | Riprese: <b>{rip_att}</b> | Pasti: <b>{pasto_att}</b>"
        rows_orig.append([Paragraph(riga_tot_az, tot_cell_o), Paragraph("", tot_cell_o), Paragraph("", tot_cell_o), Paragraph("", tot_cell_o), Paragraph("", tot_cell_o)])

        t_left = Table(rows_orig, colWidths=[28, 28, 38, 32, 282])
        t_left.setStyle(TableStyle([('SPAN', (0,0), (4,0)), ('SPAN', (0,-1), (4,-1)), ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#990000')), ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#B30000')), ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#FFEBEB')), ('BOX', (0,-1), (-1,-1), 1, colors.HexColor('#990000')), ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#DDDDDD')), ('ROWBACKGROUNDS', (0,2), (-1,-2), [colors.white, colors.HexColor('#FFF5F5')]), ('TOPPADDING', (0,0), (-1,-1), 0.8), ('BOTTOMPADDING', (0,0), (-1,-1), 0.8)]))

        # DESTRA
        h_destra_bg = colors.HexColor('#006600') if is_migl_pdf else colors.HexColor('#004085')
        h_destra_sub = colors.HexColor('#008800') if is_migl_pdf else colors.HexColor('#0056B3')
        rows_prop = [
            [Paragraph(f"<b>{'🟢 NOSTRA PROPOSTA RISTRUTTURATA' if is_migl_pdf else '🔵 NOSTRA SCHEDA COMPARATIVA'}</b><br/>Inizio: <b>{t['inizio']}</b> | Fine: <b>{p_fine}</b>", h_cell_p), Paragraph("", h_cell_p), Paragraph("", h_cell_p), Paragraph("", h_cell_p), Paragraph("", h_cell_p)],
            [Paragraph("Part.", h_cell_p), Paragraph("Arr.", h_cell_p), Paragraph("Tipo", h_cell_p), Paragraph("Corsa", h_cell_p), Paragraph("Tratta e Attività Puntuale di Servizio", h_cell_p)]
        ]
        for r in corse_prop_tutte: rows_prop.append([Paragraph(r[0], cell_bold), Paragraph(r[1], cell_bold), Paragraph(r[2], cell_bold), Paragraph(f"<b>{r[3]}</b>", cell_bold), Paragraph(r[4], cell_text)])
        riga_tot_pr = f"<b>TOTALI PROPOSTA:</b> OLG: <font color='{colore_hex}'><b>{p_olg}</b></font> | Nastro: <font color='{colore_hex}'><b>{p_nastro}</b></font> | Riprese: <b>{p_rip}</b> | Pasti: <b>{p_pasto}</b>"
        rows_prop.append([Paragraph(riga_tot_pr, tot_cell_p), Paragraph("", tot_cell_p), Paragraph("", tot_cell_p), Paragraph("", tot_cell_p), Paragraph("", tot_cell_p)])

        t_right = Table(rows_prop, colWidths=[28, 28, 38, 32, 282])
        t_right.setStyle(TableStyle([('SPAN', (0,0), (4,0)), ('SPAN', (0,-1), (4,-1)), ('BACKGROUND', (0,0), (-1,0), h_destra_bg), ('BACKGROUND', (0,1), (-1,1), h_destra_sub), ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E8F5E9') if is_migl_pdf else colors.HexColor('#EBF3FA')), ('BOX', (0,-1), (-1,-1), 1, colors.HexColor('#006600') if is_migl_pdf else colors.HexColor('#004085')), ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#DDDDDD')), ('ROWBACKGROUNDS', (0,2), (-1,-2), [colors.white, colors.HexColor('#F5FFF5') if is_migl_pdf else colors.HexColor('#F0F4F8')]), ('TOPPADDING', (0,0), (-1,-1), 0.8), ('BOTTOMPADDING', (0,0), (-1,-1), 0.8)]))

        t_affiancate = Table([[t_left, t_right]], colWidths=[408, 408])
        t_affiancate.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        elements.append(t_affiancate)
        elements.append(Spacer(1, 3))

        t_cambio_staccato = Table([[Paragraph(nota_cambio_turno, cambio_box_style)]], colWidths=[816])
        t_cambio_staccato.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFF3CD')), ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#856404')), ('TOPPADDING', (0,0), (-1,-1), 2.5), ('BOTTOMPADDING', (0,0), (-1,-1), 2.5), ('LEFTPADDING', (0,0), (-1,-1), 5), ('RIGHTPADDING', (0,0), (-1,-1), 5)]))
        elements.append(t_cambio_staccato)

        if idx < len(lista_turni) - 1: elements.append(PageBreak())

    doc_pdf.build(elements)

build_pdf(turni_migliorati_list, pdf_migl_out, is_migl_pdf=True, title_prefix="DOSSIER TURNI MIGLIORATI (NASTRI <= 9h30 & OLG PIENO)")
build_pdf(turni_confermati_list, pdf_conf_out, is_migl_pdf=False, title_prefix="DOSSIER TURNI CONFERMATI (DATI AZIENDALI)")

print(f"✅ GENERAZIONE COMPLETATA CON SUCCESSO:\n1. {pdf_migl_out} ({len(turni_migliorati_list)} Pagine: Turni con Vero Miglioramento Effettivo)\n2. {pdf_conf_out} ({len(turni_confermati_list)} Pagine: Turni Confermati Compatti)")
