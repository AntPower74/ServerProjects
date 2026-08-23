with open("/home/antonio/verifica_turni/web/index.html", "r", encoding="utf-8") as f:
    content = f.read()

target_sosta = r"""                if (isSosta) {
                    // CARD SOSTA / PAUSA CCNL (Ambra / Oro)
                    card.className = "p-3 rounded-xl bg-amber-950/20 border border-amber-500/30 border-l-4 border-l-amber-400 text-xs space-y-1.5 shadow-sm hover:border-amber-400/60 transition";
                    card.innerHTML = `
                        <div class="flex justify-between items-center">
                            <div class="flex items-center gap-2">
                                <span class="w-5 h-5 rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-bold flex items-center justify-center font-mono border border-amber-500/30">${idx + 1}</span>
                                <span class="font-mono px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                                    <i class="fa-solid fa-mug-hot text-amber-400"></i> SOSTA CCNL
                                </span>
                            </div>
                            <span class="font-mono text-amber-200 font-bold bg-slate-950 px-2 py-0.5 rounded text-[11px] border border-amber-500/30">
                                ${a.partenza || '-'} ➔ ${a.arrivo || '-'} <span class="text-amber-400 text-[10px] font-normal">(${durStr})</span>
                            </span>
                        </div>
                        <div class="flex items-center gap-1.5 text-amber-100 font-semibold text-xs pl-7">
                            <i class="fa-solid fa-location-dot text-amber-400 text-[10px] shrink-0"></i>
                            <span class="truncate">${a.descrizione || a.da || 'Sosta in Deposito'}</span>
                        </div>
                        <div class="flex justify-between items-center text-[10px] font-mono text-amber-400/80 pt-1 border-t border-amber-500/20 pl-7">
                            <span>Durata effettiva: <b>${durStr}</b></span>
                            <span class="uppercase tracking-wider font-semibold">☕ Pausa Retribuita CCNL</span>
                        </div>
                    `;"""

replacement_sosta = r"""                if (isSosta) {
                    // CALCOLO RETRIBUZIONE SOSTA (Regola: <=30m al 100%, oltre 30m 0% in residenza, 12% fuori residenza)
                    const depPrefix = (t.codice_turno || '').substring(0, 2).toLowerCase();
                    const depNome = (t.deposito || '').toLowerCase();
                    const depMap = {
                        'to': ['torino', 'c.so bolzano', 'bolzano'],
                        'pi': ['pinerolo'],
                        'pe': ['perosa'],
                        'pt': ['pont st. martin', 'pont saint martin', 'pont'],
                        'su': ['susa'],
                        'pb': ['piobesi'],
                        'ca': ['caselle'],
                        'sa': ['salbertrand'],
                        'lu': ['luserna'],
                        'ba': ['barge'],
                        'iv': ['ivrea'],
                        'bo': ['bobbio pellice', 'bobbio']
                    };
                    const keywords = depMap[depPrefix] || [depNome];
                    if (depNome && !keywords.includes(depNome)) keywords.push(depNome);
                    const descFull = ((a.descrizione || '') + ' ' + (a.da || '') + ' ' + (a.a || '')).toLowerCase();
                    const isInResidenza = keywords.some(k => k && descFull.includes(k));
                    
                    let retribBadge = "";
                    let retribDettaglio = "";
                    
                    if (durM <= 30) {
                        retribBadge = `<span class="text-emerald-400 font-bold">100% Retribuita</span>`;
                        retribDettaglio = `Sosta breve (&le; 30m) &bull; <b>${durM}m pagati</b>`;
                    } else {
                        const ecc = durM - 30;
                        if (isInResidenza) {
                            retribBadge = `<span class="text-amber-300 font-bold">In Residenza (30m 100% + ${ecc}m 0%)</span>`;
                            retribDettaglio = `30m al 100% + ${ecc}m al 0% (stacco residenza) = <b>30m pagati</b>`;
                        } else {
                            const q12 = (ecc * 0.12).toFixed(1);
                            const totPagato = (30 + ecc * 0.12).toFixed(1);
                            retribBadge = `<span class="text-indigo-300 font-bold">Fuori Residenza (30m 100% + ${ecc}m 12%)</span>`;
                            retribDettaglio = `30m al 100% + ${ecc}m al 12% (${q12}m) = <b>${totPagato}m pagati</b>`;
                        }
                    }

                    // CARD SOSTA / PAUSA CCNL (Ambra / Oro)
                    card.className = "p-3 rounded-xl bg-amber-950/20 border border-amber-500/30 border-l-4 border-l-amber-400 text-xs space-y-1.5 shadow-sm hover:border-amber-400/60 transition";
                    card.innerHTML = `
                        <div class="flex justify-between items-center">
                            <div class="flex items-center gap-2">
                                <span class="w-5 h-5 rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-bold flex items-center justify-center font-mono border border-amber-500/30">${idx + 1}</span>
                                <span class="font-mono px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                                    <i class="fa-solid fa-mug-hot text-amber-400"></i> SOSTA CCNL
                                </span>
                            </div>
                            <span class="font-mono text-amber-200 font-bold bg-slate-950 px-2 py-0.5 rounded text-[11px] border border-amber-500/30">
                                ${a.partenza || '-'} ➔ ${a.arrivo || '-'} <span class="text-amber-400 text-[10px] font-normal">(${durStr})</span>
                            </span>
                        </div>
                        <div class="flex items-center gap-1.5 text-amber-100 font-semibold text-xs pl-7">
                            <i class="fa-solid fa-location-dot text-amber-400 text-[10px] shrink-0"></i>
                            <span class="truncate">${a.descrizione || a.da || 'Sosta in Deposito'}</span>
                        </div>
                        <div class="flex justify-between items-center text-[10px] font-mono text-amber-300/90 pt-1 border-t border-amber-500/20 pl-7">
                            <span>${retribDettaglio}</span>
                            <span>${retribBadge}</span>
                        </div>
                    `;"""

if target_sosta in content:
    content = content.replace(target_sosta, replacement_sosta)
    with open("/home/antonio/verifica_turni/web/index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ Card Sosta aggiornata con dettaglio retribuzione residenza/fuori residenza.")
else:
    print("⚠️ Target non trovato esattamente, verificare index.html.")
