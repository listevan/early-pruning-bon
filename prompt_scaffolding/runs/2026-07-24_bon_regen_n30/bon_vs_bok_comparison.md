# bon (regen) vs bok (diverse / unique-pruned) — paired

Same 30 questions, prune_ratio 2, mean over plan {1000, 2500}. `selected` = judge's pick; `ceiling` = a correct candidate survived pruning. Positive delta favours **bok**.


## rank

| N | sel bon | sel bok | Δsel | ceil bon | ceil bok | Δceil | paired Δsel 95% CI | McNemar p |
|---|---|---|---|---|---|---|---|---|
| 1 | 49.2% | 49.6% | +0.4 | 49.2% | 49.6% | +0.4 | [-1.4, +2.3] | 1 |
| 2 | 56.2% | 58.3% | +2.1 | 56.2% | 59.6% | +3.3 | [-1.5, +5.6] | 0.405 |
| 4 | 64.2% | 66.3% | +2.1 | 67.5% | 68.8% | +1.2 | [-2.3, +6.5] | 0.383 |
| 8 | 63.3% | 65.0% | +1.7 | 70.0% | 69.2% | -0.8 | [-5.0, +8.3] | 0.754 |
| 16 | 68.3% | 73.3% | +5.0 | 78.3% | 78.3% | +0.0 | [-3.6, +13.6] | 0.508 |

## random

| N | sel bon | sel bok | Δsel | ceil bon | ceil bok | Δceil | paired Δsel 95% CI | McNemar p |
|---|---|---|---|---|---|---|---|---|
| 1 | 44.6% | 43.3% | -1.2 | 44.6% | 43.3% | -1.2 | [-4.0, +1.5] | 0.581 |
| 2 | 60.8% | 54.2% | -6.7 | 62.1% | 54.6% | -7.5 | [-13.2, -0.2] | 0.0113 |
| 4 | 62.9% | 60.0% | -2.9 | 67.1% | 62.1% | -5.0 | [-8.5, +2.7] | 0.311 |
| 8 | 65.0% | 63.3% | -1.7 | 70.8% | 68.3% | -2.5 | [-7.9, +4.5] | 0.774 |
| 16 | 58.3% | 68.3% | +10.0 | 75.0% | 75.0% | +0.0 | [+0.1, +19.9] | 0.109 |

## tourney

| N | sel bon | sel bok | Δsel | ceil bon | ceil bok | Δceil | paired Δsel 95% CI | McNemar p |
|---|---|---|---|---|---|---|---|---|
| 1 | 45.8% | 45.0% | -0.8 | 45.8% | 45.0% | -0.8 | [-2.8, +1.2] | 0.754 |
| 2 | 56.2% | 56.2% | +0.0 | 57.1% | 57.1% | +0.0 | [-4.1, +4.1] | 1 |
| 4 | 65.0% | 62.9% | -2.1 | 67.1% | 65.8% | -1.3 | [-5.6, +1.5] | 0.405 |
| 8 | 65.0% | 65.8% | +0.8 | 73.3% | 68.3% | -5.0 | [-5.1, +6.8] | 1 |
| 16 | 73.3% | 70.0% | -3.3 | 80.0% | 73.3% | -6.7 | [-13.8, +7.1] | 0.754 |

## Headline

- Mean ceiling delta (bok − bon) over all 15 arm×N cells: **-1.7 pts**
- Mean ceiling delta on the **rank** arm only: **+0.8 pts**

(n=30, 2 configs — directional, not powered. A near-zero ceiling delta means unique-pruning did not meaningfully change which approaches reached the judge, i.e. the plain regen pool was already about as diverse as clustering could make it.)
