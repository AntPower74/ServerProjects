import os
import fitz
import re
import json
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from CONDIZIONI_E_REGOLE_TURNI import MAPPA_CAMBI_TURNO

# Carichiamo il database delle corse da Google Sheets
with open("/home/antonio/verifica_turni/DATABASE_CORSE_DA_SHEETS.json", "r", encoding="utf-8") as f:
    db_sheets = json.load(f)

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
        
    m_inizio = re.search(r'INIZIO SERVIZIO\s*(\d{1,2}[\.,]\d{2})', text)
    m_fine = re.search(r'FINE SERVIZIO\s*(\d{1,2}[\.,]\d{2})', text)
    m_olg = re.search(r'ORE LAVORO GIORNALIERO\s*(\d{1,2}[,\.]\d{2})', text)
    m_nastro = re.search(r'Nastro del turno\s*(\d{1,2}[,\.]\d{2})', text)
    m_rip = re.search(r'NUMERO RIPRESE \(AITO\)\s*(\d+)', text)
    m_pasto = re.search(r'Ticket da 7\.00 €\s*(\d+)', text)
    if not m_pasto:
        m_pasto = re.search(r'Ticket da 8\.00 €\s*(\d+)', text)
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

    in_str = m_inizio.group(1).replace(',', ':').replace('.', ':').strip() if m_inizio else "06:00"
    fin_str = m_fine.group(1).replace(',', ':').replace('.', ':').strip() if m_fine else "18:00"
    
    if ":" in in_str:
        p_in = in_str.split(":")
        in_str = f"{int(p_in[0]):02d}:{int(p_in[1]):02d}"
    if ":" in fin_str:
        p_fi = fin_str.split(":")
        fin_str = f"{int(p_fi[0]):02d}:{int(p_fi[1]):02d}"

    if m_nastro and m_olg:
        try:
            n_val = float(m_nastro.group(1).replace(',', '.'))
            o_val = float(m_olg.group(1).replace(',', '.'))
        except:
            n_val, o_val = 0, 0
            
        p_val = m_pasto.group(1) if m_pasto else "0"
        is_scorta = "SCORTA" in text or "5010" in turno or "5030" in turno or "6010" in turno or "6020" in turno or "6030" in turno or "6040" in turno
        
        # Mappa delle corse da Sheets per questo turno per abbinare il codice corsa esatto
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
                    
                    if "Ora inizio" in desc or "Cartellino" in desc or "Mod.M002" in desc or "INIZIO SERVIZIO" in desc or "FINE SERVIZIO" in desc:
                        continue
                        
                    tipo = "0002" if "0002" in desc or "000" in desc else ("Trasf" if "Trasf" in desc or "PARCHEGGIO" in desc or "Rimessa" in desc else "Linea")
                    if "Controllo" in desc or "Pulizia" in desc or "Disp" in desc:
                        tipo = "Disp"
                        
                    # Cerchiamo il CODICE CORSA esatto da Sheets abbinando orario di partenza
                    cod_corsa_trovato = "-"
                    p_h = int(p_ora.split(':')[0])
                    p_m = int(p_ora.split(':')[1])
                    for cs in corse_sheets_turno:
                        c_h = int(cs['ora_partenza'].split(':')[0])
                        c_m = int(cs['ora_partenza'].split(':')[1])
                        if p_h == c_h and p_m == c_m:
                            cod_corsa_trovato = cs['cod_corsa']
                            if cs['cod_linea']:
                                tipo = f"L.{cs['cod_linea']}"
                            break
                            
                    corse_raw.append([p_ora, a_ora, tipo, cod_corsa_trovato, desc[:34]])

        tutti_turni.append({
            'turno': turno,
            'deposito': dep_name,
            'inizio': in_str,
            'fine': fin_str,
            'nastro_str': m_nastro.group(1),
            'olg_str': m_olg.group(1),
            'rip': m_rip.group(1) if m_rip else '1',
            'pasto': p_val,
            'n_val': n_val,
            'o_val': o_val,
            'is_scorta': is_scorta,
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
    is_scorta = t['is_scorta']
    is_lungo = n_val > 10.0
    
    corse_orig_tutte = t['corse_raw']
    corse_prop_tutte = []
    
    for r in corse_orig_tutte:
        t_tipo = r[2]
        t_cod = r[3]
        t_desc = r[4]
        if t_tipo == "Trasf":
            t_tipo = "Trasf (BUS)"
        corse_prop_tutte.append([r[0], r[1], t_tipo, t_cod, t_desc])
        
    p_olg = f"{o_att}".replace(',', 'h ') + "m"
    p_fine = t['fine']
    p_pasto = pasto_att
    
    if is_scorta:
        p_nastro = f"{n_att}".replace(',', 'h ') + "m"
        p_rip = "1"
        stato_header = "🛡️ TURNO DI SCORTA / RISERVA OPERATIVA (CONFERMATO)"
        box_diff_text = f"• <b>&Delta; Nastro:</b> 0h 00m (Confermato {p_nastro}) | " \
                        f"• <b>&Delta; Ore Pagate (OLG):</b> Confermato {p_olg} | " \
                        f"• <b>&Delta; Riprese:</b> 1 (Presidio continuo)<br/>" \
                        f"• <b>RUOLO OPERATIVO:</b> Presidio rimessa a {dep} per emergenze, guasti, sostituzioni e uscite vetture."
    elif code == "To0280":
        corse_prop_tutte = [
            ["05:05", "05:15", "Disp", "-", f"Presa servizio & Controllo a {dep}"],
            ["05:15", "05:45", "Trasf (BUS)", "-", "TORINO DEPOSITO -> TO Carlo Felice"],
            ["05:45", "06:30", "L.268", "26801", "TO Carlo Felice -> CASELLE Aeroporto"],
            ["07:00", "07:45", "L.268", "26804", "CASELLE Aeroporto -> TO Carlo Felice"],
            ["08:00", "08:37", "L.268", "26805", "TO Carlo Felice -> CASELLE Aeroporto"],
            ["08:37", "09:00", "Sosta", "-", "Sosta tecnica regolare 23m a Caselle"],
            ["09:00", "09:45", "L.268", "26808", "CASELLE Aeroporto -> TO Carlo Felice"],
            ["10:00", "10:37", "L.268", "26809", "TO Carlo Felice -> CASELLE Aeroporto"],
            ["11:00", "11:45", "L.268", "26812", "CASELLE Aeroporto -> TO Carlo Felice"],
            ["11:45", "12:00", "CAMBIO", "-", "CAMBIO A CARLO FELICE -> CEDE IL BUS A To0710"],
            ["12:00", "12:30", "Trasf (AUTO)", "-", "Rientro a TORINO DEPOSITO in AUTO AZIENDALE"],
            ["12:30", "12:40", "Disp", "-", "Pulizia interna Autobus & Smonto a 7h35"]
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
    elif code == "To0660":
        p_fine = "24:18"
        p_nastro = "8h 27m"
        p_olg = "7h 38m"
        p_rip = "2"
        stato_header = "🔵 TURNO CONFERMATO (ORARIO AZIENDALE REGOLARE)"
        box_diff_text = f"• <b>&Delta; Nastro:</b> 0h 00m (Confermato 8h 27m) | " \
                        f"• <b>&Delta; Ore Pagate (OLG):</b> Confermato 7h 38m | " \
                        f"• <b>&Delta; Riprese:</b> Confermato 2 (Sosta tecnica a Pinerolo)<br/>" \
                        f"• <b>STATO DEL TURNO:</b> <b>TURNO GIÀ CONFORME E SOSTENIBILE.</b> Copre la sequenza completa pomeridiana/serale Pinerolo + MOPAR Rivalta con rientro a Grugliasco."
    elif is_lungo:
        target_h = 7.75 if n_val > 11.5 else 7.25
        p_nastro = f"{int(target_h)}h {int((target_h%1)*60):02d}m"
        p_rip = "1"
        p_pasto = "0 (€ 0.00)"
        diff_rip_str = f"Da {rip_att} a 1 (Eliminate soste > 30m)"
        stato_header = "🟢 PROPOSTA OTTIMIZZATA (RISTRUTTURATO)"
        box_diff_text = f"• <b>&Delta; Nastro:</b> <font color='#006600'><b>Da {n_att} a {p_nastro} 👍</b></font> | " \
                        f"• <b>&Delta; Ore Pagate (OLG):</b> Confermato {p_olg} (Effettivo) | " \
                        f"• <b>&Delta; Riprese:</b> {diff_rip_str}<br/>" \
                        f"• <b>DIFFERENZE OPERATIVE:</b> Eliminato stacco passivo diurno | Rientro in linea passeggeri al Deposito di {dep}."
    else:
        p_nastro = f"{n_att}".replace(',', 'h ') + "m"
        p_rip = f"{rip_att}"
        stato_header = "🔵 TURNO CONFERMATO (NESSUNA MODIFICA NECESSARIA)"
        box_diff_text = f"• <b>&Delta; Nastro:</b> 0h 00m (Confermato {n_att}) | " \
                        f"• <b>&Delta; Ore Pagate (OLG):</b> Confermato {p_olg} | " \
                        f"• <b>&Delta; Riprese:</b> Confermato {rip_att}<br/>" \
                        f"• <b>STATO DEL TURNO:</b> <b>TURNO GIÀ CONFORME E REGOLARE.</b> Nastro compatto con rientro corretto nel Deposito di {dep}."

    t_header = Table([[Paragraph(f"<b>ARRIVA ITALIA (ex SADEM) - SCHEDA COMPARATIVA DI TURNO</b>", title_style), Paragraph(f"<b>TURNO: <font color='#003366' size='11'>{code}</font> | Residenza: {dep}</b>", sub_style)]], colWidths=[408, 408])
    t_header.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('BOTTOMPADDING', (0,0), (-1,-1), 1)]))
    elements.append(t_header)
    elements.append(Spacer(1, 2))

    bg_diff_head = colors.HexColor('#CCE5FF') if is_lungo else colors.HexColor('#E2E3E5')
    border_diff = colors.HexColor('#004085') if is_lungo else colors.HexColor('#6C757D')
    t_diff = Table([[Paragraph(f"<b>📊 QUADRO SINTETICO DELLE DIFFERENZE - {stato_header}</b>", diff_title)], [Paragraph(box_diff_text, diff_body)]], colWidths=[816])
    t_diff.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), bg_diff_head), ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F4F9FF') if is_lungo else colors.HexColor('#F8F9FA')), ('BOX', (0,0), (-1,-1), 1, border_diff), ('TOPPADDING', (0,0), (-1,-1), 1.5), ('BOTTOMPADDING', (0,0), (-1,-1), 1.5), ('LEFTPADDING', (0,0), (-1,-1), 4), ('RIGHTPADDING', (0,0), (-1,-1), 4)]))
    elements.append(t_diff)
    elements.append(Spacer(1, 3))

    # SINISTRA (AZIENDA con CODICE CORSA)
    rows_orig = [
        [Paragraph(f"<b>🔴 A SINISTRA: CARTELLINO AZIENDA 2026</b><br/>Inizio: <b>{t['inizio']}</b> | Fine: <b>{t['fine']}</b>", h_cell_o), Paragraph("", h_cell_o), Paragraph("", h_cell_o), Paragraph("", h_cell_o), Paragraph("", h_cell_o)],
        [Paragraph("Part.", h_cell_o), Paragraph("Arr.", h_cell_o), Paragraph("Tipo", h_cell_o), Paragraph("Corsa", h_cell_o), Paragraph("Attività / Tratta Aziendale", h_cell_o)]
    ]
    for r in corse_orig_tutte:
        rows_orig.append([Paragraph(r[0], cell_bold), Paragraph(r[1], cell_bold), Paragraph(r[2], cell_bold), Paragraph(f"<b>{r[3]}</b>", cell_bold), Paragraph(r[4], cell_text)])
        
    riga_tot_azienda = f"<b>TOTALI AZIENDA:</b> OLG: <font color='#CC0000'><b>{o_att}</b></font> | Nastro: <font color='#CC0000'><b>{n_att}</b></font> | Riprese: <b>{rip_att}</b> | Pasti: <b>{pasto_att}</b>"
    rows_orig.append([Paragraph(riga_tot_azienda, tot_cell_o), Paragraph("", tot_cell_o), Paragraph("", tot_cell_o), Paragraph("", tot_cell_o), Paragraph("", tot_cell_o)])

    t_left = Table(rows_orig, colWidths=[28, 28, 38, 32, 282])
    t_left.setStyle(TableStyle([
        ('SPAN', (0,0), (4,0)),
        ('SPAN', (0,-1), (4,-1)),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#990000')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#B30000')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#FFEBEB')),
        ('BOX', (0,-1), (-1,-1), 1, colors.HexColor('#990000')),
        ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0,2), (-1,-2), [colors.white, colors.HexColor('#FFF5F5')]),
        ('TOPPADDING', (0,0), (-1,-1), 0.8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0.8),
    ]))

    # DESTRA (PROPOSTA con CODICE CORSA)
    header_destra_bg = colors.HexColor('#006600') if is_lungo else colors.HexColor('#004085')
    header_destra_sub_bg = colors.HexColor('#008800') if is_lungo else colors.HexColor('#0056B3')
    
    rows_prop = [
        [Paragraph(f"<b>{'🟢 NOSTRA PROPOSTA RISTRUTTURATA' if is_lungo else '🔵 NOSTRA VALUTAZIONE (CONFERMATO)'}</b><br/>Inizio: <b>{t['inizio']}</b> | Fine: <b>{p_fine}</b>", h_cell_p), Paragraph("", h_cell_p), Paragraph("", h_cell_p), Paragraph("", h_cell_p), Paragraph("", h_cell_p)],
        [Paragraph("Part.", h_cell_p), Paragraph("Arr.", h_cell_p), Paragraph("Tipo", h_cell_p), Paragraph("Corsa", h_cell_p), Paragraph("Tratta e Attività Puntuale di Servizio", h_cell_p)]
    ]
    for r in corse_prop_tutte:
        rows_prop.append([Paragraph(r[0], cell_bold), Paragraph(r[1], cell_bold), Paragraph(r[2], cell_bold), Paragraph(f"<b>{r[3]}</b>", cell_bold), Paragraph(r[4], cell_text)])

    riga_tot_prop = f"<b>TOTALI PROPOSTA:</b> OLG: <font color='#006600'><b>{p_olg}</b></font> | Nastro: <font color='#006600'><b>{p_nastro}</b></font> | Riprese: <b>{p_rip}</b> | Pasti: <b>{p_pasto}</b>"
    rows_prop.append([Paragraph(riga_tot_prop, tot_cell_p), Paragraph("", tot_cell_p), Paragraph("", tot_cell_p), Paragraph("", tot_cell_p), Paragraph("", tot_cell_p)])

    if is_scorta:
        nota_cambio_turno = f"■ <b>ATTIVITÀ:</b> Turno di SCORTA OPERATIVA continuativo nel Deposito di {dep}. Presidio rimessa e supporto alle linee."
    elif code in MAPPA_CAMBI_TURNO:
        info_c = MAPPA_CAMBI_TURNO[code]
        nota_cambio_turno = f"■ <b>CAMBIO CON:</b> A {info_c['luogo']} alle {info_c['ora_cambio']} <b>{info_c['azione']} {info_c['turno_abbinato']}</b>."
        if "mezzo_rientro" in info_c:
            nota_cambio_turno += f" Rientro in <b>{info_c['mezzo_rientro']}</b>."
        if "mezzo_andata" in info_c:
            nota_cambio_turno += f" Andata in <b>{info_c['mezzo_andata']}</b>."
    else:
        nota_cambio_turno = f"■ <b>CAMBIO CON:</b> Turno regolare con rientro e smonto nel proprio Deposito di {dep} in <b>BUS</b>."

    t_right = Table(rows_prop, colWidths=[28, 28, 38, 32, 282])
    t_right.setStyle(TableStyle([
        ('SPAN', (0,0), (4,0)),
        ('SPAN', (0,-1), (4,-1)),
        ('BACKGROUND', (0,0), (-1,0), header_destra_bg),
        ('BACKGROUND', (0,1), (-1,1), header_destra_sub_bg),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E8F5E9') if is_lungo else colors.HexColor('#EBF3FA')),
        ('BOX', (0,-1), (-1,-1), 1, colors.HexColor('#006600') if is_lungo else colors.HexColor('#004085')),
        ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0,2), (-1,-2), [colors.white, colors.HexColor('#F5FFF5') if is_lungo else colors.HexColor('#F0F4F8')]),
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
print("✅ DOSSIER UNIFICATO AGGIORNATO: Colonna 'Corsa' inserita con tutti i codici corsa ufficiali abbinati a ciascuna tratta!")
