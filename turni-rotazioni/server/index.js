import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { db, run, get, all } from './db.js';
import { requireAdmin } from './adminAuth.js';
import { computeSchedule, resolveBlock, computeTurno, deriveHolidaysFromSchoolCalendar } from './rotation.js';

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3002;

// --- shared data loaders --------------------------------------------------

async function loadDepot(depotId) {
  return get('SELECT * FROM depots WHERE id = ?', [depotId]);
}

async function loadDrivers(depotId, { activeOnly = true } = {}) {
  const sql = activeOnly
    ? 'SELECT * FROM drivers WHERE depot_id = ? AND active = 1 ORDER BY rotation_position'
    : 'SELECT * FROM drivers WHERE depot_id = ? ORDER BY rotation_position';
  return all(sql, [depotId]);
}

async function loadCalendarData(depotId) {
  const [specialPeriodsRaw, blocks, holidaysRows, calendarRanges, schoolCalendarYears] = await Promise.all([
    all('SELECT * FROM special_periods WHERE depot_id = ? AND active = 1', [depotId]),
    all('SELECT * FROM rotation_blocks WHERE depot_id = ?', [depotId]),
    all('SELECT date FROM holidays', []),
    all('SELECT * FROM calendar_ranges', []),
    all('SELECT * FROM school_calendar_years', []),
  ]);

  const blockById = new Map(blocks.map((b) => [b.id, b]));
  const standardBlocksByType = {};
  for (const b of blocks) {
    if (b.is_standard) standardBlocksByType[b.block_type] = b;
  }
  const specialPeriods = specialPeriodsRaw.map((p) => ({ ...p, block: blockById.get(p.block_id) }));
  const holidays = new Set(holidaysRows.map((h) => h.date));
  for (const h of deriveHolidaysFromSchoolCalendar(schoolCalendarYears)) holidays.add(h.date);

  const blockIds = blocks.map((b) => b.id);
  const cells = blockIds.length
    ? await all(
        `SELECT * FROM rotation_cells WHERE block_id IN (${blockIds.map(() => '?').join(',')})`,
        blockIds
      )
    : [];
  const turnoLookup = new Map(
    cells.map((c) => [`${c.block_id}:${c.weekday}:${c.col_index}`, c.turno_code])
  );

  return { specialPeriods, standardBlocksByType, holidays, calendarRanges, turnoLookup };
}

// --- public endpoints ------------------------------------------------------

app.get('/api/depots', async (req, res) => {
  res.json(await all('SELECT * FROM depots ORDER BY sort_order'));
});

app.get('/api/depots/:id/drivers', async (req, res) => {
  res.json(await loadDrivers(req.params.id));
});

app.get('/api/schedule', async (req, res) => {
  const { depot: depotId, from, to } = req.query;
  if (!depotId || !from || !to) {
    return res.status(400).json({ ok: false, reason: 'depot, from, to are required' });
  }
  const depot = await loadDepot(depotId);
  if (!depot) return res.status(404).json({ ok: false, reason: 'depot not found' });

  const drivers = await loadDrivers(depotId);
  const calendarData = await loadCalendarData(depotId);
  const rows = computeSchedule(from, to, depot, drivers, calendarData, calendarData.turnoLookup);
  res.json({ depot, drivers, schedule: rows });
});

// --- admin: depots -----------------------------------------------------

app.get('/api/admin/depots/:id', requireAdmin, async (req, res) => {
  const depot = await loadDepot(req.params.id);
  if (!depot) return res.status(404).json({ ok: false, reason: 'depot not found' });
  res.json(depot);
});

app.put('/api/admin/depots/:id', requireAdmin, async (req, res) => {
  const { name, cycle_length, reference_date } = req.body;
  await run(
    'UPDATE depots SET name = COALESCE(?, name), cycle_length = COALESCE(?, cycle_length), reference_date = COALESCE(?, reference_date) WHERE id = ?',
    [name ?? null, cycle_length ?? null, reference_date ?? null, req.params.id]
  );
  res.json(await loadDepot(req.params.id));
});

// --- admin: drivers ------------------------------------------------------

app.get('/api/admin/depots/:id/drivers', requireAdmin, async (req, res) => {
  res.json(await loadDrivers(req.params.id, { activeOnly: false }));
});

app.post('/api/admin/depots/:id/drivers', requireAdmin, async (req, res) => {
  const { name } = req.body;
  if (!name) return res.status(400).json({ ok: false, reason: 'name is required' });
  const maxRow = await get(
    'SELECT MAX(rotation_position) AS maxPos FROM drivers WHERE depot_id = ?',
    [req.params.id]
  );
  const nextPos = (maxRow?.maxPos ?? 0) + 1;
  const result = await run(
    'INSERT INTO drivers (depot_id, name, rotation_position) VALUES (?, ?, ?)',
    [req.params.id, name, nextPos]
  );
  res.status(201).json(await get('SELECT * FROM drivers WHERE id = ?', [result.lastID]));
});

app.put('/api/admin/drivers/:id', requireAdmin, async (req, res) => {
  const { name, active } = req.body;
  await run(
    'UPDATE drivers SET name = COALESCE(?, name), active = COALESCE(?, active), updated_at = CURRENT_TIMESTAMP WHERE id = ?',
    [name ?? null, active === undefined ? null : (active ? 1 : 0), req.params.id]
  );
  res.json(await get('SELECT * FROM drivers WHERE id = ?', [req.params.id]));
});

// Explicit swap, kept separate from rename so an accidental reorder can't slip in.
app.put('/api/admin/drivers/:id/reorder', requireAdmin, async (req, res) => {
  const { swapWithDriverId } = req.body;
  const a = await get('SELECT * FROM drivers WHERE id = ?', [req.params.id]);
  const b = await get('SELECT * FROM drivers WHERE id = ?', [swapWithDriverId]);
  if (!a || !b || a.depot_id !== b.depot_id) {
    return res.status(400).json({ ok: false, reason: 'both drivers must exist and share a depot' });
  }
  await run('UPDATE drivers SET rotation_position = ? WHERE id = ?', [b.rotation_position, a.id]);
  await run('UPDATE drivers SET rotation_position = ? WHERE id = ?', [a.rotation_position, b.id]);
  res.json(await loadDrivers(a.depot_id, { activeOnly: false }));
});

// --- admin: rotation blocks + cells ---------------------------------------

app.get('/api/admin/depots/:id/blocks', requireAdmin, async (req, res) => {
  res.json(await all('SELECT * FROM rotation_blocks WHERE depot_id = ? ORDER BY is_standard DESC, id', [req.params.id]));
});

app.post('/api/admin/depots/:id/blocks', requireAdmin, async (req, res) => {
  const { block_type, label } = req.body;
  if (!block_type || !label) {
    return res.status(400).json({ ok: false, reason: 'block_type and label are required' });
  }
  const depot = await loadDepot(req.params.id);
  if (!depot) return res.status(404).json({ ok: false, reason: 'depot not found' });

  const result = await run(
    'INSERT INTO rotation_blocks (depot_id, block_type, label, is_standard) VALUES (?, ?, ?, 0)',
    [req.params.id, block_type, label]
  );
  const blockId = result.lastID;

  const stmt = db.prepare(
    'INSERT INTO rotation_cells (block_id, weekday, col_index, turno_code) VALUES (?, ?, ?, ?)'
  );
  for (let weekday = 0; weekday < 7; weekday += 1) {
    for (let col = 1; col <= depot.cycle_length; col += 1) {
      stmt.run(blockId, weekday, col, 'DISP');
    }
  }
  stmt.finalize();

  res.status(201).json(await get('SELECT * FROM rotation_blocks WHERE id = ?', [blockId]));
});

app.get('/api/admin/blocks/:id/cells', requireAdmin, async (req, res) => {
  res.json(await all('SELECT * FROM rotation_cells WHERE block_id = ? ORDER BY weekday, col_index', [req.params.id]));
});

app.put('/api/admin/blocks/:id/cells', requireAdmin, async (req, res) => {
  const { cells } = req.body; // [{weekday, col_index, turno_code}]
  if (!Array.isArray(cells)) return res.status(400).json({ ok: false, reason: 'cells array is required' });

  const stmt = db.prepare(
    `INSERT INTO rotation_cells (block_id, weekday, col_index, turno_code) VALUES (?, ?, ?, ?)
     ON CONFLICT(block_id, weekday, col_index) DO UPDATE SET turno_code = excluded.turno_code`
  );
  for (const c of cells) {
    stmt.run(req.params.id, c.weekday, c.col_index, c.turno_code);
  }
  stmt.finalize((err) => {
    if (err) return res.status(500).json({ ok: false, reason: err.message });
    res.json({ ok: true, updated: cells.length });
  });
});

// --- admin: special periods -------------------------------------------

app.get('/api/admin/special-periods', requireAdmin, async (req, res) => {
  const { depot } = req.query;
  res.json(
    depot
      ? await all('SELECT * FROM special_periods WHERE depot_id = ? ORDER BY start_date', [depot])
      : await all('SELECT * FROM special_periods ORDER BY depot_id, start_date')
  );
});

app.post('/api/admin/special-periods', requireAdmin, async (req, res) => {
  const { depot_id, label, start_date, end_date, block_id, priority } = req.body;
  const result = await run(
    'INSERT INTO special_periods (depot_id, label, start_date, end_date, block_id, priority) VALUES (?, ?, ?, ?, ?, ?)',
    [depot_id, label, start_date, end_date, block_id, priority ?? 0]
  );
  res.status(201).json(await get('SELECT * FROM special_periods WHERE id = ?', [result.lastID]));
});

app.put('/api/admin/special-periods/:id', requireAdmin, async (req, res) => {
  const { label, start_date, end_date, block_id, priority, active } = req.body;
  await run(
    `UPDATE special_periods SET
       label = COALESCE(?, label), start_date = COALESCE(?, start_date),
       end_date = COALESCE(?, end_date), block_id = COALESCE(?, block_id),
       priority = COALESCE(?, priority), active = COALESCE(?, active)
     WHERE id = ?`,
    [label ?? null, start_date ?? null, end_date ?? null, block_id ?? null,
      priority ?? null, active === undefined ? null : (active ? 1 : 0), req.params.id]
  );
  res.json(await get('SELECT * FROM special_periods WHERE id = ?', [req.params.id]));
});

app.delete('/api/admin/special-periods/:id', requireAdmin, async (req, res) => {
  const period = await get('SELECT * FROM special_periods WHERE id = ?', [req.params.id]);
  await run('DELETE FROM special_periods WHERE id = ?', [req.params.id]);

  if (period) {
    // Clean up the block this period owned, unless it's a standard block or
    // still used by another special period - avoids leaving an orphan grid
    // tab behind (e.g. a "new block" created for a period that got deleted).
    const block = await get('SELECT * FROM rotation_blocks WHERE id = ?', [period.block_id]);
    const stillUsed = await get(
      'SELECT 1 FROM special_periods WHERE block_id = ?',
      [period.block_id]
    );
    if (block && !block.is_standard && !stillUsed) {
      await run('DELETE FROM rotation_blocks WHERE id = ?', [block.id]);
    }
  }

  res.json({ ok: true });
});

// --- admin: shared calendar (holidays + ranges) ----------------------------

app.get('/api/admin/holidays', requireAdmin, async (req, res) => {
  res.json(await all('SELECT * FROM holidays ORDER BY date'));
});
app.post('/api/admin/holidays', requireAdmin, async (req, res) => {
  const { date, label } = req.body;
  await run('INSERT OR REPLACE INTO holidays (date, label) VALUES (?, ?)', [date, label ?? null]);
  res.status(201).json({ date, label });
});
app.delete('/api/admin/holidays/:date', requireAdmin, async (req, res) => {
  await run('DELETE FROM holidays WHERE date = ?', [req.params.date]);
  res.json({ ok: true });
});

app.get('/api/admin/calendar-ranges', requireAdmin, async (req, res) => {
  res.json(await all('SELECT * FROM calendar_ranges ORDER BY kind, start_date'));
});
app.post('/api/admin/calendar-ranges', requireAdmin, async (req, res) => {
  const { kind, start_date, end_date, label } = req.body;
  const result = await run(
    'INSERT INTO calendar_ranges (kind, start_date, end_date, label) VALUES (?, ?, ?, ?)',
    [kind, start_date, end_date, label ?? null]
  );
  res.status(201).json(await get('SELECT * FROM calendar_ranges WHERE id = ?', [result.lastID]));
});
app.put('/api/admin/calendar-ranges/:id', requireAdmin, async (req, res) => {
  const { kind, start_date, end_date, label } = req.body;
  await run(
    'UPDATE calendar_ranges SET kind = COALESCE(?, kind), start_date = COALESCE(?, start_date), end_date = COALESCE(?, end_date), label = COALESCE(?, label) WHERE id = ?',
    [kind ?? null, start_date ?? null, end_date ?? null, label ?? null, req.params.id]
  );
  res.json(await get('SELECT * FROM calendar_ranges WHERE id = ?', [req.params.id]));
});
app.delete('/api/admin/calendar-ranges/:id', requireAdmin, async (req, res) => {
  await run('DELETE FROM calendar_ranges WHERE id = ?', [req.params.id]);
  res.json({ ok: true });
});

// --- admin: calendario scolastico parametrico (2017-2050) ------------------
// Importato una volta da migration/05_import_school_calendar.py; questi
// endpoint permettono di correggerlo/estenderlo dal pannello, es. quando
// il foglio Google non ha ancora l'anno che serve.

app.get('/api/admin/school-calendar-years', requireAdmin, async (req, res) => {
  res.json(await all('SELECT * FROM school_calendar_years ORDER BY year'));
});

app.put('/api/admin/school-calendar-years/:year', requireAdmin, async (req, res) => {
  const {
    easter_date, summer_end_day_june, summer_start_day_september,
    agosto_start_day, agosto_end_day,
    carnevale1_day, carnevale1_month, carnevale2_day, carnevale2_month,
    epifania_active, liberazione_active, lavoro_active,
    forze_armate_active, tutti_santi_active, immacolata_active,
  } = req.body;
  const year = Number(req.params.year);
  await run(
    `INSERT INTO school_calendar_years (
       year, easter_date, summer_end_day_june, summer_start_day_september,
       agosto_start_day, agosto_end_day,
       carnevale1_day, carnevale1_month, carnevale2_day, carnevale2_month,
       epifania_active, liberazione_active, lavoro_active,
       forze_armate_active, tutti_santi_active, immacolata_active
     ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
     ON CONFLICT(year) DO UPDATE SET
       easter_date=COALESCE(excluded.easter_date, easter_date),
       summer_end_day_june=COALESCE(excluded.summer_end_day_june, summer_end_day_june),
       summer_start_day_september=COALESCE(excluded.summer_start_day_september, summer_start_day_september),
       agosto_start_day=COALESCE(excluded.agosto_start_day, agosto_start_day),
       agosto_end_day=COALESCE(excluded.agosto_end_day, agosto_end_day),
       carnevale1_day=COALESCE(excluded.carnevale1_day, carnevale1_day),
       carnevale1_month=COALESCE(excluded.carnevale1_month, carnevale1_month),
       carnevale2_day=COALESCE(excluded.carnevale2_day, carnevale2_day),
       carnevale2_month=COALESCE(excluded.carnevale2_month, carnevale2_month),
       epifania_active=COALESCE(excluded.epifania_active, epifania_active),
       liberazione_active=COALESCE(excluded.liberazione_active, liberazione_active),
       lavoro_active=COALESCE(excluded.lavoro_active, lavoro_active),
       forze_armate_active=COALESCE(excluded.forze_armate_active, forze_armate_active),
       tutti_santi_active=COALESCE(excluded.tutti_santi_active, tutti_santi_active),
       immacolata_active=COALESCE(excluded.immacolata_active, immacolata_active)`,
    [
      year, easter_date ?? null, summer_end_day_june ?? null, summer_start_day_september ?? null,
      agosto_start_day ?? null, agosto_end_day ?? null,
      carnevale1_day ?? null, carnevale1_month ?? null, carnevale2_day ?? null, carnevale2_month ?? null,
      epifania_active === undefined ? null : (epifania_active ? 1 : 0),
      liberazione_active === undefined ? null : (liberazione_active ? 1 : 0),
      lavoro_active === undefined ? null : (lavoro_active ? 1 : 0),
      forze_armate_active === undefined ? null : (forze_armate_active ? 1 : 0),
      tutti_santi_active === undefined ? null : (tutti_santi_active ? 1 : 0),
      immacolata_active === undefined ? null : (immacolata_active ? 1 : 0),
    ]
  );
  res.json(await get('SELECT * FROM school_calendar_years WHERE year = ?', [year]));
});

// --- admin: schedule preview (verification tool) ---------------------------

app.get('/api/admin/schedule-preview', requireAdmin, async (req, res) => {
  const { depot: depotId, date } = req.query;
  if (!depotId || !date) return res.status(400).json({ ok: false, reason: 'depot and date are required' });

  const depot = await loadDepot(depotId);
  if (!depot) return res.status(404).json({ ok: false, reason: 'depot not found' });

  const drivers = await loadDrivers(depotId);
  const calendarData = await loadCalendarData(depotId);
  const { block, via, blockType, specialPeriod } = resolveBlock(date, depotId, calendarData);

  const rows = drivers.map((driver) => ({
    driver: { id: driver.id, name: driver.name, rotation_position: driver.rotation_position },
    turno: computeTurno(date, depot, driver, calendarData, calendarData.turnoLookup),
  }));

  res.json({
    depot,
    date,
    resolvedVia: via,
    blockType: blockType ?? null,
    specialPeriod: specialPeriod ?? null,
    block: block ?? null,
    drivers: rows,
  });
});

app.listen(PORT, () => {
  console.log(`turni-rotazioni backend listening on :${PORT}`);
});
