import pandas as pd
from datetime import datetime

df = pd.read_excel('/Calendario Scolastico/CAL2026-2027-14SETT-10GIU-DEFINITIVO.xls', header=None)

months_map = {
    'settembre': 9, 'ottobre': 10, 'novembre': 11, 'dicembre': 12, 'dicembre ': 12,
    'gennaio': 1, 'febbraio': 2, 'marzo': 3, 'aprile': 4, 'maggio': 5, 'giugno': 6,
    'luglio': 7, 'agosto': 8
}

data = []
year = 2026

for c in range(0, len(df.columns), 3):
    col_month = df.iloc[:, c].tolist()
    col_dayweek = df.iloc[:, c+1].tolist() if c+1 < len(df.columns) else []
    col_note = df.iloc[:, c+2].tolist() if c+2 < len(df.columns) else []
    
    month_num = None
    start_row = 0
    for r in range(len(col_month)):
        val = str(col_month[r]).strip().lower()
        if val in months_map:
            month_num = months_map[val]
            start_row = r + 1
            if month_num == 1:
                year = 2027
            break
            
    if not month_num: continue
    
    for r in range(start_row, len(col_month)):
        day_val = col_month[r]
        if pd.isna(day_val): continue
        try:
            day = int(float(day_val))
        except:
            continue
            
        dw = str(col_dayweek[r]).strip().lower() if r < len(col_dayweek) else ''
        note = str(col_note[r]).strip() if r < len(col_note) and not pd.isna(col_note[r]) else ''
        
        # Base logic for Tipo:
        tipo = 'Scolastico'
        if dw == 'dom.' or dw == 'sab.':
            tipo = 'Festivo' if dw == 'dom.' else 'Scolastico' # wait, Saturday is often Scolastico in Italy
        if note and 'FESTA' in note.upper() or note.upper() == 'SANTI' or 'NATALE' in note.upper() or 'PASQUA' in note.upper():
            tipo = 'Festivo'
            
        # Summer break
        if month_num in [7, 8]:
            tipo = 'Vacanza (Estiva)'
        if month_num == 6 and day > 10:
            tipo = 'Vacanza (Estiva)'
        if month_num == 9 and day < 14:
            tipo = 'Vacanza (Estiva)'
            
        data.append({
            'Data': f"{day:02d}/{month_num:02d}/{year}",
            'Giorno': dw,
            'Tipo': tipo,
            'Nota': note
        })

df_out = pd.DataFrame(data)
df_out.to_csv('/root/orari-app/Calendario_Scolastico.csv', index=False)
print("Generated /root/orari-app/Calendario_Scolastico.csv")
