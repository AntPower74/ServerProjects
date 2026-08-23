import csv
import gspread

SPREADSHEET_ID = '1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM'
CSV_PATH = 'verifica_turni_settembre_2026.csv'
CREDS_PATH = 'credentials.json'

DEPOT_TO_TAB = {
    'Torino': 'TO',
    'Perosa': 'PE',
    'Pinerolo': 'PI',
    'Piobesi': 'PB',
    'Pont': 'PT',
    'Luserna': 'LU',
}


def tab_for_row(row):
    dep_graph = row['Deposito (grafico)']
    if dep_graph in DEPOT_TO_TAB:
        return DEPOT_TO_TAB[dep_graph]
    dep_cart = row['Deposito (cartellino)']
    if 'Ivrea' in dep_cart:
        return 'IV'
    return None


def main():
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames
        rows = list(reader)

    by_tab = {}
    anomalie = []
    for row in rows:
        tab = tab_for_row(row)
        if tab is None:
            print("ATTENZIONE: turno senza deposito riconosciuto:", row['Turno'])
            continue
        by_tab.setdefault(tab, []).append(row)
        if row['Esito'] != 'OK':
            anomalie.append(row)

    gc = gspread.service_account(filename=CREDS_PATH)
    sh = gc.open_by_key(SPREADSHEET_ID)

    for tab, tab_rows in by_tab.items():
        ws = sh.worksheet(tab)
        values = [header] + [[r[h] for h in header] for r in tab_rows]
        ws.clear()
        ws.update(values, value_input_option='USER_ENTERED')
        print(f"{tab}: {len(tab_rows)} righe scritte")

    ws = sh.worksheet('Anomalie')
    values = [header] + [[r[h] for h in header] for r in anomalie]
    ws.clear()
    ws.update(values, value_input_option='USER_ENTERED')
    print(f"Anomalie: {len(anomalie)} righe scritte")


if __name__ == '__main__':
    main()
