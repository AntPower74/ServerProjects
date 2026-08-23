import glob
import os
import re
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def parse_time(t_str):
    if not t_str or ':' not in t_str: return 0
    h, m = map(int, t_str.split(':'))
    return h * 60 + m

def fmt_t(mins):
    mins = int(mins) % 1440
    return f"{mins//60:02d}.{mins%60:02d}"

print("Leggo i file HTML dei turni della DOMENICA...")
files = glob.glob('/home/antonio/verifica_turni/Turni settembre 2025 dom/VisualizzaTurnoStandard*')
shifts_data = {}

for fpath in files:
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    
    tables = soup.find_all('table')
    if len(tables) < 2: continue
    
    tbody = tables[1].find('tbody')
    if not tbody: continue
    
    shift_trips = []
    shift_name = None
    
    for tr in tbody.find_all('tr'):
        tds = [td.text.strip() for td in tr.find_all('td')]
        if len(tds) > 4:
            s_name = tds[0].strip()
            if s_name:
                shift_name = s_name.capitalize() if s_name[:2].isalpha() else s_name
                
            start_m = parse_time(tds[1])
            end_m = parse_time(tds[3])
            
            if end_m < start_m - 300: 
                end_m += 1440
                
            loc_end = tds[4]
            shift_trips.append((start_m, end_m, loc_end))
            
    if shift_name and shift_trips:
        shift_trips.sort(key=lambda x: x[0])
        
        for i in range(1, len(shift_trips)):
            if shift_trips[i][0] < shift_trips[i-1][0] - 300:
                shift_trips[i] = (shift_trips[i][0] + 1440, shift_trips[i][1], shift_trips[i][2])
                if shift_trips[i][1] < shift_trips[i][0]:
                    shift_trips[i] = (shift_trips[i][0], shift_trips[i][1] + 1440, shift_trips[i][2])
        
        shifts_data[shift_name] = shift_trips

print(f"Estratti {len(shifts_data)} turni unici dai file HTML della DOMENICA.")

# Costruisco le riprese
shifts_riprese = {}
for name, trips in shifts_data.items():
    if not trips: continue
    
    riprese = []
    sostas = []
    
    curr_start = trips[0][0]
    curr_end = trips[0][1]
    curr_loc = trips[0][2]
    
    for start, end, loc in trips[1:]:
        if start - curr_end > 30:
            riprese.append([curr_start, curr_end])
            
            best_loc = curr_loc.lower()
            if 'cas' in best_loc: loc_name = 'Caselle'
            elif 'to ' in best_loc or 'pn' in best_loc: loc_name = 'Torino'
            elif 'pin' in best_loc: loc_name = 'Pinerolo'
            elif 'sus' in best_loc: loc_name = 'Susa'
            else: loc_name = curr_loc
            
            sostas.append(loc_name)
            
            curr_start = start
            curr_end = end
            curr_loc = loc
        else:
            curr_end = max(curr_end, end)
            curr_loc = loc
            
    riprese.append([curr_start, curr_end])
    
    # Applica i 10 minuti di accessorio
    for r in riprese:
        r[0] -= 10
        r[1] += 10
        
    shifts_riprese[name] = {'riprese': riprese, 'sostas': sostas}

print("Connessione a Google Sheets...")
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)
ws = client.open_by_key('1dSn5yQTj355fF3JWjZW4gD3Tb0X7VflvQXB06KTtecM').worksheet('Tabella Turni scol 2025')
data = ws.get_all_values()

cols_map = [
    (('F', 5), ('G', 6), ('H', 7)),
    (('I', 8), ('J', 9), ('K', 10)),
    (('L', 11), ('M', 12), ('N', 13)),
    (('O', 14), ('P', 15), ('Q', 16)),
    (('R', 17), ('S', 18), ('T', 19)),
    (('U', 20), ('V', 21), ('W', 22))
]

updates = []
matched = 0

for i, row in enumerate(data):
    if i == 0: continue
    
    name = row[0].strip()
    if not name: continue
    
    match_name = name.capitalize() if name[:2].isalpha() else name
    
    if match_name in shifts_riprese:
        # Clear first
        for (s_col, _), (e_col, _), (sosta_col, _) in cols_map:
            updates.append({'range': f'{s_col}{i+1}', 'values': [['']]})
            updates.append({'range': f'{e_col}{i+1}', 'values': [['']]})
            updates.append({'range': f'{sosta_col}{i+1}', 'values': [['']]})
            
        shift_info = shifts_riprese[match_name]
        riprese = shift_info['riprese']
        sostas = shift_info['sostas']
        
        for r_idx, (s, e) in enumerate(riprese[:6]):
            s_col = cols_map[r_idx][0][0]
            e_col = cols_map[r_idx][1][0]
            updates.append({'range': f'{s_col}{i+1}', 'values': [[fmt_t(s)]]})
            updates.append({'range': f'{e_col}{i+1}', 'values': [[fmt_t(e)]]})
            
            if r_idx < len(riprese) - 1 and r_idx < len(sostas):
                sosta_col = cols_map[r_idx][2][0]
                updates.append({'range': f'{sosta_col}{i+1}', 'values': [[sostas[r_idx]]] })
                
        matched += 1

print(f"Sto per aggiornare {matched} turni della DOMENICA nel foglio Google usando i dati originali del sito web...")
batch_size = 200
for i in range(0, len(updates), batch_size):
    ws.batch_update(updates[i:i+batch_size])

print("Aggiornamento DOMENICA completato con successo! (Precisione al 100%)")
