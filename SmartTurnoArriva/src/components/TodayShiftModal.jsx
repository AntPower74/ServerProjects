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
  
  // Riconoscimento Hub Aeroportuali (Malpensa T1 / T2 / Ovest / Nord / Est)
  if (q.includes('malpensa') && s.includes('malpensa')) return true;
  if ((q.includes('caselle') || q.includes('aeroporto')) && (s.includes('caselle') || s.includes('aeroporto'))) return true;
  
  // Hub Città di Torino
  if ((q.includes('porta susa') || q.includes('bolzano') || q.includes('autostazione')) && (s.includes('porta susa') || s.includes('bolzano') || s.includes('autostazione'))) return true;
  if ((q.includes('porta nuova') || q.includes('carlo felice') || q.includes('v emanuele')) && (s.includes('porta nuova') || s.includes('carlo felice') || s.includes('v emanuele'))) return true;
  if (q.includes('torino') && s.includes('torino')) return true;

  // Capolinea e Hub principali
  const hubs = ['pinerolo', 'perosa', 'sestriere', 'bobbio', 'airasca', 'ivrea', 'oulx', 'barge', 'torre pellice', 'claviere', 'cesana', 'bardonecchia', 'susa', 'cumiana', 'giaveno', 'rivalta', 'orbassano', 'trana', 'avigliana'];
  for (const h of hubs) {
    if (q.includes(h) && s.includes(h)) return true;
  }

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
  const parts = clean.split(/\s*[-–—]\s*/).filter(Boolean);
  
  if (parts.length === 1) {
    return { from: parts[0].trim(), to: '' };
  }
  if (parts.length === 2) {
    return { from: parts[0].trim(), to: parts[1].trim() };
  }
  if (parts.length >= 3) {
    const p0_u = parts[0].toUpperCase();
    const p1_u = parts[1].toUpperCase();
    
    // Se le prime due parti compongono il capolinea di origine (es. TORINO - Autostazione c.so Bolzano)
    if (
      p0_u.includes('TORINO') || p0_u.includes('TO') ||
      p0_u.includes('PINEROLO') || p0_u.includes('PEROSA') ||
      p0_u.includes('SESTRIERE') || p0_u.includes('CASELLE') ||
      p0_u.includes('IVREA') || p0_u.includes('AIRASCA') ||
      p0_u.includes('BOBBIO') || p0_u.includes('BARGE') ||
      p0_u.includes('OULX') || p0_u.includes('SUSA')
    ) {
      if (
        p1_u.includes('AUTOSTAZIONE') || p1_u.includes('BOLZANO') ||
        p1_u.includes('STAZIONE') || p1_u.includes('FS') ||
        p1_u.includes('PORTA') || p1_u.includes('CATTANEO') ||
        p1_u.includes('GIULIO') || p1_u.includes('CARDUCCI') ||
        p1_u.includes('MOMBARCARO') || p1_u.includes('SANTA RITA') ||
        p1_u.includes('CAIO MARIO') || p1_u.includes('PIAZZA') ||
        p1_u.includes('CORSO') || p1_u.includes('VIA') ||
        p1_u.includes('V.') || p1_u.includes('CAPOL') || p1_u.includes('COLLE')
      ) {
        return {
          from: `${parts[0]} - ${parts[1]}`,
          to: parts.slice(2).join(' - ')
        };
      }
    }

    // Se le ultime due parti compongono il capolinea di destinazione (es. MALPENSA OVEST - TORINO - Autostazione c.so Bolzano)
    const pEnd1_u = parts[parts.length - 2].toUpperCase();
    const pEnd2_u = parts[parts.length - 1].toUpperCase();
    if (
      pEnd1_u.includes('TORINO') || pEnd1_u.includes('TO') ||
      pEnd1_u.includes('PINEROLO') || pEnd1_u.includes('PEROSA') ||
      pEnd1_u.includes('SESTRIERE') || pEnd1_u.includes('CASELLE') ||
      pEnd1_u.includes('IVREA') || pEnd1_u.includes('AIRASCA') ||
      pEnd1_u.includes('BOBBIO') || pEnd1_u.includes('BARGE') ||
      pEnd1_u.includes('OULX') || pEnd1_u.includes('SUSA')
    ) {
      return {
        from: parts.slice(0, parts.length - 2).join(' - '),
        to: `${parts[parts.length - 2]} - ${parts[parts.length - 1]}`
      };
    }

    return {
      from: parts[0].trim(),
      to: parts.slice(1).join(' - ').trim()
    };
  }
  return { from: clean, to: '' };
};

const getCleanTratta = (c) => {
  if (!c) return { fromClean: '', toClean: '' };
  const parsedDa = parseTratta(c.da);
  const parsedA = parseTratta(c.a);
  
  let from = parsedDa.from || c.da || '';
  let to = parsedDa.to || parsedA.to || parsedA.from || c.a || '';
  
  return {
    fromClean: formatStopDisplayName(from),
    toClean: formatStopDisplayName(to)
  };
};



const matchTripInDb = (c) => {
  if (!c || !databaseOrari || !databaseOrari.trips) return null;
  const lineClean = String(c.linea || '').replace(/\D+/g, '');
  const depM = parseTimeToMinutes(c.partenza);
  const arrM = parseTimeToMinutes(c.arrivo);
  if (depM === null) return null;

  const { fromClean, toClean } = getCleanTratta(c);

  let bestTrip = null;
  let bestScore = -1;

  for (const t of databaseOrari.trips) {
    const tLineClean = String(t.line || '').replace(/\D+/g, '');
    if (lineClean && tLineClean) {
      if (!tLineClean.includes(lineClean) && !lineClean.includes(tLineClean)) continue;
    } else if (lineClean && !tLineClean) {
      continue;
    }

    const validStops = t.stops.filter(s => isValidTime(s.time));
    if (validStops.length === 0) continue;

    const firstStop = validStops[0];
    const lastStop = validStops[validStops.length - 1];
    const tDepM = parseTimeToMinutes(firstStop.time);
    const tArrM = parseTimeToMinutes(lastStop.time);

    let score = 0;

    // 1. Partenza esatta dal capolinea di partenza
    if (tDepM !== null && tDepM === depM) {
      score += 10;
      if (fromClean && matchStop(firstStop.name, fromClean)) score += 5;
    }

    // 2. Arrivo esatto al capolinea di destinazione
    if (arrM !== null && tArrM !== null && tArrM === arrM) {
      score += 10;
      if (toClean && matchStop(lastStop.name, toClean)) score += 5;
    }

    // 3. Corrispondenza tratta
    if (fromClean && matchStop(firstStop.name, fromClean)) score += 3;
    if (toClean && matchStop(lastStop.name, toClean)) score += 3;

    // 4. Se corsa parziale / intermedia
    if (score < 10) {
      const intermediateMatch = validStops.some((s, idx) => {
        const sM = parseTimeToMinutes(s.time);
        if (sM === depM && fromClean && matchStop(s.name, fromClean)) {
          return idx < validStops.length - 1;
        }
        return false;
      });
      if (intermediateMatch) score += 6;
    }

    if (score > bestScore && score >= 10) {
      bestScore = score;
      bestTrip = t;
    }
  }

  return bestTrip;
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
  const firstFromClean = getCleanTratta(firstCorsa).fromClean;

  // Post-service calculation
  const lastCorsa = activeTurno?.corse?.[activeTurno.corse.length - 1];
  const lastArrM = lastCorsa ? parseTimeToMinutes(lastCorsa.arrivo) : null;
  const postDiffM = (endM !== null && lastArrM !== null) ? ((endM - lastArrM + 1440) % 1440) : 0;
  const lastToClean = getCleanTratta(lastCorsa).toClean;


  const renderContent = () => (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-color)',
      borderRadius: '16px',
      width: '100%',
      maxWidth: isEmbedded ? '800px' : '640px',
      margin: '0 auto',
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
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              
              {/* 1. PRE-SERVIZIO SINGLE ROW */}
              {preDiffM > 0 && (
                <div style={{
                  background: 'rgba(16, 185, 129, 0.08)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  borderRadius: '8px', padding: '6px 10px',
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  fontSize: '0.78rem', flexWrap: 'wrap', gap: '6px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                    <span style={{
                      background: '#10b981', color: '#121214', fontWeight: '800',
                      fontSize: '0.68rem', padding: '2px 6px', borderRadius: '4px'
                    }}>
                      PRE-SERVIZIO
                    </span>
                    <span style={{ color: 'var(--text-main)' }}>
                      Presa <strong style={{ color: '#10b981' }}>{activeTurno.inizio}</strong> (Dep. {activeTurno.deposito})
                    </span>
                    <ArrowRight size={12} style={{ color: 'var(--text-muted)' }} />
                    <span style={{ color: 'var(--text-main)' }}>
                      1ª Corsa <strong style={{ color: 'var(--accent-cyan)' }}>{firstCorsa.partenza}</strong> ({firstFromClean})
                    </span>
                  </div>
                  <span style={{ fontSize: '0.72rem', fontWeight: 'bold', color: '#10b981' }}>
                    ⏱️ {formatDuration(preDiffM)}
                  </span>
                </div>
              )}

              {/* 2. CHRONOLOGICAL CORSE IN SINGLE ROWS: [N° Corsa] [Linea] [Partenza ➔ Arrivo] [Tratta Da ➔ A] */}
              {activeTurno.corse.map((c, cIdx) => {
                const { fromClean, toClean } = getCleanTratta(c);
                const depM = parseTimeToMinutes(c.partenza);
                const arrM = parseTimeToMinutes(c.arrivo);
                const runDur = (depM !== null && arrM !== null) ? formatDuration((arrM - depM + 1440) % 1440) : '';
                const matchedTrip = matchTripInDb(c);
                const isCorsaOpen = expandedCorsaIdx === cIdx;

                // Calculate Layover or Deadhead Transfer
                let intermediateStep = null;
                if (cIdx < activeTurno.corse.length - 1) {
                  const nextC = activeTurno.corse[cIdx + 1];
                  const nextTratta = getCleanTratta(nextC);
                  const nextFromClean = nextTratta.fromClean;
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
                    {/* Corsa Single Row */}
                    <div 
                      onClick={() => matchedTrip && setExpandedCorsaIdx(isCorsaOpen ? null : cIdx)}
                      style={{
                        background: isCorsaOpen ? 'var(--bg-card-hover)' : 'var(--bg-card)',
                        border: '1px solid var(--border-color)',
                        borderRadius: '8px', padding: '8px 10px',
                        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                        gap: '8px', flexWrap: 'wrap',
                        cursor: matchedTrip ? 'pointer' : 'default',
                        transition: 'background 0.15s ease'
                      }}
                    >
                      {/* [N° Corsa] [Linea] */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '5px', minWidth: '95px' }}>
                        <span style={{
                          background: '#10b981', color: '#121214', fontWeight: '800',
                          fontSize: '0.72rem', padding: '2px 6px', borderRadius: '4px'
                        }}>
                          {cIdx + 1}ª
                        </span>
                        <span style={{
                          background: 'rgba(6, 182, 212, 0.15)', color: 'var(--accent-cyan)',
                          fontWeight: '700', fontSize: '0.72rem', padding: '2px 6px', borderRadius: '4px',
                          border: '1px solid rgba(6, 182, 212, 0.3)'
                        }}>
                          L. {c.linea}
                        </span>
                      </div>

                      {/* [Partenza ➔ Arrivo] */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '5px', minWidth: '120px' }}>
                        <strong style={{ fontSize: '0.92rem', color: '#10b981', fontFamily: 'monospace' }}>{c.partenza}</strong>
                        <ArrowRight size={13} style={{ color: 'var(--text-muted)' }} />
                        <strong style={{ fontSize: '0.92rem', color: 'var(--accent-cyan)', fontFamily: 'monospace' }}>{c.arrivo}</strong>
                        {runDur && (
                          <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                            ({runDur})
                          </span>
                        )}
                      </div>

                      {/* [Tratta Da ➔ A] */}
                      <div style={{
                        flex: '1 1 180px',
                        fontSize: '0.78rem',
                        color: 'var(--text-main)',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '5px',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                      }}>
                        <span style={{ fontWeight: '600', color: 'var(--text-main)' }}>{fromClean}</span>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>➔</span>
                        <span style={{ fontWeight: '600', color: 'var(--text-main)' }}>{toClean}</span>
                      </div>

                      {/* Expand indicator if stops available */}
                      {matchedTrip && (
                        <div style={{ display: 'flex', alignItems: 'center', color: 'var(--text-muted)' }}>
                          <ChevronDown size={14} style={{ transform: isCorsaOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
                        </div>
                      )}
                    </div>

                    {/* Expandable stops on tap */}
                    {isCorsaOpen && matchedTrip && (
                      <div style={{
                        margin: '-2px 0 4px 12px', background: 'var(--bg-card-hover)', border: '1px solid var(--border-color)',
                        borderRadius: '8px', padding: '6px 10px', display: 'flex', flexDirection: 'column', gap: '3px'
                      }}>
                        <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', fontWeight: 'bold', marginBottom: '2px' }}>
                          Fermate Programmate Corsa {matchedTrip.id}:
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
                                display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.73rem',
                                padding: (isStart || isEnd) ? '2px 4px' : '1px 0',
                                background: isStart ? 'rgba(16, 185, 129, 0.12)' : isEnd ? 'rgba(6, 182, 212, 0.12)' : 'transparent',
                                borderRadius: '4px'
                              }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '5px', flexWrap: 'wrap' }}>
                                  <span style={{ fontSize: '0.65rem' }}>{isStart ? '🟢' : isEnd ? '🏁' : '🔵'}</span>
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
                                        borderRadius: '4px', padding: '1px 4px', fontSize: '0.6rem',
                                        fontWeight: '700', color: 'var(--accent-orange)', cursor: 'pointer',
                                        display: 'inline-flex', alignItems: 'center', gap: '2px'
                                      }}
                                    >
                                      <Shuffle size={8} />
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
                                  margin: '2px 0 3px 12px', padding: '4px 8px',
                                  background: 'rgba(245, 166, 35, 0.1)', borderLeft: '3px solid var(--accent-orange)',
                                  borderRadius: '4px', fontSize: '0.68rem', display: 'flex', flexDirection: 'column', gap: '3px'
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

                    {/* 3. INTERMEDIATE LAYOVER OR DEADHEAD TRANSFER SINGLE ROW */}
                    {intermediateStep && intermediateStep.mins > 0 && (
                      <div style={{
                        display: 'flex', alignItems: 'center', gap: '6px',
                        background: intermediateStep.isDeadhead ? 'rgba(6, 182, 212, 0.06)' : 'rgba(245, 166, 35, 0.06)',
                        border: intermediateStep.isDeadhead ? '1px dashed rgba(6, 182, 212, 0.35)' : '1px dashed rgba(245, 166, 35, 0.3)',
                        borderRadius: '6px', padding: '4px 10px', fontSize: '0.72rem',
                        color: intermediateStep.isDeadhead ? 'var(--accent-cyan)' : 'var(--accent-orange)'
                      }}>
                        {intermediateStep.isDeadhead ? <Truck size={13} /> : <Coffee size={13} />}
                        <span>
                          <strong>{intermediateStep.isDeadhead ? 'Raccordo' : 'Sosta'} ({intermediateStep.formatted}):</strong> dalle {intermediateStep.fromTime} alle {intermediateStep.toTime}
                          {intermediateStep.isDeadhead ? ` (da ${intermediateStep.fromLoc} a ${intermediateStep.toLoc})` : (intermediateStep.fromLoc ? ` a ${intermediateStep.fromLoc}` : '')}
                        </span>
                      </div>
                    )}
                  </React.Fragment>
                );
              })}

              {/* 4. POST-SERVIZIO SINGLE ROW */}
              {postDiffM > 0 && (
                <div style={{
                  background: 'rgba(245, 166, 35, 0.08)',
                  border: '1px solid rgba(245, 166, 35, 0.3)',
                  borderRadius: '8px', padding: '6px 10px',
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  fontSize: '0.78rem', flexWrap: 'wrap', gap: '6px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                    <span style={{
                      background: 'var(--accent-orange)', color: '#121214', fontWeight: '800',
                      fontSize: '0.68rem', padding: '2px 6px', borderRadius: '4px'
                    }}>
                      POST-SERVIZIO
                    </span>
                    <span style={{ color: 'var(--text-main)' }}>
                      Arrivo Ultima Corsa <strong style={{ color: 'var(--accent-cyan)' }}>{lastCorsa.arrivo}</strong> ({lastToClean})
                    </span>
                    <ArrowRight size={12} style={{ color: 'var(--text-muted)' }} />
                    <span style={{ color: 'var(--text-main)' }}>
                      Smonto <strong style={{ color: 'var(--accent-orange)' }}>{activeTurno.fine}</strong> (Dep. {activeTurno.deposito})
                    </span>
                  </div>
                  <span style={{ fontSize: '0.72rem', fontWeight: 'bold', color: 'var(--accent-orange)' }}>
                    ⏱️ {formatDuration(postDiffM)}
                  </span>
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
