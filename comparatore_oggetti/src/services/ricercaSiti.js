export function normalizzaQueryMercato(query) {
  if (!query) return ''
  let q = query.trim()
  if (/^samsung\s+s\d+/i.test(q) && !/galaxy/i.test(q)) {
    q = q.replace(/^samsung\s+/i, 'Samsung Galaxy ')
  }
  if (/^s(7|8|9|10|20|21|22|23|24)$/i.test(q)) {
    q = `Samsung Galaxy ${q.toUpperCase()}`
  }
  return q
}

export const SITI_MERCATO = {
  subito: {
    etichetta: 'Subito',
    costruisciUrl: (query) => `https://www.subito.it/annunci-italia/vendita/usato/?q=${encodeURIComponent(normalizzaQueryMercato(query))}&order=price_asc`
  },
  vinted: {
    etichetta: 'Vinted',
    costruisciUrl: (query) => `https://www.vinted.it/catalog?search_text=${encodeURIComponent(normalizzaQueryMercato(query))}&order=price_low_to_high`
  },
  marketplace: {
    etichetta: 'Marketplace',
    costruisciUrl: (query) => `https://www.facebook.com/marketplace/search/?query=${encodeURIComponent(normalizzaQueryMercato(query))}`
  }
}

export function apriSitoMercato(sito, query) {
  const config = SITI_MERCATO[sito]
  if (!config) return
  window.open(config.costruisciUrl(query), '_blank')
}
