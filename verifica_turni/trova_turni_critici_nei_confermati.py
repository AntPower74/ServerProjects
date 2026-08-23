import fitz
import re

doc = fitz.open("Comparazione turni 2025-2026/Cartellini Giovedì Base Soluzione 1.pdf")
malpensa_set = {'To2010', 'To2020', 'To2030', 'To2040', 'To2050', 'To2060', 'To2070', 'To2080', 'To2090'}

turni_da_migliorare_subito = []

for pno, page in enumerate(doc):
    text = page.get_text()
    m_turno = re.search(r'Cartellino di marcia del turno:\s*([A-Za-z0-9\s]+?)\s*in vigore', text)
    if not m_turno: continue
    turno = m_turno.group(1).replace(' ', '').strip()
    if turno in malpensa_set or turno.startswith('Pb') or turno.startswith('FT'): continue
    
    m_nastro = re.search(r'Nastro del turno\s*(\d{1,2}[,\.]\d{2})', text)
    m_olg = re.search(r'ORE LAVORO GIORNALIERO\s*(\d{1,2}[,\.]\d{2})', text)
    m_rip = re.search(r'NUMERO RIPRESE \(AITO\)\s*(\d+)', text)
    m_dep = re.search(r'TURNO\s+\d+\s+DI\s+([A-Z\s\.]+)', text)
    dep_name = m_dep.group(1).strip() if m_dep else turno[:2]
    
    if m_nastro and m_olg:
        n_val = float(m_nastro.group(1).replace(',', '.'))
        o_val = float(m_olg.group(1).replace(',', '.'))
        rip_val = int(m_rip.group(1)) if m_rip else 1
        
        # Turni che hanno:
        # 1. Nastro lungo (> 10h30)
        # 2. Oppure OLG basso (< 6h00)
        # 3. Oppure 2-3 Riprese spezzate
        if n_val >= 10.5 or (rip_val >= 2 and n_val >= 9.5) or (o_val < 6.0 and n_val > 8.0):
            turni_da_migliorare_subito.append({
                'turno': turno,
                'dep': dep_name,
                'nastro': n_val,
                'olg': o_val,
                'rip': rip_val,
                'buco_ore': n_val - o_val
            })

doc.close()

print(f"=== TOTALE TURNI NEI 'CONFERMATI' CHE HANNO GRAVI CRITICITÀ DA MIGLIORARE: {len(turni_da_migliorare_subito)} ===")
print("Esempi più critici per Deposito:\n")
turni_da_migliorare_subito.sort(key=lambda x: x['nastro'], reverse=True)
for t in turni_da_migliorare_subito[:25]:
    print(f"• Turno {t['turno']:<8} ({t['dep']:<15}): Nastro {t['nastro']:>5.2f}h | OLG {t['olg']:>4.2f}h | Riprese: {t['rip']} | Ore Perse/Non Pagate: {t['buco_ore']:>4.2f}h")

