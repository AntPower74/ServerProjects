import gspread

SPREADSHEET_ID = '1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM'
CREDS_PATH = 'credentials.json'
HELPER_COL_LETTER = 'Q'  # colonna di supporto nascosta: K_minuti - C_minuti
HELPER_COL_IDX = 16  # 0-based (Q)
HELPER2_COL_LETTER = 'R'  # colonna di supporto nascosta: N_minuti - F_minuti (Nastro)
HELPER2_COL_IDX = 17  # 0-based (R)

RED = {'red': 0.8, 'green': 0.0, 'blue': 0.0}
GREEN = {'red': 0.0, 'green': 0.55, 'blue': 0.0}


def to_min(hhmm):
    if not hhmm or ':' not in hhmm:
        return None
    h, m = hhmm.split(':')
    return int(h) * 60 + int(m)


def main():
    gc = gspread.service_account(filename=CREDS_PATH)
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet('Turni2026')
    vals = ws.get_all_values()

    diffs = []
    diffs_nastro = []
    for row in vals[2:]:
        c = row[2] if len(row) > 2 else ''
        k = row[10] if len(row) > 10 else ''
        mc, mk = to_min(c), to_min(k)
        diffs.append([mk - mc if (mc is not None and mk is not None) else ''])

        f = row[5] if len(row) > 5 else ''
        n = row[13] if len(row) > 13 else ''
        mf, mn = to_min(f), to_min(n)
        diffs_nastro.append([mn - mf if (mf is not None and mn is not None) else ''])

    # scriviamo come frazione di giorno (minuti/1440) cosi possiamo formattarla come ore:minuti;
    # il segno (e quindi il confronto <0 />0 nelle regole sotto) resta invariato
    diffs_frac = [[v[0] / 1440 if v[0] != '' else ''] for v in diffs]
    diffs_nastro_frac = [[v[0] / 1440 if v[0] != '' else ''] for v in diffs_nastro]

    ws.update(range_name=f'{HELPER_COL_LETTER}3:{HELPER_COL_LETTER}{2 + len(diffs)}',
              values=diffs_frac, value_input_option='RAW')
    ws.update(range_name=f'{HELPER_COL_LETTER}2', values=[['diff K-C (ore, supporto)']], value_input_option='RAW')

    ws.update(range_name=f'{HELPER2_COL_LETTER}3:{HELPER2_COL_LETTER}{2 + len(diffs_nastro)}',
              values=diffs_nastro_frac, value_input_option='RAW')
    ws.update(range_name=f'{HELPER2_COL_LETTER}2', values=[['diff N-F (ore, supporto)']], value_input_option='RAW')

    # rimuovi eventuali regole già presenti
    meta = sh.fetch_sheet_metadata()
    sheet_meta = next(s for s in meta['sheets'] if s['properties']['sheetId'] == ws.id)
    n_existing = len(sheet_meta.get('conditionalFormats', []))
    delete_requests = [{'deleteConditionalFormatRule': {'sheetId': ws.id, 'index': 0}} for _ in range(n_existing)]

    k_range = {'sheetId': ws.id, 'startRowIndex': 2, 'startColumnIndex': 10, 'endColumnIndex': 11}
    n_range = {'sheetId': ws.id, 'startRowIndex': 2, 'startColumnIndex': 13, 'endColumnIndex': 14}
    helper_ref = f'${HELPER_COL_LETTER}3'
    helper2_ref = f'${HELPER2_COL_LETTER}3'

    def rule(idx, rng, ref, op, color):
        return {'addConditionalFormatRule': {
            'rule': {
                'ranges': [rng],
                'booleanRule': {
                    'condition': {'type': 'CUSTOM_FORMULA', 'values': [{'userEnteredValue': f'={ref}{op}0'}]},
                    'format': {'textFormat': {'foregroundColor': color, 'bold': True}},
                },
            },
            'index': idx,
        }}

    add_requests = [
        rule(0, k_range, helper_ref, '<', RED),
        rule(1, k_range, helper_ref, '>', GREEN),
        rule(2, n_range, helper2_ref, '<', RED),
        rule(3, n_range, helper2_ref, '>', GREEN),
    ]

    # colonne di supporto visibili, formattate come ore:minuti (con segno)
    show_and_format_requests = []
    for idx in (HELPER_COL_IDX, HELPER2_COL_IDX):
        show_and_format_requests.append({
            'updateDimensionProperties': {
                'range': {'sheetId': ws.id, 'dimension': 'COLUMNS', 'startIndex': idx, 'endIndex': idx + 1},
                'properties': {'hiddenByUser': False},
                'fields': 'hiddenByUser',
            }
        })
        show_and_format_requests.append({
            'repeatCell': {
                'range': {'sheetId': ws.id, 'startRowIndex': 2, 'startColumnIndex': idx, 'endColumnIndex': idx + 1},
                'cell': {'userEnteredFormat': {'numberFormat': {'type': 'TIME', 'pattern': '[h]:mm'}}},
                'fields': 'userEnteredFormat.numberFormat',
            }
        })

    sh.batch_update({'requests': delete_requests + add_requests + show_and_format_requests})
    print("Colonne Q/R aggiornate (formato ore:minuti, visibili), formattazione condizionale applicata.")


if __name__ == '__main__':
    main()
