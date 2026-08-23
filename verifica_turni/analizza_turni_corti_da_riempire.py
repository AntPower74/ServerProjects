import fitz
import re

doc = fitz.open("Comparazione turni 2025-2026/Cartellini Giovedì Base Soluzione 1.pdf")
malpensa_set = {'To2010', 'To2020', 'To2030', 'To2040', 'To2050', 'To2060', 'To2070', 'To2080', 'To2090'}

turni_critici = []

for pno, page in enumerate(doc):
    text = page.get_text()
    m_turno = re.search(r'Cartellino di marcia del turno:\s*([A-Za-z0-9\s]+?)\s*in vigore', text)
    if not m_turno: continue
    turno = m_turno.group(1).replace(' ', '').strip()
    if turno in malpensa_set or turno.startswith('Pb') or turno.startswith('FT'): continue
    
    m_olg = re.search(r'ORE LAVORO GIORNALIERO\s*(\d{1,2}[,\.]\d{2})', text)
    m_nastro = re.search(r'Nastro del turno\s*(\d{1,2}[,\.]\d{2})', text)
    m_dep = re.search(r'TURNO\s+\d+\s+DI\s+([A-Z\s\.]+)', text)
    
    dep_name = m_dep.group(1).strip() if m_dep else turno[:2]
    
    if m_olg and m_nastro:
        o_val = float(m_olg.group(1).replace(',', '.'))
        n_val = float(m_nastro.group(1).replace(',', '.'))
        
        # Turni con nastro lungo ma paga bassa (spreco di ore passiva)
        # o turni con OLG < 6.5
        if o_val < 6.5 or (n_val - o_val) > 2.5:
            turni_critici.append({
                'turno': turno,
                'dep': dep_name,
                'nastro': n_val,
                'olg': o_val,
                'inefficienza': n_val - o_val
            })

doc.close()

print(f"=== IDENTIFICATI {len(turni_critici)} TURNI CRITICI CON SPRECO DI NASTRO E BASSO OLG ===")
print(f"{'Turno':<8} | {'Deposito':<15} | {'Nastro Azienda':<15} | {'OLG Azienda':<12} | {'Ore Sprecate (Nastro - OLG)'}")
print("-"*85)
for tc in sorted(turni_critici, key=lambda x: x['inefficienza'], reverse=True)[:15]:
    print(f"{tc['turno']:<8} | {tc['dep']:<15} | {tc['nastro']:>6.2f} ore       | {tc['olg']:>6.2f} ore    | {tc['inefficienza']:>6.2f} ore di buco passivo")

