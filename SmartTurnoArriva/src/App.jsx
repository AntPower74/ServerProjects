import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import Papa from 'papaparse';
import { Capacitor } from '@capacitor/core';
import { LocalNotifications } from '@capacitor/local-notifications';
import { Badge } from '@capawesome/capacitor-badge';
import { Calendar, Clock, AlertTriangle, User, Activity, Search as SearchIcon, ChevronDown, MapPin, FileText, Settings, Sun, Moon, Bell, BellOff, Bus } from 'lucide-react';
import SearchTrips from './components/SearchTrips';
import OrarioCorse from './components/OrarioCorse';
import Cartellini from './components/Cartellini';
import AdminPanel from './components/AdminPanel';
import UpdateBanner from './components/UpdateBanner';
import SmartTurnoHome from './components/SmartTurnoHome';
import ArrivaServices from './components/ArrivaServices';
import TodayShiftModal from './components/TodayShiftModal';
import { ADMIN_EMAIL, AUTH_STORAGE_KEY, API_BASE } from './config.js';

// Serviti dalla cache del nostro server (aggiornata ogni 5 min lato server,
// vedi vite.config.js) invece che da Google Sheets direttamente: prima
// ogni apertura app aspettava 10-12s la risposta di Google.
const CSV_URL = `${API_BASE}/api/data/csv`;
const LEGEND_URL = `${API_BASE}/api/data/legend`;
const ORARI_URL = `${API_BASE}/api/data/orari`;

const getMondayOfCurrentWeek = () => {
  const t = new Date();
  const day = t.getDay();
  const diff = t.getDate() - day + (day === 0 ? -6 : 1);
  const monday = new Date(t.getFullYear(), t.getMonth(), diff);
  monday.setHours(0, 0, 0, 0);
  return monday;
};

const parseItalianDate = (dateStr) => {
  const mesi = { "gen": 0, "feb": 1, "mar": 2, "apr": 3, "mag": 4, "giu": 5, "lug": 6, "ago": 7, "set": 8, "ott": 9, "nov": 10, "dic": 11 };
  const parts = dateStr.split(" ");
  if (parts.length >= 4) {
    const day = parseInt(parts[1], 10);
    const month = mesi[parts[2].toLowerCase()];
    const year = parseInt("20" + parts[3], 10);
    if (!isNaN(day) && month !== undefined && !isNaN(year)) {
      return new Date(year, month, day);
    }
  }
  return new Date(0);
};

// Stessa logica di lookup usata nel rendering della timeline (vedi piu' sotto),
// estratta qui per essere riusata anche nel calcolo delle notifiche.
const getOrarioText = (turno, periodo, lowerDate, orariTurni) => {
  if (!orariTurni[turno]) return "-";
  const periodoLower = periodo ? periodo.toLowerCase() : "";
  const isFestivo = lowerDate.includes("dom") || periodoLower.includes("festivo") || periodoLower.includes("domenica") || turno === "RF";

  let periodoKey = "Non Scolastico";
  if (periodoLower.includes("scolastico") && !periodoLower.includes("non scolastico")) {
    periodoKey = "Scolastico";
  } else if (periodoLower.includes("non scol")) {
    periodoKey = "Non Scolastico";
  } else if (periodoLower.includes("agosto")) {
    periodoKey = "Agosto";
  }

  if (isFestivo) periodoKey = "Festivo Infrasettimanale";
  else if (lowerDate.includes("sab") && periodoLower.includes("scolastico") && !periodoLower.includes("non scolastico")) periodoKey = "Sabato SCOL";
  else if (lowerDate.includes("sab") && periodoLower.includes("non scolastico")) periodoKey = "Sabato Non SCOL";
  else if (lowerDate.includes("dom")) periodoKey = "Domenica";

  return orariTurni[turno][periodoKey] || orariTurni[turno]["Scolastico"] || orariTurni[turno]["Non Scolastico"] || "-";
};

function App() {
  const [activeTab, setActiveTab] = useState('shifts'); // 'shifts' or 'search'
  const [data, setData] = useState([]);
  const [drivers, setDrivers] = useState([]);
  const [selectedDriver, setSelectedDriver] = useState("");
  const [selectedYear, setSelectedYear] = useState(() => {
    return localStorage.getItem("shiftlink_saved_year") || "";
  });
  const [selectedMonth, setSelectedMonth] = useState(() => {
    return localStorage.getItem("shiftlink_saved_month_only") || "Tutti";
  });
  const [selectedDepot, setSelectedDepot] = useState(() => {
    let saved = localStorage.getItem("shiftlink_saved_depot") || "Tutti";
    if (saved === "Torino") saved = "Torino TPL";
    return saved;
  });
  const [viewMode, setViewMode] = useState(() => {
    return localStorage.getItem("shiftlink_view_mode") || "today";
  });
  const [legend, setLegend] = useState({});
  const [orariTurni, setOrariTurni] = useState({});
  const [loading, setLoading] = useState(true);
  const [introDone, setIntroDone] = useState(false);
  const handleIntroFinish = useCallback(() => setIntroDone(true), []);
  const [error, setError] = useState(null);
  const [periodoIndex, setPeriodoIndex] = useState(-1);
  const [lastUpdate, setLastUpdate] = useState("");
  const [theme, setTheme] = useState(() => localStorage.getItem('smartturno_theme') || 'dark');
  const [arrivaNoticesCount, setArrivaNoticesCount] = useState(0);
  const [isTodayShiftModalOpen, setIsTodayShiftModalOpen] = useState(false);
  const [modalTurnoCode, setModalTurnoCode] = useState('');
  const [hasAutoOpenedToday, setHasAutoOpenedToday] = useState(false);

  // In dark mode i bordi colorati delle celle vengono attenuati (alpha piu'
  // basso) cosi' l'anello attorno al turno risulta piu' sottile alla vista
  // sul sfondo scuro; in chiaro restano a piena saturazione.
  const cellBorderColors = theme === 'dark'
    ? { festivo: 'rgba(239, 68, 68, 0.45)', sabato: 'rgba(59, 130, 246, 0.45)', nonScolastico: 'rgba(74, 222, 128, 0.4)', scolastico: 'rgba(253, 224, 71, 0.4)' }
    : { festivo: '#dc2626', sabato: '#2563eb', nonScolastico: '#16a34a', scolastico: '#d97706' };

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('smartturno_theme', theme);
  }, [theme]);

  const [notifEnabled, setNotifEnabled] = useState(() => localStorage.getItem('smartturno_notif_enabled') === '1');
  const [notifBusy, setNotifBusy] = useState(false);
  const [notifOffset, setNotifOffset] = useState(() => parseInt(localStorage.getItem('smartturno_notif_offset')) || 60);
  const [isNotifMenuOpen, setIsNotifMenuOpen] = useState(false);

  useEffect(() => {
    localStorage.setItem('smartturno_notif_enabled', notifEnabled ? '1' : '0');
  }, [notifEnabled]);

  useEffect(() => {
    localStorage.setItem('smartturno_notif_offset', notifOffset.toString());
  }, [notifOffset]);

  const getOffsetLabel = (mins) => {
    if (mins === 60) return "1 ora";
    if (mins === 120) return "2 ore";
    if (mins > 60 && mins < 120) return `1 ora e ${mins - 60} min`;
    return `${mins} minuti`;
  };

  const notifOptions = Array.from({length: 24}, (_, i) => (i + 1) * 5);

  const [searchTerm, setSearchTerm] = useState("");
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const [showAdmin, setShowAdmin] = useState(false);
  const isAdmin = localStorage.getItem(AUTH_STORAGE_KEY) === ADMIN_EMAIL;

  // Auto-aggiornamento: controlla ogni 2 minuti se il server è stato aggiornato
  useEffect(() => {
    let currentVersion = null;
    const checkVersion = () => {
      fetch('/version', { cache: 'no-store' })
        .then(r => r.json())
        .then(({ v }) => {
          if (currentVersion === null) { currentVersion = v; return; }
          if (v !== currentVersion) { window.location.reload(); }
        })
        .catch(() => {}); // ignora errori di rete
    };
    checkVersion();
    const interval = setInterval(checkVersion, 2 * 60 * 1000); // ogni 2 minuti
    return () => clearInterval(interval);
  }, []);


  useEffect(() => {
    if (selectedDriver) setSearchTerm(selectedDriver);
  }, [selectedDriver]);

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
        setSearchTerm(selectedDriver);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [selectedDriver]);

  useEffect(() => {
    const fetchWithTimeout = (url, label, ms = 15000) => {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), ms);
      return fetch(url, { signal: controller.signal })
        .then(res => { clearTimeout(timer); if (!res.ok) throw new Error(`Errore network ${label}`); return res.text(); })
        .catch(err => { clearTimeout(timer); throw new Error(err.name === 'AbortError' ? `Timeout: ${label} non risponde` : err.message); });
    };

    Promise.all([
      fetchWithTimeout(CSV_URL, 'CSV Turni'),
      fetchWithTimeout(LEGEND_URL, 'Legenda'),
      fetchWithTimeout(ORARI_URL, 'Orari Turni'),
    ]).then(([csvText, legendText, orariText]) => {
      // Parse legend
      Papa.parse(legendText, {
        header: false,
        skipEmptyLines: true,
        complete: (results) => {
          const legendMap = {};
          results.data.forEach((row, index) => {
            if (index > 0) { // Skip header
              const turnoCode = row[0]?.trim();
              if (turnoCode) {
                if (!legendMap[turnoCode]) {
                  legendMap[turnoCode] = { nome: row[1]?.trim() || "", trips: [] };
                }
                if (row[5] && row[7]) { // partenza e arrivo
                  legendMap[turnoCode].trips.push({
                    partenza: row[5],
                    arrivo: row[7],
                    da: row[2],
                    a: row[4],
                    linea: row[3]
                  });
                }
              }
            }
          });
          setLegend(legendMap);
        },
      });

      // Parse orari turni
      Papa.parse(orariText, {
        header: true,
        skipEmptyLines: true,
        complete: (results) => {
          const orariMap = {};
          results.data.forEach(row => {
            const turnoCode = row["Turno"]?.trim();
            if (turnoCode) {
              orariMap[turnoCode] = row;
            }
          });
          setOrariTurni(orariMap);
        }
      });

      // Parse main data
      Papa.parse(csvText, {
        skipEmptyLines: true,
        complete: (results) => {
          const rows = results.data;
          if (rows.length < 2) {
            setError("Il file CSV è vuoto o non valido.");
            setLoading(false);
            return;
          }

          const headers = rows[0];
          setPeriodoIndex(headers.findIndex(h => h && h.trim() === "Periodo"));
          const extractedDrivers = [];
          let driverStartIndex = 11;
          
          for (let i = driverStartIndex; i < headers.length; i++) {
            const header = headers[i]?.trim();
            if (header === "RIGA Rotazione" || header === "Periodo" || header === "Scolastico") break;
            if (header && header !== "" && !header.startsWith("(0") && header !== "Merlo" && header !== "Vassallo") {
              const depotCounts = { pe:0, su:0, ca:0, pb:0, to:0, pi:0, pt:0, lu:0 };
              for (let r = 2; r < rows.length; r++) {
                 const turno = (rows[r] && rows[r][i] ? rows[r][i] : "").trim().toLowerCase();
                 if (!turno) continue;
                 if (turno.startsWith("pe")) depotCounts.pe++;
                 else if (turno.startsWith("su")) depotCounts.su++;
                 else if (turno.startsWith("ca")) depotCounts.ca++;
                 else if (turno.startsWith("pb")) depotCounts.pb++;
                 else if (turno.startsWith("to")) depotCounts.to++;
                 else if (turno.startsWith("pi")) depotCounts.pi++;
                 else if (turno.startsWith("pt")) depotCounts.pt++;
                 else if (turno.startsWith("lu")) depotCounts.lu++;
              }
              let maxDepot = "altro";
              let maxCount = 0;
              for (const [dep, count] of Object.entries(depotCounts)) {
                 if (count > maxCount) { maxCount = count; maxDepot = dep; }
              }
              const depotNames = {
                pe: "Perosa", su: "Susa", ca: "Caselle", pb: "Piobesi",
                to: "Torino TPL", pi: "Pinerolo", pt: "Pont", lu: "Luserna", altro: "Altro"
              };
              
              let finalDepot = depotNames[maxDepot];
              if (maxDepot === "to") {
                 const malpensaDrivers = [
                   "Potenza", "D'Agostino", "Favara", "Stabile", "Giambrone",
                   "Pozzi", "Actis Grosso", "Lamonaca", "Sibona", "La Monica",
                   "Marongiu", "Pizzolla", "Petrilli"
                 ];
                 const isMalpensa = malpensaDrivers.some(md => header.toLowerCase().includes(md.toLowerCase()));
                 if (isMalpensa) finalDepot = "Torino Malpensa";
              }
              
              extractedDrivers.push({ name: header, index: i, depot: finalDepot });
            }
          }

          extractedDrivers.sort((a, b) => a.name.localeCompare(b.name));

          setData(rows.slice(2)); 
          setDrivers(extractedDrivers);
          const savedEmail = localStorage.getItem(AUTH_STORAGE_KEY) || "";
          const savedDriver = localStorage.getItem("shiftlink_saved_driver");
          let initialDriver = null;
          if (savedDriver && extractedDrivers.some(d => d.name === savedDriver)) {
            initialDriver = extractedDrivers.find(d => d.name === savedDriver);
          } else if (savedEmail) {
            const emailPrefix = savedEmail.split("@")[0].toLowerCase().replace(/[^a-z0-9]/g, " ");
            const emailParts = emailPrefix.split(/\s+/).filter(Boolean);
            initialDriver = extractedDrivers.find(d => {
              const dLower = d.name.toLowerCase();
              return emailParts.some(part => part.length >= 3 && dLower.includes(part));
            });
          }
          if (!initialDriver && extractedDrivers.length > 0) {
            initialDriver = extractedDrivers[0];
          }
          if (initialDriver) {
            setSelectedDriver(initialDriver.name);
            setSelectedDepot(initialDriver.depot);
            localStorage.setItem("shiftlink_saved_driver", initialDriver.name);
          }
          const now = new Date();
          setLastUpdate(now.toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' }) + " del " + now.toLocaleDateString('it-IT'));
          setLoading(false);
        },
      });
    }).catch((error) => {
      console.error("Error fetching data:", error);
      setError("Impossibile caricare i dati dal foglio Google.");
      setLoading(false);
    });
  }, []);

  const selectedDriverObj = drivers.find(d => d.name === selectedDriver);
  const driverColIndex = selectedDriverObj ? selectedDriverObj.index : -1;

  const processedShifts = data.map(row => {
    const date = row[0] || "";
    const turno = driverColIndex !== -1 ? (row[driverColIndex] || "").trim() : "";
    const periodo = periodoIndex !== -1 ? (row[periodoIndex] || "").toLowerCase() : "";
    return { date, turno, periodo };
  }).filter(s => s.date && s.turno);

  const todayShiftInfo = useMemo(() => {
    const mesi = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"];
    const today = new Date();
    const todayDay = today.getDate().toString();
    const todayMonth = mesi[today.getMonth()];
    const todayYear = today.getFullYear().toString().slice(-2);

    const found = processedShifts.find(shift => {
      const dParts = shift.date.split(" ");
      if (dParts.length >= 4) {
        const dDay = parseInt(dParts[1], 10).toString();
        const dMonth = dParts[2].toLowerCase();
        const dYear = dParts[3];
        return dDay === todayDay && dMonth === todayMonth && dYear === todayYear;
      }
      return false;
    });

    const formattedDate = `${today.getDate()} ${todayMonth.toUpperCase()} 20${todayYear}`;
    return {
      turno: found?.turno || '',
      dateStr: found?.date || formattedDate
    };
  }, [processedShifts]);

  // Prossimi turni (max 30 giorni) con un orario di inizio valido, usati per
  // programmare le notifiche locali "un'ora prima". Dipende solo da stato
  // stabile (data/orariTurni/driverColIndex/periodoIndex) e non da
  // processedShifts, che e' un nuovo array ad ogni render e romperebbe la
  // memoizzazione facendo ripartire lo scheduling in continuazione.
  const upcomingShiftNotifications = useMemo(() => {
    if (driverColIndex === -1) return [];
    const now = new Date();
    const todayMidnight = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const results = [];
    for (const row of data) {
      const date = row[0] || "";
      const turno = (row[driverColIndex] || "").trim();
      if (!date || !turno) continue;
      const periodo = periodoIndex !== -1 ? (row[periodoIndex] || "").toLowerCase() : "";

      const shiftDate = parseItalianDate(date);
      const diffDays = (shiftDate - todayMidnight) / 86400000;
      if (diffDays < 0 || diffDays > 30) continue;

      const orarioText = getOrarioText(turno, periodo, date.toLowerCase(), orariTurni);
      const match = /^(\d{2}):(\d{2})/.exec(orarioText || "");
      if (!match) continue; // riposo / non disponibile / orario mancante

      const startDate = new Date(shiftDate.getFullYear(), shiftDate.getMonth(), shiftDate.getDate(), parseInt(match[1], 10), parseInt(match[2], 10));
      const notifyDate = new Date(startDate.getTime() - notifOffset * 60 * 1000);
      if (notifyDate <= now) continue;

      const id = shiftDate.getFullYear() * 10000 + (shiftDate.getMonth() + 1) * 100 + shiftDate.getDate();
      results.push({
        id,
        title: `Turno ${turno} tra ${getOffsetLabel(notifOffset)}`,
        turnoCode: turno,
        body: `Inizio alle ${orarioText}`,
        schedule: { at: notifyDate, allowWhileIdle: true },
        startDate: startDate
      });
    }
    return results;
  }, [data, driverColIndex, periodoIndex, orariTurni, notifOffset]);

  useEffect(() => {
    if (!Capacitor.isNativePlatform()) return;
    let cancelled = false;
    (async () => {
      try {
        const { notifications: pending } = await LocalNotifications.getPending();
        if (pending.length) {
          await LocalNotifications.cancel({ notifications: pending.map(n => ({ id: n.id })) });
        }
        if (cancelled || !notifEnabled || upcomingShiftNotifications.length === 0) return;
        await LocalNotifications.schedule({ notifications: upcomingShiftNotifications });
      } catch (e) {
        console.error("Errore scheduling notifiche", e);
      }
    })();
    return () => { cancelled = true; };
  }, [notifEnabled, upcomingShiftNotifications]);

  // Numerino sull'icona dell'app: rispecchia sempre il numero di notifiche
  // turno ancora presenti (non lette/non scartate) nella tendina di sistema,
  // cosi' non serve tenere un contatore manuale separato da resincronizzare.
  useEffect(() => {
    if (!Capacitor.isNativePlatform()) return;
    const syncBadge = async () => {
      try {
        const { isSupported } = await Badge.isSupported();
        if (!isSupported) return;
        const { notifications } = await LocalNotifications.getDeliveredNotifications();
        await Badge.set({ count: notifications.length });
      } catch (e) {
        console.error("Errore sync badge", e);
      }
    };
    syncBadge();
    let listenerHandle;
    LocalNotifications.addListener('localNotificationReceived', syncBadge).then(h => { listenerHandle = h; });
    const onVisible = () => { if (document.visibilityState === 'visible') syncBadge(); };
    document.addEventListener('visibilitychange', onVisible);
    return () => {
      document.removeEventListener('visibilitychange', onVisible);
      if (listenerHandle) listenerHandle.remove();
    };
  }, []);

  const downloadICS = (shifts, offsetMins) => {
    if (shifts.length === 0) {
      alert("Non ci sono turni imminenti (nei prossimi 30 giorni) da esportare nel calendario.");
      return;
    }
    let icsContent = "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//SmartTurnoArriva//IT\r\n";
    
    shifts.forEach(shift => {
      if (!shift.startDate) return;
      const sd = shift.startDate;
      const ed = new Date(sd.getTime() + 6 * 60 * 60 * 1000);

      const formatICSDate = (d) => {
        return d.getUTCFullYear() +
          String(d.getUTCMonth() + 1).padStart(2, '0') +
          String(d.getUTCDate()).padStart(2, '0') + 'T' +
          String(d.getUTCHours()).padStart(2, '0') +
          String(d.getUTCMinutes()).padStart(2, '0') +
          String(d.getUTCSeconds()).padStart(2, '0') + 'Z';
      };

      const dtstart = formatICSDate(sd);
      const dtend = formatICSDate(ed);
      const dtstamp = formatICSDate(new Date());

      icsContent += "BEGIN:VEVENT\r\n";
      icsContent += `UID:smartturno-${shift.id}@smartturno\r\n`;
      icsContent += `DTSTAMP:${dtstamp}\r\n`;
      icsContent += `DTSTART:${dtstart}\r\n`;
      icsContent += `DTEND:${dtend}\r\n`;
      icsContent += `SUMMARY:Turno ${shift.turnoCode}\r\n`;
      icsContent += `DESCRIPTION:${shift.body}\r\n`;
      icsContent += "BEGIN:VALARM\r\n";
      icsContent += "ACTION:DISPLAY\r\n";
      icsContent += `DESCRIPTION:Promemoria Turno\r\n`;
      icsContent += `TRIGGER:-PT${offsetMins}M\r\n`;
      icsContent += "END:VALARM\r\n";
      icsContent += "END:VEVENT\r\n";
    });
    
    icsContent += "END:VCALENDAR";

    const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = "turni_smartturno.ics";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const enableNotifications = async () => {
    if (!Capacitor.isNativePlatform()) {
      alert("Stai usando l'app dal browser web. Verrà scaricato un file per aggiungere i turni al Calendario (iPhone/iPad/PC) con le relative notifiche.");
      downloadICS(upcomingShiftNotifications, notifOffset);
      setNotifEnabled(true);
      return;
    }
    setNotifBusy(true);
    try {
      const current = await LocalNotifications.checkPermissions();
      let granted = current.display === 'granted';
      if (!granted) {
        const req = await LocalNotifications.requestPermissions();
        granted = req.display === 'granted';
      }
      if (!granted) {
        alert("Permesso notifiche negato. Abilitalo dalle impostazioni Android dell'app per ricevere l'avviso prima del turno.");
        return;
      }
      try { await Badge.requestPermissions(); } catch {} // opzionale: non tutti i launcher lo richiedono
      setNotifEnabled(true);
    } finally {
      setNotifBusy(false);
    }
  };

  const allYears = Array.from(new Set(processedShifts.map(s => {
    const parts = s.date.split(" ");
    if (parts.length >= 4) return `20${parts[3]}`;
    return "";
  }).filter(Boolean)));

  const allMonths = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"];

  useEffect(() => {
    if (allYears.length > 0 && !selectedYear && selectedYear !== "Tutti") {
      const defaultYear = allYears[0];
      setSelectedYear(defaultYear);
      localStorage.setItem("shiftlink_saved_year", defaultYear);
    }
  }, [allYears, selectedYear]);

  const filteredShifts = useMemo(() => {
    return processedShifts.filter(s => {
      const parts = s.date.split(" ");
      if (parts.length < 4) return false;
      const sMonth = parts[2];
      const sYear = `20${parts[3]}`;
      
      const matchYear = selectedYear === "Tutti" || sYear === selectedYear;
      const matchMonth = selectedMonth === "Tutti" || sMonth === selectedMonth;
      
      if (selectedYear === "Tutti" && selectedMonth === "Tutti") {
         const shiftDate = parseItalianDate(s.date);
         return shiftDate >= getMondayOfCurrentWeek();
      }
      
      return matchYear && matchMonth;
    }).slice(0, (selectedYear === "Tutti" && selectedMonth === "Tutti") ? 31 : undefined);
  }, [processedShifts, selectedYear, selectedMonth]);

  const filteredDrivers = useMemo(() => {
    return selectedDepot === "Tutti" ? drivers : drivers.filter(d => d.depot === selectedDepot);
  }, [drivers, selectedDepot]);

  const filteredRawRows = useMemo(() => {
    return data.filter(row => {
      const parts = (row[0]||"").split(" ");
      if (parts.length < 4) return false;
      const sMonth = parts[2];
      const sYear = `20${parts[3]}`;
      
      const matchYear = selectedYear === "Tutti" || sYear === selectedYear;
      const matchMonth = selectedMonth === "Tutti" || sMonth === selectedMonth;
      
      if (selectedYear === "Tutti" && selectedMonth === "Tutti") {
         if (!row[0]) return false;
         const shiftDate = parseItalianDate(row[0]);
         return shiftDate >= getMondayOfCurrentWeek();
      }
      
      return matchYear && matchMonth;
    }).slice(0, (selectedYear === "Tutti" && selectedMonth === "Tutti") ? 31 : undefined);
  }, [data, selectedYear, selectedMonth]);

  if (loading || !introDone) {
    return <SmartTurnoHome onFinish={handleIntroFinish} />;
  }

  if (error) {
    return (
      <div className="loading-container" style={{color: 'var(--accent-red)'}}>
        <AlertTriangle size={32} style={{marginRight: '0.5rem'}}/> {error}
      </div>
    );
  }
  return (
    <div className="app-container">
      <div className="app-fade-in">
      <div className="header">
        <div className="header-title-container">
          <div className="header-logo">
            <img src="/icon-512.png" alt="" className="header-logo-img" />
            SmartTurnoArriva
          </div>

          <button
            type="button"
            className="theme-toggle-btn"
            onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
            title={theme === 'dark' ? 'Passa al tema chiaro' : 'Passa al tema scuro'}
          >
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </button>

          <div style={{ position: 'absolute', top: 'env(safe-area-inset-top, 0px)', right: '44px', zIndex: 20 }}>
            <button
              type="button"
              className={`theme-toggle-btn ${notifEnabled ? 'is-active' : ''}`}
              style={{ position: 'relative', top: 'auto', right: 'auto', zIndex: 'auto' }}
              onClick={() => setIsNotifMenuOpen(!isNotifMenuOpen)}
              disabled={notifBusy}
              title={notifEnabled ? `Notifiche attive: avviso ${getOffsetLabel(notifOffset)} prima` : "Attiva notifiche"}
            >
              {notifEnabled ? <Bell size={18} /> : <BellOff size={18} />}
            </button>
            {isNotifMenuOpen && (
              <div className="notif-dropdown" style={{ position: 'absolute', top: '100%', right: 0, marginTop: '0.5rem', background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px', zIndex: 100, minWidth: '180px', boxShadow: '0 4px 12px rgba(0,0,0,0.5)', overflowY: 'auto', maxHeight: '300px' }}>
                {!notifEnabled ? (
                  <>
                    <div style={{ padding: '0.75rem 1rem', fontSize: '0.85rem', color: 'var(--text-muted)', borderBottom: '1px solid var(--border-color)', fontWeight: 'bold' }}>Attiva avviso prima:</div>
                    {notifOptions.map(mins => (
                      <div key={mins} onClick={() => { setNotifOffset(mins); enableNotifications(); setIsNotifMenuOpen(false); }} style={{ padding: '0.75rem 1rem', cursor: 'pointer', borderBottom: '1px solid rgba(255,255,255,0.05)' }} className="notif-menu-item">
                        {getOffsetLabel(mins)}
                      </div>
                    ))}
                  </>
                ) : (
                  <>
                    <div onClick={() => {
                      setNotifEnabled(false);
                      setIsNotifMenuOpen(false);
                      if (!Capacitor.isNativePlatform()) {
                        alert("Icona disattivata. Ricorda però che i turni esportati nel Calendario vanno rimossi manualmente dall'app Calendario.");
                      }
                    }} style={{ padding: '0.75rem 1rem', cursor: 'pointer', color: 'var(--accent-red)', borderBottom: '1px solid var(--border-color)', fontWeight: 'bold' }} className="notif-menu-item">
                      Disattiva notifiche
                    </div>
                    <div style={{ padding: '0.75rem 1rem', fontSize: '0.85rem', color: 'var(--text-muted)', borderBottom: '1px solid var(--border-color)', fontWeight: 'bold' }}>Modifica preavviso:</div>
                    {notifOptions.map(mins => (
                      <div key={mins} onClick={() => { setNotifOffset(mins); setIsNotifMenuOpen(false); }} style={{ padding: '0.75rem 1rem', cursor: 'pointer', background: notifOffset === mins ? 'rgba(56, 189, 248, 0.15)' : 'transparent', color: notifOffset === mins ? 'var(--accent-cyan)' : 'inherit', borderBottom: '1px solid rgba(255,255,255,0.05)' }} className="notif-menu-item">
                        {getOffsetLabel(mins)} {notifOffset === mins && '✓'}
                      </div>
                    ))}
                  </>
                )}
              </div>
            )}
          </div>

          {activeTab === 'search' && <SearchTrips />}
          {activeTab === 'orariocorse' && <OrarioCorse />}
          {activeTab === 'cartellini' && <Cartellini />}
          {activeTab === 'arriva' && <ArrivaServices onNoticeCountUpdate={setArrivaNoticesCount} />}

          {activeTab === 'shifts' && (
            <div className="filters-container" style={{display: 'flex', gap: '0.65rem', width: '100%', maxWidth: '800px', flexDirection: 'column'}}>
            
              {/* 1. Nome Autista (con selettore / cerca autista rapido) */}
              <div style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <div className="autocomplete-wrapper" ref={dropdownRef} style={{ flex: '1 1 100%', width: '100%' }}>
                  <User size={18} className="autocomplete-icon" style={{ color: 'var(--accent-orange)' }} />
                  <input 
                    type="text"
                    className="driver-input"
                    value={searchTerm}
                    onChange={(e) => {
                      setSearchTerm(e.target.value);
                      setIsDropdownOpen(true);
                    }}
                    onFocus={() => {
                       setSearchTerm("");
                       setIsDropdownOpen(true);
                    }}
                    placeholder="Nome autista..."
                    style={{ 
                      background: 'rgba(245, 166, 35, 0.08)', 
                      borderColor: 'rgba(245, 166, 35, 0.35)', 
                      fontWeight: '700',
                      color: 'var(--text-main)',
                      fontSize: '0.92rem',
                      paddingLeft: '36px'
                    }}
                  />
                  <ChevronDown size={18} className="autocomplete-chevron" onClick={() => { setIsDropdownOpen(!isDropdownOpen); }} />
                  
                  {isDropdownOpen && (
                    <ul className="autocomplete-dropdown" style={{ zIndex: 9999 }}>
                      {drivers.filter(d => d.name.toLowerCase().includes(searchTerm.toLowerCase())).length > 0 ? (
                        drivers.filter(d => d.name.toLowerCase().includes(searchTerm.toLowerCase())).map(d => (
                          <li 
                            key={d.name}
                            className={d.name === selectedDriver ? 'selected' : ''}
                            onMouseDown={() => { 
                              setSelectedDriver(d.name);
                              setSearchTerm(d.name);
                              setIsDropdownOpen(false);
                              setSelectedDepot(d.depot);
                              localStorage.setItem("shiftlink_saved_driver", d.name);
                            }}
                          >
                            {d.name} ({d.depot})
                          </li>
                        ))
                      ) : (
                        <li className="no-results">Nessun autista trovato</li>
                      )}
                    </ul>
                  )}
                </div>
              </div>

              {/* 2. Tre Tasti Navigazione: [ 🟢 Turno Oggi ] [ 📅 Vista Mese ] [ 🏢 Vista Deposito ] */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '0.4rem',
                width: '100%',
                background: 'var(--bg-card-hover)',
                padding: '4px',
                borderRadius: '12px',
                border: '1px solid var(--border-color)'
              }}>
                <button
                  type="button"
                  onClick={() => {
                    setViewMode('today');
                    localStorage.setItem('shiftlink_view_mode', 'today');
                  }}
                  style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '5px',
                    padding: '0.6rem 0.2rem', borderRadius: '8px',
                    border: viewMode === 'today' ? '1px solid rgba(16, 185, 129, 0.6)' : '1px solid transparent',
                    background: viewMode === 'today' ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.3), rgba(6, 182, 212, 0.2))' : 'transparent',
                    color: viewMode === 'today' ? '#10b981' : 'var(--text-muted)',
                    fontWeight: viewMode === 'today' ? '800' : '600',
                    cursor: 'pointer', fontSize: '0.8rem', transition: 'all 0.2s', whiteSpace: 'nowrap'
                  }}
                >
                  <span style={{ fontSize: '0.85rem' }}>🟢</span>
                  <span>Turno Oggi</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setViewMode('personal');
                    localStorage.setItem('shiftlink_view_mode', 'personal');
                  }}
                  style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '5px',
                    padding: '0.6rem 0.2rem', borderRadius: '8px',
                    border: viewMode === 'personal' ? '1px solid var(--accent-orange)' : '1px solid transparent',
                    background: viewMode === 'personal' ? 'rgba(245, 166, 35, 0.2)' : 'transparent',
                    color: viewMode === 'personal' ? 'var(--accent-orange)' : 'var(--text-muted)',
                    fontWeight: viewMode === 'personal' ? '800' : '600',
                    cursor: 'pointer', fontSize: '0.8rem', transition: 'all 0.2s', whiteSpace: 'nowrap'
                  }}
                >
                  <Calendar size={14} />
                  <span>Vista Mese</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setViewMode('depot');
                    localStorage.setItem('shiftlink_view_mode', 'depot');
                  }}
                  style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '5px',
                    padding: '0.6rem 0.2rem', borderRadius: '8px',
                    border: viewMode === 'depot' ? '1px solid var(--accent-cyan)' : '1px solid transparent',
                    background: viewMode === 'depot' ? 'rgba(6, 182, 212, 0.2)' : 'transparent',
                    color: viewMode === 'depot' ? 'var(--accent-cyan)' : 'var(--text-muted)',
                    fontWeight: viewMode === 'depot' ? '800' : '600',
                    cursor: 'pointer', fontSize: '0.8rem', transition: 'all 0.2s', whiteSpace: 'nowrap'
                  }}
                >
                  <MapPin size={14} />
                  <span>Vista Deposito</span>
                </button>
              </div>

              {/* 3. Selettore Deposito (se in vista deposito) */}
              {viewMode === 'depot' && (
                <div className="driver-selector" style={{width: '100%', marginBottom: '0.2rem', display: 'flex', alignItems: 'center'}}>
                  <MapPin size={18} style={{marginRight: '0.5rem', color: 'var(--accent-cyan)'}} />
                  <select 
                    value={selectedDepot} 
                    onChange={(e) => {
                      setSelectedDepot(e.target.value);
                      localStorage.setItem("shiftlink_saved_depot", e.target.value);
                    }}
                    className="driver-select-dropdown"
                    style={{flex: 1, padding: '0.5rem', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--bg-card)', color: 'var(--text-light)', outline: 'none'}}
                  >
                    <option value="Tutti">Tutti i depositi</option>
                    <option value="Torino TPL">Torino TPL</option>
                    <option value="Torino Malpensa">Torino Malpensa</option>
                    <option value="Pinerolo">Pinerolo</option>
                    <option value="Perosa">Perosa</option>
                    <option value="Susa">Susa</option>
                    <option value="Caselle">Caselle</option>
                    <option value="Piobesi">Piobesi</option>
                    <option value="Pont">Pont</option>
                    <option value="Luserna">Luserna</option>
                    <option value="Altro">Altro</option>
                  </select>
                </div>
              )}

              {/* 4. Filtri Data Anno e Mese (quando in Vista Mese o Vista Deposito) */}
              {viewMode !== 'today' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem', flex: '0 0 auto', width: '100%' }}>
                  <div className="date-filters-wrapper" style={{ display: 'flex', gap: '0.5rem' }}>
                    <div className="autocomplete-wrapper" style={{width: '130px'}}>
                      <select 
                        className="driver-select"
                        style={{ paddingLeft: '1rem', paddingRight: '2rem' }}
                        value={selectedYear} 
                        onChange={(e) => {
                          setSelectedYear(e.target.value);
                          localStorage.setItem("shiftlink_saved_year", e.target.value);
                        }}
                      >
                        <option value="Tutti">Anno</option>
                        {allYears.map(y => (
                          <option key={y} value={y}>{y}</option>
                        ))}
                      </select>
                      <ChevronDown size={18} className="autocomplete-chevron" style={{pointerEvents: 'none'}} />
                    </div>

                    <div className="autocomplete-wrapper" style={{width: '120px'}}>
                      <select 
                        className="driver-select"
                        style={{ paddingLeft: '1rem', paddingRight: '2rem' }}
                        value={selectedMonth} 
                        onChange={(e) => {
                          setSelectedMonth(e.target.value);
                          localStorage.setItem("shiftlink_saved_month_only", e.target.value);
                        }}
                      >
                        <option value="Tutti">Mese</option>
                        {allMonths.map(m => (
                          <option key={m} value={m}>{m.toUpperCase()}</option>
                        ))}
                      </select>
                      <ChevronDown size={18} className="autocomplete-chevron" style={{pointerEvents: 'none'}} />
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

      </div>

      {activeTab === 'shifts' && (
      <>
      {viewMode === 'today' && (
        <TodayShiftModal
          isEmbedded={true}
          initialTurnoCode={modalTurnoCode || todayShiftInfo.turno}
          driverName={selectedDriver}
          dateStr={todayShiftInfo.dateStr}
        />
      )}
      {viewMode === 'personal' && (
      <div className="timeline-container">
        <div className="timeline-header">
          <div className="timeline-cell header-cell">Data</div>
          <div className="timeline-cell header-cell">Turno</div>
          <div className="timeline-cell header-cell">Orario</div>
        </div>

        {filteredShifts.length === 0 ? (
          <div style={{padding: '2rem', textAlign: 'center', color: 'var(--text-muted)'}}>Nessun turno trovato.</div>
        ) : filteredShifts.map((shift, index) => {
          const { date, turno } = shift;
          
          let shiftClass = "shift-cyan";
          if (turno === "RIP") shiftClass = "shift-rest";
          else if (turno === "DISP") shiftClass = "shift-disp";
          else if (turno === "RF" || turno === "RC") shiftClass = "shift-disp";
          else if (turno.includes("To209") || turno.includes("To208")) shiftClass = "shift-purple"; 

          const lowerDate = date.toLowerCase();
          const periodoLower = shift.periodo ? shift.periodo.toLowerCase() : "";
          const isFestivo = lowerDate.includes("dom") || periodoLower.includes("festivo") || periodoLower.includes("domenica") || turno === "RF";

          const mesi = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"];
          const today = new Date();
          const todayDay = today.getDate().toString();
          const todayMonth = mesi[today.getMonth()];
          const todayYear = today.getFullYear().toString().slice(-2);
          
          let isToday = false;
          const parts = date.split(" ");
          if (parts.length >= 4) {
             const dDay = parts[1];
             const dMonth = parts[2].toLowerCase();
             const dYear = parts[3];
             if (dDay === todayDay && dMonth === todayMonth && dYear === todayYear) {
                isToday = true;
             }
          }

          let orarioText = "-";
          
          if (orariTurni[turno]) {
             let periodoKey = "Non Scolastico";
             if (shift.periodo.toLowerCase().includes("scolastico") && !shift.periodo.toLowerCase().includes("non scolastico")) {
                periodoKey = "Scolastico";
             } else if (shift.periodo.toLowerCase().includes("non scol")) {
                periodoKey = "Non Scolastico";
             } else if (shift.periodo.toLowerCase().includes("agosto")) {
                periodoKey = "Agosto";
             }
             
             if (isFestivo) periodoKey = "Festivo Infrasettimanale";
             else if (lowerDate.includes("sab") && shift.periodo.toLowerCase().includes("scolastico") && !shift.periodo.toLowerCase().includes("non scolastico")) periodoKey = "Sabato SCOL";
             else if (lowerDate.includes("sab") && shift.periodo.toLowerCase().includes("non scolastico")) periodoKey = "Sabato Non SCOL";
             else if (lowerDate.includes("dom")) periodoKey = "Domenica";
             
             // Fallback lookup strategy
             orarioText = orariTurni[turno][periodoKey] || orariTurni[turno]["Scolastico"] || orariTurni[turno]["Non Scolastico"] || "-";
          }

          let displayDate = date.toUpperCase().trim();
          const displayParts = displayDate.split(" ");
          if (displayParts.length >= 3) {
            displayDate = `${displayParts[0]} ${displayParts[1]} ${displayParts[2]}`;
          }

          let hasColor = false;
          let borderColor = "transparent";
          let textColor = "var(--text-main)";
          let timeTextColor = "var(--text-main)";

          if (isFestivo) {
             borderColor = cellBorderColors.festivo;
             textColor = "#ef4444";
             timeTextColor = "#ef4444";
             hasColor = true;
          } else if (lowerDate.includes("sab")) {
             borderColor = cellBorderColors.sabato;
             textColor = "#3b82f6";
             timeTextColor = "#3b82f6";
             hasColor = true;
          } else if (shift.periodo) {
             if (shift.periodo.toLowerCase().includes("non scolastico") || shift.periodo.toLowerCase().includes("non scol")) {
                borderColor = cellBorderColors.nonScolastico;
                hasColor = true;
             }
             else if (shift.periodo.toLowerCase().includes("scolastico") || shift.periodo.toLowerCase().includes("scol")) {
                borderColor = cellBorderColors.scolastico;
                hasColor = true;
             }
          }

          return (
            <div 
              className={`timeline-row ${isToday ? 'is-today' : ''}`} 
              key={index}
              onClick={() => {
                if (turno && turno !== 'RIP') {
                  setModalTurnoCode(turno);
                  setViewMode('today');
                  localStorage.setItem('shiftlink_view_mode', 'today');
                }
              }}
              style={{ cursor: 'pointer' }}
              title="Tocca per vedere i dettagli e le corse del turno"
            >
              <div className="timeline-cell date-text" style={{ color: textColor, fontSize: '0.85rem', justifyContent: 'center', textAlign: 'center' }}>{displayDate}</div>

              <div className="timeline-cell" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <div className={`shift-block ${shiftClass}`} style={{
                     backgroundColor: 'transparent',
                     color: textColor,
                     border: hasColor ? `1px solid ${borderColor}` : '1px solid var(--border-color)',
                     justifyContent: 'center',
                     textAlign: 'center',
                     width: '100%',
                     fontWeight: hasColor ? 'bold' : 'normal',
                     fontSize: '0.85rem'
                }}>
                  {turno}
                </div>
              </div>

              <div className="timeline-cell text-muted" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.9rem' }}>
                {orarioText}
              </div>
            </div>
          );
        })}
      </div>
      )}

      {viewMode === 'depot' && (
        <div className="depot-view-container" style={{ overflowX: 'auto', borderRadius: '8px', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-card)', marginBottom: '2rem' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', whiteSpace: 'nowrap' }}>
            <thead>
              <tr>
                <th style={{ position: 'sticky', left: 0, backgroundColor: 'var(--bg-card)', zIndex: 10, padding: '0.1rem 0.2rem', textAlign: 'left', borderBottom: '2px solid var(--border-color)', borderRight: '1px solid var(--border-color)', color: 'var(--text-light)', fontSize: '0.65rem' }}>
                  Data
                </th>
                {filteredDrivers.map(driver => (
                  <th key={driver.name} style={{ padding: '0.1rem 0.2rem', textAlign: 'center', borderBottom: '2px solid var(--border-color)', minWidth: '30px', color: 'var(--text-muted)', fontSize: '0.65rem', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {driver.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {(() => {
                const mesi = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"];
                const today = new Date();
                const todayDay = today.getDate().toString();
                const todayMonth = mesi[today.getMonth()];
                const todayYear = today.getFullYear().toString().slice(-2);

                return filteredRawRows.map((row, idx) => {
                   const dateStr = row[0] || "";
                   const parts = dateStr.toUpperCase().trim().split(" ");
                   const shortDate = parts.length >= 3 ? `${parts[0]} ${parts[1]} ${parts[2]}` : dateStr;
                   
                   let isToday = false;
                   const dParts = dateStr.split(" ");
                   if (dParts.length >= 4) {
                      const dDay = dParts[1];
                      const dMonth = dParts[2].toLowerCase();
                      const dYear = dParts[3];
                      if (dDay === todayDay && dMonth === todayMonth && dYear === todayYear) {
                         isToday = true;
                      }
                   }

                   const lowerDate = dateStr.toLowerCase();
                   const periodoStr = periodoIndex !== -1 ? (row[periodoIndex] || "").toLowerCase() : "";
                   const isFestivo = lowerDate.includes("dom") || periodoStr.includes("festivo") || periodoStr.includes("domenica");
                   const isSabato = lowerDate.includes("sab") && !isFestivo;

                   let dateColor = 'var(--text-main)';
                   if (isToday) dateColor = '#60a5fa';
                   else if (isFestivo) dateColor = '#ef4444';
                   else if (isSabato) dateColor = '#3b82f6';

                   return (
                     <tr key={idx} className={isToday ? "depot-today-row" : ""} style={{ borderBottom: isToday ? 'none' : '1px solid var(--border-color)' }}>
                       <td style={{ position: 'sticky', left: 0, backgroundColor: 'var(--bg-card)', zIndex: 9, padding: '0.1rem 0.2rem', fontWeight: isToday ? '800' : '500', borderRight: isToday ? '2px solid var(--today-border)' : '1px solid var(--border-color)', color: dateColor, fontSize: '0.65rem' }}>
                         {shortDate}
                         {isToday && <span style={{ display: 'block', marginTop: '0.1rem', backgroundColor: '#2563eb', color: '#ffffff', fontSize: '0.55rem', padding: '1px 2px', borderRadius: '2px', fontWeight: 'bold', width: 'fit-content' }}>OGGI</span>}
                       </td>
                       {filteredDrivers.map(driver => {
                          const shift = (row[driver.index] || "").trim();
                          let shiftClass = "shift-cyan";
                          if (shift === "RIP") shiftClass = "shift-rest";
                          else if (shift === "DISP" || shift === "RF" || shift === "RC") shiftClass = "shift-disp";
                          else if (shift.includes("To209") || shift.includes("To208")) shiftClass = "shift-purple";
                          
                          const periodoStr = periodoIndex !== -1 ? (row[periodoIndex] || "").toLowerCase() : "";
                          const isFestivoShift = lowerDate.includes("dom") || periodoStr.includes("festivo") || periodoStr.includes("domenica") || shift === "RF";
                          const isSabatoShift = lowerDate.includes("sab") && !isFestivoShift;

                          let hasColor = false;
                          let borderColor = "transparent";
                          let textColor = "var(--text-main)";

                          if (isFestivoShift) {
                             borderColor = cellBorderColors.festivo;
                             textColor = "#ef4444";
                             hasColor = true;
                          } else if (isSabatoShift) {
                             borderColor = cellBorderColors.sabato;
                             textColor = "#3b82f6";
                             hasColor = true;
                          } else if (periodoStr) {
                             if (periodoStr.includes("non scolastico") || periodoStr.includes("non scol")) {
                                borderColor = cellBorderColors.nonScolastico; // verde chiaro
                                hasColor = true;
                             } else if (periodoStr.includes("scolastico") || periodoStr.includes("scol")) {
                                borderColor = cellBorderColors.scolastico; // giallo chiaro
                                hasColor = true;
                             }
                          }
                          
                          return (
                            <td 
                              key={driver.name} 
                              onClick={() => {
                                if (shift && shift !== 'RIP') {
                                  setSelectedDriver(driver.name);
                                  setSearchTerm(driver.name);
                                  setModalTurnoCode(shift);
                                  setViewMode('today');
                                  localStorage.setItem('shiftlink_saved_driver', driver.name);
                                  localStorage.setItem('shiftlink_view_mode', 'today');
                                }
                              }}
                              style={{ 
                                cursor: shift ? 'pointer' : 'default',
                                padding: '0.1rem 0.2rem', 
                                textAlign: 'center', 
                                backgroundColor: isToday ? 'rgba(37, 99, 235, 0.05)' : 'transparent', 
                                borderTop: isToday ? '2px solid var(--today-border)' : 'none', 
                                borderBottom: isToday ? '2px solid var(--today-border)' : 'none' 
                              }}
                              title={shift ? `Tocca per aprire ${shift} (${driver.name})` : ''}
                            >
                              {shift ? (
                                <div className={`shift-block ${shiftClass}`} style={{ margin: 0, padding: '0 0.1rem', display: 'inline-block', fontSize: '0.65rem', width: '100%', backgroundColor: 'transparent', color: textColor, border: hasColor ? `1px solid ${borderColor}` : '1px solid var(--border-color)', fontWeight: hasColor ? 'bold' : 'normal', borderRadius: '3px' }}>
                                  {shift}
                                </div>
                              ) : (
                                <span style={{color: 'var(--text-muted)', fontSize: '0.7rem'}}>-</span>
                              )}
                            </td>
                          );
                       })}
                     </tr>
                   );
                });
              })()}
            </tbody>
          </table>
        </div>
      )}
      </>
      )}
      


      <div style={{ height: '70px' }}></div>
      </div>
      <nav style={{
        position: 'fixed',
        bottom: 0, left: 0, right: 0,
        background: 'var(--nav-bg)',
        backdropFilter: 'blur(10px)',
        borderTop: '1px solid var(--nav-border)',
        display: 'flex',
        justifyContent: 'space-around',
        padding: '12px 0 calc(12px + env(safe-area-inset-bottom, 0px))',
        zIndex: 1000,
        boxShadow: '0 -4px 20px rgba(0,0,0,0.1)'
      }}>
        <button 
          onClick={() => setActiveTab('shifts')}
          style={{ 
            background: 'none', border: 'none', 
            color: activeTab === 'shifts' ? 'var(--accent-orange)' : 'var(--text-muted)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px',
            fontSize: '0.75rem', cursor: 'pointer', flex: 1
          }}
        >
          <Calendar size={24} />
          <span>Turni</span>
        </button>
        <button
          onClick={() => setActiveTab('orariocorse')}
          style={{
            background: 'none', border: 'none',
            color: activeTab === 'orariocorse' ? 'var(--accent-orange)' : 'var(--text-muted)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px',
            fontSize: '0.75rem', cursor: 'pointer', flex: 1
          }}
        >
          <Clock size={24} />
          <span>Orario Corse</span>
        </button>
        <button
          onClick={() => setActiveTab('cartellini')}
          style={{
            background: 'none', border: 'none',
            color: activeTab === 'cartellini' ? 'var(--accent-orange)' : 'var(--text-muted)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px',
            fontSize: '0.75rem', cursor: 'pointer', flex: 1
          }}
        >
          <FileText size={24} />
          <span>Cartellini</span>
        </button>
        <button 
          onClick={() => setActiveTab('arriva')}
          style={{ 
            background: 'none', border: 'none', 
            color: activeTab === 'arriva' || activeTab === 'search' ? 'var(--accent-orange)' : 'var(--text-muted)',
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px',
            fontSize: '0.75rem', cursor: 'pointer', flex: 1, position: 'relative'
          }}
        >
          <div style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Bus size={24} />
            {arrivaNoticesCount > 0 && (
              <span style={{
                position: 'absolute', top: '-4px', right: '-8px',
                background: 'var(--accent-orange)', color: '#121214',
                fontSize: '0.65rem', fontWeight: 'bold',
                padding: '1px 5px', borderRadius: '10px',
                lineHeight: '1'
              }}>
                {arrivaNoticesCount}
              </span>
            )}
          </div>
          <span>Viaggia & Arriva</span>
        </button>
        {isAdmin && (
          <button
            onClick={() => setShowAdmin(true)}
            style={{
              background: 'none', border: 'none',
              color: 'var(--text-muted)',
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px',
              fontSize: '0.75rem', cursor: 'pointer', flex: 1
            }}
          >
            <Settings size={24} />
            <span>Admin</span>
          </button>
        )}
      </nav>
      {showAdmin && <AdminPanel onClose={() => setShowAdmin(false)} />}
      <TodayShiftModal
        isOpen={isTodayShiftModalOpen}
        onClose={() => setIsTodayShiftModalOpen(false)}
        initialTurnoCode={modalTurnoCode || todayShiftInfo.turno}
        driverName={selectedDriver}
        dateStr={todayShiftInfo.dateStr}
      />
      <UpdateBanner />
    </div>
  );
}

export default App;
