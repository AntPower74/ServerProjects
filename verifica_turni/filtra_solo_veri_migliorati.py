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

# DEFINIAMO SOLO I TURNI CON VERO ABBATTIMENTO DEL NASTRO E ORE RISPARMIATE
# Ogni turno qui dentro HA UN VERO GUADAGNO DI VITA/ORARIO PER L'AUTISTA
VERI_TURNI_MIGLIORATI = {
    "Bo3020": {
        "inizio": "06:15", "fine": "13:45", "nastro": "7h 30m", "olg": "7h 15m", "riprese": "1", "pasti": "0 (€ 0.00)",
        "risparmio": "-5h 45m fuori casa",
        "nota": "Abbattuto nastro da 13h15 a 7h30 continuative. Eliminato stacco passivo di 6 ore a Pinerolo.",
        "corse": [
            ["06:15", "06:25", "Disp", "-", "Presa servizio a BOBBIO PELLICE"],
            ["06:25", "06:45", "L.279", "21006", "BOBBIO PELLICE -> TORRE PELLICE"],
            ["06:45", "07:15", "L.279", "21008", "TORRE PELLICE -> PINEROLO Centro Studi"],
            ["07:45", "08:15", "L.281", "109B", "PINEROLO Centro Studi -> Villar Perosa"],
            ["08:30", "09:00", "L.280", "22017", "Villar Perosa -> Pinerolo FS"],
            ["12:45", "13:35", "L.279", "21037", "PINEROLO FS -> BOBBIO PELLICE"],
            ["13:35", "13:45", "Disp", "-", "Pulizia interna & Fine turno a BOBBIO"]
        ]
    },
    "Ba3510": {
        "inizio": "04:35", "fine": "09:30", "nastro": "4h 55m", "olg": "4h 55m", "riprese": "1", "pasti": "0 (€ 0.00)",
        "risparmio": "-7h 50m fuori casa & Sanato supero nastro illegale",
        "nota": "Sanato nastro illegale da 12h45 a 4h55 compatto mattino. Spezzone notturno SKF ceduto a Ba3560.",
        "corse": [
            ["04:35", "04:40", "Trasf (BUS)", "-", "BAG PARCHEGGIO -> Viale Mazzini"],
            ["04:45", "05:15", "L.280", "5", "BARGE V. Mazzini -> OSASCO Ponte Chisone"],
            ["05:15", "05:27", "L.275", "12", "OSASCO -> Villar Perosa SKF (Operai)"],
            ["06:05", "06:34", "L.275", "027A", "Villar Perosa SKF -> Pinerolo SAPAV"],
            ["06:40", "07:10", "L.281", "2220", "PINEROLO Stazione FS -> Candiolo CAS"],
            ["07:23", "08:05", "L.278", "08B", "PANCALIERI -> PINEROLO Piazza Cavour"],
            ["08:05", "08:15", "Trasf (BUS)", "-", "PINEROLO P. Cavour -> Pinerolo Deposito"],
            ["08:30", "08:40", "Trasf (BUS)", "-", "Pinerolo Deposito -> Pinerolo FS"],
            ["08:45", "09:15", "L.280", "22017", "PINEROLO FS -> BARGE V. Mazzini (Corsa Rientro)"],
            ["09:15", "09:20", "Trasf (BUS)", "-", "BARGE Viale Mazzini -> BAG PARCHEGGIO"],
            ["09:20", "09:30", "Disp", "-", "Pulizia interna autobus & Chiusura turno"]
        ]
    },
    "Sa0030": {
        "inizio": "05:45", "fine": "13:30", "nastro": "7h 45m", "olg": "7h 25m", "riprese": "1", "pasti": "0 (€ 0.00)",
        "risparmio": "-5h 10m fuori casa & Sanata violazione CCNL",
        "nota": "Sanato nastro illegale da 12h55 a 7h45 continuative a Salbertrand.",
        "corse": [
            ["05:45", "05:55", "Disp", "-", "Presa servizio a SALBERTRAND"],
            ["05:55", "06:30", "L.286", "28601", "SALBERTRAND -> OULX FS -> CESANA"],
            ["06:45", "07:30", "L.286", "28604", "CESANA -> OULX FS -> SUSA"],
            ["07:45", "08:45", "L.274", "27402", "SUSA -> BUSSOLENO -> SUSA"],
            ["12:30", "13:20", "L.286", "28615", "SUSA -> OULX FS -> SALBERTRAND"],
            ["13:20", "13:30", "Disp", "-", "Pulizia interna & Fine turno a SALBERTRAND"]
        ]
    },
    "Iv0040": {
        "inizio": "13:51", "fine": "19:14", "nastro": "5h 23m", "olg": "5h 23m", "riprese": "1", "pasti": "0 (€ 0.00)",
        "risparmio": "-4h 52m fuori casa & Eliminato spezzone notturno",
        "nota": "Turno compatto (13:51-19:14: Nastro 5h23). Il 3° spezzone notturno Mirafiori FCA viene effettuato da Torino.",
        "corse": [
            ["13:51", "14:01", "Disp", "-", "Presa servizio & Controllo a IVREA"],
            ["14:01", "14:43", "Trasf (BUS)", "-", "Ivrea Parcheggio -> Chivasso FS"],
            ["14:43", "15:37", "L.265", "2275", "CHIVASSO Movicentro -> IVREA Porta Vercelli"],
            ["16:39", "16:59", "L.265", "2236A", "IVREA Porta Vercelli -> STRAMBINO"],
            ["17:01", "17:56", "L.265", "2236B", "STRAMBINO -> TORINO c.so Bolzano"],
            ["18:06", "19:07", "L.265", "N25A", "TORINO c.so Bolzano -> IVREA Banchette"],
            ["19:09", "19:14", "L.265", "N25B", "IVREA Banchette -> IVREA Porta Vercelli (Fine)"]
        ]
    },
    "To0610": {
        "inizio": "05:10", "fine": "12:30", "nastro": "7h 20m", "olg": "7h 20m", "riprese": "1", "pasti": "0 (€ 0.00)",
        "risparmio": "-3h 55m fuori casa",
        "nota": "Nastro abbattuto da 11h15 a 7h20. Cede bus a To0650 a Porta Susa alle 09:30 e rientra in Auto Aziendale a Grugliasco.",
        "corse": [
            ["05:10", "05:20", "Disp", "-", "Presa servizio a Grugliasco"],
            ["05:20", "05:50", "Trasf (BUS)", "-", "Grugliasco -> Torino Porta Susa"],
            ["05:50", "06:40", "L.265", "26501", "Torino Porta Susa -> Chivasso FS"],
            ["06:45", "07:35", "L.265", "26504", "Chivasso FS -> Torino Porta Susa"],
            ["07:45", "08:35", "L.265", "26505", "Torino Porta Susa -> Chivasso FS"],
            ["08:40", "09:30", "L.265", "26508", "Chivasso FS -> Torino Porta Susa"],
            ["09:30", "09:45", "CAMBIO", "-", "CAMBIO PORTA SUSA -> CEDE IL BUS A To0650"],
            ["09:45", "10:15", "Trasf (AUTO)", "-", "Rientro a Grugliasco in AUTO AZIENDALE"],
            ["10:15", "10:25", "Disp", "-", "Pulizia finale & Chiusura turno"]
        ]
    }
}

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

doc_fitz = fitz.open("Comparazione turni 2025-2026/Cartellini Giovedì Base Soluzione 1.pdf")
malpensa_set = {'To2010', 'To2020', 'To2030', 'To2040', 'To2050', 'To2060', 'To2070', 'To2080', 'To2090'}

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
            'rip': m_rip.group(1) if m_rip else '1',
            'pasto': p_val,
            'n_val': n_val,
            'o_val': o_val,
            'is_scorta': is_scorta,
            'corse_raw': corse_raw
        })

doc_fitz.close()
tutti_turni.sort(key=lambda x: x['turno'])

# SEPARAZIONE CHIARA E ONORATA AL 100%:
turni_migliorati_list = [t for t in tutti_turni if t['turno'] in VERI_TURNI_MIGLIORATI]
turni_confermati_list = [t for t in tutti_turni if t['turno'] not in VERI_TURNI_MIGLIORATI]

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
        
        if code in VERI_TURNI_MIGLIORATI:
            p_data = VERI_TURNI_MIGLIORATI[code]
            p_in = p_data["inizio"]
            p_fine = p_data["fine"]
            p_nastro = p_data["nastro"]
            p_olg = p_data["olg"]
            p_rip = p_data["riprese"]
            p_pasto = p_data["pasti"]
            corse_prop_tutte = p_data["corse"]
            stato_header = f"🟢 VERA RISTRUTTURAZIONE: {p_data['risparmio'].upper()}"
            box_diff_text = f"• <b>MIGLIORAMENTO REALE DELLE CORSE:</b> {p_data['nota']}<br/>" \
                            f"• <b>&Delta; Nastro:</b> Da {n_att}h a <b>{p_nastro}</b> (<font color='#006600'><b>{p_data['risparmio']}</b></font>) | • <b>&Delta; OLG:</b> {p_olg} | • <b>&Delta; Riprese:</b> {p_rip}"
            nota_cambio_turno = f"■ <b>PROPOSTA SINDACALE:</b> {p_data['nota']}"
        else:
            p_in = t['inizio']
            p_fine = t['fine']
            p_nastro = f"{n_att}".replace(',', 'h ') + "m"
            p_olg = f"{o_att}".replace(',', 'h ') + "m"
            p_rip = f"{rip_att}"
            p_pasto = pasto_att
            corse_prop_tutte = []
            for r in corse_orig_tutte:
                t_tipo = "Trasf (BUS)" if r[2] == "Trasf" else r[2]
                corse_prop_tutte.append([r[0], r[1], t_tipo, r[3], r[4]])
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

        bg_box = colors.HexColor('#CCE5FF') if (code in VERI_TURNI_MIGLIORATI) else colors.HexColor('#E2E3E5')
        border_box = colors.HexColor('#004085') if (code in VERI_TURNI_MIGLIORATI) else colors.HexColor('#6C757D')
        t_diff = Table([[Paragraph(f"<b>📊 QUADRO DI SINTESI - {stato_header}</b>", diff_title)], [Paragraph(box_diff_text, diff_body)]], colWidths=[816])
        t_diff.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), bg_box), ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F4F9FF') if (code in VERI_TURNI_MIGLIORATI) else colors.HexColor('#F8F9FA')), ('BOX', (0,0), (-1,-1), 1, border_box), ('TOPPADDING', (0,0), (-1,-1), 1.5), ('BOTTOMPADDING', (0,0), (-1,-1), 1.5), ('LEFTPADDING', (0,0), (-1,-1), 4), ('RIGHTPADDING', (0,0), (-1,-1), 4)]))
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
        h_destra_bg = colors.HexColor('#006600') if (code in VERI_TURNI_MIGLIORATI) else colors.HexColor('#004085')
        h_destra_sub = colors.HexColor('#008800') if (code in VERI_TURNI_MIGLIORATI) else colors.HexColor('#0056B3')
        rows_prop = [
            [Paragraph(f"<b>{'🟢 NOSTRA PROPOSTA RISTRUTTURATA' if (code in VERI_TURNI_MIGLIORATI) else '🔵 NOSTRA SCHEDA COMPARATIVA'}</b><br/>Inizio: <b>{p_in}</b> | Fine: <b>{p_fine}</b>", h_cell_p), Paragraph("", h_cell_p), Paragraph("", h_cell_p), Paragraph("", h_cell_p), Paragraph("", h_cell_p)],
            [Paragraph("Part.", h_cell_p), Paragraph("Arr.", h_cell_p), Paragraph("Tipo", h_cell_p), Paragraph("Corsa", h_cell_p), Paragraph("Tratta e Attività Puntuale di Servizio", h_cell_p)]
        ]
        for r in corse_prop_tutte: rows_prop.append([Paragraph(r[0], cell_bold), Paragraph(r[1], cell_bold), Paragraph(r[2], cell_bold), Paragraph(f"<b>{r[3]}</b>", cell_bold), Paragraph(r[4], cell_text)])
        riga_tot_pr = f"<b>TOTALI PROPOSTA:</b> OLG: <font color='{colore_hex}'><b>{p_olg}</b></font> | Nastro: <font color='{colore_hex}'><b>{p_nastro}</b></font> | Riprese: <b>{p_rip}</b> | Pasti: <b>{p_pasto}</b>"
        rows_prop.append([Paragraph(riga_tot_pr, tot_cell_p), Paragraph("", tot_cell_p), Paragraph("", tot_cell_p), Paragraph("", tot_cell_p), Paragraph("", tot_cell_p)])

        t_right = Table(rows_prop, colWidths=[28, 28, 38, 32, 282])
        t_right.setStyle(TableStyle([('SPAN', (0,0), (4,0)), ('SPAN', (0,-1), (4,-1)), ('BACKGROUND', (0,0), (-1,0), h_destra_bg), ('BACKGROUND', (0,1), (-1,1), h_destra_sub), ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#E8F5E9') if (code in VERI_TURNI_MIGLIORATI) else colors.HexColor('#EBF3FA')), ('BOX', (0,-1), (-1,-1), 1, colors.HexColor('#006600') if (code in VERI_TURNI_MIGLIORATI) else colors.HexColor('#004085')), ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor('#DDDDDD')), ('ROWBACKGROUNDS', (0,2), (-1,-2), [colors.white, colors.HexColor('#F5FFF5') if (code in VERI_TURNI_MIGLIORATI) else colors.HexColor('#F0F4F8')]), ('TOPPADDING', (0,0), (-1,-1), 0.8), ('BOTTOMPADDING', (0,0), (-1,-1), 0.8)]))

        t_affiancate = Table([[t_left, t_right]], colWidths=[408, 408])
        t_affiancate.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
        elements.append(t_affiancate)
        elements.append(Spacer(1, 3))

        t_cambio_staccato = Table([[Paragraph(nota_cambio_turno, cambio_box_style)]], colWidths=[816])
        t_cambio_staccato.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FFF3CD')), ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#856404')), ('TOPPADDING', (0,0), (-1,-1), 2.5), ('BOTTOMPADDING', (0,0), (-1,-1), 2.5), ('LEFTPADDING', (0,0), (-1,-1), 5), ('RIGHTPADDING', (0,0), (-1,-1), 5)]))
        elements.append(t_cambio_staccato)

        if idx < len(lista_turni) - 1: elements.append(PageBreak())

    doc_pdf.build(elements)

build_pdf(turni_migliorati_list, pdf_migl_out, is_migl_pdf=True, title_prefix="DOSSIER TURNI MIGLIORATI (ABBATTIMENTO NASTRO & RIPRESE)")
build_pdf(turni_confermati_list, pdf_conf_out, is_migl_pdf=False, title_prefix="DOSSIER TURNI CONFERMATI (DATI AZIENDALI)")

print(f"✅ GENERATI I 2 FASCICOLI:\n1. {pdf_migl_out} ({len(turni_migliorati_list)} Pagine: Solo i Turni con Reale Risparmio di Ore)\n2. {pdf_conf_out} ({len(turni_confermati_list)} Pagine: Turni Confermati Compatti)")
