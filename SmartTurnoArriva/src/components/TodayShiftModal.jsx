import React, { useState, useMemo } from 'react';
import { 
  Clock, 
  Layers, 
  FileText, 
  ExternalLink, 
  Smartphone, 
  Shuffle, 
  ChevronDown, 
  X, 
  Search, 
  Edit3, 
  ArrowRight, 
  Coffee, 
  AlertCircle,
  Truck,
  ShieldCheck
} from 'lucide-react';
import { AppLauncher } from '@capacitor/app-launcher';
import { Capacitor } from '@capacitor/core';
import turniCorseDb from '../data/turni_corse_db.json';
import cartelliniDb from '../data/cartellini.json';
import databaseOrari from '../data/database_orari.json';

const isValidTime = (t) => {
  if (!t || typeof t !== 'string') return false;
  const clean = t.trim();
  if (clean === '-' || clean === '' || clean.length > 5) return false;
  return /^([0-1]?[0-9]|2[0-3])[:.][0-5][0-9]$/.test(clean);
};

const parseTimeToMinutes = (t) => {
  if (!isValidTime(t)) return null;
  const clean = t.trim().replace(':', '.');
  const parts = clean.split('.');
  return parseInt(parts[0], 10) * 60 + parseInt(parts[1], 10);
};

const formatDuration = (mins) => {
  if (!mins || mins <= 0) return '';
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  if (h === 0) return `${m} min`;
  return `${h}h ${m > 0 ? `${m}m` : ''}`;
};

const normalizeStop = (str) => {
  if (!str) return '';
  return str.toLowerCase().replace(/[,\-–—/().]+/g, ' ').replace(/\s+/g, ' ').trim();
};

const matchStop = (stopName, query) => {
  if (!stopName || !query) return false;
  const s = normalizeStop(stopName);
  const q = normalizeStop(query);
  if (s === q || s.includes(q) || q.includes(s)) return true;
  if ((q.includes('porta susa') || q.includes('bolzano')) && (s.includes('porta susa') || s.includes('bolzano'))) return true;
  if ((q.includes('porta nuova') || q.includes('carlo felice')) && (s.includes('porta nuova') || s.includes('carlo felice'))) return true;
  return false;
};

const formatStopDisplayName = (name) => {
  if (!name) return '';
  let clean = name.trim();
  if (clean.toLowerCase().includes('perosa arg')) {
    return 'PEROSA ARGENTINA - piazza Terzo Alpini';
  }
  clean = clean.replace(/\s*\((?:Arrivo|Partenza|arrivo|partenza|part\.)\)/gi, '');
  clean = clean.replace(/\s+(?:arrivo|partenza|part\.)\s*$/gi, '');
  return clean.trim();
};

const isTorinoUrbanStop = (name) => {
  if (!name) return false;
  const lower = name.toLowerCase();
  if (lower.includes('aeroporto') || lower.includes('caselle')) return false;
  return lower.startsWith('to -') || 
         lower.startsWith('to –') || 
         lower.startsWith('torino -') || 
         lower.includes('porta nuova') || 
         lower.includes('porta susa') || 
         lower.includes('bolzano') || 
         lower.includes('stradella') || 
         lower.includes('stampini') || 
         lower.includes('livorno') || 
         lower.includes('umbria') || 
         lower.includes('giulio cesare') || 
         lower.includes('carlo felice') || 
         lower.includes('v emanuele') ||
         lower.includes('torino autostazione') ||
         lower.includes('torino c.so');
};

const isSameLine = (lineA, lineB) => {
  if (!lineA || !lineB) return false;
  const numA = String(lineA).replace(/\D+/g, '');
  const numB = String(lineB).replace(/\D+/g, '');
  if (numA && numB && numA === numB) return true;
  const cleanA = String(lineA).toLowerCase().replace(/[^a-z0-9]/g, '');
  const cleanB = String(lineB).toLowerCase().replace(/[^a-z0-9]/g, '');
  return cleanA === cleanB || cleanA.includes(cleanB) || cleanB.includes(cleanA);
};

const getStopConnections = (stopName, arrivalTime, excludeTripId, dayFilter = 'today', windowMins = 25, excludeLine = null) => {
  const arrMins = parseTimeToMinutes(arrivalTime);
  if (arrMins === null || !stopName) return [];

  let currentLine = excludeLine;
  if (!currentLine && excludeTripId) {
    const curTrip = databaseOrari.trips.find(t => t.id === excludeTripId);
    if (curTrip) currentLine = curTrip.line;
  }

  const isCurrentStopTorinoUrban = isTorinoUrbanStop(stopName);
  const dow = new Date().getDay();
  const connections = [];
  const seenKeys = new Set();

  databaseOrari.trips.forEach(trip => {
    if (trip.id === excludeTripId) return;

    if (currentLine && isSameLine(currentLine, trip.line)) {
      return;
    }

    if (dayFilter === 'today') {
      if (dow === 0) {
        if (!trip.days.includes('7') && !trip.days.includes('8') && trip.season !== 'FES' && trip.season !== 'FEST') return;
      } else if (dow === 6) {
        if (!trip.days.includes('6')) return;
      } else {
        const isFerMatch = trip.days.includes(String(dow)) ||
          trip.days.includes('1') || trip.days.includes('2') || trip.days.includes('3') || trip.days.includes('4') || trip.days.includes('5') ||
          trip.season === 'FER';
        if (!isFerMatch) return;
      }
    }

    const validStops = trip.stops.filter(s => isValidTime(s.time));
    for (let i = 0; i < validStops.length - 1; i++) {
      const s = validStops[i];
      if (matchStop(s.name, stopName) || matchStop(stopName, s.name)) {
        const depMins = parseTimeToMinutes(s.time);
        if (depMins !== null) {
          const diff = (depMins - arrMins + 1440) % 1440;
          if (diff >= 0 && diff <= windowMins) {
            const destStop = validStops[validStops.length - 1];

            if (isCurrentStopTorinoUrban && isTorinoUrbanStop(destStop.name)) {
              return;
            }

            const cleanDest = formatStopDisplayName(destStop.name);
            const key = `${trip.line}_${s.time}_${cleanDest}`;
            if (!seenKeys.has(key)) {
              seenKeys.add(key);
              connections.push({
                tripId: trip.id,
                line: trip.line,
                departureTime: s.time,
                waitMins: diff,
                directionTo: cleanDest
              });
            }
          }
        }
      }
    }
  });

  connections.sort((a, b) => a.waitMins - b.waitMins);
  return connections;
};

const getCartellinoPdf = (code) => {
  if (!code || !cartelliniDb) return null;
  const clean = code.trim().toLowerCase();
  
  const allCartellini = [
    ...(cartelliniDb['lun-ven']?.A || []),
    ...(cartelliniDb['lun-ven']?.B || []),
    ...(cartelliniDb['sabato'] || []),
    ...(cartelliniDb['domenica'] || [])
  ];

  const found = allCartellini.find(c => (c.turno && c.turno.toLowerCase() === clean) || (c.file && c.file.toLowerCase().includes(clean)));
  return found ? `/cartellini/${found.file}` : null;
};

const parseTratta = (str) => {
  if (!str) return { from: '', to: '' };
  const clean = str.trim();
  const parts = clean.split(' - ');
  if (parts.length === 2) {
    return { from: parts[0].trim(), to: parts[1].trim() };
  }
  for (let i = 1; i < parts.length; i++) {
    const left = parts.slice(0, i).join(' - ');
    const right = parts.slice(i).join(' - ');
    const rightUpper = right.toUpperCase();
    if (rightUpper.startsWith('TORINO') || rightUpper.startsWith('TO -') || rightUpper.startsWith('PINEROLO') || rightUpper.startsWith('PEROSA') || rightUpper.startsWith('AIRASCA') || rightUpper.startsWith('CASELLE') || rightUpper.startsWith('IVREA') || rightUpper.startsWith('OULX') || rightUpper.startsWith('SESTRIERE') || rightUpper.startsWith('BOBBIO') || rightUpper.startsWith('BARGE') || rightUpper.startsWith('VILLAR')) {
      return { from: left.trim(), to: right.trim() };
    }
  }
  return { from: parts[0].trim(), to: parts.slice(1).join(' - ').trim() };
};

const matchTripInDb = (c) => {
  if (!c || !databaseOrari || !databaseOrari.trips) return null;
  const lineClean = String(c.linea || '').replace(/\D+/g, '');
  const depM = parseTimeToMinutes(c.partenza);
  if (depM === null) return null;

  const tratta = parseTratta(c.da);

  return databaseOrari.trips.find(t => {
    const tLineClean = String(t.line || '').replace(/\D+/g, '');
    if (lineClean && tLineClean) {
      if (!tLineClean.includes(lineClean) && !lineClean.includes(tLineClean)) return false;
    } else if (lineClean && !tLineClean) {
      return false;
    }

    const validStops = t.stops.filter(s => isValidTime(s.time));
    if (validStops.length === 0) return false;

    return validStops.some(s => {
      const sM = parseTimeToMinutes(s.time);
      if (sM === depM) {
        if (tratta.from) return matchStop(s.name, tratta.from);
        return true;
      }
      return false;
    });
  });
};

export default function TodayShiftModal({ 
  isOpen = true, 
  onClose, 
  initialTurnoCode, 
  driverName, 
  dateStr, 
  isEmbedded = false 
}) {
  const [selectedTurnoCode, setSelectedTurnoCode] = useState(initialTurnoCode || '');
  const [isEditingTurno, setIsEditingTurno] = useState(false);
  const [turnoInputSearch, setTurnoInputSearch] = useState(initialTurnoCode || '');
  const [expandedCorsaIdx, setExpandedCorsaIdx] = useState(null);
  const [expandedConnKey, setExpandedConnKey] = useState(null);
  const [toastMessage, setToastMessage] = useState(null);

  React.useEffect(() => {
    if (initialTurnoCode) {
      setSelectedTurnoCode(initialTurnoCode);
      setTurnoInputSearch(initialTurnoCode);
    }
  }, [initialTurnoCode]);

  const activeTurno = useMemo(() => {
    if (!selectedTurnoCode) return null;
    const clean = selectedTurnoCode.trim().toLowerCase().replace(/^turno\s*/i, '');
    let found = turniCorseDb.find(t => t.codice.toLowerCase() === clean);
    if (!found) {
      found = turniCorseDb.find(t => t.codice.toLowerCase().includes(clean) || clean.includes(t.codice.toLowerCase()));
    }
    return found || null;
  }, [selectedTurnoCode]);

  const autocompleteTurni = useMemo(() => {
    if (!turnoInputSearch || turnoInputSearch.length < 1) return turniCorseDb.slice(0, 10);
    const q = turnoInputSearch.toLowerCase().trim();
    return turniCorseDb.filter(t => 
      t.codice.toLowerCase().includes(q) || 
      (t.nome && t.nome.toLowerCase().includes(q)) || 
      (t.deposito && t.deposito.toLowerCase().includes(q))
    ).slice(0, 12);
  }, [turnoInputSearch]);

  const handleLaunchApp = async (fromName = '', toName = '') => {
    const pkg = 'net.pluservice.Arriva';
    if (fromName && toName) {
      if (typeof navigator !== 'undefined' && navigator.clipboard && navigator.clipboard.writeText) {
        try {
          await navigator.clipboard.writeText(`${fromName} - ${toName}`);
          setToastMessage(`📋 Tratta copiata: ${fromName} ➔ ${toName}`);
          setTimeout(() => setToastMessage(null), 3500);
        } catch (e) {}
      }
    }

    try {
      if (Capacitor.isNativePlatform()) {
        const { value } = await AppLauncher.canOpenUrl({ url: pkg });
        if (value) {
          await AppLauncher.openUrl({ url: pkg });
        } else {
          window.open(`https://play.google.com/store/apps/details?id=${pkg}`, '_system');
        }
      } else {
        window.open(`https://play.google.com/store/apps/details?id=${pkg}`, '_blank');
      }
    } catch (e) {
      window.open(`https://play.google.com/store/apps/details?id=${pkg}`, '_blank');
    }
  };

  const pdfUrl = activeTurno ? getCartellinoPdf(activeTurno.codice) : null;
  const startM = activeTurno ? parseTimeToMinutes(activeTurno.inizio) : null;
  const endM = activeTurno ? parseTimeToMinutes(activeTurno.fine) : null;
  const nastroSpan = (startM !== null && endM !== null) ? formatDuration((endM - startM + 1440) % 1440) : '';

  // Pre-service calculation
  const firstCorsa = activeTurno?.corse?.[0];
  const firstDepM = firstCorsa ? parseTimeToMinutes(firstCorsa.partenza) : null;
  const preDiffM = (startM !== null && firstDepM !== null) ? ((firstDepM - startM + 1440) % 1440) : 0;
  const firstFromClean = firstCorsa ? formatStopDisplayName(parseTratta(firstCorsa.da).from) : '';

  // Post-service calculation
  const lastCorsa = activeTurno?.corse?.[activeTurno.corse.length - 1];
  const lastArrM = lastCorsa ? parseTimeToMinutes(lastCorsa.arrivo) : null;
  const postDiffM = (endM !== null && lastArrM !== null) ? ((endM - lastArrM + 1440) % 1440) : 0;
  const lastToClean = lastCorsa ? formatStopDisplayName(parseTratta(lastCorsa.da).to || lastCorsa.a) : '';

  const renderContent = () => (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-color)',
      borderRadius: '16px',
      width: '100%',
      maxWidth: isEmbedded ? '100%' : '640px',
      maxHeight: isEmbedded ? 'none' : '90vh',
      display: 'flex',
      flexDirection: 'column',
      boxShadow: isEmbedded ? '0 4px 20px rgba(0,0,0,0.15)' : '0 20px 40px rgba(0,0,0,0.3)',
      overflow: 'hidden'
    }}>
      
      {/* Header */}
      <div style={{
        padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-color)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        background: 'linear-gradient(135deg, rgba(245, 166, 35, 0.12), rgba(6, 182, 212, 0.05))'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '1.2rem' }}>🟢</span>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.05rem', fontWeight: '800', color: 'var(--text-main)' }}>
              Il Mio Turno di Oggi
            </h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              {driverName && <span>👤 {driverName}</span>}
              {dateStr && <span>📅 {dateStr}</span>}
            </div>
          </div>
        </div>

        {!isEmbedded && onClose && (
          <button
            type="button"
            onClick={onClose}
            style={{
              background: 'var(--btn-bg)', border: '1px solid var(--border-color)', borderRadius: '50%',
              width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: 'var(--text-muted)', cursor: 'pointer'
            }}
          >
            <X size={18} />
          </button>
        )}
      </div>

      {/* Body */}
      <div style={{
        padding: '1rem 1.25rem',
        overflowY: isEmbedded ? 'visible' : 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem'
      }}>
        
        {/* Turno Selector & Editable Switcher */}
        <div style={{
          background: 'var(--bg-card-hover)', border: '1px solid var(--border-color)',
          borderRadius: '12px', padding: '10px 14px', display: 'flex', flexDirection: 'column', gap: '8px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '6px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Turno:</span>
              <strong style={{
                fontSize: '0.95rem', color: 'var(--accent-orange)', background: 'rgba(245, 166, 35, 0.15)',
                padding: '2px 8px', borderRadius: '6px', border: '1px solid rgba(245, 166, 35, 0.35)'
              }}>
                {selectedTurnoCode || 'Nessuno'}
              </strong>
              {activeTurno && (
                <span style={{ fontSize: '0.8rem', color: 'var(--text-main)', fontWeight: '600' }}>
                  {activeTurno.nome}
                </span>
              )}
            </div>

            <button
              type="button"
              onClick={() => setIsEditingTurno(!isEditingTurno)}
              style={{
                background: isEditingTurno ? 'var(--accent-orange)' : 'var(--btn-bg)',
                color: isEditingTurno ? '#121214' : 'var(--text-main)',
                border: '1px solid var(--border-color)', borderRadius: '6px',
                padding: '4px 10px', fontSize: '0.75rem', fontWeight: '700',
                cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px'
              }}
            >
              <Edit3 size={12} />
              <span>{isEditingTurno ? 'Chiudi' : 'Cambia / Cerca Turno'}</span>
            </button>
          </div>

          {/* Editable Autocomplete Input */}
          {isEditingTurno && (
            <div style={{ marginTop: '6px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              <div style={{ position: 'relative' }}>
                <Search size={15} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  type="text"
                  value={turnoInputSearch}
                  onChange={(e) => setTurnoInputSearch(e.target.value)}
                  placeholder="Digita codice turno (es. Pe0300, Pi0010, Ca0017, To0660)..."
                  style={{
                    width: '100%', background: 'var(--bg-card)', border: '1px solid var(--accent-orange)',
                    borderRadius: '8px', padding: '8px 10px 8px 32px', color: 'var(--text-main)',
                    fontSize: '0.85rem', outline: 'none'
                  }}
                />
              </div>

              <div style={{
                display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '4px', flexWrap: 'wrap'
              }}>
                {autocompleteTurni.map(t => (
                  <button
                    key={t.codice}
                    type="button"
                    onClick={() => {
                      setSelectedTurnoCode(t.codice);
                      setTurnoInputSearch(t.codice);
                      setIsEditingTurno(false);
                    }}
                    style={{
                      background: selectedTurnoCode === t.codice ? 'var(--accent-orange)' : 'var(--btn-bg)',
                      color: selectedTurnoCode === t.codice ? '#121214' : 'var(--text-main)',
                      border: '1px solid var(--border-color)', borderRadius: '6px',
                      padding: '3px 8px', fontSize: '0.72rem', fontWeight: 'bold', cursor: 'pointer'
                    }}
                  >
                    {t.codice} ({t.deposito})
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Turno Summary Hero & Times */}
        {activeTurno ? (
          <>
            <div style={{
              background: 'var(--bg-card-hover)', border: '1px solid var(--border-color)',
              borderRadius: '12px', padding: '10px 14px', display: 'flex', flexDirection: 'column', gap: '8px'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Clock size={16} style={{ color: '#10b981' }} />
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Presa ➔ Smonto:</span>
                  <strong style={{ fontSize: '0.95rem', color: 'var(--text-main)' }}>{activeTurno.inizio} ➔ {activeTurno.fine}</strong>
                  {nastroSpan && (
                    <span style={{ fontSize: '0.75rem', fontWeight: 'bold', color: 'var(--accent-orange)', background: 'rgba(245, 166, 35, 0.12)', padding: '2px 6px', borderRadius: '4px' }}>
                      ⏱️ {nastroSpan}
                    </span>
                  )}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '0.72rem', color: 'var(--accent-cyan)', background: 'rgba(6, 182, 212, 0.12)', padding: '2px 6px', borderRadius: '4px' }}>
                    Dep. {activeTurno.deposito}
                  </span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', background: 'var(--btn-bg)', padding: '2px 6px', borderRadius: '4px' }}>
                    {activeTurno.giorno}
                  </span>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border-color)', paddingTop: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.78rem', color: 'var(--text-main)' }}>
                  <Layers size={14} style={{ color: 'var(--accent-cyan)' }} />
                  <span><strong>{activeTurno.corse.length}</strong> corse di linea assegnate</span>
                </div>

                {pdfUrl && (
                  <a
                    href={pdfUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: 'inline-flex', alignItems: 'center', gap: '4px',
                      background: 'rgba(6, 182, 212, 0.15)', border: '1px solid rgba(6, 182, 212, 0.35)',
                      color: 'var(--accent-cyan)', padding: '3px 8px', borderRadius: '6px',
                      fontSize: '0.72rem', fontWeight: 'bold', textDecoration: 'none'
                    }}
                  >
                    <FileText size={12} />
                    <span>PDF Cartellino</span>
                    <ExternalLink size={10} />
                  </a>
                )}
              </div>
            </div>

            {/* Timeline of Pre-Service, Corse, Deadheads, and Post-Service */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', borderLeft: '3px solid var(--accent-orange)', paddingLeft: '10px' }}>
              
              {/* 1. PRE-SERVIZIO CARD */}
              {preDiffM > 0 && (
                <div style={{
                  background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.08))',
                  border: '1px solid rgba(16, 185, 129, 0.35)',
                  borderRadius: '10px', padding: '10px 12px', display: 'flex', flexDirection: 'column', gap: '6px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{
                        background: '#10b981', color: '#121214', fontWeight: '800',
                        fontSize: '0.72rem', padding: '2px 7px', borderRadius: '4px'
                      }}>
                        PRE-SERVIZIO
                      </span>
                      <span style={{ color: 'var(--text-main)', fontWeight: '700', fontSize: '0.78rem' }}>
                        Presa Servizio & Trasferimento di Andata
                      </span>
                    </div>
                    <span style={{ fontSize: '0.72rem', fontWeight: 'bold', color: '#10b981' }}>
                      ⏱️ {formatDuration(preDiffM)}
                    </span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-card)', border: '1px solid var(--border-color)', padding: '6px 10px', borderRadius: '8px', fontSize: '0.78rem' }}>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                      <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Presa Servizio</span>
                      <strong style={{ color: '#10b981' }}>{activeTurno.inizio} (Dep. {activeTurno.deposito})</strong>
                    </div>
                    <ArrowRight size={14} style={{ color: 'var(--text-muted)' }} />
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                      <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Inizio 1ª Corsa</span>
                      <strong style={{ color: 'var(--accent-cyan)' }}>{firstCorsa.partenza} ({firstFromClean})</strong>
                    </div>
                  </div>
                </div>
              )}

              {/* 2. CHRONOLOGICAL CORSE */}
              {activeTurno.corse.map((c, cIdx) => {
                const tratta = parseTratta(c.da);
                const fromClean = formatStopDisplayName(tratta.from);
                const toClean = formatStopDisplayName(tratta.to || c.a);
                const depM = parseTimeToMinutes(c.partenza);
                const arrM = parseTimeToMinutes(c.arrivo);
                const runDur = (depM !== null && arrM !== null) ? formatDuration((arrM - depM + 1440) % 1440) : '';
                const matchedTrip = matchTripInDb(c);
                const isCorsaOpen = expandedCorsaIdx === cIdx;

                // Calculate Layover or Deadhead Transfer
                let intermediateStep = null;
                if (cIdx < activeTurno.corse.length - 1) {
                  const nextC = activeTurno.corse[cIdx + 1];
                  const nextTratta = parseTratta(nextC.da);
                  const nextFromClean = formatStopDisplayName(nextTratta.from);
                  const nextDepM = parseTimeToMinutes(nextC.partenza);

                  if (arrM !== null && nextDepM !== null) {
                    const diff = (nextDepM - arrM + 1440) % 1440;
                    const isDeadhead = toClean && nextFromClean && !matchStop(toClean, nextFromClean);

                    intermediateStep = {
                      mins: diff,
                      formatted: formatDuration(diff),
                      fromTime: c.arrivo,
                      toTime: nextC.partenza,
                      fromLoc: toClean,
                      toLoc: nextFromClean,
                      isDeadhead
                    };
                  }
                }

                return (
                  <React.Fragment key={cIdx}>
                    {/* Corsa Card */}
                    <div style={{
                      background: 'var(--bg-card)', border: '1px solid var(--border-color)',
                      borderRadius: '10px', padding: '10px 12px', display: 'flex', flexDirection: 'column', gap: '8px'
                    }}>
                      {/* Corsa Header */}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <span style={{
                            background: '#10b981', color: '#121214', fontWeight: '800',
                            fontSize: '0.72rem', padding: '2px 7px', borderRadius: '4px'
                          }}>
                            {cIdx + 1}ª CORSA
                          </span>
                          <span style={{
                            background: 'rgba(6, 182, 212, 0.15)', color: 'var(--accent-cyan)',
                            fontWeight: '700', fontSize: '0.72rem', padding: '2px 7px', borderRadius: '4px',
                            border: '1px solid rgba(6, 182, 212, 0.3)'
                          }}>
                            Linea {c.linea}
                          </span>
                        </div>

                        {runDur && (
                          <span style={{ fontSize: '0.72rem', fontWeight: 'bold', color: 'var(--accent-orange)' }}>
                            ⏱️ {runDur}
                          </span>
                        )}
                      </div>

                      {/* Origin -> Destination Times Hero */}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-card-hover)', padding: '6px 10px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                        <div style={{ display: 'flex', flexDirection: 'column', maxWidth: '42%' }}>
                          <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Partenza</span>
                          <span style={{ fontSize: '1.1rem', fontWeight: '800', color: '#10b981' }}>{c.partenza}</span>
                          <span style={{ fontSize: '0.72rem', color: 'var(--text-main)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {fromClean}
                          </span>
                        </div>

                        <ArrowRight size={16} style={{ color: 'var(--text-muted)' }} />

                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', maxWidth: '42%' }}>
                          <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Arrivo</span>
                          <span style={{ fontSize: '1.1rem', fontWeight: '800', color: 'var(--accent-cyan)' }}>{c.arrivo}</span>
                          <span style={{ fontSize: '0.72rem', color: 'var(--text-main)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', textAlign: 'right' }}>
                            {toClean}
                          </span>
                        </div>
                      </div>

                      {/* Action / Expansion row */}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '2px', flexWrap: 'wrap', gap: '6px' }}>
                        {matchedTrip ? (
                          <button
                            type="button"
                            onClick={() => setExpandedCorsaIdx(isCorsaOpen ? null : cIdx)}
                            style={{
                              background: 'transparent', border: 'none', color: 'var(--accent-orange)',
                              fontSize: '0.73rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: '600'
                            }}
                          >
                            <span>{isCorsaOpen ? 'Nascondi fermate' : `Vedi ${matchedTrip.stops.filter(s => isValidTime(s.time)).length} fermate & coincidenze`}</span>
                            <ChevronDown size={13} style={{ transform: isCorsaOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
                          </button>
                        ) : (
                          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                            Corsa Diretta Cartellino
                          </span>
                        )}

                        <button
                          type="button"
                          onClick={() => handleLaunchApp(fromClean, toClean)}
                          style={{
                            background: 'var(--btn-bg)', border: '1px solid var(--border-color)',
                            borderRadius: '6px', padding: '3px 8px', color: 'var(--text-main)',
                            fontSize: '0.7rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px'
                          }}
                        >
                          <Smartphone size={11} />
                          <span>MyPay Tratta</span>
                        </button>
                      </div>

                      {/* Expandable stops with coincidenze */}
                      {isCorsaOpen && matchedTrip && (
                        <div style={{
                          marginTop: '4px', background: 'var(--bg-card-hover)', border: '1px solid var(--border-color)',
                          borderRadius: '8px', padding: '8px 10px', display: 'flex', flexDirection: 'column', gap: '4px'
                        }}>
                          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 'bold', marginBottom: '2px' }}>
                            Passi Orari Programmati Corsa {matchedTrip.id}:
                          </div>
                          {matchedTrip.stops.filter(s => isValidTime(s.time)).map((st, stIdx, arr) => {
                            const isStart = stIdx === 0;
                            const isEnd = stIdx === arr.length - 1;
                            const connections = getStopConnections(st.name, st.time, matchedTrip.id, 'today', 25, c.linea);
                            const stopConnKey = `today_${cIdx}_s${stIdx}`;
                            const isStopConnOpen = expandedConnKey === stopConnKey;

                            return (
                              <div key={stIdx} style={{ display: 'flex', flexDirection: 'column' }}>
                                <div style={{
                                  display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem',
                                  padding: (isStart || isEnd) ? '3px 6px' : '2px 0',
                                  background: isStart ? 'rgba(16, 185, 129, 0.12)' : isEnd ? 'rgba(6, 182, 212, 0.12)' : 'transparent',
                                  borderRadius: '4px'
                                }}>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px', flexWrap: 'wrap' }}>
                                    <span style={{ fontSize: '0.7rem' }}>{isStart ? '🟢' : isEnd ? '🏁' : '🔵'}</span>
                                    <span style={{ color: (isStart || isEnd) ? 'var(--text-main)' : 'var(--text-muted)', fontWeight: (isStart || isEnd) ? '700' : 'normal' }}>
                                      {formatStopDisplayName(st.name)}
                                    </span>
                                    {connections.length > 0 && (
                                      <button
                                        type="button"
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          setExpandedConnKey(isStopConnOpen ? null : stopConnKey);
                                        }}
                                        style={{
                                          background: isStopConnOpen ? 'rgba(245, 166, 35, 0.3)' : 'rgba(245, 166, 35, 0.12)',
                                          border: '1px solid rgba(245, 166, 35, 0.4)',
                                          borderRadius: '4px', padding: '1px 5px', fontSize: '0.62rem',
                                          fontWeight: '700', color: 'var(--accent-orange)', cursor: 'pointer',
                                          display: 'inline-flex', alignItems: 'center', gap: '2px'
                                        }}
                                      >
                                        <Shuffle size={9} />
                                        <span>{connections.length} coinc.</span>
                                      </button>
                                    )}
                                  </div>
                                  <span style={{ color: isStart ? '#10b981' : isEnd ? 'var(--accent-cyan)' : 'var(--text-muted)', fontWeight: (isStart || isEnd) ? '700' : '500' }}>
                                    {st.time}
                                  </span>
                                </div>

                                {/* Active Connections Sub-Box */}
                                {isStopConnOpen && (
                                  <div style={{
                                    margin: '2px 0 4px 14px', padding: '6px 8px',
                                    background: 'rgba(245, 166, 35, 0.1)', borderLeft: '3px solid var(--accent-orange)',
                                    borderRadius: '4px', fontSize: '0.7rem', display: 'flex', flexDirection: 'column', gap: '4px'
                                  }}>
                                    <span style={{ color: 'var(--accent-orange)', fontWeight: 'bold' }}>Coincidenze attive (entro 25 min):</span>
                                    {connections.map((co, coIdx) => (
                                      <div key={coIdx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <span style={{ color: 'var(--text-main)' }}>L. {co.line} ➔ {co.directionTo} ({co.tripId})</span>
                                        <strong style={{ color: '#10b981' }}>{co.departureTime} (+{co.waitMins}m)</strong>
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      )}

                    </div>

                    {/* 3. INTERMEDIATE LAYOVER OR DEADHEAD TRANSFER */}
                    {intermediateStep && intermediateStep.mins > 0 && (
                      intermediateStep.isDeadhead ? (
                        <div style={{
                          display: 'flex', alignItems: 'center', gap: '8px',
                          background: 'linear-gradient(90deg, rgba(6, 182, 212, 0.15), rgba(6, 182, 212, 0.04))',
                          border: '1px dashed rgba(6, 182, 212, 0.5)',
                          borderRadius: '8px', padding: '7px 12px', fontSize: '0.75rem', color: 'var(--accent-cyan)'
                        }}>
                          <Truck size={15} />
                          <span>
                            <strong>Trasferimento a vuoto / Raccordo ({intermediateStep.formatted})</strong> da {intermediateStep.fromLoc} a {intermediateStep.toLoc} (dalle {intermediateStep.fromTime} alle {intermediateStep.toTime})
                          </span>
                        </div>
                      ) : (
                        <div style={{
                          display: 'flex', alignItems: 'center', gap: '8px',
                          background: 'linear-gradient(90deg, rgba(245, 166, 35, 0.12), rgba(245, 166, 35, 0.03))',
                          border: '1px dashed rgba(245, 166, 35, 0.4)',
                          borderRadius: '8px', padding: '6px 12px', fontSize: '0.75rem', color: 'var(--accent-orange)'
                        }}>
                          <Coffee size={14} />
                          <span>
                            <strong>Sosta al capolinea ({intermediateStep.formatted})</strong> dalle {intermediateStep.fromTime} alle {intermediateStep.toTime}
                            {intermediateStep.fromLoc ? ` a ${intermediateStep.fromLoc}` : ''}
                          </span>
                        </div>
                      )
                    )}
                  </React.Fragment>
                );
              })}

              {/* 4. POST-SERVIZIO CARD */}
              {postDiffM > 0 && (
                <div style={{
                  background: 'linear-gradient(135deg, rgba(245, 166, 35, 0.15), rgba(239, 68, 68, 0.08))',
                  border: '1px solid rgba(245, 166, 35, 0.35)',
                  borderRadius: '10px', padding: '10px 12px', display: 'flex', flexDirection: 'column', gap: '6px'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{
                        background: 'var(--accent-orange)', color: '#121214', fontWeight: '800',
                        fontSize: '0.72rem', padding: '2px 7px', borderRadius: '4px'
                      }}>
                        POST-SERVIZIO
                      </span>
                      <span style={{ color: 'var(--text-main)', fontWeight: '700', fontSize: '0.78rem' }}>
                        Rientro in Deposito, Rifornimento & Smonto
                      </span>
                    </div>
                    <span style={{ fontSize: '0.72rem', fontWeight: 'bold', color: 'var(--accent-orange)' }}>
                      ⏱️ {formatDuration(postDiffM)}
                    </span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-card)', border: '1px solid var(--border-color)', padding: '6px 10px', borderRadius: '8px', fontSize: '0.78rem' }}>
                    <div style={{ display: 'flex', flexDirection: 'column' }}>
                      <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Arrivo Ultima Corsa</span>
                      <strong style={{ color: 'var(--accent-cyan)' }}>{lastCorsa.arrivo} ({lastToClean})</strong>
                    </div>
                    <ArrowRight size={14} style={{ color: 'var(--text-muted)' }} />
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                      <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Smonto Servizio</span>
                      <strong style={{ color: 'var(--accent-orange)' }}>{activeTurno.fine} (Dep. {activeTurno.deposito})</strong>
                    </div>
                  </div>
                </div>
              )}

            </div>
          </>
        ) : (
          <div style={{
            padding: '2.5rem 1rem', textAlign: 'center', background: 'var(--bg-card)',
            borderRadius: '12px', border: '1px dashed var(--border-color)', color: 'var(--text-muted)'
          }}>
            <AlertCircle size={32} style={{ color: 'var(--accent-orange)', margin: '0 auto 0.5rem' }} />
            <h4 style={{ color: 'var(--text-main)', margin: '0 0 0.25rem 0' }}>Nessun turno operativo corrispondente</h4>
            <p style={{ margin: 0, fontSize: '0.85rem' }}>
              Il turno <strong>"{selectedTurnoCode}"</strong> potrebbe essere un riposo (RIP), disponibilità (DISP) o non avere corse di linea indicizzate.
            </p>
            <button
              type="button"
              onClick={() => setIsEditingTurno(true)}
              style={{
                marginTop: '1rem', background: 'var(--accent-orange)', color: '#121214',
                border: 'none', borderRadius: '8px', padding: '6px 14px', fontWeight: 'bold',
                fontSize: '0.8rem', cursor: 'pointer'
              }}
            >
              Scegli un altro Turno
            </button>
          </div>
        )}

      </div>

      {/* Modal Footer (only when modal popup) */}
      {!isEmbedded && (
        <div style={{
          padding: '0.75rem 1.25rem', borderTop: '1px solid var(--border-color)',
          display: 'flex', justifyContent: 'flex-end', background: 'var(--bg-card-hover)'
        }}>
          <button
            type="button"
            onClick={onClose}
            style={{
              background: 'var(--accent-orange)', color: '#121214', border: 'none',
              borderRadius: '8px', padding: '7px 18px', fontWeight: '800',
              fontSize: '0.85rem', cursor: 'pointer'
            }}
          >
            Chiudi
          </button>
        </div>
      )}

    </div>
  );

  if (isEmbedded) {
    return (
      <div style={{ width: '100%', maxWidth: '800px', margin: '0 auto' }}>
        {renderContent()}
        {/* Toast notification */}
        {toastMessage && (
          <div style={{
            position: 'fixed', bottom: '24px', left: '50%', transform: 'translateX(-50%)',
            background: '#10b981', color: '#121214', padding: '8px 16px', borderRadius: '10px',
            fontWeight: 'bold', fontSize: '0.82rem', boxShadow: '0 8px 24px rgba(0,0,0,0.2)', zIndex: 100000
          }}>
            {toastMessage}
          </div>
        )}
      </div>
    );
  }

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0, 0, 0, 0.65)', backdropFilter: 'blur(6px)',
      zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem'
    }}>
      {renderContent()}

      {/* Toast notification */}
      {toastMessage && (
        <div style={{
          position: 'fixed', bottom: '24px', left: '50%', transform: 'translateX(-50%)',
          background: '#10b981', color: '#121214', padding: '8px 16px', borderRadius: '10px',
          fontWeight: 'bold', fontSize: '0.82rem', boxShadow: '0 8px 24px rgba(0,0,0,0.2)', zIndex: 100000
        }}>
          {toastMessage}
        </div>
      )}
    </div>
  );
}
