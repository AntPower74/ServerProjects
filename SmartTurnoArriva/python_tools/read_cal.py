import pandas as pd
import sys

try:
    df = pd.read_excel('/Calendario Scolastico/CAL2026-2027-14SETT-10GIU-DEFINITIVO.xls')
    print(df.head(20))
except Exception as e:
    print(f"Error: {e}")
