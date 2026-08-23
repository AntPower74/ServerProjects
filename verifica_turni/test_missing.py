import fitz
import glob
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_shift_names(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]
    blocks = page.get_text('blocks')
    blocks = sorted(blocks, key=lambda b: b[1])
    shifts = []
    for b in blocks:
        x0, y0, x1, y1, text, block_no, block_type = b
        text = text.strip()
        if x0 < 30 and not text.startswith('(') and len(text) >= 2 and 'Crew Graph' not in text and 'Service:' not in text:
            shifts.append(text)
    return shifts

all_shifts = []
pdfs = glob.glob('Turni settembre 2026/Crew_Graph__*.pdf')
for pdf in pdfs:
    all_shifts.extend(get_shift_names(pdf))

print(f"Shifts in PDFs (total {len(all_shifts)}):")
print(all_shifts)

url = "https://docs.google.com/spreadsheets/d/1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM/edit?gid=715797777#gid=715797777"
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
ws = client.open_by_url(url).worksheet('Tabella Turni scol 2026')

sheet_shifts = []
for row in ws.get_all_values():
    if row:
        t_name = row[0].strip()
        if t_name:
            sheet_shifts.append(t_name)

print("\nShifts in Sheet:")
print(sheet_shifts)

missing = []
for s in all_shifts:
    if s not in sheet_shifts and s + '0' not in sheet_shifts:
        missing.append(s)

print("\nShifts found in PDF but not updated in Sheet:")
print(missing)

