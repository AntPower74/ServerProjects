#!/usr/bin/env python3
import fitz
import re
import json

PDF_PATH = "/home/antonio/verifica_turni/Comparazione turni 2025-2026/Cartellini lun-ven 2026.pdf"

doc = fitz.open(PDF_PATH)
turni_pinerolo = []

for page_idx in range(len(doc)):
    text = doc[page_idx].get_text()
    if not text: continue
    
    # Cerca codice turno
    m_code = re.search(r'TURNO\s+([A-Za-z0-9_]+)', text)
    if not m_code:
        m_code = re.search(r'\b(Pi\d{4}[A-Za-z0-9_]*)\b', text, re.IGNORECASE)
    
    code = m_code.group(1) if m_code else f"Turno_{page_idx+1}"
    
    if code.upper().startswith('PI'):
        # Estrai parametri
        # Inizio, Fine, Nastro, Ore Lavoro
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        nastro = ""
        ore_lav = ""
        ore_guida = ""
        sosta_100 = "0,00"
        sosta_12 = "0,00"
        riprese = "1"
        in_s = ""
        out_s = ""
        
        for idx, line in enumerate(lines):
            if 'Nastro' in line or 'NASTRO' in line:
                for k in range(max(0, idx-2), min(len(lines), idx+5)):
                    m_n = re.search(r'(\d{1,2}[.:]\d{2})', lines[k])
                    if m_n and not nastro: nastro = m_n.group(1)
            if 'Ore di Lavoro' in line or 'Ore Lavoro' in line or 'Lavoro Eff' in line:
                for k in range(max(0, idx-2), min(len(lines), idx+5)):
                    m_o = re.search(r'(\d{1,2}[.:]\d{2})', lines[k])
                    if m_o and not ore_lav: ore_lav = m_o.group(1)
            if 'Sosta al 100%' in line:
                for k in range(idx+1, min(len(lines), idx+4)):
                    m_s = re.search(r'(\d+[,\.]\d+)', lines[k])
                    if m_s and sosta_100 == "0,00": sosta_100 = m_s.group(1)
            if 'Sosta al 12%' in line:
                for k in range(idx+1, min(len(lines), idx+4)):
                    m_s = re.search(r'(\d+[,\.]\d+)', lines[k])
                    if m_s and sosta_12 == "0,00": sosta_12 = m_s.group(1)
            if 'NUMERO RIPRESE' in line or 'Riprese' in line:
                for k in range(idx+1, min(len(lines), idx+4)):
                    m_r = re.search(r'(\d+)', lines[k])
                    if m_r and riprese == "1": riprese = m_r.group(1)
                    
        turni_pinerolo.append({
            'pagina': page_idx + 1,
            'codice': code,
            'testo': text[:400].replace('\n', ' ')
        })

print(f"Trovati {len(turni_pinerolo)} turni di Pinerolo nel PDF originale.\n")
for t in turni_pinerolo:
    print(f"Pagina {t['pagina']:3d} | Codice: {t['codice']:8s} | Anteprima: {t['testo'][:120]}")
