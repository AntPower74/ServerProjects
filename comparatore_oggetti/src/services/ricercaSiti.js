// URL di ricerca per i marketplace di annunci usati. Lo scraping server-side
// di questi siti è bloccato (403 anche a richieste semplici, vedi memoria
// progetto), quindi qui costruiamo solo l'URL: l'estrazione dei risultati
// avviene lato client (bookmarklet o estensione), come per Google Lens.
export const SITI_MERCATO = {
  subito: {
    etichetta: 'Subito',
    costruisciUrl: (query) => `https://www.subito.it/annunci-italia/vendita/usato/?q=${encodeURIComponent(query)}`
  },
  vinted: {
    etichetta: 'Vinted',
    costruisciUrl: (query) => `https://www.vinted.it/catalog?search_text=${encodeURIComponent(query)}`
  },
  marketplace: {
    etichetta: 'Marketplace',
    costruisciUrl: (query) => `https://www.facebook.com/marketplace/search/?query=${encodeURIComponent(query)}`
  }
}

export function apriSitoMercato(sito, query) {
  const config = SITI_MERCATO[sito]
  if (!config) return
  // Niente 'noopener': senza relazione tra le schede, il bookmarklet sul sito
  // aperto non riuscirebbe a ritrovare/riusare questa scheda (window.open(url,
  // 'prezzlyTab') cerca solo dentro schede collegate) e ne aprirebbe una nuova
  // vuota, perdendo la ricerca in corso. Contropartita accettata: il sito aperto
  // (Subito/Vinted/Marketplace, tutti affidabili) potrebbe in teoria reindirizzare
  // questa scheda via window.opener.location — rischio basso con questi domini.
  window.open(config.costruisciUrl(query), '_blank')
}
