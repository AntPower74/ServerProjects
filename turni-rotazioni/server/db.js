import sqlite3 from 'sqlite3';
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DB_PATH = process.env.DB_PATH || path.join(__dirname, '..', 'data', 'turni.db');

fs.mkdirSync(path.dirname(DB_PATH), { recursive: true });

const sqlite = sqlite3.verbose();
export const db = new sqlite.Database(DB_PATH);

db.serialize(() => {
  db.run('PRAGMA foreign_keys = ON');

  db.run(`CREATE TABLE IF NOT EXISTS depots (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    cycle_length INTEGER NOT NULL,
    reference_date TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS drivers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    depot_id TEXT NOT NULL REFERENCES depots(id),
    name TEXT NOT NULL,
    rotation_position INTEGER NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(depot_id, rotation_position)
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS rotation_blocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    depot_id TEXT NOT NULL REFERENCES depots(id),
    block_type TEXT NOT NULL,
    label TEXT NOT NULL,
    is_standard INTEGER NOT NULL DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS rotation_cells (
    block_id INTEGER NOT NULL REFERENCES rotation_blocks(id) ON DELETE CASCADE,
    weekday INTEGER NOT NULL,
    col_index INTEGER NOT NULL,
    turno_code TEXT NOT NULL DEFAULT 'DISP',
    PRIMARY KEY (block_id, weekday, col_index)
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS special_periods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    depot_id TEXT NOT NULL REFERENCES depots(id),
    label TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    block_id INTEGER NOT NULL REFERENCES rotation_blocks(id),
    priority INTEGER NOT NULL DEFAULT 0,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS holidays (
    date TEXT PRIMARY KEY,
    label TEXT
  )`);

  db.run(`CREATE TABLE IF NOT EXISTS calendar_ranges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    label TEXT
  )`);

  // Calendario scolastico parametrico, importato dal tab "CalendarioSCOL" del
  // foglio Google (copre 2017-2050) - un anno per riga, non un elenco di date.
  // Da qui si derivano poi calendar_ranges/holidays per il calcolo dei turni.
  db.run(`CREATE TABLE IF NOT EXISTS school_calendar_years (
    year INTEGER PRIMARY KEY,
    easter_date TEXT,
    summer_end_day_june INTEGER,
    summer_start_day_september INTEGER,
    agosto_start_day INTEGER,
    agosto_end_day INTEGER,
    carnevale1_day INTEGER,
    carnevale1_month INTEGER,
    carnevale2_day INTEGER,
    carnevale2_month INTEGER,
    epifania_active INTEGER NOT NULL DEFAULT 0,
    liberazione_active INTEGER NOT NULL DEFAULT 0,
    lavoro_active INTEGER NOT NULL DEFAULT 0,
    forze_armate_active INTEGER NOT NULL DEFAULT 0,
    tutti_santi_active INTEGER NOT NULL DEFAULT 0,
    immacolata_active INTEGER NOT NULL DEFAULT 0
  )`);

  db.run(`CREATE INDEX IF NOT EXISTS idx_drivers_depot ON drivers(depot_id)`);
  db.run(`CREATE INDEX IF NOT EXISTS idx_blocks_depot ON rotation_blocks(depot_id)`);
  db.run(`CREATE INDEX IF NOT EXISTS idx_special_periods_depot ON special_periods(depot_id, start_date, end_date)`);
  db.run(`CREATE INDEX IF NOT EXISTS idx_calendar_ranges_kind ON calendar_ranges(kind, start_date, end_date)`);
});

export function run(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function callback(err) {
      if (err) reject(err);
      else resolve(this);
    });
  });
}

export function get(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
  });
}

export function all(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
  });
}
