import pdfplumber
import re
import csv
import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def extract_and_upload(pdf_path, sheet_url):
    turni = []
    
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
                    # extract what's after NASTRO:
                    # e.g., TEMPO PAGATO: 04:42 NASTRO: 5H 18M
                    nastro = line.split("NASTRO:")[1].strip()
            
            if nome_turno or deposito:
                turni.append([nome_turno, inizio, fine, nastro, deposito])

    # Upload to Google Sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    
    try:
        spreadsheet = client.open_by_url(sheet_url)
        # Check if worksheet exists
        try:
            worksheet = spreadsheet.worksheet("verifica orari")
            print("Foglio 'verifica orari' trovato, lo pulisco...")
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            print("Creo il nuovo foglio 'verifica orari'...")
            worksheet = spreadsheet.add_worksheet(title="verifica orari", rows=str(max(100, len(turni)+10)), cols="10")
            
        header = ["Nome Turno", "Orario Inizio", "Orario Fine", "Nastro Lavorativo", "Deposito"]
        data_to_upload = [header] + turni
        
        print("Carico i dati sul nuovo foglio...")
        worksheet.update(range_name='A1', values=data_to_upload)
        print("Dati caricati con successo su 'verifica orari'!")
        
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == '__main__':
    url = "https://docs.google.com/spreadsheets/d/1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM/edit?usp=sharing"
    extract_and_upload('Cartellini_turni.pdf', url)
