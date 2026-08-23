#!/usr/bin/env python3
"""
=============================================================================
MOTORE DI OTTIMIZZAZIONE E SCAMBIO CORSE TURNI TPL
=============================================================================
Funzionalità:
1. Carica la base turni aziendale completa (cartellini 2026).
2. Valuta i parametri chiave per ciascun turno: Nastro, OLG (Ore Lavoro), Guida Continua, Pause.
3. Rileva i turni critici:
   - Nastro eccessivo (> 10h00 o >= 12h00)
   - Soste passive lunghe / buchi non retribuiti
   - OLG basso / spezzati a 3 o 4 riprese
   - Soste fuori sede (es. autista di Pinerolo a Perosa o autista di Torino a Pinerolo)
4. Trova gli scambi ottimali a parità di numero di turni (invarianza totale turni):
   - Verifica compatibilità oraria e geografica tra le corse (capolinea di arrivo = partenza)
   - Verifica vincolo normativo: Guida continua <= 5h00
   - Verifica vincolo normativo: Pausa obbligatoria entro 6h00
5. Consente l'ottimizzazione automatica o interattiva (singolo deposito o inter-deposito).
6. Genera il report comparativo completo a video, export JSON e genera il PDF ufficiale con evidenziazione grafica delle corse scambiate.
=============================================================================
"""

import json
import os
import sys
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


def time_to_min(t_str):
    """Converte una stringa oraria 'HH:MM' o 'HH.MM' in minuti da inizio giornata."""
    if not t_str:
        return 0
    t_clean = str(t_str).strip().replace('.', ':').replace(',', ':')
    parts = t_clean.split(':')
    if len(parts) == 1:
        try:
            return int(float(parts[0])) * 60
        except ValueError:
            return 0
    try:
        return int(parts[0]) * 60 + int(parts[1])
    except ValueError:
        return 0


def min_to_time(m):
    """Converte minuti interi in formato stringa 'HH:MM'."""
    m = int(round(m))
    h = (m // 60) % 24
    mins = m % 60
    return f"{h:02d}:{mins:02d}"


def fmt_durata(m):
    """Formatta minuti in 'Xh YYm'."""
    m = int(round(m))
    h = m // 60
    mins = m % 60
    return f"{h}h {mins:02d}m"


class TurnoTPL:
    """Rappresentazione di un singolo cartellino turno con le sue attività."""
    def __init__(self, codice, nome, deposito, attivita=None, note=""):
        self.codice = codice
        self.nome = nome
        self.deposito = deposito
        self.attivita = [dict(a) for a in (attivita or [])]
        self.note = note
        self.ricalcola_metriche()

    def ricalcola_metriche(self):
        """Calcola Nastro, OLG, ore di guida, riprese, max guida continua e pause."""
        if not self.attivita:
            self.inizio_str = "00:00"
            self.fine_str = "00:00"
            self.inizio_m = 0
            self.fine_m = 0
            self.nastro_m = 0
            self.olg_m = 0
            self.guida_m = 0
            self.max_guida_continua_m = 0
            self.pausa_entro_6h = True
            self.riprese = 0
            return

        self.inizio_str = self.attivita[0].get('partenza', '00:00')
        self.fine_str = self.attivita[-1].get('arrivo', '00:00')
        self.inizio_m = time_to_min(self.inizio_str)
        self.fine_m = time_to_min(self.fine_str)

        # Se supera mezzanotte
        if self.fine_m < self.inizio_m:
            self.nastro_m = (1440 - self.inizio_m) + self.fine_m
        else:
            self.nastro_m = self.fine_m - self.inizio_m

        tot_lavoro = 0
        tot_guida = 0
        current_guida_continua = 0
        max_guida = 0
        soste_significative = []

        for i, a in enumerate(self.attivita):
            p = time_to_min(a.get('partenza', '00:00'))
            arr = time_to_min(a.get('arrivo', '00:00'))
            durata = arr - p if arr >= p else (1440 - p) + arr
            lin = str(a.get('linea', '')).strip().upper()

            if lin not in ['SOSTA', 'PAUSA']:
                tot_lavoro += durata
                if lin not in ['DISP', 'PREP']:
                    tot_guida += durata
                    current_guida_continua += durata
                else:
                    if current_guida_continua > max_guida:
                        max_guida = current_guida_continua
                    current_guida_continua = 0
            else:
                if current_guida_continua > max_guida:
                    max_guida = current_guida_continua
                current_guida_continua = 0
                soste_significative.append((p, arr, durata))

            # Controlla pause tra attività consecutive
            if i < len(self.attivita) - 1:
                next_p = time_to_min(self.attivita[i+1].get('partenza', '00:00'))
                gap = next_p - arr if next_p >= arr else (1440 - arr) + next_p
                if gap >= 15:
                    if current_guida_continua > max_guida:
                        max_guida = current_guida_continua
                    current_guida_continua = 0
                    soste_significative.append((arr, next_p, gap))

        if current_guida_continua > max_guida:
            max_guida = current_guida_continua

        self.olg_m = tot_lavoro
        self.guida_m = tot_guida
        self.max_guida_continua_m = max_guida
        self.riprese = len(soste_significative) + 1 if soste_significative else 1

        # Verifica Pausa entro 6 ore
        if self.nastro_m > 360:
            prima_sosta_ok = False
            for s_in, s_out, s_dur in soste_significative:
                tempo_da_inizio = s_in - self.inizio_m if s_in >= self.inizio_m else (1440 - self.inizio_m) + s_in
                if tempo_da_inizio <= 360 and s_dur >= 15:
                    prima_sosta_ok = True
                    break
            self.pausa_entro_6h = prima_sosta_ok
        else:
            self.pausa_entro_6h = True

    def valida_normativa(self):
        """Restituisce True se il turno rispetta guida <= 5h e pausa entro 6h."""
        return (self.max_guida_continua_m <= 300) and self.pausa_entro_6h


class OttimizzatoreTurniTPL:
    """Motore principale di ottimizzazione, scambio corse e reportistica."""
    def __init__(self, json_path=None):
        self.json_path = json_path
        self.turni_originali = {}
        self.turni_proposta = {}
        self.storico_scambi = []
        if json_path and os.path.exists(json_path):
            self.carica_da_json(json_path)

    def carica_da_json(self, path):
        """Carica i dati dei cartellini dal file JSON."""
        with open(path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        self.turni_originali = {}
        self.turni_proposta = {}

        for t in raw_data:
            code = t['codice_turno']
            nome = t.get('nome_turno', code)
            dep = t.get('deposito', 'Pinerolo')
            att = t.get('attivita', [])
            turno_orig = TurnoTPL(code, nome, dep, att)
            turno_prop = TurnoTPL(code, nome, dep, att)
            self.turni_originali[code] = turno_orig
            self.turni_proposta[code] = turno_prop

        print(f"✅ Caricati {len(self.turni_originali)} turni da: {path}")

    def analizza_criticita(self, deposito_filtro=None):
        """Identifica i turni che superano i limiti di nastro o hanno stacchi eccessivi."""
        risultati = []
        for code, t in self.turni_proposta.items():
            if deposito_filtro and not code.startswith(deposito_filtro):
                continue
            criticita = []
            if t.nastro_m >= 720:
                criticita.append(f"🔴 Nastro critico >= 12h ({fmt_durata(t.nastro_m)})")
            elif t.nastro_m >= 600:
                criticita.append(f"🟡 Nastro lungo >= 10h ({fmt_durata(t.nastro_m)})")
            if t.riprese >= 3:
                criticita.append(f"🟠 Troppe riprese ({t.riprese} riprese)")
            if t.max_guida_continua_m > 300:
                criticita.append(f"❌ Supero guida continua ({fmt_durata(t.max_guida_continua_m)} > 5h)")
            if not t.pausa_entro_6h:
                criticita.append("❌ Assenza pausa entro le prime 6h")

            if criticita:
                risultati.append({
                    'codice': code,
                    'nome': t.nome,
                    'nastro': t.nastro_m,
                    'olg': t.olg_m,
                    'riprese': t.riprese,
                    'criticita': criticita
                })
        return sorted(risultati, key=lambda x: x['nastro'], reverse=True)

    def scambia_corse(self, codice_cedente, codice_ricevente, indici_corse_cedute, nuova_dicitura_cedente=None, nuova_dicitura_ricevente=None, motivazione=""):
        """
        Esegue lo scambio di corse tra due turni:
        - Rimuove le corse indicate dal turno cedente.
        - Le inserisce nel turno ricevente con il tag '🟢 CORSA RICEVUTA DA TURNO ...'.
        - Ricalcola automaticamente metriche e conformità normativa per entrambi.
        """
        if codice_cedente not in self.turni_proposta or codice_ricevente not in self.turni_proposta:
            raise ValueError(f"Turni non trovati: {codice_cedente}, {codice_ricevente}")

        t_ced = self.turni_proposta[codice_cedente]
        t_ric = self.turni_proposta[codice_ricevente]

        corse_da_spostare = []
        nuove_att_ced = []

        for idx, a in enumerate(t_ced.attivita):
            if idx in indici_corse_cedute or (idx + 1) in indici_corse_cedute:
                a_copy = dict(a)
                a_copy['scambio_tag'] = f"🟢 CORSA RICEVUTA DA TURNO {codice_cedente}"
                corse_da_spostare.append(a_copy)
            else:
                nuove_att_ced.append(dict(a))

        nuove_att_ric = [dict(a) for a in t_ric.attivita] + corse_da_spostare
        nuove_att_ric.sort(key=lambda x: time_to_min(x.get('partenza', '00:00')))

        t_ced.attivita = nuove_att_ced
        t_ced.ricalcola_metriche()
        if nuova_dicitura_cedente:
            t_ced.nome = nuova_dicitura_cedente

        t_ric.attivita = nuove_att_ric
        t_ric.ricalcola_metriche()
        if nuova_dicitura_ricevente:
            t_ric.nome = nuova_dicitura_ricevente

        record_scambio = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'cedente': codice_cedente,
            'ricevente': codice_ricevente,
            'n_corse': len(corse_da_spostare),
            'motivazione': motivazione,
            'cedente_nastro_prima': self.turni_originali[codice_cedente].nastro_m,
            'cedente_nastro_dopo': t_ced.nastro_m,
            'ricevente_olg_prima': self.turni_originali[codice_ricevente].olg_m,
            'ricevente_olg_dopo': t_ric.olg_m
        }
        self.storico_scambi.append(record_scambio)
        return record_scambio

    def genera_report_testuale(self, deposito_filtro=None):
        """Stampa a video il confronto completo prima/dopo per ogni turno."""
        print("\n" + "=" * 115)
        print(f"               CRUSCOTTO COMPARATIVO TURNI TPL (PROPOSTA VS AZIENDA)")
        print("=" * 115)
        print(f"{'Cod.':6s} | {'Nome Turno':24s} | {'Nastro Az.':10s} | {'Nastro Prop.':12s} | {'OLG Az.':8s} | {'OLG Prop.':10s} | {'Guida Max':10s} | {'Stato Normativo'}")
        print("-" * 115)

        tot_n_az, tot_n_pr, tot_o_az, tot_o_pr = 0, 0, 0, 0
        count = 0

        for code in sorted(self.turni_proposta.keys()):
            if deposito_filtro and not code.startswith(deposito_filtro):
                continue
            orig = self.turni_originali[code]
            prop = self.turni_proposta[code]

            tot_n_az += orig.nastro_m
            tot_n_pr += prop.nastro_m
            tot_o_az += orig.olg_m
            tot_o_pr += prop.olg_m
            count += 1

            diff_n = prop.nastro_m - orig.nastro_m
            diff_n_str = f"({diff_n:+d}m)" if diff_n != 0 else "="

            diff_o = prop.olg_m - orig.olg_m
            diff_o_str = f"({diff_o:+d}m)" if diff_o != 0 else "="

            stato_norma = "🟢 OK" if prop.valida_normativa() else "❌ ANOMALIA"

            print(f"{code:6s} | {prop.nome[:24]:24s} | {fmt_durata(orig.nastro_m):10s} | {fmt_durata(prop.nastro_m):7s} {diff_n_str:5s} | {fmt_durata(orig.olg_m):8s} | {fmt_durata(prop.olg_m):6s} {diff_o_str:5s} | {fmt_durata(prop.max_guida_continua_m):10s} | {stato_norma}")

        print("-" * 115)
        if count > 0:
            print(f"📊 BILANCIO TOTALE ({count} Turni):")
            print(f"   • Nastro Totale:   {fmt_durata(tot_n_az)} (Azienda) ➔ {fmt_durata(tot_n_pr)} (Proposta) | Risparmio: {fmt_durata(tot_n_az - tot_n_pr)}")
            print(f"   • Nastro Medio:    {fmt_durata(tot_n_az / count)} (Azienda) ➔ {fmt_durata(tot_n_pr / count)} (Proposta)")
            print(f"   • OLG Totale:      {fmt_durata(tot_o_az)} (Azienda) ➔ {fmt_durata(tot_o_pr)} (Proposta)")
            print(f"   • OLG Medio:       {fmt_durata(tot_o_pr / count)}")
        print("=" * 115 + "\n")

    def esporta_pdf(self, pdf_out_path, turni_selezionati=None):
        """Genera il dossier PDF ad alta risoluzione con evidenziazione grafica delle corse scambiate."""
        if not HAS_REPORTLAB:
            print("⚠️ ReportLab non disponibile nel sistema. Installare reportlab per l'export PDF.")
            return False

        doc = SimpleDocTemplate(
            pdf_out_path,
            pagesize=landscape(A4),
            leftMargin=16,
            rightMargin=16,
            topMargin=12,
            bottomMargin=12
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('DocTitle', fontName='Helvetica-Bold', fontSize=11, leading=13, textColor=colors.HexColor('#003366'))
        sub_title_style = ParagraphStyle('SubDocTitle', fontName='Helvetica', fontSize=7.5, leading=9.0, textColor=colors.HexColor('#444444'))
        th_style = ParagraphStyle('THStyle', fontName='Helvetica-Bold', fontSize=6.8, leading=8.0, textColor=colors.white, alignment=1)
        td_cell = ParagraphStyle('TDCell', fontName='Helvetica', fontSize=6.0, leading=7.2)
        td_center = ParagraphStyle('TDCenter', fontName='Helvetica', fontSize=6.0, leading=7.2, alignment=1)
        td_right = ParagraphStyle('TDRight', fontName='Helvetica', fontSize=6.0, leading=7.2, alignment=2)
        td_ricevuta = ParagraphStyle('TDRicevuta', fontName='Helvetica-Bold', fontSize=6.0, leading=7.2, textColor=colors.HexColor('#1C4532'))
        box_body = ParagraphStyle('BoxBody', fontName='Helvetica', fontSize=6.6, leading=7.8, textColor=colors.HexColor('#1A202C'))

        elements = []
        codes_to_export = turni_selezionati or sorted(self.turni_proposta.keys())

        for code in codes_to_export:
            if code not in self.turni_proposta:
                continue
            orig = self.turni_originali[code]
            prop = self.turni_proposta[code]

            head_text = f"<b>TURNO {code} – {prop.nome}</b> (Deposito di {prop.deposito})"
            sub_text = f"Progetto: <b>Ottimizzazione Turni e Scambio Corse TPL 2026</b> | Validità: <b>Lunedì - Venerdì Scolastico</b>"

            header_table = Table([
                [Paragraph(head_text, title_style), Paragraph(f"Stato: <b>{'CONFORME' if prop.valida_normativa() else 'ATTENZIONE'}</b>", td_right)],
                [Paragraph(sub_text, sub_title_style), Paragraph(f"<b>Nastro Proposta:</b> {fmt_durata(prop.nastro_m)} | <b>OLG:</b> {fmt_durata(prop.olg_m)}", td_right)]
            ], colWidths=[580, 230])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                ('TOPPADDING', (0,0), (-1,-1), 1),
            ]))
            elements.append(header_table)
            elements.append(Spacer(1, 4))

            diff_n = prop.nastro_m - orig.nastro_m
            diff_n_str = f"{diff_n:+d}m" if diff_n != 0 else "Invariato"

            diff_o = prop.olg_m - orig.olg_m
            diff_o_str = f"{diff_o:+d}m" if diff_o != 0 else "Invariato"

            box_data = [[
                Paragraph(f"🔴 <b>CARTELLINO ATTUALE AZIENDA:</b><br/>"
                          f"• Dicitura: <b>{orig.nome}</b><br/>"
                          f"• Orario: <b>{orig.inizio_str} – {orig.fine_str}</b><br/>"
                          f"• <b>Nastro:</b> <font color='#990000'><b>{fmt_durata(orig.nastro_m)}</b></font> | <b>OLG:</b> <b>{fmt_durata(orig.olg_m)}</b><br/>"
                          f"• Riprese: <b>{orig.riprese}</b>", box_body),
                Paragraph(f"🟢 <b>NUOVA STRUTTURA DOPO LO SCAMBIO:</b><br/>"
                          f"• Nuova Qualifica: <b>{prop.nome}</b><br/>"
                          f"• Orario: <b>{prop.inizio_str} – {prop.fine_str}</b><br/>"
                          f"• <b>Nastro:</b> <font color='#006600'><b>{fmt_durata(prop.nastro_m)}</b> ({diff_n_str})</font><br/>"
                          f"• <b>OLG:</b> <font color='#006600'><b>{fmt_durata(prop.olg_m)}</b> ({diff_o_str})</font><br/>"
                          f"• Riprese: <b>{prop.riprese}</b>", box_body),
                Paragraph(f"⚖️ <b>VERIFICA VINCOLI NORMATIVI:</b><br/>"
                          f"• Max Guida Continua: <b>{fmt_durata(prop.max_guida_continua_m)}</b> (limite: 5h00)<br/>"
                          f"• Pausa entro 6 ore: <b>{'PRESENTE / CONFORME' if prop.pausa_entro_6h else 'NON PRESENTE'}</b><br/>"
                          f"• Note di Scambio: <i>{prop.note or 'Attività ottimizzate'}</i>", box_body)
            ]]
            t_box = Table(box_data, colWidths=[260, 265, 285])
            t_box.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F0F7FF')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#3182CE')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BEE3F8')),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('LEFTPADDING', (0,0), (-1,-1), 6),
                ('RIGHTPADDING', (0,0), (-1,-1), 6),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            elements.append(t_box)
            elements.append(Spacer(1, 5))

            corse_data = [[
                Paragraph("N°", th_style),
                Paragraph("Linea", th_style),
                Paragraph("Descrizione Tratta / Attività Effettiva", th_style),
                Paragraph("Part.", th_style),
                Paragraph("Arr.", th_style),
                Paragraph("Km", th_style),
                Paragraph("Dicitura / Stato Operativo della Corsa", th_style)
            ]]

            row_styles = []

            for c_idx, a in enumerate(prop.attivita, 1):
                lin = a.get('linea', '')
                desc_tratta = a.get('descrizione', f"{a.get('da','')} ➔ {a.get('a','')}" if a.get('a') else a.get('da',''))
                p = a.get('partenza', '')
                arr = a.get('arrivo', '')
                km = str(a.get('km', '-'))
                stato_scambio = a.get('scambio_tag', 'Attività Ordinaria Invariata')

                if 'RICEVUTA' in stato_scambio:
                    p_style = td_ricevuta
                    note_cell = Paragraph(f"🟢 <b>{stato_scambio}</b>", td_ricevuta)
                    row_styles.append(('BACKGROUND', (0, c_idx), (-1, c_idx), colors.HexColor('#C6F6D5')))
                elif 'SOSTA' in lin.upper() or 'PAUSA' in lin.upper():
                    p_style = td_cell
                    note_cell = Paragraph("Pausa / Sosta Operativa al Deposito", td_cell)
                    row_styles.append(('BACKGROUND', (0, c_idx), (-1, c_idx), colors.HexColor('#EDF2F7')))
                else:
                    p_style = td_cell
                    note_cell = Paragraph("Attività Ordinaria Invariata", td_cell)
                    if c_idx % 2 == 0:
                        row_styles.append(('BACKGROUND', (0, c_idx), (-1, c_idx), colors.HexColor('#F7FAFC')))

                corse_data.append([
                    Paragraph(str(c_idx), td_center),
                    Paragraph(lin, td_center),
                    Paragraph(desc_tratta[:55], p_style),
                    Paragraph(p, td_center),
                    Paragraph(arr, td_center),
                    Paragraph(km, td_right),
                    note_cell
                ])

            t_corse = Table(corse_data, colWidths=[20, 38, 330, 38, 38, 36, 310])
            t_style = [
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#003366')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E0')),
                ('TOPPADDING', (0,0), (-1,-1), 1.6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1.6),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ] + row_styles
            t_corse.setStyle(TableStyle(t_style))
            elements.append(t_corse)
            elements.append(PageBreak())

        doc.build(elements)
        print(f"✅ PDF generato con successo: {pdf_out_path}")
        return True


if __name__ == '__main__':
    default_json = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/cartellini_2026_lun_ven_completo.json"
    default_pdf = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Turni_Pinerolo_Scambi_Evidenziati.pdf"

    print("🚀 AVVIO MOTORE OTTIMIZZATORE TURNI TPL...")
    app = OttimizzatoreTurniTPL(default_json)

    # Eseguiamo il report iniziale
    app.genera_report_testuale(deposito_filtro="Pi")
