import re
import gspread

from extract_crew_graph_2025 import extract_file_shifts

SPREADSHEET_ID = '1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM'
CREDS_PATH = 'credentials.json'
PDF_PATH = 'turni scolastici 2025 grafici/Turni dal 100925_giov.base scolastico.pdf'
TAB_NAME = 'Turni2025'

HEADER = ['Turno', 'Inizio (grafico)', 'Fine (grafico)', 'Nastro (grafico)', 'Riprese (grafico)']


def turno_key(turno):
    m = re.match(r'([A-Za-z]+)(\d*)', turno)
    prefix, digits = m.group(1), m.group(2)
    return (prefix.lower(), int(digits) if digits else 0)


def main():
    shifts = extract_file_shifts(PDF_PATH)
    shifts.sort(key=lambda s: turno_key(s['turno']))

    rows = [[
        s['turno'], s['inizio_grafico'], s['fine_grafico'], s['nastro_grafico'], s['n_riprese']
    ] for s in shifts]

    gc = gspread.service_account(filename=CREDS_PATH)
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(TAB_NAME)
    ws.clear()
    ws.update([HEADER] + rows, value_input_option='USER_ENTERED')
    print(f"{TAB_NAME}: {len(rows)} righe scritte")


if __name__ == '__main__':
    main()
