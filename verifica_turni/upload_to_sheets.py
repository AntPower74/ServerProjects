import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
import sys

def upload_csv_to_sheets(sheet_url, csv_path):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)
    
    try:
        sheet = client.open_by_url(sheet_url).sheet1
        print("Foglio trovato con successo! Pulisco i dati vecchi...")
        sheet.clear()
        
        print(f"Leggo i dati da {csv_path}...")
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            data = list(reader)
        
        print("Sto scrivendo i dati sul foglio...")
        sheet.update(range_name='A1', values=data)
        print("Fatto! Dati scritti con successo sul foglio Google.")
        
    except Exception as e:
        print(f"Errore durante l'aggiornamento del foglio: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python upload_to_sheets.py <sheet_url>")
        sys.exit(1)
    upload_csv_to_sheets(sys.argv[1], 'Cartellini_Turni.csv')
