import re
import gspread

SPREADSHEET_ID = '1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM'
CREDS_PATH = 'credentials.json'


def build_25_index(vals25):
    idx = {}
    for r in vals25[1:]:
        if r and r[0]:
            idx[r[0].upper()] = r  # Turno, Deposito, Descrizione, Inizio, Fine, Nastro, Riprese
    return idx


def find_match(turno26, idx25):
    key = turno26.upper()
    if key in idx25:
        return idx25[key]
    m = re.match(r'([A-Za-z]+)(\d+)$', key)
    if m:
        alt_key = f"{m.group(1)}{m.group(2)}0"
        if alt_key in idx25:
            return idx25[alt_key]
    return None


def main():
    gc = gspread.service_account(filename=CREDS_PATH)
    sh = gc.open_by_key(SPREADSHEET_ID)

    ws26 = sh.worksheet('Turni2026')
    ws25 = sh.worksheet('Turni2025_LunVen')

    vals26 = ws26.get_all_values()
    vals25 = ws25.get_all_values()
    idx25 = build_25_index(vals25)

    n_match = 0
    left_rows = []
    for row in vals26[2:]:  # data starts at row 3 (index 2)
        turno26 = row[8] if len(row) > 8 else ''
        if not turno26:
            left_rows.append(['', '', '', '', '', '', ''])
            continue
        match = find_match(turno26, idx25)
        if match:
            n_match += 1
            left_rows.append(match[:7] + [''] * (7 - len(match[:7])))
        else:
            left_rows.append(['', '', '', '', '', '', ''])

    ws26.update(f'A3:G{2 + len(left_rows)}', left_rows, value_input_option='RAW')
    print(f"Righe aggiornate: {len(left_rows)}, trovate corrispondenze: {n_match}")


if __name__ == '__main__':
    main()
