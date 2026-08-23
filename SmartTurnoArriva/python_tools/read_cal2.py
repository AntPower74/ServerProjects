import pandas as pd
df = pd.read_excel('/Calendario Scolastico/CAL2026-2027-14SETT-10GIU-DEFINITIVO.xls', header=None)
for col in df.columns[:10]:
    print(df[col].head(35).tolist())
