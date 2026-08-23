import fitz
import re
import json

doc = fitz.open("Comparazione turni 2025-2026/Cartellini Giovedì Base Soluzione 1.pdf")
malpensa_set = {'To2010', 'To2020', 'To2030', 'To2040', 'To2050', 'To2060', 'To2070', 'To2080', 'To2090'}

# REGOLE FLESSIBILI CONCORDATE:
# 1. Nastro max accettabile: 9h30 - 10h00 SE l'OLG è alto (>= 7h30 - 8h00)
# 2. Riprese max accettabili: 2 riprese (MAI 3 o 4)
# 3. Abbattimento TOTALE di tutti i nastri > 10h30 (portati a <= 9h30)
# 4. Eliminazione della 3° e 4° ripresa (portate a max 2)

turni_da_ristrutturare_perfetti = []

for pno, page in enumerate(doc):
    text = page.get_text()
    m_turno = re.search(r'Cartellino di marcia del turno:\s*([A-Za-z0-9\s]+?)\s*in vigore', text)
    if not m_turno: continue
    turno = m_turno.group(1).replace(' ', '').strip()
    if turno in malpensa_set or turno.startswith('Pb') or turno.startswith('FT'): continue
    
    m_inizio = re.search(r'INIZIO SERVIZIO\s*(\d{1,2}[\.,]\d{2})', text)
    m_fine = re.search(r'FINE SERVIZIO\s*(\d{1,2}[\.,]\d{2})', text)
    m_nastro = re.search(r'Nastro del turno\s*(\d{1,2}[,\.]\d{2})', text)
    m_olg = re.search(r'ORE LAVORO GIORNALIERO\s*(\d{1,2}[,\.]\d{2})', text)
    m_rip = re.search(r'NUMERO RIPRESE \(AITO\)\s*(\d+)', text)
    m_dep = re.search(r'TURNO\s+\d+\s+DI\s+([A-Z\s\.]+)', text)
    dep_name = m_dep.group(1).strip() if m_dep else turno[:2]
    
    if m_nastro and m_olg:
        n_val = float(m_nastro.group(1).replace(',', '.'))
        o_val = float(m_olg.group(1).replace(',', '.'))
        rip_val = int(m_rip.group(1)) if m_rip else 1
        
        # Criterio di Ristrutturazione Intelligente:
        # - Nastri > 10.30 (da abbattere a 9h30 max con paga piena)
        # - Riprese >= 3 (da ridurre a 2)
        # - OLG basso con nastro lungo (aumentare OLG a fronte di nastro 9h30)
        if n_val > 10.30 or rip_val >= 3:
            # Target Nastro: max 9h30
            nastro_target = min(9.50, n_val - 2.0)
            if nastro_target < 7.50: nastro_target = 7.50
            
            # Target OLG: sale a lavoro effettivo pieno (almeno 7h30)
            olg_target = max(o_val, 7.50) if nastro_target >= 9.0 else max(o_val, 7.00)
            
            turni_da_ristrutturare_perfetti.append({
                'turno': turno,
                'dep': dep_name,
                'n_az': n_val,
                'o_az': o_val,
                'rip_az': rip_val,
                'n_target': nastro_target,
                'o_target': olg_target,
                'rip_target': 2 if rip_val >= 3 else 1
            })

doc.close()

print(f"=== TOTALE TURNI PERIFERICI CHE RISTRUTTURIAMO CON LE NUOVE REGOLE: {len(turni_da_ristrutturare_perfetti)} ===")
print("Esempi di miglioramento (Nastro <= 9h30/10h00, OLG più alto, Max 2 Riprese):\n")
for t in turni_da_ristrutturare_perfetti[:20]:
    print(f"• Turno {t['turno']:<8} ({t['dep']:<15}): Nastro Az {t['n_az']:>5.2f}h -> Proposta {t['n_target']:>4.2f}h | OLG {t['o_az']:>4.2f}h -> {t['o_target']:>4.2f}h | Riprese: {t['rip_az']} -> {t['rip_target']}")

