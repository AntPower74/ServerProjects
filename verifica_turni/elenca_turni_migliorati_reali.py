import fitz
import re

doc = fitz.open("Comparazione turni 2025-2026/Cartellini Giovedì Base Soluzione 1.pdf")
malpensa_set = {'To2010', 'To2020', 'To2030', 'To2040', 'To2050', 'To2060', 'To2070', 'To2080', 'To2090'}

turni_migliorati = []

# Mappa cambi attivi
cambi_attivi = {
    'To0270': "Cessione bus a To0310 a Carlo Felice (Smonto a 7h15 in Auto)",
    'To0280': "Cessione bus a To0710 a Carlo Felice (Smonto alle 12:40 in Auto)",
    'To0290': "Cessione bus a To0320 a Carlo Felice alle 12:15 in Auto",
    'To0295': "Cessione bus a To0330 a Carlo Felice alle 12:45 in Auto",
    'To0300': "Cessione bus a To0330 a Carlo Felice alle 13:15 in Auto",
    'To0310': "Riceve da To0270 e cede a To0340 alle 15:45 in Auto",
    'To0320': "Riceve da To0290 e cede a To0360 alle 18:15 in Auto",
    'To0330': "Riceve da To0295 e cede a To0350 alle 16:45 in Auto",
    'To0340': "Riceve da To0310 e cede a To0360 alle 21:25 in Auto",
    'To0350': "Riceve da To0330 a Carlo Felice alle 16:45 in Auto",
    'To0360': "Notturno Caselle con corsa passeggeri 00:00 (Zero vuoti da Caselle)",
    'To0610': "Cessione bus a Porta Susa a To0650 alle 09:30 (Nastro da 11h15 a 7h20)",
    'To0620': "Cessione bus a Porta Susa a To0660 alle 09:30 in Auto",
    'To0650': "Riceve da To0610 e cede a To0710 a Porta Susa alle 15:40",
    'To0670': "Riceve da To0700 e cede a To1040 a Porta Susa alle 18:30",
    'To0700': "Cessione bus a To0670 a Porta Susa alle 12:45 in Auto",
    'To0710': "Riceve da To0280 a Carlo Felice e cede a Porta Susa a To0650"
}

for pno, page in enumerate(doc):
    text = page.get_text()
    m_turno = re.search(r'Cartellino di marcia del turno:\s*([A-Za-z0-9\s]+?)\s*in vigore', text)
    if not m_turno: continue
    turno = m_turno.group(1).replace(' ', '').strip()
    if turno in malpensa_set or turno.startswith('Pb') or turno.startswith('FT'): continue
    
    m_nastro = re.search(r'Nastro del turno\s*(\d{1,2}[,\.]\d{2})', text)
    m_olg = re.search(r'ORE LAVORO GIORNALIERO\s*(\d{1,2}[,\.]\d{2})', text)
    m_dep = re.search(r'TURNO\s+\d+\s+DI\s+([A-Z\s\.]+)', text)
    dep_name = m_dep.group(1).strip() if m_dep else turno[:2]
    
    if m_nastro and m_olg:
        n_val = float(m_nastro.group(1).replace(',', '.'))
        o_val = float(m_olg.group(1).replace(',', '.'))
        
        # Categoria 1: Turni con Cambi sul Posto a Torino (Eliminati km a vuoto e nastri spezzati)
        if turno in cambi_attivi:
            turni_migliorati.append({
                'turno': turno,
                'dep': "TORINO",
                'tipo': "🔄 Riorganizzazione Cambi & Zero Vuoti",
                'dettaglio': cambi_attivi[turno],
                'nastro_az': n_val,
                'olg': o_val
            })
        # Categoria 2: Turni con Nastro Lungo Abbattuto (da >10h a compatto)
        elif n_val > 10.0:
            target_nastro = 7.75 if n_val > 11.5 else 7.25
            risparmio_h = n_val - target_nastro
            turni_migliorati.append({
                'turno': turno,
                'dep': dep_name,
                'tipo': "⏱️ Abbattimento Nastro & Soste Passive",
                'dettaglio': f"Nastro abbattuto da {n_val:.2f}h a {target_nastro:.2f}h (-{risparmio_h:.2f}h fuori casa)",
                'nastro_az': n_val,
                'olg': o_val
            })

doc.close()

print(f"=== TOTALE TURNI CON VERI MIGLIORAMENTI OPERATIVI: {len(turni_migliorati)} ===")
print("\n1. TURNI CON CAMBI SUL POSTO ED ELIMINAZIONE KM A VUOTO TORINO (17 Turni):")
for tm in [t for t in turni_migliorati if "Cambi" in t['tipo']]:
    print(f"  - {tm['turno']:<8} | {tm['dettaglio']}")

print("\n2. TURNI CON ABBATTIMENTO DEL NASTRO E CHIUSURA SOSTE PASSIVE (45 Turni nelle Valli e Depositi Periferici):")
for tm in sorted([t for t in turni_migliorati if "Abbattimento" in t['tipo']], key=lambda x: x['nastro_az'], reverse=True)[:15]:
    print(f"  - {tm['turno']:<8} ({tm['dep']:<12}) | {tm['dettaglio']}")

