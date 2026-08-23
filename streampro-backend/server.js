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
  const res = await fetch(targetUrl);
  const contents = await res.text();
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
