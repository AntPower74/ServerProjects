import { cercaSuEbay } from './ebayClient.js'

export async function cercaSuTutteLePiattaforme(query) {
  const annunciEbay = await cercaSuEbay(query)
  const annunciCombinati = annunciEbay.map(item => ({ ...item, sorgente: 'eBay' }))

  annunciCombinati.sort((a, b) => {
    const prezzoA = parseFloat(String(a.prezzo).replace(',', '.'))
    const prezzoB = parseFloat(String(b.prezzo).replace(',', '.'))
    if (isNaN(prezzoA)) return 1
    if (isNaN(prezzoB)) return -1
    return prezzoA - prezzoB
  })

  return annunciCombinati
}
