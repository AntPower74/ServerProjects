// Loads migration/depots_raw.json (produced by 01_read_sheets.py) into the SQLite DB.
// Safe to re-run: drivers are upserted by (depot_id, rotation_position) so ids are
// preserved; rotation_blocks/cells/special_periods for a depot are replaced wholesale
// on each run (this script is for the initial import, before the admin panel is used
// as the source of truth - once live, don't re-run this over real edits).
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { db, run, get, all } from '../server/db.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const RAW_PATH = path.join(__dirname, 'depots_raw.json');

// TO's 3 hand-fixed August sub-weeks are for August 2026 (today's live fix) - the admin
// panel is where next year's dates get added/edited, this is just the initial import.
const TO_AGOSTO_YEAR = 2026;

function insertCells(blockId, cells) {
  return new Promise((resolve, reject) => {
    const stmt = db.prepare(
      'INSERT INTO rotation_cells (block_id, weekday, col_index, turno_code) VALUES (?, ?, ?, ?)'
    );
    for (const c of cells) {
      stmt.run(blockId, c.weekday, c.col_index, c.turno_code);
    }
    stmt.finalize((err) => (err ? reject(err) : resolve()));
  });
}

async function loadDepot(depot, index) {
  await run(
    'INSERT INTO depots (id, name, cycle_length, reference_date, sort_order) VALUES (?, ?, ?, ?, ?) ' +
      'ON CONFLICT(id) DO UPDATE SET name=excluded.name, cycle_length=excluded.cycle_length, reference_date=excluded.reference_date, sort_order=excluded.sort_order',
    [depot.id, depot.name, depot.cycle_length, depot.reference_date, index]
  );

  for (const driver of depot.drivers) {
    await run(
      'INSERT INTO drivers (depot_id, name, rotation_position) VALUES (?, ?, ?) ' +
        'ON CONFLICT(depot_id, rotation_position) DO UPDATE SET name=excluded.name, updated_at=CURRENT_TIMESTAMP',
      [depot.id, driver.name, driver.rotation_position]
    );
  }

  // wholesale replace of blocks/cells/special_periods for this depot (cascade deletes cells)
  const existingBlocks = await all('SELECT id FROM rotation_blocks WHERE depot_id = ?', [depot.id]);
  for (const b of existingBlocks) {
    await run('DELETE FROM rotation_blocks WHERE id = ?', [b.id]);
  }
  await run('DELETE FROM special_periods WHERE depot_id = ?', [depot.id]);

  for (const block of depot.blocks) {
    const result = await run(
      'INSERT INTO rotation_blocks (depot_id, block_type, label, is_standard) VALUES (?, ?, ?, ?)',
      [depot.id, block.block_type, block.label, block.is_standard ? 1 : 0]
    );
    const blockId = result.lastID;
    await insertCells(blockId, block.cells);

    if (!block.is_standard && block.agosto_day_range) {
      const [startDay, endDay] = block.agosto_day_range;
      const pad = (n) => String(n).padStart(2, '0');
      await run(
        'INSERT INTO special_periods (depot_id, label, start_date, end_date, block_id, priority) VALUES (?, ?, ?, ?, ?, ?)',
        [
          depot.id,
          block.label,
          `${TO_AGOSTO_YEAR}-08-${pad(startDay)}`,
          `${TO_AGOSTO_YEAR}-08-${pad(endDay)}`,
          blockId,
          10,
        ]
      );
    }
  }
}

async function main() {
  const depots = JSON.parse(fs.readFileSync(RAW_PATH, 'utf-8'));
  const order = ['TO', 'PI', 'CA', 'LU', 'PT', 'PE', 'PB', 'GT'];
  let index = 0;
  for (const depotId of order) {
    const depot = depots[depotId];
    if (!depot) continue;
    console.log(`loading ${depotId}...`);
    await loadDepot(depot, index);
    index += 1;
  }
  console.log('done.');
  db.close();
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
