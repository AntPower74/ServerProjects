#!/usr/bin/env python3
import json
from collections import Counter

ARCHIVE_FILE = '/home/antonio/indovino_pwa/archive/full_archive.json'

with open(ARCHIVE_FILE, 'r', encoding='utf-8') as f:
    draws = json.load(f)

days = {}
for d in draws:
    days.setdefault(d['data'], []).append(d)

print(f"=== OTTIMIZZAZIONE PARAMETRI SU {len(draws)} ESTRAZIONI ===")

# Test diversi Score Minimi, Finestre, e Colpi Massimi
results = []

for min_score in [40, 60, 80, 100, 120]:
    for max_colpi in [2, 3, 4, 5, 6]:
        for min_freq in [4, 6, 8]:
            tot_signals = 0
            wins = 0
            tot_spesa = 0.0
            tot_incasso = 0.0
            ambi_oro_cnt = 0
            
            for date_str, day_draws in sorted(days.items()):
                active_until = 0
                for i in range(40, len(day_draws) - max_colpi):
                    if i < active_until:
                        continue
                    curr_draw = day_draws[i]
                    window = day_draws[max(0, i-60):i]
                    if len(window) < 30:
                        continue
                        
                    spies = []
                    for s in range(1, 91):
                        indices = [k for k in range(len(window)-1) if s in window[k]['numeri']]
                        freq = len(indices)
                        if freq < min_freq:
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
                        
                    spies.sort(key=lambda x: x['score'], reverse=True)
                    if not spies or spies[0]['score'] < min_score:
                        continue
                        
                    best_spy = spies[0]
                    if best_spy['spy'] in curr_draw['numeri']:
                        tot_signals += 1
                        terzina_set = set(best_spy['top3'])
                        trade_won = False
                        spesa_t = 0.0
                        incasso_t = 0.0
                        
                        for step in range(1, max_colpi + 1):
                            nxt_idx = i + step
                            nxt_d = day_draws[nxt_idx]
                            spesa_t += 2.0
                            hits = len(terzina_set.intersection(set(nxt_d['numeri'])))
                            has_oro = (nxt_d['oro'] in terzina_set)
                            
                            if hits == 3:
                                trade_won = True
                                incasso_t = 130.0 if has_oro else 45.0
                                break
                            elif hits == 2:
                                trade_won = True
                                if has_oro:
                                    incasso_t = 25.0
                                    ambi_oro_cnt += 1
                                else:
                                    incasso_t = 2.0
                                break
                                
                        if trade_won:
                            wins += 1
                        tot_spesa += spesa_t
                        tot_incasso += incasso_t
                        active_until = i + step
                        
            if tot_signals >= 5:
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
                    'ambi_oro': ambi_oro_cnt
                })

results.sort(key=lambda x: x['netto'], reverse=True)

print(f"{'MinScore':<10}{'MaxColpi':<10}{'MinFreq':<10}{'Segnali':<10}{'WinRate':<10}{'Spesa':<10}{'Incasso':<10}{'Netto':<10}{'AmbiOro':<10}")
print("-" * 90)
for r in results[:15]:
    print(f"{r['min_score']:<10}{r['max_colpi']:<10}{r['min_freq']:<10}{r['signals']:<10}{str(r['win_rate'])+'%':<10}{str(r['spesa'])+'€':<10}{str(r['incasso'])+'€':<10}{str(r['netto'])+'€':<10}{r['ambi_oro']:<10}")

