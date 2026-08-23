#!/usr/bin/env python3
import json
from collections import Counter

ARCHIVE_FILE = '/home/antonio/indovino_pwa/archive/full_archive.json'

with open(ARCHIVE_FILE, 'r', encoding='utf-8') as f:
    draws = json.load(f)

days = {}
for d in draws:
    days.setdefault(d['data'], []).append(d)

print(f"=== OTTIMIZZAZIONE VELOCE SU {len(draws)} ESTRAZIONI ===")

# Precalcola per ogni giorno e per ogni concorso la migliore spia
precomputed_signals = []

for date_str, day_draws in sorted(days.items()):
    for i in range(35, len(day_draws) - 6):
        curr_draw = day_draws[i]
        window = day_draws[max(0, i-50):i]
        
        spies = []
        for s in range(1, 91):
            indices = [k for k in range(len(window)-1) if s in window[k]['numeri']]
            freq = len(indices)
            if freq < 4:
                continue
            post_nums = []
            post_oros = []
            for k in indices:
                post_nums.extend(window[k+1]['numeri'])
                if window[k+1]['oro'] is not None:
                    post_oros.append(window[k+1]['oro'])
            c_post = Counter(post_nums)
            c_oro = Counter(post_oros)
            top3 = [n for n, c in c_post.most_common(3)]
            top3_set = set(top3)
            ambi_post = 0
            terni_post = 0
            oro_hit = 0
            for k in indices:
                d_nxt = window[k+1]
                hits = len(top3_set.intersection(set(d_nxt['numeri'])))
                if hits >= 2: ambi_post += 1
                if hits == 3: terni_post += 1
                if d_nxt['oro'] in top3_set: oro_hit += 1
            score = (ambi_post * 4.0) + (terni_post * 20.0) + (oro_hit * 3.0) + (freq * 0.5)
            top_oro = c_oro.most_common(1)[0][0] if c_oro else top3[0]
            spies.append({'spy': s, 'score': score, 'top3': top3, 'top_oro': top_oro, 'freq': freq})
            
        if not spies:
            continue
        spies.sort(key=lambda x: x['score'], reverse=True)
        best_spy = spies[0]
        
        if best_spy['spy'] in curr_draw['numeri']:
            # Registra il segnale e l'esito per i successivi 6 concorsi
            future_outcomes = []
            for step in range(1, 7):
                nxt_d = day_draws[i + step]
                hits = len(set(best_spy['top3']).intersection(set(nxt_d['numeri'])))
                has_oro = (nxt_d['oro'] in set(best_spy['top3']))
                future_outcomes.append({'hits': hits, 'has_oro': has_oro})
                
            precomputed_signals.append({
                'data': date_str,
                'index': i,
                'spy': best_spy['spy'],
                'score': best_spy['score'],
                'freq': best_spy['freq'],
                'outcomes': future_outcomes
            })

print(f"[*] Precalcolati {len(precomputed_signals)} segnali totali.")

# Ora testa tutte le combinazioni all'istante
results = []

for min_score in [30, 45, 60, 75, 90, 110]:
    for max_colpi in [1, 2, 3, 4, 5]:
        for min_freq in [4, 6]:
            tot_signals = 0
            wins = 0
            tot_spesa = 0.0
            tot_incasso = 0.0
            ambi_oro = 0
            terni = 0
            
            last_end_idx = -1
            
            for sig in precomputed_signals:
                if sig['score'] < min_score or sig['freq'] < min_freq:
                    continue
                if sig['index'] < last_end_idx:
                    continue  # Trade ancora attivo
                    
                tot_signals += 1
                spesa_t = 0.0
                incasso_t = 0.0
                trade_won = False
                colpo_fin = max_colpi
                
                for step in range(1, max_colpi + 1):
                    spesa_t += 2.0
                    out = sig['outcomes'][step-1]
                    if out['hits'] == 3:
                        trade_won = True
                        incasso_t = 130.0 if out['has_oro'] else 45.0
                        terni += 1
                        colpo_fin = step
                        break
                    elif out['hits'] == 2:
                        trade_won = True
                        if out['has_oro']:
                            incasso_t = 25.0
                            ambi_oro += 1
                        else:
                            incasso_t = 2.0
                        colpo_fin = step
                        break
                        
                if trade_won:
                    wins += 1
                tot_spesa += spesa_t
                tot_incasso += incasso_t
                last_end_idx = sig['index'] + colpo_fin
                
            if tot_signals >= 4:
                wr = (wins / tot_signals) * 100
                netto = tot_incasso - tot_spesa
                results.append({
                    'min_score': min_score,
                    'max_colpi': max_colpi,
                    'min_freq': min_freq,
                    'signals': tot_signals,
                    'wins': wins,
                    'win_rate': round(wr, 1),
                    'spesa': round(tot_spesa, 2),
                    'incasso': round(tot_incasso, 2),
                    'netto': round(netto, 2),
                    'ambi_oro': ambi_oro,
                    'terni': terni
                })

results.sort(key=lambda x: x['netto'], reverse=True)

print(f"\n{'MinScore':<10}{'MaxColpi':<10}{'MinFreq':<10}{'Segnali':<10}{'WinRate':<10}{'Spesa':<10}{'Incasso':<10}{'Netto':<12}{'AmbiOro':<10}{'Terni':<6}")
print("-" * 95)
for r in results[:15]:
    sign = "+" if r['netto'] >= 0 else ""
    print(f"{r['min_score']:<10}{r['max_colpi']:<10}{r['min_freq']:<10}{r['signals']:<10}{str(r['win_rate'])+'%':<10}{str(r['spesa'])+'€':<10}{str(r['incasso'])+'€':<10}{sign+str(r['netto'])+'€':<12}{r['ambi_oro']:<10}{r['terni']:<6}")
