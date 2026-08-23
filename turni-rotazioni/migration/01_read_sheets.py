#!/usr/bin/env python3
"""One-time read of all 8 depot tabs from the Google Sheet into depots_raw.json.

Run with the existing verifica_turni venv:
  /home/antonio/verifica_turni/venv/bin/python3 migration/01_read_sheets.py

Reuses the service account already set up for verifica_turni/cartellini work.
"""
import json
import os
import re
import sys

import gspread
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = '/home/antonio/verifica_turni/credentials.json'
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID', '11hI0MBC6IMG5D8Sq7izljFElj2kazgQjSsjZTCCC42U')
OUT_PATH = os.path.join(os.path.dirname(__file__), 'depots_raw.json')

DEPOT_GIDS = {
    'TO': 114723232,
    'PI': 1430297395,
    'CA': 1682788033,
    'LU': 1898025534,
    'PT': 1268929728,
    'PE': 478345880,
    'GT': 1574000011,
    'PB': 1506119823,
}
DEPOT_NAMES = {
    'TO': 'Torino', 'PI': 'Pinerolo', 'CA': 'Caselle', 'LU': 'Luserna',
    'PT': 'Pont', 'PE': 'Perosa', 'GT': 'GT', 'PB': 'Piobesi',
}

MESI = {
    'gen': 1, 'gennaio': 1, 'feb': 2, 'febbraio': 2, 'mar': 3, 'marzo': 3,
    'apr': 4, 'aprile': 4, 'mag': 5, 'maggio': 5, 'giu': 6, 'giugno': 6,
    'lug': 7, 'luglio': 7, 'ago': 8, 'agosto': 8, 'set': 9, 'settembre': 9,
    'ott': 10, 'ottobre': 10, 'nov': 11, 'novembre': 11, 'dic': 12, 'dicembre': 12,
}


def parse_italian_date(s):
    """'3 novembre 2025' -> '2025-11-03'. Returns None if unparseable."""
    parts = s.strip().lower().split()
    if len(parts) != 3:
        return None
    day, month_name, year = parts
    month = MESI.get(month_name)
    if not month or not day.isdigit() or not year.isdigit():
        return None
    return f'{int(year):04d}-{month:02d}-{int(day):02d}'


def classify_label(label, used_types):
    """Map a column-A block label to a normalized block_type, handling the
    known CA/LU quirk where the 5th block is mislabeled 'Rotazione Festiva'
    again instead of 'Rotazione Natale' (positional: 2nd 'festiv' -> natale).
    Ad-hoc labels (e.g. 'Agosto dal 10 al 16') return block_type=None.
    """
    low = label.lower()
    if 'natale' in low:
        return 'natale', True
    if 'non scolastic' in low:
        return 'non_scolastico', True
    if 'scolastic' in low:
        return 'scolastico', True
    if 'festiv' in low:
        if 'festiva' in used_types:
            return 'natale', True  # 2nd occurrence = the CA/LU mislabeling quirk
        return 'festiva', True
    if low.strip() == 'rotazione agosto':
        return 'agosto', True
    return None, False  # ad-hoc block (e.g. "Agosto dal 10 al 16")


AGOSTO_RANGE_RE = re.compile(r'agosto\s+dal\s+(\d{1,2})\s+al\s+(\d{1,2})', re.IGNORECASE)


def read_depot(client, depot_id, gid):
    ss = client.open_by_key(SPREADSHEET_ID)
    ws = ss.get_worksheet_by_id(gid)
    rows = ws.get_all_values()

    header = rows[0]
    drivers = []
    for col_idx, name in enumerate(header[1:], start=1):  # column B = position 1
        name = name.strip()
        if name:
            drivers.append({'name': name, 'rotation_position': col_idx})

    # find every non-empty column-A label and its row index
    all_labels = [(i, row[0].strip()) for i, row in enumerate(rows) if row and row[0].strip()]

    # the footer (cycle_length, then reference_date) is NOT a rotation block: split it
    # off first so it isn't swept into the 7-row block loop below.
    labels = []
    footer_labels = []
    for row_i, label in all_labels:
        if not footer_labels and label.isdigit():
            footer_labels.append((row_i, label))
        elif footer_labels:
            footer_labels.append((row_i, label))
        else:
            labels.append((row_i, label))

    blocks = []
    used_types = set()
    footer_start = None
    for idx, (row_i, label) in enumerate(labels):
        block_type, is_known = classify_label(label, used_types)
        is_standard = bool(block_type)
        if is_standard:
            used_types.add(block_type)
        else:
            # ad-hoc block; try to auto-detect an "Agosto dal X al Y" special period
            block_type = re.sub(r'[^a-z0-9]+', '_', label.lower()).strip('_')

        # a block is 7 data rows starting right at its label row
        cells = []
        for weekday in range(7):
            r = row_i + weekday
            if r >= len(rows):
                break
            for driver in drivers:
                col = driver['rotation_position']
                val = rows[r][col].strip() if col < len(rows[r]) else ''
                cells.append({'weekday': weekday, 'col_index': col, 'turno_code': val or 'DISP'})

        agosto_range = AGOSTO_RANGE_RE.search(label)
        blocks.append({
            'label': label,
            'block_type': block_type,
            'is_standard': is_standard,
            'cells': cells,
            'agosto_day_range': [int(agosto_range.group(1)), int(agosto_range.group(2))] if agosto_range else None,
        })
    # footer: first entry is cycle_length (numeric), the next non-empty one is reference_date
    cycle_length = int(footer_labels[0][1]) if footer_labels else None
    reference_date = parse_italian_date(footer_labels[1][1]) if len(footer_labels) > 1 else None

    return {
        'id': depot_id,
        'name': DEPOT_NAMES[depot_id],
        'cycle_length': cycle_length,
        'reference_date': reference_date,
        'drivers': drivers,
        'blocks': blocks,
    }


def main():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)

    depots = {}
    for depot_id, gid in DEPOT_GIDS.items():
        print(f'reading {depot_id} (gid={gid})...', file=sys.stderr)
        depot = read_depot(client, depot_id, gid)
        warn = []
        if depot['cycle_length'] is None:
            warn.append('cycle_length not found')
        if depot['reference_date'] is None:
            warn.append('reference_date not parsed')
        standard_found = {b['block_type'] for b in depot['blocks'] if b['is_standard']}
        missing = {'scolastico', 'festiva', 'non_scolastico', 'agosto', 'natale'} - standard_found
        if missing:
            warn.append(f'missing standard blocks: {sorted(missing)}')
        if warn:
            print(f'  WARNING {depot_id}: {"; ".join(warn)}', file=sys.stderr)
        depots[depot_id] = depot

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(depots, f, ensure_ascii=False, indent=2)
    print(f'wrote {OUT_PATH}', file=sys.stderr)


if __name__ == '__main__':
    main()
