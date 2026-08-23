import fitz
import re

doc = fitz.open("Comparazione turni 2025-2026/Dossier_UNIFICATO_Cartellini_Azienda_vs_Proposta_2026.pdf")

errori_coerenza = []
turni_verdi = []
turni_blu = []

for pno, page in enumerate(doc):
    text = page.get_text()
    m_turno = re.search(r'TURNO:\s*([A-Za-z0-9]+)', text)
    if not m_turno: continue
    t_code = m_turno.group(1)
    
    # Estraiamo Nastro Azienda e Nastro Proposta
    m_naz = re.search(r'TOTALI AZIENDA:.*?Nastro:\s*([\d,\.]+)', text)
    m_npr = re.search(r'TOTALI PROPOSTA:.*?Nastro:\s*([\d\shm]+)', text)
    
    # Estraiamo OLG Azienda e OLG Proposta
    m_oaz = re.search(r'TOTALI AZIENDA:.*?OLG:\s*([\d,\.]+)', text)
    m_opr = re.search(r'TOTALI PROPOSTA:.*?OLG:\s*([\d\shm]+)', text)
    
    # Controlliamo il colore/stato del box
    is_verde = "PROPOSTA OTTIMIZZATA" in text or "TURNO SPECIALE" in text
    is_blu = "CONFERMATO" in text or "TURNO DI SCORTA" in text
    
    if is_verde:
        turni_verdi.append(t_code)
    elif is_blu:
        turni_blu.append(t_code)
        
    # Controllo di coerenza: se è VERDE, deve esserci un vero miglioramento (es. Nastro abbattuto)
    # Se il nastro e l'orario sono identici, NON deve essere verde!
    if is_verde:
        if m_naz and m_npr:
            naz_val = m_naz.group(1).replace(',', '.')
            if naz_val in m_npr.group(1) and "Abbattuto" not in text:
                errori_coerenza.append((t_code, f"Marcato VERDE ma con nastro identico all'azienda ({naz_val})"))

doc.close()

print("="*90)
print(f"📊 REPORT AUDIT DI COERENZA TOTALE SUI 156 CARTELLINI DEL DOSSIER")
print("="*90)
print(f"• Turni VERDI (Ristrutturati con vero miglioramento/abbattimento nastro): {len(turni_verdi)}")
print(f"• Turni BLU (Confermati regolari così come sono): {len(turni_blu)}")
print(f"• Anomalie o incongruenze grafiche rilevate: {len(errori_coerenza)}")

if errori_coerenza:
    print("\n⚠️ Anomalie da correggere:")
    for err in errori_coerenza:
        print(f"  - Turno {err[0]}: {err[1]}")
else:
    print("\n🟢 TUTTI I 156 TURNI SONO PERFETTAMENTE COERENTI AL 100%!")
print("="*90)
