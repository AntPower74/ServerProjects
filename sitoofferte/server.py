import os
import re
import json
import asyncio
import httpx
import shutil
import datetime
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

BASE         = '/home/antonio/sitoofferte'
SITO_DIR     = BASE
FILE_OFFERTE = f'{BASE}/offerte.json'
FILE_COUPON  = f'{BASE}/coupon_live.json'
FILE_ORDINI  = f'{BASE}/ordini.json'
FILE_CONTATTI= f'{BASE}/richieste_clienti.json'

# ── Logica anti-duplicati ─────────────────────────────────────────────────────

def _normalizza(titolo: str) -> str:
    return re.sub(r'[^a-z0-9]', '', titolo.lower())

def _simile(a: str, b: str, soglia: float = 0.80) -> bool:
    sa, sb = set(_normalizza(a)), set(_normalizza(b))
    if not sa or not sb:
        return False
    return len(sa & sb) / max(len(sa), len(sb)) >= soglia

def _e_duplicato(nuova: dict, offerte: list) -> bool:
    t  = nuova.get('title', '')
    p  = nuova.get('newPrice', '')
    n  = nuova.get('store', '')
    tn = _normalizza(t)
    for o in offerte:
        if o.get('title', '') == t:                            return True
        if _normalizza(o.get('title', '')) == tn:              return True
        if o.get('store','') == n and o.get('newPrice','') == p:
            if _simile(o.get('title',''), t):                  return True
    return False

# ── Salvataggio offerta ───────────────────────────────────────────────────────

def salva_offerta(titolo, prezzo, negozio, scadenza, image_url, link_volantino):
    offerte = []
    if os.path.exists(FILE_OFFERTE):
        with open(FILE_OFFERTE, 'r', encoding='utf-8') as f:
            try: offerte = json.load(f)
            except: pass

    nuova = {
        'store':      negozio,
        'title':      titolo,
        'newPrice':   str(prezzo),
        'expiration': str(scadenza),
        'image':      image_url,
        'link':       link_volantino or 'https://t.me/+0mC7roUUmYswZjA0'
    }

    if _e_duplicato(nuova, offerte):
        print(f'[SKIP] Duplicato: {titolo[:60]}')
        return False

    offerte.insert(0, nuova)
    offerte = offerte[:500]

    with open(FILE_OFFERTE, 'w', encoding='utf-8') as f:
        json.dump(offerte, f, indent=4, ensure_ascii=False)

    print(f'[OK] Salvata: {titolo[:60]}')
    return True

# ── Ricerca API Promoqui ──────────────────────────────────────────────────────

async def cerca_offerte_api(query: str) -> list:
    url = 'https://www.promoqui.it/api/2.0/offers/search'
    params = {'q': query, 'country_code': 'it', 'per_page': 30}
    headers = {'User-Agent': 'Mozilla/5.0'}
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params, headers=headers)
        r.raise_for_status()
        return r.json().get('offers', [])

# ── HTTP Handler ──────────────────────────────────────────────────────────────

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SITO_DIR, **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def _json(self, code: int, data: dict):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/api/search':
            query = parse_qs(parsed.query).get('q', [''])[0].strip()
            if not query:
                return self._json(400, {'status': 'error', 'msg': 'Missing query'})
            try:
                print(f"[SEARCH] '{query}'")
                risultati  = asyncio.run(cerca_offerte_api(query))
                con_prezzo = [o for o in risultati if o.get('price') is not None]
                ordinati   = sorted(con_prezzo, key=lambda x: float(x['price']))
                salvate = 0
                for off in ordinati[:10]:
                    titolo   = off.get('title', 'Prodotto Sconosciuto')
                    prezzo   = off.get('price', 'N/D')
                    negozio  = off.get('retailer_name', 'Negozio Sconosciuto')
                    scadenza = off.get('expiration_date', 'N/D')
                    img      = off.get('image_large') or off.get('image_big') or off.get('image_thumb')
                    slug     = off.get('leaflet_slug', '')
                    link     = f'https://www.promoqui.it/offerte/{slug}' if slug else ''
                    if salva_offerta(titolo, prezzo, negozio, scadenza, img, link):
                        salvate += 1
                return self._json(200, {'status': 'ok', 'trovate': salvate})
            except Exception as e:
                print(f'[ERR] Search: {e}')
                return self._json(500, {'status': 'error'})

        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get('Content-Length', 0))
        body   = self.rfile.read(length)

        if parsed.path == '/api/contact':
            try:
                data      = json.loads(body)
                nome      = data.get('name', 'Anonimo')
                messaggio = data.get('message', '').strip()
                if not messaggio:
                    return self._json(400, {'status': 'error'})
                entry = {
                    'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'name': nome, 'message': messaggio
                }
                richieste = []
                if os.path.exists(FILE_CONTATTI):
                    with open(FILE_CONTATTI, 'r', encoding='utf-8') as f:
                        try: richieste = json.load(f)
                        except: pass
                richieste.append(entry)
                with open(FILE_CONTATTI, 'w', encoding='utf-8') as f:
                    json.dump(richieste, f, ensure_ascii=False, indent=2)
                return self._json(200, {'status': 'ok'})
            except Exception as e:
                return self._json(500, {'status': 'error'})

        if parsed.path == '/api/checkout':
            try:
                data      = json.loads(body)
                nome      = data.get('name', '')
                indirizzo = data.get('address', '')
                carrello  = data.get('cart', [])
                totale    = data.get('total', 0)
                if not nome or not carrello:
                    return self._json(400, {'status': 'error'})
                entry = {
                    'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'name': nome, 'address': indirizzo,
                    'cart': carrello, 'total': totale
                }
                ordini = []
                if os.path.exists(FILE_ORDINI):
                    with open(FILE_ORDINI, 'r', encoding='utf-8') as f:
                        try: ordini = json.load(f)
                        except: pass
                ordini.append(entry)
                with open(FILE_ORDINI, 'w', encoding='utf-8') as f:
                    json.dump(ordini, f, ensure_ascii=False, indent=2)
                return self._json(200, {'status': 'ok'})
            except Exception as e:
                return self._json(500, {'status': 'error', 'error': str(e)})

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        if args and '/api/' in args[0]:
            super().log_message(format, *args)

# ── Avvio ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    server_address = ('127.0.0.1', 8097)
    httpd = HTTPServer(server_address, Handler)
    print(f'[sitoofferte] Server avviato su {server_address[0]}:{server_address[1]}')
    httpd.serve_forever()
