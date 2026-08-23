import glob
import re
import gspread

from extract_crew_graph import extract_file_shifts
from build_report import dep_label, nastro_grafico

SPREADSHEET_ID = '1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM'
CREDS_PATH = 'credentials.json'
GRAPH_FILES = sorted(glob.glob('Turni settembre 2026/Crew_Graph__*.pdf'))
TAB_NAME = 'Tutti i Turni'

HEADER = ['Turno', 'Deposito', 'Tempo Pagato (grafico)', 'Inizio (grafico)', 'Fine (grafico)', 'Nastro (grafico)', 'Riprese (grafico)']


def main():
    rows = []
    for gf in GRAPH_FILES:
        label = dep_label(gf)
        for s in extract_file_shifts(gf):
            rows.append([
                s['turno'],
                label,
                s['paid_graph'],
                s['inizio_grafico'],
                s['fine_grafico'],
                nastro_grafico(s['inizio_grafico'], s['fine_grafico']),
                s['n_riprese'],
            ])

    def turno_key(turno):
        m = re.match(r'([A-Za-z]+)(\d*)', turno)
        prefix, digits = m.group(1), m.group(2)
        return (prefix.lower(), int(digits) if digits else 0)

    rows.sort(key=lambda r: (r[1], turno_key(r[0])))

    gc = gspread.service_account(filename=CREDS_PATH)
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(TAB_NAME)
    ws.clear()
    ws.update([HEADER] + rows, value_input_option='USER_ENTERED')
    print(f"{TAB_NAME}: {len(rows)} righe scritte")


if __name__ == '__main__':
    main()
