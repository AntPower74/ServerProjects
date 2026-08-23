import re
import gspread

from extract_html_2025 import extract_all, prefix_of

SPREADSHEET_ID = '1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM'
CREDS_PATH = 'credentials.json'
TAB_NAME = 'Turni2025_LunVen'

HEADER = ['Turno', 'Deposito (prefisso)', 'Descrizione', 'Inizio', 'Fine', 'Nastro', 'Riprese']


def turno_key(turno):
    m = re.match(r'([A-Za-z]+)(\d*)', turno)
    prefix, digits = m.group(1), m.group(2)
    return (prefix.lower(), int(digits) if digits else 0)


def main():
    data = extract_all()
    data.sort(key=lambda d: turno_key(d['turno']))

    rows = [[
        d['turno'], prefix_of(d['turno']), d['descrizione'], d['inizio'], d['fine'], d['nastro'],
        d['riprese'] if d['riprese'] is not None else ''
    ] for d in data]

    gc = gspread.service_account(filename=CREDS_PATH)
    sh = gc.open_by_key(SPREADSHEET_ID)
    try:
        ws = sh.worksheet(TAB_NAME)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=TAB_NAME, rows=250, cols=10)

    ws.clear()
    ws.update([HEADER] + rows, value_input_option='USER_ENTERED')
    print(f"{TAB_NAME}: {len(rows)} righe scritte")


if __name__ == '__main__':
    main()
