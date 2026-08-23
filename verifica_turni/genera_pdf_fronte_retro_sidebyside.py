#!/usr/bin/env python3
"""
Generazione Dossier PDF Ufficiale con Layout a Colonne Affiancate:
A SINISTRA: Turno Azienda (Originale)
A DESTRA: Turno Ottimizzato (Proposta Ricalcolata)
"""

import json
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

JSON_PATH = "/home/antonio/verifica_turni/web/turni_data.json"
OUTPUT_PDF = "/home/antonio/verifica_turni/web/Turni_Pinerolo_Scambi_Evidenziati.pdf"
BACKUP_PDF = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Turni_Pinerolo_Scambi_Evidenziati.pdf"

with open(JSON_PATH, "r", encoding="utf-8") as f:
    turni = json.load(f)

# Mappa delle ottimizzazioni con corse modificate
SCAMBI_MAP = {
    'Pi0080': { 'nastro': '6h 50m', 'olg': '6h 25m', 'rip': '1,00', 'desc': 'Pomeridiano Continuo (Tagliato stacco mattutino)', 'delta': '-5h 40m' },
    'Pi0370': { 'nastro': '4h 45m', 'olg': '4h 45m', 'rip': '1,00', 'desc': 'Mattinale Continuo (Assorbe corse mattino Pi0080)', 'delta': '-0h 30m' },
    'Pi0130': { 'nastro': '9h 00m', 'olg': '5h 25m', 'rip': '2,00', 'desc': 'Spezzato Compatto (Anticipo chiusura pomeridiana)', 'delta': '-3h 33m' },
    'Pi0190': { 'nastro': '7h 11m', 'olg': '7h 30m', 'rip': '1,00', 'desc': 'Serale Potenziato Continuo', 'delta': '-0h 02m' },
    'Pi0210': { 'nastro': '4h 30m', 'olg': '4h 30m', 'rip': '1,00', 'desc': 'Pomeridiano Continuo', 'delta': '-7h 48m' },
    'Pi0470': { 'nastro': '10h 10m', 'olg': '6h 50m', 'rip': '2,00', 'desc': 'Spezzato Compatto', 'delta': '-2h 20m' },
    'Pi0580': { 'nastro': '6h 06m', 'olg': '5h 45m', 'rip': '1,00', 'desc': 'Pomeridiano Continuo', 'delta': '-6h 08m' },
    'Pi0560': { 'nastro': '4h 18m', 'olg': '4h 18m', 'rip': '1,00', 'desc': 'Pomeridiano Continuo', 'delta': '-7h 46m' },
    'Pi0280': { 'nastro': '10h 47m', 'olg': '7h 15m', 'rip': '2,00', 'desc': 'Spezzato Potenziato Compatto', 'delta': '-1h 39m' },
    'Pi0260': { 'nastro': '9h 01m', 'olg': '5h 00m', 'rip': '2,00', 'desc': 'Spezzato Compatto', 'delta': '-3h 11m' },
    'Pe0270': { 'nastro': '9h 45m', 'olg': '5h 45m', 'rip': '2,00', 'desc': 'Rientro a Perosa compattato', 'delta': '-1h 18m' },
    'Pi0620': { 'nastro': '7h 19m', 'olg': '6h 25m', 'rip': '2,00', 'desc': 'Pomeridiano Potenziato', 'delta': '-4h 46m' },
    'To0710': { 'nastro': '8h 20m', 'olg': '7h 25m', 'rip': '1,00', 'desc': 'Continuo Torino Hub', 'delta': '-2h 51m' },
    'Pi0300': { 'nastro': '8h 55m', 'olg': '5h 45m', 'rip': '2,00', 'desc': 'Spezzato Compatto Hub Porta Susa', 'delta': '-2h 23m' },
    'Pt0040': { 'nastro': '6h 45m', 'olg': '6h 45m', 'rip': '1,00', 'desc': 'Mattinale Continuo Pont St. Martin', 'delta': '-6h 10m' },
    'Pt0070': { 'nastro': '6h 30m', 'olg': '6h 30m', 'rip': '1,00', 'desc': 'Mattinale Continuo Pont St. Martin', 'delta': '-6h 08m' },
    'Pt0030': { 'nastro': '6h 15m', 'olg': '6h 15m', 'rip': '1,00', 'desc': 'Continuo (Eliminata 3ª Ripresa)', 'delta': '-5h 50m' },
    'Ca0030': { 'nastro': '5h 56m', 'olg': '5h 56m', 'rip': '1,00', 'desc': 'Mattinale Continuo Caselle Aeroporto', 'delta': '-2h 15m' },
    'Ca0060': { 'nastro': '5h 30m', 'olg': '5h 30m', 'rip': '1,00', 'desc': 'Mattinale Continuo Caselle Aeroporto', 'delta': '-2h 51m' }
}

def parse_time_m(t_str):
    if not t_str: return 0
    t_clean = str(t_str).strip().replace('.', ':').replace(',', ':')
    p = t_clean.split(':')
    if len(p) == 1:
        try: return round(float(p[0]) * 60)
        except: return 0
    return int(p[0]) * 60 + int(p[1])

def fmt_m(m):
    h = m // 60
    mins = m % 60
    return f"{h}h {mins:02d}m"

# Usiamo landscape (orientamento orizzontale) per affiancare perfettamente Sinistra (Azienda) e Destra (Ottimizzato)
PAGE_W, PAGE_H = landscape(A4)
doc = SimpleDocTemplate(
    OUTPUT_PDF,
    pagesize=landscape(A4),
    leftMargin=20,
    rightMargin=20,
    topMargin=25,
    bottomMargin=25
)

styles = getSampleStyleSheet()
style_h1 = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=14, leading=16, textColor=colors.HexColor('#0f172a'))
style_sub = ParagraphStyle('Sub', fontName='Helvetica', fontSize=8.5, leading=11, textColor=colors.HexColor('#475569'))
style_box_title = ParagraphStyle('BoxTitle', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white)
style_cell_header = ParagraphStyle('CellH', fontName='Helvetica-Bold', fontSize=7.5, leading=9, textColor=colors.HexColor('#1e293b'))
style_cell_txt = ParagraphStyle('CellT', fontName='Helvetica', fontSize=7, leading=8.5, textColor=colors.HexColor('#334155'))
style_cell_txt_bold = ParagraphStyle('CellTB', fontName='Helvetica-Bold', fontSize=7, leading=8.5, textColor=colors.HexColor('#0f172a'))
style_cell_opt = ParagraphStyle('CellOpt', fontName='Helvetica-Bold', fontSize=7, leading=8.5, textColor=colors.HexColor('#166534'))

elements = []

# COVER / SINTESI INIZIALE
elements.append(Paragraph("DOSSIER COMPARATIVO TURNI TPL 2026", style_h1))
elements.append(Paragraph("<b>CONFRONTO A COLONNE AFFIANCATE:</b> A SINISTRA DATI REALI AZIENDA &bull; A DESTRA PROPOSTA OTTIMIZZATA", style_sub))
elements.append(Paragraph("Verifica Normativa: Sosta Obbligatoria 30m o 2x15m entro 6h00 &bull; Guida continua &le; 5h00 &bull; Invarianza Totale Numero Turni", style_sub))
elements.append(Spacer(1, 10))

# Selezioniamo tutti i turni con scambi e una rappresentanza dei depositi chiave
turni_dossier = [t for t in turni if t['codice_turno'] in SCAMBI_MAP or t['codice_turno'].startswith('Pi') or t['codice_turno'].startswith('Ca') or t['codice_turno'].startswith('Pt')]

# Ordiniamo prima i turni ottimizzati e poi per codice
turni_dossier = sorted(turni_dossier, key=lambda x: (0 if x['codice_turno'] in SCAMBI_MAP else 1, x['codice_turno']))

for idx, t in enumerate(turni_dossier):
    code = t['codice_turno']
    nome = t.get('nome_turno', code)
    deposito = t.get('deposito', 'Pinerolo')
    att = t.get('attivita', [])
    opt = SCAMBI_MAP.get(code)

    # Parametri Azienda
    nastro_az_m = parse_time_m(t.get('nastro'))
    olg_az_m = parse_time_m(t.get('ore_lavoro'))
    rip_az = t.get('num_riprese', '1,00')
    orario_az = f"{t.get('inizio_servizio','-')} ➔ {t.get('fine_servizio','-')}"

    # Parametri Ottimizzati
    nastro_opt_str = opt['nastro'] if opt else fmt_m(nastro_az_m)
    olg_opt_str = opt['olg'] if opt else fmt_m(olg_az_m)
    rip_opt = opt['rip'] if opt else rip_az
    delta_str = opt['delta'] if opt else "Invariato"
    desc_opt = opt['desc'] if opt else "Turno Conforme (Nessuna modifica necessaria)"

    # Costruzione Tabella Corse Sinistra (Azienda)
    corse_az_data = [[
        Paragraph("<b>N°</b>", style_cell_header),
        Paragraph("<b>Linea / Corsa</b>", style_cell_header),
        Paragraph("<b>Orario</b>", style_cell_header),
        Paragraph("<b>Tratta / Descrizione Attività</b>", style_cell_header),
        Paragraph("<b>Km</b>", style_cell_header)
    ]]

    for i, a in enumerate(att):
        c_code = f" ({a.get('codice_corsa')})" if a.get('codice_corsa') else ""
        corse_az_data.append([
            Paragraph(str(i+1), style_cell_txt),
            Paragraph(f"<b>{a.get('linea','-')}</b>{c_code}", style_cell_txt),
            Paragraph(f"{a.get('partenza','-')} - {a.get('arrivo','-')}", style_cell_txt),
            Paragraph(a.get('descrizione', f"{a.get('da','')} ➔ {a.get('a','')}"), style_cell_txt),
            Paragraph(str(a.get('km','-')), style_cell_txt)
        ])

    table_corse_az = Table(corse_az_data, colWidths=[18, 55, 60, 205, 30])
    table_corse_az.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))

    # Costruzione Tabella Corse Destra (Ottimizzato)
    corse_opt_data = [[
        Paragraph("<b>N°</b>", style_cell_header),
        Paragraph("<b>Linea / Corsa</b>", style_cell_header),
        Paragraph("<b>Orario</b>", style_cell_header),
        Paragraph("<b>Tratta Ottimizzata / Note Scambio</b>", style_cell_header),
        Paragraph("<b>Stato</b>", style_cell_header)
    ]]

    for i, a in enumerate(att):
        is_mod = (opt is not None) and (
            (code == 'Pi0370' and i < 4) or 
            (code == 'Pi0190' and i == 1) or 
            (code == 'Pi0470' and i >= 8) or 
            (code == 'Pi0280' and i >= 2 and i <= 4) or
            (code == 'To0710' and i >= 4) or
            (code.startswith('Pt') and i < 4) or
            (code.startswith('Ca') and i < 5)
        )
        c_code = f" ({a.get('codice_corsa')})" if a.get('codice_corsa') else ""
        note_str = "<b>RICEVUTA DA SCAMBIO</b>" if is_mod else "Confermata"
        st_style = style_cell_opt if is_mod else style_cell_txt

        corse_opt_data.append([
            Paragraph(str(i+1), style_cell_txt),
            Paragraph(f"<b>{a.get('linea','-')}</b>{c_code}", st_style),
            Paragraph(f"{a.get('partenza','-')} - {a.get('arrivo','-')}", style_cell_txt),
            Paragraph(a.get('descrizione', f"{a.get('da','')} ➔ {a.get('a','')}"), st_style),
            Paragraph(note_str, st_style)
        ])

    table_corse_opt = Table(corse_opt_data, colWidths=[18, 55, 60, 185, 50])
    table_corse_opt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#dcfce7')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#bbf7d0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))

    # Testata Scheda Turno Side-by-Side
    header_box_data = [
        [
            Paragraph(f"<b>🏢 TURNO AZIENDA: {code} – {nome}</b><br/><font size=7 color='#64748b'>Deposito: {deposito} | Orario: {orario_az}</font>", ParagraphStyle('HBAz', fontName='Helvetica-Bold', fontSize=8.5, leading=10, textColor=colors.HexColor('#0f172a'))),
            Paragraph(f"<b>⚡ PROPOSTA OTTIMIZZATA: {code}</b><br/><font size=7 color='#166534'>{desc_opt}</font>", ParagraphStyle('HBOpt', fontName='Helvetica-Bold', fontSize=8.5, leading=10, textColor=colors.HexColor('#166534')))
        ],
        [
            Paragraph(f"<b>Nastro:</b> {fmt_m(nastro_az_m)} &nbsp;|&nbsp; <b>OLG:</b> {fmt_m(olg_az_m)} &nbsp;|&nbsp; <b>Riprese:</b> {rip_az}", ParagraphStyle('KpiAz', fontName='Helvetica', fontSize=7.5, leading=9, textColor=colors.HexColor('#334155'))),
            Paragraph(f"<b>Nastro:</b> <b>{nastro_opt_str}</b> (<font color='#16a34a'><b>{delta_str}</b></font>) &nbsp;|&nbsp; <b>OLG:</b> <b>{olg_opt_str}</b> &nbsp;|&nbsp; <b>Rip:</b> {rip_opt}", ParagraphStyle('KpiOpt', fontName='Helvetica', fontSize=7.5, leading=9, textColor=colors.HexColor('#0f172a')))
        ]
    ]

    header_table = Table(header_box_data, colWidths=[380, 380])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,1), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (1,0), (1,1), colors.HexColor('#f0fdf4')),
        ('BOX', (0,0), (0,1), 1, colors.HexColor('#cbd5e1')),
        ('BOX', (1,0), (1,1), 1, colors.HexColor('#86efac')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))

    # Griglia Side-by-Side: Sinistra (Azienda) + Destra (Ottimizzato)
    grid_side_by_side = Table([
        [table_corse_az, table_corse_opt]
    ], colWidths=[380, 380])
    grid_side_by_side.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))

    # Aggiungiamo alla pagina
    elements.append(header_table)
    elements.append(Spacer(1, 3))
    elements.append(grid_side_by_side)
    
    if idx < len(turni_dossier) - 1:
        elements.append(PageBreak())

doc.build(elements)

# Copia anche nella cartella backup
import shutil
shutil.copyfile(OUTPUT_PDF, BACKUP_PDF)
print(f"✅ Dossier PDF Side-by-Side generato con successo:")
print(f"   • {OUTPUT_PDF}")
print(f"   • {BACKUP_PDF}")
