// Estrae i prezzi (in euro) da un blocco di testo incollato manualmente
// dall'utente, ad es. copiato dalla pagina dei risultati di Google Lens.
// Riconosce sia "90 €" sia "€ 90,00" (formato usato da alcuni siti come
// Idealo), ma solo numeri accanto al simbolo €, per non confondere prezzi
// con altre misure presenti nel testo (bar, W, litri, valutazioni "4,8(403)").
export function estraiPrezziDaTesto(testo) {
  if (!testo) return []

  const corrispondenze = testo.matchAll(/(?:(\d+(?:[.,]\d{1,2})?)\s*€)|(?:€\s*(\d+(?:[.,]\d{1,2})?))/g)
  const prezzi = []

  for (const match of corrispondenze) {
    const grezzo = match[1] ?? match[2]
    const valore = parseFloat(grezzo.replace(',', '.'))
    if (!isNaN(valore) && valore > 0) {
      prezzi.push(valore)
    }
  }

  return prezzi
}
