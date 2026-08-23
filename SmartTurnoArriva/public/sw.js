// SmartTurnoArriva - Service Worker
// Strategia: rete sempre prima, nessuna cache → aggiornamenti istantanei

const CACHE_NAME = 'sta-v1';

self.addEventListener('install', (event) => {
  // Prende subito il controllo senza aspettare il prossimo caricamento
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    // Elimina tutte le vecchie cache (incluse quelle della versione "SmartTurno")
    caches.keys().then((keys) =>
      Promise.all(keys.map((key) => caches.delete(key)))
    ).then(() => {
      // Prende il controllo di tutti i client aperti immediatamente
      return self.clients.claim();
    })
  );
});

self.addEventListener('fetch', (event) => {
  // Salta richieste non-HTTP (chrome-extension, ecc.)
  if (!event.request.url.startsWith('http')) return;

  // Per tutto: rete prima, nessuna cache
  event.respondWith(
    fetch(event.request, { cache: 'no-store' })
      .catch(() => {
        // Fallback: se offline, prova dalla cache (se c'è qualcosa)
        return caches.match(event.request);
      })
  );
});

// Notifica tutti i client aperti quando c'è un aggiornamento
self.addEventListener('message', (event) => {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
});
