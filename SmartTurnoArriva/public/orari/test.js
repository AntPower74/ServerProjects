    // Set default date to today
    document.getElementById('dateSelect').valueAsDate = new Date();

    // Populate selects
    const allStops = new Set();
    tripsData.forEach(t => {
        Object.keys(t).forEach(k => {
            if(!k.startsWith('_')) allStops.add(k);
        });
    });
    const sortedStops = Array.from(allStops).sort();
    
    const fromSelect = document.getElementById('fromSelect');
    const toSelect = document.getElementById('toSelect');
    sortedStops.forEach(s => {
        fromSelect.add(new Option(s, s));
        toSelect.add(new Option(s, s));
    });

    const FESTIVITA = [
        "01-01", "06-01", "25-04", "01-05", "02-06", "15-08", "01-11", "08-12", "25-12", "26-12"
    ]; // In a real app we calculate Easter/Pasquetta too.

    function mapGiorni(codice) {
        if(codice === '12345') return 'Lun - Ven';
        if(codice === '123456') return 'Lun - Sab';
        if(codice === '6') return 'Sabato';
        if(codice === '78') return 'Dom / Festivi';
        if(codice === 'GG') return 'Tutti i giorni';
        if(codice === 'NAT') return 'Natale';
        return codice;
    }

    function updateClock() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('it-IT');
        const dateString = now.toLocaleDateString('it-IT', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
        
        document.getElementById('clock-time').textContent = timeString;
        document.getElementById('clock-date').textContent = dateString.charAt(0).toUpperCase() + dateString.slice(1);
        
        if(document.getElementById('results').innerHTML !== '') {
            // Only auto-update if the selected date is today
            const selectedDate = document.getElementById('dateSelect').value;
            const todayStr = now.toISOString().split('T')[0];
            if(selectedDate === todayStr) {
                searchTrips(true);
            }
        }
    }
    
    setInterval(updateClock, 15000); 
    updateClock(); 
    
    function parseTime(timeStr) {
        if(!timeStr || timeStr.length < 4) return 0;
        let parts = timeStr.replace(".", ":").split(":");
        if(parts.length === 2) {
            return parseInt(parts[0]) * 60 + parseInt(parts[1]);
        }
        return 0;
    }

    function isCorsaValida(trip, targetDate) {
        // Precise Logic based on PDF Legend
        const month = targetDate.getMonth() + 1;
        const day = targetDate.getDate();
        const dayOfWeek = targetDate.getDay(); // 0=Sun, 1=Mon...6=Sat
        const dateStr = (day < 10 ? '0'+day : day) + '-' + (month < 10 ? '0'+month : month);
        
        const isHoliday = FESTIVITA.includes(dateStr) || dayOfWeek === 0;
        const isAugust = month === 8;
        const isAugustBreak = isAugust && day >= 3 && day <= 23;
        
        const giorni = trip._giorni || '';
        const stagionalita = trip._stagionalita || '';
        const note = trip._note || '';

        // 1. Controlli note speciali
        if (note.includes('A') && isAugustBreak) return false;
        if (note.includes('J') && !isAugustBreak) return false;
        if (note.includes('F') && dateStr === '25-12') return true;
        if (note.includes('#') && dateStr !== '25-12') return false;

        // 2. Controlli festività/feriali (Stagionalità)
        if (stagionalita === 'FEST' && !isHoliday) return false;
        if (stagionalita === 'FER' && isHoliday) return false;

        // 3. Controlli giorni della settimana
        if (giorni) {
            if (giorni === 'GG') return true;
            if (giorni === '12345' && (isHoliday || dayOfWeek === 6)) return false;
            if (giorni === '123456' && isHoliday) return false;
            if (giorni === '6' && dayOfWeek !== 6) return false;
            if (giorni === '78' && !isHoliday) return false;
            
            // Fallback checking standard numbers inside the code
            const weekStr = dayOfWeek === 0 ? '7' : dayOfWeek.toString();
            if (giorni.match(/^[1-8]+$/) && !giorni.includes(weekStr) && !(isHoliday && giorni.includes('8'))) {
                return false;
            }
        }
        
        return true;
    }
    
    function searchTrips(isAutoUpdate = false) {
        const fromStop = document.getElementById('fromSelect').value;
        const toStop = document.getElementById('toSelect').value;
        const dateVal = document.getElementById('dateSelect').value;
        const container = document.getElementById('results');
        
        if (!isAutoUpdate) container.innerHTML = '';
        
        if (!fromStop || !toStop) {
            container.innerHTML = `<p style="text-align:center; color:#9e9ea6;">Seleziona sia la partenza che l'arrivo.</p>`;
            return;
        }
        if (fromStop === toStop) {
            container.innerHTML = '<p style="text-align:center; color:#ef4444;">Partenza e arrivo non possono essere uguali.</p>';
            return;
        }

        const targetDate = new Date(dateVal);
        
        let validTrips = [];
        
        tripsData.forEach(trip => {
            if (trip[fromStop] && trip[toStop]) {
                if (!isCorsaValida(trip, targetDate)) return;

                let time1 = parseTime(trip[fromStop]);
                let time2 = parseTime(trip[toStop]);
                
                if (time1 > 0 && time2 > 0) {
                    if (time2 < time1 && time1 > 20*60 && time2 < 4*60) {
                        time2 += 24*60; 
                    }
                    
                    if (time1 < time2) {
                        validTrips.push({
                            fromTime: trip[fromStop].replace(".", ":"),
                            toTime: trip[toStop].replace(".", ":"),
                            time1: time1,
                            time2: time2,
                            giorni: mapGiorni(trip['_giorni']),
                            note: trip['_note'] || trip['_stagionalita']
                        });
                    }
                }
            }
        });
        
        validTrips.sort((a, b) => a.time1 - b.time1);
        
        if (validTrips.length === 0) {
            container.innerHTML = '<p style="text-align:center; color:#9e9ea6; line-height:1.5;">Nessuna corsa trovata per questa tratta <b>nella data selezionata</b>.<br/><small>Controlla se si tratta di un giorno festivo, di un mese con servizio ridotto, o se le fermate sono nella direzione sbagliata.</small></p>';
            return;
        }
        
        // Next Bus check (only relevant if selected date is today)
        const now = new Date();
        const todayStr = now.toISOString().split('T')[0];
        let nextBusIndex = -1;
        
        if (dateVal === todayStr) {
            const currentMinutes = now.getHours() * 60 + now.getMinutes();
            for (let i = 0; i < validTrips.length; i++) {
                if (validTrips[i].time1 > currentMinutes && validTrips[i].time1 !== 9999) {
                    nextBusIndex = i;
                    break;
                }
            }
        }
        
        let newHtml = '';
        validTrips.forEach((t, index) => {
            const isNext = index === nextBusIndex;
            let badgeHtml = isNext ? '<div class="next-bus-badge">PROSSIMA CORSA</div>' : '';
            
            let durationMins = t.time2 - t.time1;
            let h = Math.floor(durationMins / 60);
            let m = durationMins % 60;
            let durText = h > 0 ? h + "h " + m + "m" : m + "m";
            let durationHtml = `<span>&rarr;</span><small>${durText}</small>`;
            
            let noteHtml = t.note && t.note !== 'FER' ? `<span class="note-badge">${t.note}</span>` : '';

            newHtml += `
            <div class="trip-card ${isNext ? 'next-bus' : ''}">
                ${badgeHtml}
                <div class="trip-stations">
                    <span style="color:#9e9ea6; font-size:0.85rem;">Partenza</span>
                    <span class="trip-time">${t.fromTime}</span>
                    <div><span class="giorni-badge">${t.giorni}</span></div>
                    ${noteHtml ? `<div>${noteHtml}</div>` : ''}
                </div>
                <div class="trip-duration">
                    ${durationHtml}
                </div>
