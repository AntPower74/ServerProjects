import fitz
import re
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
        blocks = page.get_text('blocks')
        blocks = sorted(blocks, key=lambda b: b[1])
        
        shifts = []
        current_shift = None
        
        for b in blocks:
            x0, y0, x1, y1, text, block_no, block_type = b
            text = text.strip()
            
            # Check if it's a shift name
            if x0 < 30 and not text.startswith('(') and len(text) >= 2 and 'Crew Graph' not in text and 'Service:' not in text:
                if current_shift:
                    shifts.append(current_shift)
                current_shift = {'name': text, 'hours': '', 'blocks': []}
                continue
                
            if current_shift:
                current_shift['blocks'].append(b)
        
        if current_shift:
            shifts.append(current_shift)
            
        for s in shifts:
            nome = s['name']
            
            hours = ""
            for b in s['blocks']:
                t = b[4].strip()
                if t.startswith('(') and t.endswith(')') and ':' in t:
                    hours = t.replace('(', '').replace(')', '')
                    break
                    
            time_blocks = []
            for b in s['blocks']:
                t = b[4].strip()
                clean_t = re.sub(r'(.)\1{2}', r'\1', t)
                
                for line in clean_t.split('\n'):
                    line = line.strip()
                    if re.search(r'\d{2}:\d{2}', line):
                        match = re.search(r'\d{2}:\d{2}', line)
                        if match:
                            time_blocks.append((b[0], match.group()))
                            
            time_blocks.sort(key=lambda x: x[0])
            ordered_times = [t for _, t in time_blocks]
            unique_times = list(dict.fromkeys(ordered_times))
            
            row = [nome, hours] + unique_times
            turni.append(row)
            
    # Deduplicate turni maintaining order (using name and hours as key)
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
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=str(max(100, len(unique_turni)+10)), cols="20")
            
        # Determine max columns
        max_len = max(len(t) for t in unique_turni) if unique_turni else 2
        header = ["Nome Turno", "Ore Pagate"]
        
        num_pairs = (max_len - 2) // 2
        if (max_len - 2) % 2 != 0:
            num_pairs += 1
            
        for i in range(1, num_pairs + 1):
            header.extend([f"Inizio {i}", f"Fine {i}"])
            
        # Pad rows to max_len
        padded_data = []
        for t in unique_turni:
            padded_row = t + [""] * (len(header) - len(t))
            padded_data.append(padded_row)
            
        data_to_upload = [header] + padded_data
        
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
