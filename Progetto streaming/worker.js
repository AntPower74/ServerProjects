// Il worker estrae solo nome/logo/url dalla M3U: la classificazione per
// marchio/tipo (vedi classifyByBrand in main.js) viene fatta a parte, così
// resta sempre aggiornata anche per playlist già in cache (IndexedDB) o
// ricaricate da "Recenti", che qui non ripassano mai dal parsing.
self.onmessage = function(e) {
  const content = e.data;
  const lines = content.split('\n');
  const result = [];
  let currentChannel = null;
  let epgUrl = '';

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith('#EXTM3U')) {
      // Alcune playlist dichiarano qui la guida XMLTV esterna (url-tvg o,
      // più raro, x-tvg-url). Quando ce n'è più di una separate da virgola
      // prendiamo solo la prima: è quella che i player di riferimento usano.
      const tvgMatch = line.match(/(?:url-tvg|x-tvg-url)="([^"]+)"/i);
      if (tvgMatch) epgUrl = tvgMatch[1].split(',')[0].trim();
    } else if (line.startsWith('#EXTINF:')) {
      currentChannel = { name: '', logo: '', group: '', url: '', tvgId: '' };

      const logoMatch = line.match(/tvg-logo="([^"]+)"/);
      if (logoMatch) currentChannel.logo = logoMatch[1];

      const idMatch = line.match(/tvg-id="([^"]+)"/);
      if (idMatch) currentChannel.tvgId = idMatch[1];

      const commaSplit = line.split(',');
      if (commaSplit.length > 1) {
        currentChannel.name = commaSplit[commaSplit.length - 1].trim();
      }
    } else if (line.startsWith('http') && currentChannel) {
      currentChannel.url = line;
      result.push(currentChannel);
      currentChannel = null;
    }

    // Report progress to UI every 10000 lines
    if (i % 10000 === 0) {
      self.postMessage({ type: 'progress', percent: Math.round((i / lines.length) * 100) });
    }
  }

  self.postMessage({ type: 'progress', percent: 100 });
  self.postMessage({ type: 'done', channels: result, epgUrl });
};
