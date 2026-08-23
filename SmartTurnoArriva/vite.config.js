import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SERVER_START_TIME = Date.now().toString();

// --- Auth backend (email + PIN) ---------------------------------------
// Dati salvati su file locale (server-data/, escluso da git e mai bundlato
// nel client): niente servizio esterno terzo, niente scadenze a sorpresa.
const DATA_DIR = path.join(__dirname, 'server-data');
const USERS_FILE = path.join(DATA_DIR, 'users.json');
const ADMIN_KEY_FILE = path.join(DATA_DIR, 'admin-key.txt');
const VERSION_FILE = path.join(DATA_DIR, 'version.json');

function readUsers() {
  try {
    const db = JSON.parse(fs.readFileSync(USERS_FILE, 'utf-8'));
    if (!db.allowedEmails) db.allowedEmails = [];
    return db;
  } catch {
    return { users: {}, allowedEmails: [] };
  }
}
function writeUsers(db) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(USERS_FILE, JSON.stringify(db, null, 2));
}
function readAdminKey() {
  try {
    return fs.readFileSync(ADMIN_KEY_FILE, 'utf-8').trim();
  } catch {
    return null;
  }
}
function sendJson(res, status, obj) {
  res.statusCode = status;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify(obj));
}
function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', (chunk) => { data += chunk; });
    req.on('end', () => {
      try { resolve(data ? JSON.parse(data) : {}); }
      catch (e) { reject(e); }
    });
    req.on('error', reject);
  });
}
const normEmail = (e) => String(e || '').trim().toLowerCase();
// Solo esadecimale: elimina qualunque spazio/carattere invisibile che
// un copia-incolla da chat/mobile puo' introdurre e che .trim() da solo
// non rimuoverebbe (es. spazi unicode, zero-width space).
const normKey = (k) => String(k || '').replace(/[^0-9a-fA-F]/g, '');
const PIN_RE = /^\d{4,6}$/;

const authApiPlugin = () => ({
  name: 'auth-api',
  configureServer(server) {
    // L'app nativa chiama questo server da un'altra origine
    // (capacitor://localhost o https://localhost) - senza CORS il
    // WebView blocca silenziosamente le fetch con "Failed to fetch".
    server.middlewares.use('/api', (req, res, next) => {
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
      if (req.method === 'OPTIONS') { res.statusCode = 204; return res.end(); }
      next();
    });

    // Vite non associa un content-type a .apk: senza questo header i
    // browser mobile non riconoscono il file come installabile e
    // finiscono per salvare la pagina intera invece del binario.
    server.middlewares.use('/smartturnoarriva.apk', (_req, res) => {
      // NB: deve stare fuori da public/ -- Vite copia tutto cio' che c'e' in
      // public/ dentro il bundle dell'app (dist/ -> assets Android), quindi
      // se l'apk fosse li' dentro ogni nuova build includerebbe se stessa
      // (e la build precedente inclusa in quella, ecc: crescita a bambola
      // russa, ~5.4MB -> 10.5MB -> 15.6MB in 3 build, probabile causa dei
      // problemi di installazione riportati dopo l'auto-update in-app).
      // Il nome file include la versione corrente (letta da version.json)
      // cosi' ogni release resta un file distinto nella cartella release/
      // invece di sovrascrivere sempre lo stesso smartturnoarriva.apk.
      let versionName = 'unknown';
      try { versionName = JSON.parse(fs.readFileSync(VERSION_FILE, 'utf-8')).versionName; } catch {}
      const fileName = `smartturnoarriva-${versionName}.apk`;
      const apkPath = path.join(__dirname, 'release', fileName);
      let stat;
      try { stat = fs.statSync(apkPath); } catch { res.statusCode = 404; return res.end('Not found'); }
      res.setHeader('Content-Type', 'application/vnd.android.package-archive');
      res.setHeader('Content-Disposition', `attachment; filename="${fileName}"`);
      res.setHeader('Content-Length', stat.size);
      fs.createReadStream(apkPath).pipe(res);
    });

    server.middlewares.use('/api/auth/exists', (req, res) => {
      const url = new URL(req.url, 'http://x');
      const email = normEmail(url.searchParams.get('email'));
      const db = readUsers();
      sendJson(res, 200, { exists: !!db.users[email] });
    });

    server.middlewares.use('/api/auth/register', async (req, res) => {
      if (req.method !== 'POST') return sendJson(res, 405, { ok: false, reason: 'method' });
      let body;
      try { body = await readBody(req); } catch { return sendJson(res, 400, { ok: false, reason: 'badrequest' }); }
      const email = normEmail(body.email);
      const pin = String(body.pin || '');
      if (!email || !email.includes('@')) return sendJson(res, 400, { ok: false, reason: 'bademail' });
      if (!PIN_RE.test(pin)) return sendJson(res, 400, { ok: false, reason: 'badpin' });
      const db = readUsers();
      if (db.users[email]) return sendJson(res, 409, { ok: false, reason: 'exists' });
      if (!db.allowedEmails.includes(email)) return sendJson(res, 403, { ok: false, reason: 'notallowed' });
      db.users[email] = { pin, createdAt: new Date().toISOString() };
      writeUsers(db);
      sendJson(res, 200, { ok: true });
    });

    server.middlewares.use('/api/auth/check', async (req, res) => {
      if (req.method !== 'POST') return sendJson(res, 405, { ok: false, reason: 'method' });
      let body;
      try { body = await readBody(req); } catch { return sendJson(res, 400, { ok: false, reason: 'badrequest' }); }
      const email = normEmail(body.email);
      const pin = String(body.pin || '');
      const db = readUsers();
      const user = db.users[email];
      if (!user) return sendJson(res, 200, { ok: false, reason: 'notfound' });
      if (user.pin !== pin) return sendJson(res, 200, { ok: false, reason: 'wrongpin' });
      sendJson(res, 200, { ok: true });
    });

    // Solo per l'amministratore (Antonio): recupero PIN da comunicare
    // manualmente all'autista che lo ha perso. Richiede la admin key,
    // che non e' mai spedita al bundle client/APK.
    server.middlewares.use('/api/auth/admin/lookup', (req, res) => {
      const url = new URL(req.url, 'http://x');
      const key = normKey(url.searchParams.get('key'));
      const adminKey = readAdminKey();
      if (!adminKey || key !== adminKey) return sendJson(res, 403, { ok: false, reason: 'forbidden' });
      const email = normEmail(url.searchParams.get('email'));
      const db = readUsers();
      const user = db.users[email];
      if (!user) return sendJson(res, 404, { ok: false, reason: 'notfound' });
      sendJson(res, 200, { ok: true, pin: user.pin, createdAt: user.createdAt });
    });

    // Manifest di aggiornamento per l'app nativa: confronta il proprio
    // versionCode (src/version.js) con quello qui e propone il download
    // della nuova APK se e' piu' recente.
    server.middlewares.use('/api/update/manifest', (_req, res) => {
      let manifest = { versionCode: 1, versionName: '1.0' };
      try { manifest = JSON.parse(fs.readFileSync(VERSION_FILE, 'utf-8')); } catch {}
      sendJson(res, 200, manifest);
    });

    server.middlewares.use('/api/auth/admin/list', (req, res) => {
      const url = new URL(req.url, 'http://x');
      const key = normKey(url.searchParams.get('key'));
      const adminKey = readAdminKey();
      if (!adminKey || key !== adminKey) return sendJson(res, 403, { ok: false, reason: 'forbidden' });
      const db = readUsers();
      const list = Object.entries(db.users).map(([email, u]) => ({ email, createdAt: u.createdAt }));
      sendJson(res, 200, { ok: true, users: list });
    });

    // Whitelist: solo le email qui dentro possono completare la
    // registrazione (creare un PIN). L'admin le aggiunge da qui prima
    // che l'autista apra l'app la prima volta.
    server.middlewares.use('/api/auth/admin/allowlist', async (req, res) => {
      const url = new URL(req.url, 'http://x');
      const key = req.method === 'GET' ? normKey(url.searchParams.get('key')) : null;
      const db = readUsers();

      if (req.method === 'GET') {
        const adminKey = readAdminKey();
        if (!adminKey || key !== adminKey) return sendJson(res, 403, { ok: false, reason: 'forbidden' });
        return sendJson(res, 200, { ok: true, allowedEmails: db.allowedEmails });
      }

      let body;
      try { body = await readBody(req); } catch { return sendJson(res, 400, { ok: false, reason: 'badrequest' }); }
      const adminKey = readAdminKey();
      if (!adminKey || normKey(body.key) !== adminKey) return sendJson(res, 403, { ok: false, reason: 'forbidden' });
      const email = normEmail(body.email);
      if (!email || !email.includes('@')) return sendJson(res, 400, { ok: false, reason: 'bademail' });

      if (req.method === 'POST') {
        if (!db.allowedEmails.includes(email)) db.allowedEmails.push(email);
        writeUsers(db);
        return sendJson(res, 200, { ok: true, allowedEmails: db.allowedEmails });
      }
      if (req.method === 'DELETE') {
        db.allowedEmails = db.allowedEmails.filter((e) => e !== email);
        writeUsers(db);
        return sendJson(res, 200, { ok: true, allowedEmails: db.allowedEmails });
      }
      sendJson(res, 405, { ok: false, reason: 'method' });
    });
  },
});

// --- Cache locale dei fogli Google (CSV) --------------------------------
// Il CSV principale e' ~2MB/1367 righe e Google Sheets impiega anche 10-12s
// a rispondere: prima lo scaricava direttamente il client ad ogni apertura
// dell'app. Ora lo scarica il server in background ogni 5 minuti e lo tiene
// in memoria, cosi' l'app lo riceve all'istante dalla nostra cache.
const GOOGLE_CSV_URL = "https://docs.google.com/spreadsheets/d/11hI0MBC6IMG5D8Sq7izljFElj2kazgQjSsjZTCCC42U/export?format=csv&gid=991701353";
const GOOGLE_LEGEND_URL = "https://docs.google.com/spreadsheets/d/1wFsrbqZn8fyiDzucjfrT9qT1prOk_gH0exriiG93F3w/export?format=csv";
const GOOGLE_ORARI_URL = "https://docs.google.com/spreadsheets/d/11hI0MBC6IMG5D8Sq7izljFElj2kazgQjSsjZTCCC42U/export?format=csv&gid=1068773424";
const SHEETS_REFRESH_MS = 5 * 60 * 1000;

const sheetsCache = { csv: null, legend: null, orari: null, updatedAt: null };

async function refreshSheetsCache() {
  try {
    const [csv, legend, orari] = await Promise.all([
      fetch(GOOGLE_CSV_URL).then((r) => r.text()),
      fetch(GOOGLE_LEGEND_URL).then((r) => r.text()),
      fetch(GOOGLE_ORARI_URL).then((r) => r.text()),
    ]);
    sheetsCache.csv = csv;
    sheetsCache.legend = legend;
    sheetsCache.orari = orari;
    sheetsCache.updatedAt = new Date().toISOString();
    console.log(`[sheets-cache] aggiornata alle ${sheetsCache.updatedAt}`);
  } catch (err) {
    // Se il refresh fallisce teniamo la cache precedente (meglio dati
    // leggermente vecchi che nessun dato).
    console.error('[sheets-cache] refresh fallito:', err.message);
  }
}

const sheetsCachePlugin = () => ({
  name: 'sheets-cache',
  configureServer(server) {
    refreshSheetsCache();
    setInterval(refreshSheetsCache, SHEETS_REFRESH_MS);

    const serveCached = (key) => (_req, res) => {
      if (!sheetsCache[key]) {
        res.statusCode = 503;
        return res.end('Cache non ancora pronta, riprova tra poco.');
      }
      res.setHeader('Content-Type', 'text/csv; charset=utf-8');
      res.setHeader('X-Cache-Updated-At', sheetsCache.updatedAt);
      res.end(sheetsCache[key]);
    };

    server.middlewares.use('/api/data/csv', serveCached('csv'));
    server.middlewares.use('/api/data/legend', serveCached('legend'));
    server.middlewares.use('/api/data/orari', serveCached('orari'));
  },
});

// --- Arriva Live Services Cache & API ---------------------------------
const ARRIVA_AREAS = {
  torino: 'https://torino.arriva.it',
  brescia: 'https://brescia.arriva.it',
  bergamo: 'https://bergamo.arriva.it',
  cremona: 'https://cremona.arriva.it',
  aosta: 'https://aosta.arriva.it',
};

const arrivaCache = {
  notices: {},
  lines: {},
};

function decodeHtml(html) {
  if (!html) return '';
  return html
    .replace(/&#8211;/g, '–')
    .replace(/&#8212;/g, '—')
    .replace(/&#8220;/g, '“')
    .replace(/&#8221;/g, '”')
    .replace(/&#8216;/g, '‘')
    .replace(/&#8217;/g, '’')
    .replace(/&#038;/g, '&')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#039;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&nbsp;/g, ' ');
}

function extractLines(text) {
  if (!text) return [];
  const matches = text.match(/(?:linea|autolinea|autolinee|corse?)\s*([0-9]{1,4}[a-z]?)/gi) || [];
  const lines = new Set();
  matches.forEach(m => {
    const num = m.replace(/(?:linea|autolinea|autolinee|corse?)\s*/i, '').trim();
    if (num) lines.add(num.toUpperCase());
  });
  return Array.from(lines);
}

async function fetchArrivaNotices(area = 'torino') {
  const baseUrl = ARRIVA_AREAS[area] || ARRIVA_AREAS.torino;
  const now = Date.now();
  const cached = arrivaCache.notices[area];
  if (cached && (now - cached.timestamp < 3 * 60 * 1000)) {
    return cached.data;
  }

  try {
    const res = await fetch(`${baseUrl}/wp-json/wp/v2/notice?per_page=30`, {
      headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' },
      signal: AbortSignal.timeout(10000)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const list = await res.json();
    
    const formatted = (Array.isArray(list) ? list : []).map(item => {
      const title = decodeHtml(item.title?.rendered || '');
      const content = item.content?.rendered || '';
      const excerpt = decodeHtml(item.excerpt?.rendered || '').replace(/<[^>]+>/g, '').trim();
      const lines = extractLines(`${title} ${excerpt}`);
      
      let type = 'general';
      const lower = `${title} ${excerpt}`.toLowerCase();
      if (lower.includes('sciopero')) type = 'strike';
      else if (lower.includes('deviazione') || lower.includes('sospensione') || lower.includes('variazione') || lower.includes('modifica')) type = 'detour';
      else if (lower.includes('lavori') || lower.includes('cantiere') || lower.includes('chiusura')) type = 'roadwork';

      return {
        id: item.id,
        date: item.date,
        modified: item.modified,
        title,
        excerpt,
        content,
        link: item.link,
        lines,
        type,
        area
      };
    });

    arrivaCache.notices[area] = { data: formatted, timestamp: now };
    return formatted;
  } catch (err) {
    console.error(`[arriva-api] errore fetch notices (${area}):`, err.message);
    return cached ? cached.data : [];
  }
}

async function fetchArrivaLines(area = 'torino') {
  const baseUrl = ARRIVA_AREAS[area] || ARRIVA_AREAS.torino;
  const now = Date.now();
  const cached = arrivaCache.lines[area];
  if (cached && (now - cached.timestamp < 15 * 60 * 1000)) {
    return cached.data;
  }

  try {
    const res = await fetch(`${baseUrl}/wp-json/wp/v2/line?per_page=100`, {
      headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' },
      signal: AbortSignal.timeout(12000)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const list = await res.json();

    const formatted = (Array.isArray(list) ? list : []).map(item => {
      const title = decodeHtml(item.title?.rendered || '');
      const acf = item.acf || {};
      return {
        id: item.id,
        title,
        code: acf.public_code || acf.internal_code || '',
        internalCode: acf.internal_code || '',
        timetablePdf: acf.timetable_attached_file || null,
        mapUrl: acf.map_external_link || null,
        kmlUrl: acf.map_kml_layer_file || null,
        link: item.link,
        area
      };
    });

    arrivaCache.lines[area] = { data: formatted, timestamp: now };
    return formatted;
  } catch (err) {
    console.error(`[arriva-api] errore fetch lines (${area}):`, err.message);
    return cached ? cached.data : [];
  }
}

const arrivaApiPlugin = () => ({
  name: 'arriva-api',
  configureServer(server) {
    // Download APK Arriva MyPay
    server.middlewares.use('/api/download/arriva-mypay.apk', (_req, res) => {
      const apkPath = path.join(__dirname, 'Arriva_MyPay_base.apk');
      let stat;
      try { stat = fs.statSync(apkPath); } catch { res.statusCode = 404; return res.end('APK Arriva MyPay non trovato sul server'); }
      res.setHeader('Content-Type', 'application/vnd.android.package-archive');
      res.setHeader('Content-Disposition', 'attachment; filename="Arriva_MyPay.apk"');
      res.setHeader('Content-Length', stat.size);
      fs.createReadStream(apkPath).pipe(res);
    });

    // Avvisi ufficiali Arriva
    server.middlewares.use('/api/arriva/notices', async (req, res) => {
      const url = new URL(req.url, 'http://x');
      const area = url.searchParams.get('area') || 'torino';
      const notices = await fetchArrivaNotices(area);
      sendJson(res, 200, { ok: true, area, count: notices.length, notices });
    });

    // Linee e prospetti orari PDF ufficiali Arriva
    server.middlewares.use('/api/arriva/lines', async (req, res) => {
      const url = new URL(req.url, 'http://x');
      const area = url.searchParams.get('area') || 'torino';
      const lines = await fetchArrivaLines(area);
      sendJson(res, 200, { ok: true, area, count: lines.length, lines });
    });
  }
});

// Plugin per disabilitare la cache su tutti i dispositivi
const noCachePlugin = () => ({
  name: 'no-cache-headers',
  configureServer(server) {
    // Endpoint versione — cambia ad ogni riavvio del server
    server.middlewares.use('/version', (_req, res) => {
      res.setHeader('Content-Type', 'application/json');
      res.setHeader('Cache-Control', 'no-store');
      res.end(JSON.stringify({ v: SERVER_START_TIME }));
    });
    // Header no-cache su tutte le risorse
    server.middlewares.use((_req, res, next) => {
      res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
      res.setHeader('Pragma', 'no-cache');
      res.setHeader('Expires', '0');
      next();
    });
  },
});


export default defineConfig({
  plugins: [
    react(),
    noCachePlugin(),
    authApiPlugin(),
    sheetsCachePlugin(),
    arrivaApiPlugin(),
  ],
  server: {
    host: '0.0.0.0',
    allowedHosts: true,
  }
})
