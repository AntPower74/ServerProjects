import re
import gspread

from extract_olg_2025 import extract_olg_by_turno

SPREADSHEET_ID = '1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM'
CREDS_PATH = 'credentials.json'
PDF_PATH = 'turni scolastici 2025 grafici/Turni dal 100925_giov.base scolastico.pdf'


def find_match(turno26, olg_dict):
    key = turno26.upper()
    if key in olg_dict:
        return olg_dict[key]
    m = re.match(r'([A-Za-z]+)(\d+)$', key)
    if m:
        alt_key = f"{m.group(1)}{m.group(2)}0"
        if alt_key in olg_dict:
            return olg_dict[alt_key]
    return None


def main():
    olg_dict = extract_olg_by_turno(PDF_PATH)

    gc = gspread.service_account(filename=CREDS_PATH)
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws26 = sh.worksheet('Turni2026')
    vals26 = ws26.get_all_values()

    n_match = 0
    col_c = []
    for row in vals26[2:]:
        turno26 = row[8] if len(row) > 8 else ''
        if not turno26:
            col_c.append([''])
            continue
        val = find_match(turno26, olg_dict)
        if val:
            n_match += 1
            col_c.append([val])
        else:
            col_c.append([''])

    ws26.update(range_name=f'C3:C{2 + len(col_c)}', values=col_c, value_input_option='RAW')
    ws26.update(range_name='C2', values=[['OLG (grafico)']], value_input_option='RAW')
    print(f"Colonna C aggiornata: {len(col_c)} righe, {n_match} corrispondenze trovate")


if __name__ == '__main__':
    main()
