import fitz
import re

doc = fitz.open("Comparazione turni 2025-2026/Cartellini Giovedì Base Soluzione 1.pdf")
malpensa_set = {'To2010', 'To2020', 'To2030', 'To2040', 'To2050', 'To2060', 'To2070', 'To2080', 'To2090'}

turni_db = []

for pno, page in enumerate(doc):
    text = page.get_text()
    m_turno = re.search(r'Cartellino di marcia del turno:\s*([A-Za-z0-9\s]+?)\s*in vigore', text)
    if not m_turno: continue
    turno = m_turno.group(1).replace(' ', '').strip()
    if turno in malpensa_set or turno.startswith('Pb'): continue
    
    m_inizio = re.search(r'Ora inizio turno\s*:\s*(\d{1,2}\.\d{2})', text)
    m_fine = re.search(r'Ora fine turno:\s*(\d{1,2}\.\d{2})', text)
    m_nastro = re.search(r'Nastro del turno\s*(\d{1,2}[,\.]\d{2})', text)
    m_olg = re.search(r'ORE LAVORO GIORNALIERO\s*(\d{1,2}[,\.]\d{2})', text)
    m_dep = re.search(r'TURNO\s+\d+\s+DI\s+([A-Z\s\.]+)', text)
    
    dep_name = m_dep.group(1).strip() if m_dep else turno[:2]
    if turno.startswith('To'): dep_name = "TORINO"
    elif turno.startswith('FT'): dep_name = "PINEROLO" if "2820" in turno else "TORINO"
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
    
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    
    corse = []
    for i, l in enumerate(lines):
        if re.match(r'^\d{1,2}\.\d{2}$', l) and i+1 < len(lines) and re.match(r'^\d{1,2}\.\d{2}$', lines[i+1]):
            p_ora = l
            a_ora = lines[i+1]
            desc = lines[i-1] if i > 0 else ""
            if not ("Ora inizio" in desc or "Cartellino" in desc or "Mod.M002" in desc):
                corse.append({'p': p_ora, 'a': a_ora, 'desc': desc})
                
    turni_db.append({
        'pno': pno + 1,
        'turno': turno,
        'deposito': dep_name,
        'inizio': m_inizio.group(1) if m_inizio else "",
        'fine': m_fine.group(1) if m_fine else "",
        'nastro': m_nastro.group(1) if m_nastro else "",
        'olg': m_olg.group(1) if m_olg else "",
        'corse': corse
    })

doc.close()

print(f"Caricati {len(turni_db)} turni ordinari per audit certosino.")

# Controlli:
# 1. Quanti turni hanno più di 12 corse (rischio troncamento grafico)
# 2. Quanti turni terminano fuori deposito residenza senza attività di rientro
# 3. Quanti turni hanno soste o trasferimenti sospetti
troncati = []
fuori_deposito = []

for t in turni_db:
    if len(t['corse']) > 12:
        troncati.append((t['turno'], len(t['corse'])))
    
    if t['corse']:
        prima_attivita = t['corse'][0]['desc']
        ultima_attivita = t['corse'][-1]['desc']
        # se non c'è pulizia o rientro
        if not ("Pulizia" in ultima_attivita or "Controllo" in ultima_attivita or "PARCHEGGIO" in ultima_attivita or "RIMESSA" in ultima_attivita or "DEPOSITO" in ultima_attivita):
            fuori_deposito.append((t['turno'], ultima_attivita))

print(f"\n1. Turni con oltre 12 righe (che rischiavano di essere tagliati nella tabella): {len(troncati)}")
for tr in troncati:
    print(f"   - {tr[0]}: {tr[1]} righe")

print(f"\n2. Turni che non chiudono con pulizia/deposito esplicito nell'estrazione: {len(fuori_deposito)}")
for fd in fuori_deposito[:15]:
    print(f"   - {fd[0]}: Ultima riga = {fd[1]}")

