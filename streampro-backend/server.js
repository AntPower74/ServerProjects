const http = require('http');
const fs = require('fs');
const path = require('path');
const dns = require('dns').promises;
const net = require('net');

const PORT = 4400;
const DATA_FILE = path.join(__dirname, 'data', 'access.json');

function readBlob() {
  try {
    const raw = fs.readFileSync(DATA_FILE, 'utf8');
    const data = JSON.parse(raw);
    return { codes: data.codes || {}, devices: data.devices || {} };
  } catch (e) {
    return { codes: {}, devices: {} };
  }
}

function writeBlob(blob) {
  const safe = { codes: blob.codes || {}, devices: blob.devices || {} };
  fs.writeFileSync(DATA_FILE, JSON.stringify(safe));
  return safe;
}

// tmpfiles.org non manda header CORS sulla pagina di destinazione del file
// caricato (solo sull'endpoint di upload), quindi il browser non può leggerla
// direttamente per estrarne il link binario diretto. Prima si usava un proxy
// CORS di terze parti (allorigins.win), che ha smesso di mandare i propri
// header CORS — questo endpoint lo sostituisce facendo la richiesta lato
// server, dove il CORS del browser non si applica.
async function resolveTmpfilesLink(landingUrl) {
  if (!/^https:\/\/tmpfiles\.org\//.test(landingUrl)) {
    throw new Error('URL non valido');
  }
  const pageRes = await fetch(landingUrl);
  const html = await pageRes.text();
  const match = html.match(/https:\/\/tmpfiles\.org\/dl\/[^"'\s]+/);
  if (!match) throw new Error('Link diretto non trovato');
  return match[0];
}

// Blocca IP privati/loopback/link-local: questo endpoint fa da proxy verso
// URL playlist scelti dall'utente (host IPTV di terzi), non deve poter essere
// usato per raggiungere servizi interni di questa VPS (SSRF).
function isPrivateIp(ip) {
  if (net.isIPv4(ip)) {
    const [a, b] = ip.split('.').map(Number);
    if (a === 127 || a === 10 || a === 0) return true;
    if (a === 169 && b === 254) return true;
    if (a === 172 && b >= 16 && b <= 31) return true;
    if (a === 192 && b === 168) return true;
    return false;
  }
  return ip === '::1' || ip.startsWith('fe80:') || ip.startsWith('fc') || ip.startsWith('fd');
}

async function fetchPlaylistContents(targetUrl) {
  let parsed;
  try {
    parsed = new URL(targetUrl);
  } catch (e) {
    throw new Error('URL non valido');
  }
  if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
    throw new Error('URL non valido');
  }
  const { address } = await dns.lookup(parsed.hostname);
  if (isPrivateIp(address)) {
    throw new Error('URL non consentito');
  }

  const ua = 'IPTVSmartersPro/3.1.5.1 (Linux; Android 11)';
  let contents = '';
  let success = false;

  // 1. Prova il download diretto della playlist con User-Agent IPTV
  try {
    const res = await fetch(targetUrl, {
      headers: {
        'User-Agent': ua,
        'Accept': '*/*'
      }
    });
    if (res.ok) {
      contents = await res.text();
      if (contents.includes('#EXTINF')) {
        success = true;
      }
    }
  } catch (err) {
    console.warn('Download diretto playlist fallito:', err.message);
  }

  // 2. Fallback Xtream API: se il server IPTV blocca get.php (errore 885/461/ecc.)
  // ma supporta le API Xtream (player_api.php), generiamo noi la playlist M3U al volo.
  if (!success) {
    const username = parsed.searchParams.get('username');
    const password = parsed.searchParams.get('password');
    if (username && password) {
      const base = `${parsed.protocol}//${parsed.host}`;
      const encUser = encodeURIComponent(username);
      const encPass = encodeURIComponent(password);

      try {
        const [catsRes, streamsRes, vodCatsRes, vodStreamsRes] = await Promise.all([
          fetch(`${base}/player_api.php?username=${encUser}&password=${encPass}&action=get_live_categories`, { headers: { 'User-Agent': ua } }).catch(() => null),
          fetch(`${base}/player_api.php?username=${encUser}&password=${encPass}&action=get_live_streams`, { headers: { 'User-Agent': ua } }).catch(() => null),
          fetch(`${base}/player_api.php?username=${encUser}&password=${encPass}&action=get_vod_categories`, { headers: { 'User-Agent': ua } }).catch(() => null),
          fetch(`${base}/player_api.php?username=${encUser}&password=${encPass}&action=get_vod_streams`, { headers: { 'User-Agent': ua } }).catch(() => null)
        ]);

        const cats = catsRes && catsRes.ok ? await catsRes.json().catch(() => []) : [];
        const streams = streamsRes && streamsRes.ok ? await streamsRes.json().catch(() => []) : [];
        const vodCats = vodCatsRes && vodCatsRes.ok ? await vodCatsRes.json().catch(() => []) : [];
        const vodStreams = vodStreamsRes && vodStreamsRes.ok ? await vodStreamsRes.json().catch(() => []) : [];

        if (Array.isArray(streams) && streams.length > 0) {
          const catMap = new Map();
          if (Array.isArray(cats)) {
            for (const c of cats) {
              if (c && c.category_id) catMap.set(String(c.category_id), c.category_name || 'Altro');
            }
          }
          const vodCatMap = new Map();
          if (Array.isArray(vodCats)) {
            for (const c of vodCats) {
              if (c && c.category_id) vodCatMap.set(String(c.category_id), c.category_name || 'Film');
            }
          }

          const lines = [`#EXTM3U url-tvg="${base}/xmltv.php?username=${encUser}&password=${encPass}"`];
          for (const s of streams) {
            if (!s || !s.stream_id) continue;
            const cat = catMap.get(String(s.category_id)) || 'Canali';
            const logo = s.stream_icon || '';
            const epg = s.epg_channel_id || '';
            const name = (s.name || 'Canale').trim();
            const sid = s.stream_id;
            const streamUrl = `${base}/live/${encUser}/${encPass}/${sid}.ts`;
            lines.push(`#EXTINF:-1 tvg-id="${epg}" tvg-logo="${logo}" group-title="${cat}",${name}`);
            lines.push(streamUrl);
          }

          if (Array.isArray(vodStreams)) {
            for (const v of vodStreams) {
              if (!v || !v.stream_id) continue;
              const cat = vodCatMap.get(String(v.category_id)) || 'Film';
              const logo = v.stream_icon || '';
              const name = (v.name || 'Film').trim();
              const sid = v.stream_id;
              const ext = v.container_extension || 'mp4';
              const streamUrl = `${base}/movie/${encUser}/${encPass}/${sid}.${ext}`;
              lines.push(`#EXTINF:-1 tvg-id="" tvg-logo="${logo}" group-title="${cat}",[FILM] ${name}`);
              lines.push(streamUrl);
            }
          }

          contents = lines.join('\n');
          success = true;
        }
      } catch (xtreamErr) {
        console.warn('Errore fallback Xtream API:', xtreamErr);
      }
    }
  }

  if (!success && !contents) {
    throw new Error('Impossibile scaricare o elaborare la playlist');
  }

  return contents;
}

const server = http.createServer((req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, PUT, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  const { pathname, searchParams } = new URL(req.url, 'http://localhost');

  if (pathname === '/resolve-tmpfiles' && req.method === 'GET') {
    const landingUrl = searchParams.get('url') || '';
    resolveTmpfilesLink(landingUrl)
      .then((url) => {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ url }));
      })
      .catch((e) => {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: e.message }));
      });
    return;
  }

  if (pathname === '/proxy-fetch' && req.method === 'GET') {
    const targetUrl = searchParams.get('url') || '';
    fetchPlaylistContents(targetUrl)
      .then((contents) => {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ contents }));
      })
      .catch((e) => {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: e.message }));
      });
    return;
  }

  if (pathname !== '/access-blob') {
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'not found' }));
    return;
  }

  if (req.method === 'GET') {
    const blob = readBlob();
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(blob));
    return;
  }

  if (req.method === 'PUT') {
    let body = '';
    req.on('data', (chunk) => { body += chunk; });
    req.on('end', () => {
      try {
        const parsed = JSON.parse(body);
        const saved = writeBlob(parsed);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(saved));
      } catch (e) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'invalid json' }));
      }
    });
    return;
  }

  res.writeHead(405, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'method not allowed' }));
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`streampro-backend listening on 127.0.0.1:${PORT}`);
});
