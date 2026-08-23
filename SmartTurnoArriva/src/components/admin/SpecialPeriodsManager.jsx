import React, { useEffect, useState } from 'react';
import { turniApi } from './turniApi.js';

export default function SpecialPeriodsManager({ depotId, adminKey }) {
  const [periods, setPeriods] = useState([]);
  const [blocks, setBlocks] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const [form, setForm] = useState({ label: '', start_date: '', end_date: '', blockChoice: 'new' });

  const load = () => {
    setBusy(true);
    setError('');
    Promise.all([turniApi.specialPeriods(depotId, adminKey), turniApi.blocks(depotId, adminKey)])
      .then(([p, b]) => { setPeriods(p); setBlocks(b); })
      .catch((e) => setError(e.message))
      .finally(() => setBusy(false));
  };

  useEffect(load, [depotId]);

  const createPeriod = async (e) => {
    e.preventDefault();
    const { label, start_date, end_date, blockChoice } = form;
    if (!label || !start_date || !end_date) return;
    setBusy(true);
    setError('');
    try {
      let block_id = blockChoice === 'new' ? null : Number(blockChoice);
      if (!block_id) {
        const block = await turniApi.createBlock(depotId, 'special', label, adminKey);
        block_id = block.id;
      }
      await turniApi.createSpecialPeriod(
        { depot_id: depotId, label, start_date, end_date, block_id, priority: 10 },
        adminKey
      );
      setForm({ label: '', start_date: '', end_date: '', blockChoice: 'new' });
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const toggleActive = async (p) => {
    setBusy(true);
    try {
      await turniApi.updateSpecialPeriod(p.id, { active: p.active ? 0 : 1 }, adminKey);
      load();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const remove = async (p) => {
    setBusy(true);
    try {
      await turniApi.deleteSpecialPeriod(p.id, adminKey);
      load();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const blockLabel = (id) => blocks.find((b) => b.id === id)?.label ?? `blocco #${id}`;

  return (
    <div>
      <form onSubmit={createPeriod} style={styles.form}>
        <input
          style={styles.input}
          placeholder="Es. Agosto dal 10 al 16"
          value={form.label}
          onChange={(e) => setForm((f) => ({ ...f, label: e.target.value }))}
        />
        <div style={styles.row}>
          <input
            style={styles.input}
            type="date"
            value={form.start_date}
            onChange={(e) => setForm((f) => ({ ...f, start_date: e.target.value }))}
          />
          <input
            style={styles.input}
            type="date"
            value={form.end_date}
            onChange={(e) => setForm((f) => ({ ...f, end_date: e.target.value }))}
          />
        </div>
        <select
          style={styles.input}
          value={form.blockChoice}
          onChange={(e) => setForm((f) => ({ ...f, blockChoice: e.target.value }))}
        >
          <option value="new">Nuovo blocco (griglia vuota da compilare)</option>
          {blocks.map((b) => (
            <option key={b.id} value={b.id}>Usa griglia esistente: {b.label}</option>
          ))}
        </select>
        <button style={styles.saveBtn} disabled={busy} type="submit">Aggiungi periodo speciale</button>
      </form>

      {error && <div style={styles.error}>{error}</div>}

      <ul style={styles.list}>
        {periods.map((p) => (
          <li key={p.id} style={{ ...styles.listItem, opacity: p.active ? 1 : 0.5 }}>
            <div>
              <div style={styles.label}>{p.label}</div>
              <div style={styles.hint}>{p.start_date} → {p.end_date} · {blockLabel(p.block_id)}</div>
            </div>
            <div style={styles.actions}>
              <button style={styles.ghostBtn} onClick={() => toggleActive(p)}>{p.active ? 'Disattiva' : 'Riattiva'}</button>
              <button style={styles.removeBtn} onClick={() => remove(p)}>Elimina</button>
            </div>
          </li>
        ))}
        {!busy && periods.length === 0 && <li style={styles.hint}>Nessun periodo speciale per questo deposito.</li>}
      </ul>
    </div>
  );
}

const styles = {
  form: { display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 14, paddingBottom: 14, borderBottom: '1px solid var(--border-color)' },
  row: { display: 'flex', gap: 8 },
  input: {
    flex: 1, boxSizing: 'border-box', background: 'var(--bg-dark)', border: '1px solid var(--border-color)',
    borderRadius: 8, color: 'var(--text-main)', padding: '9px 10px', fontSize: 14,
  },
  saveBtn: { background: 'var(--accent-cyan)', border: 'none', borderRadius: 8, color: 'var(--bg-dark)', fontWeight: 600, padding: '10px 12px', cursor: 'pointer' },
  list: { listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 8 },
  listItem: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8, padding: '8px 0', borderBottom: '1px solid var(--border-color)' },
  label: { color: 'var(--text-main)', fontSize: 13, fontWeight: 600 },
  hint: { color: 'var(--text-muted)', fontSize: 12, marginTop: 2 },
  actions: { display: 'flex', gap: 6, flexShrink: 0 },
  ghostBtn: { background: 'none', border: '1px solid var(--border-color)', color: 'var(--text-muted)', borderRadius: 6, padding: '4px 8px', fontSize: 12, cursor: 'pointer', whiteSpace: 'nowrap' },
  removeBtn: { background: 'none', border: '1px solid var(--accent-red)', color: 'var(--accent-red)', borderRadius: 6, padding: '4px 8px', fontSize: 12, cursor: 'pointer', whiteSpace: 'nowrap' },
  error: { color: 'var(--accent-red)', fontSize: 13, marginBottom: 8 },
};
