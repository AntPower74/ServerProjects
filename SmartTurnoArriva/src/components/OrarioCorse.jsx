import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import { AlertTriangle, Clock } from 'lucide-react';

const PROSPETTO_CSV = "https://docs.google.com/spreadsheets/d/1jmlp68KdVRcx_dXSXo5wPClhuCFPH5Ca92FjezQqrYk/export?format=csv&gid=737765459";

const parseTime = (t) => {
  if (!t || t === '-') return null;
  const parts = t.split('.');
  if (parts.length !== 2) return null;
  return parseInt(parts[0], 10) * 60 + parseInt(parts[1], 10);
};

const isReturnTrip = (row) => {
  let firstTime = null;
  let lastTime = null;
  for (let i = 1; i <= 9; i++) {
    const t = parseTime(row[i] ? row[i].trim() : null);
    if (t !== null) {
      if (firstTime === null) firstTime = t;
      lastTime = t;
    }
  }
  if (firstTime !== null && lastTime !== null && firstTime !== lastTime) {
    const diff = (lastTime - firstTime + 1440) % 1440;
    return diff > 720;
  }
  return false;
};

const OrarioCorse = () => {
  const [data, setData] = useState([]);
  const [headers, setHeaders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(PROSPETTO_CSV)
      .then(res => {
        if (!res.ok) throw new Error("Errore nel caricamento del prospetto");
        return res.text();
      })
      .then(csvText => {
        Papa.parse(csvText, {
          skipEmptyLines: true,
          complete: (results) => {
            const rows = results.data;
            if (rows.length < 2) {
              setError("Il file è vuoto o non valido.");
              setLoading(false);
              return;
            }
            setHeaders(rows[0].slice(0, 10));
            const validRows = rows.slice(1).filter(r => r.slice(1, 10).some(v => v.trim() !== ''));
            setData(validRows);
            setLoading(false);
          }
        });
      })
      .catch(err => {
        console.error(err);
        setError("Errore di rete o file non disponibile.");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="loading-container" style={{ color: 'var(--accent-red)' }}>
        <AlertTriangle size={32} style={{ marginRight: '0.5rem' }} /> {error}
      </div>
    );
  }

  return (
    <div style={{
      padding: '1rem',
      background: 'var(--bg-app)',
      minHeight: '100vh',
      paddingBottom: '80px',
      width: '100%',
      minWidth: 0,
      boxSizing: 'border-box',
      overflowX: 'hidden'
    }}>
      <h2 style={{
        fontSize: '1.1rem',
        fontWeight: 'bold',
        marginBottom: '1rem',
        color: 'var(--text-light)',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem'
      }}>
        <Clock size={18} /> Orario Corse
      </h2>

      <div style={{
        borderRadius: '12px',
        border: '1px solid var(--border-color)',
        overflow: 'hidden',
        background: 'var(--bg-card)',
        maxWidth: '100%'
      }}>
        <div style={{ overflowX: 'auto', maxWidth: '100%' }}>
          <table style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: '0.8rem',
            tableLayout: 'auto'
          }}>
            <thead>
              <tr>
                {headers.map((h, i) => {
                  const isTurno = i === 0;
                  return (
                    <th key={i} style={{
                      padding: isTurno ? '6px' : '4px 2px',
                      background: 'var(--bg-card)', // Serve colore solido per lo sticky
                      color: isTurno ? 'var(--accent-cyan)' : 'var(--text-muted)',
                      textAlign: 'center',
                      borderBottom: '1px solid var(--border-color)',
                      borderRight: isTurno ? '2px solid var(--border-color)' : 'none',
                      verticalAlign: 'bottom',
                      width: isTurno ? '48px' : '30px',
                      minWidth: isTurno ? '48px' : '30px',
                      maxWidth: isTurno ? '50px' : '36px',
                      position: isTurno ? 'sticky' : 'static',
                      left: 0,
                      zIndex: isTurno ? 10 : 1,
                    }}>
                      <div style={{
                        writingMode: isTurno ? 'horizontal-tb' : 'vertical-rl',
                        textOrientation: isTurno ? 'mixed' : 'mixed',
                        transform: isTurno ? 'none' : 'rotate(180deg)',
                        whiteSpace: 'nowrap',
                        fontSize: isTurno ? '0.75rem' : '0.65rem',
                        fontWeight: isTurno ? '700' : '500',
                        letterSpacing: '0.03em',
                        paddingBottom: isTurno ? '0' : '4px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        height: isTurno ? '100%' : 'auto',
                      }}>
                        {h.replace('Caselle Torinese', 'Caselle')}
                      </div>
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody>
              {data.map((row, i) => {
                const isReturn = isReturnTrip(row);
                const isGhost = row[0].trim() === '';

                let accentColor = isReturn ? 'var(--accent-purple)' : 'var(--accent-cyan)';
                let bgColor = isReturn ? 'rgba(168, 85, 247, 0.08)' : 'rgba(59, 130, 246, 0.08)';

                // Se la riga non ha turno (continuità), rendila semi-trasparente e togli lo sfondo
                if (isGhost) {
                  accentColor = 'var(--border-color)';
                  bgColor = 'transparent';
                }

                return (
                <tr key={i} style={{
                  borderBottom: '1px solid var(--border-color)',
                  transition: 'background 0.15s'
                }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-card-hover)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  {row.slice(0, 10).map((cell, j) => {
                    const isTurno = j === 0;
                    const val = cell.trim();
                    return (
                      <td key={j} style={{
                        padding: isTurno ? '6px 4px' : '6px 2px',
                        textAlign: 'center',
                        whiteSpace: 'nowrap',
                        color: isTurno ? 'var(--text-main)' : (val && val !== '-' ? accentColor : 'var(--text-muted)'),
                        fontWeight: isTurno ? '700' : (val && val !== '-' ? '600' : '400'),
                        fontSize: isTurno ? '0.8rem' : '0.7rem',
                        background: isTurno
                          ? 'var(--bg-card)' // Sfondo solido per lo sticky
                          : (val ? bgColor : 'transparent'),
                        borderRight: isTurno ? '2px solid var(--border-color)' : 'none',
                        position: isTurno ? 'sticky' : 'static',
                        left: 0,
                        zIndex: isTurno ? 5 : 1,
                      }}>
                        {val || <span style={{ color: 'var(--border-color)', fontSize: '0.6rem' }}>—</span>}
                      </td>
                    );
                  })}
                </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default OrarioCorse;
