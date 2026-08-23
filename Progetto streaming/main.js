import Hls from 'hls.js';
import mpegts from 'mpegts.js';
import { App } from '@capacitor/app';
import { registerPlugin } from '@capacitor/core';

// Plugin nativo (android/.../ApkInstallerPlugin.java) che scarica l'APK di
// aggiornamento e avvia direttamente l'installer di sistema via FileProvider,
// senza passare dal browser di sistema come prima (window.open(url,
// '_system')). Il tocco finale "Installa" richiesto da Android resta
// comunque obbligatorio, non è aggirabile.
const ApkInstaller = registerPlugin('ApkInstaller');

// Icona locale per i canali senza logo (tvg-logo) o quando il logo remoto
// non si carica: via.placeholder.com (usato prima) non risponde più, quindi
// niente più segnaposto esterno che dipende dalla rete.
const LOGO_FALLBACK = 'data:image/svg+xml;utf8,' + encodeURIComponent(
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 50">
    <rect width="50" height="50" rx="10" fill="#334155"/>
    <rect x="12" y="15" width="26" height="18" rx="2" fill="none" stroke="#94a3b8" stroke-width="2"/>
    <path d="M20 39h10M25 33v6" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"/>
  </svg>`
);

// Escape per dati non fidati (nomi canale/gruppo da playlist esterne, nomi
// digitati nelle richieste di prova da chiunque, senza autenticazione)
// inseriti via innerHTML: senza questo, un nome canale o una richiesta di
// prova come "<img src=x onerror=...>" eseguirebbe JS nel contesto della
// WebView (localStorage, credenziali Xtream salvate, ecc. sono raggiungibili
// da lì) o nel pannello admin di Antonio.
function escapeHtml(str) {
  return String(str ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

const homeScreen = document.getElementById('home-screen');
const browseScreen = document.getElementById('browse-screen');
const accessUserBtn = document.getElementById('access-user-btn');
const accessModal = document.getElementById('access-modal');
const accessModalCancelBtn = document.getElementById('access-modal-cancel');
const accessCodeInput = document.getElementById('access-code-input');
const accessSubmitBtn = document.getElementById('access-submit-btn');
const accessLockMessageEl = document.getElementById('access-lock-message');
const accessTrialBtn = document.getElementById('access-trial-btn');
const trialModal = document.getElementById('trial-modal');
const trialModalCancelBtn = document.getElementById('trial-modal-cancel');
const trialNameInput = document.getElementById('trial-name-input');
const trialSubmitBtn = document.getElementById('trial-submit-btn');
const homeTilesEl = document.querySelector('.home-tiles');
const homePanelActionEl = document.getElementById('home-panel-action');
const openAdminBtn = document.getElementById('open-admin-btn');
const adminScreen = document.getElementById('admin-screen');
const adminBackBtn = document.getElementById('admin-back-btn');
const adminTrialTabsEl = document.getElementById('admin-trial-tabs');
const adminTrialsListEl = document.getElementById('admin-trials-list');
const adminCodesListEl = document.getElementById('admin-codes-list');
const adminNewCodeInput = document.getElementById('admin-new-code');
const adminNewLabelInput = document.getElementById('admin-new-label');
const adminNewExpiryInput = document.getElementById('admin-new-expiry');
const adminNewSpecialInput = document.getElementById('admin-new-special');
const adminNewHostInput = document.getElementById('admin-new-host');
const adminNewUserInput = document.getElementById('admin-new-user');
const adminNewPassInput = document.getElementById('admin-new-pass');
const adminCreateBtn = document.getElementById('admin-create-btn');
const adminCreateToggle = document.getElementById('admin-create-toggle');
const adminCreateBody = document.getElementById('admin-create-body');
const adminCreateChevron = document.getElementById('admin-create-chevron');
const adminNewPlaylistTabsEl = document.getElementById('admin-new-playlist-tabs');
const adminNewPlaylistUrlInput = document.getElementById('admin-new-playlist-url-input');
const adminNewPlaylistFileInput = document.getElementById('admin-new-playlist-file-input');
const adminNewPlaylistFileStatusEl = document.getElementById('admin-new-playlist-file-status');
const adminCodesTabsEl = document.getElementById('admin-codes-tabs');
const adminExpiryPicker = document.getElementById('admin-expiry-picker');
const adminPlaylistModal = document.getElementById('admin-playlist-modal');
const adminPlaylistModalCodeEl = document.getElementById('admin-playlist-modal-code');
const adminEditPlaylistTabsEl = document.getElementById('admin-edit-playlist-tabs');
const adminEditPlaylistUrlInput = document.getElementById('admin-edit-playlist-url-input');
const adminEditPlaylistFileInput = document.getElementById('admin-edit-playlist-file-input');
const adminEditPlaylistFileStatusEl = document.getElementById('admin-edit-playlist-file-status');
const adminPlaylistModalCancelBtn = document.getElementById('admin-playlist-modal-cancel');
const adminPlaylistModalRemoveBtn = document.getElementById('admin-playlist-modal-remove');
const adminPlaylistModalSaveBtn = document.getElementById('admin-playlist-modal-save');
const backToHomeBtn = document.getElementById('back-to-home');
const tilePlaylistsBtn = document.getElementById('tile-playlists');
const tileFileBtn = document.getElementById('tile-file');
const tileUrlBtn = document.getElementById('tile-url');
const playlistCarouselEl = document.getElementById('playlist-carousel');
const currentPlaylistNameEl = document.getElementById('current-playlist-name');
const currentPlaylistExpiryEl = document.getElementById('current-playlist-expiry');
const refreshPlaylistBtn = document.getElementById('refresh-playlist-btn');
const exitAppBtn = document.getElementById('exit-app-btn');
const urlModal = document.getElementById('url-modal');
const urlModalCancelBtn = document.getElementById('url-modal-cancel');
const m3uUrlInput = document.getElementById('m3u-url');
const loadM3uBtn = document.getElementById('load-m3u');
const modalTabBtns = document.querySelectorAll('.modal-tab-btn');
const modalModeLink = document.getElementById('modal-mode-link');
const modalModeXtream = document.getElementById('modal-mode-xtream');
const xtreamProfileListEl = document.getElementById('xtream-profile-list');
const xtreamLabelInput = document.getElementById('xtream-label');
const xtreamHostInput = document.getElementById('xtream-host');
const xtreamUserInput = document.getElementById('xtream-user');
const xtreamPassInput = document.getElementById('xtream-pass');
let modalMode = 'link';
const m3uFileInput = document.getElementById('m3u-file');
const mainListEl = document.getElementById('main-list');
const searchInput = document.getElementById('search-input');
const video = document.getElementById('video-player');
const videoPlaceholder = document.getElementById('video-placeholder');
const channelTitleEl = document.getElementById('channel-title');
const channelGroupEl = document.getElementById('channel-group');
const nowPlayingInfo = document.getElementById('now-playing-info');
const homeLoadingBar = document.getElementById('home-loading-bar');
const homeLoadingBarFill = document.getElementById('home-loading-bar-fill');
const homeLoadingBarText = document.getElementById('home-loading-bar-text');
const epgNowTitleEl = document.getElementById('epg-now-title');
const epgNowTimeEl = document.getElementById('epg-now-time');
const epgNextTitleEl = document.getElementById('epg-next-title');
const epgNextTimeEl = document.getElementById('epg-next-time');
const categoriesPanelEl = document.getElementById('categories-panel');
const categoryListDynamicEl = document.getElementById('category-list-dynamic');
const countAllEl = document.getElementById('count-all');
const countFavsEl = document.getElementById('count-favs');
const countRecentEl = document.getElementById('count-recent');
const labelAllEl = document.getElementById('label-all');
const contentTypeTabsEl = document.getElementById('content-type-tabs');

let channels = [];
let groups = {};
let hls = null;
let tsPlayer = null;
// URL del flusso mostrato in anteprima, usato dal doppio click/tap per
// passare a schermo intero (vedi enterFullscreen più sotto).
let activeStreamUrl = null;
// Credenziali Xtream della playlist corrente (se disponibili), usate per
// interrogare la guida TV (get_short_epg) del canale in riproduzione. null
// se la playlist è stata caricata da file o da un link che non è un
// endpoint Xtream riconoscibile: in quel caso niente guida.
let currentXtreamAuth = null;
// URL di una guida XMLTV generica per la playlist corrente: o dichiarato
// dalla playlist stessa (url-tvg/x-tvg-url nell'header M3U, letto dal
// worker) o, per le playlist Xtream, ricavato dal pannello (xmltv.php).
// Usata come fallback in updateEpgPanel quando get_short_epg non basta
// (playlist non-Xtream) o non trova nulla per il canale.
let currentEpgXmlUrl = null;
// Cache in memoria delle guide XMLTV già scaricate/parsate in questa
// sessione: url -> Promise<Map<tvgId, [{start:Date, stop:Date, title}]>>.
// Una Promise (non il risultato) per deduplicare fetch concorrenti dello
// stesso canale/playlist mentre il download è ancora in corso.
const xmltvGuideCache = new Map();
let epgRequestToken = 0;
// Categoria attualmente selezionata (striscia in alto o pannello a sinistra):
// '__all__' (tutti i canali), '__favs__' (preferiti) o il nome di un gruppo.
let currentCategory = '__all__';
// Filtro a monte: 'live' | 'film' | 'serie' — deciso dalle tre caselle sotto
// il logo, prima ancora del pannello categorie.
let currentContentType = 'live';

const FILM_GROUP = '🎬 Film';
const SERIE_GROUP = '📺 Serie TV';

// Elenco marchi riconosciuti, in ordine di priorità (il primo che
// corrisponde vince). Chi non rientra in nessuno va in "Altri". Vive qui
// (non nel worker) apposta: così viene rieseguita ogni volta che i canali
// vengono mostrati, anche se arrivano da una cache vecchia (IndexedDB,
// playlist recenti) calcolata prima di un cambiamento a questa lista.
const BRAND_RULES = [
  { group: 'DAZN', match: ['DAZN'] },
  { group: 'Sky Sport', match: ['SKY SPORT'] },
  { group: 'Sky Cinema', match: ['SKY CINEMA'] },
  { group: 'Sky Prima Fila', match: ['SKY PRIMAFILA', 'SKY PRIMA FILA', 'PRIMAFILA', 'PRIMA FILA'] },
  { group: 'RAI', match: ['RAI'] },
  { group: 'Mediaset', match: ['MEDIASET', 'CANALE 5', 'CANALE5', 'ITALIA 1', 'ITALIA1', 'ITALIA 2', 'ITALIA2', 'RETE 4', 'RETE4', 'IRIS', 'LA5', 'LA 5', 'TOP CRIME', 'TWENTYSEVEN', 'FOCUS', 'CINE34', 'CINE 34', 'TGCOM'] },
  { group: 'Sky', match: ['SKY'] }
];

function classifyByBrand(name) {
  const upper = (name || '').toUpperCase();

  if (/S\d{1,2}\s*E\d{1,2}/.test(upper) || /STAGIONE\s*\d/.test(upper) || /SEASON\s*\d/.test(upper)) {
    return SERIE_GROUP;
  }
  if (/\(\d{4}\)/.test(upper) || upper.includes('FILM') || upper.includes('MOVIE')) {
    return FILM_GROUP;
  }
  for (const rule of BRAND_RULES) {
    if (rule.match.some(m => upper.includes(m))) {
      return rule.group;
    }
  }
  return 'Altri';
}

// Punto unico per impostare l'elenco canali corrente, da qualunque fonte
// (parsing fresco, cache IndexedDB, ricarica da URL): riclassifica sempre,
// così non capita più di vedere gruppi vecchi da una cache non aggiornata.
function setChannels(newChannels) {
  newChannels.forEach(c => { c.group = classifyByBrand(c.name); });
  channels = newChannels;
  groups = computeGroupCounts(channels);
  updateCounts();
  renderCategoryList();
}

function channelsForType(type) {
  if (type === 'film') return channels.filter(c => c.group === FILM_GROUP);
  if (type === 'serie') return channels.filter(c => c.group === SERIE_GROUP);
  return channels.filter(c => c.group !== FILM_GROUP && c.group !== SERIE_GROUP);
}
// Sorgente della playlist attualmente caricata, per il pulsante di refresh
// e per il testo "Playlist corrente" nella home: {type:'url', url} oppure
// {type:'file', label}.
let currentPlaylistSource = null;

// Gestione Preferiti tramite localStorage
let favorites = JSON.parse(localStorage.getItem('streampro_favs') || '[]');

function saveFavorites() {
  localStorage.setItem('streampro_favs', JSON.stringify(favorites));
}

function toggleFavorite(channel, btn) {
  const index = favorites.findIndex(f => f.url === channel.url);
  if (index > -1) {
    favorites.splice(index, 1);
    btn.classList.remove('is-fav');
    btn.textContent = '☆';
  } else {
    favorites.push(channel);
    btn.classList.add('is-fav');
    btn.textContent = '★';
  }
  saveFavorites();
  updateCounts();

  if (currentCategory === '__favs__') {
    renderChannels(favorites);
  }
}

// Canali guardati di recente (come il flag is_recent/recent_pos di StreamPRO,
// qui tenuti in un elenco a parte già ordinato dal più recente).
const MAX_RECENT_CHANNELS = 20;
let recentChannels = JSON.parse(localStorage.getItem('streampro_recent_channels') || '[]');

function addToRecentChannels(channel) {
  recentChannels = recentChannels.filter(c => c.url !== channel.url);
  recentChannels.unshift(channel);
  recentChannels = recentChannels.slice(0, MAX_RECENT_CHANNELS);
  localStorage.setItem('streampro_recent_channels', JSON.stringify(recentChannels));
  updateCounts();

  if (currentCategory === '__recent__') {
    renderChannels(recentChannels);
  }
}

function updateCounts() {
  const count = channelsForType(currentContentType).length;
  countAllEl.textContent = count > 0 ? count : '';
  countFavsEl.textContent = favorites.length > 0 ? favorites.length : '';
  countRecentEl.textContent = recentChannels.length > 0 ? recentChannels.length : '';
}

// Aggiorna il testo "Playlist corrente" / "Scadenza" nella home. La scadenza
// mostrata è quella del codice di accesso (impostata da Antonio nel
// pannello, vedi currentAccessExpiresAt) — non della playlist in sé, che di
// solito non ne porta una propria (a differenza di un vero account Xtream
// Codes, comunque non letta da nessuna parte qui).
function updateHomeStatus() {
  const expiryText = currentAccessExpiresAt ? formatAdminDate(currentAccessExpiresAt) : '—';
  if (!currentPlaylistSource) {
    currentPlaylistNameEl.textContent = 'Nessuna';
    currentPlaylistExpiryEl.textContent = expiryText;
    return;
  }
  currentPlaylistNameEl.textContent = currentPlaylistSource.label
    || (currentPlaylistSource.type === 'file' ? currentPlaylistSource.label : currentPlaylistSource.url);
  currentPlaylistExpiryEl.textContent = expiryText;
}

// Navigazione tra le due schermate: prima si sceglie la playlist, poi si naviga
function showBrowse() {
  homeScreen.classList.remove('active');
  browseScreen.classList.add('active');
}

function showHome() {
  // Ferma qualsiasi riproduzione in corso prima di tornare alla selezione playlist
  if (window.VideoPlayer && window.VideoPlayer.close) {
    window.VideoPlayer.close();
  }
  if (hls) {
    hls.destroy();
    hls = null;
  }
  if (tsPlayer) {
    tsPlayer.destroy();
    tsPlayer = null;
  }
  video.pause();
  video.removeAttribute('src');
  video.style.display = 'none';
  videoPlaceholder.style.display = 'flex';
  browseScreen.classList.remove('active');
  homeScreen.classList.add('active');
  playlistCarouselEl.classList.remove('open');
}

// Playlist recenti: sia quelle da URL (si ri-scaricano) sia i file locali
// (si tiene in memoria l'elenco canali già estratto, per riaprirli all'istante
// senza dover riselezionare il file dal telefono ogni volta).
//
// I metadati (tipo, etichetta, URL) stanno in localStorage: sono leggeri.
// I canali dei file locali invece possono essere migliaia con logo/URL lunghi
// e superare facilmente i 5-10MB di localStorage (fallisce in silenzio) — per
// quelli usiamo IndexedDB, che ha un limite molto più alto.
const RECENT_PLAYLISTS_KEY = 'streampro_recent_playlists';
const MAX_RECENT = 6;
const DB_NAME = 'streampro_db';
const DB_STORE = 'file_playlists';

function openPlaylistDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1);
    req.onupgradeneeded = () => {
      if (!req.result.objectStoreNames.contains(DB_STORE)) {
        req.result.createObjectStore(DB_STORE, { keyPath: 'label' });
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function saveFilePlaylistToDB(label, fileChannels, epgUrl) {
  const db = await openPlaylistDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(DB_STORE, 'readwrite');
    tx.objectStore(DB_STORE).put({ label, channels: fileChannels, epgUrl: epgUrl || null });
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

async function loadFilePlaylistFromDB(label) {
  const db = await openPlaylistDB();
  return new Promise((resolve, reject) => {
    const req = db.transaction(DB_STORE, 'readonly').objectStore(DB_STORE).get(label);
    req.onsuccess = () => resolve(req.result || null);
    req.onerror = () => reject(req.error);
  });
}

// Pannello di gestione degli accessi Xtream salvati (creare/modificare/
// cancellare più utenze), separato dalle playlist recenti perché qui
// servono anche host/utente/password modificabili singolarmente.
const XTREAM_PROFILES_KEY = 'streampro_xtream_profiles';
let editingXtreamProfileId = null;

function getXtreamProfiles() {
  return JSON.parse(localStorage.getItem(XTREAM_PROFILES_KEY) || '[]');
}

function persistXtreamProfiles(list) {
  try {
    localStorage.setItem(XTREAM_PROFILES_KEY, JSON.stringify(list));
  } catch (e) {
    console.warn('Impossibile salvare gli accessi Xtream:', e);
  }
  renderXtreamProfiles();
}

function upsertXtreamProfile({ id, label, host, username, password }) {
  const list = getXtreamProfiles();
  const finalLabel = label || `${username}@${host.replace(/^https?:\/\//i, '')}`;
  if (id) {
    const idx = list.findIndex(p => p.id === id);
    if (idx !== -1) {
      list[idx] = { id, label: finalLabel, host, username, password };
    }
  } else {
    list.unshift({ id: Date.now().toString(36), label: finalLabel, host, username, password });
  }
  persistXtreamProfiles(list);
}

function deleteXtreamProfile(id) {
  persistXtreamProfiles(getXtreamProfiles().filter(p => p.id !== id));
  if (editingXtreamProfileId === id) {
    editingXtreamProfileId = null;
    xtreamLabelInput.value = '';
  }
}

function fillXtreamForm(profile) {
  editingXtreamProfileId = profile.id;
  xtreamLabelInput.value = profile.label;
  xtreamHostInput.value = profile.host;
  xtreamUserInput.value = profile.username;
  xtreamPassInput.value = profile.password;
}

function renderXtreamProfiles() {
  const list = getXtreamProfiles();
  if (list.length === 0) {
    xtreamProfileListEl.innerHTML = '<div class="xtream-profile-empty">Nessun accesso salvato</div>';
    return;
  }
  xtreamProfileListEl.innerHTML = '';
  list.forEach(profile => {
    const row = document.createElement('div');
    row.className = 'xtream-profile-row';
    row.innerHTML = `
      <span class="xtream-profile-label">${escapeHtml(profile.label)}</span>
      <button type="button" class="icon-btn xtream-edit-btn" title="Modifica">
        <svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><path d="M4 20h4L18.5 9.5a2.1 2.1 0 0 0-3-3L5 17v3z" stroke="currentColor" stroke-width="2" fill="none" stroke-linejoin="round"/></svg>
      </button>
      <button type="button" class="icon-btn icon-btn-danger xtream-delete-btn" title="Elimina">
        <svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true"><path d="M6 7h12M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2m-8 0 1 13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1l1-13" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </button>
    `;
    row.querySelector('.xtream-profile-label').addEventListener('click', () => {
      fillXtreamForm(profile);
      loadFromUrl(buildXtreamM3uUrl(profile.host, profile.username, profile.password));
    });
    row.querySelector('.xtream-edit-btn').addEventListener('click', (e) => {
      e.stopPropagation();
      fillXtreamForm(profile);
    });
    row.querySelector('.xtream-delete-btn').addEventListener('click', (e) => {
      e.stopPropagation();
      if (confirm(`Eliminare l'accesso "${profile.label}"?`)) {
        deleteXtreamProfile(profile.id);
      }
    });
    xtreamProfileListEl.appendChild(row);
  });
}

function getRecentPlaylists() {
  return JSON.parse(localStorage.getItem(RECENT_PLAYLISTS_KEY) || '[]');
}

function persistRecentPlaylists(list) {
  try {
    localStorage.setItem(RECENT_PLAYLISTS_KEY, JSON.stringify(list));
  } catch (e) {
    console.warn('Impossibile salvare l\'elenco playlist recenti:', e);
  }
  renderRecentPlaylists();
}

function saveRecentUrlPlaylist(url) {
  let label;
  try {
    label = new URL(url).hostname;
  } catch {
    label = url.slice(0, 40);
  }
  currentPlaylistSource = { type: 'url', url, label };
  updateHomeStatus();
  let list = getRecentPlaylists().filter(p => !(p.type === 'url' && p.url === url));
  list.unshift({ type: 'url', url, label });
  persistRecentPlaylists(list.slice(0, MAX_RECENT));
}

async function saveRecentFilePlaylist(fileName, fileChannels, epgUrl) {
  try {
    await saveFilePlaylistToDB(fileName, fileChannels, epgUrl);
  } catch (e) {
    console.warn('Impossibile salvare la playlist file in locale:', e);
    return;
  }
  currentPlaylistSource = { type: 'file', label: fileName };
  updateHomeStatus();
  let list = getRecentPlaylists().filter(p => !(p.type === 'file' && p.label === fileName));
  list.unshift({ type: 'file', label: fileName });
  persistRecentPlaylists(list.slice(0, MAX_RECENT));
}

// Carica una playlist recente (per etichetta+tipo) senza passare dalla home
async function openRecentPlaylist(p) {
  if (p.type === 'file') {
    const data = await loadFilePlaylistFromDB(p.label);
    if (!data) {
      alert('Playlist non trovata in locale, ricaricala dal file.');
      return;
    }
    setChannels(data.channels);
    currentPlaylistSource = { type: 'file', label: p.label };
    currentXtreamAuth = null;
    currentEpgXmlUrl = data.epgUrl || null;
    updateHomeStatus();
    showBrowse();
    resetContentType();
    applyCategory('__all__');
  } else {
    loadFromUrl(p.url);
  }
}

// Banner a scorrimento nella tessera "Seleziona Playlist" della home
function renderRecentPlaylists() {
  const list = getRecentPlaylists();
  playlistCarouselEl.innerHTML = '';

  if (preactivatedPlaylist) {
    const chip = document.createElement('div');
    chip.className = 'playlist-chip playlist-chip-preactivated';
    chip.textContent = '🔒 Playlist preattiva';
    chip.addEventListener('click', (e) => {
      e.stopPropagation();
      loadPreactivatedPlaylist();
    });
    playlistCarouselEl.appendChild(chip);
  }

  list.forEach(p => {
    const chip = document.createElement('div');
    chip.className = 'playlist-chip';
    const icon = p.type === 'file' ? '📂' : '🔗';
    chip.textContent = `${icon} ${p.label}`;
    chip.addEventListener('click', (e) => {
      e.stopPropagation();
      openRecentPlaylist(p);
    });
    playlistCarouselEl.appendChild(chip);
  });
}

// Inizializza Web Worker per parsing in background
const parserWorker = new Worker(new URL('./worker.js', import.meta.url));

let workerCallback = null;
parserWorker.onmessage = function(e) {
  const data = e.data;
  if (data.type === 'progress' && workerCallback) {
    workerCallback.onProgress(data.percent);
  } else if (data.type === 'done' && workerCallback) {
    workerCallback.onDone(data.channels, data.epgUrl || null);
  }
};

function parseM3UWorker(content, onProgress, onDone) {
  workerCallback = { onProgress, onDone };
  parserWorker.postMessage(content);
}


let currentRenderLimit = 50;
let currentFilteredData = [];
let observer = null;
// Per il rilevamento a mano del "doppio clic" sulla stessa riga canale (vedi
// il click handler più sotto) — non un vero dblclick nativo.
let lastClickedChannelUrl = null;
let lastClickedAt = 0;

function renderChannels(channelData, append = false) {
  if (!append) {
    mainListEl.innerHTML = '';
    currentFilteredData = channelData;
    currentRenderLimit = 50;
  }
  
  if (currentFilteredData.length === 0) {
    mainListEl.innerHTML = '<li class="placeholder">Nessun elemento trovato</li>';
    return;
  }

  const start = append ? currentRenderLimit - 50 : 0;
  const end = currentRenderLimit;
  const toRender = currentFilteredData.slice(start, end);

  // Costruite in un DocumentFragment (fuori dal DOM vivo) e inserite tutte
  // insieme in un solo appendChild, invece di una riga alla volta: prima ogni
  // riga veniva inserita e subito dopo misurata (per il testo scorrevole dei
  // nomi lunghi), costringendo il browser a un ricalcolo di layout sincrono
  // per ognuna delle 50 righe per pagina — il vero collo di bottiglia dello
  // scorrimento lento su hardware debole (box TV). Le misure ora si fanno
  // tutte insieme, in un unico passaggio, dopo l'unico inserimento nel DOM.
  const fragment = document.createDocumentFragment();
  const createdRows = [];

  toRender.forEach(channel => {
    const li = document.createElement('li');
    li.className = 'channel-item';

    const isFav = favorites.some(f => f.url === channel.url);

    li.innerHTML = `
      <img class="channel-logo" src="${escapeHtml(channel.logo) || LOGO_FALLBACK}" alt="logo" loading="lazy" onerror="this.onerror=null; this.src='${LOGO_FALLBACK}'" />
      <div class="channel-info">
        <span class="channel-name"><span class="channel-name-track">${escapeHtml(channel.name)}</span></span>
        <span class="channel-group">${escapeHtml(channel.group)}</span>
      </div>
      <button class="fav-btn ${isFav ? 'is-fav' : ''}" tabindex="-1" aria-hidden="true">${isFav ? '★' : '☆'}</button>
    `;

    const favBtn = li.querySelector('.fav-btn');
    // Fuori dalla navigazione da telecomando dei box TV: tabindex="-1" da
    // solo non basta, perché molti telecomandi navigano leggendo l'albero di
    // accessibilità di Android (che include comunque ogni <button> reale, a
    // prescindere dal tabindex) — con aria-hidden l'elemento sparisce anche
    // da quell'albero, restando comunque visibile e cliccabile col puntatore.
    favBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleFavorite(channel, favBtn);
    });

    li.addEventListener('click', () => {
      // Rilevato a mano (non con l'evento nativo "dblclick") perché quello
      // richiede due clic quasi nello stesso punto esatto dello schermo entro
      // pochi millisecondi — con un telecomando (puntatore emulato con un
      // minimo di imprecisione, o due pressioni separate di Invio) quasi mai
      // succede, quindi il doppio clic sembrava non funzionare mai. Qui basta
      // che il secondo clic arrivi in tempo sullo stesso canale, ovunque
      // esattamente sia caduto il puntatore.
      const now = Date.now();
      const isSecondPress = lastClickedChannelUrl === channel.url && (now - lastClickedAt) < 600;
      lastClickedChannelUrl = channel.url;
      lastClickedAt = now;

      if (isSecondPress && activeStreamUrl) {
        enterFullscreen();
        return;
      }

      document.querySelectorAll('.channel-item').forEach(el => el.classList.remove('active'));
      li.classList.add('active');
      playChannel(channel);

      // Scorri verso l'alto per far vedere il player quando la lista è sopra (layout verticale)
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Doppio click nativo del mouse (desktop/browser): resta come scorciatoia
    // aggiuntiva, il rilevamento sopra copre anche i casi in cui non scatta.
    li.addEventListener('dblclick', enterFullscreen);

    fragment.appendChild(li);
    createdRows.push({ li, channel });
  });

  mainListEl.appendChild(fragment);

  // Se il nome è troppo lungo per la casella, lo facciamo scorrere (marquee)
  // invece di tagliarlo con "...". Misurato ora, dopo che tutte le righe sono
  // già nel DOM insieme, non una a una durante la costruzione.
  createdRows.forEach(({ li, channel }) => {
    const nameEl = li.querySelector('.channel-name');
    const trackEl = li.querySelector('.channel-name-track');
    if (trackEl.scrollWidth > nameEl.clientWidth) {
      const escapedName = escapeHtml(channel.name);
      trackEl.innerHTML = `${escapedName}<span class="channel-name-gap"></span>${escapedName}`;
      nameEl.classList.add('scrolling');
    }
  });

  // Setup infinite scroll observer
  if (observer) {
    observer.disconnect();
  }
  
  if (currentRenderLimit < currentFilteredData.length) {
    const sentinel = document.createElement('li');
    sentinel.className = 'placeholder';
    sentinel.textContent = 'Caricamento altri...';
    mainListEl.appendChild(sentinel);

    observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        observer.unobserve(sentinel);
        sentinel.remove();
        currentRenderLimit += 50;
        renderChannels([], true);
      }
    }, { root: mainListEl, rootMargin: '100px' });
    
    observer.observe(sentinel);
  }
}

// Ordine dei marchi principali (vedi classifyByBrand in worker.js): questi
// vanno sempre in cima, "Altri" sempre in fondo, il resto (non dovrebbe
// capitare, ma per sicurezza) in mezzo in ordine alfabetico.
const BRAND_ORDER = ['📺 Serie TV', '🎬 Film', 'DAZN', 'Sky Sport', 'Sky Cinema', 'Sky Prima Fila', 'RAI', 'Mediaset', 'Sky'];

function sortGroupNames(names) {
  return names.sort((a, b) => {
    const ia = BRAND_ORDER.indexOf(a);
    const ib = BRAND_ORDER.indexOf(b);
    if (a === 'Altri') return 1;
    if (b === 'Altri') return -1;
    if (ia !== -1 && ib !== -1) return ia - ib;
    if (ia !== -1) return -1;
    if (ib !== -1) return 1;
    return a.localeCompare(b);
  });
}

function computeGroupCounts(list) {
  const counts = {};
  list.forEach(c => {
    counts[c.group] = (counts[c.group] || 0) + 1;
  });
  return counts;
}

// Popola il pannello categorie a sinistra con i gruppi della playlist corrente,
// filtrati per nome se l'utente sta cercando (filterTerm). Film e Serie non
// hanno ulteriori sotto-categorie: sono già filtrati a monte dalle tre
// caselle Live/Film/Serie, qui sotto restano solo i marchi "in diretta".
function renderCategoryList(filterTerm = '') {
  categoryListDynamicEl.innerHTML = '';
  if (currentContentType !== 'live') return;

  const term = filterTerm.toLowerCase();
  const liveGroupCounts = computeGroupCounts(channelsForType('live'));
  const groupNames = sortGroupNames(Object.keys(liveGroupCounts)).filter(g => g.toLowerCase().includes(term));
  const maxRender = 300;

  groupNames.slice(0, maxRender).forEach(g => {
    const item = document.createElement('div');
    item.className = 'category-item';
    item.dataset.category = g;
    item.innerHTML = `<span>${escapeHtml(g)}</span><span class="count">${liveGroupCounts[g]}</span>`;
    categoryListDynamicEl.appendChild(item);
  });
}

// Seleziona una categoria (tutti / preferiti / un gruppo specifico) e mostra
// la lista canali corrispondente nel pannello centrale.
function applyCategory(category) {
  currentCategory = category;
  searchInput.value = '';
  renderCategoryList();

  document.querySelectorAll('.category-item').forEach(el => {
    el.classList.toggle('active', el.dataset.category === category);
  });

  if (category === '__all__') {
    renderChannels(channelsForType(currentContentType));
  } else if (category === '__favs__') {
    renderChannels(favorites);
  } else if (category === '__recent__') {
    renderChannels(recentChannels);
  } else {
    renderChannels(channelsForType(currentContentType).filter(c => c.group === category));
  }
}

function onCategoryClick(e) {
  const item = e.target.closest('.category-item');
  if (item) applyCategory(item.dataset.category);
}
categoriesPanelEl.addEventListener('click', onCategoryClick);

// Le tre caselle Live/Film/Serie: filtrano tutto il resto a monte
const CONTENT_TYPE_LABELS = { live: 'Tutti i canali', film: 'Tutti i film', serie: 'Tutte le serie' };

// Ad ogni nuova playlist caricata si riparte da "Live", altrimenti resterebbe
// selezionato Film/Serie da una playlist precedente.
function resetContentType() {
  currentContentType = 'live';
  contentTypeTabsEl.querySelectorAll('.content-type-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.type === 'live');
  });
  labelAllEl.textContent = CONTENT_TYPE_LABELS.live;
}

contentTypeTabsEl.addEventListener('click', (e) => {
  const btn = e.target.closest('.content-type-btn');
  if (!btn) return;

  currentContentType = btn.dataset.type;
  contentTypeTabsEl.querySelectorAll('.content-type-btn').forEach(b => {
    b.classList.toggle('active', b === btn);
  });
  labelAllEl.textContent = CONTENT_TYPE_LABELS[currentContentType];
  updateCounts();
  applyCategory('__all__');
});



// I titoli/descrizioni della guida Xtream arrivano codificati in base64;
// atob() da solo tratta il risultato come Latin1, quindi i caratteri
// accentati verrebbero storpiati senza ripassare i byte da TextDecoder.
function b64DecodeUtf8(str) {
  try {
    const binary = atob(str);
    const bytes = Uint8Array.from(binary, c => c.charCodeAt(0));
    return new TextDecoder('utf-8').decode(bytes);
  } catch {
    return str || '';
  }
}

function formatEpgTime(unixSeconds) {
  const n = Number(unixSeconds);
  if (!n) return '';
  return new Date(n * 1000).toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' });
}

// Prova la guida via API Xtream (get_short_epg): richiede le credenziali
// della playlist e uno stream_id numerico ricavabile dall'URL del canale.
// Ritorna {title, startSeconds, stopSeconds} per "ora" e "prossimo", o null
// se non disponibile (playlist non Xtream, canale senza id, nessun dato).
async function fetchXtreamEpg(channel) {
  if (!currentXtreamAuth) return null;
  const match = channel.url.match(/\/(\d+)\.(ts|m3u8)(\?|$)/i);
  if (!match) return null;

  const streamId = match[1];
  const { host, username, password } = currentXtreamAuth;
  const apiUrl = `${host}/player_api.php?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}&action=get_short_epg&stream_id=${streamId}&limit=2`;

  const res = await fetch(apiUrl);
  const data = await res.json();
  const listings = data && data.epg_listings;
  if (!listings || listings.length === 0) return null;

  const [now, next] = listings;
  return {
    now: { title: b64DecodeUtf8(now.title) || 'In onda', startSeconds: Number(now.start_timestamp), stopSeconds: Number(now.stop_timestamp) },
    next: next ? { title: b64DecodeUtf8(next.title) || '—', startSeconds: Number(next.start_timestamp) } : null
  };
}

// Costruisce l'URL della guida XMLTV completa di un pannello Xtream: quasi
// tutti i pannelli la espongono su questo endpoint standard, oltre al
// get_short_epg per-canale già usato sopra.
function buildXtreamXmltvUrl({ host, username, password }) {
  return `${host}/xmltv.php?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`;
}

// Un timestamp XMLTV è tipo "20260802220000 +0200": AAAAMMGGoomiss seguito
// da un offset UTC opzionale (assente = UTC).
function parseXmltvTimestamp(ts) {
  const m = /^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})\s*(?:([+-])(\d{2})(\d{2}))?/.exec((ts || '').trim());
  if (!m) return null;
  const [, y, mo, d, h, mi, s, sign, oh, om] = m;
  let ms = Date.UTC(+y, +mo - 1, +d, +h, +mi, +s);
  if (sign) {
    const offsetMinutes = (+oh * 60 + +om) * (sign === '+' ? 1 : -1);
    ms -= offsetMinutes * 60000;
  }
  return new Date(ms);
}

// Scarica e parsa una guida XMLTV generica, con deduplica per URL (chiamate
// concorrenti per canali diversi della stessa playlist condividono lo stesso
// download) e supporto ai file .xml.gz (comuni per queste guide, spesso
// diverse decine di MB non compressi).
function loadXmltvGuide(url) {
  if (xmltvGuideCache.has(url)) return xmltvGuideCache.get(url);

  const promise = (async () => {
    const res = await fetch(url);
    const buffer = await res.arrayBuffer();
    let bytes = new Uint8Array(buffer);

    const isGzip = bytes.length > 2 && bytes[0] === 0x1f && bytes[1] === 0x8b;
    if (isGzip) {
      if (typeof DecompressionStream === 'undefined') {
        console.warn('[xmltv] guida compressa (.gz) ma DecompressionStream non disponibile in questa WebView');
        return new Map();
      }
      const ds = new DecompressionStream('gzip');
      const decompressedStream = new Blob([bytes]).stream().pipeThrough(ds);
      bytes = new Uint8Array(await new Response(decompressedStream).arrayBuffer());
    }

    const xmlText = new TextDecoder('utf-8').decode(bytes);
    const doc = new DOMParser().parseFromString(xmlText, 'text/xml');
    if (doc.querySelector('parsererror')) {
      console.warn('[xmltv] XML non valido per', url);
      return new Map();
    }

    const byChannelId = new Map();
    for (const node of doc.getElementsByTagName('programme')) {
      const channelId = node.getAttribute('channel');
      const start = parseXmltvTimestamp(node.getAttribute('start'));
      const stop = parseXmltvTimestamp(node.getAttribute('stop'));
      const titleEl = node.getElementsByTagName('title')[0];
      if (!channelId || !start || !stop) continue;

      if (!byChannelId.has(channelId)) byChannelId.set(channelId, []);
      byChannelId.get(channelId).push({ start, stop, title: titleEl ? titleEl.textContent : '' });
    }
    for (const list of byChannelId.values()) list.sort((a, b) => a.start - b.start);
    return byChannelId;
  })().catch(err => {
    console.warn('[xmltv] impossibile caricare/parsare la guida:', err);
    xmltvGuideCache.delete(url); // permette un nuovo tentativo la prossima volta, non resta bloccata su un errore
    return new Map();
  });

  xmltvGuideCache.set(url, promise);
  return promise;
}

// Prova la guida via XMLTV generico: richiede il tvg-id del canale (dalla
// M3U) e un url-tvg noto per la playlist corrente (dichiarato dalla M3U
// stessa o, per playlist Xtream, ricavato da xmltv.php).
async function fetchXmltvEpg(channel) {
  if (!channel.tvgId || !currentEpgXmlUrl) return null;

  const byChannelId = await loadXmltvGuide(currentEpgXmlUrl);
  const listings = byChannelId.get(channel.tvgId);
  if (!listings || listings.length === 0) return null;

  const now = Date.now();
  const nowIdx = listings.findIndex(p => p.start.getTime() <= now && now < p.stop.getTime());
  if (nowIdx === -1) return null;

  const nowProgram = listings[nowIdx];
  const nextProgram = listings[nowIdx + 1] || null;
  return {
    now: { title: nowProgram.title || 'In onda', startSeconds: nowProgram.start.getTime() / 1000, stopSeconds: nowProgram.stop.getTime() / 1000 },
    next: nextProgram ? { title: nextProgram.title || '—', startSeconds: nextProgram.start.getTime() / 1000 } : null
  };
}

// Guida TV (cosa è in onda ora / a seguire) sotto l'anteprima. Prova prima
// get_short_epg (Xtream, leggero: una richiesta per canale), poi come
// fallback una guida XMLTV generica se la playlist ne dichiara una (vedi
// currentEpgXmlUrl) — copre sia le playlist non-Xtream sia i canali Xtream
// senza dati in get_short_epg.
async function updateEpgPanel(channel) {
  const token = ++epgRequestToken;
  epgNowTitleEl.textContent = 'Caricamento guida...';
  epgNowTimeEl.textContent = '';
  epgNextTitleEl.textContent = '—';
  epgNextTimeEl.textContent = '';

  let result = null;
  try {
    result = await fetchXtreamEpg(channel);
    if (!result) result = await fetchXmltvEpg(channel);
  } catch (err) {
    result = null;
  }

  if (token !== epgRequestToken) return; // nel frattempo è stato selezionato un altro canale

  if (!result) {
    epgNowTitleEl.textContent = 'Guida non disponibile per questo canale';
    epgNowTimeEl.textContent = '';
    return;
  }

  epgNowTitleEl.textContent = result.now.title;
  epgNowTimeEl.textContent = `${formatEpgTime(result.now.startSeconds)}–${formatEpgTime(result.now.stopSeconds)}`;
  if (result.next) {
    epgNextTitleEl.textContent = result.next.title;
    epgNextTimeEl.textContent = formatEpgTime(result.next.startSeconds);
  }
}

function playChannel(channel) {
  channelTitleEl.textContent = channel.name;
  channelGroupEl.textContent = channel.group;
  nowPlayingInfo.classList.add('visible');
  addToRecentChannels(channel);
  updateEpgPanel(channel);

  setTimeout(() => {
    nowPlayingInfo.classList.remove('visible');
  }, 5000);

  // Distruggi i player precedenti
  if (hls) {
    hls.destroy();
    hls = null;
  }
  if (tsPlayer) {
    tsPlayer.destroy();
    tsPlayer = null;
  }

  const originalUrl = channel.url;
  const isRawTs = originalUrl.toLowerCase().split('?')[0].endsWith('.ts');

  // Se il flusso è .ts grezzo e mpegts.js lo può decodificare, usiamo il
  // link originale (mpegts.js parla MPEG-TS nativamente). Solo se mpegts
  // non è disponibile proviamo a riscrivere in .m3u8 per i player HLS
  // (funziona solo sui server Xtream Codes che servono davvero entrambi i
  // formati sullo stesso link: NON è garantito, quindi va tentato per
  // ultimo, non forzato sempre come prima).
  let finalUrl = originalUrl;
  if (isRawTs && !mpegts.isSupported()) {
    finalUrl = originalUrl.replace(/\.ts($|\?)/i, '.m3u8$1');
  }

  // Serve al doppio click/tap per sapere quale flusso passare a schermo intero
  activeStreamUrl = finalUrl;

  // Primo tap: riproduce in anteprima nel riquadro (niente schermo intero
  // automatico). Il doppio click/tap sulla voce o sul video passa a schermo
  // intero (gestito più sotto), restando sullo stesso flusso già in corso.
  //
  // Usiamo sempre il player HTML5 (mai il plugin nativo, che apre un dialog
  // a tutto schermo e non permette un'anteprima): l'User-Agent richiesto dai
  // server IPTV è comunque garantito perché impostato a livello di intera
  // WebView in capacitor.config.json, non solo per le richieste native.
  if (document.fullscreenElement) {
    document.exitFullscreen().catch(() => {});
  }
  videoPlaceholder.style.display = 'none';
  video.style.display = 'block';

  if (isRawTs && mpegts.isSupported()) {
    // Flussi MPEG-TS grezzi: il tag <video> non li decodifica da solo
    tsPlayer = mpegts.createPlayer({ type: 'mse', isLive: true, url: finalUrl });
    tsPlayer.attachMediaElement(video);
    tsPlayer.on(mpegts.Events.ERROR, (type, details) => {
      showPlaybackError(`[mpegts] ${type} (${details})`);
    });
    tsPlayer.load();
    tsPlayer.play().catch(e => showPlaybackError('[mpegts.play] ' + e.message));
  } else if (Hls.isSupported()) {
    // Chrome/Android WebView: HLS via Media Source Extensions. Va sempre
    // provato PRIMA del ramo "nativo" sotto: alcune Android System WebView
    // dichiarano falsamente supporto nativo tramite canPlayType() ma poi
    // non sanno davvero riprodurre la playlist HLS ([native-hls.play] failed).
    hls = new Hls({ liveDurationInfinity: true });
    hls.loadSource(finalUrl);
    hls.attachMedia(video);
    hls.on(Hls.Events.MANIFEST_PARSED, () => video.play().catch(e => showPlaybackError('[hls.play] ' + e.message)));
    hls.on(Hls.Events.ERROR, (event, data) => {
      if (data.fatal) {
        showPlaybackError(`[hls.js] ${data.type} (${data.details || ''})`);
      }
    });
  } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    // Safari/iOS: unico posto dove non c'è alternativa a MSE
    video.src = finalUrl;
    video.play().catch(e => showPlaybackError('[native-hls.play] ' + e.message));
  } else {
    // Non dovrebbe mai capitare su Android/Chrome (Hls.isSupported() è
    // praticamente sempre vero lì): se succede, MSE/hls.js non sono
    // disponibili in questa WebView.
    showPlaybackError('[fallback] Hls.isSupported()=false, url=' + redactUrlForDisplay(finalUrl));
    video.src = finalUrl;
    video.play().catch(e => showPlaybackError('[fallback.play] ' + e.message));
  }
}

// Gli URL Xtream (get.php, e gli stream /live|movie|series/USER/PASS/id)
// portano le credenziali in chiaro nel percorso: non vanno mai mostrati a
// schermo così come sono (screenshot, screen sharing, semplice sguardo
// altrui), altrimenti l'attenzione già usata per nascondere le credenziali
// altrove nell'app (vedi "Playlist preattiva") sarebbe vanificata qui.
function redactUrlForDisplay(url) {
  try {
    const u = new URL(url);
    if (u.searchParams.has('password')) u.searchParams.set('password', '***');
    if (u.searchParams.has('username')) u.searchParams.set('username', '***');
    u.pathname = u.pathname.replace(/\/(live|movie|series)\/[^/]+\/[^/]+\//i, '/$1/***/***/');
    return u.toString();
  } catch {
    return url;
  }
}

// Mostra un errore di riproduzione visibile invece di fallire in silenzio
// (utile anche per capire la causa reale: es. blocco CORS del server IPTV,
// che via player nativo non capiterebbe mai ma via HTML5 sì).
function showPlaybackError(message) {
  console.error(message);
  channelGroupEl.textContent = message;
  nowPlayingInfo.classList.add('visible');
}

video.addEventListener('error', () => {
  if (video.error) {
    showPlaybackError('Errore video: codice ' + video.error.code);
  }
});

// Passa a schermo intero il flusso attualmente in anteprima. Su Android,
// Capacitor NON supporta il Fullscreen API HTML5 (il suo WebChromeClient
// chiama subito onCustomViewHidden, annullando la richiesta): l'unico modo
// affidabile è il plugin nativo, già pronto e testato per l'anteprima
// stessa. Fuori dall'app nativa (es. anteprima nel browser) usiamo invece
// il Fullscreen API standard, che lì funziona regolarmente.
function enterFullscreen() {
  if (!activeStreamUrl) return;

  const isNative = window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform();

  if (isNative && window.VideoPlayer) {
    // Il player nativo apre una propria connessione allo stream: se non
    // mettiamo in pausa l'anteprima HTML5, questa continua a riprodurre
    // (e a consumare dati/audio) sotto al fullscreen nativo, restando
    // visibile/attiva anche dopo la chiusura.
    video.pause();
    window.VideoPlayer.play(activeStreamUrl, {
      volume: 1.0,
      scalingMode: 1
    }, function () {
      console.log('Video a schermo intero chiuso');
      video.play().catch(() => {});
    }, function (err) {
      console.error('Errore schermo intero:', err);
      video.play().catch(() => {});
    });
  } else if (video.requestFullscreen) {
    video.requestFullscreen().catch(() => {});
  } else if (video.webkitRequestFullscreen) {
    video.webkitRequestFullscreen();
  }
}

// Doppio clic sul video stesso per lo schermo intero
video.addEventListener('dblclick', enterFullscreen);

// Se l'URL è un endpoint Xtream Codes (get.php con username/password nella
// query, sia costruito dalla scheda "Utente Xtream" sia incollato a mano),
// ricaviamo le credenziali per poter interrogare la guida TV (get_short_epg)
// dei canali di questa playlist. Altrimenti niente guida disponibile.
function inferXtreamAuthFromUrl(url) {
  try {
    const u = new URL(url);
    const username = u.searchParams.get('username');
    const password = u.searchParams.get('password');
    if (username && password) {
      return { host: `${u.protocol}//${u.host}`, username, password };
    }
  } catch {}
  return null;
}

// Carica M3U URL
async function loadFromUrl(url, opts = {}) {
  if (!url) return;
  // Per la playlist preattivata (vedi loadPreactivatedPlaylist) l'URL contiene
  // le credenziali decise dall'admin e non va mai mostrato nel campo "Link
  // diretto", né salvato tra le playlist recenti dell'utente.
  if (!opts.hidden) m3uUrlInput.value = url;

  // Barra visibile sulla home stessa (non dentro #browse-screen, che resta
  // nascosto — display:none via CSS — finché il caricamento non è già
  // finito: usare un elemento lì dentro come si faceva prima non mostrava
  // mai nulla durante il caricamento automatico all'avvio, che parte proprio
  // dalla home).
  homeLoadingBar.style.display = 'block';
  homeLoadingBarFill.style.width = '0%';
  homeLoadingBarText.textContent = 'Scaricamento playlist...';

  try {
    loadM3uBtn.textContent = 'Scaricamento...';
    // Instradato dal nostro backend (non dal browser) per evitare CORS e la
    // dipendenza da un proxy di terze parti (allorigins.win, spesso instabile
    // o giù del tutto) usata prima qui.
    const proxyUrl = `https://streampro.cupto.it/api/proxy-fetch?url=${encodeURIComponent(url)}`;
    const response = await fetch(proxyUrl);
    const data = await response.json();

    if (data.contents) {
      loadM3uBtn.textContent = 'Parsing in background...';
      parseM3UWorker(data.contents,
        (percent) => {
          loadM3uBtn.textContent = `Analisi... ${percent}%`;
          homeLoadingBarFill.style.width = `${percent}%`;
          homeLoadingBarText.textContent = `Caricamento playlist... ${percent}%`;
        },
        (resChannels, epgUrl) => {
          setChannels(resChannels);
          if (opts.hidden) {
            currentPlaylistSource = { type: 'preattivata', label: opts.label || 'Playlist preattiva' };
            updateHomeStatus();
          } else {
            saveRecentUrlPlaylist(url);
          }
          currentXtreamAuth = inferXtreamAuthFromUrl(url);
          // Se la playlist non dichiara una guida propria ma è Xtream, il
          // pannello espone quasi sempre xmltv.php: proviamolo come fallback.
          currentEpgXmlUrl = epgUrl || (currentXtreamAuth ? buildXtreamXmltvUrl(currentXtreamAuth) : null);
          urlModal.classList.remove('active');
          showBrowse();
          resetContentType();
          applyCategory('__all__');
          loadM3uBtn.textContent = 'Carica';
          homeLoadingBar.style.display = 'none';
        }
      );
    } else {
      alert("Errore nel caricamento della playlist");
      loadM3uBtn.textContent = 'Carica';
      homeLoadingBar.style.display = 'none';
    }
  } catch (err) {
    console.error(err);
    alert("Errore di rete o URL non valido");
    loadM3uBtn.textContent = 'Carica';
    homeLoadingBar.style.display = 'none';
  }
}

// Schede "Link diretto" / "Utente Xtream" dentro il popup di caricamento
modalTabBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    modalMode = btn.dataset.mode;
    modalTabBtns.forEach(b => b.classList.toggle('active', b === btn));
    modalModeLink.classList.toggle('active', modalMode === 'link');
    modalModeXtream.classList.toggle('active', modalMode === 'xtream');
  });
});

// Un server Xtream Codes espone tipicamente questo endpoint per generare la
// playlist M3U dalle credenziali utente: riusiamo tutta la pipeline di
// caricamento/parsing già esistente per gli URL, senza doverla duplicare.
function buildXtreamM3uUrl(host, username, password) {
  let base = host.trim();
  if (!/^https?:\/\//i.test(base)) {
    base = 'http://' + base;
  }
  base = base.replace(/\/+$/, '');
  return `${base}/get.php?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}&type=m3u_plus&output=ts`;
}

loadM3uBtn.addEventListener('click', () => {
  if (modalMode === 'xtream') {
    const host = xtreamHostInput.value.trim();
    const username = xtreamUserInput.value.trim();
    const password = xtreamPassInput.value;
    if (!host || !username || !password) {
      alert('Inserisci indirizzo server, utente e password');
      return;
    }
    upsertXtreamProfile({ id: editingXtreamProfileId, label: xtreamLabelInput.value.trim(), host, username, password });
    editingXtreamProfileId = null;
    loadFromUrl(buildXtreamM3uUrl(host, username, password));
  } else {
    loadFromUrl(m3uUrlInput.value.trim());
  }
});

// Apertura/chiusura del popup "Carica da URL"
tileUrlBtn.addEventListener('click', () => {
  editingXtreamProfileId = null;
  xtreamLabelInput.value = '';
  xtreamHostInput.value = '';
  xtreamUserInput.value = '';
  xtreamPassInput.value = '';
  urlModal.classList.add('active');
  m3uUrlInput.focus();
});
urlModalCancelBtn.addEventListener('click', () => urlModal.classList.remove('active'));
urlModal.addEventListener('click', (e) => {
  if (e.target === urlModal) urlModal.classList.remove('active');
});

// Carica file M3U locale
const tileFileLabel = tileFileBtn.querySelector('span');
const tileFileLabelOriginal = tileFileLabel.textContent;

if (tileFileBtn && m3uFileInput) {
  tileFileBtn.addEventListener('click', () => {
    m3uFileInput.click();
  });

  m3uFileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();

    reader.onprogress = (event) => {
      if (event.lengthComputable) {
        const percentLoaded = Math.round((event.loaded / event.total) * 100);
        tileFileLabel.textContent = `Lettura... ${percentLoaded}%`;
      }
    };

    reader.onload = (event) => {
      tileFileLabel.textContent = 'Analisi in corso...';
      const content = event.target.result;

      parseM3UWorker(content,
        (percent) => {
          tileFileLabel.textContent = `Analisi... ${percent}%`;
        },
        (resChannels, epgUrl) => {
          setChannels(resChannels);
          saveRecentFilePlaylist(file.name, channels, epgUrl);
          currentXtreamAuth = null;
          currentEpgXmlUrl = epgUrl || null;
          showBrowse();
          resetContentType();
          applyCategory('__all__');
          tileFileLabel.textContent = tileFileLabelOriginal;
        }
      );
    };
    reader.readAsText(file);
    e.target.value = '';
  });
}

// Il tasto Invio/Cerca della tastiera chiude semplicemente la tastiera
// (il filtro è già live sull'evento 'input'): senza questo, l'unico modo
// per chiuderla era il tasto indietro del telefono.
searchInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    e.preventDefault();
    searchInput.blur();
  }
});

// Ricerca: filtra le categorie nel pannello a sinistra. Una volta scelta la
// categoria la lista canali al centro mostra tutto il gruppo, senza bisogno
// di un'altra ricerca lì dentro.
searchInput.addEventListener('input', (e) => {
  try {
    renderCategoryList(e.target.value);
  } catch (err) {
    console.error('Errore nella ricerca:', err);
  }
});

// Torna alla schermata di selezione playlist
backToHomeBtn.addEventListener('click', showHome);

// La tessera "Seleziona Playlist" apre/chiude il banner con le playlist
// salvate (nascosto di default); se non ce ne sono avvisa l'utente.
tilePlaylistsBtn.addEventListener('click', (e) => {
  if (e.target.closest('.playlist-chip')) return;
  if (getRecentPlaylists().length === 0 && !preactivatedPlaylist) {
    alert('Nessuna playlist salvata: caricane una da file o da URL.');
    return;
  }
  playlistCarouselEl.classList.toggle('open');
});

// Aggiorna la playlist attualmente caricata
refreshPlaylistBtn.addEventListener('click', () => {
  // Il refresh controlla anche gli aggiornamenti dell'app e lo stato
  // dell'accesso (utile per chi ha mandato una richiesta di prova e vuole
  // sapere se è stata attivata, senza dover riavviare l'app).
  checkForUpdate();
  refreshAccessState();

  if (!currentPlaylistSource) {
    alert('Nessuna playlist caricata da aggiornare.');
    return;
  }
  openRecentPlaylist(currentPlaylistSource);
});

// Chiude l'app (solo su Android nativo)
exitAppBtn.addEventListener('click', () => {
  if (window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform()) {
    App.exitApp();
  }
});

// Controllo aggiornamenti automatico all'avvio (solo su app nativa Android)
// IMPORTANTE: ad ogni nuova release bisogna aggiornare il contenuto di questo
// URL (stesso indirizzo, nuovo JSON), altrimenti le app già installate non
// vedranno mai il nuovo aggiornamento.
const UPDATE_MANIFEST_URL = 'https://streampro.cupto.it/update-manifest.json';

async function checkForUpdate() {
  if (!window.Capacitor || !window.Capacitor.isNativePlatform || !window.Capacitor.isNativePlatform()) {
    return;
  }
  try {
    const info = await App.getInfo();
    const res = await fetch(UPDATE_MANIFEST_URL, { cache: 'no-store' });
    if (!res.ok) return;
    const manifest = await res.json();

    const localCode = parseInt(info.build, 10);
    const remoteCode = parseInt(manifest.versionCode, 10);

    if (remoteCode > localCode) {
      // Scarica ed apre l'installer direttamente (plugin nativo), senza
      // passare dal browser di sistema: Android mostrerà comunque un tocco
      // finale per installare (limite di sicurezza di sistema, non aggirabile
      // senza permessi speciali).
      channelGroupEl.textContent = `Download aggiornamento v${manifest.versionName} in corso...`;
      nowPlayingInfo.classList.add('visible');
      try {
        await ApkInstaller.downloadAndInstall({ url: manifest.apkUrl });
        channelGroupEl.textContent = '';
      } catch (installErr) {
        console.warn('Download/installazione aggiornamento fallita:', installErr);
        channelGroupEl.textContent = 'Download aggiornamento fallito, riprova più tardi.';
      }
    }
  } catch (err) {
    console.warn('Controllo aggiornamenti fallito (probabilmente offline):', err);
  }
}

// Controllo accessi: la lista dei codici abilitati/disabilitati (con
// scadenza opzionale, vincolo al dispositivo e, opzionalmente, una playlist
// Xtream legata al codice) la gestisce Antonio da un pannello admin separato
// (pagina HTML esterna a questa app), che scrive sullo stesso blob condiviso
// letto qui. Finché non viene inserito un codice valido, le tessere della
// home restano bloccate.
const ACCESS_CODES_URL = 'https://streampro.cupto.it/api/access-blob';
const ACCESS_CODE_KEY = 'streampro_access_code';
const DEVICE_ID_KEY = 'streampro_device_id';
// Credenziali della playlist legata al codice, se l'admin ne ha assegnata
// una: mai mostrate nell'interfaccia (niente campi precompilati, niente URL
// visibile), solo un'unica voce "Playlist preattiva" cliccabile.
let preactivatedPlaylist = null;
// Scadenza del codice/richiesta di prova che ha sbloccato l'app, mostrata
// nella home (vedi updateHomeStatus) al posto del vecchio "—" fisso.
let currentAccessExpiresAt = null;

// Android, dalla versione 6 in poi, non permette più alle app (né tantomeno
// a una WebView) di leggere il vero indirizzo MAC del dispositivo: qualsiasi
// tentativo restituirebbe sempre lo stesso valore fittizio per tutti. Come
// equivalente pratico generiamo un ID casuale univoco alla prima apertura e
// lo tratteniamo per sempre in locale: il codice viene legato al primo
// dispositivo su cui viene usato (stesso risultato pratico del "vincolarlo a
// un MAC", cioè non riutilizzabile su un secondo telefono).
function getDeviceId() {
  let id = localStorage.getItem(DEVICE_ID_KEY);
  if (!id) {
    id = (crypto.randomUUID ? crypto.randomUUID() : `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`);
    localStorage.setItem(DEVICE_ID_KEY, id);
  }
  return id;
}

// null finché non sappiamo ancora lo stato reale (primo avvio): evita di
// forzare showHome() quando la app parte già bloccata, e lo fa solo quando
// un accesso che era valido smette di esserlo (vera revoca in corso).
let lastKnownUnlocked = null;

function setUnlocked(unlocked) {
  const wasUnlocked = lastKnownUnlocked;
  lastKnownUnlocked = unlocked;
  homeTilesEl.classList.toggle('locked', !unlocked);
  accessUserBtn.classList.toggle('unlocked', unlocked);
  if (unlocked) {
    accessLockMessageEl.style.display = 'none';
    accessTrialBtn.style.display = 'none';
  } else if (wasUnlocked === true) {
    // Era sbloccata (l'utente magari sta guardando un canale) e il controllo
    // periodico ha appena scoperto che l'admin l'ha disabilitata: rispetta
    // subito la revoca invece di aspettare che l'utente torni da solo alla home.
    showHome();
  }
}

// Il messaggio/tasto sotto il logo quando l'app è bloccata: cambia se c'è
// già una richiesta di prova in attesa (niente più tasto "Richiedi", solo
// lo stato) oppure no (tasto visibile).
function showLockedMessage(pending) {
  accessLockMessageEl.style.display = 'block';
  accessLockMessageEl.textContent = pending
    ? 'Richiesta di prova inviata: in attesa di attivazione'
    : 'Accesso richiesto: inserisci il codice dal tasto in alto a destra, oppure richiedi una prova';
  accessTrialBtn.style.display = pending ? 'none' : 'inline-block';
}

async function fetchAccessBlob() {
  const res = await fetch(ACCESS_CODES_URL, { cache: 'no-store' });
  if (!res.ok) throw new Error('HTTP ' + res.status);
  const data = await res.json();
  return { codes: (data && data.codes) || {}, devices: (data && data.devices) || {} };
}

async function saveAccessBlob(blob) {
  await fetch(ACCESS_CODES_URL, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(blob)
  });
}

// Verifica un codice e, se è il primo utilizzo, lo lega a questo
// dispositivo (scrittura sul blob condiviso). Esito: { ok, reason } dove
// reason è 'missing' | 'expired' | 'device' quando ok è false.
async function checkAccessCode(code) {
  const blob = await fetchAccessBlob();
  const entry = blob.codes[code];
  if (!entry || !entry.enabled) {
    return { ok: false, reason: 'missing' };
  }
  if (entry.expiresAt && new Date(entry.expiresAt).getTime() < Date.now()) {
    return { ok: false, reason: 'expired' };
  }
  const deviceId = getDeviceId();
  if (entry.deviceId && entry.deviceId !== deviceId) {
    return { ok: false, reason: 'device' };
  }
  if (!entry.deviceId) {
    entry.deviceId = deviceId;
    blob.codes[code] = entry;
    try { await saveAccessBlob(blob); } catch (e) { console.warn('Impossibile registrare il dispositivo sul codice:', e); }
  }
  return { ok: true, entry };
}

// Un codice può avere una playlist preattivata di due forme: credenziali
// Xtream (host/username/password, che l'app ricostruisce nell'URL get.php)
// oppure un link diretto già pronto (playlistUrl), impostato dal pannello
// sia digitandolo a mano sia caricando un file (che diventa comunque un
// link, vedi uploadPlaylistFile lato pannello).
function derivePreactivatedPlaylist(entry) {
  if (entry.host && entry.username && entry.password) {
    return { type: 'xtream', host: entry.host, username: entry.username, password: entry.password };
  }
  if (entry.playlistUrl) {
    return { type: 'url', url: entry.playlistUrl };
  }
  return null;
}

// Riapre da sola l'ultima playlist usata, al primo sblocco della sessione,
// così non tocca ripescarla ogni volta dalla home. Solo una volta per avvio
// (autoLoadedLastPlaylist): il ricontrollo periodico ogni 30s chiama anche
// lui applyAccessCheckResult, e senza questa guardia riaprirebbe la playlist
// in continuazione interrompendo qualunque riproduzione in corso.
let autoLoadedLastPlaylist = false;

function applyAccessCheckResult(result) {
  const ok = !!result.ok;
  setUnlocked(ok);
  preactivatedPlaylist = ok ? derivePreactivatedPlaylist(result.entry) : null;
  currentAccessExpiresAt = ok ? (result.entry.expiresAt || null) : null;
  // Un codice "speciale" (impostato da Antonio nel pannello) sblocca anche
  // il tasto per aprire il pannello accessi dal telefono: solo i codici
  // possono essere speciali, mai le richieste di prova.
  homePanelActionEl.style.display = (ok && result.entry.special) ? 'flex' : 'none';
  renderRecentPlaylists();
  updateHomeStatus();

  if (ok && !autoLoadedLastPlaylist) {
    autoLoadedLastPlaylist = true;
    // La playlist preattivata dal codice ha la precedenza (è la scelta
    // dell'admin per questo dispositivo/codice); altrimenti si riapre
    // l'ultima playlist personale usata. Prima la preattivata richiedeva
    // comunque un tocco manuale sulla sua "chip" — da qui in poi si apre
    // da sola come l'ultima playlist, così non serve selezionare nulla ad
    // ogni avvio in nessuno dei due casi.
    if (homeScreen.classList.contains('active')) {
      if (preactivatedPlaylist) {
        loadPreactivatedPlaylist();
      } else {
        const recent = getRecentPlaylists();
        if (recent.length > 0) openRecentPlaylist(recent[0]);
      }
    }
  }

  return ok;
}

function accessFailureMessage(reason) {
  if (reason === 'device') return 'Codice già attivo su un altro dispositivo';
  if (reason === 'expired') return 'Codice scaduto';
  return 'Codice non valido';
}

// Percorso alternativo al codice: l'utente manda una richiesta di prova
// (legata al suo deviceId, niente da digitare) e l'admin la attiva dal
// pannello scegliendo lui la durata. L'app si sblocca da sola quando la
// richiesta passa a "active", senza bisogno di alcun codice.
async function checkDeviceTrial() {
  const deviceId = getDeviceId();
  const blob = await fetchAccessBlob();
  const entry = blob.devices[deviceId];
  if (!entry) return { status: 'none' };
  if (entry.status === 'rejected') return { status: 'rejected' };
  if (entry.status === 'active') {
    if (entry.expiresAt && new Date(entry.expiresAt).getTime() < Date.now()) {
      return { status: 'expired' };
    }
    return { status: 'active', entry };
  }
  return { status: 'pending' };
}

async function submitTrialRequest(name) {
  const deviceId = getDeviceId();
  const blob = await fetchAccessBlob();
  blob.devices[deviceId] = {
    status: 'pending',
    label: name || '',
    requestedAt: new Date().toISOString()
  };
  await saveAccessBlob(blob);
}

// Punto d'ingresso unico chiamato all'avvio: prova prima il codice salvato
// (se c'è), poi lo stato della richiesta di prova legata a questo
// dispositivo. Se il controllo fallisce per mancanza di rete e c'era già un
// codice valido in precedenza, non blocca chi aveva già accesso.
async function refreshAccessState() {
  const code = localStorage.getItem(ACCESS_CODE_KEY);
  if (code) {
    try {
      const result = await checkAccessCode(code);
      if (applyAccessCheckResult(result)) return;
      // Il codice resta salvato anche se il controllo fallisce ora (scaduto,
      // disabilitato...): se in futuro Antonio lo riattiva o allunga la
      // scadenza (es. rinnovo abbonamento), il prossimo controllo periodico
      // lo riconosce di nuovo da solo, senza che l'utente debba reinserirlo.
    } catch {
      setUnlocked(true);
      return;
    }
  }

  try {
    const trial = await checkDeviceTrial();
    if (trial.status === 'active') {
      setUnlocked(true);
      preactivatedPlaylist = null;
      currentAccessExpiresAt = trial.entry.expiresAt || null;
      homePanelActionEl.style.display = 'none';
      renderRecentPlaylists();
      updateHomeStatus();
      if (!autoLoadedLastPlaylist) {
        autoLoadedLastPlaylist = true;
        if (homeScreen.classList.contains('active')) {
          const recent = getRecentPlaylists();
          if (recent.length > 0) openRecentPlaylist(recent[0]);
        }
      }
      return;
    }
    setUnlocked(false);
    showLockedMessage(trial.status === 'pending');
  } catch {
    setUnlocked(false);
    showLockedMessage(false);
  }
}

// La playlist legata al codice (se presente) compare come voce fissa nel
// banner "Seleziona Playlist", sopra le playlist recenti dell'utente:
// caricarla non la salva tra le recenti né mostra mai l'URL con le
// credenziali (vedi opts.hidden in loadFromUrl).
function loadPreactivatedPlaylist() {
  if (!preactivatedPlaylist) return;
  const url = preactivatedPlaylist.type === 'url'
    ? preactivatedPlaylist.url
    : buildXtreamM3uUrl(preactivatedPlaylist.host, preactivatedPlaylist.username, preactivatedPlaylist.password);
  loadFromUrl(url, { hidden: true, label: 'Playlist preattiva' });
}

accessUserBtn.addEventListener('click', () => {
  accessCodeInput.value = localStorage.getItem(ACCESS_CODE_KEY) || '';
  accessModal.classList.add('active');
  accessCodeInput.focus();
});
accessModalCancelBtn.addEventListener('click', () => accessModal.classList.remove('active'));
accessModal.addEventListener('click', (e) => {
  if (e.target === accessModal) accessModal.classList.remove('active');
});

accessSubmitBtn.addEventListener('click', async () => {
  const code = accessCodeInput.value.trim().toUpperCase();
  if (!code) return;
  accessSubmitBtn.textContent = 'Verifica...';
  try {
    const result = await checkAccessCode(code);
    const ok = applyAccessCheckResult(result);
    if (ok) {
      localStorage.setItem(ACCESS_CODE_KEY, code);
      accessModal.classList.remove('active');
    } else {
      alert(accessFailureMessage(result.reason));
    }
  } catch (err) {
    alert('Errore di rete, riprova.');
  }
  accessSubmitBtn.textContent = 'Invia';
});

accessTrialBtn.addEventListener('click', () => {
  trialNameInput.value = '';
  trialModal.classList.add('active');
  trialNameInput.focus();
});
trialModalCancelBtn.addEventListener('click', () => trialModal.classList.remove('active'));
trialModal.addEventListener('click', (e) => {
  if (e.target === trialModal) trialModal.classList.remove('active');
});

trialSubmitBtn.addEventListener('click', async () => {
  trialSubmitBtn.textContent = 'Invio...';
  try {
    await submitTrialRequest(trialNameInput.value.trim());
    trialModal.classList.remove('active');
    showLockedMessage(true);
  } catch (err) {
    alert('Errore di rete, riprova.');
  }
  trialSubmitBtn.textContent = 'Invia richiesta';
});

// Pannello accessi in-app: stessa funzionalità della pagina admin
// standalone (creare/gestire codici e richieste di prova), raggiungibile
// solo da chi ha sbloccato l'app con un codice "speciale" (vedi
// applyAccessCheckResult). Riusa le stesse funzioni fetchAccessBlob /
// saveAccessBlob / checkAccessCode ecc. già definite sopra per il gate.

function randomAccessCode() {
  const chars = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
  const group = () => {
    let s = '';
    for (let i = 0; i < 4; i++) s += chars[Math.floor(Math.random() * chars.length)];
    return s;
  };
  return `${group()}-${group()}-${group()}`;
}

function formatAdminDate(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString('it-IT');
}

function formatAdminDateTime(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleString('it-IT');
}

function isEntryExpired(entry) {
  return !!(entry.expiresAt && new Date(entry.expiresAt).getTime() < Date.now());
}

async function shareAccessCode(code) {
  const text = `Il tuo codice di accesso StreamPRO: ${code}`;
  if (navigator.share) {
    try {
      await navigator.share({ title: 'Codice StreamPRO', text });
      return;
    } catch (e) {
      // condivisione annullata dall'utente: nessun fallback necessario
      return;
    }
  }
  try {
    await navigator.clipboard.writeText(text);
    alert('Condivisione non disponibile: codice copiato negli appunti.');
  } catch (e) {
    alert(text);
  }
}

function showAdmin() {
  homeScreen.classList.remove('active');
  adminScreen.classList.add('active');
  renderAdminCodes();
  renderAdminTrials();
}

function backFromAdmin() {
  adminScreen.classList.remove('active');
  homeScreen.classList.add('active');
}

// jsonblob (piano gratuito) ha un limite di 10 KB per l'intero archivio
// codici+richieste: una playlist intera non ci starebbe mai. Un file
// caricato dal pannello quindi non viene salvato per intero, ma prima messo
// su tmpfiles.org (stesso servizio già usato per distribuire gli APK) e nel
// codice si salva solo il link diretto risultante, poche decine di byte.
async function uploadPlaylistFile(file) {
  // tmpfiles.org rifiuta ("Invalid file name.") qualunque nome con un solo
  // carattere prima dell'estensione (es. "9.m3u") — non documentato, scoperto
  // solo provando. Si allunga qui il nome se troppo corto, prima di caricare.
  const dot = file.name.lastIndexOf('.');
  const base = dot > 0 ? file.name.slice(0, dot) : file.name;
  const ext = dot > 0 ? file.name.slice(dot) : '';
  const safeName = base.length < 2 ? `playlist-${base}${ext}` : file.name;
  const safeFile = safeName === file.name ? file : new File([file], safeName, { type: file.type });

  const form = new FormData();
  form.append('file', safeFile);
  const uploadRes = await fetch('https://tmpfiles.org/api/v1/upload', { method: 'POST', body: form });
  const uploadData = await uploadRes.json();
  if (!uploadData || uploadData.status !== 'success') throw new Error('Caricamento fallito');
  const landingUrl = uploadData.data.url;
  // La pagina di destinazione di tmpfiles.org non manda header CORS: risolta
  // dal nostro backend lato server, non da un proxy di terze parti.
  const resolveRes = await fetch(`https://streampro.cupto.it/api/resolve-tmpfiles?url=${encodeURIComponent(landingUrl)}`);
  const resolveData = await resolveRes.json();
  if (!resolveRes.ok || !resolveData.url) throw new Error(resolveData.error || 'Link diretto non trovato');
  return resolveData.url;
}

let adminCodesFilter = 'active';

function adminCodeCategory(entry) {
  return isEntryExpired(entry) ? 'expired' : 'active';
}

async function renderAdminCodes() {
  adminCodesListEl.innerHTML = '<p class="admin-list-empty">Caricamento...</p>';
  let blob;
  try {
    blob = await fetchAccessBlob();
  } catch (e) {
    adminCodesListEl.innerHTML = '<p class="admin-list-empty">Errore di caricamento.</p>';
    return;
  }
  const entries = Object.entries(blob.codes)
    .filter(([, entry]) => adminCodeCategory(entry) === adminCodesFilter)
    .sort((a, b) => (b[1].createdAt || '').localeCompare(a[1].createdAt || ''));
  if (entries.length === 0) {
    adminCodesListEl.innerHTML = '<p class="admin-list-empty">Nessun codice in questa scheda</p>';
    return;
  }
  adminCodesListEl.innerHTML = '';
  entries.forEach(([code, entry]) => {
    const hasPlaylist = (entry.host && entry.username && entry.password) || entry.playlistUrl;
    const expired = isEntryExpired(entry);
    const badges = [`<span class="admin-badge ${entry.enabled ? 'on' : 'off'}">${entry.enabled ? 'Abilitato' : 'Disabilitato'}</span>`];
    if (expired) badges.push('<span class="admin-badge off">Scaduto</span>');
    if (hasPlaylist) badges.push('<span class="admin-badge pre">playlist</span>');
    if (entry.special) badges.push('<span class="admin-badge special">speciale</span>');

    const item = document.createElement('div');
    item.className = 'admin-item';
    item.innerHTML = `
      <div class="admin-item-top">
        <span class="admin-item-code">${escapeHtml(code)}</span>
        <span>${escapeHtml(entry.label) || ''}</span>
      </div>
      <div class="admin-item-meta">
        ${entry.expiresAt ? `Scade: ${formatAdminDate(entry.expiresAt)} · ` : ''}${entry.deviceId ? 'Dispositivo agganciato' : 'Dispositivo libero'}
      </div>
      <div class="admin-badges">${badges.join('')}</div>
      <div class="admin-item-actions">
        <button class="secondary-btn toggle-btn">${entry.enabled ? 'Disabilita' : 'Abilita'}</button>
        <button class="secondary-btn expiry-btn">Scadenza</button>
        <button class="secondary-btn playlist-btn">Playlist</button>
        <button class="secondary-btn special-btn">${entry.special ? 'Togli speciale' : 'Rendi speciale'}</button>
        <button class="secondary-btn device-btn" ${entry.deviceId ? '' : 'disabled'}>Sblocca dispositivo</button>
        <button class="secondary-btn share-btn">Condividi</button>
      </div>
    `;
    item.querySelector('.toggle-btn').addEventListener('click', async () => {
      const b = await fetchAccessBlob();
      b.codes[code].enabled = !b.codes[code].enabled;
      await saveAccessBlob(b);
      renderAdminCodes();
    });
    item.querySelector('.expiry-btn').addEventListener('click', () => openAdminExpiryPicker(code, entry.expiresAt));
    item.querySelector('.playlist-btn').addEventListener('click', () => openAdminPlaylistModal(code, entry));
    item.querySelector('.special-btn').addEventListener('click', async () => {
      const b = await fetchAccessBlob();
      b.codes[code].special = !b.codes[code].special;
      await saveAccessBlob(b);
      renderAdminCodes();
    });
    item.querySelector('.device-btn').addEventListener('click', async () => {
      if (!confirm(`Sbloccare "${code}" dal dispositivo attuale?`)) return;
      const b = await fetchAccessBlob();
      delete b.codes[code].deviceId;
      await saveAccessBlob(b);
      renderAdminCodes();
    });
    item.querySelector('.share-btn').addEventListener('click', () => shareAccessCode(code));
    adminCodesListEl.appendChild(item);
  });
}

// Calendario nativo al posto del prompt testuale: un unico input date
// nascosto, riusato per ogni riga.
let adminExpiryTargetCode = null;
function openAdminExpiryPicker(code, currentIso) {
  adminExpiryTargetCode = code;
  adminExpiryPicker.value = currentIso ? currentIso.slice(0, 10) : '';
  if (adminExpiryPicker.showPicker) {
    adminExpiryPicker.showPicker();
  } else {
    adminExpiryPicker.click();
  }
}
adminExpiryPicker.addEventListener('change', async () => {
  if (!adminExpiryTargetCode) return;
  const b = await fetchAccessBlob();
  if (adminExpiryPicker.value) {
    b.codes[adminExpiryTargetCode].expiresAt = new Date(adminExpiryPicker.value + 'T23:59:59').toISOString();
  } else {
    delete b.codes[adminExpiryTargetCode].expiresAt;
  }
  await saveAccessBlob(b);
  renderAdminCodes();
});

// Modale "Playlist" per assegnare/cambiare la playlist di un codice già
// creato, tramite link diretto o file (vedi uploadPlaylistFile).
let adminEditPlaylistMode = 'url';
let adminEditPlaylistTargetCode = null;
let adminEditPlaylistUploadedUrl = null;

function openAdminPlaylistModal(code, entry) {
  adminEditPlaylistTargetCode = code;
  adminEditPlaylistUploadedUrl = null;
  adminPlaylistModalCodeEl.textContent = code;
  adminEditPlaylistUrlInput.value = entry.playlistUrl || '';
  adminEditPlaylistFileInput.value = '';
  adminEditPlaylistFileStatusEl.textContent = '';
  adminEditPlaylistMode = 'url';
  adminEditPlaylistTabsEl.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b.dataset.mode === 'url'));
  document.getElementById('admin-edit-playlist-url').classList.add('active');
  document.getElementById('admin-edit-playlist-file').classList.remove('active');
  adminPlaylistModal.classList.add('active');
}

adminEditPlaylistTabsEl.addEventListener('click', (e) => {
  const btn = e.target.closest('.tab-btn');
  if (!btn) return;
  adminEditPlaylistMode = btn.dataset.mode;
  adminEditPlaylistTabsEl.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b === btn));
  document.getElementById('admin-edit-playlist-url').classList.toggle('active', adminEditPlaylistMode === 'url');
  document.getElementById('admin-edit-playlist-file').classList.toggle('active', adminEditPlaylistMode === 'file');
});

adminEditPlaylistFileInput.addEventListener('change', async () => {
  const file = adminEditPlaylistFileInput.files[0];
  if (!file) return;
  adminEditPlaylistFileStatusEl.textContent = 'Caricamento...';
  try {
    adminEditPlaylistUploadedUrl = await uploadPlaylistFile(file);
    adminEditPlaylistFileStatusEl.textContent = `Caricato: ${file.name}`;
  } catch (err) {
    adminEditPlaylistFileStatusEl.textContent = 'Errore: ' + err.message;
    adminEditPlaylistUploadedUrl = null;
  }
});

adminPlaylistModalCancelBtn.addEventListener('click', () => adminPlaylistModal.classList.remove('active'));
adminPlaylistModal.addEventListener('click', (e) => {
  if (e.target === adminPlaylistModal) adminPlaylistModal.classList.remove('active');
});

adminPlaylistModalRemoveBtn.addEventListener('click', async () => {
  if (!adminEditPlaylistTargetCode) return;
  const b = await fetchAccessBlob();
  delete b.codes[adminEditPlaylistTargetCode].playlistUrl;
  delete b.codes[adminEditPlaylistTargetCode].host;
  delete b.codes[adminEditPlaylistTargetCode].username;
  delete b.codes[adminEditPlaylistTargetCode].password;
  await saveAccessBlob(b);
  adminPlaylistModal.classList.remove('active');
  renderAdminCodes();
});

adminPlaylistModalSaveBtn.addEventListener('click', async () => {
  if (!adminEditPlaylistTargetCode) return;
  const url = adminEditPlaylistMode === 'file' ? adminEditPlaylistUploadedUrl : adminEditPlaylistUrlInput.value.trim();
  if (!url) {
    alert(adminEditPlaylistMode === 'file' ? 'Carica prima un file' : 'Inserisci un link');
    return;
  }
  const b = await fetchAccessBlob();
  b.codes[adminEditPlaylistTargetCode].playlistUrl = url;
  // Un codice ha una sola playlist attiva alla volta: impostando un link
  // diretto si tolgono eventuali credenziali Xtream lasciate da prima.
  delete b.codes[adminEditPlaylistTargetCode].host;
  delete b.codes[adminEditPlaylistTargetCode].username;
  delete b.codes[adminEditPlaylistTargetCode].password;
  await saveAccessBlob(b);
  adminPlaylistModal.classList.remove('active');
  renderAdminCodes();
});

adminCodesTabsEl.addEventListener('click', (e) => {
  const btn = e.target.closest('.tab-btn');
  if (!btn) return;
  adminCodesFilter = btn.dataset.filter;
  adminCodesTabsEl.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b === btn));
  renderAdminCodes();
});

function adminTrialCategory(entry) {
  if (entry.status === 'rejected') return 'rejected';
  if (entry.status === 'active') return isEntryExpired(entry) ? 'expired' : 'active';
  return 'pending';
}

let adminTrialFilter = 'pending';

async function renderAdminTrials() {
  adminTrialsListEl.innerHTML = '<p class="admin-list-empty">Caricamento...</p>';
  let blob;
  try {
    blob = await fetchAccessBlob();
  } catch (e) {
    adminTrialsListEl.innerHTML = '<p class="admin-list-empty">Errore di caricamento.</p>';
    return;
  }
  const entries = Object.entries(blob.devices)
    .filter(([, entry]) => adminTrialCategory(entry) === adminTrialFilter)
    .sort((a, b) => (b[1].requestedAt || '').localeCompare(a[1].requestedAt || ''));
  if (entries.length === 0) {
    adminTrialsListEl.innerHTML = '<p class="admin-list-empty">Nessuna richiesta in questa scheda</p>';
    return;
  }
  adminTrialsListEl.innerHTML = '';
  const badgeByCategory = {
    pending: '<span class="admin-badge off">In attesa</span>',
    active: '<span class="admin-badge on">Attiva</span>',
    expired: '<span class="admin-badge off">Scaduta</span>',
    rejected: '<span class="admin-badge off">Rifiutata</span>'
  };
  entries.forEach(([deviceId, entry]) => {
    const category = adminTrialCategory(entry);
    const item = document.createElement('div');
    item.className = 'admin-item';

    let actionsHtml;
    const durationOptions = `
      <option value="1">1 giorno</option>
      <option value="3">3 giorni</option>
      <option value="7" selected>7 giorni</option>
      <option value="14">14 giorni</option>
      <option value="30">30 giorni</option>
      <option value="0">Senza scadenza</option>
    `;
    if (category === 'pending') {
      actionsHtml = `<select class="duration-select">${durationOptions}</select>
        <button class="secondary-btn activate-btn">Attiva</button>
        <button class="danger-btn reject-btn">Rifiuta</button>`;
    } else if (category === 'active') {
      actionsHtml = `<select class="duration-select">${durationOptions}</select>
        <button class="secondary-btn activate-btn">Rinnova</button>
        <button class="danger-btn reject-btn">Disabilita</button>`;
    } else {
      actionsHtml = `<button class="secondary-btn reactivate-btn">Riporta in attesa</button>`;
    }

    item.innerHTML = `
      <div class="admin-item-top">
        <span>${escapeHtml(entry.label) || '(senza nome)'}</span>
        <span class="admin-item-meta">${deviceId.slice(0, 8)}…</span>
      </div>
      <div class="admin-item-meta">
        ${formatAdminDateTime(entry.requestedAt)}${entry.expiresAt ? ` · Scade: ${formatAdminDate(entry.expiresAt)}` : ''}
      </div>
      <div class="admin-badges">${badgeByCategory[category]}</div>
      <div class="admin-item-actions">${actionsHtml}</div>
    `;
    const activateBtn = item.querySelector('.activate-btn');
    if (activateBtn) activateBtn.addEventListener('click', async () => {
      const days = parseInt(item.querySelector('.duration-select').value, 10);
      const b = await fetchAccessBlob();
      const target = b.devices[deviceId] || {};
      target.status = 'active';
      target.activatedAt = new Date().toISOString();
      if (days > 0) {
        target.expiresAt = new Date(Date.now() + days * 86400000).toISOString();
      } else {
        delete target.expiresAt;
      }
      b.devices[deviceId] = target;
      await saveAccessBlob(b);
      renderAdminTrials();
    });
    const rejectBtn = item.querySelector('.reject-btn');
    if (rejectBtn) rejectBtn.addEventListener('click', async () => {
      const b = await fetchAccessBlob();
      const target = b.devices[deviceId] || {};
      target.status = 'rejected';
      target.rejectedAt = new Date().toISOString();
      b.devices[deviceId] = target;
      await saveAccessBlob(b);
      renderAdminTrials();
    });
    const reactivateBtn = item.querySelector('.reactivate-btn');
    if (reactivateBtn) reactivateBtn.addEventListener('click', async () => {
      const b = await fetchAccessBlob();
      const target = b.devices[deviceId] || {};
      target.status = 'pending';
      delete target.expiresAt;
      b.devices[deviceId] = target;
      await saveAccessBlob(b);
      renderAdminTrials();
    });
    adminTrialsListEl.appendChild(item);
  });
}

openAdminBtn.addEventListener('click', showAdmin);
adminBackBtn.addEventListener('click', backFromAdmin);

adminTrialTabsEl.addEventListener('click', (e) => {
  const btn = e.target.closest('.tab-btn');
  if (!btn) return;
  adminTrialFilter = btn.dataset.filter;
  adminTrialTabsEl.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b === btn));
  renderAdminTrials();
});

// Sezione "Nuovo codice" a comparsa: chiusa di default per lasciare più
// spazio alle richieste di prova, che si consultano più spesso.
adminCreateToggle.addEventListener('click', () => {
  adminCreateBody.classList.toggle('open');
  adminCreateChevron.classList.toggle('open');
});

let adminNewPlaylistMode = 'xtream';
let adminNewPlaylistUploadedUrl = null;

adminNewPlaylistTabsEl.addEventListener('click', (e) => {
  const btn = e.target.closest('.tab-btn');
  if (!btn) return;
  adminNewPlaylistMode = btn.dataset.mode;
  adminNewPlaylistTabsEl.querySelectorAll('.tab-btn').forEach(b => b.classList.toggle('active', b === btn));
  document.getElementById('admin-new-playlist-xtream').classList.toggle('active', adminNewPlaylistMode === 'xtream');
  document.getElementById('admin-new-playlist-url').classList.toggle('active', adminNewPlaylistMode === 'url');
  document.getElementById('admin-new-playlist-file').classList.toggle('active', adminNewPlaylistMode === 'file');
});

adminNewPlaylistFileInput.addEventListener('change', async () => {
  const file = adminNewPlaylistFileInput.files[0];
  if (!file) return;
  adminNewPlaylistFileStatusEl.textContent = 'Caricamento...';
  try {
    adminNewPlaylistUploadedUrl = await uploadPlaylistFile(file);
    adminNewPlaylistFileStatusEl.textContent = `Caricato: ${file.name}`;
  } catch (err) {
    adminNewPlaylistFileStatusEl.textContent = 'Errore: ' + err.message;
    adminNewPlaylistUploadedUrl = null;
  }
});

adminCreateBtn.addEventListener('click', async () => {
  // Se il modulo è ancora chiuso, il primo tocco lo apre e basta: evita di
  // creare per sbaglio un codice vuoto senza che l'admin l'abbia notato.
  if (!adminCreateBody.classList.contains('open')) {
    adminCreateBody.classList.add('open');
    adminCreateChevron.classList.add('open');
    return;
  }

  const code = (adminNewCodeInput.value.trim() || randomAccessCode()).toUpperCase();
  const label = adminNewLabelInput.value.trim();
  const expiry = adminNewExpiryInput.value;
  const special = adminNewSpecialInput.checked;

  adminCreateBtn.textContent = 'Salvataggio...';
  try {
    const b = await fetchAccessBlob();
    b.codes[code] = { enabled: true, label, createdAt: new Date().toISOString() };
    if (expiry) b.codes[code].expiresAt = new Date(expiry + 'T23:59:59').toISOString();
    if (special) b.codes[code].special = true;

    if (adminNewPlaylistMode === 'xtream') {
      const host = adminNewHostInput.value.trim();
      const username = adminNewUserInput.value.trim();
      const password = adminNewPassInput.value.trim();
      if (host && username && password) {
        b.codes[code].host = host;
        b.codes[code].username = username;
        b.codes[code].password = password;
      }
    } else if (adminNewPlaylistMode === 'url') {
      const url = adminNewPlaylistUrlInput.value.trim();
      if (url) b.codes[code].playlistUrl = url;
    } else if (adminNewPlaylistMode === 'file') {
      if (!adminNewPlaylistUploadedUrl) {
        alert('Carica prima il file playlist, o cambia scheda.');
        adminCreateBtn.textContent = 'Crea codice';
        return;
      }
      b.codes[code].playlistUrl = adminNewPlaylistUploadedUrl;
    }

    await saveAccessBlob(b);
    adminNewCodeInput.value = '';
    adminNewLabelInput.value = '';
    adminNewExpiryInput.value = '';
    adminNewSpecialInput.checked = false;
    adminNewHostInput.value = '';
    adminNewUserInput.value = '';
    adminNewPassInput.value = '';
    adminNewPlaylistUrlInput.value = '';
    adminNewPlaylistFileInput.value = '';
    adminNewPlaylistFileStatusEl.textContent = '';
    adminNewPlaylistUploadedUrl = null;
    renderAdminCodes();
    shareAccessCode(code);
  } catch (err) {
    alert('Errore: ' + err.message);
  }
  adminCreateBtn.textContent = 'Crea codice';
});

// Inizializzazione: si parte sempre dalla schermata di selezione playlist
updateCounts();
updateHomeStatus();
renderRecentPlaylists();
renderXtreamProfiles();
refreshAccessState();

// Pannello admin e app comunicano solo tramite il blob condiviso: senza un
// controllo periodico, un'attivazione o una disabilitazione fatta da Antonio
// resterebbe invisibile finché l'utente non riapre l'app o preme refresh a
// mano. Ricontrolliamo lo stato di accesso ogni 30 secondi per tutta la
// sessione, così un'attivazione sblocca da sola e una revoca riporta subito
// alla home (vedi setUnlocked).
setInterval(refreshAccessState, 30000);

checkForUpdate();

// ---------- Navigazione da telecomando (box TV) ----------
// L'app è fatta per tocco: righe canale/categoria sono <li>/<div> con solo
// un click handler, mai selezionabili da tastiera/D-pad. Su un telecomando
// che sposta un puntatore, senza singoli bersagli "agganciabili" il cursore
// finisce per selezionare l'intero riquadro invece della singola riga
// (segnalato dall'utente: "a sinistra seleziona tutto il riquadro invece
// delle categorie"). Fix: ogni riga diventa un vero elemento a fuoco
// (tabindex), con un contorno visibile e Invio/OK che attiva lo stesso
// click del tocco — sia per i telecomandi D-pad puri sia per quelli che
// emulano un puntatore ma si aspettano un elemento preciso su cui atterrare.
const TV_FOCUSABLE_SELECTOR = '.channel-item, .category-item, .playlist-chip, .xtream-profile-row, .admin-item, .tab-btn';

function makeFocusable(root) {
  if (!root.querySelectorAll) return;
  root.querySelectorAll(TV_FOCUSABLE_SELECTOR).forEach(el => {
    if (!el.hasAttribute('tabindex')) el.setAttribute('tabindex', '0');
  });
}

makeFocusable(document);
new MutationObserver((mutations) => {
  mutations.forEach(m => {
    m.addedNodes.forEach(node => {
      if (node.nodeType !== 1) return;
      if (node.matches && node.matches(TV_FOCUSABLE_SELECTOR) && !node.hasAttribute('tabindex')) {
        node.setAttribute('tabindex', '0');
      }
      makeFocusable(node);
    });
  });
}).observe(document.body, { childList: true, subtree: true });

// Frecce del D-pad: senza questo, la tastiera/telecomando non ha alcun modo
// nativo di spostare il fuoco tra righe (il browser non lo fa da solo per
// elementi qualsiasi, solo per pochi controlli nativi come <select>) — le
// frecce finivano per scorrere l'intero riquadro come fosse un solo blocco
// invece di muoversi riga per riga (segnalato dall'utente sia per le
// categorie sia per i canali). Su/Giù si muovono tra i "fratelli" dello
// stesso elenco; Destra/Sinistra passano dal pannello categorie a quello
// canali e viceversa (gli unici due elenchi affiancati nell'app).
function moveTvFocus(direction) {
  const el = document.activeElement;
  if (!el || !el.matches || !el.matches(TV_FOCUSABLE_SELECTOR)) return false;

  if (direction === 'down' || direction === 'up') {
    let sibling = direction === 'down' ? el.nextElementSibling : el.previousElementSibling;
    while (sibling && !sibling.matches(TV_FOCUSABLE_SELECTOR)) {
      sibling = direction === 'down' ? sibling.nextElementSibling : sibling.previousElementSibling;
    }
    if (!sibling) return false;
    sibling.focus();
    sibling.scrollIntoView({ block: 'nearest' });
    return true;
  }

  if (direction === 'right' && el.closest('#categories-panel')) {
    const target = mainListEl.querySelector('.channel-item.active') || mainListEl.querySelector('.channel-item');
    if (!target) return false;
    target.focus();
    target.scrollIntoView({ block: 'nearest' });
    return true;
  }

  if (direction === 'left' && el.closest('#main-list')) {
    const target = categoriesPanelEl.querySelector('.category-item.active') || categoriesPanelEl.querySelector('.category-item');
    if (!target) return false;
    target.focus();
    target.scrollIntoView({ block: 'nearest' });
    return true;
  }

  return false;
}

const TV_ARROW_DIRECTIONS = { ArrowDown: 'down', ArrowUp: 'up', ArrowLeft: 'left', ArrowRight: 'right' };

document.addEventListener('keydown', (e) => {
  if (TV_ARROW_DIRECTIONS[e.key]) {
    if (moveTvFocus(TV_ARROW_DIRECTIONS[e.key])) e.preventDefault();
    return;
  }

  // Invio/Select su un elemento a fuoco che non è già un <button>/<a> nativo
  // (quelli il browser li attiva già da solo con Invio) attiva lo stesso
  // click gestito dal tocco, così telecomandi D-pad puri (senza puntatore)
  // possono usare l'app oltre a quelli con cursore emulato. Due Invio
  // ravvicinati sulla stessa riga canale attivano da soli lo schermo intero:
  // non serve simulare qui un "dblclick" apposta, il click handler della
  // riga (vedi renderChannels) riconosce già da solo due pressioni
  // ravvicinate sullo stesso canale, arrivino da un vero doppio clic o da
  // due .click() separati come questo.
  if (e.key !== 'Enter' && e.key !== ' ') return;
  const el = document.activeElement;
  if (!el || el === document.body) return;
  const tag = el.tagName;
  if (tag === 'BUTTON' || tag === 'A' || tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') return;
  e.preventDefault();
  el.click();
});

// Tasto indietro del telecomando/hardware Android: senza questo listener non
// fa letteralmente nulla (nessun comportamento di default utile in una SPA
// senza voci di history reali). Priorità: chiudi il pannello admin se aperto,
// poi torna alla home se si è nella schermata canali, altrimenti minimizza
// l'app (comportamento standard Android sulla schermata radice, non la
// chiude del tutto).
App.addListener('backButton', () => {
  if (adminScreen.classList.contains('active')) {
    backFromAdmin();
  } else if (browseScreen.classList.contains('active')) {
    showHome();
  } else {
    App.minimizeApp();
  }
});
