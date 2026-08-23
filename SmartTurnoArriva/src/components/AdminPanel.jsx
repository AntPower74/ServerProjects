import React, { useState, useEffect } from 'react';
import { API_BASE } from '../config.js';
import TurniSection from './admin/TurniSection.jsx';

const ADMIN_KEY_STORAGE = "smartturno_admin_key";

export default function AdminPanel({ onClose }) {
  const [adminKey, setAdminKey] = useState(() => localStorage.getItem(ADMIN_KEY_STORAGE) || "");
  const [unlocked, setUnlocked] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const [allowedEmails, setAllowedEmails] = useState([]);
  const [users, setUsers] = useState([]);
  const [newEmail, setNewEmail] = useState("");
  const [lookupEmail, setLookupEmail] = useState("");
  const [lookupResult, setLookupResult] = useState(null);

  const loadData = async (key) => {
    setBusy(true);
    setError("");
    try {
      const [allowRes, listRes] = await Promise.all([
        fetch(`${API_BASE}/api/auth/admin/allowlist?key=${encodeURIComponent(key)}`),
        fetch(`${API_BASE}/api/auth/admin/list?key=${encodeURIComponent(key)}`),
      ]);
      const allowData = await allowRes.json();
      const listData = await listRes.json();
      if (!allowData.ok || !listData.ok) {
        setError("Admin key errata.");
        setUnlocked(false);
        return;
      }
      setAllowedEmails(allowData.allowedEmails);
      setUsers(listData.users);
      setUnlocked(true);
      localStorage.setItem(ADMIN_KEY_STORAGE, key);
    } catch {
      setError("Impossibile contattare il server.");
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    if (adminKey) loadData(adminKey);
  }, []);

  const addEmail = async (e) => {
    e.preventDefault();
    const email = newEmail.trim().toLowerCase();
    if (!email.includes("@")) return;
    setBusy(true);
    try {
      const r = await fetch(`${API_BASE}/api/auth/admin/allowlist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key: adminKey, email }),
      });
      const data = await r.json();
      if (data.ok) { setAllowedEmails(data.allowedEmails); setNewEmail(""); }
    } finally { setBusy(false); }
  };

  const removeEmail = async (email) => {
    setBusy(true);
    try {
      const r = await fetch(`${API_BASE}/api/auth/admin/allowlist`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key: adminKey, email }),
      });
      const data = await r.json();
      if (data.ok) setAllowedEmails(data.allowedEmails);
    } finally { setBusy(false); }
  };

  const doLookup = async (e) => {
    e.preventDefault();
    setLookupResult(null);
    const email = lookupEmail.trim().toLowerCase();
    try {
      const r = await fetch(`${API_BASE}/api/auth/admin/lookup?email=${encodeURIComponent(email)}&key=${encodeURIComponent(adminKey)}`);
      const data = await r.json();
      setLookupResult(data.ok ? data : { ok: false });
    } catch {
      setLookupResult({ ok: false });
    }
  };

  return (
    <div style={styles.overlay}>
      <div style={styles.panel}>
        <div style={styles.header}>
          <span style={styles.title}>Pannello di gestione PIN</span>
          <button style={styles.closeBtn} onClick={onClose}>Chiudi</button>
        </div>

        {!unlocked && (
          <form onSubmit={(e) => { e.preventDefault(); loadData(adminKey); }}>
            <input
              style={styles.input}
              type="password"
              placeholder="Admin key"
              value={adminKey}
              onChange={(e) => setAdminKey(e.target.value)}
              autoFocus
            />
            {error && <div style={styles.error}>{error}</div>}
            <button style={styles.button} disabled={busy} type="submit">
              {busy ? "Verifica..." : "Sblocca"}
            </button>
          </form>
        )}

        {unlocked && (
          <>
            <section style={styles.section}>
              <h4 style={styles.h4}>Email autorizzate a registrarsi</h4>
              <form onSubmit={addEmail} style={styles.row}>
                <input
                  style={{ ...styles.input, marginBottom: 0 }}
                  type="email"
                  placeholder="nuova email da autorizzare"
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                />
                <button style={styles.smallBtn} disabled={busy} type="submit">Aggiungi</button>
              </form>
              <ul style={styles.list}>
                {allowedEmails.map((email) => (
                  <li key={email} style={styles.listItem}>
                    <span>{email}</span>
                    <button style={styles.removeBtn} onClick={() => removeEmail(email)}>Rimuovi</button>
                  </li>
                ))}
                {allowedEmails.length === 0 && <li style={styles.hint}>Nessuna email autorizzata.</li>}
              </ul>
            </section>

            <section style={styles.section}>
              <h4 style={styles.h4}>Recupero PIN</h4>
              <form onSubmit={doLookup} style={styles.row}>
                <input
                  style={{ ...styles.input, marginBottom: 0 }}
                  type="email"
                  placeholder="email autista"
                  value={lookupEmail}
                  onChange={(e) => setLookupEmail(e.target.value)}
                />
                <button style={styles.smallBtn} type="submit">Cerca</button>
              </form>
              {lookupResult && (
                lookupResult.ok
                  ? <div style={styles.pinResult}>PIN: <b>{lookupResult.pin}</b></div>
                  : <div style={styles.error}>Nessun accesso trovato.</div>
              )}
            </section>

            <section style={styles.section}>
              <h4 style={styles.h4}>Iscritti ({users.length})</h4>
              <ul style={styles.list}>
                {users.map((u) => (
                  <li key={u.email} style={styles.listItem}>
                    <span>{u.email}</span>
                    <span style={styles.hint}>{new Date(u.createdAt).toLocaleDateString('it-IT')}</span>
                  </li>
                ))}
              </ul>
            </section>

            <TurniSection adminKey={adminKey} />
          </>
        )}
      </div>
    </div>
  );
}

const styles = {
  overlay: {
    position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)',
    zIndex: 2000, display: 'flex', alignItems: 'flex-end',
  },
  panel: {
    width: '100%', maxHeight: '85vh', overflowY: 'auto',
    background: 'var(--bg-card)', borderTop: '1px solid var(--border-color)',
    borderRadius: '16px 16px 0 0', padding: 20,
    paddingBottom: 'calc(20px + env(safe-area-inset-bottom, 0px))',
  },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  title: { color: 'var(--accent-cyan)', fontWeight: 700, fontSize: 16 },
  closeBtn: { background: 'none', border: '1px solid var(--border-color)', borderRadius: 6, color: 'var(--text-muted)', padding: '6px 10px', cursor: 'pointer' },
  section: { marginTop: 18, paddingTop: 14, borderTop: '1px solid var(--border-color)' },
  h4: { color: 'var(--text-main)', fontSize: 14, margin: '0 0 8px' },
  row: { display: 'flex', gap: 8 },
  input: {
    flex: 1, boxSizing: 'border-box', background: 'var(--bg-dark)', border: '1px solid var(--border-color)',
    borderRadius: 8, color: 'var(--text-main)', padding: '9px 10px', fontSize: 14, marginBottom: 10,
  },
  button: { width: '100%', background: 'var(--accent-cyan)', border: 'none', borderRadius: 8, color: 'var(--bg-dark)', fontWeight: 600, padding: '10px 12px', cursor: 'pointer' },
  smallBtn: { background: 'var(--accent-cyan)', border: 'none', borderRadius: 8, color: 'var(--bg-dark)', fontWeight: 600, padding: '0 14px', cursor: 'pointer' },
  removeBtn: { background: 'none', border: '1px solid var(--accent-red)', color: 'var(--accent-red)', borderRadius: 6, padding: '3px 8px', fontSize: 12, cursor: 'pointer' },
  list: { listStyle: 'none', padding: 0, margin: '8px 0 0' },
  listItem: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 0', borderBottom: '1px solid var(--border-color)', fontSize: 13, color: 'var(--text-main)' },
  hint: { color: 'var(--text-muted)', fontSize: 12 },
  error: { color: 'var(--accent-red)', fontSize: 13, marginBottom: 8 },
  pinResult: { color: 'var(--accent-green)', fontSize: 20, fontWeight: 700, marginTop: 8 },
};
