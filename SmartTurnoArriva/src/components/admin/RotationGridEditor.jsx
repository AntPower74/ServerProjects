import React, { useEffect, useRef, useState } from 'react';
import { turniApi, WEEKDAY_LABELS } from './turniApi.js';
import SpecialPeriodsManager from './SpecialPeriodsManager.jsx';
import SchedulePreview from './SchedulePreview.jsx';
import SchoolCalendarEditor from './SchoolCalendarEditor.jsx';

const DEPOTS = ['TO', 'PI', 'CA', 'LU', 'PT', 'PE', 'PB', 'GT'];

// "Ginardi 563" -> { surname: 'Ginardi', matricola: '563' }; nomi senza matricola numerica
// (es. "Renesto", "(000-)") restano su una riga sola.
function splitDriverName(name) {
  const m = name?.match(/^(.*?)\s+(\d+)$/);
  return m ? { surname: m[1], matricola: m[2] } : { surname: name, matricola: null };
}
const MAIN_VIEWS = [
  { id: 'grid', label: 'Griglie' },
  { id: 'special', label: 'Periodi speciali' },
  { id: 'preview', label: 'Anteprima' },
  { id: 'calendar', label: 'Calendario scolastico' },
];

// Full-screen page (not the AdminPanel bottom sheet) - these grids can have up to
// 40+ columns (one per driver, like the original sheet), they need real room.
// Owns depot selection and driver renaming itself, so this one page covers the
// whole "look at/edit a deposito's rotation" workflow without leaving it.
export default function RotationGridEditor({ depotId: initialDepotId, adminKey, onClose }) {
  const [depotId, setDepotId] = useState(initialDepotId);
  const [depot, setDepot] = useState(null); // { cycle_length, reference_date, ... }
  const [mainView, setMainView] = useState('grid');
  const [drivers, setDrivers] = useState([]);
  const [blocks, setBlocks] = useState([]);
  const [activeBlockId, setActiveBlockId] = useState(null);
  const [cells, setCells] = useState([]); // [{weekday, col_index, turno_code}]
  const [dirty, setDirty] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [renamingPos, setRenamingPos] = useState(null);
  const [renameDraft, setRenameDraft] = useState('');
  const [selection, setSelection] = useState(null); // {col, anchor, focus} weekday indices 0-6
  const [bulkValue, setBulkValue] = useState('');
  const [zoom, setZoom] = useState(1); // pinch-zoom is disabled in standalone PWA mode, so this is a manual substitute
  const [knownTurni, setKnownTurni] = useState([]); // tutti i turno_code gia' visti in questo deposito, per la ricerca
  const [editingCell, setEditingCell] = useState(null); // {weekday, col} della cella con la lista aperta
  const [cellSearchTerm, setCellSearchTerm] = useState(''); // testo di ricerca, separato dal valore della cella
  const editingCellRef = useRef(null); // <td> della cella in modifica, per il rilevamento "tocco fuori"
  const pressTimerRef = useRef(null); // timer per il tap/click prolungato

  // Tap lungo (mobile) / click prolungato o doppio click (browser) per aprire
  // la ricerca - un tap/click normale resta la selezione per l'intervallo
  // multi-cella (altrimenti i due gesti si accavallano sulla stessa azione).
  // cellSearchTerm parte vuoto (non dal valore gia' in cella): altrimenti
  // aprendo una cella che ha gia' un turno la lista si restringe subito a
  // quell'unico valore invece di mostrare tutte le alternative disponibili.
  const openCellSearch = (weekday, col) => {
    setEditingCell({ weekday, col });
    setCellSearchTerm('');
  };
  const startPressTimer = (weekday, col) => {
    clearTimeout(pressTimerRef.current);
    pressTimerRef.current = setTimeout(() => openCellSearch(weekday, col), 500);
  };
  const cancelPressTimer = () => clearTimeout(pressTimerRef.current);

  // Chiude la lista al tocco/click fuori dalla cella in modifica. Non usiamo
  // onBlur dell'input: su mobile il blur scatta prima che il tap sul
  // suggerimento venga registrato (l'elemento sparisce da sotto il dito
  // prima che il tap "atterri"), quindi la selezione non arrivava mai a
  // buon fine sul cellulare. 'mousedown' (non 'pointerdown'): stesso evento
  // gia' usato dal menu a tendina di ricerca autista in App.jsx, che su
  // Safari/iOS in PWA standalone funziona gia' in modo affidabile -
  // 'pointerdown' li' e' meno prevedibile.
  useEffect(() => {
    if (!editingCell) return;
    const handleMouseDown = (e) => {
      if (editingCellRef.current && !editingCellRef.current.contains(e.target)) {
        setEditingCell(null);
      }
    };
    document.addEventListener('mousedown', handleMouseDown);
    return () => document.removeEventListener('mousedown', handleMouseDown);
  }, [editingCell]);

  const loadDepot = () => {
    setBusy(true);
    Promise.all([turniApi.blocks(depotId, adminKey), turniApi.drivers(depotId, adminKey), turniApi.depot(depotId, adminKey)])
      .then(([bs, ds, dep]) => {
        setBlocks(bs);
        setDrivers(ds);
        setDepot(dep);
        setActiveBlockId((prev) => (bs.some((b) => b.id === prev) ? prev : bs[0]?.id ?? null));
        // Vocabolario di ricerca: turni gia' usati in un qualunque blocco di
        // questo deposito (non solo quello attivo), cosi' la lista e' completa
        // fin da subito senza dover girare tutti i blocchi a mano.
        setKnownTurni([]);
        Promise.all(bs.map((b) => turniApi.cells(b.id, adminKey)))
          .then((cellsPerBlock) => {
            const set = new Set();
            cellsPerBlock.flat().forEach((c) => { if (c.turno_code) set.add(c.turno_code); });
            setKnownTurni(Array.from(set).sort());
          })
          .catch(() => {}); // non blocca l'uso della griglia se fallisce
      })
      .catch((e) => setError(e.message))
      .finally(() => setBusy(false));
  };

  useEffect(loadDepot, [depotId]);

  const patchDepot = (field, value) => setDepot((prev) => ({ ...prev, [field]: value }));

  const saveDepot = async () => {
    if (!depot) return;
    setBusy(true);
    setError('');
    try {
      const saved = await turniApi.updateDepot(depotId, {
        cycle_length: Number(depot.cycle_length) || null,
        reference_date: depot.reference_date || null,
      }, adminKey);
      setDepot(saved);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    if (!activeBlockId) return;
    setBusy(true);
    setDirty(false);
    turniApi.cells(activeBlockId, adminKey)
      .then(setCells)
      .catch((e) => setError(e.message))
      .finally(() => setBusy(false));
  }, [activeBlockId]);

  const driverByPosition = new Map(drivers.map((d) => [d.rotation_position, d]));
  const cols = Array.from(new Set(cells.map((c) => c.col_index))).sort((a, b) => a - b);
  const cellMap = new Map(cells.map((c) => [`${c.weekday}:${c.col_index}`, c.turno_code]));

  const setCell = (weekday, col_index, value) => {
    setDirty(true);
    setCells((prev) => {
      const idx = prev.findIndex((c) => c.weekday === weekday && c.col_index === col_index);
      if (idx === -1) return [...prev, { weekday, col_index, turno_code: value }];
      const next = [...prev];
      next[idx] = { ...next[idx], turno_code: value };
      return next;
    });
  };

  const save = async () => {
    setBusy(true);
    setError('');
    try {
      await turniApi.saveCells(activeBlockId, cells, adminKey);
      setDirty(false);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const startRename = (driver) => {
    setRenamingPos(driver.rotation_position);
    setRenameDraft(driver.name);
  };

  const saveRename = async (driver) => {
    const name = renameDraft.trim();
    setRenamingPos(null);
    if (!name || name === driver.name) return;
    setBusy(true);
    try {
      await turniApi.updateDriver(driver.id, { name }, adminKey);
      setDrivers((prev) => prev.map((d) => (d.id === driver.id ? { ...d, name } : d)));
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const selectCell = (weekday, col, shiftKey) => {
    setSelection((prev) => {
      if (shiftKey && prev && prev.col === col) return { ...prev, focus: weekday };
      return { col, anchor: weekday, focus: weekday };
    });
  };

  const selRange = selection ? [Math.min(selection.anchor, selection.focus), Math.max(selection.anchor, selection.focus)] : null;
  const isSelected = (weekday, col) => selection && selection.col === col && weekday >= selRange[0] && weekday <= selRange[1];
  const selectionSize = selRange ? selRange[1] - selRange[0] + 1 : 0;

  const applyBulk = () => {
    if (!selection || !bulkValue) return;
    setDirty(true);
    for (let weekday = selRange[0]; weekday <= selRange[1]; weekday += 1) {
      setCell(weekday, selection.col, bulkValue);
    }
    setBulkValue('');
  };

  const addDriver = async () => {
    const name = window.prompt('Nome nuovo autista:');
    if (!name || !name.trim()) return;
    setBusy(true);
    try {
      await turniApi.addDriver(depotId, name.trim(), adminKey);
      loadDepot();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <span style={styles.title}>Rotazioni</span>
        <div style={styles.headerBtns}>
          <button style={styles.zoomBtn} onClick={() => setZoom((z) => Math.max(0.7, +(z - 0.15).toFixed(2)))}>−</button>
          <span style={styles.zoomLabel}>{Math.round(zoom * 100)}%</span>
          <button style={styles.zoomBtn} onClick={() => setZoom((z) => Math.min(1.9, +(z + 0.15).toFixed(2)))}>+</button>
          <button style={styles.closeBtn} onClick={onClose}>Chiudi</button>
        </div>
      </div>

      <div style={styles.depotTabs}>
        {DEPOTS.map((d) => (
          <button
            key={d}
            onClick={() => setDepotId(d)}
            style={{ ...styles.depotTab, ...(d === depotId ? styles.depotTabActive : {}) }}
          >
            {d}
          </button>
        ))}
        <button style={styles.addDriverBtn} onClick={addDriver}>+ autista</button>
      </div>

      {depot && (
        <div style={styles.depotInfoBar}>
          <label style={styles.depotInfoField}>
            Autisti
            <input
              style={styles.depotInfoInput}
              type="number"
              value={depot.cycle_length ?? ''}
              onChange={(e) => patchDepot('cycle_length', e.target.value)}
              onBlur={saveDepot}
            />
          </label>
          <label style={styles.depotInfoField}>
            Data inizio rotazione
            <input
              style={styles.depotInfoInput}
              type="date"
              value={depot.reference_date ?? ''}
              onChange={(e) => patchDepot('reference_date', e.target.value)}
              onBlur={saveDepot}
            />
          </label>
          <span style={styles.depotInfoHint}>numero di autisti nel ciclo e data da cui parte la rotazione, come nel foglio TO</span>
        </div>
      )}

      <div style={styles.mainViewTabs}>
        {MAIN_VIEWS.map((v) => (
          <button
            key={v.id}
            onClick={() => setMainView(v.id)}
            style={{ ...styles.mainViewTab, ...(v.id === mainView ? styles.mainViewTabActive : {}) }}
          >
            {v.label}
          </button>
        ))}
      </div>

      {error && <div style={styles.error}>{error}</div>}

      {mainView === 'special' && <SpecialPeriodsManager depotId={depotId} adminKey={adminKey} />}
      {mainView === 'preview' && <SchedulePreview depotId={depotId} adminKey={adminKey} />}
      {mainView === 'calendar' && <SchoolCalendarEditor adminKey={adminKey} />}

      {mainView === 'grid' && (
        <>
          <div style={styles.blockTabs}>
            {blocks.map((b) => (
              <button
                key={b.id}
                onClick={() => setActiveBlockId(b.id)}
                style={{ ...styles.blockTab, ...(b.id === activeBlockId ? styles.blockTabActive : {}) }}
              >
                {b.label}
              </button>
            ))}
          </div>

          {selectionSize > 1 && (
            <div style={styles.bulkBar}>
              <span style={styles.bulkLabel}>{selectionSize} celle selezionate</span>
              <input
                style={styles.bulkInput}
                placeholder="nuovo turno per tutte"
                value={bulkValue}
                autoFocus
                onChange={(e) => setBulkValue(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && applyBulk()}
              />
              <button style={styles.smallBtn} onClick={applyBulk}>Applica</button>
              <button style={styles.ghostBtn} onClick={() => setSelection(null)}>Annulla</button>
            </div>
          )}

          {activeBlockId && (
          <>
          <div style={styles.gridWrap}>
            <table style={{ ...styles.table, fontSize: 12 * zoom }}>
              <thead>
                <tr>
                  <th style={{ ...styles.th, ...styles.cornerTh }}></th>
                  {cols.map((c) => {
                    const driver = driverByPosition.get(c);
                    return (
                      <th key={c} style={{ ...styles.th, ...(renamingPos === c ? styles.thRenaming : {}) }}>
                        {driver && renamingPos === c ? (
                          <input
                            style={styles.renameInput}
                            value={renameDraft}
                            autoFocus
                            onChange={(e) => setRenameDraft(e.target.value)}
                            onBlur={() => saveRename(driver)}
                            onKeyDown={(e) => e.key === 'Enter' && saveRename(driver)}
                          />
                        ) : (
                          <div
                            style={{ ...styles.driverHeader, fontSize: 11 * zoom, maxHeight: 90 * zoom, height: 90 * zoom }}
                            onClick={() => driver && startRename(driver)}
                            title={driver ? 'Clicca per rinominare' : ''}
                          >
                            {driver ? (
                              (() => {
                                const { surname, matricola } = splitDriverName(driver.name);
                                // driverHeader is rotated 180deg as a whole, which flips stacking
                                // order too - matricola goes first in the DOM so it ends up
                                // visually below the surname after the flip.
                                return (
                                  <>
                                    {matricola && <span style={{ ...styles.matricolaText, fontSize: 9 * zoom }}>{matricola}</span>}
                                    <span style={{ writingMode: 'vertical-rl' }}>{surname}</span>
                                  </>
                                );
                              })()
                            ) : `#${c}`}
                          </div>
                        )}
                      </th>
                    );
                  })}
                </tr>
              </thead>
              <tbody>
                {WEEKDAY_LABELS.map((label, weekday) => (
                  <tr key={weekday}>
                    <td style={styles.rowLabel}>{label}</td>
                    {cols.map((col) => {
                      const isEditing = editingCell && editingCell.weekday === weekday && editingCell.col === col;
                      const cellValue = cellMap.get(`${weekday}:${col}`) ?? '';
                      const suggestions = isEditing
                        ? knownTurni.filter((t) => t.toLowerCase().includes(cellSearchTerm.toLowerCase())).slice(0, 8)
                        : [];
                      return (
                        <td
                          key={col}
                          ref={isEditing ? editingCellRef : null}
                          style={{ ...styles.td, position: 'relative' }}
                        >
                          <input
                            style={{
                              ...styles.cellInput,
                              width: 60 * zoom, fontSize: 12 * zoom, padding: `${4 * zoom}px ${5 * zoom}px`,
                              WebkitTouchCallout: 'none', WebkitUserSelect: 'none', userSelect: 'none',
                              ...(isSelected(weekday, col) ? styles.cellInputSelected : {}),
                            }}
                            value={cellValue}
                            onChange={(e) => {
                              setCell(weekday, col, e.target.value);
                              if (isEditing) setCellSearchTerm(e.target.value);
                            }}
                            onClick={(e) => selectCell(weekday, col, e.shiftKey)}
                            onDoubleClick={() => openCellSearch(weekday, col)}
                            onMouseDown={() => startPressTimer(weekday, col)}
                            onMouseUp={cancelPressTimer}
                            onMouseLeave={cancelPressTimer}
                            onTouchStart={() => startPressTimer(weekday, col)}
                            onTouchEnd={cancelPressTimer}
                            onTouchCancel={cancelPressTimer}
                          />
                          {isEditing && suggestions.length > 0 && (
                            <div style={styles.turnoDropdown}>
                              {suggestions.map((t) => (
                                <div
                                  key={t}
                                  style={styles.turnoOption}
                                  onMouseDown={() => {
                                    setCell(weekday, col, t);
                                    setEditingCell(null);
                                  }}
                                >
                                  {t}
                                </div>
                              ))}
                            </div>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={styles.hint}>Tap prolungato (o doppio click) su una cella per cercare tra i turni gia' usati in questo deposito (o scrivi liberamente). Clic normale, poi Shift+clic su un'altra cella della stessa colonna, per selezionare un intervallo.</div>
          <button style={styles.saveBtn} disabled={!dirty || busy} onClick={save}>
            {busy ? 'Salvataggio...' : dirty ? 'Salva modifiche' : 'Salvato'}
          </button>
          </>
          )}
        </>
      )}
    </div>
  );
}

const styles = {
  page: {
    position: 'fixed', inset: 0, zIndex: 2100, background: 'var(--bg-dark)',
    display: 'flex', flexDirection: 'column', padding: 16,
    paddingBottom: 'calc(16px + env(safe-area-inset-bottom, 0px))', overflowY: 'auto',
  },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, flex: '0 0 auto' },
  title: { color: 'var(--accent-cyan)', fontWeight: 700, fontSize: 16 },
  headerBtns: { display: 'flex', alignItems: 'center', gap: 6 },
  zoomBtn: {
    background: 'var(--btn-bg)', border: '1px solid var(--border-color)', borderRadius: 6, color: 'var(--text-main)',
    width: 28, height: 28, fontSize: 16, lineHeight: 1, cursor: 'pointer',
  },
  zoomLabel: { color: 'var(--text-muted)', fontSize: 12, width: 36, textAlign: 'center' },
  closeBtn: { background: 'none', border: '1px solid var(--border-color)', borderRadius: 6, color: 'var(--text-muted)', padding: '6px 10px', cursor: 'pointer' },
  depotTabs: { display: 'flex', gap: 6, overflowX: 'auto', marginBottom: 8, paddingBottom: 4, flex: '0 0 auto' },
  depotTab: {
    flex: '0 0 auto', background: 'var(--btn-bg)', border: '1px solid var(--border-color)', borderRadius: 8,
    color: 'var(--text-muted)', padding: '6px 12px', fontSize: 13, fontWeight: 600, cursor: 'pointer',
  },
  depotTabActive: { background: 'var(--accent-cyan)', color: 'var(--bg-dark)', border: '1px solid var(--accent-cyan)' },
  addDriverBtn: {
    flex: '0 0 auto', background: 'none', border: '1px dashed var(--border-color)', borderRadius: 8,
    color: 'var(--text-muted)', padding: '6px 12px', fontSize: 13, cursor: 'pointer',
  },
  depotInfoBar: {
    display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap', marginBottom: 10,
    padding: '8px 10px', background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 8,
  },
  depotInfoField: { display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-muted)', fontSize: 12 },
  depotInfoInput: {
    boxSizing: 'border-box', background: 'var(--bg-dark)', border: '1px solid var(--border-color)',
    borderRadius: 4, color: 'var(--text-main)', padding: '3px 6px', fontSize: 12, width: 130,
  },
  depotInfoHint: { color: 'var(--text-muted)', fontSize: 11, opacity: 0.75 },
  mainViewTabs: { display: 'flex', gap: 6, overflowX: 'auto', marginBottom: 10, paddingBottom: 4, flex: '0 0 auto', borderBottom: '1px solid var(--border-color)' },
  mainViewTab: {
    flex: '0 0 auto', background: 'none', border: 'none', borderBottom: '2px solid transparent',
    color: 'var(--text-muted)', padding: '6px 4px', fontSize: 13, cursor: 'pointer', whiteSpace: 'nowrap',
  },
  mainViewTabActive: { color: 'var(--accent-cyan)', borderBottom: '2px solid var(--accent-cyan)', fontWeight: 600 },
  blockTabs: { display: 'flex', gap: 6, overflowX: 'auto', marginBottom: 10, paddingBottom: 4, flex: '0 0 auto' },
  blockTab: {
    flex: '0 0 auto', background: 'var(--btn-bg)', border: '1px solid var(--border-color)', borderRadius: 8,
    color: 'var(--text-muted)', padding: '6px 10px', fontSize: 12, cursor: 'pointer', whiteSpace: 'nowrap',
  },
  blockTabActive: { background: 'var(--accent-cyan)', color: 'var(--bg-dark)', borderColor: 'var(--accent-cyan)', fontWeight: 600 },
  bulkBar: {
    display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10, padding: '8px 10px',
    background: 'var(--btn-bg)', border: '1px solid var(--accent-cyan)', borderRadius: 8, flex: '0 0 auto', flexWrap: 'wrap',
  },
  bulkLabel: { color: 'var(--text-muted)', fontSize: 12, whiteSpace: 'nowrap' },
  bulkInput: {
    flex: 1, minWidth: 100, boxSizing: 'border-box', background: 'var(--bg-dark)', border: '1px solid var(--border-color)',
    borderRadius: 6, color: 'var(--text-main)', padding: '6px 8px', fontSize: 13,
  },
  smallBtn: { background: 'var(--accent-cyan)', border: 'none', borderRadius: 6, color: 'var(--bg-dark)', fontWeight: 600, padding: '6px 12px', fontSize: 12, cursor: 'pointer', whiteSpace: 'nowrap' },
  ghostBtn: { background: 'none', border: '1px solid var(--border-color)', color: 'var(--text-muted)', borderRadius: 6, padding: '6px 10px', fontSize: 12, cursor: 'pointer', whiteSpace: 'nowrap' },
  gridWrap: { overflow: 'auto', minWidth: 0, border: '1px solid var(--border-color)', borderRadius: 8, flex: '0 1 auto' },
  table: { borderCollapse: 'collapse', fontSize: 12 },
  th: { position: 'sticky', top: 0, background: 'var(--bg-card)', color: 'var(--text-muted)', padding: '4px 4px', borderBottom: '1px solid var(--border-color)', verticalAlign: 'middle' },
  cornerTh: { position: 'sticky', left: 0, zIndex: 1 },
  thRenaming: { zIndex: 10, overflow: 'visible' },
  driverHeader: {
    transform: 'rotate(180deg)', maxHeight: 90,
    fontSize: 11, whiteSpace: 'nowrap', cursor: 'pointer',
    display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 3,
    margin: '0 auto', height: 90,
  },
  matricolaText: { writingMode: 'vertical-rl', color: 'var(--text-muted)' },
  renameInput: {
    position: 'absolute', top: 2, left: 0, zIndex: 5,
    width: 170, boxSizing: 'border-box', background: 'var(--bg-dark)', border: '1px solid var(--accent-cyan)',
    borderRadius: 4, color: 'var(--text-main)', fontSize: 12, padding: '4px 6px', boxShadow: '2px 2px 6px rgba(0,0,0,0.4)',
  },
  rowLabel: {
    position: 'sticky', left: 0, background: 'var(--bg-card)',
    color: 'var(--text-muted)', padding: '4px 8px', borderRight: '1px solid var(--border-color)', whiteSpace: 'nowrap',
  },
  td: { padding: 2, borderBottom: '1px solid var(--border-color)' },
  cellInput: {
    width: 60, boxSizing: 'border-box', background: 'var(--bg-dark)', border: '1px solid var(--border-color)',
    borderRadius: 4, color: 'var(--text-main)', padding: '4px 5px', fontSize: 12, textAlign: 'center',
  },
  cellInputSelected: { borderColor: 'var(--accent-cyan)', boxShadow: '0 0 0 1px var(--accent-cyan)', background: 'rgba(34,211,238,0.12)' },
  turnoDropdown: {
    position: 'absolute', top: '100%', left: 0, zIndex: 20, marginTop: 2,
    background: 'var(--bg-card)', border: '1px solid var(--accent-cyan)', borderRadius: 6,
    boxShadow: '0 4px 12px rgba(0,0,0,0.5)', minWidth: 70, maxHeight: 220, overflowY: 'auto',
  },
  turnoOption: {
    padding: '7px 10px', fontSize: 12, color: 'var(--text-main)', cursor: 'pointer', whiteSpace: 'nowrap',
  },
  hint: { color: 'var(--text-muted)', fontSize: 11, marginTop: 6, flex: '0 0 auto' },
  saveBtn: { marginTop: 10, background: 'var(--accent-cyan)', border: 'none', borderRadius: 8, color: 'var(--bg-dark)', fontWeight: 600, padding: '10px 14px', cursor: 'pointer', flex: '0 0 auto' },
  error: { color: 'var(--accent-red)', fontSize: 13, marginBottom: 8 },
};
