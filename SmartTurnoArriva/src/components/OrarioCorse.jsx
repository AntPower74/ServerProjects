import React, { useState, useMemo, useRef } from 'react';
import { Clock, Search, X, Bus, ChevronDown, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import orarioCorseData from '../data/orario_corse_data.json';
import databaseOrari from '../data/database_orari.json';
import turniCorseData from '../data/turni_corse_db.json';

// Linee disponibili con descrizione e capolinea
const AVAILABLE_LINES = [
  { id: '268', code: '268', name: 'Linea 268', route: 'Torino ↔ Caselle Aeroporto', count: 144 },
  { id: '275/282', code: '275/282', name: 'Linea 275/282', route: 'Torino ↔ Pinerolo ↔ Perosa ↔ Sestriere ↔ Oulx', count: 156 },
  { id: '901', code: '901', name: 'Linea 901', route: 'Avigliana ↔ Giaveno ↔ Coazze', count: 115 },
  { id: '285', code: '285', name: 'Linea 285', route: 'Pinerolo ↔ Luserna ↔ Torre Pellice ↔ Bobbio', count: 111 },
  { id: '267', code: '267', name: 'Linea 267', route: 'Torino ↔ Orbassano ↔ Piossasco', count: 107 },
  { id: '265', code: '265', name: 'Linea 265', route: 'Torino ↔ Rivoli ↔ Giaveno', count: 75 },
  { id: '283', code: '283', name: 'Linea 283', route: 'Pinerolo ↔ Cavour ↔ Saluzzo', count: 55 },
  { id: '303', code: '303', name: 'Linea 303', route: 'Pinerolo ↔ Frossasco ↔ Cumiana', count: 55 },
  { id: '278', code: '278', name: 'Linea 278', route: 'Pinerolo ↔ Luserna ↔ Rorà', count: 40 },
  { id: '274', code: '274', name: 'Linea 274', route: 'Pinerolo ↔ Roletto ↔ Cantalupa', count: 33 },
  { id: '20 (Malpensa Express)', code: '20', name: 'Linea 20 Malpensa', route: 'Torino ↔ Milano Malpensa', count: 30 },
  { id: '101 (Torino - Aosta / SAVDA)', code: '101', name: 'Linea 101 SAVDA', route: 'Torino ↔ Ivrea ↔ Aosta', count: 14 },
  { id: 'SAVDA (Aosta ↔ Milano Malpensa)', code: 'SAVDA-MXP', name: 'SAVDA Aosta ↔ Malpensa', route: 'Aosta ↔ Châtillon ↔ Verrès ↔ Pont ↔ Malpensa', count: 5 },
  { id: 'SAVDA (Milano Malpensa ↔ Aosta)', code: 'SAVDA-AOS', name: 'SAVDA Malpensa ↔ Aosta', route: 'Malpensa ↔ Pont ↔ Verrès ↔ Châtillon ↔ Aosta', count: 5 },
];

// Configurazioni fermate canoniche ordinate per corridoio geografico (Andata)
const CANONICAL_LINE_STOPS = {
  '268': [
    { key: 'to_pn', full: 'Torino Porta Nuova', short: 'TO - Porta Nuova', patterns: ['PORTA NUOVA'] },
    { key: 'to_ps', full: 'Torino Porta Susa', short: 'TO - Porta Susa', patterns: ['PORTA SUSA'] },
    { key: 'to_umb', full: 'Torino Umbria/Livorno', short: 'TO - Umbria/Liv.', patterns: ['UMBRIA', 'LIVORNO'] },
    { key: 'to_stra', full: 'Torino Stradella', short: 'TO - Stradella', patterns: ['STRADELLA'] },
    { key: 'to_ver', full: 'Torino Veronese', short: 'TO - Veronese', patterns: ['VERONESE'] },
    { key: 'borgaro', full: 'Borgaro Torinese', short: 'Borgaro T.se', patterns: ['BORGARO'] },
    { key: 'caselle_vt', full: 'Caselle Via Torino', short: 'Caselle V. Torino', patterns: ['VIA TORINO', 'CASELLE V. TORINO'] },
    { key: 'caselle_sa', full: 'Caselle Strada Aeroporto', short: 'Caselle Str. Aeroporto', patterns: ['STRADA AEROPORTO', 'STR. AEROPORTO'] },
    { key: 'caselle_aero', full: 'Caselle Aeroporto', short: 'Caselle Aeroporto', patterns: ['AEROPORTO', 'CASELLE AEROPORTO'] }
  ],
  '275/282': [
    { key: 'to_ps', full: 'Torino Porta Susa', short: 'TO - Porta Susa', patterns: ['PORTA SUSA'] },
    { key: 'to_pn', full: 'Torino Porta Nuova', short: 'TO - Porta Nuova', patterns: ['PORTA NUOVA'] },
    { key: 'to_vinz', full: 'Torino C.so Vinzaglio', short: 'TO - Vinzaglio', patterns: ['VINZAGLIO'] },
    { key: 'to_maur', full: 'Torino Mauriziano', short: 'TO - Mauriziano', patterns: ['MAURIZIANO', 'TURATI'] },
    { key: 'to_seba', full: 'Torino Sebastopoli', short: 'TO - Sebastopoli', patterns: ['SEBASTOPOLI'] },
    { key: 'to_poveri', full: 'Torino Poveri Vecchi', short: 'TO - Poveri Vecchi', patterns: ['POVERI VECCHI'] },
    { key: 'to_cosenza', full: 'Torino C.so Cosenza', short: 'TO - Cosenza', patterns: ['COSENZA'] },
    { key: 'to_caio', full: 'Torino Caio Mario', short: 'TO - Caio Mario', patterns: ['CAIO MARIO'] },
    { key: 'to_drosso', full: 'Torino Strada Drosso', short: 'TO - Drosso', patterns: ['DROSSO'] },
    { key: 'stupinigi', full: 'Stupinigi (Palazzina/Ippodromo)', short: 'Stupinigi', patterns: ['STUPINIGI', 'IPPODROMO', 'PALAZZINA'] },
    { key: 'candiolo', full: 'Candiolo IRCCS / Bivio', short: 'Candiolo IRCCS', patterns: ['CANDIOLO', 'IRCCS', 'RICERCHE'] },
    { key: 'none', full: 'None (Bivio / Fornaci)', short: 'None Bivio', patterns: ['NONE -', 'NONE BIVIO', 'FORNACI'] },
    { key: 'volvera', full: 'Volvera Gerbole', short: 'Volvera Gerbole', patterns: ['VOLVERA', 'GERBOLE'] },
    { key: 'airasca', full: 'Airasca (Centro / SKF)', short: 'Airasca', patterns: ['AIRASCA', 'SKF'] },
    { key: 'piscina', full: 'Piscina (Baudi / Botteghe)', short: 'Piscina', patterns: ['PISCINA', 'BAUDI', 'BOTTEGHE', 'BSBORDANO', 'BAUDE'] },
    { key: 'riva', full: 'Riva di Pinerolo', short: 'Riva di Pin.', patterns: ['RIVA DI PINEROLO', 'RIVA -', 'RIVA '] },
    { key: 'pinerolo', full: 'Pinerolo - Movicentro', short: 'Pinerolo-Movicentro', patterns: ['PINEROLO -', 'PIN. -', 'PINEROLO CENTRO', 'PINEROLO CAVOUR', 'PINEROLO MOV', 'MACUMBA', 'MOVICENTRO', 'CENTRO STUDI'], excludes: ['RIVA DI PINEROLO', 'SAN SECONDO DI PINEROLO'] },
    { key: 'abbadia', full: 'Abbadia Alpina', short: 'Abbadia Alp.', patterns: ['ABBADIA', 'PONTE LEMINA', 'S. MARTINO'] },
    { key: 'porte', full: 'Porte', short: 'Porte', patterns: ['PORTE'] },
    { key: 's_germano', full: 'San Germano Chisone', short: 'S. Germano Ch.', patterns: ['S. GERMANO', 'SAN GERMANO'] },
    { key: 'villar', full: 'Villar Perosa / Dubbione', short: 'Villar Perosa', patterns: ['VILLAR PEROSA', 'V. PEROSA', 'DUBBIONE'] },
    { key: 'pinasca', full: 'Pinasca', short: 'Pinasca', patterns: ['PINASCA'] },
    { key: 'pomaretto', full: 'Pomaretto (Bivio Ospedale)', short: 'Pomaretto', patterns: ['POMARETTO'] },
    { key: 'perosa', full: 'Perosa Argentina (P.za 3° Alpini)', short: 'Perosa Arg.', patterns: ['PEROSA ARG', 'TERZO ALPINI', 'RG.-PZZA', 'PEROSA -', 'PEROSA ('], excludes: ['VILLAR PEROSA', 'V. PEROSA'] },
    { key: 'castel_bosco', full: 'Castel del Bosco', short: 'Castel d. Bosco', patterns: ['CASTEL DEL BOSCO'] },
    { key: 'roure', full: 'Roure / Roreto / Balma', short: 'Roure / Balma', patterns: ['ROURE', 'RORETO', 'BALMA'] },
    { key: 'mentoulles', full: 'Mentoulles / Villaretto', short: 'Mentoulles', patterns: ['MENTOULLES', 'VILLARETTO'] },
    { key: 'fenestrelle', full: 'Fenestrelle', short: 'Fenestrelle', patterns: ['FENESTRELLE'] },
    { key: 'usseaux', full: 'Usseaux / Pourrieres', short: 'Usseaux Bivio', patterns: ['USSEAUX', 'POURRIERES'] },
    { key: 'pragelato', full: 'Pragelato (Plan / Traverses)', short: 'Pragelato', patterns: ['PRAGELATO', 'PLAN', 'TRAVERSES'] },
    { key: 'sestriere', full: 'Sestriere / Borgata', short: 'Sestriere', patterns: ['SESTRIERE', 'BORGATA'] },
    { key: 'cesana', full: 'Cesana Torinese', short: 'Cesana T.se', patterns: ['CESANA'] },
    { key: 'oulx', full: 'Oulx (Stazione FS / Garambois)', short: 'Oulx FS', patterns: ['OULX'] }
  ],
  '901': [
    { key: 'avig_fs', full: 'Avigliana Stazione FS', short: 'Avigliana FS', patterns: ['AVIGLIANA', 'STAZIONE FS'] },
    { key: 'avig_laghi', full: 'Avigliana Laghi / Centro', short: 'Avigliana Laghi', patterns: ['LAGHI', 'CENTRO'] },
    { key: 'trana', full: 'Trana', short: 'Trana', patterns: ['TRANA'] },
    { key: 'giaveno_auto', full: 'Giaveno Autostazione', short: 'Giaveno Auto.', patterns: ['GIAVENO', 'AUTOSTAZIONE'] },
    { key: 'giaveno_sm', full: 'Giaveno S. Martino', short: 'Giaveno S.Martino', patterns: ['MARTINO'] },
    { key: 'coazze_cen', full: 'Coazze Centro', short: 'Coazze Centro', patterns: ['COAZZE', 'PIAZZA'] },
    { key: 'coazze_forno', full: 'Coazze Forno / Sangonetto', short: 'Coazze Forno', patterns: ['FORNO', 'SANGONETTO'] }
  ],
  '285': [
    { key: 'pin_fs', full: 'Pinerolo - Movicentro / Cavour', short: 'Pinerolo-Movicentro', patterns: ['PINEROLO -', 'PINEROLO CAVOUR', 'PINEROLO MOV', 'MOVICENTRO'], excludes: ['RIVA DI PINEROLO'] },
    { key: 'riva_pin', full: 'Riva di Pinerolo', short: 'Riva di Pin.', patterns: ['RIVA'] },
    { key: 'bricherasio', full: 'Bricherasio', short: 'Bricherasio', patterns: ['BRICHERASIO', 'MORERI'] },
    { key: 'bibiana', full: 'Bibiana', short: 'Bibiana', patterns: ['BIBIANA'] },
    { key: 'luserna_part', full: 'Luserna p.zza Partigiani', short: 'Luserna Partigiani', patterns: ['LUSERNA', 'PARTIGIANI'] },
    { key: 'torre_pellice', full: 'Torre Pellice', short: 'Torre Pellice', patterns: ['TORRE PELLICE'] },
    { key: 'villar_pellice', full: 'Villar Pellice', short: 'Villar Pellice', patterns: ['VILLAR PELLICE'] },
    { key: 'bobbio_pellice', full: 'Bobbio Pellice', short: 'Bobbio Pellice', patterns: ['BOBBIO'] }
  ],
  '267': [
    { key: 'to_pn', full: 'Torino Porta Nuova', short: 'TO - Porta Nuova', patterns: ['PORTA NUOVA'] },
    { key: 'to_caio', full: 'Torino Caio Mario', short: 'TO - Caio Mario', patterns: ['CAIO MARIO'] },
    { key: 'to_drosso', full: 'Torino Strada Drosso', short: 'TO - Drosso', patterns: ['DROSSO'] },
    { key: 'beinasco', full: 'Beinasco', short: 'Beinasco', patterns: ['BEINASCO', 'FORNACI'] },
    { key: 'orbassano', full: 'Orbassano Centro', short: 'Orbassano', patterns: ['ORBASSANO'] },
    { key: 'volvera_biv', full: 'Volvera Bivio', short: 'Volvera', patterns: ['VOLVERA'] },
    { key: 'piossasco', full: 'Piossasco', short: 'Piossasco', patterns: ['PIOSSASCO'] }
  ],
  '265': [
    { key: 'to_pn', full: 'Torino Porta Nuova', short: 'TO - Porta Nuova', patterns: ['PORTA NUOVA'] },
    { key: 'to_ps', full: 'Torino Porta Susa', short: 'TO - Porta Susa', patterns: ['PORTA SUSA'] },
    { key: 'rivoli', full: 'Rivoli', short: 'Rivoli', patterns: ['RIVOLI', 'CASCINE'] },
    { key: 'rosta', full: 'Rosta', short: 'Rosta', patterns: ['ROSTA'] },
    { key: 'buttigliera', full: 'Buttigliera Alta', short: 'Buttigliera', patterns: ['BUTTIGLIERA'] },
    { key: 'trana', full: 'Trana', short: 'Trana', patterns: ['TRANA'] },
    { key: 'giaveno', full: 'Giaveno', short: 'Giaveno', patterns: ['GIAVENO'] }
  ],
  '283': [
    { key: 'pin_fs', full: 'Pinerolo - Movicentro / Cavour', short: 'Pinerolo-Movicentro', patterns: ['PINEROLO -', 'PINEROLO CAVOUR', 'PINEROLO MOV', 'MOVICENTRO'], excludes: ['RIVA DI PINEROLO'] },
    { key: 'osasco', full: 'Osasco', short: 'Osasco', patterns: ['OSASCO'] },
    { key: 'garzigliana', full: 'Garzigliana', short: 'Garzigliana', patterns: ['GARZIGLIANA'] },
    { key: 'cavour', full: 'Cavour', short: 'Cavour', patterns: ['CAVOUR'] },
    { key: 'campiglione', full: 'Campiglione Fenile', short: 'Campiglione', patterns: ['CAMPIGLIONE'] },
    { key: 'saluzzo', full: 'Saluzzo', short: 'Saluzzo', patterns: ['SALUZZO'] }
  ],
  '303': [
    { key: 'pin_fs', full: 'Pinerolo - Movicentro / Cavour', short: 'Pinerolo-Movicentro', patterns: ['PINEROLO -', 'PINEROLO CAVOUR', 'PINEROLO MOV', 'MOVICENTRO'], excludes: ['RIVA DI PINEROLO'] },
    { key: 'piscina', full: 'Piscina', short: 'Piscina', patterns: ['PISCINA'] },
    { key: 'frossasco', full: 'Frossasco', short: 'Frossasco', patterns: ['FROSSASCO'] },
    { key: 'cumiana_biv', full: 'Cumiana Bivio', short: 'Cumiana Bivio', patterns: ['BIVIO CUMIANA'] },
    { key: 'cumiana_cen', full: 'Cumiana Centro', short: 'Cumiana Centro', patterns: ['CUMIANA'] },
    { key: 'cumiana_tav', full: 'Cumiana Tavernette', short: 'Cumiana Tavernette', patterns: ['TAVERNETTE'] }
  ],
  '278': [
    { key: 'pin_fs', full: 'Pinerolo - Movicentro', short: 'Pinerolo-Movicentro', patterns: ['PINEROLO -', 'PINEROLO CAVOUR', 'MOVICENTRO'], excludes: ['RIVA DI PINEROLO', 'SAN SECONDO DI PINEROLO'] },
    { key: 's_secondo', full: 'San Secondo di Pinerolo', short: 'San Secondo', patterns: ['SAN SECONDO'] },
    { key: 'bricherasio', full: 'Bricherasio', short: 'Bricherasio', patterns: ['BRICHERASIO'] },
    { key: 'luserna', full: 'Luserna San Giovanni', short: 'Luserna', patterns: ['LUSERNA'] },
    { key: 'rora', full: 'Rorà', short: 'Rorà', patterns: ['RORA', 'RORÀ'] }
  ],
  '274': [
    { key: 'pin_fs', full: 'Pinerolo - Movicentro', short: 'Pinerolo-Movicentro', patterns: ['PINEROLO -', 'PINEROLO CAVOUR', 'MOVICENTRO'], excludes: ['RIVA DI PINEROLO'] },
    { key: 'roletto', full: 'Roletto', short: 'Roletto', patterns: ['ROLETTO'] },
    { key: 'frossasco', full: 'Frossasco', short: 'Frossasco', patterns: ['FROSSASCO'] },
    { key: 'cantalupa', full: 'Cantalupa', short: 'Cantalupa', patterns: ['CANTALUPA'] }
  ],
  '20 (Malpensa Express)': [
    { key: 'to_ps', full: 'Torino Porta Susa', short: 'TO - Porta Susa', patterns: ['PORTA SUSA'] },
    { key: 'chivasso', full: 'Chivasso Centro', short: 'Chivasso', patterns: ['CHIVASSO'] },
    { key: 'santhia', full: 'Santhià', short: 'Santhià', patterns: ['SANTHIA', 'SANTHIÀ'] },
    { key: 'novara', full: 'Novara Centro', short: 'Novara', patterns: ['NOVARA'] },
    { key: 'mxp_t2', full: 'Milano Malpensa Terminal 2', short: 'Malpensa T2', patterns: ['TERMINAL 2', 'T2'] },
    { key: 'mxp_t1', full: 'Milano Malpensa Terminal 1', short: 'Malpensa T1', patterns: ['TERMINAL 1', 'T1', 'MALPENSA'] }
  ],
  '101 (Torino - Aosta / SAVDA)': [
    { key: 'to_pn', full: 'Torino Porta Nuova', short: 'TO - Porta Nuova', patterns: ['PORTA NUOVA'] },
    { key: 'to_ps', full: 'Torino Porta Susa', short: 'TO - Porta Susa', patterns: ['PORTA SUSA'] },
    { key: 'ivrea', full: 'Ivrea Autostazione', short: 'Ivrea', patterns: ['IVREA'] },
    { key: 'pont', full: 'Pont-Saint-Martin', short: 'Pont-St-Martin', patterns: ['PONT'] },
    { key: 'verres', full: 'Verrès', short: 'Verrès', patterns: ['VERRES', 'VERRÈS'] },
    { key: 'chatillon', full: 'Châtillon - Saint-Vincent', short: 'Châtillon', patterns: ['CHATILLON', 'CHÂTILLON', 'SAINT-VINCENT'] },
    { key: 'aosta', full: 'Aosta Autostazione', short: 'Aosta', patterns: ['AOSTA'] }
  ],
  'SAVDA (Aosta ↔ Milano Malpensa)': [
    { key: 'aosta', full: 'Aosta Autostazione', short: 'Aosta', patterns: ['AOSTA'] },
    { key: 'chatillon', full: 'Châtillon - Saint-Vincent', short: 'Châtillon', patterns: ['CHATILLON', 'CHÂTILLON'] },
    { key: 'verres', full: 'Verrès', short: 'Verrès', patterns: ['VERRES', 'VERRÈS'] },
    { key: 'pont', full: 'Pont-Saint-Martin', short: 'Pont-St-Martin', patterns: ['PONT'] },
    { key: 'mxp_t1', full: 'Milano Malpensa Terminal 1', short: 'Malpensa T1', patterns: ['TERMINAL 1', 'T1', 'OVEST'] },
    { key: 'mxp_t2', full: 'Milano Malpensa Terminal 2', short: 'Malpensa T2', patterns: ['TERMINAL 2', 'T2', 'NORD'] }
  ],
  'SAVDA (Milano Malpensa ↔ Aosta)': [
    { key: 'mxp_t1', full: 'Milano Malpensa Terminal 1', short: 'Malpensa T1', patterns: ['TERMINAL 1', 'T1', 'OVEST'] },
    { key: 'mxp_t2', full: 'Milano Malpensa Terminal 2', short: 'Malpensa T2', patterns: ['TERMINAL 2', 'T2', 'NORD'] },
    { key: 'pont', full: 'Pont-Saint-Martin', short: 'Pont-St-Martin', patterns: ['PONT'] },
    { key: 'verres', full: 'Verrès', short: 'Verrès', patterns: ['VERRES', 'VERRÈS'] },
    { key: 'chatillon', full: 'Châtillon - Saint-Vincent', short: 'Châtillon', patterns: ['CHATILLON', 'CHÂTILLON'] },
    { key: 'aosta', full: 'Aosta Autostazione', short: 'Aosta', patterns: ['AOSTA'] }
  ]
};

// Helper per ripulire e formattare orari HH:MM
const cleanTime = (t) => {
  if (!t || t === '—' || t === '-') return '';
  t = String(t).trim().replace('.', ':');
  const parts = t.split(':');
  if (parts.length === 2) {
    const h = parseInt(parts[0], 10);
    const m = parseInt(parts[1], 10);
    if (!isNaN(h) && !isNaN(m)) {
      return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`;
    }
  }
  return t;
};

// Helper per pulire orari da mostrare nelle celle (rimuove annotazioni come S, F, A)
const cleanDisplayTime = (val) => {
  if (!val || val === '—' || val === '-') return '—';
  const v = String(val).trim();
  if (/^[A-Za-z]$/.test(v)) return '—';
  return v;
};

// Trova codice turno autista per una corsa
const resolveTurnoForTrip = (trip) => {
  if (trip.turno && trip.turno !== '—') return trip.turno;
  if (!turniCorseData || turniCorseData.length === 0) return '—';
  
  const stops = trip.stops || [];
  if (stops.length === 0) return '—';
  
  const tripDep = cleanTime(stops[0].time);
  const tripArr = cleanTime(stops[stops.length - 1].time);
  const tripLine = String(trip.line || '');

  for (const t of turniCorseData) {
    if (!t.corse || t.corse.length === 0) continue;
    for (const c of t.corse) {
      const cLine = String(c.linea || '');
      const matchLine = !cLine || !tripLine || cLine.includes(tripLine) || tripLine.includes(cLine) || tripLine.split('/')[0] === cLine;
      if (!matchLine) continue;

      const cDep = cleanTime(c.partenza);
      const cArr = cleanTime(c.arrivo);

      if (tripDep && cDep && tripDep === cDep) return t.codice;
      if (tripArr && cArr && tripArr === cArr) return t.codice;
    }
  }
  return '—';
};

const OrarioCorse = () => {
  const [selectedLineId, setSelectedLineId] = useState('268');
  const [searchTerm, setSearchTerm] = useState('');
  const [directionFilter, setDirectionFilter] = useState('all'); // 'all' | 'outbound' | 'inbound'
  const tableContainerRef = useRef(null);

  const scrollTable = (offset) => {
    if (tableContainerRef.current) {
      tableContainerRef.current.scrollBy({ left: offset, behavior: 'smooth' });
    }
  };

  const scrollToPosition = (position) => {
    if (tableContainerRef.current) {
      tableContainerRef.current.scrollTo({ left: position === 'start' ? 0 : 99999, behavior: 'smooth' });
    }
  };

  const currentLineInfo = useMemo(() => {
    return AVAILABLE_LINES.find(l => l.id === selectedLineId) || {
      id: selectedLineId,
      name: `Linea ${selectedLineId}`,
      route: '',
      count: 0
    };
  }, [selectedLineId]);

  // Dati calcolati per la linea selezionata
  const { headers, rows } = useMemo(() => {
    // 1. Caso speciale Linea 268 (dataset manuale 144 corse)
    if (selectedLineId === '268') {
      const isReturnRow268 = (idx) => idx >= 66;
      let list = orarioCorseData.map((row, idx) => {
        const isReturn = isReturnRow268(idx);
        const cells = (isReturn && directionFilter === 'inbound') 
          ? [...row.slice(1, 10)].reverse() 
          : row.slice(1, 10);

        return {
          turno: (row[0] || '').trim(),
          isReturn,
          cells,
          originalIndex: idx,
          rawSearch: row.join(' ')
        };
      });

      if (directionFilter === 'outbound') list = list.filter(r => !r.isReturn);
      if (directionFilter === 'inbound') list = list.filter(r => r.isReturn);

      if (searchTerm.trim()) {
        const q = searchTerm.trim().toLowerCase();
        list = list.filter(r => r.rawSearch.toLowerCase().includes(q));
      }

      const headers268 = directionFilter === 'inbound'
        ? [...CANONICAL_LINE_STOPS['268']].reverse()
        : [...CANONICAL_LINE_STOPS['268']];

      return {
        headers: [
          { full: 'TURNO', short: 'TURNO', isTurno: true },
          ...headers268
        ],
        rows: list
      };
    }

    // 2. Tutte le altre linee da database_orari.json con mapping canonico ordinato
    const allTrips = (databaseOrari.trips || []).filter(t => t.line === selectedLineId);
    const lineConfig = CANONICAL_LINE_STOPS[selectedLineId] || [];

    // Classifica andata / ritorno per ogni corsa
    const classifiedTrips = allTrips.map((trip, idx) => {
      const stops = trip.stops || [];
      const firstStop = (stops[0]?.name || '').toUpperCase();
      const lastStop = (stops[stops.length - 1]?.name || '').toUpperCase();

      let isReturn = false;
      if (lastStop.includes('TORINO') || lastStop.includes('AVIGLIANA') || lastStop.includes('CHIVASSO') || lastStop.includes('PINEROLO')) {
        isReturn = true;
      } else if (firstStop.includes('TORINO') || firstStop.includes('AVIGLIANA') || firstStop.includes('CHIVASSO')) {
        isReturn = false;
      } else if (firstStop.includes('SESTRIERE') || firstStop.includes('PEROSA') || firstStop.includes('BOBBIO') || firstStop.includes('COAZZE') || firstStop.includes('AOSTA')) {
        isReturn = true;
      }

      const turno = resolveTurnoForTrip(trip);

      return {
        trip,
        turno,
        isReturn,
        stops,
        originalIndex: idx
      };
    });

    // Filtra per direzione
    let filteredTrips = classifiedTrips;
    if (directionFilter === 'outbound') filteredTrips = filteredTrips.filter(t => !t.isReturn);
    if (directionFilter === 'inbound') filteredTrips = filteredTrips.filter(t => t.isReturn);

    // Filtra per ricerca testo
    if (searchTerm.trim()) {
      const q = searchTerm.trim().toLowerCase();
      filteredTrips = filteredTrips.filter(t => {
        if (t.turno.toLowerCase().includes(q)) return true;
        return t.stops.some(s => s.name.toLowerCase().includes(q) || s.time.includes(q));
      });
    }

    // Se abbiamo configurazione fermate canoniche:
    let dynamicStopColumns = [];
    if (lineConfig.length > 0) {
      // Ordina fermate: se Ritorno, inverti la sequenza per seguire la direzione di marcia
      dynamicStopColumns = directionFilter === 'inbound' 
        ? [...lineConfig].reverse() 
        : [...lineConfig];
    } else {
      // Fallback dinamico pulito
      const seen = new Set();
      filteredTrips.forEach(t => {
        t.stops.forEach(s => {
          const rawName = s.name.trim();
          if (!seen.has(rawName)) {
            seen.add(rawName);
            dynamicStopColumns.push({
              key: rawName,
              full: rawName,
              short: rawName.length > 18 ? rawName.slice(0, 16) + '..' : rawName,
              patterns: [rawName.toUpperCase()]
            });
          }
        });
      });
    }

    const finalHeaders = [
      { full: 'TURNO', short: 'TURNO', isTurno: true },
      ...dynamicStopColumns
    ];

    // Crea le righe a matrice con matching intelligente
    const dynamicRows = filteredTrips.map(t => {
      const cells = dynamicStopColumns.map(col => {
        // Cerca nella corsa una fermata che corrisponde ai pattern della colonna (rispettando gli excludes)
        let matchedTime = '—';
        const excludes = col.excludes || [];

        for (const stop of t.stops) {
          const stopUpper = stop.name.toUpperCase();
          const isExcluded = excludes.some(ex => stopUpper.includes(ex));
          if (isExcluded) continue;

          const isMatch = col.patterns.some(p => stopUpper.includes(p));
          if (isMatch) {
            matchedTime = stop.time;
            break;
          }
        }
        return matchedTime;
      });

      return {
        turno: t.turno,
        isReturn: t.isReturn,
        cells,
        originalIndex: t.originalIndex,
        rawSearch: ''
      };
    });

    return {
      headers: finalHeaders,
      rows: dynamicRows
    };
  }, [selectedLineId, directionFilter, searchTerm]);

  // Verifica se un header corrisponde al termine di ricerca o è selezionato
  const isHeaderMatched = (header) => {
    if (!searchTerm.trim() || header.isTurno) return false;
    const q = searchTerm.trim().toLowerCase();
    const fullMatch = header.full && header.full.toLowerCase().includes(q);
    const shortMatch = header.short && header.short.toLowerCase().includes(q);
    const patternMatch = header.patterns && header.patterns.some(p => p.toLowerCase().includes(q));
    return fullMatch || shortMatch || patternMatch;
  };

  return (
    <div style={{
      padding: '0.75rem 0.5rem',
      background: 'var(--bg-app)',
      minHeight: '100vh',
      paddingBottom: '90px',
      width: '100%',
      minWidth: 0,
      boxSizing: 'border-box',
      overflowX: 'hidden'
    }}>
      {/* Intestazione Titolo con Selettore Linea */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '0.4rem',
        marginBottom: '0.75rem',
        padding: '0 0.25rem'
      }}>
        <div>
          <h2 style={{
            fontSize: '1.1rem',
            fontWeight: 'bold',
            color: 'var(--text-main)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            margin: 0
          }}>
            <Clock size={18} style={{ color: 'var(--accent-orange)' }} />
            <span>Orario Corse ({currentLineInfo.name})</span>
          </h2>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: '2px 0 0 0' }}>
            {currentLineInfo.route || 'Quadro orario con codici turno'}
          </p>
        </div>

        {/* Dropdown rapido scelta linea */}
        <div style={{ position: 'relative' }}>
          <select
            value={selectedLineId}
            onChange={(e) => setSelectedLineId(e.target.value)}
            style={{
              background: 'var(--bg-card)',
              color: 'var(--accent-cyan)',
              border: '1.5px solid var(--accent-cyan)',
              borderRadius: '8px',
              padding: '6px 28px 6px 10px',
              fontSize: '0.8rem',
              fontWeight: '700',
              cursor: 'pointer',
              outline: 'none',
              appearance: 'none'
            }}
          >
            {AVAILABLE_LINES.map(line => (
              <option key={line.id} value={line.id}>
                {line.name} ({line.route})
              </option>
            ))}
          </select>
          <ChevronDown size={14} style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', color: 'var(--accent-cyan)' }} />
        </div>
      </div>

      {/* Selettore Linee a Pills Orizzontali */}
      <div style={{
        display: 'flex',
        gap: '6px',
        overflowX: 'auto',
        paddingBottom: '6px',
        marginBottom: '0.75rem',
        WebkitOverflowScrolling: 'touch'
      }}>
        {AVAILABLE_LINES.map(line => {
          const isSelected = selectedLineId === line.id;
          return (
            <button
              key={line.id}
              type="button"
              onClick={() => setSelectedLineId(line.id)}
              style={{
                padding: '5px 10px',
                borderRadius: '8px',
                border: isSelected ? '1.5px solid var(--accent-orange)' : '1px solid var(--border-color)',
                background: isSelected ? 'rgba(245, 166, 35, 0.2)' : 'var(--bg-card)',
                color: isSelected ? 'var(--accent-orange)' : 'var(--text-main)',
                fontWeight: isSelected ? '800' : '600',
                fontSize: '0.75rem',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '5px',
                transition: 'all 0.15s'
              }}
            >
              <Bus size={12} />
              <span>{line.name}</span>
            </button>
          );
        })}
      </div>

      {/* Barra Filtri: Direzione & Ricerca */}
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '10px',
        padding: '0.6rem 0.75rem',
        marginBottom: '0.75rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '0.4rem'
        }}>
          {/* Selettore Direzione Compatto */}
          <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
            <button
              type="button"
              onClick={() => setDirectionFilter('all')}
              style={{
                padding: '4px 9px',
                borderRadius: '6px',
                border: directionFilter === 'all' ? '1px solid var(--accent-orange)' : '1px solid var(--border-color)',
                background: directionFilter === 'all' ? 'var(--accent-orange)' : 'rgba(255,255,255,0.03)',
                color: directionFilter === 'all' ? '#121214' : 'var(--text-main)',
                fontWeight: directionFilter === 'all' ? '700' : '500',
                fontSize: '0.75rem',
                cursor: 'pointer',
                transition: 'all 0.15s'
              }}
            >
              Tutte ({rows.length})
            </button>

            <button
              type="button"
              onClick={() => setDirectionFilter('outbound')}
              style={{
                padding: '4px 9px',
                borderRadius: '6px',
                border: directionFilter === 'outbound' ? '1px solid var(--accent-cyan)' : '1px solid var(--border-color)',
                background: directionFilter === 'outbound' ? 'rgba(8, 145, 178, 0.25)' : 'rgba(255,255,255,0.03)',
                color: directionFilter === 'outbound' ? 'var(--accent-cyan)' : 'var(--text-main)',
                fontWeight: directionFilter === 'outbound' ? '700' : '500',
                fontSize: '0.75rem',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '3px',
                transition: 'all 0.15s'
              }}
            >
              <span>Andata ➔</span>
            </button>

            <button
              type="button"
              onClick={() => setDirectionFilter('inbound')}
              style={{
                padding: '4px 9px',
                borderRadius: '6px',
                border: directionFilter === 'inbound' ? '1px solid #10b981' : '1px solid var(--border-color)',
                background: directionFilter === 'inbound' ? 'rgba(16, 185, 129, 0.25)' : 'rgba(255,255,255,0.03)',
                color: directionFilter === 'inbound' ? '#10b981' : 'var(--text-main)',
                fontWeight: directionFilter === 'inbound' ? '700' : '500',
                fontSize: '0.75rem',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '3px',
                transition: 'all 0.15s'
              }}
            >
              <span>⬅ Ritorno</span>
            </button>
          </div>

          {/* Ricerca Rapida Turno / Orario */}
          <div style={{ position: 'relative', minWidth: '170px', flex: '1 1 170px' }}>
            <Search size={13} style={{ position: 'absolute', left: '8px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Cerca fermata (es. Perosa, Caio Mario) o turno..."
              style={{
                width: '100%',
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid var(--border-color)',
                borderRadius: '6px',
                padding: '5px 8px 5px 26px',
                color: 'var(--text-main)',
                fontSize: '0.75rem',
                outline: 'none'
              }}
            />
            {searchTerm && (
              <X
                size={12}
                onClick={() => setSearchTerm('')}
                style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', cursor: 'pointer' }}
              />
            )}
          </div>
        </div>

        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
          Mostrate <strong>{rows.length}</strong> corse su {currentLineInfo.name}
          {searchTerm.trim() && (
            <span style={{ marginLeft: '6px', color: 'var(--accent-orange)', fontWeight: '700' }}>
              • Evidenziazione colonna attiva
            </span>
          )}
        </div>
      </div>

      {/* Barra di Navigazione Rapida Orizzontale */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(245, 166, 35, 0.08)',
        border: '1px solid rgba(245, 166, 35, 0.25)',
        borderRadius: '8px',
        padding: '5px 8px',
        marginBottom: '0.6rem',
        gap: '6px',
        flexWrap: 'wrap'
      }}>
        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span>↔️ <strong style={{ color: 'var(--accent-orange)' }}>Scorri Fermate:</strong></span>
          <span style={{ fontSize: '0.66rem', color: 'rgba(255,255,255,0.5)' }}>(o trascina a destra/sinistra)</span>
        </div>

        <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
          <button
            type="button"
            onClick={() => scrollToPosition('start')}
            title="Vai a Inizio / Partenza"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              padding: '3px 7px',
              color: 'var(--accent-orange)',
              fontSize: '0.7rem',
              fontWeight: '700',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '2px'
            }}
          >
            <ChevronsLeft size={13} />
            <span>Inizio</span>
          </button>

          <button
            type="button"
            onClick={() => scrollTable(-200)}
            title="Scorri Sinistra"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              padding: '3px 8px',
              color: 'var(--text-main)',
              fontSize: '0.7rem',
              fontWeight: '700',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '2px'
            }}
          >
            <ChevronLeft size={13} />
            <span>SX</span>
          </button>

          <button
            type="button"
            onClick={() => scrollTable(200)}
            title="Scorri Destra"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              padding: '3px 8px',
              color: 'var(--text-main)',
              fontSize: '0.7rem',
              fontWeight: '700',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '2px'
            }}
          >
            <span>DX</span>
            <ChevronRight size={13} />
          </button>

          <button
            type="button"
            onClick={() => scrollToPosition('end')}
            title="Vai a Fine / Capolinea"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              padding: '3px 7px',
              color: 'var(--accent-cyan)',
              fontSize: '0.7rem',
              fontWeight: '700',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '2px'
            }}
          >
            <span>Capolinea</span>
            <ChevronsRight size={13} />
          </button>
        </div>
      </div>

      {/* Tabella Quadro Orario a Griglia Chiara con Spaziatura Ottimale */}
      <div style={{
        borderRadius: '8px',
        border: '1.5px solid rgba(255, 255, 255, 0.18)',
        overflow: 'hidden',
        background: 'var(--bg-card)',
        maxWidth: '100%',
        boxShadow: '0 4px 20px rgba(0,0,0,0.45)'
      }}>
        <div
          ref={tableContainerRef}
          style={{
            overflowX: 'auto',
            maxHeight: 'calc(100vh - 300px)',
            overflowY: 'auto',
            maxWidth: '100%',
            WebkitOverflowScrolling: 'touch',
            scrollbarWidth: 'thin',
            scrollbarColor: '#f5a623 rgba(255,255,255,0.05)'
          }}
        >
          <table style={{
            width: 'max-content',
            minWidth: '100%',
            borderCollapse: 'collapse',
            fontSize: '0.74rem',
            tableLayout: 'fixed'
          }}>
            <thead>
              <tr style={{
                background: '#131824',
                borderBottom: '2px solid rgba(245, 166, 35, 0.6)',
                position: 'sticky',
                top: 0,
                zIndex: 20
              }}>
                {headers.map((h, i) => {
                  const isTurno = i === 0;
                  const isMatched = isHeaderMatched(h);

                  return (
                    <th
                      key={i}
                      style={{
                        padding: isTurno ? '6px 4px' : '4px 2px',
                        background: isTurno 
                          ? '#131824' 
                          : isMatched 
                            ? 'linear-gradient(180deg, rgba(245, 166, 35, 0.38) 0%, rgba(245, 166, 35, 0.18) 100%)' 
                            : '#131824',
                        color: isTurno 
                          ? 'var(--accent-orange)' 
                          : isMatched 
                            ? '#fbbf24' 
                            : '#cbd5e1',
                        textAlign: 'center',
                        borderBottom: isMatched ? '3px solid #f5a623' : '2px solid rgba(245, 166, 35, 0.6)',
                        borderRight: isTurno ? '2px solid rgba(245, 166, 35, 0.5)' : isMatched ? '2px solid #f5a623' : '1px solid rgba(255,255,255,0.15)',
                        borderLeft: isMatched ? '2px solid #f5a623' : 'none',
                        verticalAlign: 'bottom',
                        width: isTurno ? '56px' : isMatched ? '48px' : '44px',
                        minWidth: isTurno ? '56px' : isMatched ? '48px' : '44px',
                        maxWidth: isTurno ? '60px' : isMatched ? '50px' : '46px',
                        position: isTurno ? 'sticky' : 'static',
                        left: 0,
                        zIndex: isTurno ? 30 : isMatched ? 25 : 20,
                        height: isTurno ? 'auto' : '122px',
                        boxShadow: isMatched ? 'inset 0 0 10px rgba(245, 166, 35, 0.3)' : 'none'
                      }}
                      title={h.full}
                    >
                      <div style={{
                        writingMode: isTurno ? 'horizontal-tb' : 'vertical-rl',
                        transform: isTurno ? 'none' : 'rotate(180deg)',
                        whiteSpace: 'nowrap',
                        fontSize: isTurno ? '0.75rem' : isMatched ? '0.74rem' : '0.68rem',
                        fontWeight: (isTurno || isMatched) ? '900' : '600',
                        letterSpacing: '0.01em',
                        color: isTurno ? 'var(--accent-orange)' : isMatched ? '#fbbf24' : '#e2e8f0',
                        paddingBottom: isTurno ? '4px' : '6px',
                        paddingTop: isTurno ? '0' : '3px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        height: isTurno ? '100%' : '114px',
                        margin: '0 auto',
                        textShadow: isMatched ? '0 0 6px rgba(245, 166, 35, 0.5)' : 'none'
                      }}>
                        {isMatched && <span style={{ fontSize: '0.60rem', marginBottom: '2px' }}>📍</span>}
                        <span>{h.short}</span>
                      </div>
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody>
              {rows.length === 0 ? (
                <tr>
                  <td colSpan={headers.length} style={{ padding: '2rem 1rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    Nessuna corsa trovata con i filtri inseriti per {currentLineInfo.name}.
                  </td>
                </tr>
              ) : (
                rows.map((rowItem, rIdx) => {
                  const turnoCode = (rowItem.turno || '').trim();
                  const hasTurno = turnoCode !== '' && turnoCode !== '—' && turnoCode !== '-';
                  const isEven = rIdx % 2 === 0;
                  const rowBg = isEven ? 'rgba(30, 41, 59, 0.55)' : 'rgba(15, 23, 42, 0.95)';
                  const stickyBg = isEven ? '#1e293b' : '#0f172a';

                  return (
                    <tr
                      key={rIdx}
                      style={{
                        background: rowBg,
                        borderBottom: '1px solid rgba(255,255,255,0.12)',
                        height: '26px',
                        transition: 'background 0.1s'
                      }}
                      onMouseEnter={e => {
                        e.currentTarget.style.background = 'rgba(245, 166, 35, 0.2)';
                        const stickyCell = e.currentTarget.querySelector('td:first-child');
                        if (stickyCell) stickyCell.style.background = '#27272a';
                      }}
                      onMouseLeave={e => {
                        e.currentTarget.style.background = rowBg;
                        const stickyCell = e.currentTarget.querySelector('td:first-child');
                        if (stickyCell) stickyCell.style.background = stickyBg;
                      }}
                    >
                      {/* Colonna TURNO Sticky con Griglia */}
                      <td style={{
                        padding: '2px 4px',
                        textAlign: 'center',
                        position: 'sticky',
                        left: 0,
                        background: stickyBg,
                        zIndex: 5,
                        borderRight: '2px solid rgba(245, 166, 35, 0.4)',
                        borderBottom: '1px solid rgba(255,255,255,0.12)',
                        fontWeight: '800',
                        transition: 'background 0.1s'
                      }}>
                        {hasTurno ? (
                          <span style={{
                            background: rowItem.isReturn ? 'rgba(16, 185, 129, 0.22)' : 'rgba(245, 166, 35, 0.22)',
                            border: rowItem.isReturn ? '1px solid rgba(16, 185, 129, 0.5)' : '1px solid rgba(245, 166, 35, 0.5)',
                            color: rowItem.isReturn ? '#34d399' : 'var(--accent-orange)',
                            padding: '1px 4px',
                            borderRadius: '4px',
                            fontSize: '0.68rem',
                            fontWeight: '800',
                            display: 'inline-block',
                            letterSpacing: '-0.02em',
                            whiteSpace: 'nowrap'
                          }}>
                            {turnoCode}
                          </span>
                        ) : (
                          <span style={{ color: 'rgba(255,255,255,0.25)', fontSize: '0.65rem' }}>
                            {turnoCode || '—'}
                          </span>
                        )}
                      </td>

                      {/* Colonne Fermate a Griglia con Spazio e Contrasto */}
                      {rowItem.cells.map((cellVal, j) => {
                        const val = cleanDisplayTime(cellVal);
                        const isStopValid = val !== '' && val !== '—' && val !== '-';
                        const correspondingHeader = headers[j + 1];
                        const isColMatched = isHeaderMatched(correspondingHeader);

                        return (
                          <td
                            key={j}
                            style={{
                              padding: '2px 4px',
                              textAlign: 'center',
                              background: isColMatched 
                                ? (isStopValid ? 'rgba(245, 166, 35, 0.26)' : 'rgba(245, 166, 35, 0.12)')
                                : 'transparent',
                              borderLeft: isColMatched ? '1.5px solid rgba(245, 166, 35, 0.6)' : 'none',
                              borderRight: isColMatched ? '1.5px solid rgba(245, 166, 35, 0.6)' : '1px solid rgba(255,255,255,0.12)',
                              borderBottom: '1px solid rgba(255,255,255,0.12)',
                              color: isColMatched
                                ? (isStopValid ? '#fbbf24' : 'rgba(251, 191, 36, 0.4)')
                                : isStopValid 
                                  ? (rowItem.isReturn ? '#34d399' : '#38bdf8') 
                                  : 'rgba(255,255,255,0.18)',
                              fontWeight: isColMatched && isStopValid ? '800' : isStopValid ? '700' : '400',
                              fontSize: isColMatched && isStopValid ? '0.74rem' : isStopValid ? '0.72rem' : '0.64rem',
                              fontVariantNumeric: 'tabular-nums',
                              letterSpacing: '0.01em',
                              whiteSpace: 'nowrap',
                              boxShadow: isColMatched && isStopValid ? 'inset 0 0 4px rgba(245, 166, 35, 0.2)' : 'none'
                            }}
                          >
                            {isStopValid ? val : '—'}
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
