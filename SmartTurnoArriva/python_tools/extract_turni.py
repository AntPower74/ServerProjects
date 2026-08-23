import pdfplumber
import json
import re
import os

PDF_FILES = [
    "/PDF cartellino turni/Cartellini_Turni_DomenicaEstivo.pdf",
    "/PDF cartellino turni/Cartellini_Turni_GiovedìEstivo.pdf",
    "/PDF cartellino turni/Cartellini_Turni_SabatoEstivo.pdf",
]

def parse_giorno(filename):
    f = os.path.basename(filename).lower()
    if "domenica" in f: return "Domenica"
    if "giovedi" in f or "giovedì" in f: return "Giovedì"
    if "sabato" in f: return "Sabato"
    return "Feriale"

def extract_deposito(turno_name):
    # Cerca "DI XXXXX" nel nome (es: "TURNO 305 DI BOBBIO")
    m = re.search(r'\bDI\s+([A-Z][A-Z\s]+?)(?:\s+SETTIMANA|\s*$)', turno_name.upper())
    if m:
        return m.group(1).strip().title()
    # Usa la prima parola prima del trattino se c'è (es: "CASELLE-TORINO-CASELLE")
    parts = turno_name.strip().split('-')
    return parts[0].strip().title()

def parse_orario(s):
    """Converte '7.20' o '7:20' in '07:20'"""
    s = s.strip().replace('.', ':')
    parts = s.split(':')
    if len(parts) == 2:
        return f"{int(parts[0]):02d}:{parts[1].zfill(2)}"
    return s

all_turns = []

for pdf_path in PDF_FILES:
    giorno = parse_giorno(pdf_path)
    print(f"Elaborazione: {os.path.basename(pdf_path)} ({giorno})")
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue
            
            lines = text.split('\n')
            
            turno_code = None
            turno_name = None
            ora_inizio = None
            ora_fine = None
            deposito = None
            corse = []
            
            for line in lines:
                line = line.strip()
                
                # "Cartellino di marcia del turno: XXXX"
                m = re.search(r'Cartellino di marcia del turno:\s*(\S+)', line)
                if m:
                    turno_code = m.group(1).strip()
                
                # "Turno: NOME Ora inizio turno : HH.MM - Ora fine turno: HH.MM"
                m = re.search(r'Turno:\s*(.+?)\s+Ora inizio turno\s*:\s*([\d.]+)\s*-\s*Ora fine turno:\s*([\d.]+)', line)
                if m:
                    turno_name = m.group(1).strip()
                    ora_inizio = parse_orario(m.group(2))
                    ora_fine = parse_orario(m.group(3))
                    deposito = extract_deposito(turno_name)
                
                # Corse reali: iniziano con 6 cifre (numero linea)
                m = re.match(r'^(\d{6})\s+(.+)$', line)
                if m:
                    linea = m.group(1)
                    rest = m.group(2).strip()
                    
                    orari_reali = re.findall(r'\b(\d{1,2}[.:]\d{2})\b', rest)
                    
                    # La descrizione è tutto ciò che precede i numeri a fine riga
                    descrizione = re.sub(r'(\s+\d+(?:[.,]\d+)?)+$', '', rest).strip()
                    
                    da = descrizione
                    a = ""
                    
                    partenza = ""
                    arrivo = ""
                    if len(orari_reali) > 0:
                        def to_m(t_str):
                            p = t_str.replace('.', ':').split(':')
                            return int(p[0])*60 + int(p[1])
                            
                        if len(orari_reali) >= 2:
                            diff = to_m(orari_reali[1]) - to_m(orari_reali[0])
                            if diff < 0: diff += 24*60
                            
                            if diff <= 10:
                                # First time is Ripresa, second is Partenza
                                partenza = parse_orario(orari_reali[1])
                                arrivo = parse_orario(orari_reali[2]) if len(orari_reali) > 2 else ""
                            else:
                                # First time is Partenza
                                partenza = parse_orario(orari_reali[0])
                                arrivo = parse_orario(orari_reali[1])
                        else:
                            partenza = parse_orario(orari_reali[0])
                    
                    corse.append({
                        "linea": linea,
                        "da": da,
                        "a": a,
                        "partenza": partenza,
                        "arrivo": arrivo,
                    })
            
            if turno_code and corse:
                all_turns.append({
                    "codice": turno_code,
                    "nome": turno_name or turno_code,
                    "deposito": deposito or "?",
                    "giorno": giorno,
                    "ora_inizio": ora_inizio or "",
                    "ora_fine": ora_fine or "",
                    "corse": corse
                })

print(f"\nTotale turni estratti: {len(all_turns)}")
print(f"Totale corse: {sum(len(t['corse']) for t in all_turns)}")

# Campione
if all_turns:
    t = all_turns[1]
    print(f"\nEsempio turno: {t['codice']} - {t['nome']} ({t['deposito']}, {t['giorno']})")
    print(f"  Orario: {t['ora_inizio']} - {t['ora_fine']}")
    for c in t['corse'][:5]:
        print(f"  Linea {c['linea']} | {c['da']} → {c['a']} | {c['partenza']} - {c['arrivo']}")

with open("/root/turni_corse.json", "w", encoding="utf-8") as f:
    json.dump(all_turns, f, ensure_ascii=False, indent=2)

print("\nSalvato in /root/turni_corse.json")
