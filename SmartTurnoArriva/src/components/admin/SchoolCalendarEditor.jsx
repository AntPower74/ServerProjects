import React, { useEffect, useState } from 'react';
import { turniApi } from './turniApi.js';

// Non è legato a un deposito - stesso calendario scolastico/festività per
// tutti (usato per classificare le date quando si calcolano i turni).
export default function SchoolCalendarEditor({ adminKey }) {
  const [years, setYears] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const load = () => {
    setBusy(true);
    setError('');
    turniApi.schoolCalendarYears(adminKey)
      .then(setYears)
      .catch((e) => setError(e.message))
      .finally(() => setBusy(false));
  };

  useEffect(load, []);

  const patchYear = (year, field, value) => {
    setYears((prev) => prev.map((y) => (y.year === year ? { ...y, [field]: value } : y)));
  };

  const saveYear = async (year) => {
    const row = years.find((y) => y.year === year);
    if (!row) return;
    setBusy(true);
    setError('');
    try {
      const saved = await turniApi.updateSchoolCalendarYear(year, row, adminKey);
      setYears((prev) => prev.map((y) => (y.year === year ? saved : y)));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const numInput = (year, field, width = 34) => (
    <input
      style={{ ...styles.cellInput, width }}
      value={years.find((y) => y.year === year)?.[field] ?? ''}
      onChange={(e) => patchYear(year, field, e.target.value === '' ? null : Number(e.target.value))}
      onBlur={() => saveYear(year)}
    />
  );

  const dateInput = (year) => (
    <input
      style={{ ...styles.cellInput, width: 110 }}
      type="date"
      value={years.find((y) => y.year === year)?.easter_date ?? ''}
      onChange={(e) => patchYear(year, 'easter_date', e.target.value)}
      onBlur={() => saveYear(year)}
    />
  );

  const checkbox = (year, field) => (
    <input
      type="checkbox"
      checked={!!years.find((y) => y.year === year)?.[field]}
      onChange={(e) => { patchYear(year, field, e.target.checked ? 1 : 0); }}
      onBlur={() => saveYear(year)}
    />
  );

  return (
    <div>
      <div style={styles.hint}>
        Calendario scolastico parametrico (2017-2050) - usato per capire se una data è scolastica, agosto,
        natale o festiva. Le modifiche si salvano da sole quando esci da un campo.
      </div>
      {error && <div style={styles.error}>{error}</div>}
      <div style={styles.gridWrap}>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Anno</th>
              <th style={styles.th}>Pasqua</th>
              <th style={styles.th}>Fine scuola (giu)</th>
              <th style={styles.th}>Inizio scuola (set)</th>
              <th style={styles.th}>Agosto dal</th>
              <th style={styles.th}>al</th>
              <th style={styles.th}>Carnevale g/m</th>
              <th style={styles.th}>Carnevale g/m 2</th>
              <th style={styles.th}>Epifania</th>
              <th style={styles.th}>Liberazione</th>
              <th style={styles.th}>Lavoro</th>
              <th style={styles.th}>Forze Armate</th>
              <th style={styles.th}>Tutti Santi</th>
              <th style={styles.th}>Immacolata</th>
            </tr>
          </thead>
          <tbody>
            {years.map((y) => (
              <tr key={y.year}>
                <td style={styles.yearTd}>{y.year}</td>
                <td style={styles.td}>{dateInput(y.year)}</td>
                <td style={styles.td}>{numInput(y.year, 'summer_end_day_june')}</td>
                <td style={styles.td}>{numInput(y.year, 'summer_start_day_september')}</td>
                <td style={styles.td}>{numInput(y.year, 'agosto_start_day')}</td>
                <td style={styles.td}>{numInput(y.year, 'agosto_end_day')}</td>
                <td style={styles.td}>
                  {numInput(y.year, 'carnevale1_day', 26)}/{numInput(y.year, 'carnevale1_month', 26)}
                </td>
                <td style={styles.td}>
                  {numInput(y.year, 'carnevale2_day', 26)}/{numInput(y.year, 'carnevale2_month', 26)}
                </td>
                <td style={styles.tdCenter}>{checkbox(y.year, 'epifania_active')}</td>
                <td style={styles.tdCenter}>{checkbox(y.year, 'liberazione_active')}</td>
                <td style={styles.tdCenter}>{checkbox(y.year, 'lavoro_active')}</td>
                <td style={styles.tdCenter}>{checkbox(y.year, 'forze_armate_active')}</td>
                <td style={styles.tdCenter}>{checkbox(y.year, 'tutti_santi_active')}</td>
                <td style={styles.tdCenter}>{checkbox(y.year, 'immacolata_active')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const styles = {
  hint: { color: 'var(--text-muted)', fontSize: 12, marginBottom: 10 },
  gridWrap: { overflow: 'auto', minWidth: 0, border: '1px solid var(--border-color)', borderRadius: 8, maxHeight: 460 },
  table: { borderCollapse: 'collapse', fontSize: 12 },
  th: {
    position: 'sticky', top: 0, background: 'var(--bg-card)', color: 'var(--text-muted)',
    padding: '6px 6px', borderBottom: '1px solid var(--border-color)', whiteSpace: 'nowrap', fontSize: 11,
  },
  yearTd: {
    position: 'sticky', left: 0, background: 'var(--bg-card)', color: 'var(--text-main)', fontWeight: 700,
    padding: '4px 8px', borderRight: '1px solid var(--border-color)', borderBottom: '1px solid var(--border-color)',
  },
  td: { padding: '3px 4px', borderBottom: '1px solid var(--border-color)', whiteSpace: 'nowrap' },
  tdCenter: { padding: '3px 4px', borderBottom: '1px solid var(--border-color)', textAlign: 'center' },
  cellInput: {
    boxSizing: 'border-box', background: 'var(--bg-dark)', border: '1px solid var(--border-color)',
    borderRadius: 4, color: 'var(--text-main)', padding: '3px 4px', fontSize: 12, textAlign: 'center',
  },
  error: { color: 'var(--accent-red)', fontSize: 13, marginBottom: 8 },
};
