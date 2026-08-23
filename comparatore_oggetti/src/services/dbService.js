export async function salvaRicerca(nomeOggetto, prezzoBersaglio) {
  const risposta = await fetch('/api/salva-ricerca', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nome_oggetto: nomeOggetto, prezzo_bersaglio: prezzoBersaglio })
  });
  if (!risposta.ok) {
    throw new Error("Errore durante il salvataggio");
  }
  return risposta.json();
}

export async function getRicercheSalvate() {
  const risposta = await fetch('/api/ricerche-salvate');
  if (!risposta.ok) {
    throw new Error("Errore durante il caricamento dell'archivio");
  }
  const dati = await risposta.json();
  return dati.ricerche;
}

export async function eliminaRicerca(id) {
  const risposta = await fetch(`/api/ricerche-salvate/${id}`, { method: 'DELETE' });
  if (!risposta.ok) {
    throw new Error("Errore durante l'eliminazione");
  }
  return risposta.json();
}
