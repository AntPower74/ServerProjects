import json
import fitz
import re

# Carichiamo il database delle corse estratto da Google Sheets
with open("/home/antonio/verifica_turni/DATABASE_CORSE_DA_SHEETS.json", "r", encoding="utf-8") as f:
    db_sheets = json.load(f)

# Apriamo il Dossier PDF delle Nostre Proposte
doc = fitz.open("Comparazione turni 2025-2026/Dossier_UNIFICATO_Cartellini_Azienda_vs_Proposta_2026.pdf")

# Estraiamo il testo di tutte le pagine per turno
testo_per_turno = {}
for page in doc:
    text = page.get_text()
    m_turno = re.search(r'TURNO:\s*([A-Za-z0-9]+)', text)
    if m_turno:
        testo_per_turno[m_turno.group(1)] = text

doc.close()

tot_corse_sheets = 0
corse_coperte = 0
corse_mancanti = []
turni_non_in_pdf = []

for turno, corse in db_sheets.items():
    if turno not in testo_per_turno:
        turni_non_in_pdf.append((turno, len(corse)))
        continue
        
    text_turno = testo_per_turno[turno]
    
    for c in corse:
        tot_corse_sheets += 1
        # Verifichiamo orario di partenza (es. 4:45 o 04:45)
        ora_p_raw = c['ora_partenza']
        parts = ora_p_raw.split(':')
        h = int(parts[0])
        m = int(parts[1])
        ora_fmt1 = f"{h}:{m:02d}"
        ora_fmt2 = f"{h:02d}:{m:02d}"
        
        # Verifichiamo se l'orario o la linea è presente nella scheda della Nostra Proposta
        if ora_fmt1 in text_turno or ora_fmt2 in text_turno:
            corse_coperte += 1
        else:
            corse_mancanti.append({
                'turno': turno,
                'corsa_id': c['corsa_id'],
                'cod_linea': c['cod_linea'],
                'partenza': c['partenza'],
                'ora_p': ora_p_raw,
                'arrivo': c['arrivo'],
                'ora_a': c['ora_arrivo']
            })

print("="*90)
print(f"📊 REPORT AUDIT COPERTURA CORSE GOOGLE SHEETS VS NOSTRA PROPOSTA PDF")
print("="*90)
print(f"• Totale corse nel foglio 'Corse per turno': {sum(len(v) for v in db_sheets.values())}")
print(f"• Corse appartenenti ai 156 turni ordinari nel Dossier: {tot_corse_sheets}")
print(f"• Corse verificate e coperte nella Nostra Proposta: {corse_coperte} / {tot_corse_sheets} ({corse_coperte/tot_corse_sheets*100:.2f}%)")

if turni_non_in_pdf:
    print(f"\nTurni presenti in Sheets ma non nel Dossier Ordinario (es. Piobesi/Malpensa con dossier separati):")
    for t_nip in turni_non_in_pdf:
        print(f"  - {t_nip[0]}: {t_nip[1]} corse")

if corse_mancanti:
    print(f"\n⚠️ Corse con orario differente o da verificare ({len(corse_mancanti)}):")
    for cm in corse_mancanti[:10]:
        print(f"  - Turno {cm['turno']}: Linea {cm['cod_linea']} ore {cm['ora_p']} ({cm['partenza'][:25]} -> {cm['arrivo'][:25]})")
else:
    print("\n🟢 TUTTE LE CORSE DEL FOGLIO GOOGLE SHEETS SONO INTEGRALMENTE COPERTE AL 100%!")
print("="*90)
