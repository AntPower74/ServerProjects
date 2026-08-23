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
export async function cercaSuEbay(query, { marketplace = 'EBAY_IT', limite = 20 } = {}) {
  let token
  try {
    token = await ottieniToken()
  } catch (err) {
    console.warn('eBay API non configurata o token non disponibile:', err.message)
    return []
  }

  const url = new URL(`${BASE_URL}/buy/browse/v1/item_summary/search`)
  url.searchParams.set('q', query)
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
        stato: 'attivo',
        giorniFa: null
      }))
  } catch (err) {
    console.error('Errore chiamata eBay:', err.message)
    return []
  }
}
