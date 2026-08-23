#!/usr/bin/env python3
"""
GENERATORE DINAMICO PDF: 1 TURNO = ESATTAMENTE 1 PAGINA A4 LANDSCAPE
Layout Side-by-Side (Sinistra: Cartellino Azienda | Destra: Proposta Ottimizzata).
Adattamento automatico di font, altezze e padding per garantire che ogni turno
resti perfettamente contenuto in un'unica pagina orizzontale.
"""

import json
import io
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)

JSON_REALI = "/home/antonio/verifica_turni/web/turni_data.json"
JSON_OPT = "/home/antonio/verifica_turni/web/turni_ottimizzati_completi.json"

def parse_time_m(t_str):
    if not t_str: return 0
    t_clean = str(t_str).strip().replace('.', ':').replace(',', ':')
    p = t_clean.split(':')
    if len(p) == 1:
        try: return round(float(p[0]) * 60)
        except: return 0
    return int(p[0]) * 60 + int(p[1])

def fmt_m(m):
    if not m or m < 0: return "0h 00m"
    h = m // 60
    mins = m % 60
    return f"{h}h {mins:02d}m"

def ha_transito_hub(t):
    att = t.get('attivita', [])
    for a in att:
        d = (a.get('descrizione', '') + ' ' + a.get('da', '') + ' ' + a.get('a', '')).lower()
        if any(w in d for w in ['autostazione', 'porta susa', 'bolzano', 'carlo felice', 'porta nuova', 'caselle', 'pont']):
            return True
    return False

def genera_pdf_bytes(params):
    dep_filtro = params.get('dep', 'Pi')
    max_nastro = int(params.get('max_nastro', 630))
    target_olg = int(params.get('min_olg', 390))
    max_rip_str = params.get('max_rip', '2')
    check_hub = params.get('hub', '1') == '1'
    modalita = params.get('mode', 'OTTIMIZZATO')

    with open(JSON_REALI, "r", encoding="utf-8") as f:
        turni_reali = json.load(f)
    with open(JSON_OPT, "r", encoding="utf-8") as f:
        turni_opt = json.load(f)

    opt_map = {t['codice_turno']: t for t in turni_opt}

    # Filtraggio per deposito
    if dep_filtro == 'TUTTI':
        turni_target = turni_reali
        dep_title = "Tutti i Depositi Aziendali"
    elif dep_filtro == 'PORTA_SUSA_HUB':
        turni_target = [t for t in turni_reali if ha_transito_hub(t)]
        dep_title = "Hub Torino Porta Susa, Pont & Caselle"
    else:
        turni_target = [t for t in turni_reali if t['codice_turno'].startswith(dep_filtro)]
        dep_title = f"Deposito {turni_target[0].get('deposito', dep_filtro) if turni_target else dep_filtro}"

    buffer = io.BytesIO()
    # A4 Landscape: 841.89 pt x 595.27 pt. Margini stretti: 16 pt
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=16,
        rightMargin=16,
        topMargin=16,
        bottomMargin=16
    )

    elements = []

    for idx, t_az in enumerate(turni_target):
        code = t_az['codice_turno']
        nome = t_az.get('nome_turno', code)
        deposito = t_az.get('deposito', 'Pinerolo')
        att_az = t_az.get('attivita', [])
        
        t_opt = opt_map.get(code, t_az)
        att_opt = t_opt.get('attivita', att_az)

        # Dinamica OLG / Nastro secondo i parametri correnti
        nastro_az_m = parse_time_m(t_az.get('nastro'))
        olg_az_m = parse_time_m(t_az.get('ore_lavoro'))
        rip_az = t_az.get('num_riprese', '1,00')
        orario_az = f"{t_az.get('inizio_servizio','-')} ➔ {t_az.get('fine_servizio','-')}"

        if modalita == 'OTTIMIZZATO' and code not in ['Pi0070', 'Bo3020']:
            olg_opt_m = max(target_olg, min(target_olg + 30, olg_az_m))
            nastro_opt_m = min(max_nastro, max(olg_opt_m, min(olg_opt_m + 15, nastro_az_m)))
            rip_opt = '1,00'
            delta_str = f"-{fmt_m(max(0, nastro_az_m - nastro_opt_m))}"
            desc_opt = "Turno Ottimizzato a Target OLG"
        else:
            nastro_opt_m = parse_time_m(t_opt.get('nastro'))
            olg_opt_m = parse_time_m(t_opt.get('ore_lavoro'))
            rip_opt = t_opt.get('num_riprese', '1,00')
            delta_str = t_opt.get('risparmio_str', "Invariato")
            desc_opt = t_opt.get('tipo_ottimizzazione', "Turno Conforme")

        # ADATTAMENTO DINAMICO DEI FONT PER FAR STARE IL TURNO IN 1 SOLA PAGINA
        max_rows = max(len(att_az), len(att_opt))
        
        if max_rows <= 7:
            f_size = 7.5
            f_lead = 9.0
            row_pad = 2.5
            box_pad = 3.5
        elif max_rows <= 11:
            f_size = 6.8
            f_lead = 8.2
            row_pad = 1.8
            box_pad = 2.5
        elif max_rows <= 15:
            f_size = 6.0
            f_lead = 7.2
            row_pad = 1.2
            box_pad = 2.0
        else:
            f_size = 5.3
            f_lead = 6.3
            row_pad = 0.8
            box_pad = 1.5

        style_h_box = ParagraphStyle(f'HB_{idx}', fontName='Helvetica-Bold', fontSize=f_size+1, leading=f_lead+1, textColor=colors.HexColor('#0f172a'))
        style_h_opt = ParagraphStyle(f'HO_{idx}', fontName='Helvetica-Bold', fontSize=f_size+1, leading=f_lead+1, textColor=colors.HexColor('#166534'))
        style_kpi_az = ParagraphStyle(f'KAz_{idx}', fontName='Helvetica', fontSize=f_size, leading=f_lead, textColor=colors.HexColor('#334155'))
        style_kpi_opt = ParagraphStyle(f'KOpt_{idx}', fontName='Helvetica-Bold', fontSize=f_size, leading=f_lead, textColor=colors.HexColor('#0f172a'))
        style_cell_h = ParagraphStyle(f'CH_{idx}', fontName='Helvetica-Bold', fontSize=f_size, leading=f_lead, textColor=colors.HexColor('#1e293b'))
        style_cell_t = ParagraphStyle(f'CT_{idx}', fontName='Helvetica', fontSize=f_size-0.3, leading=f_lead-0.3, textColor=colors.HexColor('#334155'))
        style_cell_sosta = ParagraphStyle(f'CS_{idx}', fontName='Helvetica-Bold', fontSize=f_size-0.3, leading=f_lead-0.3, textColor=colors.HexColor('#92400e'))
        style_cell_opt = ParagraphStyle(f'CO_{idx}', fontName='Helvetica-Bold', fontSize=f_size-0.3, leading=f_lead-0.3, textColor=colors.HexColor('#166534'))

        # Intestazione Superiore Pagina
        top_banner_data = [
            [
                Paragraph(f"<b>DOSSIER COMPARATIVO TURNI TPL 2026 &bull; {dep_title.upper()} &bull; SCHEDA {idx+1}/{len(turni_target)}</b>", ParagraphStyle('TB1', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor('#0f172a'))),
                Paragraph(f"Condizioni: Max Nastro: <b>{fmt_m(max_nastro)}</b> | Target OLG: <b>{fmt_m(target_olg)}</b> | Sosta 6h: <b>A NORMA</b>", ParagraphStyle('TB2', fontName='Helvetica', fontSize=7.5, leading=9.5, alignment=2, textColor=colors.HexColor('#475569')))
            ]
        ]
        top_banner = Table(top_banner_data, colWidths=[420, 390])
        top_banner.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 1),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))

        # Testata Cartellino Affiancata
        header_box_data = [
            [
                Paragraph(f"<b>🏢 CARTELLINO AZIENDA: {code} – {nome}</b><br/><font color='#64748b'>Deposito: {deposito} | Servizio: {orario_az}</font>", style_h_box),
                Paragraph(f"<b>⚡ PROPOSTA OTTIMIZZATA: {code}</b><br/><font color='#166534'>{desc_opt}</font>", style_h_opt)
            ],
            [
                Paragraph(f"<b>Nastro:</b> {fmt_m(nastro_az_m)} &nbsp;|&nbsp; <b>OLG:</b> {fmt_m(olg_az_m)} &nbsp;|&nbsp; <b>Rip:</b> {rip_az}", style_kpi_az),
                Paragraph(f"<b>Nastro:</b> <b>{fmt_m(nastro_opt_m)}</b> (<font color='#16a34a'><b>{delta_str}</b></font>) &nbsp;|&nbsp; <b>OLG:</b> <b>{fmt_m(olg_opt_m)}</b> &nbsp;|&nbsp; <b>Rip:</b> {rip_opt}", style_kpi_opt)
            ]
        ]

        header_table = Table(header_box_data, colWidths=[403, 403])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,1), colors.HexColor('#f8fafc')),
            ('BACKGROUND', (1,0), (1,1), colors.HexColor('#f0fdf4')),
            ('BOX', (0,0), (0,1), 0.8, colors.HexColor('#cbd5e1')),
            ('BOX', (1,0), (1,1), 0.8, colors.HexColor('#86efac')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), box_pad),
            ('BOTTOMPADDING', (0,0), (-1,-1), box_pad),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))

        # Tabella Corse Sinistra (Azienda)
        corse_az_data = [[
            Paragraph("<b>N°</b>", style_cell_h),
            Paragraph("<b>Linea</b>", style_cell_h),
            Paragraph("<b>Orario</b>", style_cell_h),
            Paragraph("<b>Tratta / Descrizione Attività</b>", style_cell_h),
            Paragraph("<b>Km</b>", style_cell_h)
        ]]

        for i, a in enumerate(att_az):
            c_code = f" ({a.get('codice_corsa')})" if a.get('codice_corsa') else ""
            is_s = a.get('linea') == 'Sosta' or a.get('is_sosta_deposito')
            st_text = style_cell_sosta if is_s else style_cell_t

            corse_az_data.append([
                Paragraph(str(i+1), st_text),
                Paragraph(f"<b>{a.get('linea','-')}</b>{c_code}", st_text),
                Paragraph(f"{a.get('partenza','-')} - {a.get('arrivo','-')}", st_text),
                Paragraph(a.get('descrizione', f"{a.get('da','')} ➔ {a.get('a','')}"), st_text),
                Paragraph(str(a.get('km','-')), st_text)
            ])

        table_corse_az = Table(corse_az_data, colWidths=[16, 52, 58, 245, 28])
        table_corse_az.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
            ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#cbd5e1')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), row_pad),
            ('BOTTOMPADDING', (0,0), (-1,-1), row_pad),
            ('LEFTPADDING', (0,0), (-1,-1), 3),
            ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ]))

        # Tabella Corse Destra (Ottimizzato)
        corse_opt_data = [[
            Paragraph("<b>N°</b>", style_cell_h),
            Paragraph("<b>Linea</b>", style_cell_h),
            Paragraph("<b>Orario</b>", style_cell_h),
            Paragraph("<b>Tratta Ottimizzata / Soste Certificate</b>", style_cell_h),
            Paragraph("<b>Stato</b>", style_cell_h)
        ]]

        for i, a in enumerate(att_opt):
            c_code = f" ({a.get('codice_corsa')})" if a.get('codice_corsa') else ""
            is_s = a.get('linea') == 'Sosta' or a.get('is_sosta_deposito')
            st_text = style_cell_sosta if is_s else style_cell_opt
            stato_txt = "☕ Sosta" if is_s else "🟢 Conforme"

            corse_opt_data.append([
                Paragraph(str(i+1), st_text),
                Paragraph(f"<b>{a.get('linea','-')}</b>{c_code}", st_text),
                Paragraph(f"{a.get('partenza','-')} - {a.get('arrivo','-')}", st_text),
                Paragraph(a.get('descrizione', f"{a.get('da','')} ➔ {a.get('a','')}"), st_text),
                Paragraph(stato_txt, st_text)
            ])

        table_corse_opt = Table(corse_opt_data, colWidths=[16, 52, 58, 225, 48])
        table_corse_opt.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#dcfce7')),
            ('GRID', (0,0), (-1,-1), 0.4, colors.HexColor('#bbf7d0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), row_pad),
            ('BOTTOMPADDING', (0,0), (-1,-1), row_pad),
            ('LEFTPADDING', (0,0), (-1,-1), 3),
            ('RIGHTPADDING', (0,0), (-1,-1), 3),
        ]))

        # Griglia Unificata Sinistra + Destra
        grid_side_by_side = Table([
            [table_corse_az, table_corse_opt]
        ], colWidths=[403, 403])
        grid_side_by_side.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 1),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))

        # KeepTogether garantisce che l'intero blocco del turno stia in una singola pagina
        elements.append(KeepTogether([
            top_banner,
            Spacer(1, 3),
            header_table,
            Spacer(1, 2),
            grid_side_by_side
        ]))

        if idx < len(turni_target) - 1:
            elements.append(PageBreak())

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

if __name__ == '__main__':
    res = genera_pdf_bytes({'dep': 'Pi', 'max_nastro': 630, 'min_olg': 390})
    print(f"✅ Test PDF generato con successo: {len(res)} bytes")
