import { cercaSuEbayReale } from './ebayService.js'

export async function cercaAnnunciSimili(nomeOggetto) {
  try {
    // Ora l'aggregazione avviene nel backend unificato
    const annunci = await cercaSuEbayReale(nomeOggetto);
    return annunci;
  } catch (errore) {
    console.error('Errore dal backend:', errore.message)
    return [];
  }
}
