// Client per le API eBay (Browse API). Il Client Secret resta solo qui,
// lato server: non deve mai arrivare al browser.
const EBAY_ENV = process.env.EBAY_ENV === 'sandbox' ? 'sandbox' : 'production'

const BASE_URL = EBAY_ENV === 'sandbox'
  ? 'https://api.sandbox.ebay.com'
  : 'https://api.ebay.com'

let tokenCache = { valore: null, scadenza: 0 }

async function ottieniToken() {
  if (tokenCache.valore && Date.now() < tokenCache.scadenza) {
    return tokenCache.valore
  }

  const clientId = process.env.EBAY_CLIENT_ID
  const clientSecret = process.env.EBAY_CLIENT_SECRET

  if (!clientId || !clientSecret) {
    throw new Error('EBAY_CLIENT_ID / EBAY_CLIENT_SECRET mancanti nel file .env')
  }

  const credenziali = Buffer.from(`${clientId}:${clientSecret}`).toString('base64')

  const risposta = await fetch(`${BASE_URL}/identity/v1/oauth2/token`, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${credenziali}`,
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: new URLSearchParams({
      grant_type: 'client_credentials',
      scope: 'https://api.ebay.com/oauth/api_scope'
    })
  })

  if (!risposta.ok) {
    const testo = await risposta.text()
    throw new Error(`eBay OAuth fallito (${risposta.status}): ${testo}`)
  }

  const dati = await risposta.json()
  tokenCache = {
    valore: dati.access_token,
    // Rinnova un minuto prima della scadenza reale
    scadenza: Date.now() + (dati.expires_in - 60) * 1000
  }

  return tokenCache.valore
}

// Ricerca annunci attivi su eBay per una query testuale.
// Nota: la Browse API espone solo annunci ATTIVI. Lo storico dei "venduti"
// richiede la Marketplace Insights API, soggetta ad approvazione separata
// da parte di eBay (non disponibile di default sui nuovi account developer).
export async function cercaSuEbay(query, { marketplace = 'EBAY_IT', limite = 30 } = {}) {
  let token
  try {
    token = await ottieniToken()
  } catch (err) {
    console.warn('eBay API non configurata o token non disponibile:', err.message)
    return []
  }

  // Normalizza query ed aggiungi parole negative per escludere accessori su eBay
  let queryEbay = query.trim()
  if (/^samsung\s+s\d+/i.test(queryEbay) && !/galaxy/i.test(queryEbay)) {
    queryEbay = queryEbay.replace(/^samsung\s+/i, 'Samsung Galaxy ')
  }
  if (/^s(7|8|9|10|20|21|22|23|24)$/i.test(queryEbay)) {
    queryEbay = `Samsung Galaxy ${queryEbay.toUpperCase()}`
  }

  // Se cerchiamo uno smartphone, escludiamo cover e ricambi direttamente nella query eBay
  if (/(galaxy\s*s\d+|iphone|smartphone|cellulare)/i.test(queryEbay)) {
    queryEbay = `${queryEbay} -cover -custodia -vetro -pellicola -ricambio -ricambi -display -batteria -flex -tasti -pulsante -tab -tablet`
  }

  const url = new URL(`${BASE_URL}/buy/browse/v1/item_summary/search`)
  url.searchParams.set('q', queryEbay)
  url.searchParams.set('limit', String(limite))

  try {
    const risposta = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
        'X-EBAY-C-MARKETPLACE-ID': marketplace
      }
    })

    if (!risposta.ok) {
      const testo = await risposta.text()
      console.warn(`Ricerca eBay non riuscita (${risposta.status}): ${testo}`)
      return []
    }

    const dati = await risposta.json()

    return (dati.itemSummaries ?? [])
      .filter((item) => item.price?.value)
      .map((item) => ({
        fonte: 'eBay',
        titolo: item.title,
        prezzo: parseFloat(item.price.value),
        valuta: item.price.currency ?? 'EUR',
        condizione: item.condition ?? null,
        url: item.itemWebUrl ?? null,
        immagine: item.image?.imageUrl || item.thumbnailImages?.[0]?.imageUrl || null,
        stato: 'attivo',
        giorniFa: null
      }))
  } catch (err) {
    console.error('Errore chiamata eBay:', err.message)
    return []
  }
}
