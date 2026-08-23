import fitz
import sys
import glob
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def extract_and_upload(pdf_path, client, spreadsheet):
    print(f"Elaborazione di {pdf_path}...")
    doc = fitz.open(pdf_path)
    
    turni = []
    
    for page in doc:
        text = page.get_text('text')
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('(') and line.endswith(')') and ':' in line:
                if i > 0:
                    nome_turno = lines[i-1].strip()
                    if len(nome_turno) >= 2 and not nome_turno.startswith('('):
                        ore_pagate = line.replace('(', '').replace(')', '')
                        turni.append([nome_turno, ore_pagate])
                        
    # Deduplicate turni maintaining order
    seen = set()
    unique_turni = []
    for t in turni:
        key = f"{t[0]}_{t[1]}"
        if key not in seen:
            seen.add(key)
            unique_turni.append(t)

    # Upload to Google Sheets
    sheet_name = os.path.basename(pdf_path).replace('.pdf', '')
    
    try:
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=str(max(100, len(unique_turni)+10)), cols="5")
            
        header = ["Nome Turno", "Ore Pagate"]
        data_to_upload = [header] + unique_turni
        
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
    
    pdfs = glob.glob('Turni settembre 2026/Crew_Graph__*.pdf')
    for pdf in pdfs:
        extract_and_upload(pdf, client, spreadsheet)
