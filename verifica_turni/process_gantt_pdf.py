import pdfplumber
import re
import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def extract_and_upload(pdf_path, client, spreadsheet):
    turni = []
    
    print(f"Elaborazione di {pdf_path}...")
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(layout=True)
            if not text: continue
            
            lines = text.split('\n')
            
            for i, line in enumerate(lines):
                if line.startswith("  01 "):
                    tokens = line.split()
                    if len(tokens) >= 2:
                        turno = tokens[1]
                        nastro = tokens[-1]
                        
                        line_above = lines[i-1].strip()
                        if line_above:
                            above_tokens = line_above.split()
                            if len(above_tokens) >= 2:
                                rip = above_tokens[-1]
                                olg_token = above_tokens[-2]
                                olg = re.sub(r'[^\d,]', '', olg_token)
                                
                                turni.append([turno, olg, nastro, rip])

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
            
        header = ["Nome Turno", "OLG", "Nastro Lavorativo", "Riprese"]
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
    
    extract_and_upload('Turni dal 100925_giov.base scolastico.pdf', client, spreadsheet)
