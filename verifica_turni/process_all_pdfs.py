import pdfplumber
import re
import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import glob
import os

def extract_and_upload(pdf_path, client, spreadsheet):
    turni = []
    
    print(f"Elaborazione di {pdf_path}...")
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text: continue
            
            lines = text.split('\n')
            
            nome_turno = ""
            deposito = ""
            inizio = ""
            fine = ""
            nastro = ""
            
            # Check format type
            if "Mod.M002/1 Cartellino di marcia" in text:
                # Format 2 (Scolastici/Attuali)
                for line in lines:
                    m1 = re.search(r'Cartellino di marcia del turno:\s*([A-Za-z0-9_]+)', line)
                    if m1: nome_turno = m1.group(1)
                    
                    m2 = re.search(r'Turno:\s*(.*?)\s*Ora inizio', line)
                    if m2: deposito = m2.group(1).strip()
                    
                    m3 = re.search(r'NASTRO DEL TURNO\s*([\d,]+)', line)
                    if m3: nastro = m3.group(1)
                
                times = []
                in_trips = False
                for line in lines:
                    if line.startswith('Linea T Vettura'):
                        in_trips = True
                        continue
                    if in_trips:
                        if line.startswith('Totali'):
                            break
                        matches = re.findall(r'\b\d{1,2}\.\d{2}\b', line)
                        times.extend(matches)
                
                if times:
                    inizio = times[0].replace('.', ':')
                    fine = times[-1].replace('.', ':')
                    
            else:
                # Format 1 (Original)
                for i, line in enumerate(lines):
                    if "DEPOSITO:" in line:
                        if i > 0:
                            nome_turno = lines[i-1].strip()
                        deposito = line.split("DEPOSITO:")[1].strip()
                    if "SIGN ON:" in line and "SIGN OFF:" in line:
                        m = re.search(r"SIGN ON:\s*([\d:]+),\s*SIGN OFF:\s*([\d:]+)", line)
                        if m:
                            inizio = m.group(1)
                            fine = m.group(2)
                    if "NASTRO:" in line:
                        nastro = line.split("NASTRO:")[1].strip()
            
            if nome_turno or deposito:
                # pad inizio/fine with 0 if needed (e.g. 4:35 -> 04:35)
                if len(inizio) == 4 and inizio[1] == ':': inizio = '0' + inizio
                if len(fine) == 4 and fine[1] == ':': fine = '0' + fine
                turni.append([nome_turno, inizio, fine, nastro, deposito])

    # Upload to Google Sheets
    sheet_name = os.path.basename(pdf_path).replace('.pdf', '')
    
    try:
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            print(f"Foglio '{sheet_name}' trovato, lo pulisco...")
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            print(f"Creo il nuovo foglio '{sheet_name}'...")
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=str(max(100, len(turni)+10)), cols="10")
            
        header = ["Nome Turno", "Orario Inizio", "Orario Fine", "Nastro Lavorativo", "Deposito"]
        data_to_upload = [header] + turni
        
        print(f"Carico i dati sul foglio '{sheet_name}'...")
        worksheet.update(range_name='A1', values=data_to_upload)
        print(f"Dati caricati con successo su '{sheet_name}'!")
        
    except Exception as e:
        print(f"Errore su {sheet_name}: {e}")

if __name__ == '__main__':
    url = "https://docs.google.com/spreadsheets/d/1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM/edit?usp=sharing"
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_url(url)
    
    pdfs = glob.glob('*.pdf')
    for pdf in pdfs:
        if "scolastici" in pdf.lower():
            extract_and_upload(pdf, client, spreadsheet)
