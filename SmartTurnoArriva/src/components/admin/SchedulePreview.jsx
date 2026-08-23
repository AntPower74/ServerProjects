import React, { useState } from 'react';
import { turniApi } from './turniApi.js';

const iso = (d) => d.toISOString().slice(0, 10);
const today = () => iso(new Date());
const plusDays = (dateIso, days) => {
  const d = new Date(dateIso);
  d.setDate(d.getDate() + days);
  return iso(d);
};

// Stesso formato del foglio Google originale (colonna A del tab Calendario),
// es. "gio 1 gen 26", "lun 3 ago 26" - minuscolo, giorno senza zero iniziale, anno a 2 cifre.
const WEEKDAY_SHEET = ['lun', 'mar', 'mer', 'gio', 'ven', 'sab', 'dom'];
const MONTH_SHEET = ['gen', 'feb', 'mar', 'apr', 'mag', 'giu', 'lug', 'ago', 'set', 'ott', 'nov', 'dic'];
const MONTH_NAMES_FULL = [
  'GENNAIO', 'FEBBRAIO', 'MARZO', 'APRILE', 'MAGGIO', 'GIUGNO',
  'LUGLIO', 'AGOSTO', 'SETTEMBRE', 'OTTOBRE', 'NOVEMBRE', 'DICEMBRE',
];
const dayLabel = (dateIso) => {
  const [year, month, day] = dateIso.split('-').map(Number);
  const w = WEEKDAY_SHEET[(new Date(Date.UTC(year, month - 1, day)).getUTCDay() + 6) % 7];
  return `${w} ${day} ${MONTH_SHEET[month - 1]} ${String(year).slice(-2)}`;
};

const weekdayMon0 = (dateIso) => {
  const [year, month, day] = dateIso.split('-').map(Number);
  return (new Date(Date.UTC(year, month - 1, day)).getUTCDay() + 6) % 7; // 0=lun...6=dom
};

// Oro per i giorni "Scolastico", verde acqua per il resto (non scolastico,
// agosto) - stessa base della colonna data del foglio Google. Colorano lo sfondo.
const blockColor = (blockType) => (blockType === 'scolastico' ? 'rgb(255,229,153)' : 'rgb(183,225,205)');

// Sabato/domenica/festivo: colorano solo il TESTO, sfondo normale.
const ACCENT_TEXT = { domenica: 'rgb(230,90,80)', sabato: 'rgb(90,150,230)' };
const dayAccent = (dateIso, blockType) => {
  const weekday = weekdayMon0(dateIso);
  if (weekday === 6 || blockType === 'festiva' || blockType === 'natale') return ACCENT_TEXT.domenica;
  if (weekday === 5) return ACCENT_TEXT.sabato;
  return null;
};

// Colonna data: sfondo pieno oro/verde acqua (scolastico/non), testo colorato per sab/dom/festivo.
const dateCellStyle = (dateIso, blockType) => {
  const accent = dayAccent(dateIso, blockType);
  if (accent) return { background: 'var(--bg-dark)', color: accent, borderColor: 'var(--border-color)', fontWeight: 700 };
  return { background: blockColor(blockType), color: '#1a1a1a', borderColor: 'rgba(0,0,0,0.15)' };
};

// Celle turno: sfondo giallo chiarissimo + testo nero di base; DISP sempre
// azzurro chiaro, sabato celeste, domenica/festivo rosso (sul testo); RIP ha
// il suo sfondo verde chiaro indipendentemente dal giorno.
const TURNO_TEXT = { disp: 'rgb(37,99,235)', sabato: 'rgb(56,189,248)', domenica: 'rgb(220,38,38)' };
const turnoCellStyle = (dateIso, blockType, turno) => {
  if (turno === 'RIP') return { background: 'rgb(198,230,196)', color: 'rgb(30,41,59)' };

  const base = { background: 'rgb(255,251,224)', color: 'rgb(30,41,59)' };
  if (turno === 'DISP') return { ...base, color: TURNO_TEXT.disp, fontWeight: 700 };

  const weekday = weekdayMon0(dateIso);
  if (weekday === 6 || blockType === 'festiva' || blockType === 'natale') return { ...base, color: TURNO_TEXT.domenica, fontWeight: 700 };
  if (weekday === 5) return { ...base, color: TURNO_TEXT.sabato, fontWeight: 700 };
  return base;
};

// Ogni lunedì tra from e to (inclusi) presenti in result.schedule - una colonna = una settimana.
const mondaysIn = (schedule) => schedule.filter((row) => weekdayMon0(row.date) === 0).map((row) => row.date);

// Vista settimanale compatta: via il prefisso deposito ("To"/"Pi"/...) e gli
// zeri iniziali, resta solo il numero - RIP/DISP/RF/— restano come sono.
const compact = (turno) => {
  if (!turno || !/^[A-Za-z]+\d+$/.test(turno)) return turno;
  return turno.replace(/^[A-Za-z]+0*/, '') || '0';
};

const nextMatch = (schedule, fromIso, predicate) => schedule.find((row) => row.date >= fromIso && predicate(row));

export default function SchedulePreview({ depotId, adminKey }) {
  const [from, setFrom] = useState(today());
  const [to, setTo] = useState(plusDays(today(), 29)); // "di solito servono 30 giorni"
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [printMode, setPrintMode] = useState('daily'); // 'daily' | 'weekly'

  const run = () => {
    setBusy(true);
    setError('');
    turniApi.schedule(depotId, from, to)
      .then(setResult)
      .catch((e) => setError(e.message))
      .finally(() => setBusy(false));
  };

  const exportAs = (mode) => {
    setPrintMode(mode);
    // lascia che React ridisegni la vista richiesta prima di aprire la stampa
    setTimeout(() => window.print(), 50);
  };

  // --- vista settimanale, derivata dagli stessi dati già calcolati sopra ---
  let weekly = null;
  if (result && printMode === 'weekly') {
    const weeks = mondaysIn(result.schedule);
    const monthGroups = [];
    for (const w of weeks) {
      const d = new Date(w);
      const key = `${d.getFullYear()}-${d.getMonth()}`;
      const last = monthGroups[monthGroups.length - 1];
      if (last && last.key === key) last.weeks.push(w);
      else monthGroups.push({ key, year: d.getFullYear(), month: d.getMonth(), weeks: [w] });
    }
    const byDate = new Map(result.schedule.map((row) => [row.date, row]));
    // primo giorno/sabato/domenica/festivo del periodo scelto - non "oggi",
    // altrimenti un periodo tutto nel passato o nel futuro non troverebbe nulla
    const refDate = from;
    weekly = {
      weeks,
      monthGroups,
      byDate,
      T: nextMatch(result.schedule, refDate, () => true),
      SAB: nextMatch(result.schedule, refDate, (row) => weekdayMon0(row.date) === 5),
      DOM: nextMatch(result.schedule, refDate, (row) => weekdayMon0(row.date) === 6),
      FI: nextMatch(result.schedule, from, (row) => row.blockType === 'festiva'),
    };
  }

  return (
    <div>
      <div style={styles.row}>
        <label style={styles.label}>Da</label>
        <input style={styles.input} type="date" value={from} onChange={(e) => setFrom(e.target.value)} />
        <label style={styles.label}>A</label>
        <input style={styles.input} type="date" value={to} onChange={(e) => setTo(e.target.value)} />
      </div>
      <div style={styles.actionsRow}>
        <button style={styles.saveBtn} disabled={busy} onClick={run}>
          {busy ? 'Calcolo...' : 'Crea anteprima'}
        </button>
        {result && (
          <>
            <button style={styles.pdfBtn} onClick={() => exportAs('daily')}>Esporta PDF</button>
            <button style={styles.pdfBtn} onClick={() => exportAs('weekly')}>Esporta rotazione settimanale</button>
          </>
        )}
      </div>
      {error && <div style={styles.error}>{error}</div>}

      {result && printMode === 'daily' && (
        <div className="print-area">
          <div className="print-title" style={styles.printTitle}>{depotId} · {from} → {to}</div>
          <div style={styles.gridWrap}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={{ ...styles.th, ...styles.cornerTh }}></th>
                  {result.drivers.map((d) => (
                    <th key={d.id} style={styles.th}>
                      <div className="driver-header" style={styles.driverHeader}>{d.name}</div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.schedule.map((row) => (
                  <tr key={row.date}>
                    <td style={{ ...styles.rowLabel, ...dateCellStyle(row.date, row.blockType) }}>
                      {dayLabel(row.date)}
                    </td>
                    {result.drivers.map((d) => {
                      const turno = row.drivers[d.id] ?? '—';
                      return (
                        <td key={d.id} style={styles.td}>
                          <span style={{ ...styles.cellBox, ...turnoCellStyle(row.date, row.blockType, turno) }}>
                            {turno}
                          </span>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {result && printMode === 'weekly' && weekly && (
        <div className="print-area print-weekly">
          <div className="print-title" style={styles.printTitle}>
            ROTAZIONE — {depotId} — {[...new Set(weekly.monthGroups.map((g) => g.year))].join('/')}
          </div>
          <div style={styles.gridWrap}>
            <table style={styles.table}>
              <thead>
                <tr>
                  <th style={{ ...styles.th, ...styles.cornerTh }}></th>
                  {weekly.monthGroups.map((g) => (
                    <th key={g.key} colSpan={g.weeks.length} style={styles.monthTh}>{MONTH_NAMES_FULL[g.month]}</th>
                  ))}
                  <th style={styles.monthTh} colSpan={4}>RIF.</th>
                </tr>
                <tr>
                  <th style={{ ...styles.th, ...styles.cornerTh }}></th>
                  {weekly.weeks.map((w) => {
                    const row = weekly.byDate.get(w);
                    return (
                      <th key={w} style={{ ...styles.weekTh, ...(row ? dateCellStyle(row.date, row.blockType) : {}) }}>
                        {String(new Date(w).getDate()).padStart(2, '0')}
                      </th>
                    );
                  })}
                  <th style={styles.weekTh}>T.</th>
                  <th style={styles.weekTh}>SAB</th>
                  <th style={styles.weekTh}>DOM</th>
                  <th style={styles.weekTh}>F.I.</th>
                </tr>
              </thead>
              <tbody>
                {result.drivers.map((d) => (
                  <tr key={d.id}>
                    <td style={styles.rowLabel}>{d.name}</td>
                    {weekly.weeks.map((w) => {
                      const row = weekly.byDate.get(w);
                      const turno = row?.drivers?.[d.id] ?? '—';
                      return (
                        <td key={w} style={styles.td}>
                          <span style={{ ...styles.cellBoxSmall, ...(row ? turnoCellStyle(row.date, row.blockType, turno) : {}) }}>
                            {compact(turno)}
                          </span>
                        </td>
                      );
                    })}
                    {[weekly.T, weekly.SAB, weekly.DOM, weekly.FI].map((row, i) => {
                      const turno = row?.drivers?.[d.id] ?? '—';
                      return (
                        <td key={i} style={{ ...styles.td, ...styles.refTd }}>
                          <span style={{ ...styles.cellBoxSmall, ...(row ? turnoCellStyle(row.date, row.blockType, turno) : {}) }}>
                            {compact(turno)}
                          </span>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={styles.hint}>
            T./SAB/DOM/F.I. = stesso motore di questa anteprima, per: oggi (o l'inizio del periodo scelto),
            il prossimo sabato, la prossima domenica, e il prossimo festivo infrasettimanale nel periodo.
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  row: { display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10, flexWrap: 'wrap' },
  label: { color: 'var(--text-muted)', fontSize: 12 },
  input: {
    boxSizing: 'border-box', background: 'var(--bg-dark)', border: '1px solid var(--border-color)',
    borderRadius: 8, color: 'var(--text-main)', padding: '8px 9px', fontSize: 13,
  },
  actionsRow: { display: 'flex', gap: 8, marginBottom: 10, flexWrap: 'wrap' },
  saveBtn: { background: 'var(--accent-cyan)', border: 'none', borderRadius: 8, color: 'var(--bg-dark)', fontWeight: 600, padding: '9px 14px', cursor: 'pointer' },
  pdfBtn: { background: 'none', border: '1px solid var(--accent-cyan)', borderRadius: 8, color: 'var(--accent-cyan)', fontWeight: 600, padding: '9px 14px', cursor: 'pointer' },
  printTitle: { display: 'none' },
  gridWrap: { overflow: 'auto', minWidth: 0, border: '1px solid var(--border-color)', borderRadius: 8, maxHeight: 420 },
  table: { borderCollapse: 'collapse', fontSize: 12 },
  th: { position: 'sticky', top: 0, background: 'var(--bg-card)', color: 'var(--text-muted)', padding: '4px 4px', borderBottom: '1px solid var(--border-color)', verticalAlign: 'middle' },
  cornerTh: { position: 'sticky', left: 0, zIndex: 1 },
  driverHeader: {
    writingMode: 'vertical-rl', transform: 'rotate(180deg)', maxHeight: 90, fontSize: 11, whiteSpace: 'nowrap',
    display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto', height: 90,
  },
  rowLabel: {
    position: 'sticky', left: 0, background: 'var(--bg-card)',
    color: 'var(--text-muted)', padding: '4px 8px', borderRight: '1px solid var(--border-color)', whiteSpace: 'nowrap',
  },
  td: { padding: 2, borderBottom: '1px solid var(--border-color)' },
  cellBox: {
    display: 'block', boxSizing: 'border-box', width: 60, background: 'var(--bg-dark)',
    border: '1px solid var(--border-color)', borderRadius: 4, color: 'var(--accent-cyan)',
    padding: '4px 5px', fontSize: 12, fontFamily: 'monospace', textAlign: 'center',
  },
  monthTh: {
    position: 'sticky', top: 0, background: 'var(--btn-bg)', color: 'var(--text-main)', fontWeight: 700,
    padding: '4px 2px', borderBottom: '1px solid var(--border-color)', borderLeft: '2px solid var(--border-color)', fontSize: 11,
  },
  weekTh: { position: 'sticky', top: 27, background: 'var(--bg-card)', color: 'var(--text-muted)', padding: '3px 2px', borderBottom: '1px solid var(--border-color)', borderRadius: 4, fontSize: 10, width: 30 },
  cellBoxSmall: {
    display: 'block', boxSizing: 'border-box', minWidth: 34, background: 'var(--bg-dark)',
    border: '1px solid var(--border-color)', borderRadius: 4, color: 'var(--accent-cyan)',
    padding: '3px 3px', fontSize: 9, fontFamily: 'monospace', textAlign: 'center',
  },
  refTd: { borderLeft: '2px solid var(--border-color)', color: 'var(--text-main)', fontWeight: 600 },
  hint: { color: 'var(--text-muted)', fontSize: 11, marginTop: 8 },
  error: { color: 'var(--accent-red)', fontSize: 13, marginBottom: 8 },
};
