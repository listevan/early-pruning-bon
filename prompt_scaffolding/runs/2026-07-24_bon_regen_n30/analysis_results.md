# Analysis Results — best-of-N (bon) vs best-of-k diverse (bok)

Generated 2026-07-24 by `analysis.py --grid --regen` and `--grid --diverse` over SLURM
array `20430192` (all 4 tasks COMPLETED, exit 0:0).

- **Grid:** `max_plan_tokens` ∈ {1000, 2500} × `prune_ratio` {2} = 2 configs × 3 arms, per variant, plus the shared baseline.
- **Data:** countdown, 30 questions, best-of-N ∈ {1,2,4,8,16}, Qwen3-4B-Instruct-2507.
- **bon** (`main.py --regen`): prune to k = N/2 by rank, regenerate to N completions (even-with-top), judge best-of-N.
- **bok** (`main_diverse.py`): same, but prune to k **UNIQUE** approaches first — LLM-clustered so "unique" means a distinct strategy, not distinct wording.

## Verdict

**Forcing survivor uniqueness did not raise the oracle ceiling.** Mean ceiling delta
(bok − bon) is **−1.7 pts** over all 15 arm×N cells and **+0.8 pts** on the rank arm —
both near zero, none individually significant (n=30, 2 configs). The one nominally
significant cell (random N=2, bok worse, McNemar p=0.011) is 1 of 15 and dies under any
multiplicity correction.

Read together with the earlier finding that plain regen collapses toward best-of-k: the
plain regen pool was **already about as diverse as clustering could make it**. At
prune_ratio 2 the model's N drafts mostly fall into distinct approaches already, so
deduplicating the survivors rarely swaps anyone in, and `first_k_unique` degrades to the
plain top-k. Clustering ran (15 calls/config in the bok logs) but had little to remove.

Caveat: this is underpowered and only tests prune 2. Unique-pruning could still matter at
aggressive prune ratios (3–4), where the top-k by rank is far likelier to contain
same-approach duplicates. That is the follow-up worth running.

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

---

## Full grid — bon (best-of-N regen)
```

############################################################################################################
# CONFIG  plan=1000  prune=2.0
############################################################################################################
============================================================================================================
FILES
  baseline  2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json
  random    2026-07-24_11-05-43_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_2.0_regen.json
  rank      2026-07-24_11-05-30_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_2.0_regen.json
  tourney   2026-07-24_11-05-55_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_2.0_regen.json
  N values: [1, 2, 4, 8, 16]
  questions: baseline=100, random=30, rank=30, tourney=30
  NOTE: arms differ in question count -- paired contrasts use the 30 shared questions. Section 1 accuracies are each arm's own mean over its own questions, so the baseline row there is NOT restricted to the overlap and will not equal the contrasts.

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16
baseline      47.5%   8417t    54.5%  17179t    63.0%  34192t    69.5%  67682t    70.0% 133659t
rank          50.8%   5957t    55.8%  11181t    62.5%  21516t    61.7%  41930t    66.7%  82438t
random        42.5%   5953t    59.2%  11410t    62.5%  22735t    70.0%  43691t    56.7%  89004t
tourney       45.0%   5723t    53.3%  11210t    65.0%  21466t    68.3%  43516t    76.7%  83869t

============================================================================================================
2. JUDGE vs RANDOM PICK, WITHIN THE SAME POOL   (does selection beat chance?)

baseline N=1: judge - random       d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
baseline N=2: judge - random       d = +7.2 pts   naive 95% CI [+4.2, +10.3]   cluster 95% CI [+3.9, +10.6]   deff 1.19   b/c 35/6   McNemar p = 4.87e-06   clustered p = 2.36e-05
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 83%
baseline N=4: judge - random       d = +14.2 pts   naive 95% CI [+10.4, +18.1]   cluster 95% CI [+9.8, +18.7]   deff 1.32   b/c 63/6   McNemar p = 4.47e-13   clustered p = 2.6e-10
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 60%
baseline N=8: judge - random       d = +21.0 pts   naive 95% CI [+15.0, +27.0]   cluster 95% CI [+14.2, +27.8]   deff 1.29   b/c 44/2   McNemar p = 3.08e-11   clustered p = 1.86e-09
                                   power: MDE(80%) 9.8 pts   power to detect 5 pts = 30%   <- underpowered; a null here is NOT evidence of no effect
baseline N=16: judge - random      d = +25.0 pts   naive 95% CI [+14.8, +35.2]   cluster 95% CI [+14.8, +35.2]   deff 0.99   b/c 29/4   McNemar p = 1.09e-05   clustered p = 1.51e-06
                                   power: MDE(80%) 14.6 pts   power to detect 5 pts = 16%   <- underpowered; a null here is NOT evidence of no effect

rank N=1: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=2: judge - random           d = +8.3 pts   naive 95% CI [+3.4, +13.3]   cluster 95% CI [+3.4, +13.2]   deff 0.94   b/c 10/0   McNemar p = 0.00195   clustered p = 0.000839
                                   power: MDE(80%) 7.0 pts   power to detect 5 pts = 52%
rank N=4: judge - random           d = +10.8 pts   naive 95% CI [+4.0, +17.7]   cluster 95% CI [+2.5, +19.2]   deff 1.43   b/c 16/3   McNemar p = 0.00443   clustered p = 0.0112
                                   power: MDE(80%) 12.0 pts   power to detect 5 pts = 22%   <- underpowered; a null here is NOT evidence of no effect
rank N=8: judge - random           d = +13.3 pts   naive 95% CI [+2.4, +24.2]   cluster 95% CI [+1.9, +24.8]   deff 1.07   b/c 10/2   McNemar p = 0.0386   clustered p = 0.0224
                                   power: MDE(80%) 16.4 pts   power to detect 5 pts = 13%   <- underpowered; a null here is NOT evidence of no effect
rank N=16: judge - random          d = +23.3 pts   naive 95% CI [+7.9, +38.7]   cluster 95% CI [+7.9, +38.7]   deff 0.97   b/c 7/0   McNemar p = 0.0156   clustered p = 0.00297
                                   power: MDE(80%) 22.0 pts   power to detect 5 pts = 9%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +10.8 pts   naive 95% CI [+4.8, +16.9]   cluster 95% CI [+3.5, +18.1]   deff 1.41   b/c 14/1   McNemar p = 0.000977   clustered p = 0.00368
                                   power: MDE(80%) 10.4 pts   power to detect 5 pts = 27%   <- underpowered; a null here is NOT evidence of no effect
random N=4: judge - random         d = +12.5 pts   naive 95% CI [+5.7, +19.3]   cluster 95% CI [+4.8, +20.2]   deff 1.25   b/c 17/2   McNemar p = 0.000729   clustered p = 0.00147
                                   power: MDE(80%) 11.0 pts   power to detect 5 pts = 25%   <- underpowered; a null here is NOT evidence of no effect
random N=8: judge - random         d = +20.0 pts   naive 95% CI [+8.8, +31.2]   cluster 95% CI [+7.9, +32.1]   deff 1.12   b/c 13/1   McNemar p = 0.00183   clustered p = 0.00116
                                   power: MDE(80%) 17.3 pts   power to detect 5 pts = 13%   <- underpowered; a null here is NOT evidence of no effect
random N=16: judge - random        d = +10.0 pts   naive 95% CI [-9.6, +29.6]   cluster 95% CI [-9.6, +29.6]   deff 0.97   b/c 6/3   McNemar p = 0.508   clustered p = 0.317
                                   power: MDE(80%) 28.0 pts   power to detect 5 pts = 7%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +4.2 pts   naive 95% CI [+0.6, +7.8]   cluster 95% CI [+0.0, +8.3]   deff 1.28   b/c 5/0   McNemar p = 0.0625   clustered p = 0.0477
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
tourney N=4: judge - random        d = +10.8 pts   naive 95% CI [+4.8, +16.9]   cluster 95% CI [+4.8, +16.9]   deff 0.98   b/c 14/1   McNemar p = 0.000977   clustered p = 0.000472
                                   power: MDE(80%) 8.7 pts   power to detect 5 pts = 36%   <- underpowered; a null here is NOT evidence of no effect
tourney N=8: judge - random        d = +25.0 pts   naive 95% CI [+12.1, +37.9]   cluster 95% CI [+11.1, +38.9]   deff 1.13   b/c 17/2   McNemar p = 0.000729   clustered p = 0.000423
                                   power: MDE(80%) 19.9 pts   power to detect 5 pts = 10%   <- underpowered; a null here is NOT evidence of no effect
tourney N=16: judge - random       d = +26.7 pts   naive 95% CI [+10.6, +42.8]   cluster 95% CI [+10.6, +42.8]   deff 0.97   b/c 8/0   McNemar p = 0.00781   clustered p = 0.00116
                                   power: MDE(80%) 23.0 pts   power to detect 5 pts = 9%   <- underpowered; a null here is NOT evidence of no effect

============================================================================================================
3. ORACLE CEILING   (a correct candidate EXISTS vs the judge FINDS it)
   NOTE: for pruned arms this is pass@k over SURVIVORS, not over all N.
   Only the baseline row is a clean best-of-N ceiling.

baseline   N=1   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
baseline   N=2   ceiling  57.0%   selected  54.5%   gap  2.5 pts   capture  95.6%
baseline   N=4   ceiling  66.2%   selected  63.0%   gap  3.2 pts   capture  95.1%
baseline   N=8   ceiling  73.5%   selected  69.5%   gap  4.0 pts   capture  94.6%
baseline   N=16  ceiling  79.0%   selected  70.0%   gap  9.0 pts   capture  88.6%

rank       N=1   ceiling  50.8%   selected  50.8%   gap  0.0 pts   capture 100.0%
rank       N=2   ceiling  55.8%   selected  55.8%   gap  0.0 pts   capture 100.0%
rank       N=4   ceiling  65.8%   selected  62.5%   gap  3.3 pts   capture  94.9%
rank       N=8   ceiling  70.0%   selected  61.7%   gap  8.3 pts   capture  88.1%
rank       N=16  ceiling  73.3%   selected  66.7%   gap  6.7 pts   capture  90.9%

random     N=1   ceiling  42.5%   selected  42.5%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  60.8%   selected  59.2%   gap  1.7 pts   capture  97.3%
random     N=4   ceiling  67.5%   selected  62.5%   gap  5.0 pts   capture  92.6%
random     N=8   ceiling  73.3%   selected  70.0%   gap  3.3 pts   capture  95.5%
random     N=16  ceiling  76.7%   selected  56.7%   gap 20.0 pts   capture  73.9%

tourney    N=1   ceiling  45.0%   selected  45.0%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  54.2%   selected  53.3%   gap  0.8 pts   capture  98.5%
tourney    N=4   ceiling  66.7%   selected  65.0%   gap  1.7 pts   capture  97.5%
tourney    N=8   ceiling  75.0%   selected  68.3%   gap  6.7 pts   capture  91.1%
tourney    N=16  ceiling  76.7%   selected  76.7%   gap  0.0 pts   capture 100.0%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = +8.3 pts   naive 95% CI [+0.8, +15.9]   cluster 95% CI [+1.2, +15.5]   deff 0.87   b/c 16/6   McNemar p = 0.0525   clustered p = 0.0229
                                   power: MDE(80%) 10.3 pts   power to detect 5 pts = 28%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound +1.2 -> NON-INFERIOR   one-sided p = 0.000136
                                   tokens 5957 vs 5953  (+0.1%, 95% CI [-9.4%, +9.5%])
N=2   rank - random                d = -3.3 pts   naive 95% CI [-10.3, +3.6]   cluster 95% CI [-10.3, +3.6]   deff 0.97   b/c 7/11   McNemar p = 0.481   clustered p = 0.347
                                   power: MDE(80%) 9.9 pts   power to detect 5 pts = 29%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -10.3 -> cannot claim parity   one-sided p = 0.319
                                   tokens 11181 vs 11410  (-2.0%, 95% CI [-8.5%, +4.5%])
N=4   rank - random                d = +0.0 pts   naive 95% CI [-5.2, +5.2]   cluster 95% CI [-5.8, +5.8]   deff 1.19   b/c 5/5   McNemar p = 1   clustered p = 1
                                   power: MDE(80%) 8.2 pts   power to detect 5 pts = 40%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -5.8 -> cannot claim parity   one-sided p = 0.0443
                                   tokens 21516 vs 22735  (-5.4%, 95% CI [-11.4%, +0.7%])
N=8   rank - random                d = -8.3 pts   naive 95% CI [-16.8, +0.1]   cluster 95% CI [-17.8, +1.2]   deff 1.22   b/c 1/6   McNemar p = 0.125   clustered p = 0.0854
                                   power: MDE(80%) 13.6 pts   power to detect 5 pts = 18%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -17.8 -> cannot claim parity   one-sided p = 0.754
                                   tokens 41930 vs 43691  (-4.0%, 95% CI [-10.1%, +2.0%])
N=16  rank - random                d = +10.0 pts   naive 95% CI [-7.2, +27.2]   cluster 95% CI [-7.2, +27.2]   deff 0.97   b/c 5/2   McNemar p = 0.453   clustered p = 0.254
                                   power: MDE(80%) 24.6 pts   power to detect 5 pts = 8%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -7.2 -> cannot claim parity   one-sided p = 0.0437
                                   tokens 82438 vs 89004  (-7.4%, 95% CI [-15.4%, +0.6%])

N=1   rank - baseline              d = +0.8 pts   naive 95% CI [-7.0, +8.7]   cluster 95% CI [-6.8, +8.4]   deff 0.90   b/c 12/11   McNemar p = 1   clustered p = 0.83
                                   power: MDE(80%) 10.9 pts   power to detect 5 pts = 25%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -6.8 -> cannot claim parity   one-sided p = 0.0664
                                   tokens 5957 vs 8417  (-23.0%, 95% CI [-30.4%, -15.6%])
N=2   rank - baseline              d = -2.5 pts   naive 95% CI [-9.2, +4.2]   cluster 95% CI [-9.3, +4.3]   deff 0.98   b/c 7/10   McNemar p = 0.629   clustered p = 0.47
                                   power: MDE(80%) 9.7 pts   power to detect 5 pts = 30%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -9.3 -> cannot claim parity   one-sided p = 0.235
                                   tokens 11181 vs 17179  (-30.3%, 95% CI [-36.2%, -24.5%])
N=4   rank - baseline              d = -1.7 pts   naive 95% CI [-5.7, +2.3]   cluster 95% CI [-6.3, +3.0]   deff 1.31   b/c 2/4   McNemar p = 0.688   clustered p = 0.483
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 56%
                                   non-inferiority (margin 5 pts): lower bound -6.3 -> cannot claim parity   one-sided p = 0.0804
                                   tokens 21516 vs 34192  (-32.6%, 95% CI [-38.2%, -26.9%])
N=8   rank - baseline              d = -5.0 pts   naive 95% CI [-12.3, +2.3]   cluster 95% CI [-12.2, +2.2]   deff 0.95   b/c 1/4   McNemar p = 0.375   clustered p = 0.174
                                   power: MDE(80%) 10.3 pts   power to detect 5 pts = 27%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -12.2 -> cannot claim parity   one-sided p = 0.5
                                   tokens 41930 vs 67682  (-33.5%, 95% CI [-39.9%, -27.0%])
N=16  rank - baseline              d = +3.3 pts   naive 95% CI [-8.1, +14.8]   cluster 95% CI [-8.1, +14.8]   deff 0.97   b/c 2/1   McNemar p = 1   clustered p = 0.568
                                   power: MDE(80%) 16.4 pts   power to detect 5 pts = 13%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -8.1 -> cannot claim parity   one-sided p = 0.0768
                                   tokens 82438 vs 133659  (-34.1%, 95% CI [-39.2%, -29.0%])

N=1   tourney - baseline           d = -5.0 pts   naive 95% CI [-11.9, +1.9]   cluster 95% CI [-11.8, +1.8]   deff 0.94   b/c 6/12   McNemar p = 0.238   clustered p = 0.15
                                   power: MDE(80%) 9.7 pts   power to detect 5 pts = 30%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -11.8 -> cannot claim parity   one-sided p = 0.5
                                   tokens 5723 vs 8417  (-26.0%, 95% CI [-34.4%, -17.6%])
N=2   tourney - baseline           d = -5.0 pts   naive 95% CI [-11.1, +1.1]   cluster 95% CI [-11.8, +1.8]   deff 1.22   b/c 4/10   McNemar p = 0.18   clustered p = 0.15
                                   power: MDE(80%) 9.7 pts   power to detect 5 pts = 30%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -11.8 -> cannot claim parity   one-sided p = 0.5
                                   tokens 11210 vs 17179  (-30.1%, 95% CI [-37.1%, -23.2%])
N=4   tourney - baseline           d = +0.8 pts   naive 95% CI [-3.5, +5.2]   cluster 95% CI [-3.6, +5.2]   deff 0.99   b/c 4/3   McNemar p = 1   clustered p = 0.71
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 61%
                                   non-inferiority (margin 5 pts): lower bound -3.6 -> NON-INFERIOR   one-sided p = 0.00456
                                   tokens 21466 vs 34192  (-32.7%, 95% CI [-38.4%, -27.1%])
N=8   tourney - baseline           d = +1.7 pts   naive 95% CI [-7.0, +10.4]   cluster 95% CI [-8.3, +11.6]   deff 1.26   b/c 4/3   McNemar p = 1   clustered p = 0.743
                                   power: MDE(80%) 14.2 pts   power to detect 5 pts = 16%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -8.3 -> cannot claim parity   one-sided p = 0.0945
                                   tokens 43516 vs 67682  (-31.0%, 95% CI [-36.8%, -25.1%])
N=16  tourney - baseline           d = +13.3 pts   naive 95% CI [+1.0, +25.7]   cluster 95% CI [+1.0, +25.7]   deff 0.97   b/c 4/0   McNemar p = 0.125   clustered p = 0.0347
                                   power: MDE(80%) 17.7 pts   power to detect 5 pts = 12%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound +1.0 -> NON-INFERIOR   one-sided p = 0.00184
                                   tokens 83869 vs 133659  (-33.0%, 95% CI [-39.1%, -26.9%])

N=1   random - baseline            d = -7.5 pts   naive 95% CI [-14.9, -0.1]   cluster 95% CI [-16.0, +1.0]   deff 1.28   b/c 6/15   McNemar p = 0.0784   clustered p = 0.0844
                                   power: MDE(80%) 12.2 pts   power to detect 5 pts = 21%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -16.0 -> cannot claim parity   one-sided p = 0.717
                                   tokens 5953 vs 8417  (-23.0%, 95% CI [-32.9%, -13.2%])
N=2   random - baseline            d = +0.8 pts   naive 95% CI [-5.1, +6.7]   cluster 95% CI [-6.4, +8.1]   deff 1.45   b/c 7/6   McNemar p = 1   clustered p = 0.821
                                   power: MDE(80%) 10.3 pts   power to detect 5 pts = 27%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -6.4 -> cannot claim parity   one-sided p = 0.057
                                   tokens 11410 vs 17179  (-28.9%, 95% CI [-34.7%, -23.1%])
N=4   random - baseline            d = -1.7 pts   naive 95% CI [-7.8, +4.5]   cluster 95% CI [-9.4, +6.1]   deff 1.55   b/c 6/8   McNemar p = 0.791   clustered p = 0.674
                                   power: MDE(80%) 11.1 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -9.4 -> cannot claim parity   one-sided p = 0.2
                                   tokens 22735 vs 34192  (-28.8%, 95% CI [-35.2%, -22.3%])
N=8   random - baseline            d = +3.3 pts   naive 95% CI [-4.7, +11.4]   cluster 95% CI [-6.0, +12.7]   deff 1.30   b/c 4/2   McNemar p = 0.688   clustered p = 0.483
                                   power: MDE(80%) 13.3 pts   power to detect 5 pts = 18%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -6.0 -> cannot claim parity   one-sided p = 0.0398
                                   tokens 43691 vs 67682  (-30.7%, 95% CI [-37.0%, -24.3%])
N=16  random - baseline            d = -6.7 pts   naive 95% CI [-19.7, +6.4]   cluster 95% CI [-19.7, +6.4]   deff 0.97   b/c 1/3   McNemar p = 0.625   clustered p = 0.317
                                   power: MDE(80%) 18.7 pts   power to detect 5 pts = 11%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -19.7 -> cannot claim parity   one-sided p = 0.599
                                   tokens 89004 vs 133659  (-28.9%, 95% CI [-34.8%, -22.9%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = +0.9 pts   naive 95% CI [-2.6, +4.4]   cluster 95% CI [-2.7, +4.5]   deff 1.05   b/c 34/30   McNemar p = 0.708   clustered p = 0.632
                                   power: MDE(80%) 5.2 pts   power to detect 5 pts = 77%
                                   equal-weight per N: d = +1.3 pts (from 5 cells: +8.3, -3.3, +0.0, -8.3, +10.0)

pooled rank - baseline (chunk-wtd) d = -1.3 pts   naive 95% CI [-4.5, +1.9]   cluster 95% CI [-5.0, +2.3]   deff 1.27   b/c 24/30   McNemar p = 0.497   clustered p = 0.477
                                   power: MDE(80%) 5.3 pts   power to detect 5 pts = 76%
                                   equal-weight per N: d = -1.0 pts (from 5 cells: +0.8, -2.5, -1.7, -5.0, +3.3)

pooled tourney - baseline (chunk-wtd) d = -1.3 pts   naive 95% CI [-4.4, +1.7]   cluster 95% CI [-5.8, +3.2]   deff 2.05   b/c 22/28   McNemar p = 0.48   clustered p = 0.561
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 59%
                                   equal-weight per N: d = +1.2 pts (from 5 cells: -5.0, -5.0, +0.8, +1.7, +13.3)

pooled random - baseline (chunk-wtd) d = -2.2 pts   naive 95% CI [-5.5, +1.1]   cluster 95% CI [-7.4, +3.0]   deff 2.39   b/c 24/34   McNemar p = 0.237   clustered p = 0.404
                                   power: MDE(80%) 7.5 pts   power to detect 5 pts = 47%   <- underpowered; a null here is NOT evidence of no effect
                                   equal-weight per N: d = -2.3 pts (from 5 cells: -7.5, +0.8, -1.7, +3.3, -6.7)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = +0.8 pts   95% CI [-6.8, +8.4]   win/loss 7/3   p = 0.83   sign p = 0.344
                                   tokens 5957 vs 8417 (-29.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -6.8 -> cannot claim parity   one-sided p = 0.0664
                                   WARNING: -29% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 10.9 pts   power to detect 5 pts = 25%   <- underpowered
rank N=2 vs baseline N=1           d = +5.8 pts   95% CI [-1.5, +13.1]   win/loss 7/3   p = 0.118   sign p = 0.344
                                   tokens 11181 vs 8417 (+32.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.5 -> NON-INFERIOR   one-sided p = 0.00184
                                   WARNING: +33% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 10.4 pts   power to detect 5 pts = 27%   <- underpowered
rank N=4 vs baseline N=2           d = +4.2 pts   95% CI [-2.1, +10.4]   win/loss 6/3   p = 0.192   sign p = 0.508
                                   tokens 21516 vs 17179 (+25.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.1 -> NON-INFERIOR   one-sided p = 0.00203
                                   WARNING: +25% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 8.9 pts   power to detect 5 pts = 35%   <- underpowered
rank N=8 vs baseline N=4           d = -2.5 pts   95% CI [-9.3, +4.3]   win/loss 2/3   p = 0.47   sign p = 1
                                   tokens 41930 vs 34192 (+22.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -9.3 -> cannot claim parity   one-sided p = 0.235
                                   WARNING: +23% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 9.7 pts   power to detect 5 pts = 30%   <- underpowered
rank N=16 vs baseline N=8          d = +0.0 pts   95% CI [-9.4, +9.4]   win/loss 1/1   p = 1   sign p = 1
                                   tokens 82438 vs 67682 (+21.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -9.4 -> cannot claim parity   one-sided p = 0.149
                                   WARNING: +22% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 13.4 pts   power to detect 5 pts = 18%   <- underpowered

random N=1 vs baseline N=1         d = -7.5 pts   95% CI [-16.0, +1.0]   win/loss 4/9   p = 0.0844   sign p = 0.267
                                   tokens 5953 vs 8417 (-29.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -16.0 -> cannot claim parity   one-sided p = 0.717
                                   WARNING: -29% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 12.2 pts   power to detect 5 pts = 21%   <- underpowered
random N=2 vs baseline N=1         d = +9.2 pts   95% CI [+0.5, +17.8]   win/loss 9/2   p = 0.0373   sign p = 0.0654
                                   tokens 11410 vs 8417 (+35.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.5 -> NON-INFERIOR   one-sided p = 0.000644
                                   WARNING: +36% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 12.3 pts   power to detect 5 pts = 20%   <- underpowered
random N=4 vs baseline N=2         d = +4.2 pts   95% CI [-3.3, +11.6]   win/loss 8/4   p = 0.274   sign p = 0.388
                                   tokens 22735 vs 17179 (+32.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.3 -> NON-INFERIOR   one-sided p = 0.00801
                                   WARNING: +32% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 10.7 pts   power to detect 5 pts = 26%   <- underpowered
random N=8 vs baseline N=4         d = +5.8 pts   95% CI [-4.0, +15.7]   win/loss 5/2   p = 0.247   sign p = 0.453
                                   tokens 43691 vs 34192 (+27.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.0 -> NON-INFERIOR   one-sided p = 0.0158
                                   WARNING: +28% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 14.1 pts   power to detect 5 pts = 17%   <- underpowered
random N=16 vs baseline N=8        d = -10.0 pts   95% CI [-24.4, +4.4]   win/loss 1/4   p = 0.174   sign p = 0.375
                                   tokens 89004 vs 67682 (+31.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -24.4 -> cannot claim parity   one-sided p = 0.752
                                   WARNING: +32% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 20.6 pts   power to detect 5 pts = 10%   <- underpowered

tourney N=1 vs baseline N=1        d = -5.0 pts   95% CI [-11.8, +1.8]   win/loss 4/8   p = 0.15   sign p = 0.388
                                   tokens 5723 vs 8417 (-32.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -11.8 -> cannot claim parity   one-sided p = 0.5
                                   WARNING: -32% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 9.7 pts   power to detect 5 pts = 30%   <- underpowered
tourney N=2 vs baseline N=1        d = +3.3 pts   95% CI [-5.4, +12.0]   win/loss 8/3   p = 0.453   sign p = 0.227
                                   tokens 11210 vs 8417 (+33.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.4 -> cannot claim parity   one-sided p = 0.0303
                                   WARNING: +33% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 12.4 pts   power to detect 5 pts = 20%   <- underpowered
tourney N=4 vs baseline N=2        d = +6.7 pts   95% CI [+0.5, +12.9]   win/loss 8/2   p = 0.0347   sign p = 0.109
                                   tokens 21466 vs 17179 (+25.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.5 -> NON-INFERIOR   one-sided p = 0.000109
                                   WARNING: +25% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 8.8 pts   power to detect 5 pts = 35%   <- underpowered
tourney N=8 vs baseline N=4        d = +4.2 pts   95% CI [-5.3, +13.6]   win/loss 4/2   p = 0.386   sign p = 0.688
                                   tokens 43516 vs 34192 (+27.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.3 -> cannot claim parity   one-sided p = 0.0283
                                   WARNING: +27% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 13.5 pts   power to detect 5 pts = 18%   <- underpowered
tourney N=16 vs baseline N=8       d = +10.0 pts   95% CI [-0.9, +20.9]   win/loss 3/0   p = 0.0726   sign p = 0.25
                                   tokens 83869 vs 67682 (+23.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -0.9 -> NON-INFERIOR   one-sided p = 0.00355
                                   WARNING: +24% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 15.6 pts   power to detect 5 pts = 14%   <- underpowered

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

############################################################################################################
# CONFIG  plan=2500  prune=2.0
############################################################################################################
============================================================================================================
FILES
  baseline  2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json
  random    2026-07-24_09-05-19_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_2.0_regen.json
  rank      2026-07-24_09-05-06_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_2.0_regen.json
  tourney   2026-07-24_09-05-32_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_2.0_regen.json
  N values: [1, 2, 4, 8, 16]
  questions: baseline=100, random=30, rank=30, tourney=30
  NOTE: arms differ in question count -- paired contrasts use the 30 shared questions. Section 1 accuracies are each arm's own mean over its own questions, so the baseline row there is NOT restricted to the overlap and will not equal the contrasts.

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16
baseline      47.5%   8417t    54.5%  17179t    63.0%  34192t    69.5%  67682t    70.0% 133659t
rank          47.5%   5829t    56.7%  10144t    65.8%  20905t    65.0%  40696t    70.0%  78041t
random        46.7%   5606t    62.5%  10806t    63.3%  22737t    60.0%  44602t    60.0%  91581t
tourney       46.7%   5777t    59.2%  10228t    65.0%  20746t    61.7%  41249t    70.0%  83158t

============================================================================================================
2. JUDGE vs RANDOM PICK, WITHIN THE SAME POOL   (does selection beat chance?)

baseline N=1: judge - random       d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
baseline N=2: judge - random       d = +7.2 pts   naive 95% CI [+4.2, +10.3]   cluster 95% CI [+3.9, +10.6]   deff 1.19   b/c 35/6   McNemar p = 4.87e-06   clustered p = 2.36e-05
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 83%
baseline N=4: judge - random       d = +14.2 pts   naive 95% CI [+10.4, +18.1]   cluster 95% CI [+9.8, +18.7]   deff 1.32   b/c 63/6   McNemar p = 4.47e-13   clustered p = 2.6e-10
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 60%
baseline N=8: judge - random       d = +21.0 pts   naive 95% CI [+15.0, +27.0]   cluster 95% CI [+14.2, +27.8]   deff 1.29   b/c 44/2   McNemar p = 3.08e-11   clustered p = 1.86e-09
                                   power: MDE(80%) 9.8 pts   power to detect 5 pts = 30%   <- underpowered; a null here is NOT evidence of no effect
baseline N=16: judge - random      d = +25.0 pts   naive 95% CI [+14.8, +35.2]   cluster 95% CI [+14.8, +35.2]   deff 0.99   b/c 29/4   McNemar p = 1.09e-05   clustered p = 1.51e-06
                                   power: MDE(80%) 14.6 pts   power to detect 5 pts = 16%   <- underpowered; a null here is NOT evidence of no effect

rank N=1: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=2: judge - random           d = +1.7 pts   naive 95% CI [-0.6, +4.0]   cluster 95% CI [-0.6, +3.9]   deff 0.94   b/c 2/0   McNemar p = 0.5   clustered p = 0.15
                                   power: MDE(80%) 3.2 pts   power to detect 5 pts = 99%
rank N=4: judge - random           d = +10.0 pts   naive 95% CI [+3.7, +16.3]   cluster 95% CI [+3.1, +16.9]   deff 1.15   b/c 14/2   McNemar p = 0.00418   clustered p = 0.00444
                                   power: MDE(80%) 9.8 pts   power to detect 5 pts = 30%   <- underpowered; a null here is NOT evidence of no effect
rank N=8: judge - random           d = +10.0 pts   naive 95% CI [-0.1, +20.1]   cluster 95% CI [+0.1, +19.9]   deff 0.92   b/c 8/2   McNemar p = 0.109   clustered p = 0.0467
                                   power: MDE(80%) 14.1 pts   power to detect 5 pts = 17%   <- underpowered; a null here is NOT evidence of no effect
rank N=16: judge - random          d = +13.3 pts   naive 95% CI [+1.0, +25.7]   cluster 95% CI [+1.0, +25.7]   deff 0.97   b/c 4/0   McNemar p = 0.125   clustered p = 0.0347
                                   power: MDE(80%) 17.7 pts   power to detect 5 pts = 12%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +8.3 pts   naive 95% CI [+3.4, +13.3]   cluster 95% CI [+3.4, +13.2]   deff 0.94   b/c 10/0   McNemar p = 0.00195   clustered p = 0.000839
                                   power: MDE(80%) 7.0 pts   power to detect 5 pts = 52%
random N=4: judge - random         d = +16.7 pts   naive 95% CI [+8.9, +24.5]   cluster 95% CI [+7.2, +26.2]   deff 1.43   b/c 23/3   McNemar p = 8.8e-05   clustered p = 0.000581
                                   power: MDE(80%) 13.6 pts   power to detect 5 pts = 18%   <- underpowered; a null here is NOT evidence of no effect
random N=8: judge - random         d = +13.3 pts   naive 95% CI [+1.5, +25.2]   cluster 95% CI [+0.1, +26.6]   deff 1.21   b/c 11/3   McNemar p = 0.0574   clustered p = 0.0483
                                   power: MDE(80%) 18.9 pts   power to detect 5 pts = 11%   <- underpowered; a null here is NOT evidence of no effect
random N=16: judge - random        d = +0.0 pts   naive 95% CI [-16.3, +16.3]   cluster 95% CI [-16.3, +16.3]   deff 0.97   b/c 3/3   McNemar p = 1   clustered p = 1
                                   power: MDE(80%) 23.3 pts   power to detect 5 pts = 9%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +1.7 pts   naive 95% CI [-1.6, +4.9]   cluster 95% CI [-0.6, +3.9]   deff 0.47   b/c 3/1   McNemar p = 0.625   clustered p = 0.15
                                   power: MDE(80%) 3.2 pts   power to detect 5 pts = 99%
tourney N=4: judge - random        d = +11.7 pts   naive 95% CI [+5.4, +17.9]   cluster 95% CI [+4.0, +19.4]   deff 1.48   b/c 15/1   McNemar p = 0.000519   clustered p = 0.00297
                                   power: MDE(80%) 11.0 pts   power to detect 5 pts = 25%   <- underpowered; a null here is NOT evidence of no effect
tourney N=8: judge - random        d = +13.3 pts   naive 95% CI [+0.6, +26.1]   cluster 95% CI [+1.0, +25.7]   deff 0.91   b/c 12/4   McNemar p = 0.0768   clustered p = 0.0347
                                   power: MDE(80%) 17.7 pts   power to detect 5 pts = 12%   <- underpowered; a null here is NOT evidence of no effect
tourney N=16: judge - random       d = +16.7 pts   naive 95% CI [+0.2, +33.2]   cluster 95% CI [+0.2, +33.2]   deff 0.97   b/c 6/1   McNemar p = 0.125   clustered p = 0.0477
                                   power: MDE(80%) 23.6 pts   power to detect 5 pts = 9%   <- underpowered; a null here is NOT evidence of no effect

============================================================================================================
3. ORACLE CEILING   (a correct candidate EXISTS vs the judge FINDS it)
   NOTE: for pruned arms this is pass@k over SURVIVORS, not over all N.
   Only the baseline row is a clean best-of-N ceiling.

baseline   N=1   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
baseline   N=2   ceiling  57.0%   selected  54.5%   gap  2.5 pts   capture  95.6%
baseline   N=4   ceiling  66.2%   selected  63.0%   gap  3.2 pts   capture  95.1%
baseline   N=8   ceiling  73.5%   selected  69.5%   gap  4.0 pts   capture  94.6%
baseline   N=16  ceiling  79.0%   selected  70.0%   gap  9.0 pts   capture  88.6%

rank       N=1   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
rank       N=2   ceiling  56.7%   selected  56.7%   gap  0.0 pts   capture 100.0%
rank       N=4   ceiling  69.2%   selected  65.8%   gap  3.3 pts   capture  95.2%
rank       N=8   ceiling  70.0%   selected  65.0%   gap  5.0 pts   capture  92.9%
rank       N=16  ceiling  83.3%   selected  70.0%   gap 13.3 pts   capture  84.0%

random     N=1   ceiling  46.7%   selected  46.7%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  63.3%   selected  62.5%   gap  0.8 pts   capture  98.7%
random     N=4   ceiling  66.7%   selected  63.3%   gap  3.3 pts   capture  95.0%
random     N=8   ceiling  68.3%   selected  60.0%   gap  8.3 pts   capture  87.8%
random     N=16  ceiling  73.3%   selected  60.0%   gap 13.3 pts   capture  81.8%

tourney    N=1   ceiling  46.7%   selected  46.7%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  60.0%   selected  59.2%   gap  0.8 pts   capture  98.6%
tourney    N=4   ceiling  67.5%   selected  65.0%   gap  2.5 pts   capture  96.3%
tourney    N=8   ceiling  71.7%   selected  61.7%   gap 10.0 pts   capture  86.0%
tourney    N=16  ceiling  83.3%   selected  70.0%   gap 13.3 pts   capture  84.0%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = +0.8 pts   naive 95% CI [-6.3, +8.0]   cluster 95% CI [-4.1, +5.8]   deff 0.47   b/c 10/9   McNemar p = 1   clustered p = 0.743
                                   power: MDE(80%) 7.1 pts   power to detect 5 pts = 50%
                                   non-inferiority (margin 5 pts): lower bound -4.1 -> NON-INFERIOR   one-sided p = 0.0108
                                   tokens 5829 vs 5606  (+4.0%, 95% CI [-4.1%, +12.1%])
N=2   rank - random                d = -5.8 pts   naive 95% CI [-13.3, +1.6]   cluster 95% CI [-17.5, +5.8]   deff 2.38   b/c 7/14   McNemar p = 0.189   clustered p = 0.327
                                   power: MDE(80%) 16.7 pts   power to detect 5 pts = 13%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -17.5 -> cannot claim parity   one-sided p = 0.556
                                   tokens 10144 vs 10806  (-6.1%, 95% CI [-12.4%, +0.2%])
N=4   rank - random                d = +2.5 pts   naive 95% CI [-3.8, +8.8]   cluster 95% CI [-1.8, +6.8]   deff 0.45   b/c 9/6   McNemar p = 0.607   clustered p = 0.254
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
                                   non-inferiority (margin 5 pts): lower bound -1.8 -> NON-INFERIOR   one-sided p = 0.000315
                                   tokens 20905 vs 22737  (-8.1%, 95% CI [-13.1%, -3.0%])
N=8   rank - random                d = +5.0 pts   naive 95% CI [-4.8, +14.8]   cluster 95% CI [-3.6, +13.6]   deff 0.74   b/c 6/3   McNemar p = 0.508   clustered p = 0.254
                                   power: MDE(80%) 12.3 pts   power to detect 5 pts = 21%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -3.6 -> NON-INFERIOR   one-sided p = 0.0113
                                   tokens 40696 vs 44602  (-8.8%, 95% CI [-14.4%, -3.1%])
N=16  rank - random                d = +10.0 pts   naive 95% CI [-7.2, +27.2]   cluster 95% CI [-7.2, +27.2]   deff 0.97   b/c 5/2   McNemar p = 0.453   clustered p = 0.254
                                   power: MDE(80%) 24.6 pts   power to detect 5 pts = 8%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -7.2 -> cannot claim parity   one-sided p = 0.0437
                                   tokens 78041 vs 91581  (-14.8%, 95% CI [-19.9%, -9.7%])

N=1   rank - baseline              d = -2.5 pts   naive 95% CI [-10.0, +5.0]   cluster 95% CI [-9.7, +4.7]   deff 0.89   b/c 9/12   McNemar p = 0.664   clustered p = 0.495
                                   power: MDE(80%) 10.3 pts   power to detect 5 pts = 28%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -9.7 -> cannot claim parity   one-sided p = 0.248
                                   tokens 5829 vs 8417  (-24.6%, 95% CI [-33.1%, -16.2%])
N=2   rank - baseline              d = -1.7 pts   naive 95% CI [-6.8, +3.5]   cluster 95% CI [-8.3, +5.0]   deff 1.58   b/c 4/6   McNemar p = 0.754   clustered p = 0.622
                                   power: MDE(80%) 9.5 pts   power to detect 5 pts = 32%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -8.3 -> cannot claim parity   one-sided p = 0.162
                                   tokens 10144 vs 17179  (-36.8%, 95% CI [-41.0%, -32.6%])
N=4   rank - baseline              d = +1.7 pts   naive 95% CI [-4.0, +7.3]   cluster 95% CI [-4.5, +7.9]   deff 1.15   b/c 7/5   McNemar p = 0.774   clustered p = 0.597
                                   power: MDE(80%) 8.8 pts   power to detect 5 pts = 35%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -4.5 -> NON-INFERIOR   one-sided p = 0.0173
                                   tokens 20905 vs 34192  (-34.5%, 95% CI [-38.9%, -30.1%])
N=8   rank - baseline              d = -1.7 pts   naive 95% CI [-7.4, +4.0]   cluster 95% CI [-7.4, +4.1]   deff 0.98   b/c 1/2   McNemar p = 1   clustered p = 0.568
                                   power: MDE(80%) 8.2 pts   power to detect 5 pts = 40%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -7.4 -> cannot claim parity   one-sided p = 0.127
                                   tokens 40696 vs 67682  (-35.4%, 95% CI [-39.2%, -31.6%])
N=16  rank - baseline              d = +6.7 pts   naive 95% CI [-2.4, +15.7]   cluster 95% CI [-2.4, +15.7]   deff 0.97   b/c 2/0   McNemar p = 0.5   clustered p = 0.15
                                   power: MDE(80%) 13.0 pts   power to detect 5 pts = 19%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -2.4 -> NON-INFERIOR   one-sided p = 0.00589
                                   tokens 78041 vs 133659  (-37.6%, 95% CI [-41.4%, -33.8%])

N=1   tourney - baseline           d = -3.3 pts   naive 95% CI [-9.9, +3.2]   cluster 95% CI [-10.3, +3.6]   deff 1.09   b/c 6/10   McNemar p = 0.454   clustered p = 0.347
                                   power: MDE(80%) 9.9 pts   power to detect 5 pts = 29%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -10.3 -> cannot claim parity   one-sided p = 0.319
                                   tokens 5777 vs 8417  (-25.3%, 95% CI [-32.4%, -18.3%])
N=2   tourney - baseline           d = +0.8 pts   naive 95% CI [-5.1, +6.7]   cluster 95% CI [-4.1, +5.8]   deff 0.68   b/c 7/6   McNemar p = 1   clustered p = 0.743
                                   power: MDE(80%) 7.1 pts   power to detect 5 pts = 50%
                                   non-inferiority (margin 5 pts): lower bound -4.1 -> NON-INFERIOR   one-sided p = 0.0108
                                   tokens 10228 vs 17179  (-36.3%, 95% CI [-40.5%, -32.1%])
N=4   tourney - baseline           d = +0.8 pts   naive 95% CI [-4.1, +5.8]   cluster 95% CI [-5.6, +7.3]   deff 1.65   b/c 5/4   McNemar p = 1   clustered p = 0.799
                                   power: MDE(80%) 9.2 pts   power to detect 5 pts = 33%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -5.6 -> cannot claim parity   one-sided p = 0.0376
                                   tokens 20746 vs 34192  (-35.0%, 95% CI [-38.9%, -31.1%])
N=8   tourney - baseline           d = -5.0 pts   naive 95% CI [-14.8, +4.8]   cluster 95% CI [-16.8, +6.8]   deff 1.41   b/c 3/6   McNemar p = 0.508   clustered p = 0.408
                                   power: MDE(80%) 16.9 pts   power to detect 5 pts = 13%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -16.8 -> cannot claim parity   one-sided p = 0.5
                                   tokens 41249 vs 67682  (-34.6%, 95% CI [-39.3%, -29.8%])
N=16  tourney - baseline           d = +6.7 pts   naive 95% CI [-6.4, +19.7]   cluster 95% CI [-6.4, +19.7]   deff 0.97   b/c 3/1   McNemar p = 0.625   clustered p = 0.317
                                   power: MDE(80%) 18.7 pts   power to detect 5 pts = 11%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -6.4 -> cannot claim parity   one-sided p = 0.0401
                                   tokens 83158 vs 133659  (-33.5%, 95% CI [-37.8%, -29.3%])

N=1   random - baseline            d = -3.3 pts   naive 95% CI [-10.3, +3.6]   cluster 95% CI [-9.0, +2.3]   deff 0.64   b/c 7/11   McNemar p = 0.481   clustered p = 0.245
                                   power: MDE(80%) 8.0 pts   power to detect 5 pts = 41%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -9.0 -> cannot claim parity   one-sided p = 0.281
                                   tokens 5606 vs 8417  (-27.5%, 95% CI [-35.9%, -19.2%])
N=2   random - baseline            d = +4.2 pts   naive 95% CI [-3.3, +11.6]   cluster 95% CI [-3.3, +11.6]   deff 0.96   b/c 13/8   McNemar p = 0.383   clustered p = 0.274
                                   power: MDE(80%) 10.7 pts   power to detect 5 pts = 26%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -3.3 -> NON-INFERIOR   one-sided p = 0.00801
                                   tokens 10806 vs 17179  (-32.7%, 95% CI [-37.0%, -28.3%])
N=4   random - baseline            d = -0.8 pts   naive 95% CI [-5.8, +4.1]   cluster 95% CI [-6.3, +4.7]   deff 1.21   b/c 4/5   McNemar p = 1   clustered p = 0.767
                                   power: MDE(80%) 7.9 pts   power to detect 5 pts = 43%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -6.3 -> cannot claim parity   one-sided p = 0.0688
                                   tokens 22737 vs 34192  (-28.8%, 95% CI [-33.3%, -24.2%])
N=8   random - baseline            d = -6.7 pts   naive 95% CI [-14.6, +1.2]   cluster 95% CI [-14.4, +1.1]   deff 0.94   b/c 1/5   McNemar p = 0.219   clustered p = 0.0926
                                   power: MDE(80%) 11.1 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -14.4 -> cannot claim parity   one-sided p = 0.663
                                   tokens 44602 vs 67682  (-29.2%, 95% CI [-35.2%, -23.2%])
N=16  random - baseline            d = -3.3 pts   naive 95% CI [-20.9, +14.2]   cluster 95% CI [-20.9, +14.2]   deff 0.97   b/c 3/4   McNemar p = 1   clustered p = 0.71
                                   power: MDE(80%) 25.1 pts   power to detect 5 pts = 8%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -20.9 -> cannot claim parity   one-sided p = 0.426
                                   tokens 91581 vs 133659  (-26.8%, 95% CI [-31.8%, -21.8%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = +0.7 pts   naive 95% CI [-3.0, +4.3]   cluster 95% CI [-4.1, +5.4]   deff 1.61   b/c 37/34   McNemar p = 0.813   clustered p = 0.783
                                   power: MDE(80%) 6.8 pts   power to detect 5 pts = 54%
                                   equal-weight per N: d = +2.5 pts (from 5 cells: +0.8, -5.8, +2.5, +5.0, +10.0)

pooled rank - baseline (chunk-wtd) d = -0.4 pts   naive 95% CI [-3.5, +2.6]   cluster 95% CI [-5.0, +4.1]   deff 2.16   b/c 23/25   McNemar p = 0.885   clustered p = 0.847
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 58%
                                   equal-weight per N: d = +0.5 pts (from 5 cells: -2.5, -1.7, +1.7, -1.7, +6.7)

pooled tourney - baseline (chunk-wtd) d = -0.7 pts   naive 95% CI [-3.8, +2.4]   cluster 95% CI [-5.6, +4.2]   deff 2.40   b/c 24/27   McNemar p = 0.78   clustered p = 0.79
                                   power: MDE(80%) 7.0 pts   power to detect 5 pts = 51%
                                   equal-weight per N: d = -0.0 pts (from 5 cells: -3.3, +0.8, +0.8, -5.0, +6.7)

pooled random - baseline (chunk-wtd) d = -1.1 pts   naive 95% CI [-4.5, +2.3]   cluster 95% CI [-5.3, +3.1]   deff 1.48   b/c 28/33   McNemar p = 0.609   clustered p = 0.605
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 64%
                                   equal-weight per N: d = -2.0 pts (from 5 cells: -3.3, +4.2, -0.8, -6.7, -3.3)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = -2.5 pts   95% CI [-9.7, +4.7]   win/loss 5/5   p = 0.495   sign p = 1
                                   tokens 5829 vs 8417 (-30.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -9.7 -> cannot claim parity   one-sided p = 0.248
                                   WARNING: -31% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 10.3 pts   power to detect 5 pts = 28%   <- underpowered
rank N=2 vs baseline N=1           d = +6.7 pts   95% CI [-0.4, +13.7]   win/loss 9/2   p = 0.0628   sign p = 0.0654
                                   tokens 10144 vs 8417 (+20.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -0.4 -> NON-INFERIOR   one-sided p = 0.000564
                                   WARNING: +21% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 10.0 pts   power to detect 5 pts = 29%   <- underpowered
rank N=4 vs baseline N=2           d = +7.5 pts   95% CI [+1.7, +13.3]   win/loss 10/2   p = 0.0116   sign p = 0.0386
                                   tokens 20905 vs 17179 (+21.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +1.7 -> NON-INFERIOR   one-sided p = 1.3e-05
                                   WARNING: +22% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 8.3 pts   power to detect 5 pts = 39%   <- underpowered
rank N=8 vs baseline N=4           d = +0.8 pts   95% CI [-6.0, +7.7]   win/loss 3/2   p = 0.811   sign p = 1
                                   tokens 40696 vs 34192 (+19.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -6.0 -> cannot claim parity   one-sided p = 0.0474
                                   WARNING: +19% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 9.8 pts   power to detect 5 pts = 30%   <- underpowered
rank N=16 vs baseline N=8          d = +3.3 pts   95% CI [-8.1, +14.8]   win/loss 2/1   p = 0.568   sign p = 1
                                   tokens 78041 vs 67682 (+15.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -8.1 -> cannot claim parity   one-sided p = 0.0768
                                   WARNING: +15% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 16.4 pts   power to detect 5 pts = 13%   <- underpowered

random N=1 vs baseline N=1         d = -3.3 pts   95% CI [-9.0, +2.3]   win/loss 3/6   p = 0.245   sign p = 0.508
                                   tokens 5606 vs 8417 (-33.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -9.0 -> cannot claim parity   one-sided p = 0.281
                                   WARNING: -33% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 8.0 pts   power to detect 5 pts = 41%   <- underpowered
random N=2 vs baseline N=1         d = +12.5 pts   95% CI [+3.5, +21.5]   win/loss 10/2   p = 0.00662   sign p = 0.0386
                                   tokens 10806 vs 8417 (+28.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +3.5 -> NON-INFERIOR   one-sided p = 7.19e-05
                                   WARNING: +28% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 12.9 pts   power to detect 5 pts = 19%   <- underpowered
random N=4 vs baseline N=2         d = +5.0 pts   95% CI [-1.8, +11.8]   win/loss 6/3   p = 0.15   sign p = 0.508
                                   tokens 22737 vs 17179 (+32.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.8 -> NON-INFERIOR   one-sided p = 0.002
                                   WARNING: +32% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 9.7 pts   power to detect 5 pts = 30%   <- underpowered
random N=8 vs baseline N=4         d = -4.2 pts   95% CI [-13.0, +4.6]   win/loss 3/5   p = 0.354   sign p = 0.727
                                   tokens 44602 vs 34192 (+30.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -13.0 -> cannot claim parity   one-sided p = 0.427
                                   WARNING: +30% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 12.6 pts   power to detect 5 pts = 20%   <- underpowered
random N=16 vs baseline N=8        d = -6.7 pts   95% CI [-22.8, +9.4]   win/loss 2/4   p = 0.417   sign p = 0.688
                                   tokens 91581 vs 67682 (+35.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -22.8 -> cannot claim parity   one-sided p = 0.58
                                   WARNING: +35% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 23.0 pts   power to detect 5 pts = 9%   <- underpowered

tourney N=1 vs baseline N=1        d = -3.3 pts   95% CI [-10.3, +3.6]   win/loss 3/6   p = 0.347   sign p = 0.508
                                   tokens 5777 vs 8417 (-31.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -10.3 -> cannot claim parity   one-sided p = 0.319
                                   WARNING: -31% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 9.9 pts   power to detect 5 pts = 29%   <- underpowered
tourney N=2 vs baseline N=1        d = +9.2 pts   95% CI [+3.2, +15.1]   win/loss 8/0   p = 0.00267   sign p = 0.00781
                                   tokens 10228 vs 8417 (+21.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +3.2 -> NON-INFERIOR   one-sided p = 1.73e-06
                                   WARNING: +22% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 8.6 pts   power to detect 5 pts = 37%   <- underpowered
tourney N=4 vs baseline N=2        d = +6.7 pts   95% CI [-0.4, +13.7]   win/loss 7/2   p = 0.0628   sign p = 0.18
                                   tokens 20746 vs 17179 (+20.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -0.4 -> NON-INFERIOR   one-sided p = 0.000564
                                   WARNING: +21% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 10.0 pts   power to detect 5 pts = 29%   <- underpowered
tourney N=8 vs baseline N=4        d = -2.5 pts   95% CI [-15.0, +10.0]   win/loss 4/5   p = 0.695   sign p = 1
                                   tokens 41249 vs 34192 (+20.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -15.0 -> cannot claim parity   one-sided p = 0.348
                                   WARNING: +21% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 17.9 pts   power to detect 5 pts = 12%   <- underpowered
tourney N=16 vs baseline N=8       d = +3.3 pts   95% CI [-11.5, +18.1]   win/loss 3/2   p = 0.659   sign p = 1
                                   tokens 83158 vs 67682 (+22.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -11.5 -> cannot claim parity   one-sided p = 0.135
                                   WARNING: +23% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 21.2 pts   power to detect 5 pts = 10%   <- underpowered

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

============================================================================================================
8. CROSS-CONFIG SUMMARY   (the stable estimate: average over the grid)

   A single config is one noisy draw. Quoting the best cell overstates the
   effect because it is the maximum of many noisy cells. These are means.

   arm          N  configs  acc mean    min    max    tokens  vs base
   baseline     1        2     47.5%     48     48     8,417     0.0%
   rank         1        2     49.2%     48     51     5,893   -30.0%
   random       1        2     44.6%     42     47     5,779   -31.3%
   tourney      1        2     45.8%     45     47     5,750   -31.7%

   baseline     2        2     54.5%     55     55    17,179     0.0%
   rank         2        2     56.2%     56     57    10,662   -37.9%
   random       2        2     60.8%     59     62    11,108   -35.3%
   tourney      2        2     56.2%     53     59    10,719   -37.6%

   baseline     4        2     63.0%     63     63    34,192     0.0%
   rank         4        2     64.2%     62     66    21,211   -38.0%
   random       4        2     62.9%     62     63    22,736   -33.5%
   tourney      4        2     65.0%     65     65    21,106   -38.3%

   baseline     8        2     69.5%     70     70    67,682     0.0%
   rank         8        2     63.3%     62     65    41,313   -39.0%
   random       8        2     65.0%     60     70    44,147   -34.8%
   tourney      8        2     65.0%     62     68    42,382   -37.4%

   baseline    16        2     70.0%     70     70   133,659     0.0%
   rank        16        2     68.3%     67     70    80,240   -40.0%
   random      16        2     58.3%     57     60    90,293   -32.4%
   tourney     16        2     73.3%     70     77    83,513   -37.5%

   ORACLE CEILING COLLAPSE   (what pruning costs you before the judge acts)

   Pruning discards candidates, so a correct answer may never reach the judge.
   A smaller judge gap on a pruned arm is less headroom, not better selection.

   arm          N   ceiling  selected  judge gap  ceiling vs base
   baseline     1     47.5%     47.5%       0.0p             0.0p
   rank         1     49.2%     49.2%       0.0p             1.7p
   random       1     44.6%     44.6%       0.0p            -2.9p
   tourney      1     45.8%     45.8%       0.0p            -1.7p

   baseline     2     57.0%     54.5%       2.5p             0.0p
   rank         2     56.2%     56.2%       0.0p            -0.7p
   random       2     62.1%     60.8%       1.2p             5.1p
   tourney      2     57.1%     56.2%       0.8p             0.1p

   baseline     4     66.2%     63.0%       3.2p             0.0p
   rank         4     67.5%     64.2%       3.3p             1.3p
   random       4     67.1%     62.9%       4.2p             0.8p
   tourney      4     67.1%     65.0%       2.1p             0.8p

   baseline     8     73.5%     69.5%       4.0p             0.0p
   rank         8     70.0%     63.3%       6.7p            -3.5p
   random       8     70.8%     65.0%       5.8p            -2.7p
   tourney      8     73.3%     65.0%       8.3p            -0.2p

   baseline    16     79.0%     70.0%       9.0p             0.0p
   rank        16     78.3%     68.3%      10.0p            -0.7p
   random      16     75.0%     58.3%      16.7p            -4.0p
   tourney     16     80.0%     73.3%       6.7p             1.0p


============================================================================================================
9. ISO-TOKEN CONTRASTS   (baseline curve INTERPOLATED to each cell's actual spend)

   Section 6 snaps each cell to the nearest baseline N, leaving budget gaps up to
   +49%. Here the baseline accuracy-vs-token curve is log-interpolated to the exact
   budget each cell spent, so there is no mismatch left to warn about.

   baseline stop-tail correction: 26.25% of generated tokens
   fall after the first </answer>, which the baseline is charged for and the arms
   are not (no stop string on the baseline; stop=['</answer>'] on the arms).

      N  baseline acc   tokens raw  tokens corrected
      1         47.5%        8,417             6,253
      2         54.5%       17,179            12,849
      4         63.0%       34,192            25,532
      8         69.5%       67,682            50,363
     16         70.0%      133,659            99,021

   RAW baseline: arm accuracy minus interpolated baseline accuracy
     over 30 equal-N cells:  mean +1.97 pts   median +3.03 pts   positive 19/30   (negative 10, exact ties 1)
       plan=1000  mean +1.73 pts   (15 cells)
       plan=2500  mean +2.21 pts   (15 cells)

   STOP-CORRECTED baseline: arm accuracy minus interpolated baseline accuracy
     over 30 equal-N cells:  mean +0.07 pts   median +0.20 pts   positive 18/30   (negative 11, exact ties 1)
       plan=1000  mean -0.16 pts   (15 cells)
       plan=2500  mean +0.31 pts   (15 cells)

   Read together: against the raw baseline the pruned arms are roughly break-even at
   equal budget; against the stop-corrected baseline they are negative at every plan
   level. The apparent iso-token parity depends on charging the baseline for tokens
   the arms never emit.

============================================================================================================
7. MULTIPLE COMPARISONS   (corrected WITHIN each hypothesis family)

   Families are corrected separately. Pooling them would let the enormous
   judge-vs-random effects (p ~ 1e-9) inflate m and consume the alpha that
   the borderline arm contrasts actually need.

   family              tests  p<.05  by chance   Holm    BH
   arm-contrast           40      2          2      0     0
   judge-vs-random        28     24          1     14    20
   non-inferiority        70     32          4      9    21
   pooled                  8      0          0      0     0
   token-matched          30      5          2      0     0

   22 nominally-significant results do NOT survive BH within their family.
   Do not cite these on their own:
     p=0.00267   [token-matched] plan=2500,prune=2.0  tourney N=2 vs baseline N=1
     p=0.00662   [token-matched] plan=2500,prune=2.0  random N=2 vs baseline N=1
     p=0.0116    [token-matched] plan=2500,prune=2.0  rank N=4 vs baseline N=2
     p=0.0158    [non-inferiority] plan=1000,prune=2.0  [NI] random N=8 vs baseline N=4
     p=0.0173    [non-inferiority] plan=2500,prune=2.0  [NI] N=4   rank - baseline
     p=0.0229    [arm-contrast] plan=1000,prune=2.0  N=1   rank - random
     p=0.0283    [non-inferiority] plan=1000,prune=2.0  [NI] tourney N=8 vs baseline N=4
     p=0.0303    [non-inferiority] plan=1000,prune=2.0  [NI] tourney N=2 vs baseline N=1
     p=0.0347    [token-matched] plan=1000,prune=2.0  tourney N=4 vs baseline N=2
     p=0.0347    [arm-contrast] plan=1000,prune=2.0  N=16  tourney - baseline
     p=0.0373    [token-matched] plan=1000,prune=2.0  random N=2 vs baseline N=1
     p=0.0376    [non-inferiority] plan=2500,prune=2.0  [NI] N=4   tourney - baseline
     p=0.0398    [non-inferiority] plan=1000,prune=2.0  [NI] N=8   random - baseline
     p=0.0401    [non-inferiority] plan=2500,prune=2.0  [NI] N=16  tourney - baseline
     p=0.0437    [non-inferiority] plan=1000,prune=2.0  [NI] N=16  rank - random
     p=0.0437    [non-inferiority] plan=2500,prune=2.0  [NI] N=16  rank - random
     p=0.0443    [non-inferiority] plan=1000,prune=2.0  [NI] N=4   rank - random
     p=0.0467    [judge-vs-random] plan=2500,prune=2.0  rank N=8: judge - random
     p=0.0474    [non-inferiority] plan=2500,prune=2.0  [NI] rank N=8 vs baseline N=4
     p=0.0477    [judge-vs-random] plan=1000,prune=2.0  tourney N=2: judge - random
     ... and 2 more

   23 results survive the strict Holm correction; these are the safe ones to quote.
```

## Full grid — bok (best-of-k diverse)
```

############################################################################################################
# CONFIG  plan=1000  prune=2.0
############################################################################################################
============================================================================================================
FILES
  baseline  2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json
  random    2026-07-24_11-27-51_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_2.0_diverse.json
  rank      2026-07-24_11-27-38_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_2.0_diverse.json
  tourney   2026-07-24_11-28-04_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_2.0_diverse.json
  N values: [1, 2, 4, 8, 16]
  questions: baseline=100, random=30, rank=30, tourney=30
  NOTE: arms differ in question count -- paired contrasts use the 30 shared questions. Section 1 accuracies are each arm's own mean over its own questions, so the baseline row there is NOT restricted to the overlap and will not equal the contrasts.

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16
baseline      47.5%   8417t    54.5%  17179t    63.0%  34192t    69.5%  67682t    70.0% 133659t
rank          50.0%   5945t    56.7%  11382t    65.0%  22365t    65.0%  43656t    70.0%  83520t
random        44.2%   5928t    54.2%  11450t    60.8%  22805t    65.0%  45285t    63.3%  87638t
tourney       45.8%   5724t    55.0%  11306t    62.5%  22001t    63.3%  43921t    66.7%  86090t

============================================================================================================
2. JUDGE vs RANDOM PICK, WITHIN THE SAME POOL   (does selection beat chance?)

baseline N=1: judge - random       d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
baseline N=2: judge - random       d = +7.2 pts   naive 95% CI [+4.2, +10.3]   cluster 95% CI [+3.9, +10.6]   deff 1.19   b/c 35/6   McNemar p = 4.87e-06   clustered p = 2.36e-05
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 83%
baseline N=4: judge - random       d = +14.2 pts   naive 95% CI [+10.4, +18.1]   cluster 95% CI [+9.8, +18.7]   deff 1.32   b/c 63/6   McNemar p = 4.47e-13   clustered p = 2.6e-10
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 60%
baseline N=8: judge - random       d = +21.0 pts   naive 95% CI [+15.0, +27.0]   cluster 95% CI [+14.2, +27.8]   deff 1.29   b/c 44/2   McNemar p = 3.08e-11   clustered p = 1.86e-09
                                   power: MDE(80%) 9.8 pts   power to detect 5 pts = 30%   <- underpowered; a null here is NOT evidence of no effect
baseline N=16: judge - random      d = +25.0 pts   naive 95% CI [+14.8, +35.2]   cluster 95% CI [+14.8, +35.2]   deff 0.99   b/c 29/4   McNemar p = 1.09e-05   clustered p = 1.51e-06
                                   power: MDE(80%) 14.6 pts   power to detect 5 pts = 16%   <- underpowered; a null here is NOT evidence of no effect

rank N=1: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=2: judge - random           d = +3.3 pts   naive 95% CI [-1.3, +7.9]   cluster 95% CI [-1.8, +8.4]   deff 1.19   b/c 6/2   McNemar p = 0.289   clustered p = 0.201
                                   power: MDE(80%) 7.3 pts   power to detect 5 pts = 48%   <- underpowered; a null here is NOT evidence of no effect
rank N=4: judge - random           d = +12.5 pts   naive 95% CI [+6.1, +18.9]   cluster 95% CI [+5.2, +19.8]   deff 1.28   b/c 16/1   McNemar p = 0.000275   clustered p = 0.000839
                                   power: MDE(80%) 10.5 pts   power to detect 5 pts = 27%   <- underpowered; a null here is NOT evidence of no effect
rank N=8: judge - random           d = +18.3 pts   naive 95% CI [+7.4, +29.3]   cluster 95% CI [+5.5, +31.2]   deff 1.34   b/c 12/1   McNemar p = 0.00342   clustered p = 0.00518
                                   power: MDE(80%) 18.4 pts   power to detect 5 pts = 12%   <- underpowered; a null here is NOT evidence of no effect
rank N=16: judge - random          d = +13.3 pts   naive 95% CI [-2.2, +28.9]   cluster 95% CI [-2.2, +28.9]   deff 0.97   b/c 5/1   McNemar p = 0.219   clustered p = 0.0926
                                   power: MDE(80%) 22.2 pts   power to detect 5 pts = 9%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +7.5 pts   naive 95% CI [+2.8, +12.2]   cluster 95% CI [+2.2, +12.8]   deff 1.23   b/c 9/0   McNemar p = 0.00391   clustered p = 0.00583
                                   power: MDE(80%) 7.6 pts   power to detect 5 pts = 45%   <- underpowered; a null here is NOT evidence of no effect
random N=4: judge - random         d = +12.5 pts   naive 95% CI [+6.1, +18.9]   cluster 95% CI [+5.6, +19.4]   deff 1.15   b/c 16/1   McNemar p = 0.000275   clustered p = 0.000423
                                   power: MDE(80%) 9.9 pts   power to detect 5 pts = 29%   <- underpowered; a null here is NOT evidence of no effect
random N=8: judge - random         d = +16.7 pts   naive 95% CI [+6.1, +27.3]   cluster 95% CI [+8.1, +25.2]   deff 0.63   b/c 11/1   McNemar p = 0.00635   clustered p = 0.00014
                                   power: MDE(80%) 12.3 pts   power to detect 5 pts = 21%   <- underpowered; a null here is NOT evidence of no effect
random N=16: judge - random        d = +16.7 pts   naive 95% CI [-4.5, +37.9]   cluster 95% CI [-4.5, +37.9]   deff 0.97   b/c 8/3   McNemar p = 0.227   clustered p = 0.123
                                   power: MDE(80%) 30.3 pts   power to detect 5 pts = 7%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +6.7 pts   naive 95% CI [+1.6, +11.7]   cluster 95% CI [+1.4, +11.9]   deff 1.03   b/c 9/1   McNemar p = 0.0215   clustered p = 0.0123
                                   power: MDE(80%) 7.5 pts   power to detect 5 pts = 47%   <- underpowered; a null here is NOT evidence of no effect
tourney N=4: judge - random        d = +11.7 pts   naive 95% CI [+5.4, +17.9]   cluster 95% CI [+4.3, +19.0]   deff 1.34   b/c 15/1   McNemar p = 0.000519   clustered p = 0.00181
                                   power: MDE(80%) 10.5 pts   power to detect 5 pts = 27%   <- underpowered; a null here is NOT evidence of no effect
tourney N=8: judge - random        d = +5.0 pts   naive 95% CI [-4.8, +14.8]   cluster 95% CI [-4.8, +14.8]   deff 0.97   b/c 6/3   McNemar p = 0.508   clustered p = 0.317
                                   power: MDE(80%) 14.0 pts   power to detect 5 pts = 17%   <- underpowered; a null here is NOT evidence of no effect
tourney N=16: judge - random       d = +10.0 pts   naive 95% CI [-7.2, +27.2]   cluster 95% CI [-7.2, +27.2]   deff 0.97   b/c 5/2   McNemar p = 0.453   clustered p = 0.254
                                   power: MDE(80%) 24.6 pts   power to detect 5 pts = 8%   <- underpowered; a null here is NOT evidence of no effect

============================================================================================================
3. ORACLE CEILING   (a correct candidate EXISTS vs the judge FINDS it)
   NOTE: for pruned arms this is pass@k over SURVIVORS, not over all N.
   Only the baseline row is a clean best-of-N ceiling.

baseline   N=1   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
baseline   N=2   ceiling  57.0%   selected  54.5%   gap  2.5 pts   capture  95.6%
baseline   N=4   ceiling  66.2%   selected  63.0%   gap  3.2 pts   capture  95.1%
baseline   N=8   ceiling  73.5%   selected  69.5%   gap  4.0 pts   capture  94.6%
baseline   N=16  ceiling  79.0%   selected  70.0%   gap  9.0 pts   capture  88.6%

rank       N=1   ceiling  50.0%   selected  50.0%   gap  0.0 pts   capture 100.0%
rank       N=2   ceiling  59.2%   selected  56.7%   gap  2.5 pts   capture  95.8%
rank       N=4   ceiling  66.7%   selected  65.0%   gap  1.7 pts   capture  97.5%
rank       N=8   ceiling  70.0%   selected  65.0%   gap  5.0 pts   capture  92.9%
rank       N=16  ceiling  80.0%   selected  70.0%   gap 10.0 pts   capture  87.5%

random     N=1   ceiling  44.2%   selected  44.2%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  54.2%   selected  54.2%   gap  0.0 pts   capture 100.0%
random     N=4   ceiling  61.7%   selected  60.8%   gap  0.8 pts   capture  98.6%
random     N=8   ceiling  68.3%   selected  65.0%   gap  3.3 pts   capture  95.1%
random     N=16  ceiling  73.3%   selected  63.3%   gap 10.0 pts   capture  86.4%

tourney    N=1   ceiling  45.8%   selected  45.8%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  56.7%   selected  55.0%   gap  1.7 pts   capture  97.1%
tourney    N=4   ceiling  65.8%   selected  62.5%   gap  3.3 pts   capture  94.9%
tourney    N=8   ceiling  68.3%   selected  63.3%   gap  5.0 pts   capture  92.7%
tourney    N=16  ceiling  73.3%   selected  66.7%   gap  6.7 pts   capture  90.9%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = +5.8 pts   naive 95% CI [-1.6, +13.3]   cluster 95% CI [-2.5, +14.2]   deff 1.22   b/c 14/7   McNemar p = 0.189   clustered p = 0.172
                                   power: MDE(80%) 12.0 pts   power to detect 5 pts = 22%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -2.5 -> NON-INFERIOR   one-sided p = 0.00558
                                   tokens 5945 vs 5928  (+0.3%, 95% CI [-8.7%, +9.2%])
N=2   rank - random                d = +2.5 pts   naive 95% CI [-5.4, +10.4]   cluster 95% CI [-4.3, +9.3]   deff 0.72   b/c 13/10   McNemar p = 0.678   clustered p = 0.47
                                   power: MDE(80%) 9.7 pts   power to detect 5 pts = 30%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -4.3 -> NON-INFERIOR   one-sided p = 0.0152
                                   tokens 11382 vs 11450  (-0.6%, 95% CI [-6.4%, +5.2%])
N=4   rank - random                d = +4.2 pts   naive 95% CI [-1.2, +9.6]   cluster 95% CI [+0.8, +7.6]   deff 0.38   b/c 8/3   McNemar p = 0.227   clustered p = 0.016
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 82%
                                   non-inferiority (margin 5 pts): lower bound +0.8 -> NON-INFERIOR   one-sided p = 5.84e-08
                                   tokens 22365 vs 22805  (-1.9%, 95% CI [-6.5%, +2.6%])
N=8   rank - random                d = +0.0 pts   naive 95% CI [-8.1, +8.1]   cluster 95% CI [-8.1, +8.1]   deff 0.98   b/c 3/3   McNemar p = 1   clustered p = 1
                                   power: MDE(80%) 11.6 pts   power to detect 5 pts = 22%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -8.1 -> cannot claim parity   one-sided p = 0.114
                                   tokens 43656 vs 45285  (-3.6%, 95% CI [-8.5%, +1.3%])
N=16  rank - random                d = +6.7 pts   naive 95% CI [-9.4, +22.8]   cluster 95% CI [-9.4, +22.8]   deff 0.97   b/c 4/2   McNemar p = 0.688   clustered p = 0.417
                                   power: MDE(80%) 23.0 pts   power to detect 5 pts = 9%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -9.4 -> cannot claim parity   one-sided p = 0.0777
                                   tokens 83520 vs 87638  (-4.7%, 95% CI [-11.5%, +2.1%])

N=1   rank - baseline              d = +0.0 pts   naive 95% CI [-8.0, +8.0]   cluster 95% CI [-7.8, +7.8]   deff 0.91   b/c 12/12   McNemar p = 1   clustered p = 1
                                   power: MDE(80%) 11.1 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -7.8 -> cannot claim parity   one-sided p = 0.104
                                   tokens 5945 vs 8417  (-23.1%, 95% CI [-30.6%, -15.7%])
N=2   rank - baseline              d = -1.7 pts   naive 95% CI [-9.0, +5.7]   cluster 95% CI [-8.7, +5.4]   deff 0.89   b/c 9/11   McNemar p = 0.824   clustered p = 0.642
                                   power: MDE(80%) 10.0 pts   power to detect 5 pts = 29%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -8.7 -> cannot claim parity   one-sided p = 0.176
                                   tokens 11382 vs 17179  (-29.1%, 95% CI [-36.6%, -21.5%])
N=4   rank - baseline              d = +0.8 pts   naive 95% CI [-4.1, +5.8]   cluster 95% CI [-5.1, +6.8]   deff 1.43   b/c 5/4   McNemar p = 1   clustered p = 0.785
                                   power: MDE(80%) 8.6 pts   power to detect 5 pts = 37%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -5.1 -> cannot claim parity   one-sided p = 0.028
                                   tokens 22365 vs 34192  (-29.9%, 95% CI [-35.1%, -24.7%])
N=8   rank - baseline              d = -1.7 pts   naive 95% CI [-9.0, +5.7]   cluster 95% CI [-10.4, +7.1]   deff 1.37   b/c 2/3   McNemar p = 1   clustered p = 0.71
                                   power: MDE(80%) 12.5 pts   power to detect 5 pts = 20%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -10.4 -> cannot claim parity   one-sided p = 0.228
                                   tokens 43656 vs 67682  (-30.7%, 95% CI [-37.5%, -23.9%])
N=16  rank - baseline              d = +6.7 pts   naive 95% CI [-2.4, +15.7]   cluster 95% CI [-2.4, +15.7]   deff 0.97   b/c 2/0   McNemar p = 0.5   clustered p = 0.15
                                   power: MDE(80%) 13.0 pts   power to detect 5 pts = 19%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -2.4 -> NON-INFERIOR   one-sided p = 0.00589
                                   tokens 83520 vs 133659  (-33.3%, 95% CI [-39.5%, -27.0%])

N=1   tourney - baseline           d = -4.2 pts   naive 95% CI [-11.6, +3.3]   cluster 95% CI [-10.8, +2.5]   deff 0.77   b/c 8/13   McNemar p = 0.383   clustered p = 0.221
                                   power: MDE(80%) 9.5 pts   power to detect 5 pts = 31%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -10.8 -> cannot claim parity   one-sided p = 0.403
                                   tokens 5724 vs 8417  (-26.0%, 95% CI [-34.3%, -17.7%])
N=2   tourney - baseline           d = -3.3 pts   naive 95% CI [-9.4, +2.8]   cluster 95% CI [-7.9, +1.2]   deff 0.53   b/c 5/9   McNemar p = 0.424   clustered p = 0.15
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 58%
                                   non-inferiority (margin 5 pts): lower bound -7.9 -> cannot claim parity   one-sided p = 0.236
                                   tokens 11306 vs 17179  (-29.5%, 95% CI [-36.0%, -23.1%])
N=4   tourney - baseline           d = -1.7 pts   naive 95% CI [-6.3, +3.0]   cluster 95% CI [-6.3, +3.0]   deff 0.98   b/c 3/5   McNemar p = 0.727   clustered p = 0.483
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 56%
                                   non-inferiority (margin 5 pts): lower bound -6.3 -> cannot claim parity   one-sided p = 0.0804
                                   tokens 22001 vs 34192  (-31.1%, 95% CI [-36.8%, -25.3%])
N=8   tourney - baseline           d = -3.3 pts   naive 95% CI [-9.9, +3.2]   cluster 95% CI [-9.9, +3.2]   deff 0.97   b/c 1/3   McNemar p = 0.625   clustered p = 0.317
                                   power: MDE(80%) 9.3 pts   power to detect 5 pts = 32%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -9.9 -> cannot claim parity   one-sided p = 0.309
                                   tokens 43921 vs 67682  (-30.3%, 95% CI [-35.6%, -25.0%])
N=16  tourney - baseline           d = +3.3 pts   naive 95% CI [-8.1, +14.8]   cluster 95% CI [-8.1, +14.8]   deff 0.97   b/c 2/1   McNemar p = 1   clustered p = 0.568
                                   power: MDE(80%) 16.4 pts   power to detect 5 pts = 13%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -8.1 -> cannot claim parity   one-sided p = 0.0768
                                   tokens 86090 vs 133659  (-31.2%, 95% CI [-36.9%, -25.5%])

N=1   random - baseline            d = -5.8 pts   naive 95% CI [-13.3, +1.6]   cluster 95% CI [-14.2, +2.5]   deff 1.22   b/c 7/14   McNemar p = 0.189   clustered p = 0.172
                                   power: MDE(80%) 12.0 pts   power to detect 5 pts = 22%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -14.2 -> cannot claim parity   one-sided p = 0.577
                                   tokens 5928 vs 8417  (-23.4%, 95% CI [-32.8%, -14.0%])
N=2   random - baseline            d = -4.2 pts   naive 95% CI [-12.3, +4.0]   cluster 95% CI [-12.7, +4.3]   deff 1.05   b/c 10/15   McNemar p = 0.424   clustered p = 0.337
                                   power: MDE(80%) 12.1 pts   power to detect 5 pts = 21%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -12.7 -> cannot claim parity   one-sided p = 0.424
                                   tokens 11450 vs 17179  (-28.7%, 95% CI [-36.9%, -20.4%])
N=4   random - baseline            d = -3.3 pts   naive 95% CI [-8.5, +1.8]   cluster 95% CI [-9.0, +2.3]   deff 1.15   b/c 3/7   McNemar p = 0.344   clustered p = 0.245
                                   power: MDE(80%) 8.0 pts   power to detect 5 pts = 41%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -9.0 -> cannot claim parity   one-sided p = 0.281
                                   tokens 22805 vs 34192  (-28.5%, 95% CI [-34.1%, -22.9%])
N=8   random - baseline            d = -1.7 pts   naive 95% CI [-7.4, +4.0]   cluster 95% CI [-7.4, +4.1]   deff 0.98   b/c 1/2   McNemar p = 1   clustered p = 0.568
                                   power: MDE(80%) 8.2 pts   power to detect 5 pts = 40%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -7.4 -> cannot claim parity   one-sided p = 0.127
                                   tokens 45285 vs 67682  (-28.1%, 95% CI [-34.1%, -22.2%])
N=16  random - baseline            d = +0.0 pts   naive 95% CI [-13.3, +13.3]   cluster 95% CI [-13.3, +13.3]   deff 0.97   b/c 2/2   McNemar p = 1   clustered p = 1
                                   power: MDE(80%) 19.0 pts   power to detect 5 pts = 11%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -13.3 -> cannot claim parity   one-sided p = 0.23
                                   tokens 87638 vs 133659  (-30.0%, 95% CI [-35.2%, -24.7%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = +3.8 pts   naive 95% CI [+0.2, +7.3]   cluster 95% CI [+0.9, +6.7]   deff 0.65   b/c 42/25   McNemar p = 0.0498   clustered p = 0.0111
                                   power: MDE(80%) 4.2 pts   power to detect 5 pts = 92%
                                   equal-weight per N: d = +3.8 pts (from 5 cells: +5.8, +2.5, +4.2, +0.0, +6.7)

pooled rank - baseline (chunk-wtd) d = +0.0 pts   naive 95% CI [-3.4, +3.4]   cluster 95% CI [-4.2, +4.2]   deff 1.46   b/c 30/30   McNemar p = 1   clustered p = 1
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 65%
                                   equal-weight per N: d = +0.8 pts (from 5 cells: +0.0, -1.7, +0.8, -1.7, +6.7)

pooled tourney - baseline (chunk-wtd) d = -2.7 pts   naive 95% CI [-5.7, +0.4]   cluster 95% CI [-6.3, +1.0]   deff 1.35   b/c 19/31   McNemar p = 0.119   clustered p = 0.15
                                   power: MDE(80%) 5.2 pts   power to detect 5 pts = 77%
                                   equal-weight per N: d = -1.8 pts (from 5 cells: -4.2, -3.3, -1.7, -3.3, +3.3)

pooled random - baseline (chunk-wtd) d = -3.8 pts   naive 95% CI [-7.2, -0.3]   cluster 95% CI [-8.1, +0.5]   deff 1.49   b/c 23/40   McNemar p = 0.043   clustered p = 0.0837
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
                                   equal-weight per N: d = -3.0 pts (from 5 cells: -5.8, -4.2, -3.3, -1.7, +0.0)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = +0.0 pts   95% CI [-7.8, +7.8]   win/loss 7/4   p = 1   sign p = 0.549
                                   tokens 5945 vs 8417 (-29.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -7.8 -> cannot claim parity   one-sided p = 0.104
                                   WARNING: -29% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 11.1 pts   power to detect 5 pts = 24%   <- underpowered
rank N=2 vs baseline N=1           d = +6.7 pts   95% CI [-1.1, +14.4]   win/loss 10/5   p = 0.0926   sign p = 0.302
                                   tokens 11382 vs 8417 (+35.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.1 -> NON-INFERIOR   one-sided p = 0.00162
                                   WARNING: +35% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 11.1 pts   power to detect 5 pts = 24%   <- underpowered
rank N=4 vs baseline N=2           d = +6.7 pts   95% CI [+0.9, +12.4]   win/loss 5/0   p = 0.0224   sign p = 0.0625
                                   tokens 22365 vs 17179 (+30.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.9 -> NON-INFERIOR   one-sided p = 3.22e-05
                                   WARNING: +30% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 8.2 pts   power to detect 5 pts = 40%   <- underpowered
rank N=8 vs baseline N=4           d = +0.8 pts   95% CI [-7.5, +9.1]   win/loss 2/2   p = 0.844   sign p = 1
                                   tokens 43656 vs 34192 (+27.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -7.5 -> cannot claim parity   one-sided p = 0.0842
                                   WARNING: +28% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 11.9 pts   power to detect 5 pts = 22%   <- underpowered
rank N=16 vs baseline N=8          d = +3.3 pts   95% CI [-8.1, +14.8]   win/loss 2/1   p = 0.568   sign p = 1
                                   tokens 83520 vs 67682 (+23.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -8.1 -> cannot claim parity   one-sided p = 0.0768
                                   WARNING: +23% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 16.4 pts   power to detect 5 pts = 13%   <- underpowered

random N=1 vs baseline N=1         d = -5.8 pts   95% CI [-14.2, +2.5]   win/loss 5/8   p = 0.172   sign p = 0.581
                                   tokens 5928 vs 8417 (-29.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -14.2 -> cannot claim parity   one-sided p = 0.577
                                   WARNING: -30% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 12.0 pts   power to detect 5 pts = 22%   <- underpowered
random N=2 vs baseline N=1         d = +4.2 pts   95% CI [-4.6, +13.0]   win/loss 9/4   p = 0.354   sign p = 0.267
                                   tokens 11450 vs 8417 (+36.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.6 -> NON-INFERIOR   one-sided p = 0.0208
                                   WARNING: +36% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 12.6 pts   power to detect 5 pts = 20%   <- underpowered
random N=4 vs baseline N=2         d = +2.5 pts   95% CI [-1.1, +6.1]   win/loss 4/1   p = 0.174   sign p = 0.375
                                   tokens 22805 vs 17179 (+32.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.1 -> NON-INFERIOR   one-sided p = 2.24e-05
                                   WARNING: +33% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.1 pts   power to detect 5 pts = 78%
random N=8 vs baseline N=4         d = +0.8 pts   95% CI [-6.0, +7.7]   win/loss 3/2   p = 0.811   sign p = 1
                                   tokens 45285 vs 34192 (+32.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -6.0 -> cannot claim parity   one-sided p = 0.0474
                                   WARNING: +32% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 9.8 pts   power to detect 5 pts = 30%   <- underpowered
random N=16 vs baseline N=8        d = -3.3 pts   95% CI [-18.1, +11.5]   win/loss 2/3   p = 0.659   sign p = 1
                                   tokens 87638 vs 67682 (+29.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -18.1 -> cannot claim parity   one-sided p = 0.413
                                   WARNING: +29% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 21.2 pts   power to detect 5 pts = 10%   <- underpowered

tourney N=1 vs baseline N=1        d = -4.2 pts   95% CI [-10.8, +2.5]   win/loss 4/7   p = 0.221   sign p = 0.549
                                   tokens 5724 vs 8417 (-32.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -10.8 -> cannot claim parity   one-sided p = 0.403
                                   WARNING: -32% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 9.5 pts   power to detect 5 pts = 31%   <- underpowered
tourney N=2 vs baseline N=1        d = +5.0 pts   95% CI [+0.1, +9.9]   win/loss 8/2   p = 0.0467   sign p = 0.109
                                   tokens 11306 vs 8417 (+34.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.1 -> NON-INFERIOR   one-sided p = 3.49e-05
                                   WARNING: +34% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 7.0 pts   power to detect 5 pts = 51%
tourney N=4 vs baseline N=2        d = +4.2 pts   95% CI [-2.1, +10.4]   win/loss 8/4   p = 0.192   sign p = 0.388
                                   tokens 22001 vs 17179 (+28.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.1 -> NON-INFERIOR   one-sided p = 0.00203
                                   WARNING: +28% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 8.9 pts   power to detect 5 pts = 35%   <- underpowered
tourney N=8 vs baseline N=4        d = -0.8 pts   95% CI [-8.4, +6.8]   win/loss 3/3   p = 0.83   sign p = 1
                                   tokens 43921 vs 34192 (+28.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -8.4 -> cannot claim parity   one-sided p = 0.142
                                   WARNING: +28% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 10.9 pts   power to detect 5 pts = 25%   <- underpowered
tourney N=16 vs baseline N=8       d = +0.0 pts   95% CI [-13.3, +13.3]   win/loss 2/2   p = 1   sign p = 1
                                   tokens 86090 vs 67682 (+27.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -13.3 -> cannot claim parity   one-sided p = 0.23
                                   WARNING: +27% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 19.0 pts   power to detect 5 pts = 11%   <- underpowered

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

############################################################################################################
# CONFIG  plan=2500  prune=2.0
############################################################################################################
============================================================================================================
FILES
  baseline  2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json
  random    2026-07-24_09-22-05_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_2.0_diverse.json
  rank      2026-07-24_09-21-52_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_2.0_diverse.json
  tourney   2026-07-24_09-22-18_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_2.0_diverse.json
  N values: [1, 2, 4, 8, 16]
  questions: baseline=100, random=30, rank=30, tourney=30
  NOTE: arms differ in question count -- paired contrasts use the 30 shared questions. Section 1 accuracies are each arm's own mean over its own questions, so the baseline row there is NOT restricted to the overlap and will not equal the contrasts.

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16
baseline      47.5%   8417t    54.5%  17179t    63.0%  34192t    69.5%  67682t    70.0% 133659t
rank          49.2%   5919t    60.0%  10168t    67.5%  21829t    65.0%  41880t    76.7%  78873t
random        42.5%   5553t    54.2%  11114t    59.2%  22967t    61.7%  44713t    73.3%  87553t
tourney       44.2%   5820t    57.5%  10274t    63.3%  22008t    68.3%  41692t    73.3%  82798t

============================================================================================================
2. JUDGE vs RANDOM PICK, WITHIN THE SAME POOL   (does selection beat chance?)

baseline N=1: judge - random       d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
baseline N=2: judge - random       d = +7.2 pts   naive 95% CI [+4.2, +10.3]   cluster 95% CI [+3.9, +10.6]   deff 1.19   b/c 35/6   McNemar p = 4.87e-06   clustered p = 2.36e-05
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 83%
baseline N=4: judge - random       d = +14.2 pts   naive 95% CI [+10.4, +18.1]   cluster 95% CI [+9.8, +18.7]   deff 1.32   b/c 63/6   McNemar p = 4.47e-13   clustered p = 2.6e-10
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 60%
baseline N=8: judge - random       d = +21.0 pts   naive 95% CI [+15.0, +27.0]   cluster 95% CI [+14.2, +27.8]   deff 1.29   b/c 44/2   McNemar p = 3.08e-11   clustered p = 1.86e-09
                                   power: MDE(80%) 9.8 pts   power to detect 5 pts = 30%   <- underpowered; a null here is NOT evidence of no effect
baseline N=16: judge - random      d = +25.0 pts   naive 95% CI [+14.8, +35.2]   cluster 95% CI [+14.8, +35.2]   deff 0.99   b/c 29/4   McNemar p = 1.09e-05   clustered p = 1.51e-06
                                   power: MDE(80%) 14.6 pts   power to detect 5 pts = 16%   <- underpowered; a null here is NOT evidence of no effect

rank N=1: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=2: judge - random           d = +4.2 pts   naive 95% CI [+0.6, +7.8]   cluster 95% CI [+0.8, +7.6]   deff 0.86   b/c 5/0   McNemar p = 0.0625   clustered p = 0.016
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 82%
rank N=4: judge - random           d = +11.7 pts   naive 95% CI [+4.3, +19.1]   cluster 95% CI [+3.3, +20.0]   deff 1.24   b/c 18/4   McNemar p = 0.00434   clustered p = 0.00638
                                   power: MDE(80%) 12.0 pts   power to detect 5 pts = 21%   <- underpowered; a null here is NOT evidence of no effect
rank N=8: judge - random           d = +20.0 pts   naive 95% CI [+9.8, +30.2]   cluster 95% CI [+7.9, +32.1]   deff 1.35   b/c 12/0   McNemar p = 0.000488   clustered p = 0.00116
                                   power: MDE(80%) 17.3 pts   power to detect 5 pts = 13%   <- underpowered; a null here is NOT evidence of no effect
rank N=16: judge - random          d = +20.0 pts   naive 95% CI [+5.4, +34.6]   cluster 95% CI [+5.4, +34.6]   deff 0.97   b/c 6/0   McNemar p = 0.0312   clustered p = 0.00709
                                   power: MDE(80%) 20.8 pts   power to detect 5 pts = 10%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +5.0 pts   naive 95% CI [+0.4, +9.6]   cluster 95% CI [+0.7, +9.3]   deff 0.88   b/c 7/1   McNemar p = 0.0703   clustered p = 0.0237
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
random N=4: judge - random         d = +10.0 pts   naive 95% CI [+4.6, +15.4]   cluster 95% CI [+3.5, +16.5]   deff 1.40   b/c 12/0   McNemar p = 0.000488   clustered p = 0.00248
                                   power: MDE(80%) 9.3 pts   power to detect 5 pts = 33%   <- underpowered; a null here is NOT evidence of no effect
random N=8: judge - random         d = +20.0 pts   naive 95% CI [+7.9, +32.1]   cluster 95% CI [+5.4, +34.6]   deff 1.39   b/c 14/2   McNemar p = 0.00418   clustered p = 0.00709
                                   power: MDE(80%) 20.8 pts   power to detect 5 pts = 10%   <- underpowered; a null here is NOT evidence of no effect
random N=16: judge - random        d = +20.0 pts   naive 95% CI [+5.4, +34.6]   cluster 95% CI [+5.4, +34.6]   deff 0.97   b/c 6/0   McNemar p = 0.0312   clustered p = 0.00709
                                   power: MDE(80%) 20.8 pts   power to detect 5 pts = 10%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +2.5 pts   naive 95% CI [-0.3, +5.3]   cluster 95% CI [-0.2, +5.2]   deff 0.92   b/c 3/0   McNemar p = 0.25   clustered p = 0.0726
                                   power: MDE(80%) 3.9 pts   power to detect 5 pts = 95%
tourney N=4: judge - random        d = +10.8 pts   naive 95% CI [+4.0, +17.7]   cluster 95% CI [+3.5, +18.1]   deff 1.09   b/c 16/3   McNemar p = 0.00443   clustered p = 0.00368
                                   power: MDE(80%) 10.4 pts   power to detect 5 pts = 27%   <- underpowered; a null here is NOT evidence of no effect
tourney N=8: judge - random        d = +11.7 pts   naive 95% CI [+3.5, +19.9]   cluster 95% CI [+4.0, +19.4]   deff 0.85   b/c 7/0   McNemar p = 0.0156   clustered p = 0.00297
                                   power: MDE(80%) 11.0 pts   power to detect 5 pts = 25%   <- underpowered; a null here is NOT evidence of no effect
tourney N=16: judge - random       d = +20.0 pts   naive 95% CI [+5.4, +34.6]   cluster 95% CI [+5.4, +34.6]   deff 0.97   b/c 6/0   McNemar p = 0.0312   clustered p = 0.00709
                                   power: MDE(80%) 20.8 pts   power to detect 5 pts = 10%   <- underpowered; a null here is NOT evidence of no effect

============================================================================================================
3. ORACLE CEILING   (a correct candidate EXISTS vs the judge FINDS it)
   NOTE: for pruned arms this is pass@k over SURVIVORS, not over all N.
   Only the baseline row is a clean best-of-N ceiling.

baseline   N=1   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
baseline   N=2   ceiling  57.0%   selected  54.5%   gap  2.5 pts   capture  95.6%
baseline   N=4   ceiling  66.2%   selected  63.0%   gap  3.2 pts   capture  95.1%
baseline   N=8   ceiling  73.5%   selected  69.5%   gap  4.0 pts   capture  94.6%
baseline   N=16  ceiling  79.0%   selected  70.0%   gap  9.0 pts   capture  88.6%

rank       N=1   ceiling  49.2%   selected  49.2%   gap  0.0 pts   capture 100.0%
rank       N=2   ceiling  60.0%   selected  60.0%   gap  0.0 pts   capture 100.0%
rank       N=4   ceiling  70.8%   selected  67.5%   gap  3.3 pts   capture  95.3%
rank       N=8   ceiling  68.3%   selected  65.0%   gap  3.3 pts   capture  95.1%
rank       N=16  ceiling  76.7%   selected  76.7%   gap  0.0 pts   capture 100.0%

random     N=1   ceiling  42.5%   selected  42.5%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  55.0%   selected  54.2%   gap  0.8 pts   capture  98.5%
random     N=4   ceiling  62.5%   selected  59.2%   gap  3.3 pts   capture  94.7%
random     N=8   ceiling  68.3%   selected  61.7%   gap  6.7 pts   capture  90.2%
random     N=16  ceiling  76.7%   selected  73.3%   gap  3.3 pts   capture  95.7%

tourney    N=1   ceiling  44.2%   selected  44.2%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  57.5%   selected  57.5%   gap  0.0 pts   capture 100.0%
tourney    N=4   ceiling  65.8%   selected  63.3%   gap  2.5 pts   capture  96.2%
tourney    N=8   ceiling  68.3%   selected  68.3%   gap  0.0 pts   capture 100.0%
tourney    N=16  ceiling  73.3%   selected  73.3%   gap  0.0 pts   capture 100.0%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = +6.7 pts   naive 95% CI [+0.2, +13.1]   cluster 95% CI [+0.9, +12.4]   deff 0.76   b/c 12/4   McNemar p = 0.0768   clustered p = 0.0224
                                   power: MDE(80%) 8.2 pts   power to detect 5 pts = 40%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound +0.9 -> NON-INFERIOR   one-sided p = 3.22e-05
                                   tokens 5919 vs 5553  (+6.6%, 95% CI [+0.3%, +12.8%])
N=2   rank - random                d = +5.8 pts   naive 95% CI [+0.0, +11.7]   cluster 95% CI [-0.2, +11.9]   deff 1.05   b/c 10/3   McNemar p = 0.0923   clustered p = 0.0598
                                   power: MDE(80%) 8.7 pts   power to detect 5 pts = 36%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -0.2 -> NON-INFERIOR   one-sided p = 0.000236
                                   tokens 10168 vs 11114  (-8.5%, 95% CI [-15.2%, -1.8%])
N=4   rank - random                d = +8.3 pts   naive 95% CI [+1.9, +14.7]   cluster 95% CI [+0.8, +15.9]   deff 1.35   b/c 13/3   McNemar p = 0.0213   clustered p = 0.0306
                                   power: MDE(80%) 10.8 pts   power to detect 5 pts = 25%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound +0.8 -> NON-INFERIOR   one-sided p = 0.00027
                                   tokens 21829 vs 22967  (-5.0%, 95% CI [-9.0%, -0.9%])
N=8   rank - random                d = +3.3 pts   naive 95% CI [-3.2, +9.9]   cluster 95% CI [-4.7, +11.4]   deff 1.47   b/c 3/1   McNemar p = 0.625   clustered p = 0.417
                                   power: MDE(80%) 11.5 pts   power to detect 5 pts = 23%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -4.7 -> NON-INFERIOR   one-sided p = 0.0212
                                   tokens 41880 vs 44713  (-6.3%, 95% CI [-13.4%, +0.7%])
N=16  rank - random                d = +3.3 pts   naive 95% CI [-3.2, +9.9]   cluster 95% CI [-3.2, +9.9]   deff 0.97   b/c 1/0   McNemar p = 1   clustered p = 0.317
                                   power: MDE(80%) 9.3 pts   power to detect 5 pts = 32%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -3.2 -> NON-INFERIOR   one-sided p = 0.00621
                                   tokens 78873 vs 87553  (-9.9%, 95% CI [-14.5%, -5.3%])

N=1   rank - baseline              d = -0.8 pts   naive 95% CI [-7.6, +5.9]   cluster 95% CI [-7.3, +5.6]   deff 0.87   b/c 8/9   McNemar p = 1   clustered p = 0.799
                                   power: MDE(80%) 9.2 pts   power to detect 5 pts = 33%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -7.3 -> cannot claim parity   one-sided p = 0.102
                                   tokens 5919 vs 8417  (-23.5%, 95% CI [-32.1%, -14.9%])
N=2   rank - baseline              d = +1.7 pts   naive 95% CI [-4.0, +7.3]   cluster 95% CI [-3.6, +6.9]   deff 0.82   b/c 7/5   McNemar p = 0.774   clustered p = 0.531
                                   power: MDE(80%) 7.5 pts   power to detect 5 pts = 47%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -3.6 -> NON-INFERIOR   one-sided p = 0.00614
                                   tokens 10168 vs 17179  (-36.6%, 95% CI [-40.6%, -32.7%])
N=4   rank - baseline              d = +3.3 pts   naive 95% CI [-2.8, +9.4]   cluster 95% CI [-5.0, +11.7]   deff 1.82   b/c 9/5   McNemar p = 0.424   clustered p = 0.436
                                   power: MDE(80%) 12.0 pts   power to detect 5 pts = 21%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -5.0 -> cannot claim parity   one-sided p = 0.0257
                                   tokens 21829 vs 34192  (-31.6%, 95% CI [-36.5%, -26.7%])
N=8   rank - baseline              d = -1.7 pts   naive 95% CI [-4.9, +1.6]   cluster 95% CI [-4.9, +1.6]   deff 0.97   b/c 0/1   McNemar p = 1   clustered p = 0.317
                                   power: MDE(80%) 4.7 pts   power to detect 5 pts = 85%
                                   non-inferiority (margin 5 pts): lower bound -4.9 -> NON-INFERIOR   one-sided p = 0.0228
                                   tokens 41880 vs 67682  (-33.5%, 95% CI [-38.6%, -28.5%])
N=16  rank - baseline              d = +13.3 pts   naive 95% CI [+1.0, +25.7]   cluster 95% CI [+1.0, +25.7]   deff 0.97   b/c 4/0   McNemar p = 0.125   clustered p = 0.0347
                                   power: MDE(80%) 17.7 pts   power to detect 5 pts = 12%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound +1.0 -> NON-INFERIOR   one-sided p = 0.00184
                                   tokens 78873 vs 133659  (-37.0%, 95% CI [-40.6%, -33.4%])

N=1   tourney - baseline           d = -5.8 pts   naive 95% CI [-12.9, +1.2]   cluster 95% CI [-13.1, +1.5]   deff 1.03   b/c 6/13   McNemar p = 0.167   clustered p = 0.118
                                   power: MDE(80%) 10.4 pts   power to detect 5 pts = 27%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -13.1 -> cannot claim parity   one-sided p = 0.588
                                   tokens 5820 vs 8417  (-24.8%, 95% CI [-32.5%, -17.0%])
N=2   tourney - baseline           d = -0.8 pts   naive 95% CI [-7.2, +5.5]   cluster 95% CI [-6.3, +4.7]   deff 0.73   b/c 7/8   McNemar p = 1   clustered p = 0.767
                                   power: MDE(80%) 7.9 pts   power to detect 5 pts = 43%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -6.3 -> cannot claim parity   one-sided p = 0.0688
                                   tokens 10274 vs 17179  (-36.0%, 95% CI [-40.7%, -31.2%])
N=4   tourney - baseline           d = -0.8 pts   naive 95% CI [-6.3, +4.6]   cluster 95% CI [-8.4, +6.8]   deff 1.89   b/c 5/6   McNemar p = 1   clustered p = 0.83
                                   power: MDE(80%) 10.9 pts   power to detect 5 pts = 25%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -8.4 -> cannot claim parity   one-sided p = 0.142
                                   tokens 22008 vs 34192  (-31.0%, 95% CI [-35.2%, -26.9%])
N=8   tourney - baseline           d = +1.7 pts   naive 95% CI [-5.7, +9.0]   cluster 95% CI [-5.7, +9.1]   deff 0.98   b/c 3/2   McNemar p = 1   clustered p = 0.659
                                   power: MDE(80%) 10.6 pts   power to detect 5 pts = 26%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -5.7 -> cannot claim parity   one-sided p = 0.0388
                                   tokens 41692 vs 67682  (-33.8%, 95% CI [-38.3%, -29.4%])
N=16  tourney - baseline           d = +10.0 pts   naive 95% CI [-0.9, +20.9]   cluster 95% CI [-0.9, +20.9]   deff 0.97   b/c 3/0   McNemar p = 0.25   clustered p = 0.0726
                                   power: MDE(80%) 15.6 pts   power to detect 5 pts = 14%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -0.9 -> NON-INFERIOR   one-sided p = 0.00355
                                   tokens 82798 vs 133659  (-33.8%, 95% CI [-38.3%, -29.3%])

N=1   random - baseline            d = -7.5 pts   naive 95% CI [-14.9, -0.1]   cluster 95% CI [-14.2, -0.8]   deff 0.80   b/c 6/15   McNemar p = 0.0784   clustered p = 0.0284
                                   power: MDE(80%) 9.6 pts   power to detect 5 pts = 31%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -14.2 -> cannot claim parity   one-sided p = 0.767
                                   tokens 5553 vs 8417  (-28.2%, 95% CI [-35.8%, -20.6%])
N=2   random - baseline            d = -4.2 pts   naive 95% CI [-10.0, +1.7]   cluster 95% CI [-10.0, +1.6]   deff 0.94   b/c 4/9   McNemar p = 0.267   clustered p = 0.159
                                   power: MDE(80%) 8.3 pts   power to detect 5 pts = 39%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -10.0 -> cannot claim parity   one-sided p = 0.389
                                   tokens 11114 vs 17179  (-30.7%, 95% CI [-36.4%, -25.1%])
N=4   random - baseline            d = -5.0 pts   naive 95% CI [-10.6, +0.6]   cluster 95% CI [-11.4, +1.4]   deff 1.25   b/c 3/9   McNemar p = 0.146   clustered p = 0.125
                                   power: MDE(80%) 9.1 pts   power to detect 5 pts = 33%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -11.4 -> cannot claim parity   one-sided p = 0.5
                                   tokens 22967 vs 34192  (-28.0%, 95% CI [-33.8%, -22.3%])
N=8   random - baseline            d = -5.0 pts   naive 95% CI [-10.6, +0.6]   cluster 95% CI [-12.2, +2.2]   deff 1.62   b/c 0/3   McNemar p = 0.25   clustered p = 0.174
                                   power: MDE(80%) 10.3 pts   power to detect 5 pts = 27%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -12.2 -> cannot claim parity   one-sided p = 0.5
                                   tokens 44713 vs 67682  (-29.1%, 95% CI [-34.5%, -23.6%])
N=16  random - baseline            d = +10.0 pts   naive 95% CI [-0.9, +20.9]   cluster 95% CI [-0.9, +20.9]   deff 0.97   b/c 3/0   McNemar p = 0.25   clustered p = 0.0726
                                   power: MDE(80%) 15.6 pts   power to detect 5 pts = 14%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -0.9 -> NON-INFERIOR   one-sided p = 0.00355
                                   tokens 87553 vs 133659  (-30.0%, 95% CI [-35.0%, -25.0%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = +6.2 pts   naive 95% CI [+3.2, +9.3]   cluster 95% CI [+2.2, +10.2]   deff 1.69   b/c 39/11   McNemar p = 9.02e-05   clustered p = 0.00235
                                   power: MDE(80%) 5.7 pts   power to detect 5 pts = 69%
                                   equal-weight per N: d = +5.5 pts (from 5 cells: +6.7, +5.8, +8.3, +3.3, +3.3)

pooled rank - baseline (chunk-wtd) d = +1.8 pts   naive 95% CI [-1.2, +4.8]   cluster 95% CI [-2.6, +6.1]   deff 2.00   b/c 28/20   McNemar p = 0.312   clustered p = 0.422
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
                                   equal-weight per N: d = +3.2 pts (from 5 cells: -0.8, +1.7, +3.3, -1.7, +13.3)

pooled tourney - baseline (chunk-wtd) d = -1.1 pts   naive 95% CI [-4.3, +2.1]   cluster 95% CI [-6.0, +3.8]   deff 2.34   b/c 24/29   McNemar p = 0.583   clustered p = 0.659
                                   power: MDE(80%) 7.1 pts   power to detect 5 pts = 51%
                                   equal-weight per N: d = +0.8 pts (from 5 cells: -5.8, -0.8, -0.8, +1.7, +10.0)

pooled random - baseline (chunk-wtd) d = -4.4 pts   naive 95% CI [-7.6, -1.3]   cluster 95% CI [-9.1, +0.2]   deff 2.12   b/c 16/36   McNemar p = 0.00779   clustered p = 0.0592
                                   power: MDE(80%) 6.6 pts   power to detect 5 pts = 56%
                                   equal-weight per N: d = -2.3 pts (from 5 cells: -7.5, -4.2, -5.0, -5.0, +10.0)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = -0.8 pts   95% CI [-7.3, +5.6]   win/loss 5/4   p = 0.799   sign p = 1
                                   tokens 5919 vs 8417 (-29.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -7.3 -> cannot claim parity   one-sided p = 0.102
                                   WARNING: -30% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 9.2 pts   power to detect 5 pts = 33%   <- underpowered
rank N=2 vs baseline N=1           d = +10.0 pts   95% CI [+2.7, +17.3]   win/loss 9/1   p = 0.00709   sign p = 0.0215
                                   tokens 10168 vs 8417 (+20.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +2.7 -> NON-INFERIOR   one-sided p = 2.69e-05
                                   WARNING: +21% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 10.4 pts   power to detect 5 pts = 27%   <- underpowered
rank N=4 vs baseline N=2           d = +9.2 pts   95% CI [+1.2, +17.1]   win/loss 8/2   p = 0.024   sign p = 0.109
                                   tokens 21829 vs 17179 (+27.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +1.2 -> NON-INFERIOR   one-sided p = 0.000244
                                   WARNING: +27% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 11.4 pts   power to detect 5 pts = 23%   <- underpowered
rank N=8 vs baseline N=4           d = +0.8 pts   95% CI [-4.1, +5.8]   win/loss 2/1   p = 0.743   sign p = 1
                                   tokens 41880 vs 34192 (+22.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.1 -> NON-INFERIOR   one-sided p = 0.0108
                                   WARNING: +22% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 7.1 pts   power to detect 5 pts = 50%
rank N=16 vs baseline N=8          d = +10.0 pts   95% CI [-0.9, +20.9]   win/loss 3/0   p = 0.0726   sign p = 0.25
                                   tokens 78873 vs 67682 (+16.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -0.9 -> NON-INFERIOR   one-sided p = 0.00355
                                   WARNING: +17% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 15.6 pts   power to detect 5 pts = 14%   <- underpowered

random N=1 vs baseline N=1         d = -7.5 pts   95% CI [-14.2, -0.8]   win/loss 3/10   p = 0.0284   sign p = 0.0923
                                   tokens 5553 vs 8417 (-34.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -14.2 -> cannot claim parity   one-sided p = 0.767
                                   WARNING: -34% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 9.6 pts   power to detect 5 pts = 31%   <- underpowered
random N=2 vs baseline N=1         d = +4.2 pts   95% CI [-1.6, +10.0]   win/loss 7/3   p = 0.159   sign p = 0.344
                                   tokens 11114 vs 8417 (+32.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.6 -> NON-INFERIOR   one-sided p = 0.000966
                                   WARNING: +32% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 8.3 pts   power to detect 5 pts = 39%   <- underpowered
random N=4 vs baseline N=2         d = +0.8 pts   95% CI [-5.1, +6.8]   win/loss 6/4   p = 0.785   sign p = 0.754
                                   tokens 22967 vs 17179 (+33.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.1 -> cannot claim parity   one-sided p = 0.028
                                   WARNING: +34% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 8.6 pts   power to detect 5 pts = 37%   <- underpowered
random N=8 vs baseline N=4         d = -2.5 pts   95% CI [-10.8, +5.8]   win/loss 2/2   p = 0.553   sign p = 1
                                   tokens 44713 vs 34192 (+30.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -10.8 -> cannot claim parity   one-sided p = 0.276
                                   WARNING: +31% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 11.8 pts   power to detect 5 pts = 22%   <- underpowered
random N=16 vs baseline N=8        d = +6.7 pts   95% CI [-2.4, +15.7]   win/loss 2/0   p = 0.15   sign p = 0.5
                                   tokens 87553 vs 67682 (+29.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.4 -> NON-INFERIOR   one-sided p = 0.00589
                                   WARNING: +29% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 13.0 pts   power to detect 5 pts = 19%   <- underpowered

tourney N=1 vs baseline N=1        d = -5.8 pts   95% CI [-13.1, +1.5]   win/loss 2/7   p = 0.118   sign p = 0.18
                                   tokens 5820 vs 8417 (-30.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -13.1 -> cannot claim parity   one-sided p = 0.588
                                   WARNING: -31% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 10.4 pts   power to detect 5 pts = 27%   <- underpowered
tourney N=2 vs baseline N=1        d = +7.5 pts   95% CI [+0.4, +14.6]   win/loss 8/2   p = 0.0386   sign p = 0.109
                                   tokens 10274 vs 8417 (+22.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.4 -> NON-INFERIOR   one-sided p = 0.000283
                                   WARNING: +22% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 10.2 pts   power to detect 5 pts = 28%   <- underpowered
tourney N=4 vs baseline N=2        d = +5.0 pts   95% CI [-1.8, +11.8]   win/loss 5/2   p = 0.15   sign p = 0.453
                                   tokens 22008 vs 17179 (+28.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.8 -> NON-INFERIOR   one-sided p = 0.002
                                   WARNING: +28% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 9.7 pts   power to detect 5 pts = 30%   <- underpowered
tourney N=8 vs baseline N=4        d = +4.2 pts   95% CI [-4.0, +12.3]   win/loss 5/2   p = 0.317   sign p = 0.453
                                   tokens 41692 vs 34192 (+21.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.0 -> NON-INFERIOR   one-sided p = 0.0139
                                   WARNING: +22% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 11.7 pts   power to detect 5 pts = 22%   <- underpowered
tourney N=16 vs baseline N=8       d = +6.7 pts   95% CI [-2.4, +15.7]   win/loss 2/0   p = 0.15   sign p = 0.5
                                   tokens 82798 vs 67682 (+22.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.4 -> NON-INFERIOR   one-sided p = 0.00589
                                   WARNING: +22% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 13.0 pts   power to detect 5 pts = 19%   <- underpowered

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

============================================================================================================
8. CROSS-CONFIG SUMMARY   (the stable estimate: average over the grid)

   A single config is one noisy draw. Quoting the best cell overstates the
   effect because it is the maximum of many noisy cells. These are means.

   arm          N  configs  acc mean    min    max    tokens  vs base
   baseline     1        2     47.5%     48     48     8,417     0.0%
   rank         1        2     49.6%     49     50     5,932   -29.5%
   random       1        2     43.3%     42     44     5,740   -31.8%
   tourney      1        2     45.0%     44     46     5,772   -31.4%

   baseline     2        2     54.5%     55     55    17,179     0.0%
   rank         2        2     58.3%     57     60    10,775   -37.3%
   random       2        2     54.2%     54     54    11,282   -34.3%
   tourney      2        2     56.2%     55     57    10,790   -37.2%

   baseline     4        2     63.0%     63     63    34,192     0.0%
   rank         4        2     66.3%     65     68    22,097   -35.4%
   random       4        2     60.0%     59     61    22,886   -33.1%
   tourney      4        2     62.9%     62     63    22,004   -35.6%

   baseline     8        2     69.5%     70     70    67,682     0.0%
   rank         8        2     65.0%     65     65    42,768   -36.8%
   random       8        2     63.3%     62     65    44,999   -33.5%
   tourney      8        2     65.8%     63     68    42,806   -36.8%

   baseline    16        2     70.0%     70     70   133,659     0.0%
   rank        16        2     73.3%     70     77    81,197   -39.3%
   random      16        2     68.3%     63     73    87,596   -34.5%
   tourney     16        2     70.0%     67     73    84,444   -36.8%

   ORACLE CEILING COLLAPSE   (what pruning costs you before the judge acts)

   Pruning discards candidates, so a correct answer may never reach the judge.
   A smaller judge gap on a pruned arm is less headroom, not better selection.

   arm          N   ceiling  selected  judge gap  ceiling vs base
   baseline     1     47.5%     47.5%       0.0p             0.0p
   rank         1     49.6%     49.6%       0.0p             2.1p
   random       1     43.3%     43.3%       0.0p            -4.2p
   tourney      1     45.0%     45.0%       0.0p            -2.5p

   baseline     2     57.0%     54.5%       2.5p             0.0p
   rank         2     59.6%     58.3%       1.3p             2.6p
   random       2     54.6%     54.2%       0.4p            -2.4p
   tourney      2     57.1%     56.2%       0.8p             0.1p

   baseline     4     66.2%     63.0%       3.2p             0.0p
   rank         4     68.8%     66.3%       2.5p             2.5p
   random       4     62.1%     60.0%       2.1p            -4.2p
   tourney      4     65.8%     62.9%       2.9p            -0.4p

   baseline     8     73.5%     69.5%       4.0p             0.0p
   rank         8     69.2%     65.0%       4.2p            -4.3p
   random       8     68.3%     63.3%       5.0p            -5.2p
   tourney      8     68.3%     65.8%       2.5p            -5.2p

   baseline    16     79.0%     70.0%       9.0p             0.0p
   rank        16     78.3%     73.3%       5.0p            -0.7p
   random      16     75.0%     68.3%       6.7p            -4.0p
   tourney     16     73.3%     70.0%       3.3p            -5.7p


============================================================================================================
9. ISO-TOKEN CONTRASTS   (baseline curve INTERPOLATED to each cell's actual spend)

   Section 6 snaps each cell to the nearest baseline N, leaving budget gaps up to
   +49%. Here the baseline accuracy-vs-token curve is log-interpolated to the exact
   budget each cell spent, so there is no mismatch left to warn about.

   baseline stop-tail correction: 26.25% of generated tokens
   fall after the first </answer>, which the baseline is charged for and the arms
   are not (no stop string on the baseline; stop=['</answer>'] on the arms).

      N  baseline acc   tokens raw  tokens corrected
      1         47.5%        8,417             6,253
      2         54.5%       17,179            12,849
      4         63.0%       34,192            25,532
      8         69.5%       67,682            50,363
     16         70.0%      133,659            99,021

   RAW baseline: arm accuracy minus interpolated baseline accuracy
     over 30 equal-N cells:  mean +2.06 pts   median +2.67 pts   positive 20/30   (negative 10)
       plan=1000  mean +0.99 pts   (15 cells)
       plan=2500  mean +3.12 pts   (15 cells)

   STOP-CORRECTED baseline: arm accuracy minus interpolated baseline accuracy
     over 30 equal-N cells:  mean +0.16 pts   median +0.71 pts   positive 17/30   (negative 13)
       plan=1000  mean -0.90 pts   (15 cells)
       plan=2500  mean +1.23 pts   (15 cells)

   Read together: against the raw baseline the pruned arms are roughly break-even at
   equal budget; against the stop-corrected baseline they are negative at every plan
   level. The apparent iso-token parity depends on charging the baseline for tokens
   the arms never emit.

============================================================================================================
7. MULTIPLE COMPARISONS   (corrected WITHIN each hypothesis family)

   Families are corrected separately. Pooling them would let the enormous
   judge-vs-random effects (p ~ 1e-9) inflate m and consume the alpha that
   the borderline arm contrasts actually need.

   family              tests  p<.05  by chance   Holm    BH
   arm-contrast           40      5          2      0     0
   judge-vs-random        28     22          1     10    22
   non-inferiority        70     35          4     10    27
   pooled                  8      2          0      1     2
   token-matched          30      6          2      0     0

   19 nominally-significant results do NOT survive BH within their family.
   Do not cite these on their own:
     p=0.00709   [token-matched] plan=2500,prune=2.0  rank N=2 vs baseline N=1
     p=0.016     [arm-contrast] plan=1000,prune=2.0  N=4   rank - random
     p=0.0208    [non-inferiority] plan=1000,prune=2.0  [NI] random N=2 vs baseline N=1
     p=0.0212    [non-inferiority] plan=2500,prune=2.0  [NI] N=8   rank - random
     p=0.0224    [token-matched] plan=1000,prune=2.0  rank N=4 vs baseline N=2
     p=0.0224    [arm-contrast] plan=2500,prune=2.0  N=1   rank - random
     p=0.0228    [non-inferiority] plan=2500,prune=2.0  [NI] N=8   rank - baseline
     p=0.024     [token-matched] plan=2500,prune=2.0  rank N=4 vs baseline N=2
     p=0.0257    [non-inferiority] plan=2500,prune=2.0  [NI] N=4   rank - baseline
     p=0.028     [non-inferiority] plan=2500,prune=2.0  [NI] random N=4 vs baseline N=2
     p=0.028     [non-inferiority] plan=1000,prune=2.0  [NI] N=4   rank - baseline
     p=0.0284    [arm-contrast] plan=2500,prune=2.0  N=1   random - baseline
     p=0.0284    [token-matched] plan=2500,prune=2.0  random N=1 vs baseline N=1
     p=0.0306    [arm-contrast] plan=2500,prune=2.0  N=4   rank - random
     p=0.0347    [arm-contrast] plan=2500,prune=2.0  N=16  rank - baseline
     p=0.0386    [token-matched] plan=2500,prune=2.0  tourney N=2 vs baseline N=1
     p=0.0388    [non-inferiority] plan=2500,prune=2.0  [NI] N=8   tourney - baseline
     p=0.0467    [token-matched] plan=1000,prune=2.0  tourney N=2 vs baseline N=1
     p=0.0474    [non-inferiority] plan=1000,prune=2.0  [NI] random N=8 vs baseline N=4

   21 results survive the strict Holm correction; these are the safe ones to quote.
```
