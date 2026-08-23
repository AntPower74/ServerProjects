#!/usr/bin/env python3
"""Derives the shared holidays/calendar_ranges tables from the Google Sheet's own
"Calendario" tab helper columns (Scolastico/Festivo/Natale booleans), instead of
typing an Italian holiday calendar by hand - the sheet already has this classified
per date, we just read it once.

Run with the verifica_turni venv (has gspread already):
  /home/antonio/verifica_turni/venv/bin/python3 migration/03_seed_calendar.py

Writes directly to the same SQLite file the Node backend uses (data/turni.db) -
SQLite is a plain file format, safe to write from Python as long as the Node
server isn't writing at the exact same moment (it isn't, during migration).
"""
import os
import re
import sqlite3
import sys

import gspread
from oauth2client.service_account import ServiceAccountCredentials

CREDENTIALS_FILE = '/home/antonio/verifica_turni/credentials.json'
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID', '11hI0MBC6IMG5D8Sq7izljFElj2kazgQjSsjZTCCC42U')
CALENDARIO_GID = 991701353
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'turni.db')

# rows 3..367 = 1 Jan 2026 .. 31 Dec 2026 (confirmed by direct read earlier today).
FIRST_ROW = 3
LAST_ROW = 367

MESI = {
    'gen': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'mag': 5, 'giu': 6,
    'lug': 7, 'ago': 8, 'set': 9, 'ott': 10, 'nov': 11, 'dic': 12,
}


def parse_calendario_date(s):
    """'gio 1 gen 26' -> '2026-01-01'"""
    parts = s.strip().split()
    if len(parts) != 4:
        return None
    _, day, mon, yy = parts
    month = MESI.get(mon.lower())
    if not month:
        return None
    return f'20{yy}-{month:02d}-{int(day):02d}'


def find_header_column(header_row, label):
    for i, h in enumerate(header_row):
        if h.strip() == label:
            return i + 1  # 1-based for gspread A1 ranges
    raise ValueError(f'header {label!r} not found in Calendario row 1')


def col_letter(n):
    s = ''
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def contiguous_ranges(dates, flags):
    """dates/flags aligned lists -> list of (start_date, end_date) for contiguous True runs."""
    ranges = []
    start = None
    prev_date = None
    for date, flag in zip(dates, flags):
        if flag and start is None:
            start = date
        elif not flag and start is not None:
            ranges.append((start, prev_date))
            start = None
        prev_date = date
    if start is not None:
        ranges.append((start, prev_date))
    return ranges


def main():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    cal = client.open_by_key(SPREADSHEET_ID).get_worksheet_by_id(CALENDARIO_GID)

    header = cal.row_values(1)
    col_scolastico = col_letter(find_header_column(header, 'Scolastico'))
    col_festivo = col_letter(find_header_column(header, 'Festivo (8)'))
    col_natale = col_letter(find_header_column(header, 'Natale'))
    print(f'columns: Scolastico={col_scolastico} Festivo={col_festivo} Natale={col_natale}', file=sys.stderr)

    a_vals = cal.get(f'A{FIRST_ROW}:A{LAST_ROW}')
    scol_vals = cal.get(f'{col_scolastico}{FIRST_ROW}:{col_scolastico}{LAST_ROW}')
    fest_vals = cal.get(f'{col_festivo}{FIRST_ROW}:{col_festivo}{LAST_ROW}')
    nat_vals = cal.get(f'{col_natale}{FIRST_ROW}:{col_natale}{LAST_ROW}')

    dates, scolastico, festivo, natale = [], [], [], []
    for a, s, f, n in zip(a_vals, scol_vals, fest_vals, nat_vals):
        iso = parse_calendario_date(a[0]) if a else None
        if not iso:
            continue
        dates.append(iso)
        scolastico.append((s[0] if s else '').strip().upper() == 'TRUE')
        festivo.append((f[0] if f else '').strip().upper() == 'TRUE')
        natale.append((n[0] if n else '').strip().upper() == 'TRUE')

    scolastico_ranges = contiguous_ranges(dates, scolastico)
    natale_ranges = contiguous_ranges(dates, natale)
    holiday_dates = [d for d, is_h in zip(dates, festivo) if is_h]

    print(f'{len(scolastico_ranges)} scolastico ranges, {len(natale_ranges)} natale ranges, '
          f'{len(holiday_dates)} holiday dates', file=sys.stderr)

    conn = sqlite3.connect(DB_PATH)
    conn.execute('DELETE FROM calendar_ranges')
    conn.execute('DELETE FROM holidays')
    conn.executemany(
        'INSERT INTO calendar_ranges (kind, start_date, end_date, label) VALUES (?, ?, ?, ?)',
        [('scolastico', s, e, None) for s, e in scolastico_ranges]
        + [('natale', s, e, None) for s, e in natale_ranges],
    )
    conn.executemany(
        'INSERT OR REPLACE INTO holidays (date, label) VALUES (?, ?)',
        [(d, None) for d in holiday_dates],
    )
    conn.commit()
    conn.close()
    print('done.', file=sys.stderr)


if __name__ == '__main__':
    main()
