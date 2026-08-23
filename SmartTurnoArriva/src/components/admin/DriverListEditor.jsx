import React, { useEffect, useState } from 'react';
import { turniApi } from './turniApi.js';

export default function DriverListEditor({ depotId, adminKey }) {
  const [drivers, setDrivers] = useState([]);
  const [newName, setNewName] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [renaming, setRenaming] = useState({}); // id -> draft name

  const load = () => {
    setBusy(true);
    setError('');
    turniApi.drivers(depotId, adminKey)
      .then(setDrivers)
      .catch((e) => setError(e.message))
      .finally(() => setBusy(false));
  };

  useEffect(load, [depotId]);

  const addDriver = async (e) => {
    e.preventDefault();
    if (!newName.trim()) return;
    setBusy(true);
    try {
      await turniApi.addDriver(depotId, newName.trim(), adminKey);
      setNewName('');
      load();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const saveRename = async (id) => {
    const name = (renaming[id] ?? '').trim();
    if (!name) return;
    setBusy(true);
    try {
      await turniApi.updateDriver(id, { name }, adminKey);
      setRenaming((r) => ({ ...r, [id]: undefined }));
      load();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const toggleActive = async (driver) => {
    setBusy(true);
    try {
      await turniApi.updateDriver(driver.id, { active: driver.active ? 0 : 1 }, adminKey);
      load();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <form onSubmit={addDriver} style={styles.row}>
        <input
          style={styles.input}
          placeholder="Nome nuovo autista"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
        />
        <button style={styles.smallBtn} disabled={busy} type="submit">Aggiungi</button>
      </form>
      {error && <div style={styles.error}>{error}</div>}
      <ul style={styles.list}>
        {drivers.map((d) => (
          <li key={d.id} style={{ ...styles.listItem, opacity: d.active ? 1 : 0.5 }}>
            <span style={styles.pos}>{d.rotation_position}</span>
            {renaming[d.id] !== undefined ? (
              <input
                style={{ ...styles.input, marginBottom: 0, flex: 1 }}
                value={renaming[d.id]}
                autoFocus
                onChange={(e) => setRenaming((r) => ({ ...r, [d.id]: e.target.value }))}
                onKeyDown={(e) => e.key === 'Enter' && saveRename(d.id)}
              />
            ) : (
              <span style={{ flex: 1 }}>{d.name}</span>
            )}
            {renaming[d.id] !== undefined ? (
              <button style={styles.smallBtn} onClick={() => saveRename(d.id)}>Salva</button>
            ) : (
              <button style={styles.ghostBtn} onClick={() => setRenaming((r) => ({ ...r, [d.id]: d.name }))}>
                Rinomina
              </button>
            )}
            <button style={d.active ? styles.removeBtn : styles.smallBtn} onClick={() => toggleActive(d)}>
              {d.active ? 'Disattiva' : 'Riattiva'}
            </button>
          </li>
        ))}
        {!busy && drivers.length === 0 && <li style={styles.hint}>Nessun autista.</li>}
      </ul>
    </div>
  );
}

const styles = {
  row: { display: 'flex', gap: 8, marginBottom: 10 },
  input: {
    flex: 1, boxSizing: 'border-box', background: 'var(--bg-dark)', border: '1px solid var(--border-color)',
    borderRadius: 8, color: 'var(--text-main)', padding: '9px 10px', fontSize: 14,
  },
  smallBtn: { background: 'var(--accent-cyan)', border: 'none', borderRadius: 8, color: 'var(--bg-dark)', fontWeight: 600, padding: '0 14px', cursor: 'pointer', whiteSpace: 'nowrap' },
  ghostBtn: { background: 'none', border: '1px solid var(--border-color)', color: 'var(--text-muted)', borderRadius: 6, padding: '4px 8px', fontSize: 12, cursor: 'pointer', whiteSpace: 'nowrap' },
  removeBtn: { background: 'none', border: '1px solid var(--accent-red)', color: 'var(--accent-red)', borderRadius: 6, padding: '4px 8px', fontSize: 12, cursor: 'pointer', whiteSpace: 'nowrap' },
  list: { listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 6 },
  listItem: { display: 'flex', alignItems: 'center', gap: 8, padding: '6px 0', borderBottom: '1px solid var(--border-color)', fontSize: 13, color: 'var(--text-main)' },
  pos: { color: 'var(--text-muted)', fontSize: 11, width: 20, textAlign: 'right' },
  hint: { color: 'var(--text-muted)', fontSize: 12 },
  error: { color: 'var(--accent-red)', fontSize: 13, marginBottom: 8 },
};
