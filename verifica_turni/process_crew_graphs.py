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
            
            # Pulisce i caratteri duplicati 3 volte (es. 000999:::222000 -> 09:20)
            clean_text = re.sub(r'(.)\1{2}', r'\1', text)
            lines = clean_text.split('\n')
            
            current_starts = []
            
            for line in lines:
                # Trova orari di inizio (positivi, es: 09:20, ma ignoriamo quelli che iniziano con - o –)
                # Attenzione al trattino lungo e corto
                if re.search(r'(?<![-–])\b\d{2}:\d{2}\b', line):
                    # Trova tutti gli orari che non hanno un trattino davanti
                    starts = re.findall(r'(?<![-–])\b\d{2}:\d{2}\b', line)
                    if starts:
                        current_starts = starts
                
                # Trova orari di fine (preceduti da - o –)
                if re.search(r'[-–]\d{2}:\d{2}\b', line):
                    ends = re.findall(r'[-–](\d{2}:\d{2})\b', line)
                    if ends and current_starts:
                        # Abbiamo una coppia Inizio/Fine
                        row = ["Turno Anonimo (Grafico)"]
                        for s, e in zip(current_starts, ends):
                            row.extend([s, e])
                        turni.append(row)
                        current_starts = []

    # Upload to Google Sheets
    sheet_name = os.path.basename(pdf_path).replace('.pdf', '')
    
    try:
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            print(f"Foglio '{sheet_name}' trovato, lo pulisco...")
            worksheet.clear()
        except gspread.exceptions.WorksheetNotFound:
            print(f"Creo il nuovo foglio '{sheet_name}'...")
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=str(max(100, len(turni)+10)), cols="20")
            
        header = ["Nome Turno", "Inizio 1", "Fine 1", "Inizio 2", "Fine 2", "Inizio 3", "Fine 3", "Inizio 4", "Fine 4"]
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
    
    pdfs = glob.glob('Turni settembre 2026/Crew_Graph__*.pdf')
    for pdf in pdfs:
        extract_and_upload(pdf, client, spreadsheet)
