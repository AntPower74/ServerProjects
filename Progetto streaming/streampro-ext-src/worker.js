self.onmessage = function(e) {
  const content = e.data;
  const lines = content.split('\n');
  const result = [];
  let currentChannel = null;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    if (line.startsWith('#EXTINF:')) {
      currentChannel = { name: '', logo: '', group: 'Senza Categoria', url: '' };
      
      // Estrai logo
      const logoMatch = line.match(/tvg-logo="([^"]+)"/);
      if (logoMatch) currentChannel.logo = logoMatch[1];
      
      // Estrai gruppo (supporta group-title, tvg-group, o group)
      const groupMatch = line.match(/(?:group-title|tvg-group|group)="([^"]+)"/i);
      if (groupMatch) {
        currentChannel.group = groupMatch[1];
      } else {
        const noQuoteMatch = line.match(/(?:group-title|tvg-group|group)=([^ ,]+)/i);
        if (noQuoteMatch) currentChannel.group = noQuoteMatch[1];
      }
      
      // Estrai nome
      const commaSplit = line.split(',');
      if (commaSplit.length > 1) {
        currentChannel.name = commaSplit[commaSplit.length - 1].trim();
      }
    } else if (line.startsWith('#EXTGRP:') && currentChannel) {
      // Supporto per il tag #EXTGRP (molto comune al posto di group-title)
      currentChannel.group = line.substring(8).trim();
    } else if (line.startsWith('http') && currentChannel) {
      currentChannel.url = line;
      
      // AUTO-CATEGORIZZAZIONE INTELLIGENTE PER LISTE SENZA CATEGORIE (Specifico per liste BR)
      if (!currentChannel.group || currentChannel.group === 'Senza Categoria') {
        const name = currentChannel.name.toUpperCase();
        if (name.match(/\(\d{4}\)/)) {
          currentChannel.group = '🎬 Film (VOD)';
        } else if (name.match(/^[0-9]{3}\s*-/)) {
          currentChannel.group = '📚 Saghe / Collezioni';
        } else if (name.startsWith('GLOBO')) {
          currentChannel.group = '📺 Globo';
        } else if (name.startsWith('RECORD')) {
          currentChannel.group = '📺 Record';
        } else if (name.startsWith('SBT')) {
          currentChannel.group = '📺 SBT';
        } else if (name.startsWith('BAND')) {
          currentChannel.group = '📺 Band';
        } else if (name.includes('ESPN') || name.includes('SPORTV') || name.includes('PREMIERE') || name.includes('DAZN') || name.includes('COMBATE')) {
          currentChannel.group = '⚽ Sport';
        } else if (name.includes('HBO') || name.includes('TELECINE') || name.includes('CINEMAX') || name.includes('SPACE') || name.includes('MEGAPIX') || name.includes('AMC')) {
          currentChannel.group = '🍿 Film Premium';
        } else if (name.includes('DISCOVERY') || name.includes('HISTORY') || name.includes('ANIMAL PLANET') || name.includes('NAT GEO')) {
          currentChannel.group = '🌍 Documentari';
        } else if (name.includes('DISNEY') || name.includes('CARTOON') || name.includes('NICKELODEON') || name.includes('GLOOB')) {
          currentChannel.group = '🧸 Bambini';
        } else if (name.includes('CNN') || name.includes('NEWS') || name.includes('BAND NEWS')) {
          currentChannel.group = '📰 Notizie';
        } else {
          // Prendi la prima parola se non rientra nelle categorie famose
          const firstWord = currentChannel.name.split(' ')[0];
          if (firstWord && firstWord.length > 2) {
             currentChannel.group = '📺 ' + firstWord.charAt(0).toUpperCase() + firstWord.slice(1).toLowerCase();
          } else {
             currentChannel.group = '📺 Vari';
          }
        }
      }

      result.push(currentChannel);
      currentChannel = null;
    }

    // Report progress to UI every 10000 lines
    if (i % 10000 === 0) {
      self.postMessage({ type: 'progress', percent: Math.round((i / lines.length) * 100) });
    }
  }

  self.postMessage({ type: 'progress', percent: 100 });

  // Costruisci gruppi per non farlo fare al thread principale
  const groups = {};
  for(let i=0; i<result.length; i++) {
     const g = result[i].group;
     groups[g] = (groups[g] || 0) + 1;
  }

  self.postMessage({ type: 'done', channels: result, groups: groups });
};
