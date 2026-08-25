import React, { useState, useEffect, useMemo, useCallback, useRef, useDeferredValue } from 'react';
import { 
  Bell, 
  AlertTriangle, 
  FileText, 
  Smartphone, 
  Download, 
  ExternalLink, 
  Search, 
  RefreshCw, 
  MapPin, 
  Clock, 
  ShieldAlert, 
  Info, 
  Phone, 
  Bus, 
  CheckCircle2, 
  X, 
  ChevronRight, 
  ChevronDown, 
  Plane, 
  Ticket, 
  CreditCard, 
  Bike, 
  Compass, 
  Sparkles, 
  Luggage, 
  ShieldCheck, 
  HelpCircle, 
  Map as MapIcon, 
  FileCheck, 
  AlertCircle,
  ArrowUpDown,
  ArrowRight,
  Navigation,
  Shuffle,
  Tag,
  BookOpen,
  UserCheck,
  Layers,
  Calendar,
  Zap,
  Timer,
  Coffee,
  Truck
} from 'lucide-react';
import { AppLauncher } from '@capacitor/app-launcher';
import { Capacitor } from '@capacitor/core';
import { API_BASE } from '../config.js';
import databaseOrari from '../data/database_orari.json';
import turniCorseDb from '../data/turni_corse_db.json';
import cartelliniDb from '../data/cartellini.json';

const stopNormCache = new globalThis.Map();
function normalizeStop(str) {
  if (!str) return '';
  let res = stopNormCache.get(str);
  if (res !== undefined) return res;
  res = str.toLowerCase().replace(/[,\-–—/().]+/g, ' ').replace(/\s+/g, ' ').trim();
  stopNormCache.set(str, res);
  return res;
}

function matchStop(stopName, query) {
  if (!stopName || !query) return false;
  const s = normalizeStop(stopName);
  const q = normalizeStop(query);

  if (s === q || s.includes(q) || q.includes(s)) return true;

  // 1. Villar Perosa vs Perosa Argentina (crucial: they are separate municipalities!)
  const qHasVillar = q.includes('villar');
  const sHasVillar = s.includes('villar');
  if (qHasVillar !== sHasVillar) return false;
  if (!qHasVillar && (q.includes('perosa') || q.includes('argentina')) && (s.includes('perosa') || s.includes('argentina'))) {
    return true;
  }
  if (qHasVillar && sHasVillar && q.includes('perosa') && s.includes('perosa')) {
    return true;
  }

  // 2. Specific Airport Terminal Matching (do not greedily match local road stops like "str. Aeroporto")
  const isQueryAirportTerminal = (q.includes('aeroporto') || q.includes('airport')) && !q.includes('str') && !q.includes('44') && !q.includes('36');
  if (isQueryAirportTerminal) {
    const isStopAirportTerminal = (s.includes('torino aeroporto') || s.includes('aeroporto caselle')) && !s.includes('str') && !s.includes('44') && !s.includes('36');
    if (isStopAirportTerminal) return true;
    if (s.includes('str aeroporto') || s.includes('via torino')) return false;
  }

  // Specific Street Stop Matching
  if (q.includes('str aeroporto') || q.includes('str aerop')) {
    return s.includes('str aeroporto') || s.includes('str aerop');
  }

  // 3. Riva di Pinerolo / Candiolo via Pinerolo vs Pinerolo Centro
  if (q.includes('riva') && !s.includes('riva')) return false;
  if (!q.includes('riva') && s.includes('riva di pinerolo')) return false;
  if (!q.includes('candiolo') && s.includes('candiolo via pinerolo')) return false;

  // 4. Ultra-fast semantic alias checks (O(1) string operations)
  if ((q.includes('porta susa') || q.includes('bolzano') || (q.includes('susa') && !q.includes('val di susa'))) && (s.includes('porta susa') || s.includes('bolzano'))) {
    return true;
  }
  if ((q.includes('porta nuova') || q.includes('carlo felice') || q.includes('v eman')) && (s.includes('porta nuova') || s.includes('carlo felice') || s.includes('v eman'))) {
    return true;
  }
  if ((q.includes('malpensa') || q.includes('mxp')) && s.includes('malpensa')) return true;
  if (q.includes('aosta') && s.includes('aosta')) return true;
  if (q.includes('pinerolo') && s.includes('pinerolo')) return true;
  if (q.includes('sestriere') && s.includes('sestriere')) return true;
  if (q.includes('oulx') && s.includes('oulx')) return true;
  if (q.includes('chivasso') && s.includes('chivasso')) return true;
  if (q.includes('ivrea') && s.includes('ivrea')) return true;
  if (q.includes('pont') && s.includes('pont')) return true;
  if (q.includes('verres') && s.includes('verres')) return true;
  if (q.includes('chatillon') && s.includes('chatillon')) return true;

  return false;
}

const AREAS = [
  { id: 'torino', label: 'Torino / Piemonte', default: true },
  { id: 'brescia', label: 'Brescia' },
  { id: 'bergamo', label: 'Bergamo' },
  { id: 'cremona', label: 'Cremona' },
  { id: 'aosta', label: 'Valle d\'Aosta' }
];

const POPULAR_STOPS = [
  { label: 'Torino Porta Susa', value: 'TORINO - Porta Susa' },
  { label: 'Torino Caselle Airport', value: 'TORINO - Aeroporto (Caselle)' },
  { label: 'Milano Malpensa Airport (T1/T2)', value: 'MALPENSA OVEST (Terminal 1)' },
  { label: 'Aosta Autostazione (SAVDA)', value: 'AOSTA - Autostazione (Piazza Manzetti)' },
  { label: 'Torino Porta Nuova', value: 'TORINO - Porta Nuova' },
  { label: 'Pinerolo Movicentro', value: 'PINEROLO - Movicentro' },
  { label: 'Perosa Argentina', value: 'PEROSA ARG.-pzza Terzo Alpini (Partenza)' },
  { label: 'Sestriere', value: 'SESTRIERE' },
  { label: 'Oulx Stazione FS', value: 'OULX - Stazione FS' },
  { label: 'Chivasso Centro (A4)', value: 'CHIVASSO CENTRO - casello A4' }
];

const HUBS = [
  { name: 'Torino Porta Susa / C.so Bolzano', query: 'TORINO - Porta Susa' },
  { name: 'Torino Porta Nuova', query: 'TORINO - Porta Nuova' },
  { name: 'Chivasso Casello A4', query: 'CHIVASSO CENTRO - casello A4' },
  { name: 'Ivrea Movicentro', query: 'IVREA' },
  { name: 'Pinerolo Movicentro', query: 'PINEROLO - Movicentro' }
];

function isValidTime(t) {
  if (!t || typeof t !== 'string') return false;
  const clean = t.trim();
  if (clean === '-' || clean === '' || clean.length > 5) return false;
  // Strictly matches HH:MM or HH.MM (e.g. "06:15", "6:15", "14.30")
  return /^([0-1]?[0-9]|2[0-3])[:.][0-5][0-9]$/.test(clean);
}

function parseTimeToMinutes(t) {
  if (!isValidTime(t)) return null;
  const clean = t.trim().replace(':', '.');
  const parts = clean.split('.');
  if (parts.length !== 2) return null;
  const h = parseInt(parts[0], 10);
  const m = parseInt(parts[1], 10);
  if (isNaN(h) || isNaN(m)) return null;
  return h * 60 + m;
}

function formatDuration(mins) {
  if (!mins || mins <= 0) return '';
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  if (h === 0) return `${m} min`;
  return `${h}h ${m > 0 ? `${m}m` : ''}`;
}

function formatStopDisplayName(name) {
  if (!name) return '';
  let clean = name.trim();
  if (clean.toLowerCase().includes('perosa arg')) {
    return 'PEROSA ARGENTINA - piazza Terzo Alpini';
  }
  clean = clean.replace(/\s*\((?:Arrivo|Partenza|arrivo|partenza|part\.)\)/gi, '');
  clean = clean.replace(/\s+(?:arrivo|partenza|part\.)\s*$/gi, '');
  return clean.trim();
}

// --------------------------------------------------------------------------
// Riconoscimento Fermate Urbane di Torino (Regola Solo Carico in uscita)
// --------------------------------------------------------------------------
function isTorinoUrbanStop(name) {
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
}

function isSameLine(lineA, lineB) {
  if (!lineA || !lineB) return false;
  const numA = String(lineA).replace(/\D+/g, '');
  const numB = String(lineB).replace(/\D+/g, '');
  if (numA && numB && numA === numB) return true;
  const cleanA = String(lineA).toLowerCase().replace(/[^a-z0-9]/g, '');
  const cleanB = String(lineB).toLowerCase().replace(/[^a-z0-9]/g, '');
  return cleanA === cleanB || cleanA.includes(cleanB) || cleanB.includes(cleanA);
}

// --------------------------------------------------------------------------
// Calcolo Coincidenze / Connessioni Autista & Passeggeri (Hub Transfers)
// --------------------------------------------------------------------------
function getStopConnections(stopName, arrivalTime, excludeTripId, dayFilter = 'today', windowMins = 25, excludeLine = null) {
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

    // REGOLA FONDAMENTALE: la coincidenza è un cambio verso un'ALTRA linea (escludi corse della stessa linea)
    if (currentLine && isSameLine(currentLine, trip.line)) {
      return;
    }

    // Day filter
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
    } else if (dayFilter === 'fer') {
      if (!trip.days.includes('1') && !trip.days.includes('2') && !trip.days.includes('3') && !trip.days.includes('4') && !trip.days.includes('5') && trip.season !== 'FER') return;
    } else if (dayFilter === 'sab') {
      if (!trip.days.includes('6')) return;
    } else if (dayFilter === 'dom') {
      if (!trip.days.includes('7') && !trip.days.includes('8') && trip.season !== 'FES' && trip.season !== 'FEST') return;
    } else if (dayFilter === 'sco') {
      if (trip.season !== 'SCO' && !trip.season.includes('SCO')) return;
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

            // REGOLA TPL: a Torino si può salire solo su corse dirette FUORI Torino (non su corse che terminano a Torino)
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
                directionTo: cleanDest,
                days: trip.days
              });
            }
          }
        }
      }
    }
  });

  connections.sort((a, b) => a.waitMins - b.waitMins);
  return connections;
}

// --------------------------------------------------------------------------
// Calcolo Costi Biglietti & Tariffe Ufficiali Arriva / SAVDA / Extraurbano
// --------------------------------------------------------------------------
function calculateFare(line, fromName, toName, durationMins, isTripExpress = false) {
  const lineStr = String(line || '').toLowerCase();
  const f = String(fromName || '').toLowerCase();
  const t = String(toName || '').toLowerCase();

  // 1. Malpensa Express (Linea 20)
  if (lineStr.includes('20') || lineStr.includes('malpensa express')) {
    if (f.includes('chivasso') || f.includes('carisio') || t.includes('chivasso') || t.includes('carisio')) {
      return { 
        priceNum: 18.0, 
        price: '18,00 €', 
        type: 'Tariffa A4 Aeroporto', 
        bookingUrl: 'https://estore.arriva.it/?routeId=000020&lang=it', 
        channel: 'E-Store Arriva / A bordo' 
      };
    }
    return { 
      priceNum: 22.0, 
      price: '22,00 €', 
      type: 'Tariffa Malpensa Express', 
      bookingUrl: 'https://estore.arriva.it/?routeId=000020&lang=it', 
      channel: 'E-Store Arriva / A bordo' 
    };
  }

  // 2. SAVDA Malpensa <-> Valle d'Aosta (Diretto)
  if (lineStr.includes('savda') && (lineStr.includes('malpensa') || f.includes('malpensa') || t.includes('malpensa'))) {
    if (f.includes('pont') || t.includes('pont')) return { priceNum: 15.0, price: '15,00 €', type: 'SAVDA Malpensa', bookingUrl: 'https://estore.arriva.it/?routeId=000101&lang=it', channel: 'E-Store SAVDA' };
    if (f.includes('verres') || t.includes('verres')) return { priceNum: 17.0, price: '17,00 €', type: 'SAVDA Malpensa', bookingUrl: 'https://estore.arriva.it/?routeId=000101&lang=it', channel: 'E-Store SAVDA' };
    if (f.includes('chatillon') || t.includes('chatillon')) return { priceNum: 19.0, price: '19,00 €', type: 'SAVDA Malpensa', bookingUrl: 'https://estore.arriva.it/?routeId=000101&lang=it', channel: 'E-Store SAVDA' };
    return { 
      priceNum: 20.0, 
      price: '20,00 €', 
      type: 'SAVDA Malpensa ↔ Aosta', 
      bookingUrl: 'https://estore.arriva.it/?routeId=000101&lang=it', 
      channel: 'E-Store SAVDA / A bordo' 
    };
  }

  // 3. SAVDA Torino <-> Aosta (Linea 101)
  if (lineStr.includes('101') || (lineStr.includes('savda') && (f.includes('aosta') || t.includes('aosta')))) {
    if (f.includes('pont') || t.includes('pont')) return { priceNum: 6.5, price: '6,50 €', type: 'SAVDA Interregionale', bookingUrl: 'https://estore.arriva.it/?routeId=000101&lang=it', channel: 'E-Store / Rivendite' };
    if (f.includes('verres') || t.includes('verres')) return { priceNum: 8.2, price: '8,20 €', type: 'SAVDA Interregionale', bookingUrl: 'https://estore.arriva.it/?routeId=000101&lang=it', channel: 'E-Store / Rivendite' };
    if (f.includes('chatillon') || t.includes('chatillon')) return { priceNum: 9.4, price: '9,40 €', type: 'SAVDA Interregionale', bookingUrl: 'https://estore.arriva.it/?routeId=000101&lang=it', channel: 'E-Store / Rivendite' };
    return { 
      priceNum: 10.7, 
      price: '10,70 €', 
      type: 'SAVDA Torino ↔ Aosta', 
      bookingUrl: 'https://estore.arriva.it/?routeId=000101&lang=it', 
      channel: 'E-Store / Rivendite' 
    };
  }

  // 4. Caselle Express vs Stradale (Linea 268) - Basato sull'intera tratta capolinea-capolinea
  if (lineStr.includes('268') || f.includes('caselle') || t.includes('caselle') || f.includes('aeroporto') || t.includes('aeroporto')) {
    return { 
      priceNum: 7.5, 
      price: '7,50 €', 
      onboardPrice: '7,50 € (Contactless)', 
      type: isTripExpress ? 'Navetta Express Caselle' : 'Navetta Caselle (Stradale)', 
      isExpress: Boolean(isTripExpress), 
      bookingUrl: 'https://estore.arriva.it/?&routeId=TORCAS', 
      channel: 'App MyPay / Contactless a bordo' 
    };
  }

  // 5. Linee Extraurbane Piemonte (Pinerolo, Perosa, Sestriere, Ivrea)
  if (f.includes('sestriere') || t.includes('sestriere') || f.includes('oulx') || t.includes('oulx') || f.includes('claviere') || t.includes('claviere')) {
    return { priceNum: 8.5, price: '8,50 €', type: 'Tariffa Extraurbana Montagna (F14)', channel: 'Arriva MyPay / BIP' };
  }
  if (f.includes('perosa') || t.includes('perosa')) {
    return { priceNum: 5.6, price: '5,60 €', type: 'Tariffa Extraurbana F10 (45-50 km)', channel: 'Arriva MyPay / BIP' };
  }
  if (f.includes('pinerolo') || t.includes('pinerolo')) {
    return { priceNum: 4.6, price: '4,60 €', type: 'Tariffa Extraurbana F7 (30-35 km)', channel: 'Arriva MyPay / BIP' };
  }
  if (f.includes('ivrea') || t.includes('ivrea')) {
    return { priceNum: 6.1, price: '6,10 €', type: 'Tariffa Extraurbana F11 (50-60 km)', channel: 'Arriva MyPay / BIP' };
  }

  // 6. Calcolo automatico in base alla durata/percorrenza stimata
  if (durationMins) {
    if (durationMins <= 15) return { priceNum: 2.0, price: '2,00 €', type: 'Corsa Semplice F1 (1-5 km)', channel: 'Arriva MyPay / BIP' };
    if (durationMins <= 30) return { priceNum: 3.1, price: '3,10 €', type: 'Extraurbano F4 (15-20 km)', channel: 'Arriva MyPay / BIP' };
    if (durationMins <= 50) return { priceNum: 4.6, price: '4,60 €', type: 'Extraurbano F7/F8 (30-40 km)', channel: 'Arriva MyPay / BIP' };
    if (durationMins <= 80) return { priceNum: 6.1, price: '6,10 €', type: 'Extraurbano F11 (50-60 km)', channel: 'Arriva MyPay / BIP' };
    return { priceNum: 8.5, price: '8,50 €', type: 'Extraurbano Montagna F14', channel: 'Arriva MyPay / BIP' };
  }

  return { priceNum: 3.5, price: '3,50 €', type: 'Tariffa Extraurbana F5', channel: 'Arriva MyPay / BIP' };
}

// Trova turno associato a una corsa specifica
function matchTurnoForTrip(line, depTime, dayFilter = 'feriale') {
  if (!turniCorseDb || turniCorseDb.length === 0) return null;
  const lineClean = String(line || '').replace(/\D+/g, '');
  let depClean = String(depTime || '').replace('.', ':').trim();
  if (depClean.length === 4 && depClean[1] === ':') {
    depClean = '0' + depClean;
  }

  for (const t of turniCorseDb) {
    const giorno = t.giorno || '';
    if (dayFilter === 'domenica' || dayFilter === 'festivo') {
      if (giorno !== 'Domenica') continue;
    } else if (dayFilter === 'sabato') {
      if (giorno !== 'Sabato') continue;
    } else {
      if (giorno === 'Domenica' || giorno === 'Sabato') continue;
    }

    for (const c of (t.corse || [])) {
      let cDep = String(c.partenza || '').replace('.', ':').trim();
      if (cDep.length === 4 && cDep[1] === ':') {
        cDep = '0' + cDep;
      }
      const cLine = String(c.linea || '').replace(/\D+/g, '');

      if (cDep === depClean) {
        if (!lineClean || !cLine || cLine.includes(lineClean) || lineClean.includes(cLine)) {
          return {
            codice: t.codice,
            nome: t.nome,
            deposito: t.deposito,
            giorno: t.giorno,
            inizio: t.inizio,
            fine: t.fine,
            corsaPartenza: c.partenza,
            corsaArrivo: c.arrivo,
            corsaDa: c.da,
            corsaA: c.a,
            pdfUrl: getCartellinoPdf(t.codice)
          };
        }
      }
    }
  }
  return null;
}


function isStopAChangeoverPoint(stopName) {
  if (!stopName) return false;
  const upper = stopName.toUpperCase();
  if (upper.includes('(ARRIVO)') || upper.includes('(PARTENZA)')) return true;
  if (upper.includes('PEROSA ARG') || upper.includes('MOVICENTRO') || upper.includes('CESANA') || upper.includes('SESTRIERE') || upper.includes('OULX FS') || upper.includes('OULX - STAZIONE')) return true;
  return false;
}

function getCartellinoPdf(code) {

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
}

function parseTratta(str) {
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
}

function matchTripInDb(c) {
  if (!c || !databaseOrari || !databaseOrari.trips) return null;
  const lineClean = String(c.linea || '').replace(/\D+/g, '');
  const depM = parseTimeToMinutes(c.partenza);
  if (depM === null) return null;

  const tratta = parseTratta(c.da);

  return databaseOrari.trips.find(t => {
    // 1. Strict Line Matching if line number exists
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
}

function formatDaysLabel(days, season) {
  if (season === 'SCO') return '🎒 Scolastico';
  if (days === '12345') return '📅 Lun - Ven';
  if (days === '123456') return '📅 Lun - Sab';
  if (days === '6') return '📅 Sabato';
  if (days === '7' || days === '8' || days === '78' || season === 'FES' || season === 'FEST') return '🔴 Festivo / Dom';
  if (days === 'NAT') return '🎄 Festività';
  if (season === 'FER') return '💼 Feriale';
  return days ? `📅 Giorni ${days}` : '';
}

export default function ArrivaServices({ onNoticeCountUpdate }) {
  const [activeSubTab, setActiveSubTab] = useState('travel'); // 'travel' | 'notices' | 'lines' | 'mypay' | 'info'
  const [selectedArea, setSelectedArea] = useState('torino');
  
  // Planner Search Mode: 'route' (Fermata a Fermata) vs 'turni' (Cerca per Turno / Deposito)
  const [plannerMode, setPlannerMode] = useState('route');

  // Trip Planner (Route) State
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [isOriginOpen, setIsOriginOpen] = useState(false);
  const [isDestOpen, setIsDestOpen] = useState(false);
  const [dayFilter, setDayFilter] = useState('today'); // 'today' | 'all' | 'fer' | 'sab' | 'dom' | 'sco'
  
  // Dynamic Today Label for Dropdown
  const todayOptionLabel = useMemo(() => {
    const dayNames = ['Domenica', 'Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato'];
    const dow = new Date().getDay();
    const dayName = dayNames[dow] || 'Oggi';
    if (dow === 0) return `🟢 Oggi (${dayName} - Festivo)`;
    if (dow === 6) return `🟢 Oggi (${dayName} - Sabato)`;
    return `🟢 Oggi (${dayName} - Lun-Ven)`;
  }, []);
  
  // Time Mode State: 'now' (Prossime corse da adesso) | 'all' (Tutte le corse) | 'morning' | 'afternoon' | 'evening' | 'custom'
  const [timeViewMode, setTimeViewMode] = useState('now');
  const [customTime, setCustomTime] = useState('');
  const [expandedTripId, setExpandedTripId] = useState(null);
  const [expandedTransferLegs, setExpandedTransferLegs] = useState({});
  const [showFullLineStops, setShowFullLineStops] = useState({});
  const [expandedConnKey, setExpandedConnKey] = useState(null);



  // Turni & Deposito Search State
  const [turnoSearchTerm, setTurnoSearchTerm] = useState('');
  const [selectedDeposito, setSelectedDeposito] = useState('all');
  const [selectedTurnoGiorno, setSelectedTurnoGiorno] = useState('all');
  const [expandedTurnoKey, setExpandedTurnoKey] = useState(null);
  const [expandedTurnoCorsaKey, setExpandedTurnoCorsaKey] = useState(null);

  // Tariffs Modal State
  const [showFaresModal, setShowFaresModal] = useState(false);
  const [faresModalTab, setFaresModalTab] = useState('airport');

  const originRef = useRef(null);
  const destRef = useRef(null);

  // Notices state
  const [notices, setNotices] = useState([]);
  const [loadingNotices, setLoadingNotices] = useState(true);
  const [noticesFilter, setNoticesFilter] = useState('all');
  const [noticeSearch, setNoticeSearch] = useState('');
  const [selectedNotice, setSelectedNotice] = useState(null);

  // Lines state
  const [lines, setLines] = useState([]);
  const [loadingLines, setLoadingLines] = useState(false);
  const [lineSearch, setLineSearch] = useState('');
  const [linesLoadedArea, setLinesLoadedArea] = useState(null);

  // App launcher state
  const [isAppInstalled, setIsAppInstalled] = useState(null);
  const [launchingApp, setLaunchingApp] = useState(false);

  // Current Device Time Helper
  const currentNowStr = useMemo(() => {
    const d = new Date();
    return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
  }, []);

  const currentNowMins = useMemo(() => {
    const d = new Date();
    return d.getHours() * 60 + d.getMinutes();
  }, []);

  // Close dropdowns on outside click
  useEffect(() => {
    function handleClickOutside(e) {
      if (originRef.current && !originRef.current.contains(e.target)) {
        setIsOriginOpen(false);
      }
      if (destRef.current && !destRef.current.contains(e.target)) {
        setIsDestOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Unique Depositi List
  const depositiList = useMemo(() => {
    const set = new Set();
    turniCorseDb.forEach(t => {
      if (t.deposito && t.deposito !== '?') set.add(t.deposito);
    });
    return Array.from(set).sort();
  }, []);

  // Filtered Turni Search Results
  const filteredTurniResults = useMemo(() => {
    const q = turnoSearchTerm.trim().toLowerCase();
    return turniCorseDb.filter(t => {
      if (selectedDeposito !== 'all' && t.deposito !== selectedDeposito) return false;
      
      if (selectedTurnoGiorno !== 'all') {
        const tg = (t.giorno || '').toLowerCase();
        if (selectedTurnoGiorno === 'fer' && !tg.includes('feriale') && !tg.includes('lun')) return false;
        if (selectedTurnoGiorno === 'sab' && !tg.includes('sabato')) return false;
        if (selectedTurnoGiorno === 'dom' && !tg.includes('domenica') && !tg.includes('festivo')) return false;
      }

      if (!q) return true;
      const matchCodice = t.codice.toLowerCase().includes(q);
      const matchNome = t.nome.toLowerCase().includes(q);
      const matchDep = t.deposito.toLowerCase().includes(q);
      const matchCorsa = t.corse.some(c => 
        (c.linea && c.linea.toLowerCase().includes(q)) || 
        (c.da && c.da.toLowerCase().includes(q)) ||
        (c.partenza && c.partenza.includes(q))
      );

      return matchCodice || matchNome || matchDep || matchCorsa;
    });
  }, [turnoSearchTerm, selectedDeposito, selectedTurnoGiorno]);

  // Load notices
  const loadNotices = useCallback(async (area = selectedArea) => {
    setLoadingNotices(true);
    try {
      const res = await fetch(`${API_BASE}/api/arriva/notices?area=${area}`);
      if (!res.ok) throw new Error('Impossibile caricare gli avvisi');
      const data = await res.json();
      const list = data.notices || [];
      setNotices(list);
      if (area === 'torino' && onNoticeCountUpdate) {
        onNoticeCountUpdate(list.length);
      }
    } catch (err) {
      console.error('Errore fetch avvisi Arriva:', err);
    } finally {
      setLoadingNotices(false);
    }
  }, [selectedArea, onNoticeCountUpdate]);

  // Load lines
  const loadLines = useCallback(async (area = selectedArea) => {
    setLoadingLines(true);
    try {
      const res = await fetch(`${API_BASE}/api/arriva/lines?area=${area}`);
      if (!res.ok) throw new Error('Impossibile caricare le linee');
      const data = await res.json();
      setLines(data.lines || []);
      setLinesLoadedArea(area);
    } catch (err) {
      console.error('Errore fetch linee Arriva:', err);
    } finally {
      setLoadingLines(false);
    }
  }, [selectedArea]);

  // Check if Arriva MyPay app is installed
  useEffect(() => {
    async function checkInstalled() {
      if (Capacitor.isNativePlatform()) {
        try {
          const { value } = await AppLauncher.canOpenUrl({ url: 'net.pluservice.Arriva' });
          setIsAppInstalled(value);
        } catch (e) {
          setIsAppInstalled(false);
        }
      } else {
        setIsAppInstalled(false);
      }
    }
    checkInstalled();
  }, []);

  useEffect(() => {
    loadNotices(selectedArea);
  }, [selectedArea, loadNotices]);

  useEffect(() => {
    if (activeSubTab === 'lines' && linesLoadedArea !== selectedArea) {
      loadLines(selectedArea);
    }
  }, [activeSubTab, selectedArea, linesLoadedArea, loadLines]);

  const [toastMessage, setToastMessage] = useState(null);

  // Launch Arriva MyPay App with Route Clipboard Helper
  const handleLaunchApp = async (fromName = '', toName = '', line = '') => {
    setLaunchingApp(true);
    const pkg = 'net.pluservice.Arriva';

    if (fromName && toName) {
      if (typeof navigator !== 'undefined' && navigator.clipboard && navigator.clipboard.writeText) {
        try {
          await navigator.clipboard.writeText(`${fromName} - ${toName}`);
          setToastMessage(`📋 Tratta copiata: ${fromName} ➔ ${toName}`);
          setTimeout(() => setToastMessage(null), 4000);
        } catch (e) {
          // ignore clipboard error
        }
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
    } catch (err) {
      window.open(`https://play.google.com/store/apps/details?id=${pkg}`, '_system');
    } finally {
      setLaunchingApp(false);
    }
  };

  // Swap origin and destination
  const handleSwapStops = () => {
    const tempO = origin;
    setOrigin(destination);
    setDestination(tempO);
  };

  // Deferred values for non-blocking search calculations while typing
  const deferredOrigin = useDeferredValue(origin);
  const deferredDestination = useDeferredValue(destination);

  // Pre-indexed stops for ultra-fast autocomplete
  const allStopsIndexed = useMemo(() => {
    return (databaseOrari.stops || []).map(s => ({ raw: s, lower: s.toLowerCase() }));
  }, []);

  // Filtered stops list for autocomplete (smart ranking with key hubs prioritized)
  const filterStopsSmart = useCallback((query) => {
    const q = (query || '').toLowerCase().trim();
    if (!q) return databaseOrari.stops.slice(0, 25);

    const priorityMatches = [];
    const startsWithMatches = [];
    const containsMatches = [];

    // Prioritize main airport terminals and railway hubs
    if (q.includes('aero') || q.includes('casell') || q.includes('airp')) {
      priorityMatches.push('TORINO - Aeroporto (Caselle)');
    }
    if (q.includes('susa') || q.includes('bolzano')) {
      priorityMatches.push('TORINO - Porta Susa');
    }
    if (q.includes('nuova') || q.includes('carlo fel')) {
      priorityMatches.push('TORINO - Porta Nuova');
    }
    if (q.includes('malpensa') || q.includes('mxp')) {
      priorityMatches.push('MALPENSA OVEST (Terminal 1)');
      priorityMatches.push('MALPENSA NORD (Terminal 2)');
    }
    if (q.includes('aosta') || q.includes('savda')) {
      priorityMatches.push('AOSTA - Autostazione (Piazza Manzetti)');
    }
    if (q.includes('perosa') || q.includes('arg')) {
      priorityMatches.push('PEROSA ARGENTINA - Piazza Terzo Alpini');
    }

    for (let i = 0; i < allStopsIndexed.length; i++) {
      const item = allStopsIndexed[i];
      if (priorityMatches.includes(item.raw)) continue;
      // Skip raw PDF arrival/departure sub-rows in autocomplete for a clean UI
      if (/arrivo|partenza|part\./i.test(item.raw)) continue;

      if (item.lower.startsWith(q)) {
        startsWithMatches.push(item.raw);
      } else if (item.lower.includes(q)) {
        containsMatches.push(item.raw);
      }
    }

    return Array.from(new Set([...priorityMatches, ...startsWithMatches, ...containsMatches])).slice(0, 25);
  }, [allStopsIndexed]);

  const filteredOriginStops = useMemo(() => filterStopsSmart(origin), [origin, filterStopsSmart]);
  const filteredDestStops = useMemo(() => filterStopsSmart(destination), [destination, filterStopsSmart]);

  // Helper to find direct trips between 2 query strings
  const findDirectTrips = useCallback((fromQuery, toQuery) => {
    const results = [];
    const seenSignatures = new Set();

    // Regola TPL Extraurbano: divieto di servizio urbano interno a Torino (solo carico in uscita / solo scarico in entrata)
    if (isTorinoUrbanStop(fromQuery) && isTorinoUrbanStop(toQuery)) {
      return [];
    }

    databaseOrari.trips.forEach(trip => {
      // Days filter (Oggi, Feriale, Sabato, Festivo, Scolastico, Tutti)
      if (dayFilter === 'today') {
        const dow = new Date().getDay(); // 0=Sun, 1=Mon, ..., 6=Sat
        if (dow === 0) {
          if (!trip.days.includes('7') && !trip.days.includes('8') && trip.season !== 'FES' && trip.season !== 'FEST') return;
        } else if (dow === 6) {
          if (!trip.days.includes('6')) return;
        } else {
          const dowStr = String(dow);
          const isFerMatch = trip.days.includes(dowStr) || 
            trip.days.includes('1') || trip.days.includes('2') || trip.days.includes('3') || trip.days.includes('4') || trip.days.includes('5') ||
            trip.season === 'FER';
          if (!isFerMatch) return;
        }
      } else if (dayFilter === 'fer') {
        if (!trip.days.includes('1') && !trip.days.includes('2') && !trip.days.includes('3') && !trip.days.includes('4') && !trip.days.includes('5') && trip.season !== 'FER') return;
      } else if (dayFilter === 'sab') {
        if (!trip.days.includes('6')) return;
      } else if (dayFilter === 'dom') {
        if (!trip.days.includes('7') && !trip.days.includes('8') && trip.season !== 'FES' && trip.season !== 'FEST') return;
      } else if (dayFilter === 'sco') {
        if (trip.season !== 'SCO' && !trip.season.includes('SCO')) return;
      }

      let origIdx = -1;
      let destIdx = -1;

      trip.stops.forEach((s, idx) => {
        if (origIdx === -1 && isValidTime(s.time) && matchStop(s.name, fromQuery)) {
          origIdx = idx;
        }
        if (origIdx !== -1 && idx > origIdx && destIdx === -1 && isValidTime(s.time) && matchStop(s.name, toQuery)) {
          destIdx = idx;
        }
      });

      if (origIdx !== -1 && destIdx !== -1) {
        const origStop = trip.stops[origIdx];
        const destStop = trip.stops[destIdx];

        // Deduplication safety
        const sig = `${trip.line}_${origStop.time}_${destStop.time}_${origStop.name}_${destStop.name}_${trip.days}`;
        if (seenSignatures.has(sig)) return;
        seenSignatures.add(sig);

        const depMins = parseTimeToMinutes(origStop.time);
        const arrMins = parseTimeToMinutes(destStop.time);

        let durationMins = null;
        if (depMins !== null && arrMins !== null) {
          durationMins = (arrMins - depMins + 1440) % 1440;
        }

        // Calcolo Express vs Stradale basato sull'intera tratta capolinea-capolinea
        let isTripExpress = false;
        if (trip.line === '268' || String(trip.line).includes('268')) {
          const tStart = parseTimeToMinutes(trip.stops[0]?.time);
          const tEnd = parseTimeToMinutes(trip.stops[trip.stops.length - 1]?.time);
          let fullRunDuration = (tStart !== null && tEnd !== null) ? (tEnd - tStart) : null;
          if (fullRunDuration !== null && fullRunDuration < 0) fullRunDuration += 24 * 60;

          const hasExpressNote = (trip.notes || '').toUpperCase().includes('EXPRESS');
          const skipsIntermediateTowns = trip.stops.some(s => s.name.toLowerCase().includes('borgaro') && !isValidTime(s.time));
          isTripExpress = hasExpressNote || (fullRunDuration !== null && fullRunDuration < 44 && skipsIntermediateTowns);
        }

        const validAllStops = trip.stops.filter(s => isValidTime(s.time));
        const validIntermediateStops = trip.stops.slice(origIdx, destIdx + 1).filter(s => isValidTime(s.time));

        const fare = calculateFare(trip.line, origStop.name, destStop.name, durationMins, isTripExpress);
        const turnoAssigned = matchTurnoForTrip(trip.line, origStop.time);

        results.push({
          type: 'direct',
          tripId: trip.id,
          line: trip.line,
          isExpress: isTripExpress,
          days: trip.days,
          season: trip.season,
          notes: trip.notes,
          departureTime: origStop.time,
          arrivalTime: destStop.time,
          departureMins: depMins,
          arrivalMins: arrMins,
          durationMins,
          fromName: origStop.name,
          toName: destStop.name,
          allStops: validAllStops,
          intermediateStops: validIntermediateStops,
          fare,
          turnoAssigned
        });
      }
    });

    // Deduplicate identical physical runs (e.g. line 275/282 and line 285 sharing the exact same departure/arrival times)
    const dedupedDirectMap = new Map();
    results.forEach(res => {
      const depKey = String(res.departureTime || '').replace('.', ':');
      const arrKey = String(res.arrivalTime || '').replace('.', ':');
      const key = `${depKey}_${arrKey}`;
      
      if (!dedupedDirectMap.has(key)) {
        dedupedDirectMap.set(key, res);
      } else {
        const existing = dedupedDirectMap.get(key);
        // Keep the trip that has the most complete intermediate stops
        if ((res.intermediateStops?.length || 0) > (existing.intermediateStops?.length || 0)) {
          dedupedDirectMap.set(key, res);
        }
      }
    });

    return Array.from(dedupedDirectMap.values());
  }, [dayFilter]);


  // Combined Search: Direct + Multi-Leg Transfer Connections with Time Filtering & "Next Up" detection
  const searchResults = useMemo(() => {
    if (!deferredOrigin || !deferredDestination) return { mode: 'none', allItems: [], items: [], nextUpItem: null };

    // 1. Find all Direct Trips
    let directTrips = findDirectTrips(deferredOrigin, deferredDestination);
    directTrips.sort((a, b) => (a.departureMins ?? 9999) - (b.departureMins ?? 9999));

    // Determine min/max time bounds from timeViewMode
    let minMins = null;
    let maxMins = null;

    if (timeViewMode === 'now') {
      minMins = currentNowMins;
    } else if (timeViewMode === 'morning') {
      minMins = 5 * 60;
      maxMins = 12 * 60;
    } else if (timeViewMode === 'afternoon') {
      minMins = 12 * 60;
      maxMins = 18 * 60;
    } else if (timeViewMode === 'evening') {
      minMins = 18 * 60;
    } else if (timeViewMode === 'custom' && customTime) {
      minMins = parseTimeToMinutes(customTime);
    }

    if (directTrips.length > 0) {
      let filtered = directTrips;
      if (minMins !== null) {
        filtered = filtered.filter(t => t.departureMins === null || t.departureMins >= minMins);
      }
      if (maxMins !== null) {
        filtered = filtered.filter(t => t.departureMins === null || t.departureMins <= maxMins);
      }

      // If 'now' was selected but no more trips remain today, show message but allow easy switch
      const nextUpItem = filtered.length > 0 ? filtered[0] : null;

      return {
        mode: 'direct',
        allItems: directTrips,
        items: filtered,
        nextUpItem,
        totalDayCount: directTrips.length
      };
    }

    // 2. No direct trip found -> Find 1-transfer connection via Hubs (Smart Transit: prima coincidenza utile, zero doppioni)
    const transferSolutionsMap = new Map();

    HUBS.forEach(hub => {
      if (matchStop(deferredOrigin, hub.query) || matchStop(deferredDestination, hub.query)) return;

      const leg1List = findDirectTrips(deferredOrigin, hub.query);
      const leg2List = findDirectTrips(hub.query, deferredDestination);

      if (leg1List.length === 0 || leg2List.length === 0) return;

      leg1List.forEach(l1 => {
        if (l1.arrivalMins === null || l1.departureMins === null) return;

        // Trova SOLO la prima coincidenza utile l2 con attesa realistica compresa tra 5 e 50 minuti
        let bestL2 = null;
        let minWait = 9999;

        leg2List.forEach(l2 => {
          if (l2.departureMins === null) return;
          const waitMins = (l2.departureMins - l1.arrivalMins + 1440) % 1440;

          // Finestra reale di cambio coincidenza: da 5 min a massimo 50 min
          if (waitMins >= 5 && waitMins <= 50) {
            if (waitMins < minWait) {
              minWait = waitMins;
              bestL2 = l2;
            }
          }
        });

        if (bestL2) {
          const totalDuration = (l1.durationMins || 0) + minWait + (bestL2.durationMins || 0);
          const totalFareNum = ((l1.fare?.priceNum || 0) + (bestL2.fare?.priceNum || 0)).toFixed(2).replace('.', ',');

          const depKey = `${l1.departureTime}_${l1.fromName}`;
          const existing = transferSolutionsMap.get(depKey);

          // Se non esiste ancora per questo orario di partenza o se questa combinazione è più rapida, salvala
          if (!existing || totalDuration < existing.totalDuration) {
            transferSolutionsMap.set(depKey, {
              type: 'transfer',
              tripId: `${l1.tripId}_${bestL2.tripId}`,
              hubName: hub.name,
              waitMins: minWait,
              totalDuration,
              departureTime: l1.departureTime,
              arrivalTime: bestL2.arrivalTime,
              departureMins: l1.departureMins,
              fromName: l1.fromName,
              toName: bestL2.toName,
              totalFare: `${totalFareNum} €`,
              leg1: l1,
              leg2: bestL2
            });
          }
        }
      });
    });

    const transferSolutions = Array.from(transferSolutionsMap.values());
    transferSolutions.sort((a, b) => (a.departureMins ?? 9999) - (b.departureMins ?? 9999));


    let filteredTransfers = transferSolutions;
    if (minMins !== null) {
      filteredTransfers = filteredTransfers.filter(t => t.departureMins === null || t.departureMins >= minMins);
    }
    if (maxMins !== null) {
      filteredTransfers = filteredTransfers.filter(t => t.departureMins === null || t.departureMins <= maxMins);
    }

    return {
      mode: 'transfer',
      allItems: transferSolutions,
      items: filteredTransfers.slice(0, 20),
      nextUpItem: filteredTransfers.length > 0 ? filteredTransfers[0] : null,
      totalDayCount: transferSolutions.length
    };
  }, [deferredOrigin, deferredDestination, timeViewMode, customTime, currentNowMins, findDirectTrips]);

  const handleSearchSubmit = (e) => {
    if (e) e.preventDefault();
    setIsOriginOpen(false);
    setIsDestOpen(false);
  };

  // Filtered notices
  const filteredNotices = useMemo(() => {
    return notices.filter(n => {
      const matchType = noticesFilter === 'all' || n.type === noticesFilter;
      const q = noticeSearch.trim().toLowerCase();
      const matchSearch = !q || 
        n.title.toLowerCase().includes(q) || 
        n.excerpt.toLowerCase().includes(q) ||
        n.lines.some(l => l.toLowerCase().includes(q));
      return matchType && matchSearch;
    });
  }, [notices, noticesFilter, noticeSearch]);

  // Filtered lines
  const filteredLines = useMemo(() => {
    const q = lineSearch.trim().toLowerCase();
    if (!q) return lines;
    return lines.filter(l => 
      l.title.toLowerCase().includes(q) || 
      l.code.toLowerCase().includes(q) ||
      l.internalCode.toLowerCase().includes(q)
    );
  }, [lines, lineSearch]);

  const formatDate = (isoStr) => {
    if (!isoStr) return '';
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString('it-IT', { day: '2-digit', month: 'short', year: 'numeric' });
    } catch {
      return isoStr;
    }
  };

  return (
    <div className="arriva-services-container" style={{ width: '100%', maxWidth: '900px', margin: '0 auto', paddingBottom: '5rem' }}>
      
      {/* Hero Header */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(245, 166, 35, 0.12) 100%)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        padding: '1.25rem',
        marginBottom: '1.25rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.75rem',
        boxShadow: '0 4px 20px rgba(0,0,0,0.15)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '42px', height: '42px', borderRadius: '12px',
              background: 'linear-gradient(135deg, #0891b2, #0284c7)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: '#fff', boxShadow: '0 4px 12px rgba(8, 145, 178, 0.3)'
            }}>
              <Bus size={24} />
            </div>
            <div>
              <h2 style={{ fontSize: '1.2rem', fontWeight: '700', color: 'var(--text-main)', margin: 0, display: 'flex', alignItems: 'center', gap: '6px' }}>
                Arriva Italia <span style={{ fontSize: '0.8rem', padding: '2px 8px', background: 'rgba(245, 166, 35, 0.2)', color: 'var(--accent-orange)', borderRadius: '12px', border: '1px solid rgba(245, 166, 35, 0.4)' }}>Viaggia & MyPay</span>
              </h2>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
                Calcolo percorso, orari in tempo reale, ricerca turno e tariffe ufficiali
              </p>
            </div>
          </div>

          {/* Area Selector + Tabellario Button */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <button
              type="button"
              onClick={() => setShowFaresModal(true)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                background: 'rgba(16, 185, 129, 0.15)',
                border: '1px solid rgba(16, 185, 129, 0.4)',
                borderRadius: '8px',
                padding: '6px 12px',
                color: 'var(--accent-green)',
                fontWeight: '700',
                fontSize: '0.82rem',
                cursor: 'pointer'
              }}
            >
              <BookOpen size={15} />
              <span>Listino Tariffe</span>
            </button>

            <select
              value={selectedArea}
              onChange={(e) => setSelectedArea(e.target.value)}
              style={{
                background: 'var(--bg-card)',
                color: 'var(--text-main)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '6px 12px',
                fontSize: '0.85rem',
                cursor: 'pointer'
              }}
            >
              {AREAS.map(a => (
                <option key={a.id} value={a.id}>{a.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Sub-navigation tabs */}
        <div style={{
          display: 'flex',
          gap: '0.5rem',
          overflowX: 'auto',
          paddingTop: '0.5rem',
          borderTop: '1px solid rgba(255,255,255,0.06)'
        }}>
          <button
            onClick={() => setActiveSubTab('travel')}
            style={{
              flex: '1 1 auto',
              padding: '8px 14px',
              borderRadius: '8px',
              border: activeSubTab === 'travel' ? '1px solid var(--accent-orange)' : '1px solid var(--border-color)',
              background: activeSubTab === 'travel' ? 'var(--accent-orange)' : 'var(--bg-card)',
              color: activeSubTab === 'travel' ? '#121214' : 'var(--text-main)',
              fontWeight: activeSubTab === 'travel' ? '700' : '500',
              fontSize: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              transition: 'all 0.2s ease'
            }}
          >
            <Compass size={16} />
            <span>Viaggia & Ricerca</span>
          </button>

          <button
            onClick={() => setActiveSubTab('notices')}
            style={{
              flex: '1 1 auto',
              padding: '8px 14px',
              borderRadius: '8px',
              border: activeSubTab === 'notices' ? '1px solid var(--accent-orange)' : '1px solid var(--border-color)',
              background: activeSubTab === 'notices' ? 'var(--accent-orange)' : 'var(--bg-card)',
              color: activeSubTab === 'notices' ? '#121214' : 'var(--text-main)',
              fontWeight: activeSubTab === 'notices' ? '700' : '500',
              fontSize: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              transition: 'all 0.2s ease'
            }}
          >
            <Bell size={16} />
            <span>Avvisi & Deviazioni</span>
            {notices.length > 0 && (
              <span style={{
                background: activeSubTab === 'notices' ? '#121214' : 'var(--accent-orange)',
                color: activeSubTab === 'notices' ? '#fff' : '#121214',
                fontSize: '0.7rem',
                fontWeight: 'bold',
                padding: '1px 6px',
                borderRadius: '10px'
              }}>
                {notices.length}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveSubTab('lines')}
            style={{
              flex: '1 1 auto',
              padding: '8px 14px',
              borderRadius: '8px',
              border: activeSubTab === 'lines' ? '1px solid var(--accent-orange)' : '1px solid var(--border-color)',
              background: activeSubTab === 'lines' ? 'var(--accent-orange)' : 'var(--bg-card)',
              color: activeSubTab === 'lines' ? '#121214' : 'var(--text-main)',
              fontWeight: activeSubTab === 'lines' ? '700' : '500',
              fontSize: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              transition: 'all 0.2s ease'
            }}
          >
            <FileText size={16} />
            <span>Linee & Orari PDF</span>
          </button>

          <button
            onClick={() => setActiveSubTab('mypay')}
            style={{
              flex: '1 1 auto',
              padding: '8px 14px',
              borderRadius: '8px',
              border: activeSubTab === 'mypay' ? '1px solid var(--accent-orange)' : '1px solid var(--border-color)',
              background: activeSubTab === 'mypay' ? 'var(--accent-orange)' : 'var(--bg-card)',
              color: activeSubTab === 'mypay' ? '#121214' : 'var(--text-main)',
              fontWeight: activeSubTab === 'mypay' ? '700' : '500',
              fontSize: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              transition: 'all 0.2s ease'
            }}
          >
            <Smartphone size={16} />
            <span>App & MyPay</span>
          </button>

          <button
            onClick={() => setActiveSubTab('info')}
            style={{
              flex: '1 1 auto',
              padding: '8px 14px',
              borderRadius: '8px',
              border: activeSubTab === 'info' ? '1px solid var(--accent-orange)' : '1px solid var(--border-color)',
              background: activeSubTab === 'info' ? 'var(--accent-orange)' : 'var(--bg-card)',
              color: activeSubTab === 'info' ? '#121214' : 'var(--text-main)',
              fontWeight: activeSubTab === 'info' ? '700' : '500',
              fontSize: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              transition: 'all 0.2s ease'
            }}
          >
            <Info size={16} />
            <span>Contatti & Info</span>
          </button>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* SUB-TAB 1: VIAGGIA CON NOI - CALCOLA PERCORSO & RICERCA PER TURNO         */}
      {/* ========================================================================= */}
      {activeSubTab === 'travel' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          
          {/* Main Card */}
          <div style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--accent-cyan)',
            borderRadius: '16px',
            padding: '1.25rem',
            boxShadow: '0 8px 30px rgba(8, 145, 178, 0.12)',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem'
          }}>
            
            {/* Search Mode Switch Tabs */}
            <div style={{
              display: 'flex',
              gap: '6px',
              background: 'rgba(255,255,255,0.03)',
              padding: '4px',
              borderRadius: '12px',
              border: '1px solid var(--border-color)'
            }}>
              <button
                type="button"
                onClick={() => setPlannerMode('route')}
                style={{
                  flex: 1,
                  padding: '9px',
                  borderRadius: '9px',
                  border: 'none',
                  background: plannerMode === 'route' ? 'linear-gradient(135deg, #0891b2, #0284c7)' : 'transparent',
                  color: plannerMode === 'route' ? '#fff' : 'var(--text-muted)',
                  fontWeight: plannerMode === 'route' ? '700' : '500',
                  fontSize: '0.85rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                <Navigation size={16} />
                <span>Calcola Percorso (Fermate)</span>
              </button>

              <button
                type="button"
                onClick={() => setPlannerMode('turni')}
                style={{
                  flex: 1,
                  padding: '9px',
                  borderRadius: '9px',
                  border: 'none',
                  background: plannerMode === 'turni' ? 'linear-gradient(135deg, #f5a623, #d97706)' : 'transparent',
                  color: plannerMode === 'turni' ? '#121214' : 'var(--text-muted)',
                  fontWeight: plannerMode === 'turni' ? '700' : '500',
                  fontSize: '0.85rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                  cursor: 'pointer',
                  transition: 'all 0.2s'
                }}
              >
                <UserCheck size={16} />
                <span>Cerca Turno, Deposito & Corsa</span>
              </button>
            </div>

            {/* =================================================================== */}
            {/* MODE 1: CALCOLA PERCORSO (FERMATA ➔ FERMATA)                       */}
            {/* =================================================================== */}
            {plannerMode === 'route' && (
              <form onSubmit={handleSearchSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
                    Inserisci fermata di partenza e arrivo per visualizzare orari e prima corsa disponibile
                  </p>

                  {(origin || destination) && (
                    <button
                      type="button"
                      onClick={() => { setOrigin(''); setDestination(''); }}
                      style={{
                        background: 'transparent', border: 'none', color: 'var(--text-muted)', fontSize: '0.78rem', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px'
                      }}
                    >
                      <X size={14} />
                      <span>Azzera</span>
                    </button>
                  )}
                </div>

                {/* Input Form Partenza e Arrivo */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  
                  {/* Partenza Field */}
                  <div ref={originRef} style={{ position: 'relative' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', position: 'relative' }}>
                      <div style={{
                        width: '12px', height: '12px', borderRadius: '50%', background: '#10b981', flexShrink: 0, marginLeft: '6px'
                      }} />
                      <input
                        type="text"
                        value={origin}
                        onChange={(e) => {
                          setOrigin(e.target.value);
                          setIsOriginOpen(true);
                        }}
                        onFocus={() => setIsOriginOpen(true)}
                        placeholder="Da dove parti? (es. Torino Porta Susa, Malpensa, Pinerolo...)"
                        style={{
                          flex: 1,
                          background: 'rgba(255,255,255,0.03)',
                          border: '1px solid var(--border-color)',
                          borderRadius: '10px',
                          padding: '11px 14px',
                          color: 'var(--text-main)',
                          fontSize: '0.9rem',
                          outline: 'none'
                        }}
                      />
                      {origin && (
                        <X
                          size={16}
                          onClick={() => setOrigin('')}
                          style={{ position: 'absolute', right: '12px', color: 'var(--text-muted)', cursor: 'pointer' }}
                        />
                      )}
                    </div>

                    {/* Origin Dropdown Autocomplete */}
                    {isOriginOpen && filteredOriginStops.length > 0 && (
                      <div style={{
                        position: 'absolute', top: '100%', left: '26px', right: 0,
                        background: 'var(--bg-card)', border: '1px solid var(--accent-cyan)',
                        borderRadius: '10px', maxHeight: '220px', overflowY: 'auto',
                        zIndex: 100, boxShadow: '0 10px 25px rgba(0,0,0,0.5)', marginTop: '4px'
                      }}>
                        {filteredOriginStops.map(stop => (
                          <div
                            key={stop}
                            onClick={() => {
                              setOrigin(stop);
                              setIsOriginOpen(false);
                              if (!destination) {
                                setTimeout(() => {
                                  const destInput = destRef.current?.querySelector('input');
                                  if (destInput) {
                                    destInput.focus();
                                    setIsDestOpen(true);
                                  }
                                }, 60);
                              }
                            }}

                            style={{
                              padding: '8px 12px', fontSize: '0.85rem', cursor: 'pointer',
                              color: 'var(--text-main)', borderBottom: '1px solid rgba(255,255,255,0.04)',
                              display: 'flex', alignItems: 'center', gap: '6px'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(6, 182, 212, 0.15)'}
                            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                          >
                            <MapPin size={14} style={{ color: 'var(--accent-cyan)' }} />
                            <span>{stop}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Swap Button Divider */}
                  <div style={{ display: 'flex', justifyContent: 'center', margin: '-4px 0' }}>
                    <button
                      type="button"
                      onClick={handleSwapStops}
                      style={{
                        background: 'var(--btn-bg)',
                        border: '1px solid var(--border-color)',
                        borderRadius: '50%',
                        width: '32px', height: '32px',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        color: 'var(--accent-orange)',
                        cursor: 'pointer',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
                        transition: 'transform 0.2s'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.transform = 'rotate(180deg)'}
                      onMouseLeave={(e) => e.currentTarget.style.transform = 'rotate(0deg)'}
                      title="Inverti Partenza e Arrivo"
                    >
                      <ArrowUpDown size={15} />
                    </button>
                  </div>

                  {/* Arrivo Field */}
                  <div ref={destRef} style={{ position: 'relative' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', position: 'relative' }}>
                      <div style={{
                        width: '12px', height: '12px', borderRadius: '50%', background: '#ef4444', flexShrink: 0, marginLeft: '6px'
                      }} />
                      <input
                        type="text"
                        value={destination}
                        onChange={(e) => {
                          setDestination(e.target.value);
                          setIsDestOpen(true);
                        }}
                        onFocus={() => setIsDestOpen(true)}
                        placeholder="Dove vuoi arrivare? (es. Torino Caselle Airport, Aosta...)"
                        style={{
                          flex: 1,
                          background: 'rgba(255,255,255,0.03)',
                          border: '1px solid var(--border-color)',
                          borderRadius: '10px',
                          padding: '11px 14px',
                          color: 'var(--text-main)',
                          fontSize: '0.9rem',
                          outline: 'none'
                        }}
                      />
                      {destination && (
                        <X
                          size={16}
                          onClick={() => setDestination('')}
                          style={{ position: 'absolute', right: '12px', color: 'var(--text-muted)', cursor: 'pointer' }}
                        />
                      )}
                    </div>

                    {/* Destination Dropdown Autocomplete */}
                    {isDestOpen && filteredDestStops.length > 0 && (
                      <div style={{
                        position: 'absolute', top: '100%', left: '26px', right: 0,
                        background: 'var(--bg-card)', border: '1px solid var(--accent-orange)',
                        borderRadius: '10px', maxHeight: '220px', overflowY: 'auto',
                        zIndex: 100, boxShadow: '0 10px 25px rgba(0,0,0,0.5)', marginTop: '4px'
                      }}>
                        {filteredDestStops.map(stop => (
                          <div
                            key={stop}
                            onClick={() => {
                              setDestination(stop);
                              setIsDestOpen(false);
                            }}
                            style={{
                              padding: '8px 12px', fontSize: '0.85rem', cursor: 'pointer',
                              color: 'var(--text-main)', borderBottom: '1px solid rgba(255,255,255,0.04)',
                              display: 'flex', alignItems: 'center', gap: '6px'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(245, 166, 35, 0.15)'}
                            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                          >
                            <MapPin size={14} style={{ color: 'var(--accent-orange)' }} />
                            <span>{stop}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                </div>

                {/* Quick Popular Stop Chips */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Suggeriti:</span>
                  {POPULAR_STOPS.map(s => (
                    <button
                      key={s.label}
                      type="button"
                      onClick={() => {
                        if (!origin) {
                          setOrigin(s.value);
                        } else if (!destination) {
                          setDestination(s.value);
                        } else {
                          setDestination(s.value);
                        }
                      }}
                      style={{
                        background: 'rgba(255,255,255,0.04)',
                        border: '1px solid var(--border-color)',
                        borderRadius: '12px',
                        padding: '3px 9px',
                        fontSize: '0.74rem',
                        color: 'var(--text-main)',
                        cursor: 'pointer'
                      }}
                    >
                      + {s.label}
                    </button>
                  ))}
                </div>

                {/* =============================================================== */}
                {/* TENDINA & FILTRI ORARIO DI PARTENZA                             */}
                {/* =============================================================== */}
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.6rem',
                  padding: '10px 12px',
                  background: 'rgba(255,255,255,0.02)',
                  borderRadius: '10px',
                  border: '1px solid rgba(255,255,255,0.05)'
                }}>
                  
                  {/* Row 1: Tendina Selezione Orario */}
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flex: '1 1 250px' }}>
                      <Clock size={16} style={{ color: 'var(--accent-cyan)' }} />
                      <span style={{ fontSize: '0.8rem', fontWeight: 'bold', color: 'var(--text-main)' }}>Visualizzazione Orari:</span>
                      <select
                        value={timeViewMode}
                        onChange={(e) => setTimeViewMode(e.target.value)}
                        style={{
                          flex: 1,
                          background: 'var(--bg-card)',
                          color: 'var(--text-main)',
                          border: '1px solid var(--border-color)',
                          borderRadius: '8px',
                          padding: '6px 10px',
                          fontSize: '0.82rem',
                          fontWeight: '600',
                          outline: 'none',
                          cursor: 'pointer'
                        }}
                      >
                        <option value="now">⚡ Prossime corse da adesso ({currentNowStr})</option>
                        <option value="all">📋 Tutte le corse del giorno (00:00 - 24:00)</option>
                        <option value="morning">🌅 Mattina (05:00 - 12:00)</option>
                        <option value="afternoon">☀️ Pomeriggio (12:00 - 18:00)</option>
                        <option value="evening">🌙 Sera e Notte (18:00 - 05:00)</option>
                        <option value="custom">⏱️ Scegli orario specifico...</option>
                      </select>
                    </div>

                    {/* Custom Time Input (shown when 'custom' is selected) */}
                    {timeViewMode === 'custom' && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Dalle:</span>
                        <input
                          type="time"
                          value={customTime}
                          onChange={(e) => setCustomTime(e.target.value)}
                          style={{
                            background: 'var(--bg-card)', border: '1px solid var(--accent-orange)', borderRadius: '6px',
                            padding: '4px 8px', color: 'var(--text-main)', fontSize: '0.82rem', outline: 'none'
                          }}
                        />
                      </div>
                    )}
                  </div>

                  {/* Row 2: Filtro Giorni (Tendina a scomparsa con Oggi dinamico) */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', width: '100%', paddingTop: '6px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                    <label htmlFor="calendar-day-select" style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '5px', whiteSpace: 'nowrap' }}>
                      <Calendar size={14} style={{ color: 'var(--accent-cyan)' }} />
                      <span>Giorno:</span>
                    </label>
                    <div style={{ position: 'relative', flex: 1 }}>
                      <select
                        id="calendar-day-select"
                        value={dayFilter}
                        onChange={(e) => setDayFilter(e.target.value)}
                        style={{
                          width: '100%',
                          padding: '7px 32px 7px 10px',
                          borderRadius: '8px',
                          fontSize: '0.80rem',
                          fontWeight: '600',
                          background: 'var(--bg-input, rgba(255,255,255,0.05))',
                          border: '1px solid var(--border-color)',
                          color: dayFilter === 'today' ? '#10b981' : 'var(--text-main)',
                          cursor: 'pointer',
                          appearance: 'none',
                          WebkitAppearance: 'none'
                        }}
                      >
                        <option value="today">{todayOptionLabel}</option>
                        <option value="all">🗓️ Tutti i giorni (Tutto il calendario)</option>
                        <option value="fer">💼 Lunedì - Venerdì (Feriale)</option>
                        <option value="sab">🛍️ Sabato (Feriale)</option>
                        <option value="dom">🔴 Domenica e Festivi</option>
                        <option value="sco">🎒 Solo corse Scolastiche</option>
                      </select>
                      <ChevronDown size={14} style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', color: 'var(--text-muted)' }} />
                    </div>
                  </div>

                </div>

                {/* Results Section (Aggiornamento Istantaneo in Automatico) */}
                {(origin || destination) && (
                  <div style={{ marginTop: '0.25rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>

                    
                    {/* Header Bar with quick summary & view mode indicator */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255,255,255,0.06)', paddingBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ fontSize: '0.85rem', fontWeight: '700', color: 'var(--text-main)' }}>
                          Corse Disponibili: {searchResults.items?.length || 0}
                        </span>
                        {searchResults.totalDayCount > 0 && searchResults.items?.length !== searchResults.totalDayCount && (
                          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                            (su {searchResults.totalDayCount} totali del giorno)
                          </span>
                        )}
                        {searchResults.mode === 'transfer' && searchResults.items?.length > 0 && (
                          <span style={{ fontSize: '0.7rem', padding: '2px 6px', borderRadius: '4px', background: 'rgba(245, 166, 35, 0.15)', color: 'var(--accent-orange)', fontWeight: 'bold' }}>
                            Con Coincidenza
                          </span>
                        )}
                      </div>

                      {/* Quick Toggle: Show All vs Next Up */}
                      {searchResults.totalDayCount > 0 && (
                        <div style={{ display: 'flex', gap: '4px' }}>
                          <button
                            type="button"
                            onClick={() => setTimeViewMode('now')}
                            style={{
                              background: timeViewMode === 'now' ? 'rgba(16, 185, 129, 0.2)' : 'transparent',
                              border: timeViewMode === 'now' ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid var(--border-color)',
                              color: timeViewMode === 'now' ? 'var(--accent-green)' : 'var(--text-muted)',
                              borderRadius: '6px', padding: '2px 8px', fontSize: '0.72rem', fontWeight: 'bold', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '3px'
                            }}
                          >
                            <Zap size={11} />
                            <span>Da adesso</span>
                          </button>
                          <button
                            type="button"
                            onClick={() => setTimeViewMode('all')}
                            style={{
                              background: timeViewMode === 'all' ? 'rgba(8, 145, 178, 0.2)' : 'transparent',
                              border: timeViewMode === 'all' ? '1px solid rgba(8, 145, 178, 0.4)' : '1px solid var(--border-color)',
                              color: timeViewMode === 'all' ? 'var(--accent-cyan)' : 'var(--text-muted)',
                              borderRadius: '6px', padding: '2px 8px', fontSize: '0.72rem', fontWeight: 'bold', cursor: 'pointer'
                            }}
                          >
                            <span>Tutte ({searchResults.totalDayCount})</span>
                          </button>
                        </div>
                      )}
                    </div>

                    {!origin || !destination ? (
                      <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                        👆 Inserisci sia la fermata di <strong>partenza</strong> che di <strong>arrivo</strong> per visualizzare gli orari.
                      </div>
                    ) : (!searchResults.items || searchResults.items.length === 0) ? (
                      <div style={{
                        padding: '1.5rem', textAlign: 'center', background: 'rgba(255,255,255,0.02)',
                        borderRadius: '10px', border: '1px dashed var(--border-color)', color: 'var(--text-muted)'
                      }}>
                        {searchResults.totalDayCount > 0 ? (
                          <>
                            <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.85rem', color: 'var(--text-main)', fontWeight: '600' }}>
                              Nessuna ulteriore corsa in programma per oggi a partire dalle ore {timeViewMode === 'now' ? currentNowStr : customTime}.
                            </p>
                            <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.8rem' }}>
                              Ci sono {searchResults.totalDayCount} corse registrate nell'arco della giornata:
                            </p>
                            <button
                              type="button"
                              onClick={() => setTimeViewMode('all')}
                              style={{
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '6px',
                                padding: '8px 16px',
                                borderRadius: '8px',
                                background: 'rgba(8, 145, 178, 0.2)',
                                border: '1px solid var(--accent-cyan)',
                                color: 'var(--accent-cyan)',
                                fontSize: '0.85rem',
                                fontWeight: '700',
                                cursor: 'pointer'
                              }}
                            >
                              <Clock size={15} />
                              <span>Mostra tutte le {searchResults.totalDayCount} corse del giorno</span>
                            </button>
                          </>
                        ) : (
                          <>
                            <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.85rem', color: 'var(--text-main)', fontWeight: '600' }}>
                              Nessuna corsa diretta o con coincidenza trovata per questa combinazione.
                            </p>
                            <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.8rem' }}>
                              Puoi consultare direttamente l'app Arriva MyPay o il portale ufficiale:
                            </p>
                            <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                              <button
                                type="button"
                                onClick={handleLaunchApp}
                                style={{
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '6px',
                                  padding: '7px 14px',
                                  borderRadius: '6px',
                                  background: 'rgba(245, 166, 35, 0.15)',
                                  border: '1px solid rgba(245, 166, 35, 0.4)',
                                  color: 'var(--accent-orange)',
                                  fontSize: '0.8rem',
                                  fontWeight: '600',
                                  cursor: 'pointer'
                                }}
                              >
                                <Smartphone size={14} />
                                <span>Cerca su App Arriva MyPay</span>
                              </button>
                              <a
                                href={`https://torino.arriva.it/orari-e-linee/?departure=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destination)}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '6px',
                                  padding: '7px 14px',
                                  borderRadius: '6px',
                                  background: 'rgba(6, 182, 212, 0.15)',
                                  border: '1px solid rgba(6, 182, 212, 0.3)',
                                  color: 'var(--accent-cyan)',
                                  fontSize: '0.8rem',
                                  textDecoration: 'none',
                                  fontWeight: '600'
                                }}
                              >
                                <span>Cerca su Arriva.it</span>
                                <ExternalLink size={14} />
                              </a>
                            </div>
                          </>
                        )}
                      </div>
                    ) : (
                      searchResults.items.map((res, index) => {
                        const isExpanded = expandedTripId === res.tripId;
                        const isNextUpcoming = (timeViewMode === 'now' || timeViewMode === 'custom') && index === 0;



                        // Calculate wait time until bus departs
                        let waitMinutesDiff = null;
                        if (res.departureMins !== null && res.departureMins >= currentNowMins) {
                          waitMinutesDiff = res.departureMins - currentNowMins;
                        }

                        // DIRECT TRIP CARD
                        if (res.type === 'direct') {
                          const isMalpensa = String(res.line).includes('Malpensa') || String(res.line).includes('20');
                          const isCaselle = String(res.line).includes('268');
                          const isAosta = String(res.line).includes('101') || String(res.line).includes('Aosta') || String(res.line).includes('SAVDA');

                          return (
                            <div
                              key={res.tripId}
                              style={{
                                background: isNextUpcoming ? 'rgba(16, 185, 129, 0.04)' : 'rgba(255,255,255,0.02)',
                                border: isNextUpcoming 
                                  ? '2px solid #10b981' 
                                  : isMalpensa 
                                    ? '1px solid rgba(168, 85, 247, 0.4)' 
                                    : isAosta 
                                      ? '1px solid rgba(16, 185, 129, 0.4)' 
                                      : '1px solid var(--border-color)',
                                borderRadius: '12px',
                                padding: '0.95rem',
                                display: 'flex',
                                flexDirection: 'column',
                                gap: '0.6rem',
                                boxShadow: isNextUpcoming ? '0 0 20px rgba(16, 185, 129, 0.18)' : 'none',
                                position: 'relative'
                              }}
                            >
                              {/* Next Up Highlight Banner */}
                              {isNextUpcoming && (
                                <div style={{
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'space-between',
                                  background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.25), rgba(5, 150, 105, 0.25))',
                                  border: '1px solid rgba(16, 185, 129, 0.4)',
                                  borderRadius: '8px',
                                  padding: '4px 10px',
                                  fontSize: '0.75rem',
                                  fontWeight: '800',
                                  color: '#10b981'
                                }}>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                                    <Zap size={14} />
                                    <span>PRIMA CORSA IN PARTENZA</span>
                                  </div>
                                  {waitMinutesDiff !== null && (
                                    <span style={{ color: 'var(--text-main)' }}>
                                      {waitMinutesDiff === 0 ? 'In partenza adesso' : `Tra ${waitMinutesDiff} min`}
                                    </span>
                                  )}
                                </div>
                              )}

                              {/* Top Row: Line Badge + Turno Badge + Price Badge */}
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                                  <span style={{
                                    fontSize: '0.75rem', fontWeight: '800', padding: '2px 8px',
                                    borderRadius: '6px', 
                                    background: isMalpensa ? 'rgba(168, 85, 247, 0.2)' : isAosta ? 'rgba(16, 185, 129, 0.2)' : 'rgba(8, 145, 178, 0.2)',
                                    color: isMalpensa ? 'var(--accent-purple)' : isAosta ? 'var(--accent-green)' : 'var(--accent-cyan)', 
                                    border: isMalpensa ? '1px solid rgba(168, 85, 247, 0.4)' : isAosta ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid rgba(8, 145, 178, 0.4)'
                                  }}>
                                    {res.line.startsWith('Linea') || res.line.startsWith('SAVDA') ? res.line : `Linea ${res.line}`}
                                  </span>

                                  {/* Express vs Stradale Badge for Caselle */}
                                  {isCaselle && (
                                    <span style={{
                                      fontSize: '0.70rem', fontWeight: '800', padding: '2px 7px',
                                      borderRadius: '6px',
                                      background: res.fare?.isExpress ? 'rgba(245, 166, 35, 0.2)' : 'rgba(255,255,255,0.06)',
                                      color: res.fare?.isExpress ? 'var(--accent-orange)' : 'var(--text-muted)',
                                      border: res.fare?.isExpress ? '1px solid rgba(245, 166, 35, 0.4)' : '1px solid var(--border-color)',
                                      display: 'flex', alignItems: 'center', gap: '3px'
                                    }}>
                                      {res.fare?.isExpress ? <Zap size={11} /> : <Bus size={11} />}
                                      <span>{res.fare?.isExpress ? 'Express' : 'Stradale'}</span>
                                    </span>
                                  )}

                                  {/* Day / Period Validity Badge */}
                                  {(res.days || res.season) && (
                                    <span style={{
                                      fontSize: '0.70rem', fontWeight: '700', padding: '2px 7px',
                                      borderRadius: '6px',
                                      background: (res.days === '7' || res.days === '8' || res.days === '78' || res.season === 'FES' || res.season === 'FEST') 
                                        ? 'rgba(239, 68, 68, 0.15)' 
                                        : (res.days === '6')
                                          ? 'rgba(59, 130, 246, 0.15)'
                                          : 'rgba(16, 185, 129, 0.12)',
                                      color: (res.days === '7' || res.days === '8' || res.days === '78' || res.season === 'FES' || res.season === 'FEST') 
                                        ? '#ef4444' 
                                        : (res.days === '6')
                                          ? '#3b82f6'
                                          : '#10b981',
                                      border: (res.days === '7' || res.days === '8' || res.days === '78' || res.season === 'FES' || res.season === 'FEST') 
                                        ? '1px solid rgba(239, 68, 68, 0.35)' 
                                        : (res.days === '6')
                                          ? '1px solid rgba(59, 130, 246, 0.35)'
                                          : '1px solid rgba(16, 185, 129, 0.35)'
                                    }}>
                                      {formatDaysLabel(res.days, res.season)}
                                    </span>
                                  )}

                                  {/* Coincidenza / Cambio Intermedio Badge */}
                                  {(() => {
                                    const changeoverPoint = (res.intermediateStops || []).slice(1, -1).find((s) => isStopAChangeoverPoint(s.name));
                                    if (!changeoverPoint) return null;
                                    return (
                                      <span style={{
                                        fontSize: '0.72rem', fontWeight: '800', padding: '2px 8px',
                                        borderRadius: '6px', background: 'rgba(245, 166, 35, 0.2)',
                                        color: 'var(--accent-orange)', border: '1px solid rgba(245, 166, 35, 0.4)',
                                        display: 'inline-flex', alignItems: 'center', gap: '4px'
                                      }}>
                                        <Shuffle size={12} />
                                        <span>Coincidenza a {formatStopDisplayName(changeoverPoint.name)} (ore {changeoverPoint.time})</span>
                                      </span>
                                    );
                                  })()}


                                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                                    {res.tripId}
                                  </span>
                                </div>

                                {/* Ticket Price Badge */}
                                {res.fare && (
                                  <div style={{
                                    display: 'flex', alignItems: 'center', gap: '4px',
                                    background: 'rgba(16, 185, 129, 0.15)',
                                    border: '1px solid rgba(16, 185, 129, 0.4)',
                                    padding: '2px 8px', borderRadius: '8px',
                                    color: 'var(--accent-green)', fontWeight: '800', fontSize: '0.85rem'
                                  }}>
                                    <Tag size={13} />
                                    <span>{res.fare.price}</span>
                                  </div>
                                )}
                              </div>

                              {/* Departure -> Arrival Times Hero */}
                              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'rgba(0,0,0,0.2)', padding: '8px 12px', borderRadius: '8px' }}>
                                <div style={{ display: 'flex', flexDirection: 'column' }}>
                                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Partenza</span>
                                  <span style={{ fontSize: '1.25rem', fontWeight: '800', color: '#10b981' }}>
                                    {res.departureTime}
                                  </span>
                                  <span style={{ fontSize: '0.72rem', color: 'var(--text-main)', maxWidth: '140px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                    {formatStopDisplayName(res.fromName)}
                                  </span>
                                </div>

                                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2px' }}>
                                  {res.durationMins !== null && (
                                    <span style={{ fontSize: '0.72rem', fontWeight: 'bold', color: 'var(--accent-orange)' }}>
                                      ⏱️ {formatDuration(res.durationMins)}
                                    </span>
                                  )}
                                  <ArrowRight size={16} style={{ color: 'var(--text-muted)' }} />
                                  <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                                    {res.intermediateStops.length <= 2 ? 'Corsa Diretta' : `${res.intermediateStops.length - 1} fermate`}
                                  </span>
                                </div>

                                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Arrivo</span>
                                  <span style={{ fontSize: '1.25rem', fontWeight: '800', color: 'var(--accent-cyan)' }}>
                                    {res.arrivalTime}
                                  </span>
                                  <span style={{ fontSize: '0.72rem', color: 'var(--text-main)', maxWidth: '140px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', textAlign: 'right' }}>
                                    {formatStopDisplayName(res.toName)}
                                  </span>
                                </div>
                              </div>


                              {/* Ticket Details Box */}
                              {res.fare && (
                                <div style={{
                                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                                  background: 'rgba(255,255,255,0.02)', border: '1px dashed rgba(255,255,255,0.08)',
                                  borderRadius: '8px', padding: '6px 10px', fontSize: '0.75rem', flexWrap: 'wrap', gap: '4px'
                                }}>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-muted)' }}>
                                    <CreditCard size={14} style={{ color: 'var(--accent-cyan)' }} />
                                    <span>{res.fare.type}</span>
                                  </div>
                                  <span style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>
                                    {res.fare.channel}
                                  </span>
                                </div>
                              )}

                              {/* Actions */}
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '2px' }}>

                                <button
                                  type="button"
                                  onClick={() => setExpandedTripId(isExpanded ? null : res.tripId)}
                                  style={{
                                    background: isExpanded ? 'rgba(6, 182, 212, 0.15)' : 'rgba(255,255,255,0.04)',
                                    border: isExpanded ? '1px solid var(--accent-cyan)' : '1px solid var(--border-color)',
                                    borderRadius: '6px',
                                    padding: '4px 10px',
                                    color: isExpanded ? 'var(--accent-cyan)' : 'var(--text-main)',
                                    fontSize: '0.75rem',
                                    fontWeight: '600',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '5px'
                                  }}
                                >
                                  <MapPin size={13} style={{ color: 'var(--accent-cyan)' }} />
                                  <span>{isExpanded ? 'Chiudi fermate' : `Fermate (${res.intermediateStops?.length || 0})`}</span>
                                  <ChevronDown size={13} style={{ transform: isExpanded ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
                                </button>



                                {isAosta ? (
                                  <a
                                    href="https://estore.arriva.it/?routeId=000101&lang=it"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    style={{
                                      background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.4)',
                                      borderRadius: '6px', padding: '4px 10px', color: 'var(--accent-green)',
                                      fontSize: '0.75rem', fontWeight: '700', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px'
                                    }}
                                  >
                                    <Ticket size={13} />
                                    <span>Acquista {res.fare?.price || 'SAVDA'}</span>
                                  </a>
                                ) : isMalpensa ? (
                                  <a
                                    href="https://estore.arriva.it/?routeId=000020&lang=it"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    style={{
                                      background: 'rgba(168, 85, 247, 0.15)', border: '1px solid rgba(168, 85, 247, 0.4)',
                                      borderRadius: '6px', padding: '4px 10px', color: 'var(--accent-purple)',
                                      fontSize: '0.75rem', fontWeight: '700', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px'
                                    }}
                                  >
                                    <Ticket size={13} />
                                    <span>Acquista {res.fare?.price || 'Malpensa'}</span>
                                  </a>
                                ) : isCaselle ? (
                                  <a
                                    href="https://estore.arriva.it/?&routeId=TORCAS"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    style={{
                                      background: 'rgba(245, 166, 35, 0.15)', border: '1px solid rgba(245, 166, 35, 0.4)',
                                      borderRadius: '6px', padding: '4px 10px', color: 'var(--accent-orange)',
                                      fontSize: '0.75rem', fontWeight: '700', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px'
                                    }}
                                  >
                                    <Ticket size={13} />
                                    <span>Acquista {res.fare?.price || 'Caselle'}</span>
                                  </a>
                                ) : (
                                  <button
                                    type="button"
                                    onClick={() => handleLaunchApp(res.fromName, res.toName, res.line)}
                                    style={{
                                      background: 'rgba(245, 166, 35, 0.15)', border: '1px solid rgba(245, 166, 35, 0.3)',
                                      borderRadius: '6px', padding: '4px 10px', color: 'var(--accent-orange)',
                                      fontSize: '0.75rem', fontWeight: '700', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px'
                                    }}
                                  >
                                    <Ticket size={13} />
                                    <span>Acquista {res.fare?.price || 'MyPay'}</span>
                                  </button>
                                )}
                              </div>

                              {/* Intermediate stops */}
                              {isExpanded && (
                                <div style={{
                                  marginTop: '0.5rem', padding: '10px 12px', background: 'rgba(0,0,0,0.3)',
                                  borderRadius: '10px', borderLeft: '3px solid var(--accent-cyan)',
                                  display: 'flex', flexDirection: 'column', gap: '8px'
                                }}>
                                  {res.allStops && res.allStops.length > res.intermediateStops.length && (
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px', borderBottom: '1px solid rgba(255,255,255,0.06)', paddingBottom: '6px', flexWrap: 'wrap', gap: '4px' }}>
                                      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                                        {showFullLineStops[res.tripId] ? `Tutte le ${res.allStops.length} fermate della linea` : (res.intermediateStops.length <= 2 ? 'Tragitto Diretto' : `Tragitto (${res.intermediateStops.length} fermate)`)}
                                      </span>
                                      <button
                                        type="button"
                                        onClick={() => setShowFullLineStops(prev => ({ ...prev, [res.tripId]: !prev[res.tripId] }))}
                                        style={{
                                          background: showFullLineStops[res.tripId] ? 'rgba(8, 145, 178, 0.25)' : 'rgba(255,255,255,0.06)',
                                          border: '1px solid rgba(8, 145, 178, 0.4)',
                                          color: 'var(--accent-cyan)',
                                          padding: '2px 8px', borderRadius: '6px', fontSize: '0.70rem', fontWeight: 'bold', cursor: 'pointer'
                                        }}
                                      >
                                        {showFullLineStops[res.tripId] ? 'Mostra solo tuo tragitto' : `Mostra linea intera (${res.allStops.length} fermate)`}
                                      </button>
                                    </div>
                                  )}

                                  {(() => {
                                    const stopsToRender = showFullLineStops[res.tripId] ? res.allStops : res.intermediateStops;
                                    const fromPos = stopsToRender.findIndex(s => s.name === res.fromName);
                                    const toPos = stopsToRender.findIndex(s => s.name === res.toName);

                                    return stopsToRender.map((stop, sIdx) => {
                                      let isOriginStop = false;
                                      let isDestStop = false;
                                      let isOutsideSegment = false;

                                      if (showFullLineStops[res.tripId]) {
                                        if (sIdx === fromPos) isOriginStop = true;
                                        else if (sIdx === toPos) isDestStop = true;
                                        else if (fromPos !== -1 && toPos !== -1 && (sIdx < fromPos || sIdx > toPos)) isOutsideSegment = true;
                                      } else {
                                        if (sIdx === 0) isOriginStop = true;
                                        else if (sIdx === stopsToRender.length - 1) isDestStop = true;
                                      }

                                      const isChangeover = isStopAChangeoverPoint(stop.name) && !isOriginStop && !isDestStop && !isOutsideSegment;

                                      return (
                                        <div key={sIdx} style={{ display: 'flex', flexDirection: 'column' }}>
                                          {isChangeover && (
                                            <div style={{
                                              margin: '4px 0',
                                              padding: '5px 10px',
                                              background: 'linear-gradient(135deg, rgba(245, 166, 35, 0.22) 0%, rgba(217, 119, 6, 0.15) 100%)',
                                              border: '1px solid #f5a623',
                                              borderRadius: '6px',
                                              display: 'flex',
                                              alignItems: 'center',
                                              justifyContent: 'space-between',
                                              fontSize: '0.75rem',
                                              fontWeight: '700',
                                              color: 'var(--accent-orange)'
                                            }}>
                                              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                                <Shuffle size={13} />
                                                <span>COINCIDENZA / CAMBIO A {formatStopDisplayName(stop.name).toUpperCase()}</span>
                                              </div>
                                              <span style={{ background: '#f5a623', color: '#121214', padding: '1px 6px', borderRadius: '4px', fontWeight: '800' }}>
                                                Ore {stop.time}
                                              </span>
                                            </div>
                                          )}

                                          <div style={{
                                            display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem',
                                            opacity: isOutsideSegment ? 0.5 : 1,
                                            background: isOriginStop ? 'rgba(16, 185, 129, 0.12)' : isDestStop ? 'rgba(6, 182, 212, 0.12)' : isChangeover ? 'rgba(245, 166, 35, 0.08)' : 'transparent',
                                            padding: (isOriginStop || isDestStop || isChangeover) ? '3px 8px' : '2px 0',
                                            borderRadius: '6px'
                                          }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                                              <span style={{ fontSize: '0.75rem' }}>
                                                {isOriginStop ? '🟢' : isDestStop ? '🏁' : isChangeover ? '🔄' : isOutsideSegment ? '⚪' : '🔵'}
                                              </span>
                                              <span style={{
                                                color: (isOriginStop || isDestStop) ? 'var(--text-main)' : isChangeover ? 'var(--accent-orange)' : isOutsideSegment ? 'var(--text-muted)' : 'var(--text-main)',
                                                fontWeight: (isOriginStop || isDestStop || isChangeover) ? '700' : 'normal'
                                              }}>
                                                {formatStopDisplayName(stop.name)}
                                              </span>
                                            </div>
                                            <span style={{
                                              color: isOriginStop ? '#10b981' : isDestStop ? 'var(--accent-cyan)' : isChangeover ? 'var(--accent-orange)' : 'var(--text-muted)',
                                              fontWeight: (isOriginStop || isDestStop || isChangeover) ? '700' : '500'
                                            }}>
                                              {stop.time}
                                            </span>
                                          </div>
                                        </div>
                                      );

                                    });
                                  })()}

                                </div>
                              )}
                            </div>
                          );
                        }

                        // TRANSFER TRIP CARD (1 INTERSCAMBIO)
                        return (
                          <div
                            key={res.tripId}
                            style={{
                              background: isNextUpcoming ? 'rgba(245, 166, 35, 0.06)' : 'rgba(245, 166, 35, 0.03)',
                              border: isNextUpcoming ? '2px solid #f5a623' : '1px solid rgba(245, 166, 35, 0.3)',
                              borderRadius: '12px',
                              padding: '1rem',
                              display: 'flex',
                              flexDirection: 'column',
                              gap: '0.75rem',
                              boxShadow: isNextUpcoming ? '0 0 20px rgba(245, 166, 35, 0.2)' : 'none'
                            }}
                          >
                            {/* Next Up Highlight Banner */}
                            {isNextUpcoming && (
                              <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                background: 'linear-gradient(135deg, rgba(245, 166, 35, 0.25), rgba(217, 119, 6, 0.25))',
                                border: '1px solid rgba(245, 166, 35, 0.4)',
                                borderRadius: '8px',
                                padding: '4px 10px',
                                fontSize: '0.75rem',
                                fontWeight: '800',
                                color: 'var(--accent-orange)'
                              }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                                  <Zap size={14} />
                                  <span>PRIMA COINCIDENZA IN PARTENZA</span>
                                </div>
                                {waitMinutesDiff !== null && (
                                  <span style={{ color: 'var(--text-main)' }}>
                                    {waitMinutesDiff === 0 ? 'In partenza adesso' : `Tra ${waitMinutesDiff} min`}
                                  </span>
                                )}
                              </div>
                            )}

                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                <span style={{
                                  fontSize: '0.75rem', fontWeight: '800', padding: '2px 8px',
                                  borderRadius: '6px', background: 'rgba(245, 166, 35, 0.2)',
                                  color: 'var(--accent-orange)', border: '1px solid rgba(245, 166, 35, 0.4)',
                                  display: 'flex', alignItems: 'center', gap: '4px'
                                }}>
                                  <Shuffle size={12} />
                                  <span>1 Coincidenza</span>
                                </span>
                                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                  via {res.hubName}
                                </span>
                              </div>

                              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <span style={{ fontSize: '0.78rem', fontWeight: 'bold', color: 'var(--accent-cyan)' }}>
                                  ⏱️ Totale {formatDuration(res.totalDuration)}
                                </span>
                                {res.totalFare && (
                                  <div style={{
                                    display: 'flex', alignItems: 'center', gap: '4px',
                                    background: 'rgba(16, 185, 129, 0.15)',
                                    border: '1px solid rgba(16, 185, 129, 0.4)',
                                    padding: '2px 8px', borderRadius: '8px',
                                    color: 'var(--accent-green)', fontWeight: '800', fontSize: '0.85rem'
                                  }}>
                                    <Tag size={13} />
                                    <span>{res.totalFare}</span>
                                  </div>
                                )}
                              </div>
                            </div>

                            {/* Visual Step-by-Step Connection */}
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', background: 'rgba(0,0,0,0.25)', padding: '10px 12px', borderRadius: '10px' }}>
                              
                              {/* 1. Tratta 1 (Partenza) */}
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }} />
                                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <span style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--text-main)' }}>
                                      1ª Tratta: Linea {res.leg1.line} {res.leg1.fare ? `(${res.leg1.fare.price})` : ''}
                                    </span>
                                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                                      Da {formatStopDisplayName(res.leg1.fromName)}
                                    </span>
                                  </div>
                                </div>
                                <span style={{ fontSize: '0.9rem', fontWeight: '800', color: '#10b981' }}>
                                  {res.leg1.departureTime} ➔ {res.leg1.arrivalTime}
                                </span>
                              </div>

                              {/* 2. AL CENTRO TRA PARTENZA ED ARRIVO: Interscambio + Pulsante Unico Tendina Fermate */}
                              <div style={{
                                margin: '4px 0',
                                padding: '8px 10px',
                                borderLeft: '2px dashed var(--accent-orange)',
                                display: 'flex',
                                flexDirection: 'column',
                                gap: '6px'
                              }}>
                                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '6px' }}>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--accent-orange)' }}>
                                    <Clock size={13} />
                                    <span>Cambio a <strong>{formatStopDisplayName(res.hubName)}</strong> • Attesa {res.waitMins} min</span>
                                  </div>
                                  <button
                                    type="button"
                                    onClick={() => setExpandedTransferLegs(prev => ({ ...prev, [res.tripId]: !prev[res.tripId] }))}
                                    style={{
                                      background: expandedTransferLegs[res.tripId] ? 'rgba(245, 166, 35, 0.25)' : 'rgba(245, 166, 35, 0.12)',
                                      border: '1px solid rgba(245, 166, 35, 0.4)',
                                      borderRadius: '6px',
                                      padding: '4px 10px',
                                      color: 'var(--accent-orange)',
                                      fontSize: '0.73rem',
                                      fontWeight: '700',
                                      cursor: 'pointer',
                                      display: 'inline-flex',
                                      alignItems: 'center',
                                      gap: '5px'
                                    }}
                                  >
                                    <MapPin size={12} />
                                    <span>
                                      {expandedTransferLegs[res.tripId]
                                        ? 'Nascondi fermate'
                                        : `Vedi tutte le fermate (${(res.leg1.intermediateStops?.length || 0) + (res.leg2.intermediateStops?.length || 0)} fermate con coincidenza)`}
                                    </span>
                                    <ChevronDown size={12} style={{ transform: expandedTransferLegs[res.tripId] ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
                                  </button>
                                </div>

                                {/* Tendina Unificata con tutte le fermate del percorso */}
                                {expandedTransferLegs[res.tripId] && (
                                  <div style={{
                                    marginTop: '4px',
                                    padding: '10px 12px',
                                    background: 'rgba(0,0,0,0.35)',
                                    borderRadius: '10px',
                                    borderLeft: '3px solid var(--accent-orange)',
                                    display: 'flex',
                                    flexDirection: 'column',
                                    gap: '4px'
                                  }}>
                                    {/* 1. Sezione 1ª Tratta */}
                                    <div style={{ fontSize: '0.72rem', fontWeight: '800', color: '#10b981', display: 'flex', alignItems: 'center', gap: '5px', marginBottom: '2px' }}>
                                      <span>1ª Tratta: Linea {res.leg1.line} (da {formatStopDisplayName(res.leg1.fromName)})</span>
                                    </div>
                                    {res.leg1.intermediateStops?.map((s, idx) => (
                                      <div key={`l1_${idx}`} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.74rem' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                          <span style={{ fontSize: '0.68rem' }}>{idx === 0 ? '🟢' : '•'}</span>
                                          <span style={{ color: idx === 0 ? 'var(--text-main)' : 'var(--text-muted)', fontWeight: idx === 0 ? '700' : 'normal' }}>
                                            {formatStopDisplayName(s.name)}
                                          </span>
                                        </div>
                                        <span style={{ color: idx === 0 ? '#10b981' : 'var(--text-muted)', fontWeight: '600' }}>
                                          {s.time}
                                        </span>
                                      </div>
                                    ))}

                                    {/* 2. Coincidenza Evidenziata */}
                                    <div style={{
                                      margin: '8px 0',
                                      padding: '8px 12px',
                                      background: 'linear-gradient(135deg, rgba(245, 166, 35, 0.25) 0%, rgba(217, 119, 6, 0.2) 100%)',
                                      border: '1.5px solid #f5a623',
                                      borderRadius: '8px',
                                      display: 'flex',
                                      flexDirection: 'column',
                                      gap: '3px',
                                      boxShadow: '0 2px 10px rgba(245, 166, 35, 0.15)'
                                    }}>
                                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '4px' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: '800', color: 'var(--accent-orange)', fontSize: '0.80rem' }}>
                                          <Shuffle size={14} />
                                          <span>CAMBIO BUS A {formatStopDisplayName(res.hubName).toUpperCase()}</span>
                                        </div>
                                        <span style={{
                                          fontWeight: '800', fontSize: '0.74rem', color: '#121214', background: 'var(--accent-orange)',
                                          padding: '2px 8px', borderRadius: '4px'
                                        }}>
                                          Attesa {res.waitMins} min
                                        </span>
                                      </div>
                                      <div style={{ fontSize: '0.73rem', color: 'var(--text-main)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '2px', borderTop: '1px dashed rgba(245,166,35,0.3)', paddingTop: '4px' }}>
                                        <span>Arrivo 1ª Tratta (L.{res.leg1.line}): <strong style={{ color: '#10b981' }}>{res.leg1.arrivalTime}</strong></span>
                                        <span style={{ color: 'var(--text-muted)' }}>➔</span>
                                        <span>Ripartenza 2ª Tratta (L.{res.leg2.line}): <strong style={{ color: 'var(--accent-cyan)' }}>{res.leg2.departureTime}</strong></span>
                                      </div>
                                    </div>

                                    {/* 3. Sezione 2ª Tratta */}
                                    <div style={{ fontSize: '0.72rem', fontWeight: '800', color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: '5px', marginBottom: '2px' }}>
                                      <span>2ª Tratta: Linea {res.leg2.line} (verso {formatStopDisplayName(res.leg2.toName)})</span>
                                    </div>
                                    {res.leg2.intermediateStops?.map((s, idx) => {
                                      const isLast = idx === (res.leg2.intermediateStops.length - 1);
                                      return (
                                        <div key={`l2_${idx}`} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.74rem' }}>
                                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                            <span style={{ fontSize: '0.68rem' }}>{isLast ? '🏁' : '•'}</span>
                                            <span style={{ color: isLast ? 'var(--text-main)' : 'var(--text-muted)', fontWeight: isLast ? '700' : 'normal' }}>
                                              {formatStopDisplayName(s.name)}
                                            </span>
                                          </div>
                                          <span style={{ color: isLast ? 'var(--accent-cyan)' : 'var(--text-muted)', fontWeight: '600' }}>
                                            {s.time}
                                          </span>
                                        </div>
                                      );
                                    })}
                                  </div>
                                )}
                              </div>

                              {/* 3. Tratta 2 (Arrivo) */}
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent-cyan)' }} />
                                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                                    <span style={{ fontSize: '0.8rem', fontWeight: '700', color: 'var(--text-main)' }}>
                                      2ª Tratta: Linea {res.leg2.line} {res.leg2.fare ? `(${res.leg2.fare.price})` : ''}
                                    </span>
                                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                                      Verso {formatStopDisplayName(res.leg2.toName)}
                                    </span>
                                  </div>
                                </div>
                                <span style={{ fontSize: '0.9rem', fontWeight: '800', color: 'var(--accent-cyan)' }}>
                                  {res.leg2.departureTime} ➔ {res.leg2.arrivalTime}
                                </span>
                              </div>

                            </div>







                            {/* Action buttons */}
                            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '6px', paddingTop: '2px' }}>
                              <a
                                href="https://estore.arriva.it"
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{
                                  background: 'rgba(245, 166, 35, 0.15)',
                                  border: '1px solid rgba(245, 166, 35, 0.35)',
                                  borderRadius: '6px',
                                  padding: '4px 10px',
                                  color: 'var(--accent-orange)',
                                  fontSize: '0.75rem',
                                  fontWeight: '700',
                                  textDecoration: 'none',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '4px'
                                }}
                              >
                                <Ticket size={13} />
                                <span>Acquista Biglietti Tratte</span>
                              </a>
                            </div>

                          </div>
                        );
                      })
                    )}
                  </div>
                )}

              </form>
            )}

            {/* =================================================================== */}
            {/* MODE 2: CERCA PER TURNO, DEPOSITO & CORSA (OPERATIVO AUTISTI)       */}
            {/* =================================================================== */}
            {plannerMode === 'turni' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
                  Cerca per <strong>Codice Turno</strong> (es. <code>Bo3050</code>, <code>Ca0017</code>, <code>Pe0010</code>, <code>FT101E</code>), <strong>Deposito</strong> o <strong>Linea/Corsa</strong>.
                </p>

                {/* Input Search Row */}
                <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                  
                  {/* Text search input */}
                  <div style={{ position: 'relative', flex: '2 1 240px' }}>
                    <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                    <input
                      type="text"
                      value={turnoSearchTerm}
                      onChange={(e) => setTurnoSearchTerm(e.target.value)}
                      placeholder="Cerca turno (es. Bo3050, Ca0017, Luserna, 268)..."
                      style={{
                        width: '100%',
                        background: 'rgba(255,255,255,0.03)',
                        border: '1px solid var(--border-color)',
                        borderRadius: '10px',
                        padding: '10px 12px 10px 36px',
                        color: 'var(--text-main)',
                        fontSize: '0.88rem',
                        outline: 'none'
                      }}
                    />
                    {turnoSearchTerm && (
                      <X
                        size={16}
                        onClick={() => setTurnoSearchTerm('')}
                        style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', cursor: 'pointer' }}
                      />
                    )}
                  </div>

                  {/* Deposito Selector */}
                  <div style={{ flex: '1 1 180px' }}>
                    <select
                      value={selectedDeposito}
                      onChange={(e) => setSelectedDeposito(e.target.value)}
                      style={{
                        width: '100%',
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-color)',
                        borderRadius: '10px',
                        padding: '10px 12px',
                        color: 'var(--text-main)',
                        fontSize: '0.85rem',
                        outline: 'none',
                        cursor: 'pointer'
                      }}
                    >
                      <option value="all">Tutti i Depositi ({depositiList.length})</option>
                      {depositiList.map(dep => (
                        <option key={dep} value={dep}>{dep}</option>
                      ))}
                    </select>
                  </div>

                </div>

                {/* Day Filter Row */}
                <div style={{ display: 'flex', gap: '6px', alignItems: 'center', overflowX: 'auto', paddingBottom: '2px' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Giorno:</span>
                  {[
                    { id: 'all', label: 'Tutti i giorni' },
                    { id: 'fer', label: 'Lun-Ven' },
                    { id: 'sab', label: 'Sabato' },
                    { id: 'dom', label: 'Domenica/Festivi' }
                  ].map(d => (
                    <button
                      key={d.id}
                      type="button"
                      onClick={() => setSelectedTurnoGiorno(d.id)}
                      style={{
                        padding: '4px 10px',
                        borderRadius: '6px',
                        fontSize: '0.75rem',
                        border: selectedTurnoGiorno === d.id ? '1px solid var(--accent-orange)' : '1px solid var(--border-color)',
                        background: selectedTurnoGiorno === d.id ? 'var(--accent-orange)' : 'rgba(255,255,255,0.02)',
                        color: selectedTurnoGiorno === d.id ? '#121214' : 'var(--text-muted)',
                        cursor: 'pointer',
                        fontWeight: selectedTurnoGiorno === d.id ? '700' : 'normal',
                        whiteSpace: 'nowrap'
                      }}
                    >
                      {d.label}
                    </button>
                  ))}
                </div>

                {/* Turni List Results */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    <span>Turni trovati: <strong>{filteredTurniResults.length}</strong></span>
                    <span>Mostrati in ordine di codice</span>
                  </div>

                  {filteredTurniResults.length === 0 ? (
                    <div style={{ padding: '2rem 1rem', textAlign: 'center', background: 'rgba(255,255,255,0.02)', borderRadius: '12px', border: '1px dashed var(--border-color)', color: 'var(--text-muted)' }}>
                      <UserCheck size={28} style={{ color: 'var(--text-muted)', margin: '0 auto 0.5rem' }} />
                      <p style={{ margin: 0, fontSize: '0.85rem' }}>Nessun turno corrisponde ai criteri cercati.</p>
                    </div>
                  ) : (
                    filteredTurniResults.map(turno => {
                      const turnoKey = `${turno.codice}_${turno.giorno}`;
                      const isExpanded = expandedTurnoKey === turnoKey;

                      return (
                        <div
                          key={turnoKey}
                          style={{
                            background: 'rgba(255,255,255,0.02)',
                            border: '1px solid var(--border-color)',
                            borderRadius: '12px',
                            padding: '1rem',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '0.6rem'
                          }}
                        >
                          {/* Turno Header Row */}
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <span style={{
                                fontSize: '0.85rem', fontWeight: '800', padding: '3px 10px',
                                borderRadius: '6px', background: 'linear-gradient(135deg, rgba(245, 166, 35, 0.25), rgba(217, 119, 6, 0.25))',
                                color: 'var(--accent-orange)', border: '1px solid rgba(245, 166, 35, 0.4)'
                              }}>
                                {turno.codice}
                              </span>
                              <span style={{ fontSize: '0.85rem', fontWeight: '600', color: 'var(--text-main)' }}>
                                {turno.nome}
                              </span>
                            </div>

                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                              <span style={{
                                fontSize: '0.72rem', padding: '2px 8px', borderRadius: '6px',
                                background: 'rgba(6, 182, 212, 0.15)', color: 'var(--accent-cyan)',
                                border: '1px solid rgba(6, 182, 212, 0.3)'
                              }}>
                                Dep. {turno.deposito}
                              </span>
                              <span style={{
                                fontSize: '0.72rem', padding: '2px 8px', borderRadius: '6px',
                                background: 'rgba(255,255,255,0.05)', color: 'var(--text-muted)'
                              }}>
                                {turno.giorno}
                              </span>
                            </div>
                          </div>

                          {/* Time Span & Total Corse Summary */}
                          {(() => {
                            const startM = parseTimeToMinutes(turno.inizio);
                            const endM = parseTimeToMinutes(turno.fine);
                            const nastroSpan = startM !== null && endM !== null ? formatDuration((endM - startM + 1440) % 1440) : '';
                            const pdfUrl = getCartellinoPdf(turno.codice);

                            return (
                              <>
                                <div style={{
                                  display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '6px',
                                  background: 'rgba(0,0,0,0.25)', padding: '8px 12px', borderRadius: '8px', fontSize: '0.8rem'
                                }}>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                    <Clock size={15} style={{ color: '#10b981' }} />
                                    <span style={{ color: 'var(--text-muted)' }}>Presa / Smonto:</span>
                                    <strong style={{ color: 'var(--text-main)' }}>{turno.inizio} ➔ {turno.fine}</strong>
                                    {nastroSpan && (
                                      <span style={{ color: 'var(--accent-orange)', fontWeight: 'bold', fontSize: '0.75rem', background: 'rgba(245, 166, 35, 0.12)', padding: '1px 6px', borderRadius: '4px' }}>
                                        ⏱️ {nastroSpan}
                                      </span>
                                    )}
                                  </div>

                                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--accent-cyan)' }}>
                                      <Layers size={14} />
                                      <span><strong>{turno.corse.length}</strong> corse</span>
                                    </div>
                                    {pdfUrl && (
                                      <a
                                        href={pdfUrl}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        onClick={(e) => e.stopPropagation()}
                                        style={{
                                          display: 'inline-flex', alignItems: 'center', gap: '4px',
                                          background: 'rgba(6, 182, 212, 0.15)', border: '1px solid rgba(6, 182, 212, 0.35)',
                                          color: 'var(--accent-cyan)', padding: '2px 8px', borderRadius: '6px',
                                          fontSize: '0.72rem', fontWeight: 'bold', textDecoration: 'none'
                                        }}
                                      >
                                        <FileText size={12} />
                                        <span>PDF Ufficiale</span>
                                        <ExternalLink size={10} />
                                      </a>
                                    )}
                                  </div>
                                </div>

                                {/* Toggle expand / Action Button */}
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '2px' }}>
                                  <button
                                    type="button"
                                    onClick={() => setExpandedTurnoKey(isExpanded ? null : turnoKey)}
                                    style={{
                                      background: isExpanded ? 'rgba(245, 166, 35, 0.15)' : 'transparent',
                                      border: isExpanded ? '1px solid rgba(245, 166, 35, 0.35)' : 'none',
                                      borderRadius: '6px', padding: '4px 8px',
                                      color: 'var(--accent-orange)', fontSize: '0.78rem', cursor: 'pointer',
                                      display: 'flex', alignItems: 'center', gap: '5px', fontWeight: '700'
                                    }}
                                  >
                                    <Navigation size={13} />
                                    <span>{isExpanded ? 'Chiudi foglio di marcia' : `Apri foglio di marcia (${turno.corse.length} corse)`}</span>
                                    <ChevronDown size={14} style={{ transform: isExpanded ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
                                  </button>

                                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                                    Orari e Passi di Guida
                                  </span>
                                </div>

                                {/* Assigned Corse Timeline */}
                                {isExpanded && (
                                  <div style={{
                                    marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem',
                                    borderLeft: '3px solid var(--accent-orange)', paddingLeft: '10px'
                                  }}>
                                    {/* 1. PRE-SERVIZIO CARD */}
                                    {(() => {
                                      const firstC = turno.corse[0];
                                      const firstDepM = firstC ? parseTimeToMinutes(firstC.partenza) : null;
                                      const preDiff = (startM !== null && firstDepM !== null) ? ((firstDepM - startM + 1440) % 1440) : 0;
                                      const firstFromClean = firstC ? formatStopDisplayName(parseTratta(firstC.da).from) : '';

                                      if (preDiff <= 0) return null;

                                      return (
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
                                              ⏱️ {formatDuration(preDiff)}
                                            </span>
                                          </div>

                                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-card)', border: '1px solid var(--border-color)', padding: '6px 10px', borderRadius: '8px', fontSize: '0.78rem' }}>
                                            <div style={{ display: 'flex', flexDirection: 'column' }}>
                                              <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Presa Servizio</span>
                                              <strong style={{ color: '#10b981' }}>{turno.inizio} (Dep. {turno.deposito})</strong>
                                            </div>
                                            <ArrowRight size={14} style={{ color: 'var(--text-muted)' }} />
                                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                                              <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Inizio 1ª Corsa</span>
                                              <strong style={{ color: 'var(--accent-cyan)' }}>{firstC.partenza} ({firstFromClean})</strong>
                                            </div>
                                          </div>
                                        </div>
                                      );
                                    })()}

                                    {/* 2. CHRONOLOGICAL CORSE */}
                                    {turno.corse.map((c, cIdx) => {
                                      const tratta = parseTratta(c.da);
                                      const fromClean = formatStopDisplayName(tratta.from);
                                      const toClean = formatStopDisplayName(tratta.to || c.a);
                                      const depM = parseTimeToMinutes(c.partenza);
                                      const arrM = parseTimeToMinutes(c.arrivo);
                                      const runDur = (depM !== null && arrM !== null) ? formatDuration((arrM - depM + 1440) % 1440) : '';
                                      const matchedTrip = matchTripInDb(c);
                                      const corsaKey = `${turnoKey}_c${cIdx}`;
                                      const isCorsaOpen = expandedTurnoCorsaKey === corsaKey;

                                      // Calculate Layover or Deadhead Transfer
                                      let intermediateStep = null;
                                      if (cIdx < turno.corse.length - 1) {
                                        const nextC = turno.corse[cIdx + 1];
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

                                            {/* Route & Times */}
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-card-hover)', border: '1px solid var(--border-color)', padding: '6px 10px', borderRadius: '8px' }}>
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
                                                  onClick={() => setExpandedTurnoCorsaKey(isCorsaOpen ? null : corsaKey)}
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
                                                  Corsa Diretta / Cartellino
                                                </span>
                                              )}

                                              <button
                                                type="button"
                                                onClick={() => handleLaunchApp(fromClean, toClean, c.linea)}
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
                                                  const connections = getStopConnections(st.name, st.time, matchedTrip.id, selectedTurnoGiorno === 'all' ? 'today' : selectedTurnoGiorno, 25, c.linea);
                                                  const stopConnKey = `${turnoKey}_c${cIdx}_s${stIdx}`;
                                                  const isStopConnOpen = expandedStopConnKey === stopConnKey;

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
                                                                setExpandedStopConnKey(isStopConnOpen ? null : stopConnKey);
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
                                    {(() => {
                                      const lastC = turno.corse[turno.corse.length - 1];
                                      const lastArrM = lastC ? parseTimeToMinutes(lastC.arrivo) : null;
                                      const postDiff = (endM !== null && lastArrM !== null) ? ((endM - lastArrM + 1440) % 1440) : 0;
                                      const lastToClean = lastC ? formatStopDisplayName(parseTratta(lastC.da).to || lastC.a) : '';

                                      if (postDiff <= 0) return null;

                                      return (
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
                                              ⏱️ {formatDuration(postDiff)}
                                            </span>
                                          </div>

                                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-card)', border: '1px solid var(--border-color)', padding: '6px 10px', borderRadius: '8px', fontSize: '0.78rem' }}>
                                            <div style={{ display: 'flex', flexDirection: 'column' }}>
                                              <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Arrivo Ultima Corsa</span>
                                              <strong style={{ color: 'var(--accent-cyan)' }}>{lastC.arrivo} ({lastToClean})</strong>
                                            </div>
                                            <ArrowRight size={14} style={{ color: 'var(--text-muted)' }} />
                                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                                              <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>Smonto Servizio</span>
                                              <strong style={{ color: 'var(--accent-orange)' }}>{turno.fine} (Dep. {turno.deposito})</strong>
                                            </div>
                                          </div>
                                        </div>
                                      );
                                    })()}
                                  </div>
                                )}
                              </>
                            );
                          })()}

                        </div>
                      );
                    })
                  )}
                </div>

              </div>
            )}

          </div>

          {/* Sezione Collegamenti Aeroportuali & Speciali */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Plane size={20} style={{ color: 'var(--accent-cyan)' }} />
                <h3 style={{ fontSize: '1.05rem', fontWeight: '700', color: 'var(--text-main)', margin: 0 }}>
                  Collegamenti Aeroportuali & Linee Dirette
                </h3>
              </div>

              <button
                type="button"
                onClick={() => {
                  setFaresModalTab('airport');
                  setShowFaresModal(true);
                }}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--accent-orange)',
                  fontSize: '0.8rem',
                  fontWeight: '600',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <span>Vedi tutte le tariffe e abbonamenti</span>
                <ChevronRight size={14} />
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(270px, 1fr))', gap: '0.75rem' }}>
              
              {/* Card 1: Milano Malpensa */}
              <div style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '14px',
                padding: '1.25rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '0.75rem'
              }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 'bold', padding: '2px 8px', borderRadius: '6px', background: 'rgba(168, 85, 247, 0.15)', color: 'var(--accent-purple)' }}>
                      Linea 20 / Malpensa Express
                    </span>
                    <span style={{ fontSize: '0.75rem', fontWeight: 'bold', color: 'var(--accent-green)' }}>da 18,00 € / 22,00 €</span>
                  </div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: '700', color: 'var(--text-main)', margin: '0 0 4px 0' }}>
                    Torino ↔ Milano Malpensa (T1 & T2)
                  </h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
                    Partenze da C.so Bolzano (Porta Susa), C.so Giulio Cesare e Chivasso. Prenotazione posto a bordo garantito.
                  </p>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                  <a
                    href="https://estore.arriva.it/?routeId=000020&lang=it"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      flex: 1,
                      padding: '7px 10px',
                      borderRadius: '8px',
                      background: 'rgba(168, 85, 247, 0.15)',
                      border: '1px solid rgba(168, 85, 247, 0.4)',
                      color: 'var(--accent-purple)',
                      fontSize: '0.8rem',
                      fontWeight: '700',
                      textAlign: 'center',
                      textDecoration: 'none',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '4px'
                    }}
                  >
                    <Ticket size={14} />
                    <span>Acquista Biglietto (22 €)</span>
                  </a>
                  <a
                    href="https://torino.arriva.it/torino-aeroporto-di-milano-malpensa/"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      padding: '7px 10px',
                      borderRadius: '8px',
                      background: 'var(--btn-bg)',
                      border: '1px solid var(--border-color)',
                      color: 'var(--text-main)',
                      fontSize: '0.8rem',
                      textDecoration: 'none',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <ExternalLink size={14} />
                  </a>
                </div>
              </div>

              {/* Card 2: Torino Airport (Caselle) */}
              <div style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '14px',
                padding: '1.25rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '0.75rem'
              }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 'bold', padding: '2px 8px', borderRadius: '6px', background: 'rgba(6, 182, 212, 0.15)', color: 'var(--accent-cyan)' }}>
                      Navetta Express 268
                    </span>
                    <span style={{ fontSize: '0.75rem', fontWeight: 'bold', color: 'var(--accent-green)' }}>7,50 €</span>
                  </div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: '700', color: 'var(--text-main)', margin: '0 0 4px 0' }}>
                    Torino Centro ↔ Torino Airport
                  </h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
                    Fermate a Torino Porta Nuova, Porta Susa, Borgaro e arrivo diretto al Terminal Partenze Caselle.
                  </p>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                  <a
                    href="https://estore.arriva.it/?&routeId=TORCAS"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      flex: 1,
                      padding: '7px 10px',
                      borderRadius: '8px',
                      background: 'rgba(245, 166, 35, 0.15)',
                      border: '1px solid rgba(245, 166, 35, 0.4)',
                      color: 'var(--accent-orange)',
                      fontSize: '0.8rem',
                      fontWeight: '700',
                      textAlign: 'center',
                      textDecoration: 'none',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '4px'
                    }}
                  >
                    <Ticket size={14} />
                    <span>Acquista Biglietto (7,50 €)</span>
                  </a>
                  <a
                    href="https://torino.arriva.it/linee-aeroportuale-tpl-torino-centro-torino-airport/"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      padding: '7px 10px',
                      borderRadius: '8px',
                      background: 'var(--btn-bg)',
                      border: '1px solid var(--border-color)',
                      color: 'var(--text-main)',
                      fontSize: '0.8rem',
                      textDecoration: 'none',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <ExternalLink size={14} />
                  </a>
                </div>
              </div>

              {/* Card 3: Valle d'Aosta */}
              <div style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '14px',
                padding: '1.25rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '0.75rem'
              }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 'bold', padding: '2px 8px', borderRadius: '6px', background: 'rgba(16, 185, 129, 0.15)', color: 'var(--accent-green)' }}>
                      SAVDA / Arriva
                    </span>
                    <span style={{ fontSize: '0.75rem', fontWeight: 'bold', color: 'var(--accent-green)' }}>da 6,50 € a 20,00 €</span>
                  </div>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: '700', color: 'var(--text-main)', margin: '0 0 4px 0' }}>
                    Valle d'Aosta ↔ Torino & Malpensa
                  </h4>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.4 }}>
                    Collegamenti diretti per Aosta, Châtillon, Verrès e Pont St. Martin da Torino e dall'Aeroporto di Milano Malpensa.
                  </p>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                  <a
                    href="https://estore.arriva.it/?routeId=000101&lang=it"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      flex: 1,
                      padding: '7px 10px',
                      borderRadius: '8px',
                      background: 'rgba(16, 185, 129, 0.15)',
                      border: '1px solid rgba(16, 185, 129, 0.4)',
                      color: 'var(--accent-green)',
                      fontSize: '0.8rem',
                      fontWeight: '700',
                      textAlign: 'center',
                      textDecoration: 'none',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '4px'
                    }}
                  >
                    <Ticket size={14} />
                    <span>Acquista Biglietto SAVDA</span>
                  </a>
                  <a
                    href="https://aosta.arriva.it/aosta-torino/"
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      padding: '7px 10px',
                      borderRadius: '8px',
                      background: 'var(--btn-bg)',
                      border: '1px solid var(--border-color)',
                      color: 'var(--text-main)',
                      fontSize: '0.8rem',
                      textDecoration: 'none',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center'
                    }}
                  >
                    <ExternalLink size={14} />
                  </a>
                </div>
              </div>

            </div>
          </div>

          {/* Sezione Biglietti, Abbonamenti & Formula */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.75rem' }}>
              <CreditCard size={20} style={{ color: 'var(--accent-orange)' }} />
              <h3 style={{ fontSize: '1.05rem', fontWeight: '700', color: 'var(--text-main)', margin: 0 }}>
                Biglietti, Abbonamenti & Sistema Formula
              </h3>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '0.75rem' }}>
              
              <a
                href="https://torino.arriva.it/abbonati-online/"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '12px',
                  padding: '1rem',
                  textDecoration: 'none',
                  color: 'inherit',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.75rem'
                }}
              >
                <div style={{ padding: '8px', borderRadius: '10px', background: 'rgba(245, 166, 35, 0.15)', color: 'var(--accent-orange)' }}>
                  <CreditCard size={20} />
                </div>
                <div>
                  <h4 style={{ fontSize: '0.9rem', fontWeight: '700', color: 'var(--text-main)', margin: '0 0 2px 0' }}>
                    Abbonati Online
                  </h4>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.35 }}>
                    Ricarica abbonamenti mensili e annuali su tessera BIP senza code allo sportello.
                  </p>
                </div>
              </a>

              <a
                href="https://torino.arriva.it/titoli-di-viaggio-formula/"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '12px',
                  padding: '1rem',
                  textDecoration: 'none',
                  color: 'inherit',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.75rem'
                }}
              >
                <div style={{ padding: '8px', borderRadius: '10px', background: 'rgba(6, 182, 212, 0.15)', color: 'var(--accent-cyan)' }}>
                  <MapIcon size={20} />
                </div>
                <div>
                  <h4 style={{ fontSize: '0.9rem', fontWeight: '700', color: 'var(--text-main)', margin: '0 0 2px 0' }}>
                    Sistema Integrato Formula
                  </h4>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.35 }}>
                    Viaggia su bus Arriva, GTT e treni metropolitani con una sola tariffa integrata (Zone 1-8).
                  </p>
                </div>
              </a>

              <a
                href="https://torino.arriva.it/rivenditori/"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '12px',
                  padding: '1rem',
                  textDecoration: 'none',
                  color: 'inherit',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.75rem'
                }}
              >
                <div style={{ padding: '8px', borderRadius: '10px', background: 'rgba(168, 85, 247, 0.15)', color: 'var(--accent-green)' }}>
                  <MapPin size={20} />
                </div>
                <div>
                  <h4 style={{ fontSize: '0.9rem', fontWeight: '700', color: 'var(--text-main)', margin: '0 0 2px 0' }}>
                    Biglietterie & Rivendite
                  </h4>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.35 }}>
                    Mappa delle rivendite autorizzate, edicole e sportelli sul territorio piemontese.
                  </p>
                </div>
              </a>

              <a
                href="https://torino.arriva.it/sei-uno-studente/"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '12px',
                  padding: '1rem',
                  textDecoration: 'none',
                  color: 'inherit',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '0.75rem'
                }}
              >
                <div style={{ padding: '8px', borderRadius: '10px', background: 'rgba(168, 85, 247, 0.15)', color: 'var(--accent-purple)' }}>
                  <Sparkles size={20} />
                </div>
                <div>
                  <h4 style={{ fontSize: '0.9rem', fontWeight: '700', color: 'var(--text-main)', margin: '0 0 2px 0' }}>
                    Agevolazioni Studenti
                  </h4>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.35 }}>
                    Abbonamenti 10 e 12 mesi per scuole e università con tariffe agevolate.
                  </p>
                </div>
              </a>

            </div>
          </div>

          {/* Sezione Regole di Viaggio & Note Operative */}
          <div style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: '14px',
            padding: '1.25rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldCheck size={20} style={{ color: 'var(--accent-cyan)' }} />
              <h3 style={{ fontSize: '1.05rem', fontWeight: '700', color: 'var(--text-main)', margin: 0 }}>
                Regolamento di Viaggio & Servizi a Bordo
              </h3>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.75rem', fontSize: '0.85rem' }}>
              
              <div style={{ padding: '10px', borderRadius: '10px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: '700', color: 'var(--accent-orange)', marginBottom: '4px' }}>
                  <Bike size={16} />
                  <span>Biciclette & Monopattini</span>
                </div>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.35 }}>
                  Bici pieghevoli e monopattini ammessi a bordo se chiusi. Su linee abilitate è attiva la prenotazione della rastrelliera esterna.
                </p>
              </div>

              <div style={{ padding: '10px', borderRadius: '10px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: '700', color: 'var(--accent-cyan)', marginBottom: '4px' }}>
                  <Luggage size={16} />
                  <span>Bagagli Consentiti</span>
                </div>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.35 }}>
                  Gratuito un bagaglio a mano (max 50x30x25 cm). I bagagli voluminosi vanno alloggiati nel bagagliaio inferiore dell'autobus.
                </p>
              </div>

              <div style={{ padding: '10px', borderRadius: '10px', background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.04)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: '700', color: 'var(--accent-green)', marginBottom: '4px' }}>
                  <HelpCircle size={16} />
                  <span>Oggetti Smarriti</span>
                </div>
                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', margin: 0, lineHeight: 1.35 }}>
                  Per oggetti dimenticati a bordo, contattare l'Ufficio Movimento o compilare il modulo online su <a href="https://torino.arriva.it/oggetti-smarriti/" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-cyan)' }}>arriva.it</a>.
                </p>
              </div>

            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
              <a
                href="https://arriva.it/condizioni-di-viaggio-tpl/#torino"
                target="_blank"
                rel="noopener noreferrer"
                style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}
              >
                <FileCheck size={14} />
                <span>Consulta le Condizioni Generali di Viaggio TPL Arriva</span>
              </a>
              <a
                href="https://arriva.it/sanzioni/"
                target="_blank"
                rel="noopener noreferrer"
                style={{ fontSize: '0.8rem', color: 'var(--accent-orange)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}
              >
                <AlertCircle size={14} />
                <span>Norme e Sanzioni Tariffarie</span>
              </a>
            </div>
          </div>

        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-TAB 2: AVVISI & DEVIAZIONI                                            */}
      {/* ========================================================================= */}
      {activeSubTab === 'notices' && (
        <div>
          {/* Controls: Search, filters, refresh */}
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '0.75rem',
            marginBottom: '1rem',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            {/* Search input */}
            <div style={{
              position: 'relative',
              flex: '1 1 240px'
            }}>
              <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                type="text"
                value={noticeSearch}
                onChange={(e) => setNoticeSearch(e.target.value)}
                placeholder="Cerca linea (es. 265, 268) o parola chiave..."
                style={{
                  width: '100%',
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '10px',
                  padding: '9px 12px 9px 36px',
                  color: 'var(--text-main)',
                  fontSize: '0.85rem'
                }}
              />
              {noticeSearch && (
                <X
                  size={16}
                  onClick={() => setNoticeSearch('')}
                  style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', cursor: 'pointer' }}
                />
              )}
            </div>

            {/* Refresh button */}
            <button
              onClick={() => loadNotices(selectedArea)}
              disabled={loadingNotices}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '10px',
                padding: '9px 14px',
                color: 'var(--text-main)',
                fontSize: '0.85rem',
                cursor: loadingNotices ? 'not-allowed' : 'pointer'
              }}
            >
              <RefreshCw size={14} className={loadingNotices ? 'animate-spin' : ''} />
              <span>Aggiorna</span>
            </button>
          </div>

          {/* Filter Chips */}
          <div style={{ display: 'flex', gap: '0.5rem', overflowX: 'auto', marginBottom: '1.25rem', paddingBottom: '4px' }}>
            {[
              { id: 'all', label: 'Tutti gli avvisi' },
              { id: 'detour', label: '🔄 Deviazioni & Sospensioni' },
              { id: 'strike', label: '⚠️ Scioperi' },
              { id: 'roadwork', label: '🚧 Cantieri & Lavori' }
            ].map(f => (
              <button
                key={f.id}
                onClick={() => setNoticesFilter(f.id)}
                style={{
                  padding: '5px 12px',
                  borderRadius: '20px',
                  fontSize: '0.8rem',
                  fontWeight: noticesFilter === f.id ? '600' : 'normal',
                  background: noticesFilter === f.id ? 'var(--accent-cyan)' : 'var(--bg-card)',
                  color: noticesFilter === f.id ? '#121214' : 'var(--text-muted)',
                  border: noticesFilter === f.id ? '1px solid var(--accent-cyan)' : '1px solid var(--border-color)',
                  cursor: 'pointer',
                  whiteSpace: 'nowrap'
                }}
              >
                {f.label}
              </button>
            ))}
          </div>

          {/* Notices List */}
          {loadingNotices ? (
            <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
              <RefreshCw size={28} className="animate-spin" style={{ margin: '0 auto 1rem', color: 'var(--accent-cyan)' }} />
              <p>Caricamento avvisi ufficiali Arriva in corso...</p>
            </div>
          ) : filteredNotices.length === 0 ? (
            <div style={{
              background: 'var(--bg-card)',
              border: '1px dashed var(--border-color)',
              borderRadius: '12px',
              padding: '2.5rem 1rem',
              textAlign: 'center',
              color: 'var(--text-muted)'
            }}>
              <CheckCircle2 size={32} style={{ color: 'var(--accent-green)', margin: '0 auto 0.75rem' }} />
              <h3 style={{ fontSize: '1rem', color: 'var(--text-main)', marginBottom: '0.25rem' }}>Nessun avviso trovato</h3>
              <p style={{ fontSize: '0.85rem' }}>
                {noticeSearch || noticesFilter !== 'all' 
                  ? 'Nessun comunicato corrisponde ai filtri selezionati.' 
                  : 'Nessuna deviazione o allerta attiva per l\'area selezionata.'}
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {filteredNotices.map((n) => {
                let badgeBg = 'rgba(6, 182, 212, 0.12)';
                let badgeBorder = 'rgba(6, 182, 212, 0.3)';
                let badgeColor = 'var(--accent-cyan)';
                let badgeText = 'Comunicato';

                if (n.type === 'strike') {
                  badgeBg = 'rgba(239, 68, 68, 0.15)';
                  badgeBorder = 'rgba(239, 68, 68, 0.4)';
                  badgeColor = 'var(--accent-red)';
                  badgeText = 'Sciopero';
                } else if (n.type === 'detour') {
                  badgeBg = 'rgba(245, 166, 35, 0.15)';
                  badgeBorder = 'rgba(245, 166, 35, 0.4)';
                  badgeColor = 'var(--accent-orange)';
                  badgeText = 'Deviazione';
                } else if (n.type === 'roadwork') {
                  badgeBg = 'rgba(168, 85, 247, 0.15)';
                  badgeBorder = 'rgba(168, 85, 247, 0.4)';
                  badgeColor = 'var(--accent-purple)';
                  badgeText = 'Lavori Stradali';
                }

                return (
                  <div
                    key={n.id}
                    onClick={() => setSelectedNotice(n)}
                    style={{
                      background: 'var(--bg-card)',
                      border: '1px solid var(--border-color)',
                      borderRadius: '12px',
                      padding: '1rem 1.25rem',
                      cursor: 'pointer',
                      transition: 'transform 0.15s ease, border-color 0.15s ease',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.5rem'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = 'var(--accent-cyan)';
                      e.currentTarget.style.transform = 'translateY(-2px)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = 'var(--border-color)';
                      e.currentTarget.style.transform = 'translateY(0)';
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                        <span style={{
                          fontSize: '0.7rem',
                          fontWeight: '700',
                          padding: '2px 8px',
                          borderRadius: '6px',
                          background: badgeBg,
                          border: `1px solid ${badgeBorder}`,
                          color: badgeColor,
                          textTransform: 'uppercase'
                        }}>
                          {badgeText}
                        </span>

                        {n.lines && n.lines.map(l => (
                          <span key={l} style={{
                            fontSize: '0.75rem',
                            fontWeight: 'bold',
                            padding: '2px 8px',
                            borderRadius: '6px',
                            background: 'rgba(255,255,255,0.06)',
                            border: '1px solid var(--border-color)',
                            color: 'var(--accent-orange)'
                          }}>
                            Linea {l}
                          </span>
                        ))}
                      </div>

                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {formatDate(n.date)}
                      </span>
                    </div>

                    <h4 style={{ fontSize: '0.95rem', fontWeight: '600', color: 'var(--text-main)', margin: '0.25rem 0 0 0', lineHeight: 1.35 }}>
                      {n.title}
                    </h4>

                    {n.excerpt && (
                      <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                        {n.excerpt}
                      </p>
                    )}

                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', marginTop: '0.25rem', gap: '4px', fontSize: '0.8rem', color: 'var(--accent-cyan)', fontWeight: '500' }}>
                      <span>Dettagli avviso</span>
                      <ChevronRight size={14} />
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Notice Detail Modal */}
          {selectedNotice && (
            <div style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0,0,0,0.7)',
              backdropFilter: 'blur(6px)',
              zIndex: 9999,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '1rem'
            }}>
              <div style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '16px',
                width: '100%',
                maxWidth: '650px',
                maxHeight: '85vh',
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
                boxShadow: '0 20px 40px rgba(0,0,0,0.5)'
              }}>
                <div style={{
                  padding: '1rem 1.25rem',
                  borderBottom: '1px solid var(--border-color)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  background: 'rgba(255,255,255,0.02)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <AlertTriangle size={18} style={{ color: 'var(--accent-orange)' }} />
                    <span style={{ fontWeight: '700', fontSize: '0.9rem', color: 'var(--text-main)' }}>
                      Comunicato Ufficiale Arriva
                    </span>
                  </div>
                  <button
                    onClick={() => setSelectedNotice(null)}
                    style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '4px' }}
                  >
                    <X size={20} />
                  </button>
                </div>

                <div style={{ padding: '1.25rem', overflowY: 'auto', flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Data pubblicazione: <strong>{formatDate(selectedNotice.date)}</strong>
                    </span>
                    {selectedNotice.lines && selectedNotice.lines.length > 0 && (
                      <div style={{ display: 'flex', gap: '4px' }}>
                        {selectedNotice.lines.map(l => (
                          <span key={l} style={{ fontSize: '0.75rem', fontWeight: 'bold', padding: '2px 8px', borderRadius: '6px', background: 'rgba(245,166,35,0.15)', color: 'var(--accent-orange)' }}>
                            Linea {l}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: 'var(--text-main)', marginBottom: '1rem', lineHeight: 1.4 }}>
                    {selectedNotice.title}
                  </h3>

                  {selectedNotice.content ? (
                    <div 
                      className="arriva-notice-html"
                      style={{ fontSize: '0.9rem', lineHeight: 1.6, color: 'var(--text-main)' }}
                      dangerouslySetInnerHTML={{ __html: selectedNotice.content }}
                    />
                  ) : (
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                      {selectedNotice.excerpt || 'Nessun dettaglio aggiuntivo nel testo del comunicato.'}
                    </p>
                  )}
                </div>

                <div style={{
                  padding: '0.75rem 1.25rem',
                  borderTop: '1px solid var(--border-color)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  background: 'rgba(255,255,255,0.02)'
                }}>
                  {selectedNotice.link && (
                    <a
                      href={selectedNotice.link}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        fontSize: '0.85rem',
                        color: 'var(--accent-cyan)',
                        textDecoration: 'none'
                      }}
                    >
                      <span>Vedi su portale Arriva</span>
                      <ExternalLink size={14} />
                    </a>
                  )}

                  <button
                    onClick={() => setSelectedNotice(null)}
                    style={{
                      background: 'var(--btn-bg)',
                      border: '1px solid var(--border-color)',
                      borderRadius: '8px',
                      padding: '6px 16px',
                      color: 'var(--text-main)',
                      fontSize: '0.85rem',
                      cursor: 'pointer'
                    }}
                  >
                    Chiudi
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-TAB 3: LINEE & ORARI PDF                                              */}
      {/* ========================================================================= */}
      {activeSubTab === 'lines' && (
        <div>
          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1rem', alignItems: 'center' }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                type="text"
                value={lineSearch}
                onChange={(e) => setLineSearch(e.target.value)}
                placeholder="Cerca linea o destinazione (es. 265, 101, Milano, Malpensa, Aosta, Ivrea)..."
                style={{
                  width: '100%',
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '10px',
                  padding: '9px 12px 9px 36px',
                  color: 'var(--text-main)',
                  fontSize: '0.85rem'
                }}
              />
              {lineSearch && (
                <X
                  size={16}
                  onClick={() => setLineSearch('')}
                  style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)', cursor: 'pointer' }}
                />
              )}
            </div>

            <button
              onClick={() => loadLines(selectedArea)}
              disabled={loadingLines}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '10px',
                padding: '9px 14px',
                color: 'var(--text-main)',
                fontSize: '0.85rem',
                cursor: loadingLines ? 'not-allowed' : 'pointer'
              }}
            >
              <RefreshCw size={14} className={loadingLines ? 'animate-spin' : ''} />
              <span>Ricarica</span>
            </button>
          </div>

          {/* Lines List */}
          {loadingLines ? (
            <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-muted)' }}>
              <RefreshCw size={28} className="animate-spin" style={{ margin: '0 auto 1rem', color: 'var(--accent-cyan)' }} />
              <p>Caricamento linee e prospetti orari PDF...</p>
            </div>
          ) : filteredLines.length === 0 ? (
            <div style={{
              background: 'var(--bg-card)',
              border: '1px dashed var(--border-color)',
              borderRadius: '12px',
              padding: '2.5rem 1rem',
              textAlign: 'center',
              color: 'var(--text-muted)'
            }}>
              <Bus size={32} style={{ color: 'var(--text-muted)', margin: '0 auto 0.75rem' }} />
              <h3 style={{ fontSize: '1rem', color: 'var(--text-main)', marginBottom: '0.25rem' }}>Nessuna linea trovata</h3>
              <p style={{ fontSize: '0.85rem' }}>Verifica il termine di ricerca inserito o l'area selezionata.</p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '0.75rem' }}>
              {filteredLines.map((line) => (
                <div
                  key={line.id}
                  style={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '12px',
                    padding: '1rem',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
                    gap: '0.75rem',
                    transition: 'border-color 0.15s ease'
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <span style={{
                        fontSize: '0.75rem',
                        fontWeight: '800',
                        padding: '2px 8px',
                        borderRadius: '6px',
                        background: 'rgba(8, 145, 178, 0.15)',
                        border: '1px solid rgba(8, 145, 178, 0.3)',
                        color: 'var(--accent-cyan)'
                      }}>
                        {line.code ? `Linea ${line.code}` : 'Autolinea'}
                      </span>

                      {line.internalCode && line.internalCode !== line.code && (
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                          Cod. {line.internalCode}
                        </span>
                      )}
                    </div>

                    <h4 style={{ fontSize: '0.9rem', fontWeight: '600', color: 'var(--text-main)', margin: 0, lineHeight: 1.35 }}>
                      {line.title}
                    </h4>
                  </div>

                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                    {line.timetablePdf ? (
                      <a
                        href={line.timetablePdf}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          flex: 1,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '6px',
                          padding: '6px 10px',
                          borderRadius: '6px',
                          background: 'rgba(245, 166, 35, 0.15)',
                          border: '1px solid rgba(245, 166, 35, 0.3)',
                          color: 'var(--accent-orange)',
                          fontSize: '0.75rem',
                          fontWeight: '600',
                          textDecoration: 'none'
                        }}
                      >
                        <FileText size={14} />
                        <span>Orario PDF</span>
                      </a>
                    ) : (
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', padding: '6px 0' }}>Orario su portale</span>
                    )}

                    {line.mapUrl && (
                      <a
                        href={line.mapUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '4px',
                          padding: '6px 10px',
                          borderRadius: '6px',
                          background: 'var(--btn-bg)',
                          border: '1px solid var(--border-color)',
                          color: 'var(--text-main)',
                          fontSize: '0.75rem',
                          textDecoration: 'none'
                        }}
                      >
                        <MapPin size={14} />
                        <span>Mappa</span>
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-TAB 4: APP & MYPAY                                                    */}
      {/* ========================================================================= */}
      {activeSubTab === 'mypay' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          
          <div style={{
            background: 'linear-gradient(135deg, rgba(8, 145, 178, 0.2) 0%, rgba(28, 28, 31, 0.8) 100%)',
            border: '1px solid var(--accent-cyan)',
            borderRadius: '16px',
            padding: '1.5rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
            boxShadow: '0 8px 30px rgba(8, 145, 178, 0.15)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div style={{
                width: '54px', height: '54px', borderRadius: '14px',
                background: '#0891b2',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: '#fff', boxShadow: '0 4px 14px rgba(8, 145, 178, 0.4)',
                flexShrink: 0
              }}>
                <Smartphone size={30} />
              </div>
              <div>
                <h3 style={{ fontSize: '1.15rem', fontWeight: '700', color: 'var(--text-main)', margin: '0 0 4px 0' }}>
                  Arriva MyPay
                </h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
                  App ufficiale Arriva per titoli di viaggio, tessere, borsellino elettronico e servizi di mobilità.
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              <button
                onClick={handleLaunchApp}
                disabled={launchingApp}
                style={{
                  flex: '1 1 200px',
                  background: 'linear-gradient(135deg, #f5a623 0%, #d97706 100%)',
                  border: 'none',
                  borderRadius: '10px',
                  padding: '12px 18px',
                  color: '#121214',
                  fontWeight: '700',
                  fontSize: '0.95rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  cursor: 'pointer',
                  boxShadow: '0 4px 15px rgba(245, 166, 35, 0.3)'
                }}
              >
                <Smartphone size={18} />
                <span>Apri App Arriva MyPay</span>
              </button>

              <a
                href={`${API_BASE}/api/download/arriva-mypay.apk`}
                download="Arriva_MyPay.apk"
                style={{
                  flex: '1 1 200px',
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '10px',
                  padding: '12px 18px',
                  color: 'var(--text-main)',
                  fontWeight: '600',
                  fontSize: '0.9rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  textDecoration: 'none'
                }}
              >
                <Download size={18} style={{ color: 'var(--accent-cyan)' }} />
                <span>Scarica APK Arriva MyPay (56 MB)</span>
              </a>
            </div>
          </div>

          {/* Quick Access Services Grid */}
          <h3 style={{ fontSize: '1rem', fontWeight: '700', color: 'var(--text-main)', margin: '0.5rem 0 0 0' }}>
            Servizi Online & Portali Arriva
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '0.75rem' }}>
            <a
              href="https://torino.arriva.it/orari-e-linee/"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '12px',
                padding: '1rem',
                textDecoration: 'none',
                color: 'inherit',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '0.75rem'
              }}
            >
              <Bus size={22} style={{ color: 'var(--accent-cyan)', marginTop: '2px', flexShrink: 0 }} />
              <div>
                <h4 style={{ fontSize: '0.9rem', fontWeight: '600', color: 'var(--text-main)', margin: '0 0 2px 0' }}>
                  Calcola Percorso & Fermate
                </h4>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
                  Trova linee e passaggi fermata sul portale Arriva.
                </p>
              </div>
            </a>

            <a
              href="https://torino.arriva.it/tariffe-e-abbonamenti/"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '12px',
                padding: '1rem',
                textDecoration: 'none',
                color: 'inherit',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '0.75rem'
              }}
            >
              <Sparkles size={22} style={{ color: 'var(--accent-orange)', marginTop: '2px', flexShrink: 0 }} />
              <div>
                <h4 style={{ fontSize: '0.9rem', fontWeight: '600', color: 'var(--text-main)', margin: '0 0 2px 0' }}>
                  Abbonamenti & BIP
                </h4>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
                  Rinnovo tessere e abbonamenti TPL Piemonte.
                </p>
              </div>
            </a>

            <a
              href="https://arriva.it"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '12px',
                padding: '1rem',
                textDecoration: 'none',
                color: 'inherit',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '0.75rem'
              }}
            >
              <ExternalLink size={22} style={{ color: 'var(--accent-purple)', marginTop: '2px', flexShrink: 0 }} />
              <div>
                <h4 style={{ fontSize: '0.9rem', fontWeight: '600', color: 'var(--text-main)', margin: '0 0 2px 0' }}>
                  Portale Nazionale Arriva.it
                </h4>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
                  Sito corporate, news nazionali e rete dei trasporti.
                </p>
              </div>
            </a>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-TAB 5: CONTATTI & INFO                                                */}
      {/* ========================================================================= */}
      {activeSubTab === 'info' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: '14px',
            padding: '1.25rem'
          }}>
            <h3 style={{ fontSize: '1rem', fontWeight: '700', color: 'var(--text-main)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Phone size={18} style={{ color: 'var(--accent-green)' }} />
              <span>Contatti Arriva Piemonte / Torino</span>
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.85rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '6px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Sede Arriva Italia - Torino</span>
                <span style={{ color: 'var(--text-main)', fontWeight: '600' }}>Strada del Portone 145/26, Grugliasco (TO)</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '6px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Call Center & Assistenza</span>
                <a href="tel:035289000" style={{ color: 'var(--accent-cyan)', textDecoration: 'none', fontWeight: '600' }}>035 28 90 00</a>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '6px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Biglietteria Autostazione Torino</span>
                <span style={{ color: 'var(--text-main)', fontWeight: '600' }}>Corso Vittorio Emanuele II 131/H</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '6px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Portale Reclami & Info</span>
                <a href="https://torino.arriva.it/contatti-e-assistenza/" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-cyan)', textDecoration: 'none', fontWeight: '600' }}>
                  Assistenza Online
                </a>
              </div>
            </div>
          </div>

          <div style={{
            background: 'rgba(6, 182, 212, 0.08)',
            border: '1px solid rgba(6, 182, 212, 0.25)',
            borderRadius: '14px',
            padding: '1.25rem'
          }}>
            <h3 style={{ fontSize: '0.95rem', fontWeight: '700', color: 'var(--accent-cyan)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <ShieldAlert size={18} />
              <span>Note Operative & Infomobilità</span>
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-main)', lineHeight: 1.5, margin: 0 }}>
              I dati degli avvisi di servizio e gli orari PDF ufficiali vengono aggiornati costantemente dal nostro server in tempo reale interrogando le sorgenti certificate Arriva Italia.
            </p>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* MODAL: TABELLARIO & LISTINO TARIFFE UFFICIALE                             */}
      {/* ========================================================================= */}
      {showFaresModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.75)',
          backdropFilter: 'blur(8px)',
          zIndex: 99999,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '1rem'
        }}>
          <div style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-color)',
            borderRadius: '18px',
            width: '100%',
            maxWidth: '750px',
            maxHeight: '90vh',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            boxShadow: '0 25px 50px rgba(0,0,0,0.6)'
          }}>
            {/* Modal Header */}
            <div style={{
              padding: '1rem 1.25rem',
              borderBottom: '1px solid var(--border-color)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              background: 'linear-gradient(135deg, rgba(8, 145, 178, 0.15) 0%, rgba(245, 166, 35, 0.1) 100%)'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BookOpen size={20} style={{ color: 'var(--accent-orange)' }} />
                <div>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: '700', color: 'var(--text-main)', margin: 0 }}>
                    Listino Tariffe Ufficiale Arriva & SAVDA
                  </h3>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0 }}>
                    Tutti i prezzi ufficiali in vigore per singole tratte, A/R e abbonamenti
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowFaresModal(false)}
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '4px' }}
              >
                <X size={20} />
              </button>
            </div>

            {/* Sub-tabs selector */}
            <div style={{
              display: 'flex',
              gap: '0.4rem',
              padding: '0.75rem 1.25rem',
              background: 'rgba(255,255,255,0.02)',
              borderBottom: '1px solid rgba(255,255,255,0.05)',
              overflowX: 'auto'
            }}>
              {[
                { id: 'airport', label: '✈️ Aeroporti (Malpensa & Caselle)' },
                { id: 'savda', label: '🏔️ SAVDA Valle d\'Aosta' },
                { id: 'bip', label: '🚌 Extraurbano BIP (Piemonte)' },
                { id: 'formula', label: '🎟️ Sistema Formula' }
              ].map(t => (
                <button
                  key={t.id}
                  onClick={() => setFaresModalTab(t.id)}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '8px',
                    fontSize: '0.8rem',
                    fontWeight: faresModalTab === t.id ? '700' : '500',
                    background: faresModalTab === t.id ? 'var(--accent-cyan)' : 'transparent',
                    color: faresModalTab === t.id ? '#121214' : 'var(--text-muted)',
                    border: faresModalTab === t.id ? '1px solid var(--accent-cyan)' : '1px solid var(--border-color)',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {/* Modal Body */}
            <div style={{ padding: '1.25rem', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              
              {/* TAB 1: AEROPORTI */}
              {faresModalTab === 'airport' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  
                  {/* Malpensa Express */}
                  <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(168, 85, 247, 0.3)', borderRadius: '12px', padding: '1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: '700', color: 'var(--accent-purple)' }}>
                        Linea 20 / Malpensa Express (Torino ↔ Malpensa T1/T2)
                      </span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Prenotazione posto garantito</span>
                    </div>

                    <table style={{ width: '100%', fontSize: '0.82rem', borderCollapse: 'collapse', color: 'var(--text-main)' }}>
                      <tbody>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '6px 0' }}>Corsa Semplice (da Torino Porta Susa / C.so G. Cesare)</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-green)' }}>22,00 €</td>
                        </tr>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '6px 0' }}>Andata e Ritorno A/R (valido 30 giorni)</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-orange)' }}>39,00 €</td>
                        </tr>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '6px 0' }}>Corsa Semplice da Chivasso / Carisio (Casello A4)</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-green)' }}>18,00 €</td>
                        </tr>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '6px 0' }}>Andata e Ritorno A/R da Chivasso / Carisio</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-orange)' }}>32,00 €</td>
                        </tr>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '6px 0' }}>Carnet 10 Corse (da Torino)</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700' }}>180,00 € (18 €/corsa)</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '6px 0' }}>Bambini (2-12 anni)</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700' }}>11,00 €</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  {/* Caselle Express */}
                  <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(6, 182, 212, 0.3)', borderRadius: '12px', padding: '1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: '700', color: 'var(--accent-cyan)' }}>
                        Linea 268 / Caselle Express (Torino Centro ↔ Aeroporto Caselle)
                      </span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Frequenza ogni 15-30 min</span>
                    </div>

                    <table style={{ width: '100%', fontSize: '0.82rem', borderCollapse: 'collapse', color: 'var(--text-main)' }}>
                      <tbody>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '6px 0' }}>Corsa Semplice (MyPay / Tabaccheria / Contactless a bordo)</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-green)' }}>7,50 €</td>
                        </tr>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '6px 0' }}>Andata e Ritorno A/R</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-orange)' }}>14,00 €</td>
                        </tr>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '6px 0' }}>Corsa Semplice con Torino+Piemonte Card</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-green)' }}>5,00 €</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '6px 0' }}>Acquisto a bordo in contanti dal conducente</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700' }}>8,00 €</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                </div>
              )}

              {/* TAB 2: SAVDA VALLE D'AOSTA */}
              {faresModalTab === 'savda' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  
                  {/* SAVDA Malpensa */}
                  <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '12px', padding: '1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: '700', color: 'var(--accent-green)' }}>
                        SAVDA Diretto: Milano Malpensa ↔ Valle d'Aosta
                      </span>
                    </div>

                    <table style={{ width: '100%', fontSize: '0.82rem', borderCollapse: 'collapse', color: 'var(--text-main)' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)' }}>
                          <th style={{ textAlign: 'left', padding: '4px 0' }}>Destinazione da Malpensa</th>
                          <th style={{ textAlign: 'right', padding: '4px 0' }}>Corsa Semplice</th>
                          <th style={{ textAlign: 'right', padding: '4px 0' }}>Andata & Ritorno (A/R)</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '6px 0' }}>Pont Saint Martin</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-green)' }}>15,00 €</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-orange)' }}>28,00 €</td>
                        </tr>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '6px 0' }}>Verrès</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-green)' }}>17,00 €</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-orange)' }}>31,00 €</td>
                        </tr>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '6px 0' }}>Châtillon / Saint-Vincent</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-green)' }}>19,00 €</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-orange)' }}>34,00 €</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '6px 0' }}>Aosta Autostazione (Piazza Manzetti)</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-green)' }}>20,00 €</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-orange)' }}>36,00 €</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                  {/* SAVDA Torino Linea 101 */}
                  <div style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(6, 182, 212, 0.3)', borderRadius: '12px', padding: '1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: '700', color: 'var(--accent-cyan)' }}>
                        SAVDA Linea 101: Torino ↔ Valle d'Aosta
                      </span>
                    </div>

                    <table style={{ width: '100%', fontSize: '0.82rem', borderCollapse: 'collapse', color: 'var(--text-main)' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)' }}>
                          <th style={{ textAlign: 'left', padding: '4px 0' }}>Destinazione da Torino</th>
                          <th style={{ textAlign: 'right', padding: '4px 0' }}>Corsa Semplice</th>
                          <th style={{ textAlign: 'right', padding: '4px 0' }}>Andata & Ritorno (A/R)</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '6px 0' }}>Pont Saint Martin</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-green)' }}>6,50 €</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-orange)' }}>12,00 €</td>
                        </tr>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '6px 0' }}>Verrès</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-green)' }}>8,20 €</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-orange)' }}>15,00 €</td>
                        </tr>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '6px 0' }}>Châtillon / Saint-Vincent</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-green)' }}>9,40 €</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-orange)' }}>17,50 €</td>
                        </tr>
                        <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                          <td style={{ padding: '6px 0' }}>Aosta Autostazione</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-green)' }}>10,70 €</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-orange)' }}>19,50 €</td>
                        </tr>
                        <tr>
                          <td style={{ padding: '6px 0' }}>Ivrea ↔ Aosta</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-green)' }}>7,20 €</td>
                          <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-orange)' }}>13,00 €</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>

                </div>
              )}

              {/* TAB 3: BIP EXTRAURBANO PIEMONTE */}
              {faresModalTab === 'bip' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
                    Tariffario chilometrico Regionale TPL Piemonte (Linee 275, 282, 260, 265, 310, 510 e provinciali):
                  </p>

                  <table style={{ width: '100%', fontSize: '0.82rem', borderCollapse: 'collapse', color: 'var(--text-main)' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)' }}>
                        <th style={{ textAlign: 'left', padding: '4px 0' }}>Fascia (Distanza km)</th>
                        <th style={{ textAlign: 'center', padding: '4px 0' }}>Corsa Semplice</th>
                        <th style={{ textAlign: 'right', padding: '4px 0' }}>Abbonamento Mensile</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[
                        { f: 'F1 (1 - 5 km)', cs: '1,70 €', m: '38,00 €' },
                        { f: 'F2 (5,1 - 10 km)', cs: '2,20 €', m: '47,00 €' },
                        { f: 'F3 (10,1 - 15 km)', cs: '2,60 €', m: '55,00 €' },
                        { f: 'F4 (15,1 - 20 km)', cs: '3,10 €', m: '63,00 €' },
                        { f: 'F5 (20,1 - 25 km)', cs: '3,50 €', m: '70,00 €' },
                        { f: 'F6 (25,1 - 30 km)', cs: '3,80 €', m: '76,00 €' },
                        { f: 'F7 (30,1 - 35 km - es. TO-Pinerolo)', cs: '4,60 €', m: '84,00 €' },
                        { f: 'F8 (35,1 - 40 km)', cs: '4,60 €', m: '89,00 €' },
                        { f: 'F9 (40,1 - 45 km)', cs: '5,10 €', m: '95,00 €' },
                        { f: 'F10 (45,1 - 50 km - es. TO-Perosa)', cs: '5,60 €', m: '101,00 €' },
                        { f: 'F11 (50,1 - 60 km - es. TO-Ivrea)', cs: '6,10 €', m: '108,00 €' },
                        { f: 'F12 (60,1 - 70 km)', cs: '6,80 €', m: '116,00 €' },
                        { f: 'F13 (70,1 - 80 km)', cs: '7,50 €', m: '124,00 €' },
                        { f: 'F14 (80,1 - 90 km - es. TO-Sestriere)', cs: '8,50 €', m: '133,00 €' },
                        { f: 'F15 (> 90 km)', cs: '9,50 €', m: '142,00 €' }
                      ].map((r, i) => (
                        <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                          <td style={{ padding: '5px 0' }}>{r.f}</td>
                          <td style={{ padding: '5px 0', textAlign: 'center', fontWeight: '700', color: 'var(--accent-green)' }}>{r.cs}</td>
                          <td style={{ padding: '5px 0', textAlign: 'right', fontWeight: '600' }}>{r.m}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* TAB 4: SISTEMA FORMULA */}
              {faresModalTab === 'formula' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
                    Tariffe integrate per viaggiare indistintamente su rete Arriva, GTT urbana/suburbana e treni SFM (Trenitalia):
                  </p>

                  <table style={{ width: '100%', fontSize: '0.82rem', borderCollapse: 'collapse', color: 'var(--text-main)' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: 'var(--text-muted)' }}>
                        <th style={{ textAlign: 'left', padding: '4px 0' }}>Tipologia Titolo Formula</th>
                        <th style={{ textAlign: 'center', padding: '4px 0' }}>Validità</th>
                        <th style={{ textAlign: 'right', padding: '4px 0' }}>Prezzo Corsa</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                        <td style={{ padding: '6px 0' }}>City / Formula U (Torino Urbano)</td>
                        <td style={{ padding: '6px 0', textAlign: 'center' }}>100 min</td>
                        <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-green)' }}>2,00 €</td>
                      </tr>
                      <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                        <td style={{ padding: '6px 0' }}>Formula 1 (Zona U + 1 Zona adiacente)</td>
                        <td style={{ padding: '6px 0', textAlign: 'center' }}>120 min</td>
                        <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-green)' }}>2,50 €</td>
                      </tr>
                      <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                        <td style={{ padding: '6px 0' }}>Formula 2 (Zona U + 2 Zone)</td>
                        <td style={{ padding: '6px 0', textAlign: 'center' }}>150 min</td>
                        <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-green)' }}>3,20 €</td>
                      </tr>
                      <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                        <td style={{ padding: '6px 0' }}>Formula 3 (es. Torino + Pinerolo)</td>
                        <td style={{ padding: '6px 0', textAlign: 'center' }}>180 min</td>
                        <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-green)' }}>4,30 €</td>
                      </tr>
                      <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                        <td style={{ padding: '6px 0' }}>Formula 4 (Zone U + 4 Zone)</td>
                        <td style={{ padding: '6px 0', textAlign: 'center' }}>210 min</td>
                        <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-green)' }}>5,30 €</td>
                      </tr>
                      <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                        <td style={{ padding: '6px 0' }}>Daily U (Giornaliero Rete Urbana Torino)</td>
                        <td style={{ padding: '6px 0', textAlign: 'center' }}>Fino a fine servizio</td>
                        <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-cyan)' }}>4,50 €</td>
                      </tr>
                      <tr>
                        <td style={{ padding: '6px 0' }}>MultiDaily 7 (7 Giornalieri)</td>
                        <td style={{ padding: '6px 0', textAlign: 'center' }}>7 giorni a scelta</td>
                        <td style={{ padding: '6px 0', textAlign: 'right', fontWeight: '700', color: 'var(--accent-orange)' }}>21,00 €</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              )}

            </div>

            {/* Modal Footer */}
            <div style={{
              padding: '0.75rem 1.25rem',
              borderTop: '1px solid var(--border-color)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              background: 'rgba(255,255,255,0.02)'
            }}>
              <a
                href="https://torino.arriva.it/tariffe-e-abbonamenti/"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '0.85rem',
                  color: 'var(--accent-cyan)',
                  textDecoration: 'none'
                }}
              >
                <span>Portale Ufficiale Tariffe Arriva.it</span>
                <ExternalLink size={14} />
              </a>

              <button
                type="button"
                onClick={() => setShowFaresModal(false)}
                style={{
                  background: 'var(--btn-bg)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  padding: '6px 16px',
                  color: 'var(--text-main)',
                  fontSize: '0.85rem',
                  cursor: 'pointer'
                }}
              >
                Chiudi
              </button>
            </div>

          </div>
        </div>
      )}

      {/* Floating Toast Notification */}
      {toastMessage && (
        <div style={{
          position: 'fixed',
          bottom: '24px',
          left: '50%',
          transform: 'translateX(-50%)',
          background: '#18181b',
          color: '#fff',
          border: '1px solid #10b981',
          borderRadius: '10px',
          padding: '10px 18px',
          fontSize: '0.82rem',
          fontWeight: '600',
          boxShadow: '0 8px 24px rgba(0,0,0,0.6)',
          zIndex: 99999,
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          pointerEvents: 'none'
        }}>
          <CheckCircle2 size={16} style={{ color: '#10b981' }} />
          <span>{toastMessage}</span>
        </div>
      )}

    </div>
  );
}
