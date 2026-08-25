import React, { useState, useMemo } from 'react';
import { Clock, Search, X, ArrowRight, ArrowLeft } from 'lucide-react';
import orarioCorseData from '../data/orario_corse_data.json';

const HEADERS = [
  'TURNO',
  'Torino Porta Nuova',
  'Torino Porta Susa',
  'Torino Umbria/Livorno',
  'Torino Stradella',
  'Torino Veronese',
  'Borgaro Torinese',
  'Caselle Via Torino',
  'Caselle Strada Aeroporto',
  'Caselle Aeroporto'
];

// Inbound trips have first times starting from Caselle (rows after index 65)
const isReturnRow = (index) => {
  return index >= 66;
};

const OrarioCorse = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [directionFilter, setDirectionFilter] = useState('all'); // 'all' | 'outbound' | 'inbound'

  const filteredData = useMemo(() => {
    let list = orarioCorseData.map((row, idx) => {
      const isReturn = isReturnRow(idx);
      return {
        row,
        originalIndex: idx,
        isReturn
      };
    });

    if (directionFilter === 'outbound') {
      list = list.filter(item => !item.isReturn);
    } else if (directionFilter === 'inbound') {
      list = list.filter(item => item.isReturn);
    }

    if (searchTerm.trim()) {
      const q = searchTerm.trim().toLowerCase();
      list = list.filter(item => 
        item.row.some(cell => String(cell).toLowerCase().includes(q))
      );
    }

    return list;
  }, [searchTerm, directionFilter]);

  return (
    <div style={{
      padding: '1rem',
      background: 'var(--bg-app)',
      minHeight: '100vh',
      paddingBottom: '90px',
      width: '100%',
      minWidth: 0,
      boxSizing: 'border-box',
      overflowX: 'hidden'
    }}>
      {/* Header Titolo */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '0.5rem',
        marginBottom: '1rem'
      }}>
        <div>
          <h2 style={{
            fontSize: '1.2rem',
            fontWeight: 'bold',
            color: 'var(--text-main)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            margin: 0
          }}>
            <Clock size={20} style={{ color: 'var(--accent-orange)' }} />
            <span>Orario Corse (Linea 268 Torino ↔ Caselle Aeroporto)</span>
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: '2px 0 0 0' }}>
            Quadro orario ufficiale completo con codici turno autista e fermate intermedie.
          </p>
        </div>
      </div>

      {/* Barra Filtri: Direzione & Ricerca */}
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '12px',
        padding: '0.75rem 1rem',
        marginBottom: '1rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.75rem'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '0.5rem'
        }}>
          {/* Selettore Direzione */}
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
            <button
              type="button"
              onClick={() => setDirectionFilter('all')}
              style={{
                padding: '6px 12px',
                borderRadius: '8px',
                border: directionFilter === 'all' ? '1px solid var(--accent-orange)' : '1px solid var(--border-color)',
                background: directionFilter === 'all' ? 'var(--accent-orange)' : 'rgba(255,255,255,0.03)',
                color: directionFilter === 'all' ? '#121214' : 'var(--text-main)',
                fontWeight: directionFilter === 'all' ? '700' : '500',
                fontSize: '0.8rem',
                cursor: 'pointer',
                transition: 'all 0.15s'
              }}
            >
              Tutte le Corse (144)
            </button>

            <button
              type="button"
              onClick={() => setDirectionFilter('outbound')}
              style={{
                padding: '6px 12px',
                borderRadius: '8px',
                border: directionFilter === 'outbound' ? '1px solid var(--accent-cyan)' : '1px solid var(--border-color)',
                background: directionFilter === 'outbound' ? 'rgba(8, 145, 178, 0.25)' : 'rgba(255,255,255,0.03)',
                color: directionFilter === 'outbound' ? 'var(--accent-cyan)' : 'var(--text-main)',
                fontWeight: directionFilter === 'outbound' ? '700' : '500',
                fontSize: '0.8rem',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                transition: 'all 0.15s'
              }}
            >
              <span>Andata (Torino ➔ Aeroporto)</span>
              <ArrowRight size={13} />
            </button>

            <button
              type="button"
              onClick={() => setDirectionFilter('inbound')}
              style={{
                padding: '6px 12px',
                borderRadius: '8px',
                border: directionFilter === 'inbound' ? '1px solid #10b981' : '1px solid var(--border-color)',
                background: directionFilter === 'inbound' ? 'rgba(16, 185, 129, 0.25)' : 'rgba(255,255,255,0.03)',
                color: directionFilter === 'inbound' ? '#10b981' : 'var(--text-main)',
                fontWeight: directionFilter === 'inbound' ? '700' : '500',
                fontSize: '0.8rem',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                transition: 'all 0.15s'
              }}
            >
              <ArrowLeft size={13} />
              <span>Ritorno (Aeroporto ➔ Torino)</span>
            </button>
          </div>

          {/* Ricerca per Turno o Orario */}
          <div style={{ position: 'relative', minWidth: '220px', flex: '1 1 200px' }}>
            <Search size={15} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Cerca Turno (es. To0260, Ca0030) o orario..."
              style={{
                width: '100%',
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '7px 10px 7px 32px',
                color: 'var(--text-main)',
                fontSize: '0.82rem',
                outline: 'none'
              }}
            />
            {searchTerm && (
              <X
                size={14}
                onClick={() => setSearchTerm('')}
                style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', cursor: 'pointer' }}
              />
            )}
          </div>
        </div>

        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          Mostrate <strong>{filteredData.length}</strong> corse su 144 totali
        </div>
      </div>

      {/* Tabella Quadro Orario */}
      <div style={{
        borderRadius: '12px',
        border: '1px solid var(--border-color)',
        overflow: 'hidden',
        background: 'var(--bg-card)',
        maxWidth: '100%',
        boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
      }}>
        <div style={{ overflowX: 'auto', maxWidth: '100%' }}>
          <table style={{
            width: '100%',
            borderCollapse: 'collapse',
            fontSize: '0.8rem',
            textAlign: 'center',
            whiteSpace: 'nowrap'
          }}>
            <thead>
              <tr style={{
                background: 'linear-gradient(135deg, rgba(8, 145, 178, 0.2) 0%, rgba(245, 166, 35, 0.15) 100%)',
                borderBottom: '2px solid rgba(245, 166, 35, 0.5)'
              }}>
                {HEADERS.map((h, i) => {
                  const isTurno = i === 0;
                  return (
                    <th
                      key={i}
                      style={{
                        padding: isTurno ? '10px 14px' : '10px 8px',
                        background: isTurno ? 'var(--bg-card)' : 'transparent',
                        color: isTurno ? 'var(--accent-orange)' : 'var(--text-main)',
                        fontWeight: '800',
                        fontSize: isTurno ? '0.82rem' : '0.75rem',
                        borderRight: isTurno ? '2px solid var(--border-color)' : '1px solid rgba(255,255,255,0.04)',
                        position: isTurno ? 'sticky' : 'static',
                        left: 0,
                        zIndex: isTurno ? 10 : 1,
                        minWidth: isTurno ? '90px' : '80px',
                        maxWidth: isTurno ? '100px' : '120px',
                        textAlign: isTurno ? 'left' : 'center',
                        textTransform: isTurno ? 'uppercase' : 'none'
                      }}
                    >
                      {h}
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody>
              {filteredData.length === 0 ? (
                <tr>
                  <td colSpan={HEADERS.length} style={{ padding: '2.5rem 1rem', color: 'var(--text-muted)' }}>
                    Nessuna corsa trovata con i filtri inseriti.
                  </td>
                </tr>
              ) : (
                filteredData.map(({ row, isReturn, originalIndex }) => {
                  const turnoCode = (row[0] || '').trim();
                  const hasTurno = turnoCode !== '' && turnoCode !== '—' && turnoCode !== '-';
                  const isEven = originalIndex % 2 === 0;

                  return (
                    <tr
                      key={originalIndex}
                      style={{
                        background: isEven ? 'rgba(255,255,255,0.015)' : 'rgba(0,0,0,0.15)',
                        borderBottom: '1px solid rgba(255,255,255,0.05)',
                        transition: 'background 0.15s'
                      }}
                      onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.06)'}
                      onMouseLeave={e => e.currentTarget.style.background = isEven ? 'rgba(255,255,255,0.015)' : 'rgba(0,0,0,0.15)'}
                    >
                      {/* Colonna TURNO Sticky */}
                      <td style={{
                        padding: '8px 12px',
                        textAlign: 'left',
                        position: 'sticky',
                        left: 0,
                        background: 'var(--bg-card)',
                        zIndex: 2,
                        borderRight: '2px solid var(--border-color)',
                        fontWeight: '800'
                      }}>
                        {hasTurno ? (
                          <span style={{
                            background: isReturn ? 'rgba(16, 185, 129, 0.18)' : 'rgba(245, 166, 35, 0.18)',
                            border: isReturn ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid rgba(245, 166, 35, 0.4)',
                            color: isReturn ? '#10b981' : 'var(--accent-orange)',
                            padding: '2px 8px',
                            borderRadius: '5px',
                            fontSize: '0.78rem',
                            fontWeight: '800',
                            display: 'inline-block'
                          }}>
                            {turnoCode}
                          </span>
                        ) : (
                          <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', paddingLeft: '6px' }}>
                            {turnoCode || '—'}
                          </span>
                        )}
                      </td>

                      {/* Colonne Fermate */}
                      {row.slice(1, 10).map((cell, j) => {
                        const val = (cell || '').trim();
                        const isStopValid = val !== '' && val !== '—' && val !== '-';

                        return (
                          <td
                            key={j}
                            style={{
                              padding: '8px 6px',
                              color: isStopValid ? '#fff' : 'rgba(255,255,255,0.2)',
                              fontWeight: isStopValid ? '700' : 'normal',
                              fontSize: isStopValid ? '0.80rem' : '0.75rem',
                              borderRight: '1px solid rgba(255,255,255,0.03)'
                            }}
                          >
                            {val || '—'}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default OrarioCorse;
