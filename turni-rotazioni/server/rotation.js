// Pure functions reimplementing the Google Sheet's INDEX/MATCH/MOD rotation formulas.
// No DB access here - callers load depot/driver/block/cell/calendar data and pass it in.

const MS_PER_DAY = 86400000;

function toUTCDate(isoDate) {
  const [y, m, d] = isoDate.split('-').map(Number);
  return Date.UTC(y, m - 1, d);
}

// 0=Mon ... 6=Sun (matches GIORNO.SETTIMANA(date,2)-1 in the original sheet)
export function weekdayMon0(isoDate) {
  const jsDay = new Date(toUTCDate(isoDate)).getUTCDay(); // 0=Sun..6=Sat
  return (jsDay + 6) % 7;
}

export function weeksSince(referenceIsoDate, targetIsoDate) {
  const days = Math.floor((toUTCDate(targetIsoDate) - toUTCDate(referenceIsoDate)) / MS_PER_DAY);
  return Math.floor(days / 7);
}

// Mirrors the sheet's MOD(weeks+position, cycleLength) with 0 replaced by cycleLength.
export function resolveColumn(rotationPosition, weeks, cycleLength) {
  const m = ((weeks + rotationPosition) % cycleLength + cycleLength) % cycleLength;
  return m === 0 ? cycleLength : m;
}

function inRange(isoDate, start, end) {
  return isoDate >= start && isoDate <= end;
}

// Precedence: natale > festivo (single-day holiday) > agosto (safety-net, whole-August
// fallback for dates not covered by any special_period) > scolastico > non_scolastico.
// Domenica/Sabato are NOT separate block types: each standard block already has all 7
// weekday rows, so Saturday/Sunday resolve via weekdayMon0() inside whichever block applies.
export function classifyBlockType(isoDate, { holidays, calendarRanges }) {
  const isNatale = calendarRanges.some(
    (r) => r.kind === 'natale' && inRange(isoDate, r.start_date, r.end_date)
  );
  if (isNatale) return 'natale';

  const isFestivo = holidays.has(isoDate);
  if (isFestivo) return 'festiva';

  const month = Number(isoDate.slice(5, 7));
  if (month === 8) return 'agosto';

  const isScolastico = calendarRanges.some(
    (r) => r.kind === 'scolastico' && inRange(isoDate, r.start_date, r.end_date)
  );
  return isScolastico ? 'scolastico' : 'non_scolastico';
}

// Deriva festivi puntuali (giorno singolo) dalle righe di school_calendar_years:
// le 6 festivita' fisse si applicano solo per gli anni con la spunta a vero
// (confermato dall'utente: rispetta la spunta anno per anno, non e' un default
// sempre-attivo); i due giorni di Carnevale sono date dirette g/m, sempre
// applicate quando presenti (nessuna spunta associata nel foglio sorgente).
const FIXED_HOLIDAYS = [
  ['epifania_active', 1, 6, 'epifania'],
  ['liberazione_active', 4, 25, 'liberazione'],
  ['lavoro_active', 5, 1, 'lavoro'],
  ['forze_armate_active', 6, 2, 'forze_armate'],
  ['tutti_santi_active', 11, 1, 'tutti_santi'],
  ['immacolata_active', 12, 8, 'immacolata'],
];
const CARNEVALE_FIELDS = [
  ['carnevale1_day', 'carnevale1_month', 'carnevale1'],
  ['carnevale2_day', 'carnevale2_month', 'carnevale2'],
];

function isoFromYMD(year, month, day) {
  return `${String(year).padStart(4, '0')}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
}

export function deriveHolidaysFromSchoolCalendar(schoolCalendarYears) {
  const dates = [];
  for (const y of schoolCalendarYears) {
    for (const [field, month, day, label] of FIXED_HOLIDAYS) {
      if (y[field]) dates.push({ date: isoFromYMD(y.year, month, day), label });
    }
    for (const [dayField, monthField, label] of CARNEVALE_FIELDS) {
      const day = y[dayField];
      const month = y[monthField];
      if (day && month) dates.push({ date: isoFromYMD(y.year, month, day), label });
    }
  }
  return dates;
}

// Returns the rotation_blocks row to use for this depot+date: a matching special_period
// (highest priority wins) if any, otherwise the standard block for the classified type.
export function resolveBlock(isoDate, depotId, { specialPeriods, standardBlocksByType, holidays, calendarRanges }) {
  const candidates = specialPeriods.filter(
    (p) => p.depot_id === depotId && p.active && inRange(isoDate, p.start_date, p.end_date)
  );
  if (candidates.length > 0) {
    candidates.sort((a, b) => b.priority - a.priority);
    return { block: candidates[0].block, via: 'special_period', specialPeriod: candidates[0] };
  }

  const blockType = classifyBlockType(isoDate, { holidays, calendarRanges });
  const block = standardBlocksByType[blockType];
  return { block, via: 'standard', blockType };
}

// turnoLookup: Map keyed `${block_id}:${weekday}:${col_index}` -> turno_code
export function computeTurno(isoDate, depot, driver, calendarData, turnoLookup) {
  const { block } = resolveBlock(isoDate, depot.id, calendarData);
  if (!block) return null;

  const weekday = weekdayMon0(isoDate);
  const weeks = weeksSince(depot.reference_date, isoDate);
  const col = resolveColumn(driver.rotation_position, weeks, depot.cycle_length);
  const key = `${block.id}:${weekday}:${col}`;
  return turnoLookup.get(key) ?? null;
}

function* dateRange(fromIso, toIso) {
  let cursor = toUTCDate(fromIso);
  const end = toUTCDate(toIso);
  while (cursor <= end) {
    yield new Date(cursor).toISOString().slice(0, 10);
    cursor += MS_PER_DAY;
  }
}

export function computeSchedule(fromIso, toIso, depot, drivers, calendarData, turnoLookup) {
  const rows = [];
  for (const isoDate of dateRange(fromIso, toIso)) {
    const { block, via, blockType } = resolveBlock(isoDate, depot.id, calendarData);
    const perDate = { date: isoDate, blockType: blockType ?? (via === 'special_period' ? 'special' : null), drivers: {} };
    for (const driver of drivers) {
      perDate.drivers[driver.id] = computeTurno(isoDate, depot, driver, calendarData, turnoLookup);
    }
    rows.push(perDate);
  }
  return rows;
}
