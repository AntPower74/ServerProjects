import re
import gspread

from extract_cartellini_2025 import parse_pdf
from extract_html_2025 import extract_all as extract_html_2025_all

SPREADSHEET_ID = '1rYNF0ACFfsICiMWFID_6NCRE47WDmcJnFB24kFQ8aSM'
CREDS_PATH = 'credentials.json'
TAB_NAME = 'Comparazione'
CARTELLINI_2025 = ['cartellini2025/cartellini_4sb025.pdf', 'cartellini2025/cartellini_cas32.pdf']

HEADER = ['Turno', 'Deposito (2026)',
          'Ore Pagate 2025', 'Ore Pagate 2026', 'Delta Ore Pagate', 'Esito Ore Pagate',
          'Nastro 2025', 'Nastro 2026', 'Delta Nastro', 'Esito Nastro',
          'Riprese 2025', 'Riprese 2026', 'Delta Riprese', 'Esito Riprese',
          'Presenza', 'Differenza Riduzione (min)']


def format_delta(minutes):
    if minutes is None:
        return ''
    if minutes == 0:
        return '0'
    sign = '-' if minutes < 0 else ''
    m = abs(minutes)
    return f"{sign}{m // 60}:{m % 60:02d}"


def to_min(hhmm):
    if not hhmm:
        return None
    sep = ':' if ':' in hhmm else '.'
    h, m = hhmm.split(sep)
    return int(h) * 60 + int(m)


def load_2025_merged():
    """Merge cartellini PDF (has Ore Pagate) with HTML export (wider coverage),
    matching turno codes case-insensitively. PDF data wins when both exist."""
    merged = {}  # key = UPPER(turno) -> dict(display, ore_lavoro_giornaliero, nastro_turno, numero_riprese, fonte)

    for pdf_path in CARTELLINI_2025:
        for t in parse_pdf(pdf_path):
            key = t['turno'].upper()
            merged[key] = {
                'display': t['turno'],
                'ore_lavoro_giornaliero': t['ore_lavoro_giornaliero'],
                'nastro_turno': t['nastro_turno'],
                'numero_riprese': t['numero_riprese'],
                'fonte': 'cartellino',
            }

    for d in extract_html_2025_all():
        key = d['turno'].upper()
        if key in merged:
            continue  # cartellino data already present and preferred
        merged[key] = {
            'display': d['turno'],
            'ore_lavoro_giornaliero': '',
            'nastro_turno': d['nastro'],
            'numero_riprese': str(d['riprese']) if d['riprese'] is not None else '',
            'fonte': 'html',
        }

    return merged


def turno_key(turno):
    m = re.match(r'([A-Za-z]+)(\d*)', turno)
    prefix, digits = m.group(1), m.group(2)
    return (prefix.lower(), int(digits) if digits else 0)


def esito_lower_better(delta):
    if delta is None:
        return ''
    if delta < 0:
        return '👍'
    if delta > 0:
        return '👎'
    return '='


def esito_higher_better(delta):
    if delta is None:
        return ''
    if delta > 0:
        return '👍'
    if delta < 0:
        return '👎'
    return '='


def main():
    gc = gspread.service_account(filename=CREDS_PATH)
    sh = gc.open_by_key(SPREADSHEET_ID)

    vals26 = sh.worksheet('Turni2026').get_all_values()[1:]
    by26 = {r[0].upper(): r for r in vals26}  # key = UPPER(turno)
    by25 = load_2025_merged()  # key = UPPER(turno)

    # Il 2025 a volte numera lo stesso turno con uno "0" finale in più
    # (es. 2026 "Pe001" == 2025 "PE0010"). Riallineo quelle chiavi su quella 2026.
    n_realigned = 0
    for key26 in list(by26):
        if key26 in by25:
            continue
        m = re.match(r'([A-Za-z]+)(\d+)$', key26)
        if not m:
            continue
        alt_key = f"{m.group(1)}{m.group(2)}0"
        if alt_key in by25:
            by25[key26] = by25.pop(alt_key)
            n_realigned += 1
    if n_realigned:
        print(f"Riallineati {n_realigned} turni 2025 con '0' finale in più al codice 2026 corrispondente")

    common = sorted(set(by26) & set(by25))
    only26 = sorted(set(by26) - set(by25))
    only25 = sorted(set(by25) - set(by26))
    all_keys = sorted(set(by26) | set(by25), key=turno_key)

    rows = []
    for key in all_keys:
        r26 = by26.get(key)  # Turno, Deposito, Tempo Pagato, Inizio, Fine, Nastro, Riprese
        r25 = by25.get(key)  # dict: display, ore_lavoro_giornaliero, nastro_turno, numero_riprese, fonte

        turno = r26[0] if r26 is not None else r25['display']

        if r26 is None:
            rows.append([turno, '', r25['ore_lavoro_giornaliero'], '', '', '',
                         r25['nastro_turno'], '', '', '',
                         r25['numero_riprese'], '', '', '', 'SOLO 2025', ''])
            continue
        if r25 is None:
            rows.append([turno, r26[1], '', r26[2], '', '',
                         '', r26[5], '', '',
                         '', r26[6], '', '', 'SOLO 2026', ''])
            continue

        pagate25, pagate26 = r25['ore_lavoro_giornaliero'], r26[2]
        d_pagate = to_min(pagate26) - to_min(pagate25) if pagate25 and pagate26 else None
        e_pagate = esito_higher_better(d_pagate)

        nastro25, nastro26 = r25['nastro_turno'], r26[5]
        d_nastro = to_min(nastro26) - to_min(nastro25)
        e_nastro = esito_lower_better(d_nastro)

        riprese25 = int(float(r25['numero_riprese'])) if r25['numero_riprese'] else None
        riprese26 = int(r26[6])
        d_riprese = riprese26 - riprese25 if riprese25 is not None else None
        e_riprese = esito_lower_better(d_riprese)

        diff_riduzione = d_pagate - d_nastro if d_pagate is not None else ''

        rows.append([
            turno, r26[1],
            pagate25, pagate26, format_delta(d_pagate), e_pagate,
            nastro25, nastro26, format_delta(d_nastro), e_nastro,
            riprese25 if riprese25 is not None else '', riprese26, d_riprese if d_riprese is not None else '', e_riprese,
            '✓', diff_riduzione,
        ])

    gc = gspread.service_account(filename=CREDS_PATH)
    sh = gc.open_by_key(SPREADSHEET_ID)
    try:
        ws = sh.worksheet(TAB_NAME)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=TAB_NAME, rows=300, cols=10)

    ws.clear()
    ws.update([HEADER] + rows, value_input_option='RAW')

    # rimuovi eventuali regole di formattazione condizionale già presenti su questo foglio
    meta = sh.fetch_sheet_metadata()
    sheet_meta = next(s for s in meta['sheets'] if s['properties']['sheetId'] == ws.id)
    n_existing_rules = len(sheet_meta.get('conditionalFormats', []))
    delete_requests = [
        {'deleteConditionalFormatRule': {'sheetId': ws.id, 'index': 0}}
        for _ in range(n_existing_rules)
    ]

    GREEN_BG = {'red': 0.72, 'green': 0.88, 'blue': 0.72}
    RED_BG = {'red': 0.96, 'green': 0.73, 'blue': 0.73}

    def rule_request(col_idx, value, color, index):
        return {
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [{
                        'sheetId': ws.id,
                        'startRowIndex': 1,
                        'startColumnIndex': col_idx,
                        'endColumnIndex': col_idx + 1,
                    }],
                    'booleanRule': {
                        'condition': {'type': 'TEXT_EQ', 'values': [{'userEnteredValue': value}]},
                        'format': {'backgroundColor': color},
                    },
                },
                'index': index,
            }
        }

    presenza_col = HEADER.index('Presenza')
    esito_cols = [HEADER.index('Esito Ore Pagate'), HEADER.index('Esito Nastro'), HEADER.index('Esito Riprese')]

    add_requests = [rule_request(presenza_col, '✓', GREEN_BG, 0)]
    idx = 1
    for col in esito_cols:
        add_requests.append(rule_request(col, '👍', GREEN_BG, idx))
        idx += 1
        add_requests.append(rule_request(col, '👎', RED_BG, idx))
        idx += 1

    sh.batch_update({'requests': delete_requests + add_requests})

    from collections import Counter
    confrontati = [r for r in rows if r[14] == '✓']
    c_pagate = Counter(r[5] for r in confrontati)
    c_nastro = Counter(r[9] for r in confrontati)
    c_riprese = Counter(r[13] for r in confrontati)
    print(f"Turni totali (unione): {len(all_keys)}")
    print(f"Turni comuni confrontati: {len(common)}")
    print(f"  Ore Pagate -> {dict(c_pagate)}")
    print(f"  Nastro -> {dict(c_nastro)}")
    print(f"  Riprese -> {dict(c_riprese)}")
    print(f"Solo 2026 (nuovi): {len(only26)}")
    print(f"Solo 2025 (non più presenti / rinumerati): {len(only25)}")
    print(f"Scritto su '{TAB_NAME}': {len(rows)} righe")


if __name__ == '__main__':
    main()
