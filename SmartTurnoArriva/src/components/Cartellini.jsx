import React, { useState, useMemo } from 'react';
import { Capacitor } from '@capacitor/core';
import { FileText, Search as SearchIcon, ChevronDown } from 'lucide-react';
import cartelliniData from '../data/cartellini.json';
import { API_BASE } from '../config.js';

const GIORNI_TABS = [
  { key: 'lun-ven', label: 'Lun - Ven' },
  { key: 'sabato', label: 'Sabato' },
  { key: 'domenica', label: 'Domenica' },
];

// Le settimane "A" e "B" alternano ogni settimana di calendario (lun-dom).
// Ancoraggio noto: settimana ISO 32/2026 (6-9 agosto) = B, 33/2026 (13-16
// agosto) = A -> settimana pari = B, dispari = A. Vale per Lun-Ven e Sabato,
// che condividono lo stesso ciclo (i cartellini caricati per le due
// categorie ricadono sempre nella stessa settimana solare).
const getSettimanaCorrente = (date = new Date()) => {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const dayNum = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  const isoWeek = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
  return isoWeek % 2 === 0 ? 'B' : 'A';
};

const apriCartellino = (t) => {
  const url = `${API_BASE}/cartellini/${t.file}`;
  // Nell'app nativa il webview carica gli asset da uno pseudo-dominio
  // locale: un link relativo/target=_blank non apre nulla. '_system' fa
  // aprire l'URL assoluto nel browser di sistema (stesso trucco di
  // UpdateBanner.jsx per il link di download apk).
  if (Capacitor.isNativePlatform()) {
    window.open(url, '_system');
  } else {
    window.open(url, '_blank', 'noopener,noreferrer');
  }
};

const Cartellini = () => {
  const [giorno, setGiorno] = useState('lun-ven');
  const [search, setSearch] = useState('');
  const [selectedDeposito, setSelectedDeposito] = useState('Tutti');
  const [openDepositi, setOpenDepositi] = useState({});

  // Lun-Ven alterna su 2 settimane: mostriamo sempre quella in vigore oggi.
  // Sabato invece usa un unico set: i dati della settimana "A" ricevuti si
  // sono rivelati in gran parte cartellini della Domenica etichettati per
  // errore come Sabato, quindi finche' non arriva un file corretto teniamo
  // solo il set verificato (ex settimana B).
  const settimanaCorrente = useMemo(() => getSettimanaCorrente(), []);
  const haSettimane = giorno === 'lun-ven';
  const turni = haSettimane ? (cartelliniData[giorno]?.[settimanaCorrente] || []) : (cartelliniData[giorno] || []);

  const depositoOptions = useMemo(() => {
    const set = new Set(turni.map(t => t.deposito));
    return ['Tutti', ...Array.from(set).sort()];
  }, [turni]);

  const cambiaGiorno = (key) => {
    setGiorno(key);
    setSelectedDeposito('Tutti');
  };

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return turni.filter(t => {
      const matchDeposito = selectedDeposito === 'Tutti' || t.deposito === selectedDeposito;
      const matchSearch = !q ||
        t.turno.toLowerCase().includes(q) ||
        t.descrizione.toLowerCase().includes(q) ||
        t.deposito.toLowerCase().includes(q);
      return matchDeposito && matchSearch;
    });
  }, [turni, search, selectedDeposito]);

  const grouped = useMemo(() => {
    const map = {};
    filtered.forEach(t => {
      if (!map[t.deposito]) map[t.deposito] = [];
      map[t.deposito].push(t);
    });
    return Object.entries(map).sort((a, b) => a[0].localeCompare(b[0]));
  }, [filtered]);

  const toggleDeposito = (dep) => {
    setOpenDepositi(prev => ({ ...prev, [dep]: !prev[dep] }));
  };

  return (
    <div style={{
      padding: '1rem',
      background: 'var(--bg-app)',
      minHeight: '100vh',
      paddingBottom: '80px',
      width: '100%',
      maxWidth: '800px',
      margin: '0 auto',
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
        <FileText size={18} /> Cartellini Turni
      </h2>

      <div style={{ display: 'flex', gap: '0.4rem', marginBottom: '1rem' }}>
        {GIORNI_TABS.map(tab => (
          <button
            key={tab.key}
            onClick={() => cambiaGiorno(tab.key)}
            style={{
              flex: '1 1 0',
              minWidth: 0,
              padding: '0.5rem 0.4rem',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              background: giorno === tab.key ? 'var(--accent-cyan)' : 'var(--btn-bg)',
              color: giorno === tab.key ? '#000' : 'var(--text-light)',
              fontWeight: 'bold',
              cursor: 'pointer',
              fontSize: '0.8rem',
              whiteSpace: 'nowrap'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {haSettimane && (
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.4rem',
          padding: '0.3rem 0.7rem',
          marginBottom: '0.75rem',
          borderRadius: '999px',
          border: '1px solid var(--border-color)',
          background: 'var(--bg-card)',
          color: 'var(--text-muted)',
          fontSize: '0.75rem'
        }}>
          Settimana <strong style={{ color: 'var(--accent-cyan)' }}>{settimanaCorrente}</strong> in vigore oggi
        </div>
      )}

      <div style={{
        display: 'flex',
        gap: '0.4rem',
        marginBottom: '0.75rem',
        overflowX: 'auto',
        flexWrap: 'nowrap',
        WebkitOverflowScrolling: 'touch',
        paddingBottom: '0.25rem',
        maxWidth: '100%'
      }}>
        {depositoOptions.map(dep => (
          <button
            key={dep}
            onClick={() => setSelectedDeposito(dep)}
            style={{
              flexShrink: 0,
              padding: '0.35rem 0.8rem',
              borderRadius: '999px',
              border: '1px solid var(--border-color)',
              background: selectedDeposito === dep ? 'var(--accent-cyan)' : 'var(--btn-bg)',
              color: selectedDeposito === dep ? '#000' : 'var(--text-muted)',
              fontWeight: '600',
              cursor: 'pointer',
              fontSize: '0.75rem',
              whiteSpace: 'nowrap'
            }}
          >
            {dep}
          </button>
        ))}
      </div>

      <div className="autocomplete-wrapper" style={{ marginBottom: '1rem', width: '100%' }}>
        <SearchIcon size={18} className="autocomplete-icon" style={{ color: 'var(--accent-cyan)' }} />
        <input
          type="text"
          className="driver-input"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Cerca turno, deposito..."
          style={{ background: 'rgba(56, 189, 248, 0.05)', width: '100%' }}
        />
      </div>

      {turni.length === 0 ? (
        <div style={{
          padding: '2rem',
          textAlign: 'center',
          color: 'var(--text-muted)',
          border: '1px dashed var(--border-color)',
          borderRadius: '12px'
        }}>
          Nessun cartellino caricato per {GIORNI_TABS.find(t => t.key === giorno)?.label.toLowerCase()}.
        </div>
      ) : grouped.length === 0 ? (
        <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
          Nessun turno trovato per "{search}".
        </div>
      ) : (
        grouped.map(([deposito, list]) => {
          const isOpen = openDepositi[deposito] !== false; // aperto di default
          return (
            <div key={deposito} style={{
              marginBottom: '0.75rem',
              borderRadius: '12px',
              border: '1px solid var(--border-color)',
              overflow: 'hidden',
              background: 'var(--bg-card)'
            }}>
              <button
                onClick={() => toggleDeposito(deposito)}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.75rem 1rem',
                  background: 'var(--bg-card-hover)',
                  border: 'none',
                  color: 'var(--accent-cyan)',
                  fontWeight: 'bold',
                  fontSize: '0.9rem',
                  cursor: 'pointer'
                }}
              >
                <span>{deposito} ({list.length})</span>
                <ChevronDown size={18} style={{ transform: isOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
              </button>
              {isOpen && (
                <div>
                  {list.map(t => (
                    <div key={t.turno} style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      gap: '0.75rem',
                      padding: '0.6rem 1rem',
                      borderTop: '1px solid var(--border-color)',
                      fontSize: '0.85rem'
                    }}>
                      <span style={{ color: 'var(--text-light)', fontWeight: '700' }}>{t.turno}</span>
                      <button
                        onClick={() => apriCartellino(t)}
                        style={{
                          flexShrink: 0,
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.35rem',
                          padding: '0.4rem 0.75rem',
                          borderRadius: '8px',
                          border: '1px solid var(--accent-cyan)',
                          background: 'transparent',
                          color: 'var(--accent-cyan)',
                          fontSize: '0.75rem',
                          fontWeight: '600',
                          whiteSpace: 'nowrap',
                          cursor: 'pointer'
                        }}
                      >
                        <FileText size={14} /> Apri cartellino
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })
      )}
    </div>
  );
};

export default Cartellini;
