import React, { useState } from 'react';
import RotationGridEditor from './RotationGridEditor.jsx';

// Tutto (depositi, griglie, periodi speciali, anteprima, rinomina autisti) vive
// dentro la pagina a schermo intero RotationGridEditor - qui resta solo l'ingresso.
export default function TurniSection({ adminKey }) {
  const [gridOpen, setGridOpen] = useState(false);

  return (
    <section style={styles.section}>
      <h4 style={styles.h4}>Turni e rotazioni</h4>
      <button style={styles.gridOpenBtn} onClick={() => setGridOpen(true)}>
        Apri rotazioni →
      </button>
      {gridOpen && (
        <RotationGridEditor depotId="TO" adminKey={adminKey} onClose={() => setGridOpen(false)} />
      )}
    </section>
  );
}

const styles = {
  section: { marginTop: 18, paddingTop: 14, borderTop: '1px solid var(--border-color)' },
  h4: { color: 'var(--text-main)', fontSize: 14, margin: '0 0 8px' },
  gridOpenBtn: {
    width: '100%', background: 'var(--btn-bg)', border: '1px solid var(--accent-cyan)', borderRadius: 8,
    color: 'var(--accent-cyan)', fontWeight: 600, padding: '10px 12px', fontSize: 13, cursor: 'pointer',
  },
};
