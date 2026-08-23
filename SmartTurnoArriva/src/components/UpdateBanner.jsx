import React, { useState, useEffect } from 'react';
import { Capacitor } from '@capacitor/core';
import { API_BASE } from '../config.js';
import { APP_VERSION_CODE } from '../version.js';

export default function UpdateBanner() {
  const [update, setUpdate] = useState(null); // { versionName, apkUrl }
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    if (!Capacitor.isNativePlatform()) return; // web/PWA si aggiorna gia' da solo
    fetch(`${API_BASE}/api/update/manifest`, { cache: 'no-store' })
      .then((r) => r.json())
      .then(({ versionCode, versionName }) => {
        if (versionCode > APP_VERSION_CODE) {
          setUpdate({ versionName, apkUrl: `${API_BASE}/smartturnoarriva.apk` });
        }
      })
      .catch(() => {}); // niente banner se il check fallisce
  }, []);

  if (!update || dismissed) return null;

  return (
    <div style={styles.banner}>
      <span>Nuova versione disponibile ({update.versionName})</span>
      <div style={styles.actions}>
        <button style={styles.updateBtn} onClick={() => window.open(update.apkUrl, '_system')}>
          Aggiorna
        </button>
        <button style={styles.dismissBtn} onClick={() => setDismissed(true)}>
          Dopo
        </button>
      </div>
    </div>
  );
}

const styles = {
  banner: {
    position: 'fixed',
    // Sopra la barra di navigazione (fixed, bottom:0, zIndex:1000 in
    // App.jsx) - stessa posizione/zIndex la farebbe coprire o accavallare.
    bottom: 'calc(70px + env(safe-area-inset-bottom, 0px))',
    left: 0,
    right: 0,
    zIndex: 1500,
    background: 'var(--bg-card)',
    borderTop: '1px solid var(--accent-cyan)',
    color: 'var(--text-main)',
    padding: '10px 14px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    fontSize: 13,
    gap: 10,
    boxShadow: '0 -2px 10px rgba(0,0,0,0.3)',
  },
  actions: { display: 'flex', gap: 8, flexShrink: 0 },
  updateBtn: {
    background: 'var(--accent-cyan)',
    border: 'none',
    borderRadius: 6,
    color: 'var(--bg-dark)',
    fontWeight: 600,
    padding: '6px 10px',
    fontSize: 13,
    cursor: 'pointer',
  },
  dismissBtn: {
    background: 'none',
    border: '1px solid var(--border-color)',
    borderRadius: 6,
    color: 'var(--text-muted)',
    padding: '6px 10px',
    fontSize: 13,
    cursor: 'pointer',
  },
};
