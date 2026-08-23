// Chiama il backend locale (server/index.js), che a sua volta interroga
// l'eBay Browse API tenendo il Client Secret al sicuro lato server.
export async function cercaSuEbayReale(query) {
  const risposta = await fetch(`/api/search?q=${encodeURIComponent(query)}`)

  if (!risposta.ok) {
    const dati = await risposta.json().catch(() => ({}))
    throw new Error(dati.errore ?? `Errore ${risposta.status} dal backend eBay`)
  }

  const dati = await risposta.json()
  return dati.annunci
}
