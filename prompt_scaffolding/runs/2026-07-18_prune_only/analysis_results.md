# Analysis Results

Generated 2026-07-19 19:58 by `analysis.py --grid` over SLURM array `20276744`.

- **Grid:** `max_plan_tokens` ∈ {1000, 2500, 4000} × `prune_ratio` ∈ {1.5, 2, 3, 4} = 12 configs × 3 arms + shared baseline.
- **Data:** countdown, 100 questions, best-of-N ∈ {1,2,4,8,16}, Qwen3-4B-Instruct-2507.

## Read this first — two estimands, do not splice them

`§4` compares arms at **equal N**: that is where the 50–60% token reduction lives, and there accuracy is
**significantly worse**. `§6` compares at **matched budget**: that is where parity is licensed, but the
realized saving is much smaller, because each pruned cell is matched to a *smaller* baseline N.
Quoting the token number from §4 and the parity verdict from §6 combines two different comparisons.

**The §4 token reduction is also not apples-to-apples.** The baseline is generated with no stop string and the
arms stop at `</answer>`, so the baseline is charged for the 26.25% of its generated tokens that follow the
closing tag. Corrected, the equal-N reduction is **38–45%** at bon ≥ 2, not 50–60%. §9 reports the iso-token
contrast on both bases; the verdict flips sign between them.

## Method notes

- Paired tests, clustered by question, finite-sample corrected.
- §4 now contrasts **all three** arms against baseline (rank, tourney **and random**); random was previously omitted.
- §7 corrects within families and includes the non-inferiority tests.
- Cells with >15% budget mismatch are flagged inline in §6; they are not matched-budget results.
- Baseline-only tests are recorded once, not once per config.
- §9 (new) re-bases §6 by *interpolating* the baseline accuracy-vs-token curve to each cell's actual
  spend, on both the raw and the stop-corrected baseline. It records no p-values (it re-describes the
  same cells as §6).

```

############################################################################################################
# CONFIG  plan=1000  prune=1.5
############################################################################################################
============================================================================================================
FILES
  baseline  2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json
  random    2026-07-19_07-07-37_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_1.5.json
  rank      2026-07-19_07-06-50_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_1.5.json
  tourney   2026-07-19_07-08-25_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_1.5.json
  N values: [1, 2, 4, 8, 16]

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16
baseline      47.5%   8417t    54.5%  17179t    63.0%  34192t    69.5%  67682t    70.0% 133659t
rank          46.5%   6099t    46.0%   7065t    52.2%  13847t    63.5%  32495t    65.0%  63229t
random        46.8%   5858t    48.8%   6705t    56.2%  14011t    62.5%  32907t    71.0%  63967t
tourney       45.8%   5920t    49.5%   6843t    53.0%  14242t    63.0%  32627t    69.0%  63679t

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
rank N=2: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=4: judge - random           d = +4.2 pts   naive 95% CI [+1.6, +6.9]   cluster 95% CI [+1.5, +7.0]   deff 1.13   b/c 23/6   McNemar p = 0.00232   clustered p = 0.00284
                                   power: MDE(80%) 4.0 pts   power to detect 5 pts = 94%
rank N=8: judge - random           d = +14.0 pts   naive 95% CI [+8.4, +19.6]   cluster 95% CI [+7.8, +20.2]   deff 1.25   b/c 32/4   McNemar p = 1.94e-06   clustered p = 1.1e-05
                                   power: MDE(80%) 8.9 pts   power to detect 5 pts = 35%   <- underpowered; a null here is NOT evidence of no effect
rank N=16: judge - random          d = +14.0 pts   naive 95% CI [+6.1, +21.9]   cluster 95% CI [+6.1, +21.9]   deff 0.99   b/c 16/2   McNemar p = 0.00131   clustered p = 0.000505
                                   power: MDE(80%) 11.3 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=4: judge - random         d = +9.8 pts   naive 95% CI [+6.5, +13.0]   cluster 95% CI [+5.8, +13.7]   deff 1.41   b/c 44/5   McNemar p = 7.6e-09   clustered p = 1.18e-06
                                   power: MDE(80%) 5.6 pts   power to detect 5 pts = 70%
random N=8: judge - random         d = +17.0 pts   naive 95% CI [+11.3, +22.7]   cluster 95% CI [+10.9, +23.1]   deff 1.12   b/c 37/3   McNemar p = 1.95e-08   clustered p = 4.86e-08
                                   power: MDE(80%) 8.7 pts   power to detect 5 pts = 36%   <- underpowered; a null here is NOT evidence of no effect
random N=16: judge - random        d = +27.0 pts   naive 95% CI [+16.6, +37.4]   cluster 95% CI [+16.6, +37.4]   deff 0.99   b/c 31/4   McNemar p = 3.47e-06   clustered p = 3.34e-07
                                   power: MDE(80%) 14.8 pts   power to detect 5 pts = 16%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=4: judge - random        d = +7.8 pts   naive 95% CI [+4.9, +10.6]   cluster 95% CI [+4.7, +10.8]   deff 1.08   b/c 34/3   McNemar p = 1.23e-07   clustered p = 4.55e-07
                                   power: MDE(80%) 4.3 pts   power to detect 5 pts = 90%
tourney N=8: judge - random        d = +13.5 pts   naive 95% CI [+7.3, +19.7]   cluster 95% CI [+6.3, +20.7]   deff 1.36   b/c 35/8   McNemar p = 4.19e-05   clustered p = 0.000247
                                   power: MDE(80%) 10.3 pts   power to detect 5 pts = 27%   <- underpowered; a null here is NOT evidence of no effect
tourney N=16: judge - random       d = +19.0 pts   naive 95% CI [+9.5, +28.5]   cluster 95% CI [+9.5, +28.5]   deff 0.99   b/c 23/4   McNemar p = 0.000311   clustered p = 9.27e-05
                                   power: MDE(80%) 13.6 pts   power to detect 5 pts = 18%   <- underpowered; a null here is NOT evidence of no effect

============================================================================================================
3. ORACLE CEILING   (a correct candidate EXISTS vs the judge FINDS it)
   NOTE: for pruned arms this is pass@k over SURVIVORS, not over all N.
   Only the baseline row is a clean best-of-N ceiling.

baseline   N=1   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
baseline   N=2   ceiling  57.0%   selected  54.5%   gap  2.5 pts   capture  95.6%
baseline   N=4   ceiling  66.2%   selected  63.0%   gap  3.2 pts   capture  95.1%
baseline   N=8   ceiling  73.5%   selected  69.5%   gap  4.0 pts   capture  94.6%
baseline   N=16  ceiling  79.0%   selected  70.0%   gap  9.0 pts   capture  88.6%

rank       N=1   ceiling  46.5%   selected  46.5%   gap  0.0 pts   capture 100.0%
rank       N=2   ceiling  46.0%   selected  46.0%   gap  0.0 pts   capture 100.0%
rank       N=4   ceiling  54.2%   selected  52.2%   gap  2.0 pts   capture  96.3%
rank       N=8   ceiling  67.0%   selected  63.5%   gap  3.5 pts   capture  94.8%
rank       N=16  ceiling  72.0%   selected  65.0%   gap  7.0 pts   capture  90.3%

random     N=1   ceiling  46.8%   selected  46.8%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  48.8%   selected  48.8%   gap  0.0 pts   capture 100.0%
random     N=4   ceiling  58.2%   selected  56.2%   gap  2.0 pts   capture  96.6%
random     N=8   ceiling  66.0%   selected  62.5%   gap  3.5 pts   capture  94.7%
random     N=16  ceiling  78.0%   selected  71.0%   gap  7.0 pts   capture  91.0%

tourney    N=1   ceiling  45.8%   selected  45.8%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  49.5%   selected  49.5%   gap  0.0 pts   capture 100.0%
tourney    N=4   ceiling  55.8%   selected  53.0%   gap  2.7 pts   capture  95.1%
tourney    N=8   ceiling  67.5%   selected  63.0%   gap  4.5 pts   capture  93.3%
tourney    N=16  ceiling  75.0%   selected  69.0%   gap  6.0 pts   capture  92.0%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = -0.2 pts   naive 95% CI [-4.1, +3.6]   cluster 95% CI [-3.7, +3.2]   deff 0.78   b/c 31/32   McNemar p = 1   clustered p = 0.887
                                   power: MDE(80%) 4.9 pts   power to detect 5 pts = 81%
                                   non-inferiority (margin 5 pts): lower bound -3.7 -> NON-INFERIOR   one-sided p = 0.00346
                                   tokens 6099 vs 5858  (+4.1%, 95% CI [-0.2%, +8.4%])
N=2   rank - random                d = -2.8 pts   naive 95% CI [-6.7, +1.2]   cluster 95% CI [-6.9, +1.4]   deff 1.08   b/c 27/38   McNemar p = 0.215   clustered p = 0.19
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
                                   non-inferiority (margin 5 pts): lower bound -6.9 -> cannot claim parity   one-sided p = 0.142
                                   tokens 7065 vs 6705  (+5.4%, 95% CI [+0.7%, +10.1%])
N=4   rank - random                d = -4.0 pts   naive 95% CI [-8.2, +0.2]   cluster 95% CI [-8.5, +0.5]   deff 1.13   b/c 29/45   McNemar p = 0.0805   clustered p = 0.0814
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 59%
                                   non-inferiority (margin 5 pts): lower bound -8.5 -> cannot claim parity   one-sided p = 0.332
                                   tokens 13847 vs 14011  (-1.2%, 95% CI [-4.3%, +2.0%])
N=8   rank - random                d = +1.0 pts   naive 95% CI [-4.4, +6.4]   cluster 95% CI [-4.0, +6.0]   deff 0.86   b/c 16/14   McNemar p = 0.856   clustered p = 0.696
                                   power: MDE(80%) 7.2 pts   power to detect 5 pts = 50%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -4.0 -> NON-INFERIOR   one-sided p = 0.00955
                                   tokens 32495 vs 32907  (-1.3%, 95% CI [-4.5%, +2.0%])
N=16  rank - random                d = -6.0 pts   naive 95% CI [-14.3, +2.3]   cluster 95% CI [-14.3, +2.3]   deff 0.99   b/c 6/12   McNemar p = 0.238   clustered p = 0.155
                                   power: MDE(80%) 11.8 pts   power to detect 5 pts = 22%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -14.3 -> cannot claim parity   one-sided p = 0.594
                                   tokens 63229 vs 63967  (-1.2%, 95% CI [-4.2%, +1.9%])

N=1   rank - baseline              d = -1.0 pts   naive 95% CI [-5.4, +3.4]   cluster 95% CI [-5.6, +3.6]   deff 1.07   b/c 38/42   McNemar p = 0.738   clustered p = 0.668
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 57%
                                   non-inferiority (margin 5 pts): lower bound -5.6 -> cannot claim parity   one-sided p = 0.0429
                                   tokens 6099 vs 8417  (-27.5%, 95% CI [-32.4%, -22.7%])
N=2   rank - baseline              d = -8.5 pts   naive 95% CI [-12.6, -4.4]   cluster 95% CI [-12.8, -4.2]   deff 1.07   b/c 20/54   McNemar p = 9.61e-05   clustered p = 0.000109
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
                                   non-inferiority (margin 5 pts): lower bound -12.8 -> cannot claim parity   one-sided p = 0.944
                                   tokens 7065 vs 17179  (-58.9%, 95% CI [-61.2%, -56.6%])
N=4   rank - baseline              d = -10.8 pts   naive 95% CI [-15.0, -6.5]   cluster 95% CI [-15.2, -6.3]   deff 1.11   b/c 18/61   McNemar p = 1.27e-06   clustered p = 2.48e-06
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 59%
                                   non-inferiority (margin 5 pts): lower bound -15.2 -> cannot claim parity   one-sided p = 0.994
                                   tokens 13847 vs 34192  (-59.5%, 95% CI [-61.4%, -57.6%])
N=8   rank - baseline              d = -6.0 pts   naive 95% CI [-10.9, -1.1]   cluster 95% CI [-11.1, -0.9]   deff 1.05   b/c 7/19   McNemar p = 0.029   clustered p = 0.0205
                                   power: MDE(80%) 7.3 pts   power to detect 5 pts = 49%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -11.1 -> cannot claim parity   one-sided p = 0.65
                                   tokens 32495 vs 67682  (-52.0%, 95% CI [-54.3%, -49.7%])
N=16  rank - baseline              d = -5.0 pts   naive 95% CI [-13.1, +3.1]   cluster 95% CI [-13.1, +3.1]   deff 0.99   b/c 6/11   McNemar p = 0.332   clustered p = 0.224
                                   power: MDE(80%) 11.5 pts   power to detect 5 pts = 23%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -13.1 -> cannot claim parity   one-sided p = 0.5
                                   tokens 63229 vs 133659  (-52.7%, 95% CI [-54.8%, -50.6%])

N=1   tourney - baseline           d = -1.8 pts   naive 95% CI [-6.1, +2.6]   cluster 95% CI [-5.7, +2.2]   deff 0.82   b/c 36/43   McNemar p = 0.5   clustered p = 0.386
                                   power: MDE(80%) 5.7 pts   power to detect 5 pts = 70%
                                   non-inferiority (margin 5 pts): lower bound -5.7 -> cannot claim parity   one-sided p = 0.0536
                                   tokens 5920 vs 8417  (-29.7%, 95% CI [-34.1%, -25.3%])
N=2   tourney - baseline           d = -5.0 pts   naive 95% CI [-9.0, -1.0]   cluster 95% CI [-9.3, -0.7]   deff 1.13   b/c 24/44   McNemar p = 0.0205   clustered p = 0.0225
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
                                   non-inferiority (margin 5 pts): lower bound -9.3 -> cannot claim parity   one-sided p = 0.5
                                   tokens 6843 vs 17179  (-60.2%, 95% CI [-62.5%, -57.8%])
N=4   tourney - baseline           d = -10.0 pts   naive 95% CI [-14.3, -5.7]   cluster 95% CI [-14.9, -5.1]   deff 1.25   b/c 21/61   McNemar p = 1.13e-05   clustered p = 5.81e-05
                                   power: MDE(80%) 7.0 pts   power to detect 5 pts = 52%
                                   non-inferiority (margin 5 pts): lower bound -14.9 -> cannot claim parity   one-sided p = 0.978
                                   tokens 14242 vs 34192  (-58.3%, 95% CI [-60.3%, -56.4%])
N=8   tourney - baseline           d = -6.5 pts   naive 95% CI [-11.9, -1.1]   cluster 95% CI [-12.0, -1.0]   deff 1.03   b/c 9/22   McNemar p = 0.0294   clustered p = 0.0208
                                   power: MDE(80%) 7.9 pts   power to detect 5 pts = 43%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -12.0 -> cannot claim parity   one-sided p = 0.703
                                   tokens 32627 vs 67682  (-51.8%, 95% CI [-53.8%, -49.8%])
N=16  tourney - baseline           d = -1.0 pts   naive 95% CI [-9.1, +7.1]   cluster 95% CI [-9.1, +7.1]   deff 0.99   b/c 8/9   McNemar p = 1   clustered p = 0.809
                                   power: MDE(80%) 11.6 pts   power to detect 5 pts = 23%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -9.1 -> cannot claim parity   one-sided p = 0.167
                                   tokens 63679 vs 133659  (-52.4%, 95% CI [-54.6%, -50.1%])

N=1   random - baseline            d = -0.8 pts   naive 95% CI [-5.3, +3.8]   cluster 95% CI [-4.8, +3.3]   deff 0.77   b/c 42/45   McNemar p = 0.83   clustered p = 0.715
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 68%
                                   non-inferiority (margin 5 pts): lower bound -4.8 -> NON-INFERIOR   one-sided p = 0.0193
                                   tokens 5858 vs 8417  (-30.4%, 95% CI [-35.0%, -25.8%])
N=2   random - baseline            d = -5.8 pts   naive 95% CI [-9.7, -1.8]   cluster 95% CI [-9.6, -1.9]   deff 0.94   b/c 22/45   McNemar p = 0.00674   clustered p = 0.00358
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 72%
                                   non-inferiority (margin 5 pts): lower bound -9.6 -> cannot claim parity   one-sided p = 0.648
                                   tokens 6705 vs 17179  (-61.0%, 95% CI [-63.2%, -58.7%])
N=4   random - baseline            d = -6.8 pts   naive 95% CI [-10.9, -2.6]   cluster 95% CI [-11.6, -1.9]   deff 1.33   b/c 24/51   McNemar p = 0.00244   clustered p = 0.00657
                                   power: MDE(80%) 7.0 pts   power to detect 5 pts = 52%
                                   non-inferiority (margin 5 pts): lower bound -11.6 -> cannot claim parity   one-sided p = 0.759
                                   tokens 14011 vs 34192  (-59.0%, 95% CI [-61.1%, -57.0%])
N=8   random - baseline            d = -7.0 pts   naive 95% CI [-12.1, -1.9]   cluster 95% CI [-12.4, -1.6]   deff 1.11   b/c 7/21   McNemar p = 0.0125   clustered p = 0.011
                                   power: MDE(80%) 7.7 pts   power to detect 5 pts = 44%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -12.4 -> cannot claim parity   one-sided p = 0.766
                                   tokens 32907 vs 67682  (-51.4%, 95% CI [-53.7%, -49.0%])
N=16  random - baseline            d = +1.0 pts   naive 95% CI [-7.6, +9.6]   cluster 95% CI [-7.6, +9.6]   deff 0.99   b/c 10/9   McNemar p = 1   clustered p = 0.819
                                   power: MDE(80%) 12.3 pts   power to detect 5 pts = 21%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -7.6 -> cannot claim parity   one-sided p = 0.0854
                                   tokens 63967 vs 133659  (-52.1%, 95% CI [-54.5%, -49.8%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = -2.1 pts   naive 95% CI [-4.2, -0.1]   cluster 95% CI [-4.3, +0.1]   deff 1.13   b/c 109/141   McNemar p = 0.0497   clustered p = 0.0579
                                   power: MDE(80%) 3.2 pts   power to detect 5 pts = 99%
                                   equal-weight per N: d = -2.4 pts (from 5 cells: -0.2, -2.8, -4.0, +1.0, -6.0)

pooled rank - baseline (chunk-wtd) d = -6.5 pts   naive 95% CI [-8.7, -4.4]   cluster 95% CI [-9.3, -3.8]   deff 1.65   b/c 89/187   McNemar p = 3.64e-09   clustered p = 3.89e-06
                                   power: MDE(80%) 4.0 pts   power to detect 5 pts = 94%
                                   equal-weight per N: d = -6.2 pts (from 5 cells: -1.0, -8.5, -10.8, -6.0, -5.0)

pooled tourney - baseline (chunk-wtd) d = -5.4 pts   naive 95% CI [-7.6, -3.2]   cluster 95% CI [-8.4, -2.4]   deff 1.85   b/c 98/179   McNemar p = 1.3e-06   clustered p = 0.000337
                                   power: MDE(80%) 4.2 pts   power to detect 5 pts = 91%
                                   equal-weight per N: d = -4.9 pts (from 5 cells: -1.8, -5.0, -10.0, -6.5, -1.0)

pooled random - baseline (chunk-wtd) d = -4.4 pts   naive 95% CI [-6.6, -2.2]   cluster 95% CI [-7.2, -1.6]   deff 1.68   b/c 105/171   McNemar p = 8.5e-05   clustered p = 0.00216
                                   power: MDE(80%) 4.0 pts   power to detect 5 pts = 94%
                                   equal-weight per N: d = -3.9 pts (from 5 cells: -0.8, -5.8, -6.8, -7.0, +1.0)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = -1.0 pts   95% CI [-5.6, +3.6]   win/loss 20/23   p = 0.668   sign p = 0.761
                                   tokens 6099 vs 8417 (-27.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.6 -> cannot claim parity   one-sided p = 0.0429
                                   WARNING: -28% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 57%
rank N=2 vs baseline N=1           d = -1.5 pts   95% CI [-5.4, +2.4]   win/loss 14/22   p = 0.447   sign p = 0.243
                                   tokens 7065 vs 8417 (-16.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.4 -> cannot claim parity   one-sided p = 0.038
                                   WARNING: -16% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 72%
rank N=4 vs baseline N=2           d = -2.2 pts   95% CI [-6.2, +1.7]   win/loss 17/25   p = 0.264   sign p = 0.28
                                   tokens 13847 vs 17179 (-19.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -6.2 -> cannot claim parity   one-sided p = 0.086
                                   WARNING: -19% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.6 pts   power to detect 5 pts = 70%
rank N=8 vs baseline N=4           d = +0.5 pts   95% CI [-4.6, +5.6]   win/loss 17/18   p = 0.847   sign p = 1
                                   tokens 32495 vs 34192 (-5.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.6 -> NON-INFERIOR   one-sided p = 0.0167
                                   power: MDE(80%) 7.2 pts   power to detect 5 pts = 49%   <- underpowered
rank N=16 vs baseline N=8          d = -4.5 pts   95% CI [-10.6, +1.6]   win/loss 8/13   p = 0.147   sign p = 0.383
                                   tokens 63229 vs 67682 (-6.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -10.6 -> cannot claim parity   one-sided p = 0.436
                                   power: MDE(80%) 8.7 pts   power to detect 5 pts = 36%   <- underpowered

random N=1 vs baseline N=1         d = -0.8 pts   95% CI [-4.8, +3.3]   win/loss 17/19   p = 0.715   sign p = 0.868
                                   tokens 5858 vs 8417 (-30.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.8 -> NON-INFERIOR   one-sided p = 0.0193
                                   WARNING: -30% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 68%
random N=2 vs baseline N=1         d = +1.2 pts   95% CI [-2.8, +5.3]   win/loss 23/18   p = 0.549   sign p = 0.533
                                   tokens 6705 vs 8417 (-20.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.8 -> NON-INFERIOR   one-sided p = 0.00135
                                   WARNING: -20% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 67%
random N=4 vs baseline N=2         d = +1.8 pts   95% CI [-2.5, +6.0]   win/loss 22/17   p = 0.42   sign p = 0.522
                                   tokens 14011 vs 17179 (-18.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.5 -> NON-INFERIOR   one-sided p = 0.000928
                                   WARNING: -18% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 64%
random N=8 vs baseline N=4         d = -0.5 pts   95% CI [-5.5, +4.5]   win/loss 18/20   p = 0.844   sign p = 0.871
                                   tokens 32907 vs 34192 (-3.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.5 -> cannot claim parity   one-sided p = 0.0381
                                   power: MDE(80%) 7.1 pts   power to detect 5 pts = 50%
random N=16 vs baseline N=8        d = +1.5 pts   95% CI [-6.3, +9.3]   win/loss 15/12   p = 0.707   sign p = 0.701
                                   tokens 63967 vs 67682 (-5.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -6.3 -> cannot claim parity   one-sided p = 0.0515
                                   power: MDE(80%) 11.2 pts   power to detect 5 pts = 24%   <- underpowered

tourney N=1 vs baseline N=1        d = -1.8 pts   95% CI [-5.7, +2.2]   win/loss 16/23   p = 0.386   sign p = 0.337
                                   tokens 5920 vs 8417 (-29.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.7 -> cannot claim parity   one-sided p = 0.0536
                                   WARNING: -30% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.7 pts   power to detect 5 pts = 70%
tourney N=2 vs baseline N=1        d = +2.0 pts   95% CI [-2.5, +6.5]   win/loss 21/19   p = 0.383   sign p = 0.875
                                   tokens 6843 vs 8417 (-18.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.5 -> NON-INFERIOR   one-sided p = 0.00114
                                   WARNING: -19% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 59%
tourney N=4 vs baseline N=2        d = -1.5 pts   95% CI [-5.4, +2.4]   win/loss 18/20   p = 0.447   sign p = 0.871
                                   tokens 14242 vs 17179 (-17.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.4 -> cannot claim parity   one-sided p = 0.038
                                   WARNING: -17% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 72%
tourney N=8 vs baseline N=4        d = +0.0 pts   95% CI [-5.8, +5.8]   win/loss 18/17   p = 1   sign p = 1
                                   tokens 32627 vs 34192 (-4.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.8 -> cannot claim parity   one-sided p = 0.0451
                                   power: MDE(80%) 8.3 pts   power to detect 5 pts = 40%   <- underpowered
tourney N=16 vs baseline N=8       d = -0.5 pts   95% CI [-6.3, +5.3]   win/loss 10/10   p = 0.866   sign p = 1
                                   tokens 63679 vs 67682 (-5.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -6.3 -> cannot claim parity   one-sided p = 0.065
                                   power: MDE(80%) 8.3 pts   power to detect 5 pts = 39%   <- underpowered

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

############################################################################################################
# CONFIG  plan=1000  prune=2.0
############################################################################################################
============================================================================================================
FILES
  baseline  2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json
  random    2026-07-19_04-07-38_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_2.0.json
  rank      2026-07-19_04-06-52_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_2.0.json
  tourney   2026-07-19_04-08-25_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_2.0.json
  N values: [1, 2, 4, 8, 16]

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16
baseline      47.5%   8417t    54.5%  17179t    63.0%  34192t    69.5%  67682t    70.0% 133659t
rank          47.0%   6106t    48.5%   6889t    54.2%  14284t    62.5%  27529t    75.0%  52407t
random        45.2%   5889t    47.5%   6927t    52.5%  14310t    59.5%  28314t    69.0%  55328t
tourney       44.5%   6076t    46.2%   6896t    56.0%  13991t    62.5%  27580t    68.0%  55450t

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
rank N=2: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=4: judge - random           d = +7.2 pts   naive 95% CI [+4.4, +10.1]   cluster 95% CI [+4.2, +10.3]   deff 1.17   b/c 32/3   McNemar p = 4.18e-07   clustered p = 3.4e-06
                                   power: MDE(80%) 4.4 pts   power to detect 5 pts = 89%
rank N=8: judge - random           d = +14.5 pts   naive 95% CI [+9.2, +19.8]   cluster 95% CI [+8.9, +20.1]   deff 1.13   b/c 31/2   McNemar p = 1.31e-07   clustered p = 4.32e-07
                                   power: MDE(80%) 8.0 pts   power to detect 5 pts = 41%   <- underpowered; a null here is NOT evidence of no effect
rank N=16: judge - random          d = +25.0 pts   naive 95% CI [+16.5, +33.5]   cluster 95% CI [+16.5, +33.5]   deff 0.99   b/c 25/0   McNemar p = 5.96e-08   clustered p = 9.22e-09
                                   power: MDE(80%) 12.2 pts   power to detect 5 pts = 21%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=4: judge - random         d = +8.5 pts   naive 95% CI [+5.6, +11.4]   cluster 95% CI [+5.3, +11.7]   deff 1.21   b/c 36/2   McNemar p = 5.4e-09   clustered p = 2.07e-07
                                   power: MDE(80%) 4.6 pts   power to detect 5 pts = 86%
random N=8: judge - random         d = +15.0 pts   naive 95% CI [+9.3, +20.7]   cluster 95% CI [+9.0, +21.0]   deff 1.10   b/c 34/4   McNemar p = 6.04e-07   clustered p = 9.24e-07
                                   power: MDE(80%) 8.6 pts   power to detect 5 pts = 37%   <- underpowered; a null here is NOT evidence of no effect
random N=16: judge - random        d = +25.0 pts   naive 95% CI [+15.2, +34.8]   cluster 95% CI [+15.2, +34.8]   deff 0.99   b/c 28/3   McNemar p = 4.65e-06   clustered p = 5.73e-07
                                   power: MDE(80%) 14.0 pts   power to detect 5 pts = 17%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=4: judge - random        d = +8.8 pts   naive 95% CI [+5.6, +11.9]   cluster 95% CI [+5.2, +12.3]   deff 1.21   b/c 40/5   McNemar p = 7.88e-08   clustered p = 1.02e-06
                                   power: MDE(80%) 5.0 pts   power to detect 5 pts = 80%
tourney N=8: judge - random        d = +18.0 pts   naive 95% CI [+12.7, +23.3]   cluster 95% CI [+12.2, +23.8]   deff 1.18   b/c 36/0   McNemar p = 2.91e-11   clustered p = 1.44e-09
                                   power: MDE(80%) 8.3 pts   power to detect 5 pts = 39%   <- underpowered; a null here is NOT evidence of no effect
tourney N=16: judge - random       d = +20.0 pts   naive 95% CI [+10.8, +29.2]   cluster 95% CI [+10.8, +29.2]   deff 0.99   b/c 23/3   McNemar p = 8.8e-05   clustered p = 2.21e-05
                                   power: MDE(80%) 13.2 pts   power to detect 5 pts = 18%   <- underpowered; a null here is NOT evidence of no effect

============================================================================================================
3. ORACLE CEILING   (a correct candidate EXISTS vs the judge FINDS it)
   NOTE: for pruned arms this is pass@k over SURVIVORS, not over all N.
   Only the baseline row is a clean best-of-N ceiling.

baseline   N=1   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
baseline   N=2   ceiling  57.0%   selected  54.5%   gap  2.5 pts   capture  95.6%
baseline   N=4   ceiling  66.2%   selected  63.0%   gap  3.2 pts   capture  95.1%
baseline   N=8   ceiling  73.5%   selected  69.5%   gap  4.0 pts   capture  94.6%
baseline   N=16  ceiling  79.0%   selected  70.0%   gap  9.0 pts   capture  88.6%

rank       N=1   ceiling  47.0%   selected  47.0%   gap  0.0 pts   capture 100.0%
rank       N=2   ceiling  48.5%   selected  48.5%   gap  0.0 pts   capture 100.0%
rank       N=4   ceiling  55.5%   selected  54.2%   gap  1.3 pts   capture  97.7%
rank       N=8   ceiling  66.0%   selected  62.5%   gap  3.5 pts   capture  94.7%
rank       N=16  ceiling  76.0%   selected  75.0%   gap  1.0 pts   capture  98.7%

random     N=1   ceiling  45.2%   selected  45.2%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
random     N=4   ceiling  54.0%   selected  52.5%   gap  1.5 pts   capture  97.2%
random     N=8   ceiling  63.5%   selected  59.5%   gap  4.0 pts   capture  93.7%
random     N=16  ceiling  75.0%   selected  69.0%   gap  6.0 pts   capture  92.0%

tourney    N=1   ceiling  44.5%   selected  44.5%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  46.2%   selected  46.2%   gap  0.0 pts   capture 100.0%
tourney    N=4   ceiling  57.5%   selected  56.0%   gap  1.5 pts   capture  97.4%
tourney    N=8   ceiling  65.0%   selected  62.5%   gap  2.5 pts   capture  96.2%
tourney    N=16  ceiling  72.0%   selected  68.0%   gap  4.0 pts   capture  94.4%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = +1.8 pts   naive 95% CI [-2.4, +5.9]   cluster 95% CI [-2.4, +5.9]   deff 1.02   b/c 39/32   McNemar p = 0.477   clustered p = 0.413
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 65%
                                   non-inferiority (margin 5 pts): lower bound -2.4 -> NON-INFERIOR   one-sided p = 0.000803
                                   tokens 6106 vs 5889  (+3.7%, 95% CI [-1.6%, +9.0%])
N=2   rank - random                d = +1.0 pts   naive 95% CI [-3.4, +5.4]   cluster 95% CI [-3.6, +5.6]   deff 1.04   b/c 43/39   McNemar p = 0.741   clustered p = 0.668
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 57%
                                   non-inferiority (margin 5 pts): lower bound -3.6 -> NON-INFERIOR   one-sided p = 0.00498
                                   tokens 6889 vs 6927  (-0.5%, 95% CI [-5.6%, +4.5%])
N=4   rank - random                d = +1.8 pts   naive 95% CI [-2.4, +5.9]   cluster 95% CI [-1.8, +5.3]   deff 0.74   b/c 39/32   McNemar p = 0.477   clustered p = 0.336
                                   power: MDE(80%) 5.1 pts   power to detect 5 pts = 78%
                                   non-inferiority (margin 5 pts): lower bound -1.8 -> NON-INFERIOR   one-sided p = 0.000105
                                   tokens 14284 vs 14310  (-0.2%, 95% CI [-3.5%, +3.1%])
N=8   rank - random                d = +3.0 pts   naive 95% CI [-2.5, +8.5]   cluster 95% CI [-3.2, +9.2]   deff 1.24   b/c 19/13   McNemar p = 0.377   clustered p = 0.343
                                   power: MDE(80%) 8.9 pts   power to detect 5 pts = 35%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -3.2 -> NON-INFERIOR   one-sided p = 0.00573
                                   tokens 27529 vs 28314  (-2.8%, 95% CI [-6.2%, +0.6%])
N=16  rank - random                d = +6.0 pts   naive 95% CI [-1.8, +13.8]   cluster 95% CI [-1.8, +13.8]   deff 0.99   b/c 11/5   McNemar p = 0.21   clustered p = 0.131
                                   power: MDE(80%) 11.1 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -1.8 -> NON-INFERIOR   one-sided p = 0.00282
                                   tokens 52407 vs 55328  (-5.3%, 95% CI [-8.3%, -2.3%])

N=1   rank - baseline              d = -0.5 pts   naive 95% CI [-4.7, +3.7]   cluster 95% CI [-4.5, +3.5]   deff 0.89   b/c 36/38   McNemar p = 0.908   clustered p = 0.806
                                   power: MDE(80%) 5.7 pts   power to detect 5 pts = 69%
                                   non-inferiority (margin 5 pts): lower bound -4.5 -> NON-INFERIOR   one-sided p = 0.0137
                                   tokens 6106 vs 8417  (-27.5%, 95% CI [-31.7%, -23.2%])
N=2   rank - baseline              d = -6.0 pts   naive 95% CI [-9.9, -2.1]   cluster 95% CI [-9.6, -2.4]   deff 0.86   b/c 20/44   McNemar p = 0.00369   clustered p = 0.00119
                                   power: MDE(80%) 5.2 pts   power to detect 5 pts = 77%
                                   non-inferiority (margin 5 pts): lower bound -9.6 -> cannot claim parity   one-sided p = 0.706
                                   tokens 6889 vs 17179  (-59.9%, 95% CI [-62.2%, -57.6%])
N=4   rank - baseline              d = -8.8 pts   naive 95% CI [-13.0, -4.5]   cluster 95% CI [-13.4, -4.1]   deff 1.17   b/c 22/57   McNemar p = 0.000103   clustered p = 0.000219
                                   power: MDE(80%) 6.6 pts   power to detect 5 pts = 56%
                                   non-inferiority (margin 5 pts): lower bound -13.4 -> cannot claim parity   one-sided p = 0.943
                                   tokens 14284 vs 34192  (-58.2%, 95% CI [-60.1%, -56.3%])
N=8   rank - baseline              d = -7.0 pts   naive 95% CI [-12.6, -1.4]   cluster 95% CI [-12.9, -1.1]   deff 1.09   b/c 10/24   McNemar p = 0.0243   clustered p = 0.0203
                                   power: MDE(80%) 8.5 pts   power to detect 5 pts = 38%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -12.9 -> cannot claim parity   one-sided p = 0.746
                                   tokens 27529 vs 67682  (-59.3%, 95% CI [-61.2%, -57.4%])
N=16  rank - baseline              d = +5.0 pts   naive 95% CI [-2.0, +12.0]   cluster 95% CI [-2.0, +12.0]   deff 0.99   b/c 9/4   McNemar p = 0.267   clustered p = 0.164
                                   power: MDE(80%) 10.1 pts   power to detect 5 pts = 29%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -2.0 -> NON-INFERIOR   one-sided p = 0.00266
                                   tokens 52407 vs 133659  (-60.8%, 95% CI [-62.5%, -59.0%])

N=1   tourney - baseline           d = -3.0 pts   naive 95% CI [-7.3, +1.3]   cluster 95% CI [-7.7, +1.7]   deff 1.19   b/c 32/44   McNemar p = 0.207   clustered p = 0.21
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
                                   non-inferiority (margin 5 pts): lower bound -7.7 -> cannot claim parity   one-sided p = 0.201
                                   tokens 6076 vs 8417  (-27.8%, 95% CI [-32.9%, -22.7%])
N=2   tourney - baseline           d = -8.2 pts   naive 95% CI [-12.2, -4.3]   cluster 95% CI [-12.3, -4.2]   deff 1.06   b/c 17/50   McNemar p = 6.74e-05   clustered p = 6.93e-05
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 67%
                                   non-inferiority (margin 5 pts): lower bound -12.3 -> cannot claim parity   one-sided p = 0.941
                                   tokens 6896 vs 17179  (-59.9%, 95% CI [-62.1%, -57.6%])
N=4   tourney - baseline           d = -7.0 pts   naive 95% CI [-11.1, -2.9]   cluster 95% CI [-11.5, -2.5]   deff 1.17   b/c 22/50   McNemar p = 0.00129   clustered p = 0.00212
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 59%
                                   non-inferiority (margin 5 pts): lower bound -11.5 -> cannot claim parity   one-sided p = 0.81
                                   tokens 13991 vs 34192  (-59.1%, 95% CI [-60.9%, -57.3%])
N=8   tourney - baseline           d = -7.0 pts   naive 95% CI [-12.3, -1.7]   cluster 95% CI [-12.7, -1.3]   deff 1.17   b/c 8/22   McNemar p = 0.0161   clustered p = 0.017
                                   power: MDE(80%) 8.2 pts   power to detect 5 pts = 40%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -12.7 -> cannot claim parity   one-sided p = 0.752
                                   tokens 27580 vs 67682  (-59.3%, 95% CI [-61.2%, -57.3%])
N=16  tourney - baseline           d = -2.0 pts   naive 95% CI [-9.9, +5.9]   cluster 95% CI [-9.9, +5.9]   deff 0.99   b/c 7/9   McNemar p = 0.804   clustered p = 0.618
                                   power: MDE(80%) 11.2 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -9.9 -> cannot claim parity   one-sided p = 0.227
                                   tokens 55450 vs 133659  (-58.5%, 95% CI [-60.5%, -56.5%])

N=1   random - baseline            d = -2.2 pts   naive 95% CI [-6.8, +2.3]   cluster 95% CI [-7.0, +2.5]   deff 1.08   b/c 38/47   McNemar p = 0.386   clustered p = 0.351
                                   power: MDE(80%) 6.8 pts   power to detect 5 pts = 54%
                                   non-inferiority (margin 5 pts): lower bound -7.0 -> cannot claim parity   one-sided p = 0.127
                                   tokens 5889 vs 8417  (-30.0%, 95% CI [-34.7%, -25.4%])
N=2   random - baseline            d = -7.0 pts   naive 95% CI [-11.4, -2.6]   cluster 95% CI [-11.8, -2.2]   deff 1.14   b/c 28/56   McNemar p = 0.00299   clustered p = 0.00409
                                   power: MDE(80%) 6.8 pts   power to detect 5 pts = 54%
                                   non-inferiority (margin 5 pts): lower bound -11.8 -> cannot claim parity   one-sided p = 0.794
                                   tokens 6927 vs 17179  (-59.7%, 95% CI [-62.1%, -57.2%])
N=4   random - baseline            d = -10.5 pts   naive 95% CI [-14.8, -6.2]   cluster 95% CI [-15.2, -5.8]   deff 1.16   b/c 20/62   McNemar p = 3.71e-06   clustered p = 1.1e-05
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
                                   non-inferiority (margin 5 pts): lower bound -15.2 -> cannot claim parity   one-sided p = 0.989
                                   tokens 14310 vs 34192  (-58.1%, 95% CI [-60.2%, -56.1%])
N=8   random - baseline            d = -10.0 pts   naive 95% CI [-15.6, -4.4]   cluster 95% CI [-16.1, -3.9]   deff 1.18   b/c 7/27   McNemar p = 0.000821   clustered p = 0.00125
                                   power: MDE(80%) 8.7 pts   power to detect 5 pts = 36%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -16.1 -> cannot claim parity   one-sided p = 0.947
                                   tokens 28314 vs 67682  (-58.2%, 95% CI [-60.3%, -56.0%])
N=16  random - baseline            d = -1.0 pts   naive 95% CI [-8.6, +6.6]   cluster 95% CI [-8.6, +6.6]   deff 0.99   b/c 7/8   McNemar p = 1   clustered p = 0.797
                                   power: MDE(80%) 10.9 pts   power to detect 5 pts = 25%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -8.6 -> cannot claim parity   one-sided p = 0.152
                                   tokens 55328 vs 133659  (-58.6%, 95% CI [-60.6%, -56.6%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = +2.0 pts   naive 95% CI [-0.2, +4.2]   cluster 95% CI [-0.2, +4.2]   deff 1.02   b/c 151/121   McNemar p = 0.0785   clustered p = 0.0729
                                   power: MDE(80%) 3.1 pts   power to detect 5 pts = 99%
                                   equal-weight per N: d = +2.7 pts (from 5 cells: +1.8, +1.0, +1.8, +3.0, +6.0)

pooled rank - baseline (chunk-wtd) d = -4.7 pts   naive 95% CI [-6.8, -2.6]   cluster 95% CI [-7.3, -2.0]   deff 1.57   b/c 97/167   McNemar p = 1.95e-05   clustered p = 0.000573
                                   power: MDE(80%) 3.8 pts   power to detect 5 pts = 96%
                                   equal-weight per N: d = -3.4 pts (from 5 cells: -0.5, -6.0, -8.8, -7.0, +5.0)

pooled tourney - baseline (chunk-wtd) d = -5.9 pts   naive 95% CI [-8.0, -3.8]   cluster 95% CI [-8.6, -3.2]   deff 1.65   b/c 86/175   McNemar p = 3.82e-08   clustered p = 1.62e-05
                                   power: MDE(80%) 3.9 pts   power to detect 5 pts = 95%
                                   equal-weight per N: d = -5.5 pts (from 5 cells: -3.0, -8.2, -7.0, -7.0, -2.0)

pooled random - baseline (chunk-wtd) d = -6.7 pts   naive 95% CI [-8.9, -4.4]   cluster 95% CI [-9.8, -3.5]   deff 1.97   b/c 100/200   McNemar p = 8.01e-09   clustered p = 3.49e-05
                                   power: MDE(80%) 4.5 pts   power to detect 5 pts = 87%
                                   equal-weight per N: d = -6.2 pts (from 5 cells: -2.2, -7.0, -10.5, -10.0, -1.0)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = -0.5 pts   95% CI [-4.5, +3.5]   win/loss 16/21   p = 0.806   sign p = 0.511
                                   tokens 6106 vs 8417 (-27.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.5 -> NON-INFERIOR   one-sided p = 0.0137
                                   WARNING: -27% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.7 pts   power to detect 5 pts = 69%
rank N=2 vs baseline N=1           d = +1.0 pts   95% CI [-2.5, +4.5]   win/loss 19/16   p = 0.58   sign p = 0.736
                                   tokens 6889 vs 8417 (-18.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.5 -> NON-INFERIOR   one-sided p = 0.000456
                                   WARNING: -18% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.1 pts   power to detect 5 pts = 79%
rank N=4 vs baseline N=2           d = -0.2 pts   95% CI [-4.1, +3.6]   win/loss 20/17   p = 0.899   sign p = 0.743
                                   tokens 14284 vs 17179 (-16.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.1 -> NON-INFERIOR   one-sided p = 0.00775
                                   WARNING: -17% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 72%
rank N=8 vs baseline N=4           d = -0.5 pts   95% CI [-6.4, +5.4]   win/loss 20/18   p = 0.869   sign p = 0.871
                                   tokens 27529 vs 34192 (-19.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -6.4 -> cannot claim parity   one-sided p = 0.0691
                                   WARNING: -19% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 8.5 pts   power to detect 5 pts = 38%   <- underpowered
rank N=16 vs baseline N=8          d = +5.5 pts   95% CI [-0.6, +11.6]   win/loss 15/6   p = 0.075   sign p = 0.0784
                                   tokens 52407 vs 67682 (-22.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -0.6 -> NON-INFERIOR   one-sided p = 0.000338
                                   WARNING: -23% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 8.7 pts   power to detect 5 pts = 37%   <- underpowered

random N=1 vs baseline N=1         d = -2.2 pts   95% CI [-7.0, +2.5]   win/loss 18/21   p = 0.351   sign p = 0.749
                                   tokens 5889 vs 8417 (-30.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -7.0 -> cannot claim parity   one-sided p = 0.127
                                   WARNING: -30% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.8 pts   power to detect 5 pts = 54%
random N=2 vs baseline N=1         d = +0.0 pts   95% CI [-4.9, +4.9]   win/loss 23/21   p = 1   sign p = 0.88
                                   tokens 6927 vs 8417 (-17.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.9 -> NON-INFERIOR   one-sided p = 0.0233
                                   WARNING: -18% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 7.0 pts   power to detect 5 pts = 51%
random N=4 vs baseline N=2         d = -2.0 pts   95% CI [-5.5, +1.5]   win/loss 16/21   p = 0.267   sign p = 0.511
                                   tokens 14310 vs 17179 (-16.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.5 -> cannot claim parity   one-sided p = 0.0479
                                   WARNING: -17% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.0 pts   power to detect 5 pts = 79%
random N=8 vs baseline N=4         d = -3.5 pts   95% CI [-8.1, +1.1]   win/loss 14/21   p = 0.138   sign p = 0.311
                                   tokens 28314 vs 34192 (-17.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -8.1 -> cannot claim parity   one-sided p = 0.262
                                   WARNING: -17% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.6 pts   power to detect 5 pts = 56%
random N=16 vs baseline N=8        d = -0.5 pts   95% CI [-6.7, +5.7]   win/loss 11/10   p = 0.873   sign p = 1
                                   tokens 55328 vs 67682 (-18.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -6.7 -> cannot claim parity   one-sided p = 0.0758
                                   WARNING: -18% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 8.8 pts   power to detect 5 pts = 36%   <- underpowered

tourney N=1 vs baseline N=1        d = -3.0 pts   95% CI [-7.7, +1.7]   win/loss 15/22   p = 0.21   sign p = 0.324
                                   tokens 6076 vs 8417 (-27.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -7.7 -> cannot claim parity   one-sided p = 0.201
                                   WARNING: -28% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
tourney N=2 vs baseline N=1        d = -1.2 pts   95% CI [-5.5, +3.0]   win/loss 19/25   p = 0.56   sign p = 0.451
                                   tokens 6896 vs 8417 (-18.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.5 -> cannot claim parity   one-sided p = 0.0401
                                   WARNING: -18% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 65%
tourney N=4 vs baseline N=2        d = +1.5 pts   95% CI [-2.5, +5.5]   win/loss 19/18   p = 0.461   sign p = 1
                                   tokens 13991 vs 17179 (-18.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.5 -> NON-INFERIOR   one-sided p = 0.000704
                                   WARNING: -19% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.7 pts   power to detect 5 pts = 69%
tourney N=8 vs baseline N=4        d = -0.5 pts   95% CI [-5.1, +4.1]   win/loss 16/18   p = 0.83   sign p = 0.864
                                   tokens 27580 vs 34192 (-19.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.1 -> cannot claim parity   one-sided p = 0.0267
                                   WARNING: -19% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 57%
tourney N=16 vs baseline N=8       d = -1.5 pts   95% CI [-6.2, +3.2]   win/loss 7/10   p = 0.533   sign p = 0.629
                                   tokens 55450 vs 67682 (-18.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -6.2 -> cannot claim parity   one-sided p = 0.0728
                                   WARNING: -18% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

############################################################################################################
# CONFIG  plan=1000  prune=3.0
############################################################################################################
============================================================================================================
FILES
  baseline  2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json
  random    2026-07-18_19-18-01_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_3.0.json
  rank      2026-07-18_19-17-17_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_3.0.json
  tourney   2026-07-18_19-18-45_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_3.0.json
  N values: [1, 2, 4, 8, 16]

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16
baseline      47.5%   8417t    54.5%  17179t    63.0%  34192t    69.5%  67682t    70.0% 133659t
rank          46.0%   6132t    46.2%   6856t    46.5%   9037t    55.0%  17204t    65.0%  38015t
random        45.0%   6129t    44.5%   6967t    46.8%   8758t    53.5%  17896t    66.0%  40614t
tourney       45.0%   6035t    46.5%   7046t    47.2%   9308t    56.0%  18282t    63.0%  41085t

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
rank N=2: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=4: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=8: judge - random           d = +6.0 pts   naive 95% CI [+2.7, +9.3]   cluster 95% CI [+2.5, +9.5]   deff 1.11   b/c 12/0   McNemar p = 0.000488   clustered p = 0.000754
                                   power: MDE(80%) 5.0 pts   power to detect 5 pts = 80%
rank N=16: judge - random          d = +14.0 pts   naive 95% CI [+6.1, +21.9]   cluster 95% CI [+6.1, +21.9]   deff 0.99   b/c 16/2   McNemar p = 0.00131   clustered p = 0.000505
                                   power: MDE(80%) 11.3 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=4: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=8: judge - random         d = +13.5 pts   naive 95% CI [+8.6, +18.4]   cluster 95% CI [+8.7, +18.3]   deff 0.93   b/c 28/1   McNemar p = 1.12e-07   clustered p = 3.45e-08
                                   power: MDE(80%) 6.9 pts   power to detect 5 pts = 53%
random N=16: judge - random        d = +22.0 pts   naive 95% CI [+12.9, +31.1]   cluster 95% CI [+12.9, +31.1]   deff 0.99   b/c 24/2   McNemar p = 1.05e-05   clustered p = 1.95e-06
                                   power: MDE(80%) 13.0 pts   power to detect 5 pts = 19%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=4: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=8: judge - random        d = +5.0 pts   naive 95% CI [+0.9, +9.1]   cluster 95% CI [+0.7, +9.3]   deff 1.08   b/c 14/4   McNemar p = 0.0309   clustered p = 0.0225
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
tourney N=16: judge - random       d = +18.0 pts   naive 95% CI [+9.9, +26.1]   cluster 95% CI [+9.9, +26.1]   deff 0.99   b/c 19/1   McNemar p = 4.01e-05   clustered p = 1.22e-05
                                   power: MDE(80%) 11.5 pts   power to detect 5 pts = 23%   <- underpowered; a null here is NOT evidence of no effect

============================================================================================================
3. ORACLE CEILING   (a correct candidate EXISTS vs the judge FINDS it)
   NOTE: for pruned arms this is pass@k over SURVIVORS, not over all N.
   Only the baseline row is a clean best-of-N ceiling.

baseline   N=1   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
baseline   N=2   ceiling  57.0%   selected  54.5%   gap  2.5 pts   capture  95.6%
baseline   N=4   ceiling  66.2%   selected  63.0%   gap  3.2 pts   capture  95.1%
baseline   N=8   ceiling  73.5%   selected  69.5%   gap  4.0 pts   capture  94.6%
baseline   N=16  ceiling  79.0%   selected  70.0%   gap  9.0 pts   capture  88.6%

rank       N=1   ceiling  46.0%   selected  46.0%   gap  0.0 pts   capture 100.0%
rank       N=2   ceiling  46.2%   selected  46.2%   gap  0.0 pts   capture 100.0%
rank       N=4   ceiling  46.5%   selected  46.5%   gap  0.0 pts   capture 100.0%
rank       N=8   ceiling  56.0%   selected  55.0%   gap  1.0 pts   capture  98.2%
rank       N=16  ceiling  68.0%   selected  65.0%   gap  3.0 pts   capture  95.6%

random     N=1   ceiling  45.0%   selected  45.0%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  44.5%   selected  44.5%   gap  0.0 pts   capture 100.0%
random     N=4   ceiling  46.8%   selected  46.8%   gap  0.0 pts   capture 100.0%
random     N=8   ceiling  56.0%   selected  53.5%   gap  2.5 pts   capture  95.5%
random     N=16  ceiling  68.0%   selected  66.0%   gap  2.0 pts   capture  97.1%

tourney    N=1   ceiling  45.0%   selected  45.0%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  46.5%   selected  46.5%   gap  0.0 pts   capture 100.0%
tourney    N=4   ceiling  47.2%   selected  47.2%   gap  0.0 pts   capture 100.0%
tourney    N=8   ceiling  58.5%   selected  56.0%   gap  2.5 pts   capture  95.7%
tourney    N=16  ceiling  68.0%   selected  63.0%   gap  5.0 pts   capture  92.6%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = +1.0 pts   naive 95% CI [-3.0, +5.0]   cluster 95% CI [-2.8, +4.8]   deff 0.88   b/c 36/32   McNemar p = 0.716   clustered p = 0.607
                                   power: MDE(80%) 5.4 pts   power to detect 5 pts = 73%
                                   non-inferiority (margin 5 pts): lower bound -2.8 -> NON-INFERIOR   one-sided p = 0.00101
                                   tokens 6132 vs 6129  (+0.0%, 95% CI [-4.7%, +4.8%])
N=2   rank - random                d = +1.8 pts   naive 95% CI [-2.5, +6.0]   cluster 95% CI [-2.7, +6.2]   deff 1.07   b/c 41/34   McNemar p = 0.489   clustered p = 0.438
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 60%
                                   non-inferiority (margin 5 pts): lower bound -2.7 -> NON-INFERIOR   one-sided p = 0.00138
                                   tokens 6856 vs 6967  (-1.6%, 95% CI [-6.0%, +2.8%])
N=4   rank - random                d = -0.2 pts   naive 95% CI [-4.9, +4.4]   cluster 95% CI [-4.8, +4.3]   deff 0.97   b/c 44/45   McNemar p = 1   clustered p = 0.915
                                   power: MDE(80%) 6.6 pts   power to detect 5 pts = 57%
                                   non-inferiority (margin 5 pts): lower bound -4.8 -> NON-INFERIOR   one-sided p = 0.0213
                                   tokens 9037 vs 8758  (+3.2%, 95% CI [-0.8%, +7.2%])
N=8   rank - random                d = +1.5 pts   naive 95% CI [-4.1, +7.1]   cluster 95% CI [-3.8, +6.8]   deff 0.87   b/c 18/15   McNemar p = 0.728   clustered p = 0.579
                                   power: MDE(80%) 7.6 pts   power to detect 5 pts = 46%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -3.8 -> NON-INFERIOR   one-sided p = 0.00807
                                   tokens 17204 vs 17896  (-3.9%, 95% CI [-7.4%, -0.3%])
N=16  rank - random                d = -1.0 pts   naive 95% CI [-8.6, +6.6]   cluster 95% CI [-8.6, +6.6]   deff 0.99   b/c 7/8   McNemar p = 1   clustered p = 0.797
                                   power: MDE(80%) 10.9 pts   power to detect 5 pts = 25%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -8.6 -> cannot claim parity   one-sided p = 0.152
                                   tokens 38015 vs 40614  (-6.4%, 95% CI [-9.9%, -2.9%])

N=1   rank - baseline              d = -1.5 pts   naive 95% CI [-5.8, +2.8]   cluster 95% CI [-5.7, +2.7]   deff 0.92   b/c 36/42   McNemar p = 0.572   clustered p = 0.481
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 65%
                                   non-inferiority (margin 5 pts): lower bound -5.7 -> cannot claim parity   one-sided p = 0.0499
                                   tokens 6132 vs 8417  (-27.2%, 95% CI [-31.5%, -22.8%])
N=2   rank - baseline              d = -8.2 pts   naive 95% CI [-12.2, -4.3]   cluster 95% CI [-12.3, -4.2]   deff 1.03   b/c 18/51   McNemar p = 8.77e-05   clustered p = 6.93e-05
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 67%
                                   non-inferiority (margin 5 pts): lower bound -12.3 -> cannot claim parity   one-sided p = 0.941
                                   tokens 6856 vs 17179  (-60.1%, 95% CI [-62.4%, -57.8%])
N=4   rank - baseline              d = -16.5 pts   naive 95% CI [-21.0, -12.0]   cluster 95% CI [-22.2, -10.8]   deff 1.58   b/c 15/81   McNemar p = 4.03e-12   clustered p = 1.48e-08
                                   power: MDE(80%) 8.2 pts   power to detect 5 pts = 40%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -22.2 -> cannot claim parity   one-sided p = 1
                                   tokens 9037 vs 34192  (-73.6%, 95% CI [-75.1%, -72.1%])
N=8   rank - baseline              d = -14.5 pts   naive 95% CI [-20.3, -8.7]   cluster 95% CI [-20.6, -8.4]   deff 1.10   b/c 5/34   McNemar p = 2.43e-06   clustered p = 3.4e-06
                                   power: MDE(80%) 8.7 pts   power to detect 5 pts = 36%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -20.6 -> cannot claim parity   one-sided p = 0.999
                                   tokens 17204 vs 67682  (-74.6%, 95% CI [-76.0%, -73.2%])
N=16  rank - baseline              d = -5.0 pts   naive 95% CI [-14.4, +4.4]   cluster 95% CI [-14.4, +4.4]   deff 0.99   b/c 9/14   McNemar p = 0.405   clustered p = 0.297
                                   power: MDE(80%) 13.4 pts   power to detect 5 pts = 18%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -14.4 -> cannot claim parity   one-sided p = 0.5
                                   tokens 38015 vs 133659  (-71.6%, 95% CI [-73.0%, -70.2%])

N=1   tourney - baseline           d = -2.5 pts   naive 95% CI [-6.9, +1.9]   cluster 95% CI [-6.9, +1.9]   deff 0.99   b/c 36/46   McNemar p = 0.32   clustered p = 0.269
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 60%
                                   non-inferiority (margin 5 pts): lower bound -6.9 -> cannot claim parity   one-sided p = 0.134
                                   tokens 6035 vs 8417  (-28.3%, 95% CI [-33.5%, -23.1%])
N=2   tourney - baseline           d = -8.0 pts   naive 95% CI [-11.9, -4.1]   cluster 95% CI [-12.4, -3.6]   deff 1.25   b/c 17/49   McNemar p = 0.000101   clustered p = 0.000364
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 61%
                                   non-inferiority (margin 5 pts): lower bound -12.4 -> cannot claim parity   one-sided p = 0.909
                                   tokens 7046 vs 17179  (-59.0%, 95% CI [-61.4%, -56.5%])
N=4   tourney - baseline           d = -15.8 pts   naive 95% CI [-20.2, -11.3]   cluster 95% CI [-21.2, -10.3]   deff 1.48   b/c 15/78   McNemar p = 1.94e-11   clustered p = 1.65e-08
                                   power: MDE(80%) 7.8 pts   power to detect 5 pts = 43%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -21.2 -> cannot claim parity   one-sided p = 1
                                   tokens 9308 vs 34192  (-72.8%, 95% CI [-74.3%, -71.2%])
N=8   tourney - baseline           d = -13.5 pts   naive 95% CI [-18.8, -8.2]   cluster 95% CI [-19.2, -7.8]   deff 1.14   b/c 3/30   McNemar p = 1.4e-06   clustered p = 3.71e-06
                                   power: MDE(80%) 8.2 pts   power to detect 5 pts = 40%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -19.2 -> cannot claim parity   one-sided p = 0.998
                                   tokens 18282 vs 67682  (-73.0%, 95% CI [-74.5%, -71.5%])
N=16  tourney - baseline           d = -7.0 pts   naive 95% CI [-15.5, +1.5]   cluster 95% CI [-15.5, +1.5]   deff 0.99   b/c 6/13   McNemar p = 0.167   clustered p = 0.105
                                   power: MDE(80%) 12.1 pts   power to detect 5 pts = 21%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -15.5 -> cannot claim parity   one-sided p = 0.678
                                   tokens 41085 vs 133659  (-69.3%, 95% CI [-70.9%, -67.6%])

N=1   random - baseline            d = -2.5 pts   naive 95% CI [-7.0, +2.0]   cluster 95% CI [-7.0, +2.0]   deff 0.99   b/c 38/48   McNemar p = 0.332   clustered p = 0.28
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 58%
                                   non-inferiority (margin 5 pts): lower bound -7.0 -> cannot claim parity   one-sided p = 0.14
                                   tokens 6129 vs 8417  (-27.2%, 95% CI [-32.0%, -22.4%])
N=2   random - baseline            d = -10.0 pts   naive 95% CI [-14.3, -5.7]   cluster 95% CI [-14.3, -5.7]   deff 1.00   b/c 21/61   McNemar p = 1.13e-05   clustered p = 6.59e-06
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
                                   non-inferiority (margin 5 pts): lower bound -14.3 -> cannot claim parity   one-sided p = 0.988
                                   tokens 6967 vs 17179  (-59.4%, 95% CI [-61.7%, -57.2%])
N=4   random - baseline            d = -16.2 pts   naive 95% CI [-20.9, -11.6]   cluster 95% CI [-21.5, -11.0]   deff 1.27   b/c 17/82   McNemar p = 2.18e-11   clustered p = 1.12e-09
                                   power: MDE(80%) 7.5 pts   power to detect 5 pts = 47%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -21.5 -> cannot claim parity   one-sided p = 1
                                   tokens 8758 vs 34192  (-74.4%, 95% CI [-75.9%, -72.9%])
N=8   random - baseline            d = -16.0 pts   naive 95% CI [-21.8, -10.2]   cluster 95% CI [-22.1, -9.9]   deff 1.08   b/c 4/36   McNemar p = 1.86e-07   clustered p = 2.2e-07
                                   power: MDE(80%) 8.7 pts   power to detect 5 pts = 37%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -22.1 -> cannot claim parity   one-sided p = 1
                                   tokens 17896 vs 67682  (-73.6%, 95% CI [-75.1%, -72.0%])
N=16  random - baseline            d = -4.0 pts   naive 95% CI [-12.3, +4.3]   cluster 95% CI [-12.3, +4.3]   deff 0.99   b/c 7/11   McNemar p = 0.481   clustered p = 0.346
                                   power: MDE(80%) 11.9 pts   power to detect 5 pts = 22%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -12.3 -> cannot claim parity   one-sided p = 0.407
                                   tokens 40614 vs 133659  (-69.6%, 95% CI [-71.3%, -67.9%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = +0.8 pts   naive 95% CI [-1.4, +3.0]   cluster 95% CI [-1.6, +3.2]   deff 1.17   b/c 146/134   McNemar p = 0.511   clustered p = 0.51
                                   power: MDE(80%) 3.4 pts   power to detect 5 pts = 98%
                                   equal-weight per N: d = +0.6 pts (from 5 cells: +1.0, +1.8, -0.2, +1.5, -1.0)

pooled rank - baseline (chunk-wtd) d = -9.3 pts   naive 95% CI [-11.5, -7.0]   cluster 95% CI [-12.4, -6.1]   deff 1.96   b/c 83/222   McNemar p = 8.59e-16   clustered p = 7.75e-09
                                   power: MDE(80%) 4.5 pts   power to detect 5 pts = 88%
                                   equal-weight per N: d = -9.2 pts (from 5 cells: -1.5, -8.2, -16.5, -14.5, -5.0)

pooled tourney - baseline (chunk-wtd) d = -9.3 pts   naive 95% CI [-11.5, -7.1]   cluster 95% CI [-12.6, -5.9]   deff 2.31   b/c 77/216   McNemar p = 2e-16   clustered p = 5.51e-08
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 83%
                                   equal-weight per N: d = -9.3 pts (from 5 cells: -2.5, -8.0, -15.8, -13.5, -7.0)

pooled random - baseline (chunk-wtd) d = -10.1 pts   naive 95% CI [-12.4, -7.8]   cluster 95% CI [-13.2, -7.0]   deff 1.78   b/c 87/238   McNemar p = 2.28e-17   clustered p = 1.67e-10
                                   power: MDE(80%) 4.4 pts   power to detect 5 pts = 89%
                                   equal-weight per N: d = -9.8 pts (from 5 cells: -2.5, -10.0, -16.2, -16.0, -4.0)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = -1.5 pts   95% CI [-5.7, +2.7]   win/loss 16/21   p = 0.481   sign p = 0.511
                                   tokens 6132 vs 8417 (-27.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.7 -> cannot claim parity   one-sided p = 0.0499
                                   WARNING: -27% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 65%
rank N=2 vs baseline N=1           d = -1.2 pts   95% CI [-5.4, +2.9]   win/loss 15/22   p = 0.554   sign p = 0.324
                                   tokens 6856 vs 8417 (-18.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.4 -> cannot claim parity   one-sided p = 0.038
                                   WARNING: -19% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
rank N=4 vs baseline N=1           d = -1.0 pts   95% CI [-5.6, +3.6]   win/loss 23/25   p = 0.668   sign p = 0.885
                                   tokens 9037 vs 8417 (+7.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.6 -> cannot claim parity   one-sided p = 0.0429
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 57%
rank N=8 vs baseline N=2           d = +0.5 pts   95% CI [-4.6, +5.6]   win/loss 22/14   p = 0.847   sign p = 0.243
                                   tokens 17204 vs 17179 (+0.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.6 -> NON-INFERIOR   one-sided p = 0.0167
                                   power: MDE(80%) 7.2 pts   power to detect 5 pts = 49%   <- underpowered
rank N=16 vs baseline N=4          d = +2.0 pts   95% CI [-4.5, +8.5]   win/loss 19/17   p = 0.545   sign p = 0.868
                                   tokens 38015 vs 34192 (+11.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.5 -> NON-INFERIOR   one-sided p = 0.0172
                                   power: MDE(80%) 9.3 pts   power to detect 5 pts = 33%   <- underpowered

random N=1 vs baseline N=1         d = -2.5 pts   95% CI [-7.0, +2.0]   win/loss 20/24   p = 0.28   sign p = 0.652
                                   tokens 6129 vs 8417 (-27.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -7.0 -> cannot claim parity   one-sided p = 0.14
                                   WARNING: -27% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 58%
random N=2 vs baseline N=1         d = -3.0 pts   95% CI [-7.2, +1.2]   win/loss 14/20   p = 0.161   sign p = 0.392
                                   tokens 6967 vs 8417 (-17.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -7.2 -> cannot claim parity   one-sided p = 0.175
                                   WARNING: -17% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 65%
random N=4 vs baseline N=1         d = -0.8 pts   95% CI [-4.4, +2.9]   win/loss 20/20   p = 0.687   sign p = 1
                                   tokens 8758 vs 8417 (+4.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.4 -> NON-INFERIOR   one-sided p = 0.0112
                                   power: MDE(80%) 5.2 pts   power to detect 5 pts = 77%
random N=8 vs baseline N=2         d = -1.0 pts   95% CI [-5.6, +3.6]   win/loss 19/18   p = 0.668   sign p = 1
                                   tokens 17896 vs 17179 (+4.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.6 -> cannot claim parity   one-sided p = 0.0429
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 57%
random N=16 vs baseline N=4        d = +3.0 pts   95% CI [-3.5, +9.5]   win/loss 21/15   p = 0.363   sign p = 0.405
                                   tokens 40614 vs 34192 (+18.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.5 -> NON-INFERIOR   one-sided p = 0.00768
                                   WARNING: +19% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 9.2 pts   power to detect 5 pts = 33%   <- underpowered

tourney N=1 vs baseline N=1        d = -2.5 pts   95% CI [-6.9, +1.9]   win/loss 17/24   p = 0.269   sign p = 0.349
                                   tokens 6035 vs 8417 (-28.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -6.9 -> cannot claim parity   one-sided p = 0.134
                                   WARNING: -28% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 60%
tourney N=2 vs baseline N=1        d = -1.0 pts   95% CI [-5.2, +3.2]   win/loss 18/20   p = 0.639   sign p = 0.871
                                   tokens 7046 vs 8417 (-16.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.2 -> cannot claim parity   one-sided p = 0.0302
                                   WARNING: -16% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 65%
tourney N=4 vs baseline N=1        d = -0.2 pts   95% CI [-4.4, +3.9]   win/loss 15/20   p = 0.906   sign p = 0.5
                                   tokens 9308 vs 8417 (+10.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.4 -> NON-INFERIOR   one-sided p = 0.0124
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
tourney N=8 vs baseline N=2        d = +1.5 pts   95% CI [-3.7, +6.7]   win/loss 20/15   p = 0.569   sign p = 0.5
                                   tokens 18282 vs 17179 (+6.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.7 -> NON-INFERIOR   one-sided p = 0.00674
                                   power: MDE(80%) 7.4 pts   power to detect 5 pts = 48%   <- underpowered
tourney N=16 vs baseline N=4       d = +0.0 pts   95% CI [-7.6, +7.6]   win/loss 22/17   p = 1   sign p = 0.522
                                   tokens 41085 vs 34192 (+20.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -7.6 -> cannot claim parity   one-sided p = 0.0985
                                   WARNING: +20% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 10.9 pts   power to detect 5 pts = 25%   <- underpowered

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

############################################################################################################
# CONFIG  plan=1000  prune=4.0
############################################################################################################
============================================================================================================
FILES
  baseline  2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json
  random    2026-07-18_18-29-02_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_4.0.json
  rank      2026-07-18_18-28-18_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_4.0.json
  tourney   2026-07-18_18-29-45_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_4.0.json
  N values: [1, 2, 4, 8, 16]

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16
baseline      47.5%   8417t    54.5%  17179t    63.0%  34192t    69.5%  67682t    70.0% 133659t
rank          46.0%   6132t    45.8%   6933t    48.0%   8840t    57.0%  16992t    64.0%  33380t
random        45.0%   6039t    45.8%   7128t    45.0%   8854t    56.0%  17700t    58.0%  35916t
tourney       45.2%   5801t    46.0%   6926t    48.0%   9228t    57.0%  18469t    60.0%  37322t

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
rank N=2: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=4: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=8: judge - random           d = +5.5 pts   naive 95% CI [+2.3, +8.7]   cluster 95% CI [+2.1, +8.9]   deff 1.13   b/c 11/0   McNemar p = 0.000977   clustered p = 0.00143
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 83%
rank N=16: judge - random          d = +16.0 pts   naive 95% CI [+8.8, +23.2]   cluster 95% CI [+8.8, +23.2]   deff 0.99   b/c 16/0   McNemar p = 3.05e-05   clustered p = 1.41e-05
                                   power: MDE(80%) 10.3 pts   power to detect 5 pts = 27%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=4: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=8: judge - random         d = +9.5 pts   naive 95% CI [+5.4, +13.6]   cluster 95% CI [+5.6, +13.4]   deff 0.89   b/c 19/0   McNemar p = 3.81e-06   clustered p = 1.44e-06
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 72%
random N=16: judge - random        d = +15.0 pts   naive 95% CI [+6.9, +23.1]   cluster 95% CI [+6.9, +23.1]   deff 0.99   b/c 17/2   McNemar p = 0.000729   clustered p = 0.000266
                                   power: MDE(80%) 11.5 pts   power to detect 5 pts = 23%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=4: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=8: judge - random        d = +8.5 pts   naive 95% CI [+4.2, +12.8]   cluster 95% CI [+3.9, +13.1]   deff 1.13   b/c 19/2   McNemar p = 0.000221   clustered p = 0.000322
                                   power: MDE(80%) 6.6 pts   power to detect 5 pts = 56%
tourney N=16: judge - random       d = +11.0 pts   naive 95% CI [+3.2, +18.8]   cluster 95% CI [+3.2, +18.8]   deff 0.99   b/c 14/3   McNemar p = 0.0127   clustered p = 0.00588
                                   power: MDE(80%) 11.2 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect

============================================================================================================
3. ORACLE CEILING   (a correct candidate EXISTS vs the judge FINDS it)
   NOTE: for pruned arms this is pass@k over SURVIVORS, not over all N.
   Only the baseline row is a clean best-of-N ceiling.

baseline   N=1   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
baseline   N=2   ceiling  57.0%   selected  54.5%   gap  2.5 pts   capture  95.6%
baseline   N=4   ceiling  66.2%   selected  63.0%   gap  3.2 pts   capture  95.1%
baseline   N=8   ceiling  73.5%   selected  69.5%   gap  4.0 pts   capture  94.6%
baseline   N=16  ceiling  79.0%   selected  70.0%   gap  9.0 pts   capture  88.6%

rank       N=1   ceiling  46.0%   selected  46.0%   gap  0.0 pts   capture 100.0%
rank       N=2   ceiling  45.8%   selected  45.8%   gap  0.0 pts   capture 100.0%
rank       N=4   ceiling  48.0%   selected  48.0%   gap  0.0 pts   capture 100.0%
rank       N=8   ceiling  57.0%   selected  57.0%   gap  0.0 pts   capture 100.0%
rank       N=16  ceiling  66.0%   selected  64.0%   gap  2.0 pts   capture  97.0%

random     N=1   ceiling  45.0%   selected  45.0%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  45.8%   selected  45.8%   gap  0.0 pts   capture 100.0%
random     N=4   ceiling  45.0%   selected  45.0%   gap  0.0 pts   capture 100.0%
random     N=8   ceiling  57.0%   selected  56.0%   gap  1.0 pts   capture  98.2%
random     N=16  ceiling  62.0%   selected  58.0%   gap  4.0 pts   capture  93.5%

tourney    N=1   ceiling  45.2%   selected  45.2%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  46.0%   selected  46.0%   gap  0.0 pts   capture 100.0%
tourney    N=4   ceiling  48.0%   selected  48.0%   gap  0.0 pts   capture 100.0%
tourney    N=8   ceiling  58.5%   selected  57.0%   gap  1.5 pts   capture  97.4%
tourney    N=16  ceiling  63.0%   selected  60.0%   gap  3.0 pts   capture  95.2%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = +1.0 pts   naive 95% CI [-3.2, +5.2]   cluster 95% CI [-3.1, +5.1]   deff 0.94   b/c 38/34   McNemar p = 0.724   clustered p = 0.629
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 68%
                                   non-inferiority (margin 5 pts): lower bound -3.1 -> NON-INFERIOR   one-sided p = 0.00187
                                   tokens 6132 vs 6039  (+1.5%, 95% CI [-3.4%, +6.4%])
N=2   rank - random                d = +0.0 pts   naive 95% CI [-3.9, +3.9]   cluster 95% CI [-4.2, +4.2]   deff 1.15   b/c 32/32   McNemar p = 1   clustered p = 1
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 64%
                                   non-inferiority (margin 5 pts): lower bound -4.2 -> NON-INFERIOR   one-sided p = 0.0104
                                   tokens 6933 vs 7128  (-2.7%, 95% CI [-6.7%, +1.2%])
N=4   rank - random                d = +3.0 pts   naive 95% CI [-1.7, +7.7]   cluster 95% CI [-1.7, +7.7]   deff 0.96   b/c 53/41   McNemar p = 0.256   clustered p = 0.21
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
                                   non-inferiority (margin 5 pts): lower bound -1.7 -> NON-INFERIOR   one-sided p = 0.00041
                                   tokens 8840 vs 8854  (-0.2%, 95% CI [-3.8%, +3.4%])
N=8   rank - random                d = +1.0 pts   naive 95% CI [-5.1, +7.1]   cluster 95% CI [-5.5, +7.5]   deff 1.15   b/c 20/18   McNemar p = 0.871   clustered p = 0.764
                                   power: MDE(80%) 9.3 pts   power to detect 5 pts = 32%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -5.5 -> cannot claim parity   one-sided p = 0.0359
                                   tokens 16992 vs 17700  (-4.0%, 95% CI [-7.8%, -0.2%])
N=16  rank - random                d = +6.0 pts   naive 95% CI [-1.8, +13.8]   cluster 95% CI [-1.8, +13.8]   deff 0.99   b/c 11/5   McNemar p = 0.21   clustered p = 0.131
                                   power: MDE(80%) 11.1 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -1.8 -> NON-INFERIOR   one-sided p = 0.00282
                                   tokens 33380 vs 35916  (-7.1%, 95% CI [-10.7%, -3.5%])

N=1   rank - baseline              d = -1.5 pts   naive 95% CI [-5.8, +2.8]   cluster 95% CI [-5.7, +2.7]   deff 0.92   b/c 36/42   McNemar p = 0.572   clustered p = 0.481
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 65%
                                   non-inferiority (margin 5 pts): lower bound -5.7 -> cannot claim parity   one-sided p = 0.0499
                                   tokens 6132 vs 8417  (-27.2%, 95% CI [-31.5%, -22.8%])
N=2   rank - baseline              d = -8.8 pts   naive 95% CI [-13.0, -4.5]   cluster 95% CI [-13.1, -4.4]   deff 1.04   b/c 21/56   McNemar p = 8.22e-05   clustered p = 7.04e-05
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
                                   non-inferiority (margin 5 pts): lower bound -13.1 -> cannot claim parity   one-sided p = 0.956
                                   tokens 6933 vs 17179  (-59.6%, 95% CI [-61.9%, -57.4%])
N=4   rank - baseline              d = -15.0 pts   naive 95% CI [-19.4, -10.6]   cluster 95% CI [-20.3, -9.7]   deff 1.43   b/c 15/75   McNemar p = 9.18e-11   clustered p = 2.97e-08
                                   power: MDE(80%) 7.6 pts   power to detect 5 pts = 46%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -20.3 -> cannot claim parity   one-sided p = 1
                                   tokens 8840 vs 34192  (-74.1%, 95% CI [-75.6%, -72.7%])
N=8   rank - baseline              d = -12.5 pts   naive 95% CI [-18.2, -6.8]   cluster 95% CI [-18.9, -6.1]   deff 1.26   b/c 6/31   McNemar p = 4.13e-05   clustered p = 0.000142
                                   power: MDE(80%) 9.2 pts   power to detect 5 pts = 33%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -18.9 -> cannot claim parity   one-sided p = 0.989
                                   tokens 16992 vs 67682  (-74.9%, 95% CI [-76.3%, -73.5%])
N=16  rank - baseline              d = -6.0 pts   naive 95% CI [-14.7, +2.7]   cluster 95% CI [-14.7, +2.7]   deff 0.99   b/c 7/13   McNemar p = 0.263   clustered p = 0.178
                                   power: MDE(80%) 12.5 pts   power to detect 5 pts = 20%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -14.7 -> cannot claim parity   one-sided p = 0.589
                                   tokens 33380 vs 133659  (-75.0%, 95% CI [-76.5%, -73.6%])

N=1   tourney - baseline           d = -2.2 pts   naive 95% CI [-6.7, +2.2]   cluster 95% CI [-6.7, +2.2]   deff 0.99   b/c 37/46   McNemar p = 0.38   clustered p = 0.323
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 59%
                                   non-inferiority (margin 5 pts): lower bound -6.7 -> cannot claim parity   one-sided p = 0.114
                                   tokens 5801 vs 8417  (-31.1%, 95% CI [-35.8%, -26.3%])
N=2   tourney - baseline           d = -8.5 pts   naive 95% CI [-12.5, -4.5]   cluster 95% CI [-12.9, -4.1]   deff 1.17   b/c 18/52   McNemar p = 5.85e-05   clustered p = 0.000134
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 61%
                                   non-inferiority (margin 5 pts): lower bound -12.9 -> cannot claim parity   one-sided p = 0.942
                                   tokens 6926 vs 17179  (-59.7%, 95% CI [-61.8%, -57.6%])
N=4   tourney - baseline           d = -15.0 pts   naive 95% CI [-19.3, -10.7]   cluster 95% CI [-20.7, -9.3]   deff 1.71   b/c 13/73   McNemar p = 2.72e-11   clustered p = 2.03e-07
                                   power: MDE(80%) 8.1 pts   power to detect 5 pts = 41%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -20.7 -> cannot claim parity   one-sided p = 1
                                   tokens 9228 vs 34192  (-73.0%, 95% CI [-74.6%, -71.4%])
N=8   tourney - baseline           d = -12.5 pts   naive 95% CI [-18.5, -6.5]   cluster 95% CI [-18.8, -6.2]   deff 1.07   b/c 8/33   McNemar p = 0.000112   clustered p = 9.75e-05
                                   power: MDE(80%) 9.0 pts   power to detect 5 pts = 34%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -18.8 -> cannot claim parity   one-sided p = 0.99
                                   tokens 18469 vs 67682  (-72.7%, 95% CI [-74.4%, -71.1%])
N=16  tourney - baseline           d = -10.0 pts   naive 95% CI [-19.0, -1.0]   cluster 95% CI [-19.0, -1.0]   deff 0.99   b/c 6/16   McNemar p = 0.0525   clustered p = 0.0299
                                   power: MDE(80%) 12.9 pts   power to detect 5 pts = 19%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -19.0 -> cannot claim parity   one-sided p = 0.861
                                   tokens 37322 vs 133659  (-72.1%, 95% CI [-73.8%, -70.4%])

N=1   random - baseline            d = -2.5 pts   naive 95% CI [-7.0, +2.0]   cluster 95% CI [-6.9, +1.9]   deff 0.94   b/c 38/48   McNemar p = 0.332   clustered p = 0.269
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 60%
                                   non-inferiority (margin 5 pts): lower bound -6.9 -> cannot claim parity   one-sided p = 0.134
                                   tokens 6039 vs 8417  (-28.3%, 95% CI [-33.0%, -23.5%])
N=2   random - baseline            d = -8.8 pts   naive 95% CI [-13.0, -4.5]   cluster 95% CI [-12.8, -4.7]   deff 0.93   b/c 21/56   McNemar p = 8.22e-05   clustered p = 2.67e-05
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 67%
                                   non-inferiority (margin 5 pts): lower bound -12.8 -> cannot claim parity   one-sided p = 0.964
                                   tokens 7128 vs 17179  (-58.5%, 95% CI [-60.9%, -56.1%])
N=4   random - baseline            d = -18.0 pts   naive 95% CI [-22.6, -13.4]   cluster 95% CI [-23.0, -13.0]   deff 1.17   b/c 15/87   McNemar p = 1.65e-13   clustered p = 2.23e-12
                                   power: MDE(80%) 7.2 pts   power to detect 5 pts = 50%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -23.0 -> cannot claim parity   one-sided p = 1
                                   tokens 8854 vs 34192  (-74.1%, 95% CI [-75.6%, -72.6%])
N=8   random - baseline            d = -13.5 pts   naive 95% CI [-19.3, -7.7]   cluster 95% CI [-19.9, -7.1]   deff 1.17   b/c 6/33   McNemar p = 1.43e-05   clustered p = 3.19e-05
                                   power: MDE(80%) 9.1 pts   power to detect 5 pts = 34%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -19.9 -> cannot claim parity   one-sided p = 0.996
                                   tokens 17700 vs 67682  (-73.8%, 95% CI [-75.5%, -72.2%])
N=16  random - baseline            d = -12.0 pts   naive 95% CI [-20.9, -3.1]   cluster 95% CI [-20.9, -3.1]   deff 0.99   b/c 5/17   McNemar p = 0.0169   clustered p = 0.00846
                                   power: MDE(80%) 12.8 pts   power to detect 5 pts = 19%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -20.9 -> cannot claim parity   one-sided p = 0.938
                                   tokens 35916 vs 133659  (-73.1%, 95% CI [-74.7%, -71.6%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = +1.6 pts   naive 95% CI [-0.6, +3.8]   cluster 95% CI [-0.6, +3.8]   deff 1.02   b/c 154/130   McNemar p = 0.172   clustered p = 0.16
                                   power: MDE(80%) 3.2 pts   power to detect 5 pts = 99%
                                   equal-weight per N: d = +2.2 pts (from 5 cells: +1.0, +0.0, +3.0, +1.0, +6.0)

pooled rank - baseline (chunk-wtd) d = -8.8 pts   naive 95% CI [-11.0, -6.6]   cluster 95% CI [-12.0, -5.6]   deff 2.09   b/c 85/217   McNemar p = 1.82e-14   clustered p = 9.96e-08
                                   power: MDE(80%) 4.6 pts   power to detect 5 pts = 86%
                                   equal-weight per N: d = -8.8 pts (from 5 cells: -1.5, -8.8, -15.0, -12.5, -6.0)

pooled tourney - baseline (chunk-wtd) d = -9.2 pts   naive 95% CI [-11.4, -7.0]   cluster 95% CI [-12.7, -5.7]   deff 2.44   b/c 82/220   McNemar p = 9.95e-16   clustered p = 2.44e-07
                                   power: MDE(80%) 5.0 pts   power to detect 5 pts = 80%
                                   equal-weight per N: d = -9.7 pts (from 5 cells: -2.2, -8.5, -15.0, -12.5, -10.0)

pooled random - baseline (chunk-wtd) d = -10.4 pts   naive 95% CI [-12.7, -8.1]   cluster 95% CI [-13.3, -7.5]   deff 1.60   b/c 85/241   McNemar p = 1.97e-18   clustered p = 3.28e-12
                                   power: MDE(80%) 4.2 pts   power to detect 5 pts = 92%
                                   equal-weight per N: d = -10.9 pts (from 5 cells: -2.5, -8.8, -18.0, -13.5, -12.0)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = -1.5 pts   95% CI [-5.7, +2.7]   win/loss 16/21   p = 0.481   sign p = 0.511
                                   tokens 6132 vs 8417 (-27.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.7 -> cannot claim parity   one-sided p = 0.0499
                                   WARNING: -27% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 65%
rank N=2 vs baseline N=1           d = -1.8 pts   95% CI [-6.3, +2.8]   win/loss 20/24   p = 0.454   sign p = 0.652
                                   tokens 6933 vs 8417 (-17.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -6.3 -> cannot claim parity   one-sided p = 0.0822
                                   WARNING: -18% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 57%
rank N=4 vs baseline N=1           d = +0.5 pts   95% CI [-3.8, +4.8]   win/loss 18/18   p = 0.819   sign p = 1
                                   tokens 8840 vs 8417 (+5.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.8 -> NON-INFERIOR   one-sided p = 0.00601
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
rank N=8 vs baseline N=2           d = +2.5 pts   95% CI [-3.2, +8.2]   win/loss 23/16   p = 0.388   sign p = 0.337
                                   tokens 16992 vs 17179 (-1.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.2 -> NON-INFERIOR   one-sided p = 0.00482
                                   power: MDE(80%) 8.1 pts   power to detect 5 pts = 41%   <- underpowered
rank N=16 vs baseline N=4          d = +1.0 pts   95% CI [-5.6, +7.6]   win/loss 20/16   p = 0.768   sign p = 0.618
                                   tokens 33380 vs 34192 (-2.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.6 -> cannot claim parity   one-sided p = 0.0383
                                   power: MDE(80%) 9.5 pts   power to detect 5 pts = 31%   <- underpowered

random N=1 vs baseline N=1         d = -2.5 pts   95% CI [-6.9, +1.9]   win/loss 18/21   p = 0.269   sign p = 0.749
                                   tokens 6039 vs 8417 (-28.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -6.9 -> cannot claim parity   one-sided p = 0.134
                                   WARNING: -28% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 60%
random N=2 vs baseline N=1         d = -1.8 pts   95% CI [-5.8, +2.3]   win/loss 15/23   p = 0.393   sign p = 0.256
                                   tokens 7128 vs 8417 (-15.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.8 -> cannot claim parity   one-sided p = 0.0564
                                   WARNING: -15% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.7 pts   power to detect 5 pts = 68%
random N=4 vs baseline N=1         d = -2.5 pts   95% CI [-6.2, +1.2]   win/loss 15/21   p = 0.18   sign p = 0.405
                                   tokens 8854 vs 8417 (+5.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -6.2 -> cannot claim parity   one-sided p = 0.0899
                                   power: MDE(80%) 5.2 pts   power to detect 5 pts = 77%
random N=8 vs baseline N=2         d = +1.5 pts   95% CI [-3.3, +6.3]   win/loss 19/13   p = 0.537   sign p = 0.377
                                   tokens 17700 vs 17179 (+3.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.3 -> NON-INFERIOR   one-sided p = 0.00375
                                   power: MDE(80%) 6.8 pts   power to detect 5 pts = 54%
random N=16 vs baseline N=4        d = -5.0 pts   95% CI [-11.6, +1.6]   win/loss 16/22   p = 0.136   sign p = 0.418
                                   tokens 35916 vs 34192 (+5.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -11.6 -> cannot claim parity   one-sided p = 0.5
                                   power: MDE(80%) 9.4 pts   power to detect 5 pts = 32%   <- underpowered

tourney N=1 vs baseline N=1        d = -2.2 pts   95% CI [-6.7, +2.2]   win/loss 18/24   p = 0.323   sign p = 0.441
                                   tokens 5801 vs 8417 (-31.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -6.7 -> cannot claim parity   one-sided p = 0.114
                                   WARNING: -31% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 59%
tourney N=2 vs baseline N=1        d = -1.5 pts   95% CI [-6.0, +3.0]   win/loss 18/21   p = 0.514   sign p = 0.749
                                   tokens 6926 vs 8417 (-17.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -6.0 -> cannot claim parity   one-sided p = 0.0639
                                   WARNING: -18% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 59%
tourney N=4 vs baseline N=1        d = +0.5 pts   95% CI [-4.0, +5.0]   win/loss 21/20   p = 0.826   sign p = 1
                                   tokens 9228 vs 8417 (+9.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.0 -> NON-INFERIOR   one-sided p = 0.00781
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 59%
tourney N=8 vs baseline N=2        d = +2.5 pts   95% CI [-2.4, +7.4]   win/loss 22/13   p = 0.322   sign p = 0.175
                                   tokens 18469 vs 17179 (+7.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.4 -> NON-INFERIOR   one-sided p = 0.00149
                                   power: MDE(80%) 7.1 pts   power to detect 5 pts = 51%
tourney N=16 vs baseline N=4       d = -3.0 pts   95% CI [-8.7, +2.7]   win/loss 16/19   p = 0.3   sign p = 0.736
                                   tokens 37322 vs 34192 (+9.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -8.7 -> cannot claim parity   one-sided p = 0.245
                                   power: MDE(80%) 8.1 pts   power to detect 5 pts = 41%   <- underpowered

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

############################################################################################################
# CONFIG  plan=2500  prune=1.5
############################################################################################################
============================================================================================================
FILES
  baseline  2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json
  random    2026-07-19_05-49-06_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_1.5.json
  rank      2026-07-19_05-48-19_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_1.5.json
  tourney   2026-07-19_05-49-53_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_1.5.json
  N values: [1, 2, 4, 8, 16]

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16
baseline      47.5%   8417t    54.5%  17179t    63.0%  34192t    69.5%  67682t    70.0% 133659t
rank          50.0%   6110t    49.2%   7979t    55.5%  16330t    68.0%  35727t    76.0%  70448t
random        50.0%   5921t    46.2%   8212t    56.8%  16750t    64.5%  36447t    68.0%  73759t
tourney       48.8%   5963t    50.0%   8013t    59.2%  16036t    64.5%  35764t    70.0%  70080t

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
rank N=2: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=4: judge - random           d = +6.8 pts   naive 95% CI [+4.2, +9.3]   cluster 95% CI [+3.9, +9.6]   deff 1.24   b/c 28/1   McNemar p = 1.12e-07   clustered p = 3.71e-06
                                   power: MDE(80%) 4.1 pts   power to detect 5 pts = 93%
rank N=8: judge - random           d = +16.5 pts   naive 95% CI [+11.0, +22.0]   cluster 95% CI [+10.1, +22.9]   deff 1.33   b/c 35/2   McNemar p = 1.02e-08   clustered p = 4.2e-07
                                   power: MDE(80%) 9.1 pts   power to detect 5 pts = 33%   <- underpowered; a null here is NOT evidence of no effect
rank N=16: judge - random          d = +22.0 pts   naive 95% CI [+13.8, +30.2]   cluster 95% CI [+13.8, +30.2]   deff 0.99   b/c 22/0   McNemar p = 4.77e-07   clustered p = 1.26e-07
                                   power: MDE(80%) 11.7 pts   power to detect 5 pts = 22%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=4: judge - random         d = +6.8 pts   naive 95% CI [+3.8, +9.7]   cluster 95% CI [+3.8, +9.7]   deff 1.01   b/c 32/5   McNemar p = 7.43e-06   clustered p = 6.94e-06
                                   power: MDE(80%) 4.2 pts   power to detect 5 pts = 91%
random N=8: judge - random         d = +17.0 pts   naive 95% CI [+11.3, +22.7]   cluster 95% CI [+11.4, +22.6]   deff 0.94   b/c 37/3   McNemar p = 1.95e-08   clustered p = 2.86e-09
                                   power: MDE(80%) 8.0 pts   power to detect 5 pts = 42%   <- underpowered; a null here is NOT evidence of no effect
random N=16: judge - random        d = +24.0 pts   naive 95% CI [+15.1, +32.9]   cluster 95% CI [+15.1, +32.9]   deff 0.99   b/c 25/1   McNemar p = 8.05e-07   clustered p = 1.11e-07
                                   power: MDE(80%) 12.7 pts   power to detect 5 pts = 20%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=4: judge - random        d = +8.2 pts   naive 95% CI [+5.4, +11.1]   cluster 95% CI [+4.8, +11.7]   deff 1.46   b/c 35/2   McNemar p = 1.02e-08   clustered p = 3.51e-06
                                   power: MDE(80%) 5.0 pts   power to detect 5 pts = 80%
tourney N=8: judge - random        d = +15.5 pts   naive 95% CI [+10.3, +20.7]   cluster 95% CI [+10.2, +20.8]   deff 1.04   b/c 32/1   McNemar p = 7.92e-09   clustered p = 1.27e-08
                                   power: MDE(80%) 7.6 pts   power to detect 5 pts = 45%   <- underpowered; a null here is NOT evidence of no effect
tourney N=16: judge - random       d = +20.0 pts   naive 95% CI [+10.8, +29.2]   cluster 95% CI [+10.8, +29.2]   deff 0.99   b/c 23/3   McNemar p = 8.8e-05   clustered p = 2.21e-05
                                   power: MDE(80%) 13.2 pts   power to detect 5 pts = 18%   <- underpowered; a null here is NOT evidence of no effect

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
rank       N=2   ceiling  49.2%   selected  49.2%   gap  0.0 pts   capture 100.0%
rank       N=4   ceiling  56.8%   selected  55.5%   gap  1.2 pts   capture  97.8%
rank       N=8   ceiling  71.5%   selected  68.0%   gap  3.5 pts   capture  95.1%
rank       N=16  ceiling  80.0%   selected  76.0%   gap  4.0 pts   capture  95.0%

random     N=1   ceiling  50.0%   selected  50.0%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  46.2%   selected  46.2%   gap  0.0 pts   capture 100.0%
random     N=4   ceiling  58.2%   selected  56.8%   gap  1.5 pts   capture  97.4%
random     N=8   ceiling  68.0%   selected  64.5%   gap  3.5 pts   capture  94.9%
random     N=16  ceiling  72.0%   selected  68.0%   gap  4.0 pts   capture  94.4%

tourney    N=1   ceiling  48.8%   selected  48.8%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  50.0%   selected  50.0%   gap  0.0 pts   capture 100.0%
tourney    N=4   ceiling  60.2%   selected  59.2%   gap  1.0 pts   capture  98.3%
tourney    N=8   ceiling  67.5%   selected  64.5%   gap  3.0 pts   capture  95.6%
tourney    N=16  ceiling  74.0%   selected  70.0%   gap  4.0 pts   capture  94.6%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = +0.0 pts   naive 95% CI [-3.4, +3.4]   cluster 95% CI [-3.9, +3.9]   deff 1.33   b/c 24/24   McNemar p = 1   clustered p = 1
                                   power: MDE(80%) 5.6 pts   power to detect 5 pts = 70%
                                   non-inferiority (margin 5 pts): lower bound -3.9 -> NON-INFERIOR   one-sided p = 0.00643
                                   tokens 6110 vs 5921  (+3.2%, 95% CI [+0.0%, +6.3%])
N=2   rank - random                d = +3.0 pts   naive 95% CI [-0.9, +6.9]   cluster 95% CI [-0.7, +6.7]   deff 0.89   b/c 38/26   McNemar p = 0.169   clustered p = 0.112
                                   power: MDE(80%) 5.3 pts   power to detect 5 pts = 75%
                                   non-inferiority (margin 5 pts): lower bound -0.7 -> NON-INFERIOR   one-sided p = 1.15e-05
                                   tokens 7979 vs 8212  (-2.8%, 95% CI [-6.0%, +0.4%])
N=4   rank - random                d = -1.2 pts   naive 95% CI [-5.0, +2.5]   cluster 95% CI [-4.2, +1.7]   deff 0.62   b/c 27/32   McNemar p = 0.603   clustered p = 0.412
                                   power: MDE(80%) 4.3 pts   power to detect 5 pts = 91%
                                   non-inferiority (margin 5 pts): lower bound -4.2 -> NON-INFERIOR   one-sided p = 0.00691
                                   tokens 16330 vs 16750  (-2.5%, 95% CI [-4.7%, -0.3%])
N=8   rank - random                d = +3.5 pts   naive 95% CI [-1.2, +8.2]   cluster 95% CI [-1.4, +8.4]   deff 1.07   b/c 15/8   McNemar p = 0.21   clustered p = 0.159
                                   power: MDE(80%) 7.0 pts   power to detect 5 pts = 52%
                                   non-inferiority (margin 5 pts): lower bound -1.4 -> NON-INFERIOR   one-sided p = 0.000317
                                   tokens 35727 vs 36447  (-2.0%, 95% CI [-4.3%, +0.4%])
N=16  rank - random                d = +8.0 pts   naive 95% CI [+1.4, +14.6]   cluster 95% CI [+1.4, +14.6]   deff 0.99   b/c 10/2   McNemar p = 0.0386   clustered p = 0.0182
                                   power: MDE(80%) 9.5 pts   power to detect 5 pts = 31%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound +1.4 -> NON-INFERIOR   one-sided p = 6.21e-05
                                   tokens 70448 vs 73759  (-4.5%, 95% CI [-6.4%, -2.5%])

N=1   rank - baseline              d = +2.5 pts   naive 95% CI [-1.4, +6.4]   cluster 95% CI [-1.2, +6.2]   deff 0.92   b/c 36/26   McNemar p = 0.253   clustered p = 0.188
                                   power: MDE(80%) 5.3 pts   power to detect 5 pts = 75%
                                   non-inferiority (margin 5 pts): lower bound -1.2 -> NON-INFERIOR   one-sided p = 3.85e-05
                                   tokens 6110 vs 8417  (-27.4%, 95% CI [-31.5%, -23.4%])
N=2   rank - baseline              d = -5.2 pts   naive 95% CI [-8.9, -1.6]   cluster 95% CI [-9.4, -1.1]   deff 1.26   b/c 18/39   McNemar p = 0.00751   clustered p = 0.0129
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
                                   non-inferiority (margin 5 pts): lower bound -9.4 -> cannot claim parity   one-sided p = 0.547
                                   tokens 7979 vs 17179  (-53.6%, 95% CI [-55.8%, -51.3%])
N=4   rank - baseline              d = -7.5 pts   naive 95% CI [-11.5, -3.5]   cluster 95% CI [-12.2, -2.8]   deff 1.34   b/c 20/50   McNemar p = 0.00044   clustered p = 0.00175
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
                                   non-inferiority (margin 5 pts): lower bound -12.2 -> cannot claim parity   one-sided p = 0.852
                                   tokens 16330 vs 34192  (-52.2%, 95% CI [-54.3%, -50.2%])
N=8   rank - baseline              d = -1.5 pts   naive 95% CI [-6.6, +3.6]   cluster 95% CI [-6.4, +3.4]   deff 0.92   b/c 12/15   McNemar p = 0.701   clustered p = 0.55
                                   power: MDE(80%) 7.0 pts   power to detect 5 pts = 51%
                                   non-inferiority (margin 5 pts): lower bound -6.4 -> cannot claim parity   one-sided p = 0.0814
                                   tokens 35727 vs 67682  (-47.2%, 95% CI [-49.2%, -45.2%])
N=16  rank - baseline              d = +6.0 pts   naive 95% CI [-1.8, +13.8]   cluster 95% CI [-1.8, +13.8]   deff 0.99   b/c 11/5   McNemar p = 0.21   clustered p = 0.131
                                   power: MDE(80%) 11.1 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -1.8 -> NON-INFERIOR   one-sided p = 0.00282
                                   tokens 70448 vs 133659  (-47.3%, 95% CI [-49.5%, -45.1%])

N=1   tourney - baseline           d = +1.2 pts   naive 95% CI [-2.5, +5.0]   cluster 95% CI [-2.2, +4.7]   deff 0.83   b/c 32/27   McNemar p = 0.603   clustered p = 0.476
                                   power: MDE(80%) 4.9 pts   power to detect 5 pts = 81%
                                   non-inferiority (margin 5 pts): lower bound -2.2 -> NON-INFERIOR   one-sided p = 0.000184
                                   tokens 5963 vs 8417  (-29.2%, 95% CI [-33.3%, -25.0%])
N=2   tourney - baseline           d = -4.5 pts   naive 95% CI [-8.5, -0.5]   cluster 95% CI [-8.5, -0.5]   deff 0.99   b/c 24/42   McNemar p = 0.0356   clustered p = 0.026
                                   power: MDE(80%) 5.7 pts   power to detect 5 pts = 70%
                                   non-inferiority (margin 5 pts): lower bound -8.5 -> cannot claim parity   one-sided p = 0.402
                                   tokens 8013 vs 17179  (-53.4%, 95% CI [-55.7%, -51.0%])
N=4   tourney - baseline           d = -3.8 pts   naive 95% CI [-7.6, +0.1]   cluster 95% CI [-8.4, +0.9]   deff 1.42   b/c 24/39   McNemar p = 0.0769   clustered p = 0.113
                                   power: MDE(80%) 6.6 pts   power to detect 5 pts = 56%
                                   non-inferiority (margin 5 pts): lower bound -8.4 -> cannot claim parity   one-sided p = 0.299
                                   tokens 16036 vs 34192  (-53.1%, 95% CI [-55.1%, -51.1%])
N=8   tourney - baseline           d = -5.0 pts   naive 95% CI [-10.0, -0.0]   cluster 95% CI [-10.1, +0.1]   deff 1.05   b/c 8/18   McNemar p = 0.0755   clustered p = 0.0555
                                   power: MDE(80%) 7.3 pts   power to detect 5 pts = 48%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -10.1 -> cannot claim parity   one-sided p = 0.5
                                   tokens 35764 vs 67682  (-47.2%, 95% CI [-49.3%, -45.1%])
N=16  tourney - baseline           d = +0.0 pts   naive 95% CI [-8.4, +8.4]   cluster 95% CI [-8.4, +8.4]   deff 0.99   b/c 9/9   McNemar p = 1   clustered p = 1
                                   power: MDE(80%) 11.9 pts   power to detect 5 pts = 22%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -8.4 -> cannot claim parity   one-sided p = 0.12
                                   tokens 70080 vs 133659  (-47.6%, 95% CI [-49.6%, -45.5%])

N=1   random - baseline            d = +2.5 pts   naive 95% CI [-1.2, +6.2]   cluster 95% CI [-0.8, +5.8]   deff 0.78   b/c 34/24   McNemar p = 0.237   clustered p = 0.138
                                   power: MDE(80%) 4.7 pts   power to detect 5 pts = 84%
                                   non-inferiority (margin 5 pts): lower bound -0.8 -> NON-INFERIOR   one-sided p = 4.3e-06
                                   tokens 5921 vs 8417  (-29.7%, 95% CI [-33.6%, -25.7%])
N=2   random - baseline            d = -8.2 pts   naive 95% CI [-12.2, -4.3]   cluster 95% CI [-12.4, -4.1]   deff 1.09   b/c 18/51   McNemar p = 8.77e-05   clustered p = 0.00011
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 65%
                                   non-inferiority (margin 5 pts): lower bound -12.4 -> cannot claim parity   one-sided p = 0.936
                                   tokens 8212 vs 17179  (-52.2%, 95% CI [-54.9%, -49.5%])
N=4   random - baseline            d = -6.2 pts   naive 95% CI [-10.5, -2.0]   cluster 95% CI [-11.3, -1.2]   deff 1.42   b/c 25/50   McNemar p = 0.00523   clustered p = 0.0151
                                   power: MDE(80%) 7.2 pts   power to detect 5 pts = 49%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -11.3 -> cannot claim parity   one-sided p = 0.687
                                   tokens 16750 vs 34192  (-51.0%, 95% CI [-53.4%, -48.6%])
N=8   random - baseline            d = -5.0 pts   naive 95% CI [-10.2, +0.2]   cluster 95% CI [-10.1, +0.1]   deff 0.98   b/c 9/19   McNemar p = 0.0872   clustered p = 0.0555
                                   power: MDE(80%) 7.3 pts   power to detect 5 pts = 48%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -10.1 -> cannot claim parity   one-sided p = 0.5
                                   tokens 36447 vs 67682  (-46.1%, 95% CI [-48.6%, -43.7%])
N=16  random - baseline            d = -2.0 pts   naive 95% CI [-10.8, +6.8]   cluster 95% CI [-10.8, +6.8]   deff 0.99   b/c 9/11   McNemar p = 0.824   clustered p = 0.656
                                   power: MDE(80%) 12.6 pts   power to detect 5 pts = 20%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -10.8 -> cannot claim parity   one-sided p = 0.252
                                   tokens 73759 vs 133659  (-44.8%, 95% CI [-47.2%, -42.5%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = +1.5 pts   naive 95% CI [-0.4, +3.3]   cluster 95% CI [-0.5, +3.4]   deff 1.06   b/c 114/92   McNemar p = 0.143   clustered p = 0.139
                                   power: MDE(80%) 2.8 pts   power to detect 5 pts = 100%
                                   equal-weight per N: d = +2.7 pts (from 5 cells: +0.0, +3.0, -1.2, +3.5, +8.0)

pooled rank - baseline (chunk-wtd) d = -2.5 pts   naive 95% CI [-4.5, -0.5]   cluster 95% CI [-5.3, +0.2]   deff 1.88   b/c 97/135   McNemar p = 0.015   clustered p = 0.0694
                                   power: MDE(80%) 3.9 pts   power to detect 5 pts = 95%
                                   equal-weight per N: d = -1.1 pts (from 5 cells: +2.5, -5.2, -7.5, -1.5, +6.0)

pooled tourney - baseline (chunk-wtd) d = -2.5 pts   naive 95% CI [-4.5, -0.5]   cluster 95% CI [-5.2, +0.1]   deff 1.75   b/c 97/135   McNemar p = 0.015   clustered p = 0.0598
                                   power: MDE(80%) 3.8 pts   power to detect 5 pts = 96%
                                   equal-weight per N: d = -2.4 pts (from 5 cells: +1.2, -4.5, -3.8, -5.0, +0.0)

pooled random - baseline (chunk-wtd) d = -4.0 pts   naive 95% CI [-6.1, -1.9]   cluster 95% CI [-6.8, -1.2]   deff 1.81   b/c 95/155   McNemar p = 0.000178   clustered p = 0.00479
                                   power: MDE(80%) 4.0 pts   power to detect 5 pts = 94%
                                   equal-weight per N: d = -3.8 pts (from 5 cells: +2.5, -8.2, -6.2, -5.0, -2.0)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = +2.5 pts   95% CI [-1.2, +6.2]   win/loss 19/13   p = 0.188   sign p = 0.377
                                   tokens 6110 vs 8417 (-27.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.2 -> NON-INFERIOR   one-sided p = 3.85e-05
                                   WARNING: -27% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.3 pts   power to detect 5 pts = 75%
rank N=2 vs baseline N=1           d = +1.8 pts   95% CI [-2.4, +5.9]   win/loss 22/16   p = 0.413   sign p = 0.418
                                   tokens 7979 vs 8417 (-5.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.4 -> NON-INFERIOR   one-sided p = 0.000803
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 65%
rank N=4 vs baseline N=2           d = +1.0 pts   95% CI [-2.5, +4.5]   win/loss 17/12   p = 0.573   sign p = 0.458
                                   tokens 16330 vs 17179 (-4.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.5 -> NON-INFERIOR   one-sided p = 0.000359
                                   power: MDE(80%) 5.0 pts   power to detect 5 pts = 80%
rank N=8 vs baseline N=4           d = +5.0 pts   95% CI [+0.4, +9.6]   win/loss 23/12   p = 0.0319   sign p = 0.0895
                                   tokens 35727 vs 34192 (+4.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.4 -> NON-INFERIOR   one-sided p = 8.87e-06
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 57%
rank N=16 vs baseline N=8          d = +6.5 pts   95% CI [-0.1, +13.1]   win/loss 17/6   p = 0.0547   sign p = 0.0347
                                   tokens 70448 vs 67682 (+4.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -0.1 -> NON-INFERIOR   one-sided p = 0.000337
                                   power: MDE(80%) 9.5 pts   power to detect 5 pts = 31%   <- underpowered

random N=1 vs baseline N=1         d = +2.5 pts   95% CI [-0.8, +5.8]   win/loss 16/10   p = 0.138   sign p = 0.327
                                   tokens 5921 vs 8417 (-29.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -0.8 -> NON-INFERIOR   one-sided p = 4.3e-06
                                   WARNING: -30% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 4.7 pts   power to detect 5 pts = 84%
random N=2 vs baseline N=1         d = -1.2 pts   95% CI [-5.1, +2.6]   win/loss 18/22   p = 0.523   sign p = 0.636
                                   tokens 8212 vs 8417 (-2.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.1 -> cannot claim parity   one-sided p = 0.0278
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 72%
random N=4 vs baseline N=2         d = +2.2 pts   95% CI [-1.6, +6.1]   win/loss 21/14   p = 0.256   sign p = 0.311
                                   tokens 16750 vs 17179 (-2.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.6 -> NON-INFERIOR   one-sided p = 0.000127
                                   power: MDE(80%) 5.6 pts   power to detect 5 pts = 71%
random N=8 vs baseline N=4         d = +1.5 pts   95% CI [-3.1, +6.1]   win/loss 20/16   p = 0.519   sign p = 0.618
                                   tokens 36447 vs 34192 (+6.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.1 -> NON-INFERIOR   one-sided p = 0.00259
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 58%
random N=16 vs baseline N=8        d = -1.5 pts   95% CI [-8.2, +5.2]   win/loss 11/12   p = 0.663   sign p = 1
                                   tokens 73759 vs 67682 (+9.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -8.2 -> cannot claim parity   one-sided p = 0.155
                                   power: MDE(80%) 9.6 pts   power to detect 5 pts = 31%   <- underpowered

tourney N=1 vs baseline N=1        d = +1.2 pts   95% CI [-2.2, +4.7]   win/loss 17/15   p = 0.476   sign p = 0.86
                                   tokens 5963 vs 8417 (-29.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.2 -> NON-INFERIOR   one-sided p = 0.000184
                                   WARNING: -29% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 4.9 pts   power to detect 5 pts = 81%
tourney N=2 vs baseline N=1        d = +2.5 pts   95% CI [-1.3, +6.3]   win/loss 21/12   p = 0.203   sign p = 0.163
                                   tokens 8013 vs 8417 (-4.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.3 -> NON-INFERIOR   one-sided p = 6.62e-05
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 72%
tourney N=4 vs baseline N=2        d = +4.8 pts   95% CI [+0.6, +8.9]   win/loss 24/9   p = 0.0232   sign p = 0.0135
                                   tokens 16036 vs 17179 (-6.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.6 -> NON-INFERIOR   one-sided p = 1.59e-06
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 67%
tourney N=8 vs baseline N=4        d = +1.5 pts   95% CI [-3.2, +6.2]   win/loss 17/14   p = 0.528   sign p = 0.72
                                   tokens 35764 vs 34192 (+4.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.2 -> NON-INFERIOR   one-sided p = 0.00314
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 56%
tourney N=16 vs baseline N=8       d = +0.5 pts   95% CI [-5.7, +6.7]   win/loss 10/11   p = 0.873   sign p = 1
                                   tokens 70080 vs 67682 (+3.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.7 -> cannot claim parity   one-sided p = 0.0398
                                   power: MDE(80%) 8.8 pts   power to detect 5 pts = 36%   <- underpowered

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

############################################################################################################
# CONFIG  plan=2500  prune=2.0
############################################################################################################
============================================================================================================
FILES
  baseline  2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json
  random    2026-07-19_02-41-36_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_2.0.json
  rank      2026-07-19_02-40-50_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_2.0.json
  tourney   2026-07-19_02-42-22_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_2.0.json
  N values: [1, 2, 4, 8, 16]

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16
baseline      47.5%   8417t    54.5%  17179t    63.0%  34192t    69.5%  67682t    70.0% 133659t
rank          48.0%   6194t    49.5%   8001t    59.5%  16221t    67.0%  31058t    67.0%  62187t
random        47.2%   6031t    46.5%   8162t    56.5%  16660t    62.5%  32762t    61.0%  67224t
tourney       47.8%   5980t    51.7%   7959t    58.0%  16353t    63.5%  32431t    66.0%  63974t

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
rank N=2: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=4: judge - random           d = +10.0 pts   naive 95% CI [+6.9, +13.1]   cluster 95% CI [+6.2, +13.8]   deff 1.50   b/c 42/2   McNemar p = 1.13e-10   clustered p = 2.78e-07
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 73%
rank N=8: judge - random           d = +15.0 pts   naive 95% CI [+9.5, +20.5]   cluster 95% CI [+9.5, +20.5]   deff 0.98   b/c 33/3   McNemar p = 2.27e-07   clustered p = 8.27e-08
                                   power: MDE(80%) 7.8 pts   power to detect 5 pts = 43%   <- underpowered; a null here is NOT evidence of no effect
rank N=16: judge - random          d = +18.0 pts   naive 95% CI [+9.5, +26.5]   cluster 95% CI [+9.5, +26.5]   deff 0.99   b/c 20/2   McNemar p = 0.000121   clustered p = 3.55e-05
                                   power: MDE(80%) 12.2 pts   power to detect 5 pts = 21%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=4: judge - random         d = +11.0 pts   naive 95% CI [+7.9, +14.1]   cluster 95% CI [+7.4, +14.6]   deff 1.28   b/c 45/1   McNemar p = 1.34e-12   clustered p = 1.6e-09
                                   power: MDE(80%) 5.1 pts   power to detect 5 pts = 78%
random N=8: judge - random         d = +12.5 pts   naive 95% CI [+7.5, +17.5]   cluster 95% CI [+7.4, +17.6]   deff 1.03   b/c 27/2   McNemar p = 1.62e-06   clustered p = 1.51e-06
                                   power: MDE(80%) 7.3 pts   power to detect 5 pts = 49%   <- underpowered; a null here is NOT evidence of no effect
random N=16: judge - random        d = +12.0 pts   naive 95% CI [+3.5, +20.5]   cluster 95% CI [+3.5, +20.5]   deff 0.99   b/c 16/4   McNemar p = 0.0118   clustered p = 0.00558
                                   power: MDE(80%) 12.1 pts   power to detect 5 pts = 21%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=4: judge - random        d = +9.8 pts   naive 95% CI [+6.6, +12.9]   cluster 95% CI [+5.9, +13.6]   deff 1.45   b/c 42/3   McNemar p = 8.65e-10   clustered p = 5.21e-07
                                   power: MDE(80%) 5.4 pts   power to detect 5 pts = 73%
tourney N=8: judge - random        d = +14.0 pts   naive 95% CI [+8.4, +19.6]   cluster 95% CI [+8.2, +19.8]   deff 1.06   b/c 32/4   McNemar p = 1.94e-06   clustered p = 1.87e-06
                                   power: MDE(80%) 8.2 pts   power to detect 5 pts = 40%   <- underpowered; a null here is NOT evidence of no effect
tourney N=16: judge - random       d = +16.0 pts   naive 95% CI [+6.5, +25.5]   cluster 95% CI [+6.5, +25.5]   deff 0.99   b/c 21/5   McNemar p = 0.00249   clustered p = 0.00101
                                   power: MDE(80%) 13.6 pts   power to detect 5 pts = 18%   <- underpowered; a null here is NOT evidence of no effect

============================================================================================================
3. ORACLE CEILING   (a correct candidate EXISTS vs the judge FINDS it)
   NOTE: for pruned arms this is pass@k over SURVIVORS, not over all N.
   Only the baseline row is a clean best-of-N ceiling.

baseline   N=1   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
baseline   N=2   ceiling  57.0%   selected  54.5%   gap  2.5 pts   capture  95.6%
baseline   N=4   ceiling  66.2%   selected  63.0%   gap  3.2 pts   capture  95.1%
baseline   N=8   ceiling  73.5%   selected  69.5%   gap  4.0 pts   capture  94.6%
baseline   N=16  ceiling  79.0%   selected  70.0%   gap  9.0 pts   capture  88.6%

rank       N=1   ceiling  48.0%   selected  48.0%   gap  0.0 pts   capture 100.0%
rank       N=2   ceiling  49.5%   selected  49.5%   gap  0.0 pts   capture 100.0%
rank       N=4   ceiling  60.5%   selected  59.5%   gap  1.0 pts   capture  98.3%
rank       N=8   ceiling  70.5%   selected  67.0%   gap  3.5 pts   capture  95.0%
rank       N=16  ceiling  76.0%   selected  67.0%   gap  9.0 pts   capture  88.2%

random     N=1   ceiling  47.2%   selected  47.2%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  46.5%   selected  46.5%   gap  0.0 pts   capture 100.0%
random     N=4   ceiling  58.0%   selected  56.5%   gap  1.5 pts   capture  97.4%
random     N=8   ceiling  64.5%   selected  62.5%   gap  2.0 pts   capture  96.9%
random     N=16  ceiling  74.0%   selected  61.0%   gap 13.0 pts   capture  82.4%

tourney    N=1   ceiling  47.8%   selected  47.8%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  51.7%   selected  51.7%   gap  0.0 pts   capture 100.0%
tourney    N=4   ceiling  59.8%   selected  58.0%   gap  1.8 pts   capture  97.1%
tourney    N=8   ceiling  66.5%   selected  63.5%   gap  3.0 pts   capture  95.5%
tourney    N=16  ceiling  74.0%   selected  66.0%   gap  8.0 pts   capture  89.2%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = +0.8 pts   naive 95% CI [-1.8, +3.3]   cluster 95% CI [-1.7, +3.2]   deff 0.92   b/c 15/12   McNemar p = 0.701   clustered p = 0.55
                                   power: MDE(80%) 3.5 pts   power to detect 5 pts = 98%
                                   non-inferiority (margin 5 pts): lower bound -1.7 -> NON-INFERIOR   one-sided p = 2.27e-06
                                   tokens 6194 vs 6031  (+2.7%, 95% CI [+0.3%, +5.1%])
N=2   rank - random                d = +3.0 pts   naive 95% CI [-0.7, +6.7]   cluster 95% CI [-0.8, +6.8]   deff 1.09   b/c 34/22   McNemar p = 0.141   clustered p = 0.125
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 72%
                                   non-inferiority (margin 5 pts): lower bound -0.8 -> NON-INFERIOR   one-sided p = 2.14e-05
                                   tokens 8001 vs 8162  (-2.0%, 95% CI [-5.3%, +1.4%])
N=4   rank - random                d = +3.0 pts   naive 95% CI [-0.9, +6.9]   cluster 95% CI [-0.3, +6.3]   deff 0.72   b/c 37/25   McNemar p = 0.162   clustered p = 0.0737
                                   power: MDE(80%) 4.7 pts   power to detect 5 pts = 85%
                                   non-inferiority (margin 5 pts): lower bound -0.3 -> NON-INFERIOR   one-sided p = 9.22e-07
                                   tokens 16221 vs 16660  (-2.6%, 95% CI [-5.1%, -0.1%])
N=8   rank - random                d = +4.5 pts   naive 95% CI [-0.8, +9.8]   cluster 95% CI [-0.7, +9.7]   deff 0.98   b/c 19/10   McNemar p = 0.136   clustered p = 0.0917
                                   power: MDE(80%) 7.5 pts   power to detect 5 pts = 47%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -0.7 -> NON-INFERIOR   one-sided p = 0.000185
                                   tokens 31058 vs 32762  (-5.2%, 95% CI [-7.6%, -2.8%])
N=16  rank - random                d = +6.0 pts   naive 95% CI [-2.7, +14.7]   cluster 95% CI [-2.7, +14.7]   deff 0.99   b/c 13/7   McNemar p = 0.263   clustered p = 0.178
                                   power: MDE(80%) 12.5 pts   power to detect 5 pts = 20%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -2.7 -> NON-INFERIOR   one-sided p = 0.00676
                                   tokens 62187 vs 67224  (-7.5%, 95% CI [-9.9%, -5.1%])

N=1   rank - baseline              d = +0.5 pts   naive 95% CI [-3.2, +4.2]   cluster 95% CI [-3.0, +4.0]   deff 0.93   b/c 29/27   McNemar p = 0.894   clustered p = 0.782
                                   power: MDE(80%) 5.1 pts   power to detect 5 pts = 79%
                                   non-inferiority (margin 5 pts): lower bound -3.0 -> NON-INFERIOR   one-sided p = 0.0012
                                   tokens 6194 vs 8417  (-26.4%, 95% CI [-30.8%, -22.0%])
N=2   rank - baseline              d = -5.0 pts   naive 95% CI [-8.8, -1.2]   cluster 95% CI [-9.2, -0.8]   deff 1.25   b/c 20/40   McNemar p = 0.0135   clustered p = 0.0207
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 64%
                                   non-inferiority (margin 5 pts): lower bound -9.2 -> cannot claim parity   one-sided p = 0.5
                                   tokens 8001 vs 17179  (-53.4%, 95% CI [-55.8%, -51.1%])
N=4   rank - baseline              d = -3.5 pts   naive 95% CI [-7.3, +0.3]   cluster 95% CI [-7.5, +0.5]   deff 1.11   b/c 23/37   McNemar p = 0.0925   clustered p = 0.0865
                                   power: MDE(80%) 5.7 pts   power to detect 5 pts = 69%
                                   non-inferiority (margin 5 pts): lower bound -7.5 -> cannot claim parity   one-sided p = 0.231
                                   tokens 16221 vs 34192  (-52.6%, 95% CI [-54.7%, -50.5%])
N=8   rank - baseline              d = -2.5 pts   naive 95% CI [-8.0, +3.0]   cluster 95% CI [-7.4, +2.4]   deff 0.80   b/c 13/18   McNemar p = 0.473   clustered p = 0.317
                                   power: MDE(80%) 7.0 pts   power to detect 5 pts = 52%
                                   non-inferiority (margin 5 pts): lower bound -7.4 -> cannot claim parity   one-sided p = 0.159
                                   tokens 31058 vs 67682  (-54.1%, 95% CI [-56.1%, -52.1%])
N=16  rank - baseline              d = -3.0 pts   naive 95% CI [-11.6, +5.6]   cluster 95% CI [-11.6, +5.6]   deff 0.99   b/c 8/11   McNemar p = 0.648   clustered p = 0.492
                                   power: MDE(80%) 12.2 pts   power to detect 5 pts = 21%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -11.6 -> cannot claim parity   one-sided p = 0.324
                                   tokens 62187 vs 133659  (-53.5%, 95% CI [-55.4%, -51.5%])

N=1   tourney - baseline           d = +0.2 pts   naive 95% CI [-3.9, +4.4]   cluster 95% CI [-3.8, +4.3]   deff 0.97   b/c 36/35   McNemar p = 1   clustered p = 0.905
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 67%
                                   non-inferiority (margin 5 pts): lower bound -3.8 -> NON-INFERIOR   one-sided p = 0.00594
                                   tokens 5980 vs 8417  (-29.0%, 95% CI [-33.0%, -24.9%])
N=2   tourney - baseline           d = -2.8 pts   naive 95% CI [-6.5, +1.0]   cluster 95% CI [-6.5, +1.0]   deff 0.98   b/c 24/35   McNemar p = 0.193   clustered p = 0.15
                                   power: MDE(80%) 5.4 pts   power to detect 5 pts = 74%
                                   non-inferiority (margin 5 pts): lower bound -6.5 -> cannot claim parity   one-sided p = 0.119
                                   tokens 7959 vs 17179  (-53.7%, 95% CI [-55.9%, -51.4%])
N=4   tourney - baseline           d = -5.0 pts   naive 95% CI [-8.8, -1.2]   cluster 95% CI [-9.5, -0.5]   deff 1.37   b/c 21/41   McNemar p = 0.0151   clustered p = 0.0299
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 58%
                                   non-inferiority (margin 5 pts): lower bound -9.5 -> cannot claim parity   one-sided p = 0.5
                                   tokens 16353 vs 34192  (-52.2%, 95% CI [-54.2%, -50.2%])
N=8   tourney - baseline           d = -6.0 pts   naive 95% CI [-11.3, -0.7]   cluster 95% CI [-10.7, -1.3]   deff 0.77   b/c 9/21   McNemar p = 0.0428   clustered p = 0.0119
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
                                   non-inferiority (margin 5 pts): lower bound -10.7 -> cannot claim parity   one-sided p = 0.662
                                   tokens 32431 vs 67682  (-52.1%, 95% CI [-54.2%, -49.9%])
N=16  tourney - baseline           d = -4.0 pts   naive 95% CI [-12.3, +4.3]   cluster 95% CI [-12.3, +4.3]   deff 0.99   b/c 7/11   McNemar p = 0.481   clustered p = 0.346
                                   power: MDE(80%) 11.9 pts   power to detect 5 pts = 22%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -12.3 -> cannot claim parity   one-sided p = 0.407
                                   tokens 63974 vs 133659  (-52.1%, 95% CI [-54.4%, -49.9%])

N=1   random - baseline            d = -0.2 pts   naive 95% CI [-4.2, +3.7]   cluster 95% CI [-4.4, +3.9]   deff 1.09   b/c 32/33   McNemar p = 1   clustered p = 0.906
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
                                   non-inferiority (margin 5 pts): lower bound -4.4 -> NON-INFERIOR   one-sided p = 0.0124
                                   tokens 6031 vs 8417  (-28.4%, 95% CI [-32.5%, -24.2%])
N=2   random - baseline            d = -8.0 pts   naive 95% CI [-11.8, -4.2]   cluster 95% CI [-12.5, -3.5]   deff 1.33   b/c 16/48   McNemar p = 7.73e-05   clustered p = 0.00043
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 60%
                                   non-inferiority (margin 5 pts): lower bound -12.5 -> cannot claim parity   one-sided p = 0.907
                                   tokens 8162 vs 17179  (-52.5%, 95% CI [-55.2%, -49.8%])
N=4   random - baseline            d = -6.5 pts   naive 95% CI [-10.6, -2.4]   cluster 95% CI [-11.0, -2.0]   deff 1.22   b/c 22/48   McNemar p = 0.00255   clustered p = 0.00458
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 59%
                                   non-inferiority (margin 5 pts): lower bound -11.0 -> cannot claim parity   one-sided p = 0.744
                                   tokens 16660 vs 34192  (-51.3%, 95% CI [-53.6%, -48.9%])
N=8   random - baseline            d = -7.0 pts   naive 95% CI [-12.1, -1.9]   cluster 95% CI [-12.0, -2.0]   deff 0.96   b/c 7/21   McNemar p = 0.0125   clustered p = 0.00634
                                   power: MDE(80%) 7.2 pts   power to detect 5 pts = 50%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -12.0 -> cannot claim parity   one-sided p = 0.782
                                   tokens 32762 vs 67682  (-51.6%, 95% CI [-54.0%, -49.2%])
N=16  random - baseline            d = -9.0 pts   naive 95% CI [-18.3, +0.3]   cluster 95% CI [-18.3, +0.3]   deff 0.99   b/c 7/16   McNemar p = 0.0931   clustered p = 0.0573
                                   power: MDE(80%) 13.3 pts   power to detect 5 pts = 18%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -18.3 -> cannot claim parity   one-sided p = 0.801
                                   tokens 67224 vs 133659  (-49.7%, 95% CI [-52.2%, -47.2%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = +2.8 pts   naive 95% CI [+1.0, +4.6]   cluster 95% CI [+0.9, +4.7]   deff 1.12   b/c 118/76   McNemar p = 0.00314   clustered p = 0.0045
                                   power: MDE(80%) 2.8 pts   power to detect 5 pts = 100%
                                   equal-weight per N: d = +3.4 pts (from 5 cells: +0.8, +3.0, +3.0, +4.5, +6.0)

pooled rank - baseline (chunk-wtd) d = -2.7 pts   naive 95% CI [-4.6, -0.7]   cluster 95% CI [-5.4, +0.1]   deff 1.96   b/c 93/133   McNemar p = 0.00933   clustered p = 0.0583
                                   power: MDE(80%) 3.9 pts   power to detect 5 pts = 94%
                                   equal-weight per N: d = -2.7 pts (from 5 cells: +0.5, -5.0, -3.5, -2.5, -3.0)

pooled tourney - baseline (chunk-wtd) d = -3.1 pts   naive 95% CI [-5.1, -1.0]   cluster 95% CI [-5.7, -0.4]   deff 1.73   b/c 97/143   McNemar p = 0.00359   clustered p = 0.0243
                                   power: MDE(80%) 3.8 pts   power to detect 5 pts = 96%
                                   equal-weight per N: d = -3.5 pts (from 5 cells: +0.2, -2.8, -5.0, -6.0, -4.0)

pooled random - baseline (chunk-wtd) d = -5.5 pts   naive 95% CI [-7.5, -3.4]   cluster 95% CI [-8.5, -2.4]   deff 2.19   b/c 84/166   McNemar p = 2.37e-07   clustered p = 0.00044
                                   power: MDE(80%) 4.4 pts   power to detect 5 pts = 90%
                                   equal-weight per N: d = -6.2 pts (from 5 cells: -0.2, -8.0, -6.5, -7.0, -9.0)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = +0.5 pts   95% CI [-3.0, +4.0]   win/loss 17/15   p = 0.782   sign p = 0.86
                                   tokens 6194 vs 8417 (-26.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.0 -> NON-INFERIOR   one-sided p = 0.0012
                                   WARNING: -26% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.1 pts   power to detect 5 pts = 79%
rank N=2 vs baseline N=1           d = +2.0 pts   95% CI [-2.3, +6.3]   win/loss 25/18   p = 0.359   sign p = 0.36
                                   tokens 8001 vs 8417 (-4.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.3 -> NON-INFERIOR   one-sided p = 0.000665
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
rank N=4 vs baseline N=2           d = +5.0 pts   95% CI [+1.5, +8.5]   win/loss 21/7   p = 0.00489   sign p = 0.0125
                                   tokens 16221 vs 17179 (-5.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +1.5 -> NON-INFERIOR   one-sided p = 9.09e-09
                                   power: MDE(80%) 5.0 pts   power to detect 5 pts = 80%
rank N=8 vs baseline N=4           d = +4.0 pts   95% CI [-1.0, +9.0]   win/loss 26/14   p = 0.118   sign p = 0.0807
                                   tokens 31058 vs 34192 (-9.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.0 -> NON-INFERIOR   one-sided p = 0.000214
                                   power: MDE(80%) 7.2 pts   power to detect 5 pts = 50%   <- underpowered
rank N=16 vs baseline N=8          d = -2.5 pts   95% CI [-8.9, +3.9]   win/loss 9/13   p = 0.447   sign p = 0.523
                                   tokens 62187 vs 67682 (-8.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -8.9 -> cannot claim parity   one-sided p = 0.223
                                   power: MDE(80%) 9.2 pts   power to detect 5 pts = 33%   <- underpowered

random N=1 vs baseline N=1         d = -0.2 pts   95% CI [-4.4, +3.9]   win/loss 18/21   p = 0.906   sign p = 0.749
                                   tokens 6031 vs 8417 (-28.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.4 -> NON-INFERIOR   one-sided p = 0.0124
                                   WARNING: -28% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
random N=2 vs baseline N=1         d = -1.0 pts   95% CI [-5.3, +3.3]   win/loss 16/23   p = 0.652   sign p = 0.337
                                   tokens 8162 vs 8417 (-3.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.3 -> cannot claim parity   one-sided p = 0.0356
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
random N=4 vs baseline N=2         d = +2.0 pts   95% CI [-1.6, +5.6]   win/loss 19/12   p = 0.276   sign p = 0.281
                                   tokens 16660 vs 17179 (-3.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.6 -> NON-INFERIOR   one-sided p = 6.84e-05
                                   power: MDE(80%) 5.1 pts   power to detect 5 pts = 78%
random N=8 vs baseline N=4         d = -0.5 pts   95% CI [-5.2, +4.2]   win/loss 16/17   p = 0.834   sign p = 1
                                   tokens 32762 vs 34192 (-4.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.2 -> cannot claim parity   one-sided p = 0.0295
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
random N=16 vs baseline N=8        d = -8.5 pts   95% CI [-15.9, -1.1]   win/loss 7/19   p = 0.0239   sign p = 0.029
                                   tokens 67224 vs 67682 (-0.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -15.9 -> cannot claim parity   one-sided p = 0.824
                                   power: MDE(80%) 10.5 pts   power to detect 5 pts = 26%   <- underpowered

tourney N=1 vs baseline N=1        d = +0.2 pts   95% CI [-3.8, +4.3]   win/loss 19/21   p = 0.905   sign p = 0.875
                                   tokens 5980 vs 8417 (-29.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.8 -> NON-INFERIOR   one-sided p = 0.00594
                                   WARNING: -29% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 67%
tourney N=2 vs baseline N=1        d = +4.2 pts   95% CI [+0.5, +8.0]   win/loss 22/10   p = 0.0265   sign p = 0.0501
                                   tokens 7959 vs 8417 (-5.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.5 -> NON-INFERIOR   one-sided p = 6.85e-07
                                   power: MDE(80%) 5.4 pts   power to detect 5 pts = 74%
tourney N=4 vs baseline N=2        d = +3.5 pts   95% CI [-0.3, +7.3]   win/loss 20/10   p = 0.0722   sign p = 0.0987
                                   tokens 16353 vs 17179 (-4.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -0.3 -> NON-INFERIOR   one-sided p = 6.33e-06
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 73%
tourney N=8 vs baseline N=4        d = +0.5 pts   95% CI [-4.0, +5.0]   win/loss 17/16   p = 0.826   sign p = 1
                                   tokens 32431 vs 34192 (-5.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.0 -> NON-INFERIOR   one-sided p = 0.00781
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 59%
tourney N=16 vs baseline N=8       d = -3.5 pts   95% CI [-10.5, +3.5]   win/loss 10/14   p = 0.327   sign p = 0.541
                                   tokens 63974 vs 67682 (-5.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -10.5 -> cannot claim parity   one-sided p = 0.337
                                   power: MDE(80%) 10.0 pts   power to detect 5 pts = 29%   <- underpowered

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

############################################################################################################
# CONFIG  plan=2500  prune=3.0
############################################################################################################
============================================================================================================
FILES
  baseline  2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json
  random    2026-07-18_18-13-23_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_3.0.json
  rank      2026-07-18_18-12-39_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_3.0.json
  tourney   2026-07-18_18-14-07_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_3.0.json
  N values: [1, 2, 4, 8, 16]

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16
baseline      47.5%   8417t    54.5%  17179t    63.0%  34192t    69.5%  67682t    70.0% 133659t
rank          49.8%   6093t    49.8%   7997t    53.8%  12137t    58.5%  23974t    66.0%  50214t
random        50.2%   5815t    47.5%   8032t    50.0%  12472t    58.0%  25334t    66.0%  54652t
tourney       50.7%   5925t    52.0%   7952t    52.8%  12478t    60.5%  25192t    68.0%  52725t

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
rank N=2: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=4: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=8: judge - random           d = +6.0 pts   naive 95% CI [+2.7, +9.3]   cluster 95% CI [+2.8, +9.2]   deff 0.93   b/c 12/0   McNemar p = 0.000488   clustered p = 0.000239
                                   power: MDE(80%) 4.6 pts   power to detect 5 pts = 86%
rank N=16: judge - random          d = +15.0 pts   naive 95% CI [+7.4, +22.6]   cluster 95% CI [+7.4, +22.6]   deff 0.99   b/c 16/1   McNemar p = 0.000275   clustered p = 0.000102
                                   power: MDE(80%) 10.8 pts   power to detect 5 pts = 25%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=4: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=8: judge - random         d = +13.5 pts   naive 95% CI [+8.2, +18.8]   cluster 95% CI [+8.1, +18.9]   deff 1.01   b/c 30/3   McNemar p = 1.4e-06   clustered p = 8.28e-07
                                   power: MDE(80%) 7.7 pts   power to detect 5 pts = 45%   <- underpowered; a null here is NOT evidence of no effect
random N=16: judge - random        d = +19.0 pts   naive 95% CI [+10.8, +27.2]   cluster 95% CI [+10.8, +27.2]   deff 0.99   b/c 20/1   McNemar p = 2.1e-05   clustered p = 5.8e-06
                                   power: MDE(80%) 11.7 pts   power to detect 5 pts = 22%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=4: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=8: judge - random        d = +9.0 pts   naive 95% CI [+4.8, +13.2]   cluster 95% CI [+4.7, +13.3]   deff 1.02   b/c 19/1   McNemar p = 4.01e-05   clustered p = 3.55e-05
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
tourney N=16: judge - random       d = +13.0 pts   naive 95% CI [+5.8, +20.2]   cluster 95% CI [+5.8, +20.2]   deff 0.99   b/c 14/1   McNemar p = 0.000977   clustered p = 0.000392
                                   power: MDE(80%) 10.3 pts   power to detect 5 pts = 28%   <- underpowered; a null here is NOT evidence of no effect

============================================================================================================
3. ORACLE CEILING   (a correct candidate EXISTS vs the judge FINDS it)
   NOTE: for pruned arms this is pass@k over SURVIVORS, not over all N.
   Only the baseline row is a clean best-of-N ceiling.

baseline   N=1   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
baseline   N=2   ceiling  57.0%   selected  54.5%   gap  2.5 pts   capture  95.6%
baseline   N=4   ceiling  66.2%   selected  63.0%   gap  3.2 pts   capture  95.1%
baseline   N=8   ceiling  73.5%   selected  69.5%   gap  4.0 pts   capture  94.6%
baseline   N=16  ceiling  79.0%   selected  70.0%   gap  9.0 pts   capture  88.6%

rank       N=1   ceiling  49.8%   selected  49.8%   gap  0.0 pts   capture 100.0%
rank       N=2   ceiling  49.8%   selected  49.8%   gap  0.0 pts   capture 100.0%
rank       N=4   ceiling  53.8%   selected  53.8%   gap  0.0 pts   capture 100.0%
rank       N=8   ceiling  59.0%   selected  58.5%   gap  0.5 pts   capture  99.2%
rank       N=16  ceiling  70.0%   selected  66.0%   gap  4.0 pts   capture  94.3%

random     N=1   ceiling  50.2%   selected  50.2%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
random     N=4   ceiling  50.0%   selected  50.0%   gap  0.0 pts   capture 100.0%
random     N=8   ceiling  59.5%   selected  58.0%   gap  1.5 pts   capture  97.5%
random     N=16  ceiling  69.0%   selected  66.0%   gap  3.0 pts   capture  95.7%

tourney    N=1   ceiling  50.7%   selected  50.7%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  52.0%   selected  52.0%   gap  0.0 pts   capture 100.0%
tourney    N=4   ceiling  52.8%   selected  52.8%   gap  0.0 pts   capture 100.0%
tourney    N=8   ceiling  61.5%   selected  60.5%   gap  1.0 pts   capture  98.4%
tourney    N=16  ceiling  71.0%   selected  68.0%   gap  3.0 pts   capture  95.8%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = -0.5 pts   naive 95% CI [-3.7, +2.7]   cluster 95% CI [-3.8, +2.8]   deff 1.04   b/c 20/22   McNemar p = 0.878   clustered p = 0.764
                                   power: MDE(80%) 4.7 pts   power to detect 5 pts = 85%
                                   non-inferiority (margin 5 pts): lower bound -3.8 -> NON-INFERIOR   one-sided p = 0.00345
                                   tokens 6093 vs 5815  (+4.8%, 95% CI [+2.0%, +7.5%])
N=2   rank - random                d = +2.2 pts   naive 95% CI [-1.7, +6.2]   cluster 95% CI [-1.2, +5.7]   deff 0.77   b/c 37/28   McNemar p = 0.321   clustered p = 0.206
                                   power: MDE(80%) 5.0 pts   power to detect 5 pts = 80%
                                   non-inferiority (margin 5 pts): lower bound -1.2 -> NON-INFERIOR   one-sided p = 2.32e-05
                                   tokens 7997 vs 8032  (-0.4%, 95% CI [-3.4%, +2.5%])
N=4   rank - random                d = +3.8 pts   naive 95% CI [-0.4, +7.9]   cluster 95% CI [-0.4, +7.9]   deff 0.97   b/c 44/29   McNemar p = 0.101   clustered p = 0.076
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
                                   non-inferiority (margin 5 pts): lower bound -0.4 -> NON-INFERIOR   one-sided p = 1.73e-05
                                   tokens 12137 vs 12472  (-2.7%, 95% CI [-4.9%, -0.5%])
N=8   rank - random                d = +0.5 pts   naive 95% CI [-4.6, +5.6]   cluster 95% CI [-4.6, +5.6]   deff 0.99   b/c 14/13   McNemar p = 1   clustered p = 0.848
                                   power: MDE(80%) 7.3 pts   power to detect 5 pts = 48%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -4.6 -> NON-INFERIOR   one-sided p = 0.0176
                                   tokens 23974 vs 25334  (-5.4%, 95% CI [-7.6%, -3.1%])
N=16  rank - random                d = +0.0 pts   naive 95% CI [-7.4, +7.4]   cluster 95% CI [-7.4, +7.4]   deff 0.99   b/c 7/7   McNemar p = 1   clustered p = 1
                                   power: MDE(80%) 10.5 pts   power to detect 5 pts = 26%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -7.4 -> cannot claim parity   one-sided p = 0.0918
                                   tokens 50214 vs 54652  (-8.1%, 95% CI [-10.4%, -5.8%])

N=1   rank - baseline              d = +2.2 pts   naive 95% CI [-1.8, +6.3]   cluster 95% CI [-2.3, +6.8]   deff 1.29   b/c 38/29   McNemar p = 0.328   clustered p = 0.335
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 57%
                                   non-inferiority (margin 5 pts): lower bound -2.3 -> NON-INFERIOR   one-sided p = 0.000942
                                   tokens 6093 vs 8417  (-27.6%, 95% CI [-31.9%, -23.4%])
N=2   rank - baseline              d = -4.8 pts   naive 95% CI [-8.7, -0.8]   cluster 95% CI [-8.4, -1.1]   deff 0.86   b/c 23/42   McNemar p = 0.0248   clustered p = 0.0111
                                   power: MDE(80%) 5.2 pts   power to detect 5 pts = 76%
                                   non-inferiority (margin 5 pts): lower bound -8.4 -> cannot claim parity   one-sided p = 0.447
                                   tokens 7997 vs 17179  (-53.4%, 95% CI [-55.7%, -51.2%])
N=4   rank - baseline              d = -9.2 pts   naive 95% CI [-13.2, -5.3]   cluster 95% CI [-14.5, -4.0]   deff 1.72   b/c 16/53   McNemar p = 9.1e-06   clustered p = 0.000543
                                   power: MDE(80%) 7.5 pts   power to detect 5 pts = 46%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -14.5 -> cannot claim parity   one-sided p = 0.944
                                   tokens 12137 vs 34192  (-64.5%, 95% CI [-66.5%, -62.5%])
N=8   rank - baseline              d = -11.0 pts   naive 95% CI [-16.3, -5.7]   cluster 95% CI [-16.7, -5.3]   deff 1.12   b/c 5/27   McNemar p = 0.000113   clustered p = 0.000144
                                   power: MDE(80%) 8.1 pts   power to detect 5 pts = 41%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -16.7 -> cannot claim parity   one-sided p = 0.981
                                   tokens 23974 vs 67682  (-64.6%, 95% CI [-66.5%, -62.6%])
N=16  rank - baseline              d = -4.0 pts   naive 95% CI [-12.3, +4.3]   cluster 95% CI [-12.3, +4.3]   deff 0.99   b/c 7/11   McNemar p = 0.481   clustered p = 0.346
                                   power: MDE(80%) 11.9 pts   power to detect 5 pts = 22%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -12.3 -> cannot claim parity   one-sided p = 0.407
                                   tokens 50214 vs 133659  (-62.4%, 95% CI [-64.4%, -60.5%])

N=1   tourney - baseline           d = +3.2 pts   naive 95% CI [-0.7, +7.2]   cluster 95% CI [+0.2, +6.3]   deff 0.58   b/c 39/26   McNemar p = 0.136   clustered p = 0.0342
                                   power: MDE(80%) 4.3 pts   power to detect 5 pts = 90%
                                   non-inferiority (margin 5 pts): lower bound +0.2 -> NON-INFERIOR   one-sided p = 3.82e-08
                                   tokens 5925 vs 8417  (-29.6%, 95% CI [-33.3%, -25.9%])
N=2   tourney - baseline           d = -2.5 pts   naive 95% CI [-6.2, +1.2]   cluster 95% CI [-5.8, +0.8]   deff 0.78   b/c 24/34   McNemar p = 0.237   clustered p = 0.138
                                   power: MDE(80%) 4.7 pts   power to detect 5 pts = 84%
                                   non-inferiority (margin 5 pts): lower bound -5.8 -> cannot claim parity   one-sided p = 0.069
                                   tokens 7952 vs 17179  (-53.7%, 95% CI [-56.2%, -51.3%])
N=4   tourney - baseline           d = -10.2 pts   naive 95% CI [-14.3, -6.2]   cluster 95% CI [-15.5, -5.0]   deff 1.71   b/c 15/56   McNemar p = 1.04e-06   clustered p = 0.000135
                                   power: MDE(80%) 7.5 pts   power to detect 5 pts = 46%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -15.5 -> cannot claim parity   one-sided p = 0.975
                                   tokens 12478 vs 34192  (-63.5%, 95% CI [-65.6%, -61.4%])
N=8   tourney - baseline           d = -9.0 pts   naive 95% CI [-14.6, -3.4]   cluster 95% CI [-14.3, -3.7]   deff 0.88   b/c 8/26   McNemar p = 0.00294   clustered p = 0.000839
                                   power: MDE(80%) 7.6 pts   power to detect 5 pts = 46%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -14.3 -> cannot claim parity   one-sided p = 0.931
                                   tokens 25192 vs 67682  (-62.8%, 95% CI [-65.0%, -60.6%])
N=16  tourney - baseline           d = -2.0 pts   naive 95% CI [-10.8, +6.8]   cluster 95% CI [-10.8, +6.8]   deff 0.99   b/c 9/11   McNemar p = 0.824   clustered p = 0.656
                                   power: MDE(80%) 12.6 pts   power to detect 5 pts = 20%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -10.8 -> cannot claim parity   one-sided p = 0.252
                                   tokens 52725 vs 133659  (-60.6%, 95% CI [-62.6%, -58.5%])

N=1   random - baseline            d = +2.8 pts   naive 95% CI [-1.3, +6.8]   cluster 95% CI [-1.2, +6.7]   deff 0.95   b/c 39/28   McNemar p = 0.222   clustered p = 0.171
                                   power: MDE(80%) 5.6 pts   power to detect 5 pts = 70%
                                   non-inferiority (margin 5 pts): lower bound -1.2 -> NON-INFERIOR   one-sided p = 5.63e-05
                                   tokens 5815 vs 8417  (-30.9%, 95% CI [-34.8%, -27.1%])
N=2   random - baseline            d = -7.0 pts   naive 95% CI [-11.3, -2.7]   cluster 95% CI [-10.9, -3.1]   deff 0.84   b/c 25/53   McNemar p = 0.00203   clustered p = 0.000505
                                   power: MDE(80%) 5.6 pts   power to detect 5 pts = 70%
                                   non-inferiority (margin 5 pts): lower bound -10.9 -> cannot claim parity   one-sided p = 0.84
                                   tokens 8032 vs 17179  (-53.2%, 95% CI [-55.6%, -50.9%])
N=4   random - baseline            d = -13.0 pts   naive 95% CI [-17.5, -8.5]   cluster 95% CI [-17.8, -8.2]   deff 1.16   b/c 19/71   McNemar p = 3.13e-08   clustered p = 1.48e-07
                                   power: MDE(80%) 6.9 pts   power to detect 5 pts = 52%
                                   non-inferiority (margin 5 pts): lower bound -17.8 -> cannot claim parity   one-sided p = 0.999
                                   tokens 12472 vs 34192  (-63.5%, 95% CI [-65.7%, -61.3%])
N=8   random - baseline            d = -11.5 pts   naive 95% CI [-17.4, -5.6]   cluster 95% CI [-17.5, -5.5]   deff 1.03   b/c 8/31   McNemar p = 0.000294   clustered p = 0.000194
                                   power: MDE(80%) 8.6 pts   power to detect 5 pts = 37%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -17.5 -> cannot claim parity   one-sided p = 0.982
                                   tokens 25334 vs 67682  (-62.6%, 95% CI [-64.9%, -60.3%])
N=16  random - baseline            d = -4.0 pts   naive 95% CI [-13.2, +5.2]   cluster 95% CI [-13.2, +5.2]   deff 0.99   b/c 9/13   McNemar p = 0.523   clustered p = 0.394
                                   power: MDE(80%) 13.2 pts   power to detect 5 pts = 19%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -13.2 -> cannot claim parity   one-sided p = 0.416
                                   tokens 54652 vs 133659  (-59.1%, 95% CI [-61.5%, -56.7%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = +1.5 pts   naive 95% CI [-0.4, +3.5]   cluster 95% CI [-0.4, +3.5]   deff 0.99   b/c 122/99   McNemar p = 0.139   clustered p = 0.121
                                   power: MDE(80%) 2.8 pts   power to detect 5 pts = 100%
                                   equal-weight per N: d = +1.2 pts (from 5 cells: -0.5, +2.2, +3.8, +0.5, +0.0)

pooled rank - baseline (chunk-wtd) d = -4.9 pts   naive 95% CI [-6.9, -2.8]   cluster 95% CI [-8.0, -1.8]   deff 2.23   b/c 89/162   McNemar p = 4.76e-06   clustered p = 0.00199
                                   power: MDE(80%) 4.4 pts   power to detect 5 pts = 89%
                                   equal-weight per N: d = -5.4 pts (from 5 cells: +2.2, -4.8, -9.2, -11.0, -4.0)

pooled tourney - baseline (chunk-wtd) d = -3.9 pts   naive 95% CI [-5.9, -1.8]   cluster 95% CI [-6.7, -1.0]   deff 1.95   b/c 95/153   McNemar p = 0.000279   clustered p = 0.00833
                                   power: MDE(80%) 4.1 pts   power to detect 5 pts = 93%
                                   equal-weight per N: d = -4.1 pts (from 5 cells: +3.2, -2.5, -10.2, -9.0, -2.0)

pooled random - baseline (chunk-wtd) d = -6.4 pts   naive 95% CI [-8.6, -4.2]   cluster 95% CI [-9.2, -3.6]   deff 1.56   b/c 100/196   McNemar p = 2.56e-08   clustered p = 7e-06
                                   power: MDE(80%) 4.0 pts   power to detect 5 pts = 94%
                                   equal-weight per N: d = -6.6 pts (from 5 cells: +2.8, -7.0, -13.0, -11.5, -4.0)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = +2.2 pts   95% CI [-2.3, +6.8]   win/loss 23/19   p = 0.335   sign p = 0.644
                                   tokens 6093 vs 8417 (-27.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.3 -> NON-INFERIOR   one-sided p = 0.000942
                                   WARNING: -28% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 57%
rank N=2 vs baseline N=1           d = +2.2 pts   95% CI [-1.2, +5.7]   win/loss 19/11   p = 0.206   sign p = 0.2
                                   tokens 7997 vs 8417 (-5.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.2 -> NON-INFERIOR   one-sided p = 2.32e-05
                                   power: MDE(80%) 5.0 pts   power to detect 5 pts = 80%
rank N=4 vs baseline N=1           d = +6.2 pts   95% CI [+1.5, +11.0]   win/loss 28/11   p = 0.0098   sign p = 0.00948
                                   tokens 12137 vs 8417 (+44.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +1.5 -> NON-INFERIOR   one-sided p = 1.67e-06
                                   WARNING: +44% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.8 pts   power to detect 5 pts = 54%
rank N=8 vs baseline N=2           d = +4.0 pts   95% CI [-1.0, +9.0]   win/loss 25/11   p = 0.118   sign p = 0.0288
                                   tokens 23974 vs 17179 (+39.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.0 -> NON-INFERIOR   one-sided p = 0.000214
                                   WARNING: +40% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 7.2 pts   power to detect 5 pts = 50%   <- underpowered
rank N=16 vs baseline N=4          d = +3.0 pts   95% CI [-3.3, +9.3]   win/loss 22/14   p = 0.352   sign p = 0.243
                                   tokens 50214 vs 34192 (+46.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.3 -> NON-INFERIOR   one-sided p = 0.00653
                                   WARNING: +47% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 9.0 pts   power to detect 5 pts = 34%   <- underpowered

random N=1 vs baseline N=1         d = +2.8 pts   95% CI [-1.2, +6.7]   win/loss 22/16   p = 0.171   sign p = 0.418
                                   tokens 5815 vs 8417 (-30.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.2 -> NON-INFERIOR   one-sided p = 5.63e-05
                                   WARNING: -31% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.6 pts   power to detect 5 pts = 70%
random N=2 vs baseline N=1         d = +0.0 pts   95% CI [-4.1, +4.1]   win/loss 20/22   p = 1   sign p = 0.878
                                   tokens 8032 vs 8417 (-4.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.1 -> NON-INFERIOR   one-sided p = 0.00791
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 67%
random N=4 vs baseline N=1         d = +2.5 pts   95% CI [-1.5, +6.5]   win/loss 24/18   p = 0.217   sign p = 0.441
                                   tokens 12472 vs 8417 (+48.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.5 -> NON-INFERIOR   one-sided p = 0.000107
                                   WARNING: +48% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.7 pts   power to detect 5 pts = 69%
random N=8 vs baseline N=2         d = +3.5 pts   95% CI [-2.1, +9.1]   win/loss 26/13   p = 0.218   sign p = 0.0533
                                   tokens 25334 vs 17179 (+47.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.1 -> NON-INFERIOR   one-sided p = 0.0014
                                   WARNING: +47% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 8.0 pts   power to detect 5 pts = 42%   <- underpowered
random N=16 vs baseline N=8        d = -3.5 pts   95% CI [-9.9, +2.9]   win/loss 8/14   p = 0.285   sign p = 0.286
                                   tokens 54652 vs 67682 (-19.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -9.9 -> cannot claim parity   one-sided p = 0.324
                                   WARNING: -19% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 9.2 pts   power to detect 5 pts = 33%   <- underpowered

tourney N=1 vs baseline N=1        d = +3.2 pts   95% CI [+0.2, +6.3]   win/loss 19/8   p = 0.0342   sign p = 0.0522
                                   tokens 5925 vs 8417 (-29.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.2 -> NON-INFERIOR   one-sided p = 3.82e-08
                                   WARNING: -30% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 4.3 pts   power to detect 5 pts = 90%
tourney N=2 vs baseline N=1        d = +4.5 pts   95% CI [+0.4, +8.6]   win/loss 26/12   p = 0.0308   sign p = 0.0336
                                   tokens 7952 vs 8417 (-5.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.4 -> NON-INFERIOR   one-sided p = 2.56e-06
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 67%
tourney N=4 vs baseline N=1        d = +5.2 pts   95% CI [+0.3, +10.2]   win/loss 30/13   p = 0.0391   sign p = 0.0137
                                   tokens 12478 vs 8417 (+48.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.3 -> NON-INFERIOR   one-sided p = 2.82e-05
                                   WARNING: +48% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 7.1 pts   power to detect 5 pts = 50%
tourney N=8 vs baseline N=2        d = +6.0 pts   95% CI [+1.0, +11.0]   win/loss 26/11   p = 0.0193   sign p = 0.0201
                                   tokens 25192 vs 17179 (+46.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +1.0 -> NON-INFERIOR   one-sided p = 9.02e-06
                                   WARNING: +47% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 7.2 pts   power to detect 5 pts = 50%   <- underpowered
tourney N=16 vs baseline N=8       d = -1.5 pts   95% CI [-8.0, +5.0]   win/loss 9/13   p = 0.649   sign p = 0.523
                                   tokens 52725 vs 67682 (-22.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -8.0 -> cannot claim parity   one-sided p = 0.144
                                   WARNING: -22% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 9.2 pts   power to detect 5 pts = 33%   <- underpowered

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

############################################################################################################
# CONFIG  plan=2500  prune=4.0
############################################################################################################
============================================================================================================
FILES
  baseline  2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json
  random    2026-07-18_17-37-50_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_4.0.json
  rank      2026-07-18_17-37-07_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_4.0.json
  tourney   2026-07-18_17-38-34_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_4.0.json
  N values: [1, 2, 4, 8, 16]

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16
baseline      47.5%   8417t    54.5%  17179t    63.0%  34192t    69.5%  67682t    70.0% 133659t
rank          49.5%   6000t    50.7%   7927t    55.5%  12154t    59.0%  24021t    66.0%  47036t
random        49.8%   5864t    46.8%   8137t    47.5%  12531t    56.5%  25399t    62.0%  50887t
tourney       49.8%   5869t    50.2%   7984t    55.0%  12525t    59.5%  25051t    69.0%  49978t

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
rank N=2: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=4: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=8: judge - random           d = +5.5 pts   naive 95% CI [+2.0, +9.0]   cluster 95% CI [+1.8, +9.2]   deff 1.11   b/c 12/1   McNemar p = 0.00342   clustered p = 0.00321
                                   power: MDE(80%) 5.2 pts   power to detect 5 pts = 76%
rank N=16: judge - random          d = +10.0 pts   naive 95% CI [+2.9, +17.1]   cluster 95% CI [+2.9, +17.1]   deff 0.99   b/c 12/2   McNemar p = 0.0129   clustered p = 0.00579
                                   power: MDE(80%) 10.2 pts   power to detect 5 pts = 28%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=4: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=8: judge - random         d = +9.0 pts   naive 95% CI [+4.6, +13.4]   cluster 95% CI [+4.1, +13.9]   deff 1.21   b/c 20/2   McNemar p = 0.000121   clustered p = 0.000319
                                   power: MDE(80%) 7.0 pts   power to detect 5 pts = 52%
random N=16: judge - random        d = +11.0 pts   naive 95% CI [+3.2, +18.8]   cluster 95% CI [+3.2, +18.8]   deff 0.99   b/c 14/3   McNemar p = 0.0127   clustered p = 0.00588
                                   power: MDE(80%) 11.2 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=4: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=8: judge - random        d = +5.0 pts   naive 95% CI [+1.7, +8.3]   cluster 95% CI [+1.7, +8.3]   deff 0.95   b/c 11/1   McNemar p = 0.00635   clustered p = 0.0027
                                   power: MDE(80%) 4.7 pts   power to detect 5 pts = 85%
tourney N=16: judge - random       d = +15.0 pts   naive 95% CI [+8.0, +22.0]   cluster 95% CI [+8.0, +22.0]   deff 0.99   b/c 15/0   McNemar p = 6.1e-05   clustered p = 2.92e-05
                                   power: MDE(80%) 10.1 pts   power to detect 5 pts = 29%   <- underpowered; a null here is NOT evidence of no effect

============================================================================================================
3. ORACLE CEILING   (a correct candidate EXISTS vs the judge FINDS it)
   NOTE: for pruned arms this is pass@k over SURVIVORS, not over all N.
   Only the baseline row is a clean best-of-N ceiling.

baseline   N=1   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
baseline   N=2   ceiling  57.0%   selected  54.5%   gap  2.5 pts   capture  95.6%
baseline   N=4   ceiling  66.2%   selected  63.0%   gap  3.2 pts   capture  95.1%
baseline   N=8   ceiling  73.5%   selected  69.5%   gap  4.0 pts   capture  94.6%
baseline   N=16  ceiling  79.0%   selected  70.0%   gap  9.0 pts   capture  88.6%

rank       N=1   ceiling  49.5%   selected  49.5%   gap  0.0 pts   capture 100.0%
rank       N=2   ceiling  50.7%   selected  50.7%   gap  0.0 pts   capture 100.0%
rank       N=4   ceiling  55.5%   selected  55.5%   gap  0.0 pts   capture 100.0%
rank       N=8   ceiling  60.5%   selected  59.0%   gap  1.5 pts   capture  97.5%
rank       N=16  ceiling  69.0%   selected  66.0%   gap  3.0 pts   capture  95.7%

random     N=1   ceiling  49.8%   selected  49.8%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  46.8%   selected  46.8%   gap  0.0 pts   capture 100.0%
random     N=4   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
random     N=8   ceiling  58.0%   selected  56.5%   gap  1.5 pts   capture  97.4%
random     N=16  ceiling  66.0%   selected  62.0%   gap  4.0 pts   capture  93.9%

tourney    N=1   ceiling  49.8%   selected  49.8%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  50.2%   selected  50.2%   gap  0.0 pts   capture 100.0%
tourney    N=4   ceiling  55.0%   selected  55.0%   gap  0.0 pts   capture 100.0%
tourney    N=8   ceiling  60.5%   selected  59.5%   gap  1.0 pts   capture  98.3%
tourney    N=16  ceiling  70.0%   selected  69.0%   gap  1.0 pts   capture  98.6%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = -0.2 pts   naive 95% CI [-4.1, +3.6]   cluster 95% CI [-4.9, +4.4]   deff 1.41   b/c 31/32   McNemar p = 1   clustered p = 0.916
                                   power: MDE(80%) 6.6 pts   power to detect 5 pts = 56%
                                   non-inferiority (margin 5 pts): lower bound -4.9 -> NON-INFERIOR   one-sided p = 0.0225
                                   tokens 6000 vs 5864  (+2.3%, 95% CI [-1.2%, +5.9%])
N=2   rank - random                d = +4.0 pts   naive 95% CI [-0.1, +8.1]   cluster 95% CI [-0.3, +8.3]   deff 1.05   b/c 44/28   McNemar p = 0.0764   clustered p = 0.0668
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
                                   non-inferiority (margin 5 pts): lower bound -0.3 -> NON-INFERIOR   one-sided p = 1.86e-05
                                   tokens 7927 vs 8137  (-2.6%, 95% CI [-5.6%, +0.5%])
N=4   rank - random                d = +8.0 pts   naive 95% CI [+3.9, +12.1]   cluster 95% CI [+3.5, +12.5]   deff 1.17   b/c 53/21   McNemar p = 0.000256   clustered p = 0.000503
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 58%
                                   non-inferiority (margin 5 pts): lower bound +3.5 -> NON-INFERIOR   one-sided p = 7.87e-09
                                   tokens 12154 vs 12531  (-3.0%, 95% CI [-5.3%, -0.7%])
N=8   rank - random                d = +2.5 pts   naive 95% CI [-2.6, +7.6]   cluster 95% CI [-2.8, +7.8]   deff 1.06   b/c 16/11   McNemar p = 0.442   clustered p = 0.353
                                   power: MDE(80%) 7.5 pts   power to detect 5 pts = 46%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -2.8 -> NON-INFERIOR   one-sided p = 0.00269
                                   tokens 24021 vs 25399  (-5.4%, 95% CI [-7.8%, -3.1%])
N=16  rank - random                d = +4.0 pts   naive 95% CI [-3.3, +11.3]   cluster 95% CI [-3.3, +11.3]   deff 0.99   b/c 9/5   McNemar p = 0.424   clustered p = 0.285
                                   power: MDE(80%) 10.5 pts   power to detect 5 pts = 27%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -3.3 -> NON-INFERIOR   one-sided p = 0.00804
                                   tokens 47036 vs 50887  (-7.6%, 95% CI [-9.8%, -5.3%])

N=1   rank - baseline              d = +2.0 pts   naive 95% CI [-2.2, +6.2]   cluster 95% CI [-2.4, +6.4]   deff 1.13   b/c 40/32   McNemar p = 0.41   clustered p = 0.378
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 60%
                                   non-inferiority (margin 5 pts): lower bound -2.4 -> NON-INFERIOR   one-sided p = 0.00101
                                   tokens 6000 vs 8417  (-28.7%, 95% CI [-32.9%, -24.5%])
N=2   rank - baseline              d = -3.8 pts   naive 95% CI [-7.4, -0.1]   cluster 95% CI [-8.1, +0.6]   deff 1.36   b/c 21/36   McNemar p = 0.0627   clustered p = 0.0885
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
                                   non-inferiority (margin 5 pts): lower bound -8.1 -> cannot claim parity   one-sided p = 0.285
                                   tokens 7927 vs 17179  (-53.9%, 95% CI [-56.1%, -51.6%])
N=4   rank - baseline              d = -7.5 pts   naive 95% CI [-11.6, -3.4]   cluster 95% CI [-12.4, -2.6]   deff 1.44   b/c 21/51   McNemar p = 0.000535   clustered p = 0.00298
                                   power: MDE(80%) 7.1 pts   power to detect 5 pts = 51%
                                   non-inferiority (margin 5 pts): lower bound -12.4 -> cannot claim parity   one-sided p = 0.839
                                   tokens 12154 vs 34192  (-64.5%, 95% CI [-66.5%, -62.5%])
N=8   rank - baseline              d = -10.5 pts   naive 95% CI [-15.8, -5.2]   cluster 95% CI [-15.9, -5.1]   deff 1.06   b/c 5/26   McNemar p = 0.000192   clustered p = 0.000158
                                   power: MDE(80%) 7.8 pts   power to detect 5 pts = 44%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -15.9 -> cannot claim parity   one-sided p = 0.976
                                   tokens 24021 vs 67682  (-64.5%, 95% CI [-66.5%, -62.5%])
N=16  rank - baseline              d = -4.0 pts   naive 95% CI [-11.3, +3.3]   cluster 95% CI [-11.3, +3.3]   deff 0.99   b/c 5/9   McNemar p = 0.424   clustered p = 0.285
                                   power: MDE(80%) 10.5 pts   power to detect 5 pts = 27%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -11.3 -> cannot claim parity   one-sided p = 0.395
                                   tokens 47036 vs 133659  (-64.8%, 95% CI [-66.8%, -62.8%])

N=1   tourney - baseline           d = +2.2 pts   naive 95% CI [-1.5, +6.0]   cluster 95% CI [-0.9, +5.4]   deff 0.72   b/c 34/25   McNemar p = 0.298   clustered p = 0.168
                                   power: MDE(80%) 4.6 pts   power to detect 5 pts = 87%
                                   non-inferiority (margin 5 pts): lower bound -0.9 -> NON-INFERIOR   one-sided p = 4.45e-06
                                   tokens 5869 vs 8417  (-30.3%, 95% CI [-34.1%, -26.5%])
N=2   tourney - baseline           d = -4.2 pts   naive 95% CI [-8.2, -0.3]   cluster 95% CI [-7.4, -1.1]   deff 0.65   b/c 24/41   McNemar p = 0.0464   clustered p = 0.00914
                                   power: MDE(80%) 4.6 pts   power to detect 5 pts = 87%
                                   non-inferiority (margin 5 pts): lower bound -7.4 -> cannot claim parity   one-sided p = 0.323
                                   tokens 7984 vs 17179  (-53.5%, 95% CI [-55.8%, -51.3%])
N=4   tourney - baseline           d = -8.0 pts   naive 95% CI [-12.2, -3.8]   cluster 95% CI [-13.4, -2.6]   deff 1.63   b/c 22/54   McNemar p = 0.000313   clustered p = 0.00362
                                   power: MDE(80%) 7.7 pts   power to detect 5 pts = 44%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -13.4 -> cannot claim parity   one-sided p = 0.862
                                   tokens 12525 vs 34192  (-63.4%, 95% CI [-65.4%, -61.3%])
N=8   tourney - baseline           d = -10.0 pts   naive 95% CI [-15.0, -5.0]   cluster 95% CI [-15.0, -5.0]   deff 1.00   b/c 4/24   McNemar p = 0.00018   clustered p = 9.51e-05
                                   power: MDE(80%) 7.2 pts   power to detect 5 pts = 50%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -15.0 -> cannot claim parity   one-sided p = 0.974
                                   tokens 25051 vs 67682  (-63.0%, 95% CI [-65.1%, -60.9%])
N=16  tourney - baseline           d = -1.0 pts   naive 95% CI [-8.6, +6.6]   cluster 95% CI [-8.6, +6.6]   deff 0.99   b/c 7/8   McNemar p = 1   clustered p = 0.797
                                   power: MDE(80%) 10.9 pts   power to detect 5 pts = 25%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -8.6 -> cannot claim parity   one-sided p = 0.152
                                   tokens 49978 vs 133659  (-62.6%, 95% CI [-64.9%, -60.4%])

N=1   random - baseline            d = +2.2 pts   naive 95% CI [-1.5, +6.0]   cluster 95% CI [-1.8, +6.3]   deff 1.16   b/c 34/25   McNemar p = 0.298   clustered p = 0.278
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 67%
                                   non-inferiority (margin 5 pts): lower bound -1.8 -> NON-INFERIOR   one-sided p = 0.000238
                                   tokens 5864 vs 8417  (-30.3%, 95% CI [-34.5%, -26.2%])
N=2   random - baseline            d = -7.8 pts   naive 95% CI [-12.0, -3.5]   cluster 95% CI [-11.5, -4.0]   deff 0.77   b/c 24/55   McNemar p = 0.000639   clustered p = 6.27e-05
                                   power: MDE(80%) 5.4 pts   power to detect 5 pts = 73%
                                   non-inferiority (margin 5 pts): lower bound -11.5 -> cannot claim parity   one-sided p = 0.922
                                   tokens 8137 vs 17179  (-52.6%, 95% CI [-55.1%, -50.2%])
N=4   random - baseline            d = -15.5 pts   naive 95% CI [-20.2, -10.8]   cluster 95% CI [-20.9, -10.1]   deff 1.34   b/c 19/81   McNemar p = 2.7e-10   clustered p = 2.2e-08
                                   power: MDE(80%) 7.8 pts   power to detect 5 pts = 44%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -20.9 -> cannot claim parity   one-sided p = 1
                                   tokens 12531 vs 34192  (-63.3%, 95% CI [-65.5%, -61.2%])
N=8   random - baseline            d = -13.0 pts   naive 95% CI [-18.8, -7.2]   cluster 95% CI [-18.7, -7.3]   deff 0.96   b/c 6/32   McNemar p = 2.43e-05   clustered p = 7.22e-06
                                   power: MDE(80%) 8.1 pts   power to detect 5 pts = 41%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -18.7 -> cannot claim parity   one-sided p = 0.997
                                   tokens 25399 vs 67682  (-62.5%, 95% CI [-64.7%, -60.2%])
N=16  random - baseline            d = -8.0 pts   naive 95% CI [-17.1, +1.1]   cluster 95% CI [-17.1, +1.1]   deff 0.99   b/c 7/15   McNemar p = 0.134   clustered p = 0.085
                                   power: MDE(80%) 13.0 pts   power to detect 5 pts = 19%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -17.1 -> cannot claim parity   one-sided p = 0.741
                                   tokens 50887 vs 133659  (-61.9%, 95% CI [-64.3%, -59.6%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = +3.7 pts   naive 95% CI [+1.7, +5.8]   cluster 95% CI [+1.6, +5.9]   deff 1.11   b/c 153/97   McNemar p = 0.00048   clustered p = 0.000773
                                   power: MDE(80%) 3.1 pts   power to detect 5 pts = 99%
                                   equal-weight per N: d = +3.6 pts (from 5 cells: -0.2, +4.0, +8.0, +2.5, +4.0)

pooled rank - baseline (chunk-wtd) d = -4.1 pts   naive 95% CI [-6.2, -2.1]   cluster 95% CI [-7.2, -1.1]   deff 2.23   b/c 92/154   McNemar p = 9.3e-05   clustered p = 0.00815
                                   power: MDE(80%) 4.4 pts   power to detect 5 pts = 89%
                                   equal-weight per N: d = -4.8 pts (from 5 cells: +2.0, -3.8, -7.5, -10.5, -4.0)

pooled tourney - baseline (chunk-wtd) d = -4.1 pts   naive 95% CI [-6.1, -2.0]   cluster 95% CI [-7.0, -1.2]   deff 2.04   b/c 91/152   McNemar p = 0.00011   clustered p = 0.0061
                                   power: MDE(80%) 4.2 pts   power to detect 5 pts = 92%
                                   equal-weight per N: d = -4.2 pts (from 5 cells: +2.2, -4.2, -8.0, -10.0, -1.0)

pooled random - baseline (chunk-wtd) d = -7.9 pts   naive 95% CI [-10.1, -5.6]   cluster 95% CI [-10.6, -5.1]   deff 1.55   b/c 90/208   McNemar p = 6.51e-12   clustered p = 2.78e-08
                                   power: MDE(80%) 4.0 pts   power to detect 5 pts = 94%
                                   equal-weight per N: d = -8.4 pts (from 5 cells: +2.2, -7.8, -15.5, -13.0, -8.0)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = +2.0 pts   95% CI [-2.4, +6.4]   win/loss 24/18   p = 0.378   sign p = 0.441
                                   tokens 6000 vs 8417 (-28.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.4 -> NON-INFERIOR   one-sided p = 0.00101
                                   WARNING: -29% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 60%
rank N=2 vs baseline N=1           d = +3.2 pts   95% CI [-1.2, +7.7]   win/loss 24/13   p = 0.156   sign p = 0.0989
                                   tokens 7927 vs 8417 (-5.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.2 -> NON-INFERIOR   one-sided p = 0.000161
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 59%
rank N=4 vs baseline N=1           d = +8.0 pts   95% CI [+3.2, +12.8]   win/loss 32/12   p = 0.00101   sign p = 0.00366
                                   tokens 12154 vs 8417 (+44.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +3.2 -> NON-INFERIOR   one-sided p = 4.56e-08
                                   WARNING: +44% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.8 pts   power to detect 5 pts = 54%
rank N=8 vs baseline N=2           d = +4.5 pts   95% CI [-0.2, +9.2]   win/loss 26/7   p = 0.0601   sign p = 0.00132
                                   tokens 24021 vs 17179 (+39.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -0.2 -> NON-INFERIOR   one-sided p = 3.61e-05
                                   WARNING: +40% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
rank N=16 vs baseline N=4          d = +3.0 pts   95% CI [-3.2, +9.2]   win/loss 21/14   p = 0.34   sign p = 0.311
                                   tokens 47036 vs 34192 (+37.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.2 -> NON-INFERIOR   one-sided p = 0.00547
                                   WARNING: +38% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 8.8 pts   power to detect 5 pts = 36%   <- underpowered

random N=1 vs baseline N=1         d = +2.2 pts   95% CI [-1.8, +6.3]   win/loss 18/15   p = 0.278   sign p = 0.728
                                   tokens 5864 vs 8417 (-30.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.8 -> NON-INFERIOR   one-sided p = 0.000238
                                   WARNING: -30% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 67%
random N=2 vs baseline N=1         d = -0.8 pts   95% CI [-4.4, +2.9]   win/loss 18/19   p = 0.687   sign p = 1
                                   tokens 8137 vs 8417 (-3.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.4 -> NON-INFERIOR   one-sided p = 0.0112
                                   power: MDE(80%) 5.2 pts   power to detect 5 pts = 77%
random N=4 vs baseline N=1         d = +0.0 pts   95% CI [-4.3, +4.3]   win/loss 20/20   p = 1   sign p = 1
                                   tokens 12531 vs 8417 (+48.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.3 -> NON-INFERIOR   one-sided p = 0.0121
                                   WARNING: +49% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
random N=8 vs baseline N=2         d = +2.0 pts   95% CI [-3.1, +7.1]   win/loss 25/14   p = 0.447   sign p = 0.108
                                   tokens 25399 vs 17179 (+47.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.1 -> NON-INFERIOR   one-sided p = 0.00386
                                   WARNING: +48% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 7.4 pts   power to detect 5 pts = 48%   <- underpowered
random N=16 vs baseline N=4        d = -1.0 pts   95% CI [-7.0, +5.0]   win/loss 18/18   p = 0.745   sign p = 1
                                   tokens 50887 vs 34192 (+48.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -7.0 -> cannot claim parity   one-sided p = 0.0967
                                   WARNING: +49% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 8.6 pts   power to detect 5 pts = 37%   <- underpowered

tourney N=1 vs baseline N=1        d = +2.2 pts   95% CI [-0.9, +5.4]   win/loss 17/12   p = 0.168   sign p = 0.458
                                   tokens 5869 vs 8417 (-30.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -0.9 -> NON-INFERIOR   one-sided p = 4.45e-06
                                   WARNING: -30% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 4.6 pts   power to detect 5 pts = 87%
tourney N=2 vs baseline N=1        d = +2.8 pts   95% CI [-0.4, +5.9]   win/loss 19/12   p = 0.0904   sign p = 0.281
                                   tokens 7984 vs 8417 (-5.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -0.4 -> NON-INFERIOR   one-sided p = 9.15e-07
                                   power: MDE(80%) 4.6 pts   power to detect 5 pts = 87%
tourney N=4 vs baseline N=1        d = +7.5 pts   95% CI [+2.9, +12.1]   win/loss 31/11   p = 0.00156   sign p = 0.00289
                                   tokens 12525 vs 8417 (+48.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +2.9 -> NON-INFERIOR   one-sided p = 6.7e-08
                                   WARNING: +49% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.6 pts   power to detect 5 pts = 56%
tourney N=8 vs baseline N=2        d = +5.0 pts   95% CI [+0.4, +9.6]   win/loss 23/9   p = 0.0319   sign p = 0.0201
                                   tokens 25051 vs 17179 (+45.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.4 -> NON-INFERIOR   one-sided p = 8.87e-06
                                   WARNING: +46% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 57%
tourney N=16 vs baseline N=4       d = +6.0 pts   95% CI [-0.5, +12.5]   win/loss 25/11   p = 0.0721   sign p = 0.0288
                                   tokens 49978 vs 34192 (+46.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -0.5 -> NON-INFERIOR   one-sided p = 0.000487
                                   WARNING: +46% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 9.3 pts   power to detect 5 pts = 32%   <- underpowered

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

############################################################################################################
# CONFIG  plan=4000  prune=1.5
############################################################################################################
============================================================================================================
FILES
  baseline  2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json
  random    2026-07-19_02-46-39_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_4000_prune_1.5.json
  rank      2026-07-19_02-45-52_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_4000_prune_1.5.json
  tourney   2026-07-19_02-47-25_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_4000_prune_1.5.json
  N values: [1, 2, 4, 8, 16]

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16
baseline      47.5%   8417t    54.5%  17179t    63.0%  34192t    69.5%  67682t    70.0% 133659t
rank          48.2%   6194t    52.2%   8933t    62.3%  18071t    67.5%  38611t    67.0%  76481t
random        45.8%   6011t    48.5%   9019t    55.8%  18661t    65.0%  40211t    67.0%  79499t
tourney       46.5%   6048t    50.5%   8943t    61.3%  17884t    67.0%  38569t    66.0%  75978t

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
rank N=2: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=4: judge - random           d = +8.8 pts   naive 95% CI [+5.9, +11.6]   cluster 95% CI [+5.8, +11.7]   deff 1.02   b/c 36/1   McNemar p = 5.53e-10   clustered p = 3.47e-09
                                   power: MDE(80%) 4.1 pts   power to detect 5 pts = 92%
rank N=8: judge - random           d = +18.0 pts   naive 95% CI [+12.0, +24.0]   cluster 95% CI [+11.4, +24.6]   deff 1.19   b/c 40/4   McNemar p = 1.71e-08   clustered p = 9.43e-08
                                   power: MDE(80%) 9.4 pts   power to detect 5 pts = 32%   <- underpowered; a null here is NOT evidence of no effect
rank N=16: judge - random          d = +23.0 pts   naive 95% CI [+13.4, +32.6]   cluster 95% CI [+13.4, +32.6]   deff 0.99   b/c 26/3   McNemar p = 1.52e-05   clustered p = 2.6e-06
                                   power: MDE(80%) 13.7 pts   power to detect 5 pts = 17%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=4: judge - random         d = +7.0 pts   naive 95% CI [+3.9, +10.1]   cluster 95% CI [+3.7, +10.3]   deff 1.15   b/c 35/7   McNemar p = 1.51e-05   clustered p = 4.12e-05
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 83%
random N=8: judge - random         d = +19.0 pts   naive 95% CI [+13.5, +24.5]   cluster 95% CI [+13.1, +24.9]   deff 1.15   b/c 38/0   McNemar p = 7.28e-12   clustered p = 2.29e-10
                                   power: MDE(80%) 8.4 pts   power to detect 5 pts = 39%   <- underpowered; a null here is NOT evidence of no effect
random N=16: judge - random        d = +21.0 pts   naive 95% CI [+11.6, +30.4]   cluster 95% CI [+11.6, +30.4]   deff 0.99   b/c 24/3   McNemar p = 4.92e-05   clustered p = 1.1e-05
                                   power: MDE(80%) 13.4 pts   power to detect 5 pts = 18%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=4: judge - random        d = +8.0 pts   naive 95% CI [+5.3, +10.7]   cluster 95% CI [+4.9, +11.1]   deff 1.35   b/c 32/0   McNemar p = 4.66e-10   clustered p = 4.43e-07
                                   power: MDE(80%) 4.4 pts   power to detect 5 pts = 88%
tourney N=8: judge - random        d = +15.0 pts   naive 95% CI [+9.8, +20.2]   cluster 95% CI [+9.2, +20.8]   deff 1.27   b/c 31/1   McNemar p = 1.54e-08   clustered p = 4.52e-07
                                   power: MDE(80%) 8.3 pts   power to detect 5 pts = 39%   <- underpowered; a null here is NOT evidence of no effect
tourney N=16: judge - random       d = +10.0 pts   naive 95% CI [+1.0, +19.0]   cluster 95% CI [+1.0, +19.0]   deff 0.99   b/c 16/6   McNemar p = 0.0525   clustered p = 0.0299
                                   power: MDE(80%) 12.9 pts   power to detect 5 pts = 19%   <- underpowered; a null here is NOT evidence of no effect

============================================================================================================
3. ORACLE CEILING   (a correct candidate EXISTS vs the judge FINDS it)
   NOTE: for pruned arms this is pass@k over SURVIVORS, not over all N.
   Only the baseline row is a clean best-of-N ceiling.

baseline   N=1   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
baseline   N=2   ceiling  57.0%   selected  54.5%   gap  2.5 pts   capture  95.6%
baseline   N=4   ceiling  66.2%   selected  63.0%   gap  3.2 pts   capture  95.1%
baseline   N=8   ceiling  73.5%   selected  69.5%   gap  4.0 pts   capture  94.6%
baseline   N=16  ceiling  79.0%   selected  70.0%   gap  9.0 pts   capture  88.6%

rank       N=1   ceiling  48.2%   selected  48.2%   gap  0.0 pts   capture 100.0%
rank       N=2   ceiling  52.2%   selected  52.2%   gap  0.0 pts   capture 100.0%
rank       N=4   ceiling  62.7%   selected  62.3%   gap  0.5 pts   capture  99.2%
rank       N=8   ceiling  70.5%   selected  67.5%   gap  3.0 pts   capture  95.7%
rank       N=16  ceiling  75.0%   selected  67.0%   gap  8.0 pts   capture  89.3%

random     N=1   ceiling  45.8%   selected  45.8%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  48.5%   selected  48.5%   gap  0.0 pts   capture 100.0%
random     N=4   ceiling  59.0%   selected  55.8%   gap  3.2 pts   capture  94.5%
random     N=8   ceiling  65.5%   selected  65.0%   gap  0.5 pts   capture  99.2%
random     N=16  ceiling  74.0%   selected  67.0%   gap  7.0 pts   capture  90.5%

tourney    N=1   ceiling  46.5%   selected  46.5%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  50.5%   selected  50.5%   gap  0.0 pts   capture 100.0%
tourney    N=4   ceiling  61.5%   selected  61.3%   gap  0.2 pts   capture  99.6%
tourney    N=8   ceiling  70.0%   selected  67.0%   gap  3.0 pts   capture  95.7%
tourney    N=16  ceiling  76.0%   selected  66.0%   gap 10.0 pts   capture  86.8%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = +2.5 pts   naive 95% CI [+0.1, +4.9]   cluster 95% CI [+0.1, +4.9]   deff 0.97   b/c 17/7   McNemar p = 0.0639   clustered p = 0.038
                                   power: MDE(80%) 3.4 pts   power to detect 5 pts = 99%
                                   non-inferiority (margin 5 pts): lower bound +0.1 -> NON-INFERIOR   one-sided p = 2.42e-10
                                   tokens 6194 vs 6011  (+3.0%, 95% CI [+1.0%, +5.1%])
N=2   rank - random                d = +3.8 pts   naive 95% CI [+0.3, +7.2]   cluster 95% CI [+0.3, +7.2]   deff 0.96   b/c 33/18   McNemar p = 0.0489   clustered p = 0.0326
                                   power: MDE(80%) 4.9 pts   power to detect 5 pts = 81%
                                   non-inferiority (margin 5 pts): lower bound +0.3 -> NON-INFERIOR   one-sided p = 3.06e-07
                                   tokens 8933 vs 9019  (-0.9%, 95% CI [-3.1%, +1.2%])
N=4   rank - random                d = +6.5 pts   naive 95% CI [+2.8, +10.2]   cluster 95% CI [+2.2, +10.8]   deff 1.32   b/c 43/17   McNemar p = 0.00107   clustered p = 0.00324
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
                                   non-inferiority (margin 5 pts): lower bound +2.2 -> NON-INFERIOR   one-sided p = 9.55e-08
                                   tokens 18071 vs 18661  (-3.2%, 95% CI [-5.0%, -1.3%])
N=8   rank - random                d = +2.5 pts   naive 95% CI [-2.0, +7.0]   cluster 95% CI [-1.8, +6.8]   deff 0.89   b/c 13/8   McNemar p = 0.383   clustered p = 0.251
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
                                   non-inferiority (margin 5 pts): lower bound -1.8 -> NON-INFERIOR   one-sided p = 0.000284
                                   tokens 38611 vs 40211  (-4.0%, 95% CI [-5.6%, -2.3%])
N=16  rank - random                d = +0.0 pts   naive 95% CI [-6.8, +6.8]   cluster 95% CI [-6.8, +6.8]   deff 0.99   b/c 6/6   McNemar p = 1   clustered p = 1
                                   power: MDE(80%) 9.8 pts   power to detect 5 pts = 30%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -6.8 -> cannot claim parity   one-sided p = 0.0755
                                   tokens 76481 vs 79499  (-3.8%, 95% CI [-5.5%, -2.1%])

N=1   rank - baseline              d = +0.8 pts   naive 95% CI [-2.5, +4.0]   cluster 95% CI [-2.5, +4.0]   deff 0.95   b/c 24/21   McNemar p = 0.766   clustered p = 0.649
                                   power: MDE(80%) 4.6 pts   power to detect 5 pts = 86%
                                   non-inferiority (margin 5 pts): lower bound -2.5 -> NON-INFERIOR   one-sided p = 0.000238
                                   tokens 6194 vs 8417  (-26.4%, 95% CI [-30.0%, -22.8%])
N=2   rank - baseline              d = -2.2 pts   naive 95% CI [-5.5, +1.0]   cluster 95% CI [-5.7, +1.2]   deff 1.12   b/c 17/26   McNemar p = 0.222   clustered p = 0.197
                                   power: MDE(80%) 4.9 pts   power to detect 5 pts = 82%
                                   non-inferiority (margin 5 pts): lower bound -5.7 -> cannot claim parity   one-sided p = 0.0574
                                   tokens 8933 vs 17179  (-48.0%, 95% CI [-50.2%, -45.8%])
N=4   rank - baseline              d = -0.8 pts   naive 95% CI [-4.3, +2.8]   cluster 95% CI [-4.9, +3.4]   deff 1.39   b/c 24/27   McNemar p = 0.78   clustered p = 0.723
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
                                   non-inferiority (margin 5 pts): lower bound -4.9 -> NON-INFERIOR   one-sided p = 0.0223
                                   tokens 18071 vs 34192  (-47.1%, 95% CI [-49.2%, -45.1%])
N=8   rank - baseline              d = -2.0 pts   naive 95% CI [-6.8, +2.8]   cluster 95% CI [-6.8, +2.8]   deff 0.99   b/c 10/14   McNemar p = 0.541   clustered p = 0.415
                                   power: MDE(80%) 6.9 pts   power to detect 5 pts = 53%
                                   non-inferiority (margin 5 pts): lower bound -6.8 -> cannot claim parity   one-sided p = 0.111
                                   tokens 38611 vs 67682  (-43.0%, 95% CI [-45.0%, -40.9%])
N=16  rank - baseline              d = -3.0 pts   naive 95% CI [-10.1, +4.1]   cluster 95% CI [-10.1, +4.1]   deff 0.99   b/c 5/8   McNemar p = 0.581   clustered p = 0.406
                                   power: MDE(80%) 10.1 pts   power to detect 5 pts = 28%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -10.1 -> cannot claim parity   one-sided p = 0.29
                                   tokens 76481 vs 133659  (-42.8%, 95% CI [-45.0%, -40.6%])

N=1   tourney - baseline           d = -1.0 pts   naive 95% CI [-4.2, +2.2]   cluster 95% CI [-4.3, +2.3]   deff 1.09   b/c 19/23   McNemar p = 0.644   clustered p = 0.557
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 84%
                                   non-inferiority (margin 5 pts): lower bound -4.3 -> NON-INFERIOR   one-sided p = 0.00935
                                   tokens 6048 vs 8417  (-28.2%, 95% CI [-31.6%, -24.8%])
N=2   tourney - baseline           d = -4.0 pts   naive 95% CI [-7.3, -0.7]   cluster 95% CI [-7.8, -0.2]   deff 1.31   b/c 15/31   McNemar p = 0.0259   clustered p = 0.0389
                                   power: MDE(80%) 5.4 pts   power to detect 5 pts = 73%
                                   non-inferiority (margin 5 pts): lower bound -7.8 -> cannot claim parity   one-sided p = 0.303
                                   tokens 8943 vs 17179  (-47.9%, 95% CI [-50.2%, -45.7%])
N=4   tourney - baseline           d = -1.8 pts   naive 95% CI [-5.2, +1.7]   cluster 95% CI [-5.2, +1.7]   deff 0.99   b/c 21/28   McNemar p = 0.392   clustered p = 0.317
                                   power: MDE(80%) 4.9 pts   power to detect 5 pts = 82%
                                   non-inferiority (margin 5 pts): lower bound -5.2 -> cannot claim parity   one-sided p = 0.0316
                                   tokens 17884 vs 34192  (-47.7%, 95% CI [-49.8%, -45.6%])
N=8   tourney - baseline           d = -2.5 pts   naive 95% CI [-7.0, +2.0]   cluster 95% CI [-7.2, +2.2]   deff 1.08   b/c 8/13   McNemar p = 0.383   clustered p = 0.297
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
                                   non-inferiority (margin 5 pts): lower bound -7.2 -> cannot claim parity   one-sided p = 0.148
                                   tokens 38569 vs 67682  (-43.0%, 95% CI [-45.0%, -41.0%])
N=16  tourney - baseline           d = -4.0 pts   naive 95% CI [-11.3, +3.3]   cluster 95% CI [-11.3, +3.3]   deff 0.99   b/c 5/9   McNemar p = 0.424   clustered p = 0.285
                                   power: MDE(80%) 10.5 pts   power to detect 5 pts = 27%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -11.3 -> cannot claim parity   one-sided p = 0.395
                                   tokens 75978 vs 133659  (-43.2%, 95% CI [-45.2%, -41.1%])

N=1   random - baseline            d = -1.8 pts   naive 95% CI [-5.0, +1.5]   cluster 95% CI [-5.3, +1.8]   deff 1.17   b/c 19/26   McNemar p = 0.371   clustered p = 0.336
                                   power: MDE(80%) 5.1 pts   power to detect 5 pts = 78%
                                   non-inferiority (margin 5 pts): lower bound -5.3 -> cannot claim parity   one-sided p = 0.0371
                                   tokens 6011 vs 8417  (-28.6%, 95% CI [-31.9%, -25.2%])
N=2   random - baseline            d = -6.0 pts   naive 95% CI [-10.1, -1.9]   cluster 95% CI [-10.2, -1.8]   deff 1.05   b/c 23/47   McNemar p = 0.00558   clustered p = 0.00496
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 65%
                                   non-inferiority (margin 5 pts): lower bound -10.2 -> cannot claim parity   one-sided p = 0.68
                                   tokens 9019 vs 17179  (-47.5%, 95% CI [-50.1%, -44.9%])
N=4   random - baseline            d = -7.2 pts   naive 95% CI [-11.1, -3.4]   cluster 95% CI [-11.7, -2.8]   deff 1.32   b/c 17/46   McNemar p = 0.000337   clustered p = 0.00131
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 60%
                                   non-inferiority (margin 5 pts): lower bound -11.7 -> cannot claim parity   one-sided p = 0.841
                                   tokens 18661 vs 34192  (-45.4%, 95% CI [-47.8%, -43.0%])
N=8   random - baseline            d = -4.5 pts   naive 95% CI [-9.2, +0.2]   cluster 95% CI [-9.1, +0.1]   deff 0.98   b/c 7/16   McNemar p = 0.0931   clustered p = 0.0573
                                   power: MDE(80%) 6.6 pts   power to detect 5 pts = 56%
                                   non-inferiority (margin 5 pts): lower bound -9.1 -> cannot claim parity   one-sided p = 0.416
                                   tokens 40211 vs 67682  (-40.6%, 95% CI [-43.1%, -38.1%])
N=16  random - baseline            d = -3.0 pts   naive 95% CI [-11.1, +5.1]   cluster 95% CI [-11.1, +5.1]   deff 0.99   b/c 7/10   McNemar p = 0.629   clustered p = 0.468
                                   power: MDE(80%) 11.6 pts   power to detect 5 pts = 23%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -11.1 -> cannot claim parity   one-sided p = 0.314
                                   tokens 79499 vs 133659  (-40.5%, 95% CI [-43.0%, -38.0%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = +3.7 pts   naive 95% CI [+2.0, +5.4]   cluster 95% CI [+1.9, +5.6]   deff 1.21   b/c 112/56   McNemar p = 1.86e-05   clustered p = 8.37e-05
                                   power: MDE(80%) 2.7 pts   power to detect 5 pts = 100%
                                   equal-weight per N: d = +3.0 pts (from 5 cells: +2.5, +3.8, +6.5, +2.5, +0.0)

pooled rank - baseline (chunk-wtd) d = -1.1 pts   naive 95% CI [-2.8, +0.7]   cluster 95% CI [-3.5, +1.4]   deff 1.96   b/c 80/96   McNemar p = 0.258   clustered p = 0.392
                                   power: MDE(80%) 3.5 pts   power to detect 5 pts = 98%
                                   equal-weight per N: d = -1.4 pts (from 5 cells: +0.8, -2.2, -0.8, -2.0, -3.0)

pooled tourney - baseline (chunk-wtd) d = -2.4 pts   naive 95% CI [-4.1, -0.7]   cluster 95% CI [-4.7, -0.1]   deff 1.85   b/c 68/104   McNemar p = 0.00743   clustered p = 0.0443
                                   power: MDE(80%) 3.3 pts   power to detect 5 pts = 99%
                                   equal-weight per N: d = -2.7 pts (from 5 cells: -1.0, -4.0, -1.8, -2.5, -4.0)

pooled random - baseline (chunk-wtd) d = -4.8 pts   naive 95% CI [-6.7, -2.9]   cluster 95% CI [-7.5, -2.1]   deff 2.00   b/c 73/145   McNemar p = 1.23e-06   clustered p = 0.000552
                                   power: MDE(80%) 3.9 pts   power to detect 5 pts = 95%
                                   equal-weight per N: d = -4.5 pts (from 5 cells: -1.8, -6.0, -7.2, -4.5, -3.0)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = +0.8 pts   95% CI [-2.5, +4.0]   win/loss 17/14   p = 0.649   sign p = 0.72
                                   tokens 6194 vs 8417 (-26.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.5 -> NON-INFERIOR   one-sided p = 0.000238
                                   WARNING: -26% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 4.6 pts   power to detect 5 pts = 86%
rank N=2 vs baseline N=1           d = +4.8 pts   95% CI [+1.1, +8.4]   win/loss 29/12   p = 0.0111   sign p = 0.0115
                                   tokens 8933 vs 8417 (+6.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +1.1 -> NON-INFERIOR   one-sided p = 9.24e-08
                                   power: MDE(80%) 5.2 pts   power to detect 5 pts = 76%
rank N=4 vs baseline N=2           d = +7.8 pts   95% CI [+3.5, +12.0]   win/loss 30/7   p = 0.000318   sign p = 0.000191
                                   tokens 18071 vs 17179 (+5.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +3.5 -> NON-INFERIOR   one-sided p = 1.58e-09
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 64%
rank N=8 vs baseline N=4           d = +4.5 pts   95% CI [+0.0, +9.0]   win/loss 22/12   p = 0.049   sign p = 0.121
                                   tokens 38611 vs 34192 (+12.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.0 -> NON-INFERIOR   one-sided p = 1.62e-05
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 59%
rank N=16 vs baseline N=8          d = -2.5 pts   95% CI [-8.6, +3.6]   win/loss 10/11   p = 0.424   sign p = 1
                                   tokens 76481 vs 67682 (+13.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -8.6 -> cannot claim parity   one-sided p = 0.212
                                   power: MDE(80%) 8.8 pts   power to detect 5 pts = 36%   <- underpowered

random N=1 vs baseline N=1         d = -1.8 pts   95% CI [-5.3, +1.8]   win/loss 15/20   p = 0.336   sign p = 0.5
                                   tokens 6011 vs 8417 (-28.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.3 -> cannot claim parity   one-sided p = 0.0371
                                   WARNING: -29% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.1 pts   power to detect 5 pts = 78%
random N=2 vs baseline N=1         d = +1.0 pts   95% CI [-2.9, +4.9]   win/loss 19/16   p = 0.618   sign p = 0.736
                                   tokens 9019 vs 8417 (+7.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.9 -> NON-INFERIOR   one-sided p = 0.0014
                                   power: MDE(80%) 5.6 pts   power to detect 5 pts = 70%
random N=4 vs baseline N=2         d = +1.2 pts   95% CI [-3.1, +5.6]   win/loss 19/15   p = 0.57   sign p = 0.608
                                   tokens 18661 vs 17179 (+8.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.1 -> NON-INFERIOR   one-sided p = 0.00226
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
random N=8 vs baseline N=4         d = +2.0 pts   95% CI [-2.4, +6.4]   win/loss 19/13   p = 0.378   sign p = 0.377
                                   tokens 40211 vs 34192 (+17.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.4 -> NON-INFERIOR   one-sided p = 0.00101
                                   WARNING: +18% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 60%
random N=16 vs baseline N=8        d = -2.5 pts   95% CI [-8.6, +3.6]   win/loss 9/12   p = 0.424   sign p = 0.664
                                   tokens 79499 vs 67682 (+17.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -8.6 -> cannot claim parity   one-sided p = 0.212
                                   WARNING: +17% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 8.8 pts   power to detect 5 pts = 36%   <- underpowered

tourney N=1 vs baseline N=1        d = -1.0 pts   95% CI [-4.3, +2.3]   win/loss 16/18   p = 0.557   sign p = 0.864
                                   tokens 6048 vs 8417 (-28.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.3 -> NON-INFERIOR   one-sided p = 0.00935
                                   WARNING: -28% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 84%
tourney N=2 vs baseline N=1        d = +3.0 pts   95% CI [-0.9, +6.9]   win/loss 25/12   p = 0.131   sign p = 0.047
                                   tokens 8943 vs 8417 (+6.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -0.9 -> NON-INFERIOR   one-sided p = 2.84e-05
                                   power: MDE(80%) 5.6 pts   power to detect 5 pts = 71%
tourney N=4 vs baseline N=2        d = +6.8 pts   95% CI [+3.1, +10.4]   win/loss 31/7   p = 0.000319   sign p = 0.000116
                                   tokens 17884 vs 17179 (+4.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +3.1 -> NON-INFERIOR   one-sided p = 1.86e-10
                                   power: MDE(80%) 5.3 pts   power to detect 5 pts = 76%
tourney N=8 vs baseline N=4        d = +4.0 pts   95% CI [-0.7, +8.7]   win/loss 20/11   p = 0.0959   sign p = 0.15
                                   tokens 38569 vs 34192 (+12.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -0.7 -> NON-INFERIOR   one-sided p = 8.99e-05
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
tourney N=16 vs baseline N=8       d = -3.5 pts   95% CI [-9.3, +2.3]   win/loss 8/12   p = 0.236   sign p = 0.503
                                   tokens 75978 vs 67682 (+12.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -9.3 -> cannot claim parity   one-sided p = 0.306
                                   power: MDE(80%) 8.3 pts   power to detect 5 pts = 40%   <- underpowered

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

############################################################################################################
# CONFIG  plan=4000  prune=2.0
############################################################################################################
============================================================================================================
FILES
  baseline  2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json
  random    2026-07-18_23-54-12_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_4000_prune_2.0.json
  rank      2026-07-18_23-53-27_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_4000_prune_2.0.json
  tourney   2026-07-18_23-54-58_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_4000_prune_2.0.json
  N values: [1, 2, 4, 8, 16]

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16
baseline      47.5%   8417t    54.5%  17179t    63.0%  34192t    69.5%  67682t    70.0% 133659t
rank          48.2%   6194t    51.5%   8952t    60.0%  18137t    64.0%  35465t    71.0%  70465t
random        45.8%   6010t    45.5%   9178t    53.5%  18947t    62.5%  37241t    66.0%  73139t
tourney       47.0%   5989t    51.7%   9026t    60.0%  18156t    68.0%  35900t    64.0%  71954t

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
rank N=2: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=4: judge - random           d = +9.0 pts   naive 95% CI [+6.0, +12.0]   cluster 95% CI [+5.6, +12.4]   deff 1.28   b/c 38/2   McNemar p = 1.49e-09   clustered p = 1.76e-07
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 83%
rank N=8: judge - random           d = +12.0 pts   naive 95% CI [+7.1, +16.9]   cluster 95% CI [+7.2, +16.8]   deff 0.96   b/c 26/2   McNemar p = 3.03e-06   clustered p = 1.23e-06
                                   power: MDE(80%) 6.9 pts   power to detect 5 pts = 52%
rank N=16: judge - random          d = +20.0 pts   naive 95% CI [+12.1, +27.9]   cluster 95% CI [+12.1, +27.9]   deff 0.99   b/c 20/0   McNemar p = 1.91e-06   clustered p = 6.53e-07
                                   power: MDE(80%) 11.3 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=4: judge - random         d = +8.2 pts   naive 95% CI [+5.0, +11.5]   cluster 95% CI [+4.8, +11.7]   deff 1.08   b/c 40/7   McNemar p = 1.07e-06   clustered p = 2.2e-06
                                   power: MDE(80%) 4.9 pts   power to detect 5 pts = 82%
random N=8: judge - random         d = +13.0 pts   naive 95% CI [+7.7, +18.3]   cluster 95% CI [+7.2, +18.8]   deff 1.23   b/c 29/3   McNemar p = 2.56e-06   clustered p = 1.31e-05
                                   power: MDE(80%) 8.4 pts   power to detect 5 pts = 39%   <- underpowered; a null here is NOT evidence of no effect
random N=16: judge - random        d = +15.0 pts   naive 95% CI [+6.5, +23.5]   cluster 95% CI [+6.5, +23.5]   deff 0.99   b/c 18/3   McNemar p = 0.00149   clustered p = 0.000567
                                   power: MDE(80%) 12.2 pts   power to detect 5 pts = 21%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=4: judge - random        d = +7.2 pts   naive 95% CI [+4.5, +10.0]   cluster 95% CI [+4.2, +10.3]   deff 1.25   b/c 31/2   McNemar p = 1.31e-07   clustered p = 3.4e-06
                                   power: MDE(80%) 4.4 pts   power to detect 5 pts = 89%
tourney N=8: judge - random        d = +14.5 pts   naive 95% CI [+9.4, +19.6]   cluster 95% CI [+8.7, +20.3]   deff 1.28   b/c 30/1   McNemar p = 2.98e-08   clustered p = 9.29e-07
                                   power: MDE(80%) 8.3 pts   power to detect 5 pts = 39%   <- underpowered; a null here is NOT evidence of no effect
tourney N=16: judge - random       d = +11.0 pts   naive 95% CI [+3.2, +18.8]   cluster 95% CI [+3.2, +18.8]   deff 0.99   b/c 14/3   McNemar p = 0.0127   clustered p = 0.00588
                                   power: MDE(80%) 11.2 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect

============================================================================================================
3. ORACLE CEILING   (a correct candidate EXISTS vs the judge FINDS it)
   NOTE: for pruned arms this is pass@k over SURVIVORS, not over all N.
   Only the baseline row is a clean best-of-N ceiling.

baseline   N=1   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
baseline   N=2   ceiling  57.0%   selected  54.5%   gap  2.5 pts   capture  95.6%
baseline   N=4   ceiling  66.2%   selected  63.0%   gap  3.2 pts   capture  95.1%
baseline   N=8   ceiling  73.5%   selected  69.5%   gap  4.0 pts   capture  94.6%
baseline   N=16  ceiling  79.0%   selected  70.0%   gap  9.0 pts   capture  88.6%

rank       N=1   ceiling  48.2%   selected  48.2%   gap  0.0 pts   capture 100.0%
rank       N=2   ceiling  51.5%   selected  51.5%   gap  0.0 pts   capture 100.0%
rank       N=4   ceiling  60.5%   selected  60.0%   gap  0.5 pts   capture  99.2%
rank       N=8   ceiling  67.0%   selected  64.0%   gap  3.0 pts   capture  95.5%
rank       N=16  ceiling  76.0%   selected  71.0%   gap  5.0 pts   capture  93.4%

random     N=1   ceiling  45.8%   selected  45.8%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  45.5%   selected  45.5%   gap  0.0 pts   capture 100.0%
random     N=4   ceiling  56.0%   selected  53.5%   gap  2.5 pts   capture  95.5%
random     N=8   ceiling  65.5%   selected  62.5%   gap  3.0 pts   capture  95.4%
random     N=16  ceiling  72.0%   selected  66.0%   gap  6.0 pts   capture  91.7%

tourney    N=1   ceiling  47.0%   selected  47.0%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  51.7%   selected  51.7%   gap  0.0 pts   capture 100.0%
tourney    N=4   ceiling  60.5%   selected  60.0%   gap  0.5 pts   capture  99.2%
tourney    N=8   ceiling  68.5%   selected  68.0%   gap  0.5 pts   capture  99.3%
tourney    N=16  ceiling  74.0%   selected  64.0%   gap 10.0 pts   capture  86.5%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = +2.5 pts   naive 95% CI [+0.1, +4.9]   cluster 95% CI [+0.1, +4.9]   deff 0.97   b/c 17/7   McNemar p = 0.0639   clustered p = 0.038
                                   power: MDE(80%) 3.4 pts   power to detect 5 pts = 99%
                                   non-inferiority (margin 5 pts): lower bound +0.1 -> NON-INFERIOR   one-sided p = 2.42e-10
                                   tokens 6194 vs 6010  (+3.1%, 95% CI [+1.0%, +5.1%])
N=2   rank - random                d = +6.0 pts   naive 95% CI [+2.7, +9.3]   cluster 95% CI [+2.2, +9.8]   deff 1.29   b/c 36/12   McNemar p = 0.000717   clustered p = 0.00209
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 73%
                                   non-inferiority (margin 5 pts): lower bound +2.2 -> NON-INFERIOR   one-sided p = 8.47e-09
                                   tokens 8952 vs 9178  (-2.5%, 95% CI [-4.5%, -0.4%])
N=4   rank - random                d = +6.5 pts   naive 95% CI [+3.0, +10.0]   cluster 95% CI [+2.6, +10.4]   deff 1.17   b/c 40/14   McNemar p = 0.000535   clustered p = 0.000947
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 72%
                                   non-inferiority (margin 5 pts): lower bound +2.6 -> NON-INFERIOR   one-sided p = 2.48e-09
                                   tokens 18137 vs 18947  (-4.3%, 95% CI [-6.1%, -2.4%])
N=8   rank - random                d = +1.5 pts   naive 95% CI [-3.2, +6.2]   cluster 95% CI [-3.2, +6.2]   deff 0.99   b/c 13/10   McNemar p = 0.678   clustered p = 0.533
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
                                   non-inferiority (margin 5 pts): lower bound -3.2 -> NON-INFERIOR   one-sided p = 0.00344
                                   tokens 35465 vs 37241  (-4.8%, 95% CI [-6.6%, -2.9%])
N=16  rank - random                d = +5.0 pts   naive 95% CI [-2.6, +12.6]   cluster 95% CI [-2.6, +12.6]   deff 0.99   b/c 10/5   McNemar p = 0.302   clustered p = 0.195
                                   power: MDE(80%) 10.8 pts   power to detect 5 pts = 25%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -2.6 -> NON-INFERIOR   one-sided p = 0.00479
                                   tokens 70465 vs 73139  (-3.7%, 95% CI [-5.4%, -1.9%])

N=1   rank - baseline              d = +0.8 pts   naive 95% CI [-2.5, +4.0]   cluster 95% CI [-2.5, +4.0]   deff 0.95   b/c 24/21   McNemar p = 0.766   clustered p = 0.649
                                   power: MDE(80%) 4.6 pts   power to detect 5 pts = 86%
                                   non-inferiority (margin 5 pts): lower bound -2.5 -> NON-INFERIOR   one-sided p = 0.000238
                                   tokens 6194 vs 8417  (-26.4%, 95% CI [-30.0%, -22.8%])
N=2   rank - baseline              d = -3.0 pts   naive 95% CI [-6.2, +0.2]   cluster 95% CI [-6.7, +0.7]   deff 1.29   b/c 16/28   McNemar p = 0.0961   clustered p = 0.112
                                   power: MDE(80%) 5.3 pts   power to detect 5 pts = 75%
                                   non-inferiority (margin 5 pts): lower bound -6.7 -> cannot claim parity   one-sided p = 0.145
                                   tokens 8952 vs 17179  (-47.9%, 95% CI [-50.1%, -45.7%])
N=4   rank - baseline              d = -3.0 pts   naive 95% CI [-6.7, +0.7]   cluster 95% CI [-7.3, +1.3]   deff 1.34   b/c 22/34   McNemar p = 0.141   clustered p = 0.167
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
                                   non-inferiority (margin 5 pts): lower bound -7.3 -> cannot claim parity   one-sided p = 0.178
                                   tokens 18137 vs 34192  (-47.0%, 95% CI [-49.0%, -44.9%])
N=8   rank - baseline              d = -5.5 pts   naive 95% CI [-10.1, -0.9]   cluster 95% CI [-10.3, -0.7]   deff 1.06   b/c 6/17   McNemar p = 0.0347   clustered p = 0.0248
                                   power: MDE(80%) 6.9 pts   power to detect 5 pts = 53%
                                   non-inferiority (margin 5 pts): lower bound -10.3 -> cannot claim parity   one-sided p = 0.581
                                   tokens 35465 vs 67682  (-47.6%, 95% CI [-49.7%, -45.5%])
N=16  rank - baseline              d = +1.0 pts   naive 95% CI [-6.6, +8.6]   cluster 95% CI [-6.6, +8.6]   deff 0.99   b/c 8/7   McNemar p = 1   clustered p = 0.797
                                   power: MDE(80%) 10.9 pts   power to detect 5 pts = 25%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -6.6 -> cannot claim parity   one-sided p = 0.0615
                                   tokens 70465 vs 133659  (-47.3%, 95% CI [-49.4%, -45.2%])

N=1   tourney - baseline           d = -0.5 pts   naive 95% CI [-3.8, +2.8]   cluster 95% CI [-4.2, +3.2]   deff 1.21   b/c 22/24   McNemar p = 0.883   clustered p = 0.79
                                   power: MDE(80%) 5.3 pts   power to detect 5 pts = 76%
                                   non-inferiority (margin 5 pts): lower bound -4.2 -> NON-INFERIOR   one-sided p = 0.00833
                                   tokens 5989 vs 8417  (-28.9%, 95% CI [-32.3%, -25.4%])
N=2   tourney - baseline           d = -2.8 pts   naive 95% CI [-6.1, +0.6]   cluster 95% CI [-6.6, +1.1]   deff 1.32   b/c 18/29   McNemar p = 0.144   clustered p = 0.164
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 72%
                                   non-inferiority (margin 5 pts): lower bound -6.6 -> cannot claim parity   one-sided p = 0.127
                                   tokens 9026 vs 17179  (-47.5%, 95% CI [-49.7%, -45.2%])
N=4   tourney - baseline           d = -3.0 pts   naive 95% CI [-6.3, +0.3]   cluster 95% CI [-7.0, +1.0]   deff 1.45   b/c 17/29   McNemar p = 0.104   clustered p = 0.143
                                   power: MDE(80%) 5.7 pts   power to detect 5 pts = 68%
                                   non-inferiority (margin 5 pts): lower bound -7.0 -> cannot claim parity   one-sided p = 0.165
                                   tokens 18156 vs 34192  (-46.9%, 95% CI [-48.9%, -44.9%])
N=8   tourney - baseline           d = -1.5 pts   naive 95% CI [-6.0, +3.0]   cluster 95% CI [-5.8, +2.8]   deff 0.90   b/c 9/12   McNemar p = 0.664   clustered p = 0.492
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
                                   non-inferiority (margin 5 pts): lower bound -5.8 -> cannot claim parity   one-sided p = 0.0546
                                   tokens 35900 vs 67682  (-47.0%, 95% CI [-49.2%, -44.7%])
N=16  tourney - baseline           d = -6.0 pts   naive 95% CI [-14.3, +2.3]   cluster 95% CI [-14.3, +2.3]   deff 0.99   b/c 6/12   McNemar p = 0.238   clustered p = 0.155
                                   power: MDE(80%) 11.8 pts   power to detect 5 pts = 22%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -14.3 -> cannot claim parity   one-sided p = 0.594
                                   tokens 71954 vs 133659  (-46.2%, 95% CI [-48.4%, -44.0%])

N=1   random - baseline            d = -1.8 pts   naive 95% CI [-5.0, +1.5]   cluster 95% CI [-5.3, +1.8]   deff 1.17   b/c 19/26   McNemar p = 0.371   clustered p = 0.336
                                   power: MDE(80%) 5.1 pts   power to detect 5 pts = 78%
                                   non-inferiority (margin 5 pts): lower bound -5.3 -> cannot claim parity   one-sided p = 0.0371
                                   tokens 6010 vs 8417  (-28.6%, 95% CI [-31.9%, -25.2%])
N=2   random - baseline            d = -9.0 pts   naive 95% CI [-12.8, -5.2]   cluster 95% CI [-12.8, -5.2]   deff 1.00   b/c 13/49   McNemar p = 4.82e-06   clustered p = 3.14e-06
                                   power: MDE(80%) 5.4 pts   power to detect 5 pts = 74%
                                   non-inferiority (margin 5 pts): lower bound -12.8 -> cannot claim parity   one-sided p = 0.981
                                   tokens 9178 vs 17179  (-46.6%, 95% CI [-49.0%, -44.1%])
N=4   random - baseline            d = -9.5 pts   naive 95% CI [-13.6, -5.4]   cluster 95% CI [-14.3, -4.7]   deff 1.36   b/c 17/55   McNemar p = 8.14e-06   clustered p = 9.27e-05
                                   power: MDE(80%) 6.8 pts   power to detect 5 pts = 54%
                                   non-inferiority (margin 5 pts): lower bound -14.3 -> cannot claim parity   one-sided p = 0.968
                                   tokens 18947 vs 34192  (-44.6%, 95% CI [-47.1%, -42.1%])
N=8   random - baseline            d = -7.0 pts   naive 95% CI [-12.1, -1.9]   cluster 95% CI [-12.6, -1.4]   deff 1.18   b/c 7/21   McNemar p = 0.0125   clustered p = 0.0139
                                   power: MDE(80%) 8.0 pts   power to detect 5 pts = 42%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -12.6 -> cannot claim parity   one-sided p = 0.759
                                   tokens 37241 vs 67682  (-45.0%, 95% CI [-47.6%, -42.4%])
N=16  random - baseline            d = -4.0 pts   naive 95% CI [-11.8, +3.8]   cluster 95% CI [-11.8, +3.8]   deff 0.99   b/c 6/10   McNemar p = 0.454   clustered p = 0.317
                                   power: MDE(80%) 11.2 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -11.8 -> cannot claim parity   one-sided p = 0.401
                                   tokens 73139 vs 133659  (-45.3%, 95% CI [-47.7%, -42.9%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = +4.5 pts   naive 95% CI [+2.9, +6.2]   cluster 95% CI [+2.3, +6.8]   deff 1.82   b/c 116/48   McNemar p = 1.12e-07   clustered p = 7.89e-05
                                   power: MDE(80%) 3.2 pts   power to detect 5 pts = 99%
                                   equal-weight per N: d = +4.3 pts (from 5 cells: +2.5, +6.0, +6.5, +1.5, +5.0)

pooled rank - baseline (chunk-wtd) d = -2.1 pts   naive 95% CI [-3.8, -0.3]   cluster 95% CI [-4.7, +0.5]   deff 2.16   b/c 76/107   McNemar p = 0.0263   clustered p = 0.12
                                   power: MDE(80%) 3.7 pts   power to detect 5 pts = 96%
                                   equal-weight per N: d = -1.9 pts (from 5 cells: +0.8, -3.0, -3.0, -5.5, +1.0)

pooled tourney - baseline (chunk-wtd) d = -2.3 pts   naive 95% CI [-4.0, -0.5]   cluster 95% CI [-4.9, +0.4]   deff 2.34   b/c 72/106   McNemar p = 0.0132   clustered p = 0.0966
                                   power: MDE(80%) 3.8 pts   power to detect 5 pts = 96%
                                   equal-weight per N: d = -2.7 pts (from 5 cells: -0.5, -2.8, -3.0, -1.5, -6.0)

pooled random - baseline (chunk-wtd) d = -6.6 pts   naive 95% CI [-8.5, -4.7]   cluster 95% CI [-9.4, -3.8]   deff 2.09   b/c 62/161   McNemar p = 2.49e-11   clustered p = 3.69e-06
                                   power: MDE(80%) 4.0 pts   power to detect 5 pts = 94%
                                   equal-weight per N: d = -6.2 pts (from 5 cells: -1.8, -9.0, -9.5, -7.0, -4.0)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = +0.8 pts   95% CI [-2.5, +4.0]   win/loss 17/14   p = 0.649   sign p = 0.72
                                   tokens 6194 vs 8417 (-26.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.5 -> NON-INFERIOR   one-sided p = 0.000238
                                   WARNING: -26% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 4.6 pts   power to detect 5 pts = 86%
rank N=2 vs baseline N=1           d = +4.0 pts   95% CI [-0.3, +8.3]   win/loss 30/13   p = 0.0668   sign p = 0.0137
                                   tokens 8952 vs 8417 (+6.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -0.3 -> NON-INFERIOR   one-sided p = 1.86e-05
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
rank N=4 vs baseline N=2           d = +5.5 pts   95% CI [+1.9, +9.1]   win/loss 27/10   p = 0.00268   sign p = 0.00763
                                   tokens 18137 vs 17179 (+5.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +1.9 -> NON-INFERIOR   one-sided p = 4.97e-09
                                   power: MDE(80%) 5.1 pts   power to detect 5 pts = 78%
rank N=8 vs baseline N=4           d = +1.0 pts   95% CI [-4.1, +6.1]   win/loss 18/16   p = 0.699   sign p = 0.864
                                   tokens 35465 vs 34192 (+3.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.1 -> NON-INFERIOR   one-sided p = 0.0101
                                   power: MDE(80%) 7.2 pts   power to detect 5 pts = 49%   <- underpowered
rank N=16 vs baseline N=8          d = +1.5 pts   95% CI [-4.3, +7.3]   win/loss 11/9   p = 0.613   sign p = 0.824
                                   tokens 70465 vs 67682 (+4.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.3 -> NON-INFERIOR   one-sided p = 0.0143
                                   power: MDE(80%) 8.3 pts   power to detect 5 pts = 39%   <- underpowered

random N=1 vs baseline N=1         d = -1.8 pts   95% CI [-5.3, +1.8]   win/loss 15/20   p = 0.336   sign p = 0.5
                                   tokens 6010 vs 8417 (-28.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.3 -> cannot claim parity   one-sided p = 0.0371
                                   WARNING: -29% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.1 pts   power to detect 5 pts = 78%
random N=2 vs baseline N=1         d = -2.0 pts   95% CI [-5.6, +1.6]   win/loss 16/21   p = 0.276   sign p = 0.511
                                   tokens 9178 vs 8417 (+9.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.6 -> cannot claim parity   one-sided p = 0.0511
                                   power: MDE(80%) 5.1 pts   power to detect 5 pts = 78%
random N=4 vs baseline N=2         d = -1.0 pts   95% CI [-4.7, +2.7]   win/loss 18/16   p = 0.601   sign p = 0.864
                                   tokens 18947 vs 17179 (+10.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.7 -> NON-INFERIOR   one-sided p = 0.0182
                                   power: MDE(80%) 5.4 pts   power to detect 5 pts = 74%
random N=8 vs baseline N=4         d = -0.5 pts   95% CI [-5.5, +4.5]   win/loss 16/17   p = 0.844   sign p = 1
                                   tokens 37241 vs 34192 (+8.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.5 -> cannot claim parity   one-sided p = 0.0381
                                   power: MDE(80%) 7.1 pts   power to detect 5 pts = 50%
random N=16 vs baseline N=8        d = -3.5 pts   95% CI [-9.3, +2.3]   win/loss 8/12   p = 0.236   sign p = 0.503
                                   tokens 73139 vs 67682 (+8.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -9.3 -> cannot claim parity   one-sided p = 0.306
                                   power: MDE(80%) 8.3 pts   power to detect 5 pts = 40%   <- underpowered

tourney N=1 vs baseline N=1        d = -0.5 pts   95% CI [-4.2, +3.2]   win/loss 17/18   p = 0.79   sign p = 1
                                   tokens 5989 vs 8417 (-28.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.2 -> NON-INFERIOR   one-sided p = 0.00833
                                   WARNING: -29% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.3 pts   power to detect 5 pts = 76%
tourney N=2 vs baseline N=1        d = +4.2 pts   95% CI [+0.1, +8.4]   win/loss 24/12   p = 0.0434   sign p = 0.0652
                                   tokens 9026 vs 8417 (+7.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.1 -> NON-INFERIOR   one-sided p = 5.49e-06
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
tourney N=4 vs baseline N=2        d = +5.5 pts   95% CI [+2.0, +9.0]   win/loss 26/6   p = 0.00221   sign p = 0.000535
                                   tokens 18156 vs 17179 (+5.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +2.0 -> NON-INFERIOR   one-sided p = 2.57e-09
                                   power: MDE(80%) 5.0 pts   power to detect 5 pts = 79%
tourney N=8 vs baseline N=4        d = +5.0 pts   95% CI [+0.2, +9.8]   win/loss 22/12   p = 0.0401   sign p = 0.121
                                   tokens 35900 vs 34192 (+5.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.2 -> NON-INFERIOR   one-sided p = 2.02e-05
                                   power: MDE(80%) 6.8 pts   power to detect 5 pts = 54%
tourney N=16 vs baseline N=8       d = -5.5 pts   95% CI [-12.7, +1.7]   win/loss 9/16   p = 0.136   sign p = 0.23
                                   tokens 71954 vs 67682 (+6.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -12.7 -> cannot claim parity   one-sided p = 0.554
                                   power: MDE(80%) 10.3 pts   power to detect 5 pts = 27%   <- underpowered

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

############################################################################################################
# CONFIG  plan=4000  prune=3.0
############################################################################################################
============================================================================================================
FILES
  baseline  2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json
  random    2026-07-18_17-21-03_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_4000_prune_3.0.json
  rank      2026-07-18_17-20-18_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_4000_prune_3.0.json
  tourney   2026-07-18_17-21-47_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_4000_prune_3.0.json
  N values: [1, 2, 4, 8, 16]

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16
baseline      47.5%   8417t    54.5%  17179t    63.0%  34192t    69.5%  67682t    70.0% 133659t
rank          47.0%   6205t    50.0%   9086t    56.5%  15276t    65.0%  29866t    66.0%  60715t
random        47.2%   5980t    47.5%   9353t    48.2%  15666t    54.5%  31665t    64.0%  65839t
tourney       47.0%   5990t    49.8%   8999t    57.2%  15501t    63.0%  30857t    72.0%  63473t

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
rank N=2: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=4: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=8: judge - random           d = +6.0 pts   naive 95% CI [+2.4, +9.6]   cluster 95% CI [+2.5, +9.5]   deff 0.94   b/c 13/1   McNemar p = 0.00183   clustered p = 0.000754
                                   power: MDE(80%) 5.0 pts   power to detect 5 pts = 80%
rank N=16: judge - random          d = +8.0 pts   naive 95% CI [+0.8, +15.2]   cluster 95% CI [+0.8, +15.2]   deff 0.99   b/c 11/3   McNemar p = 0.0574   clustered p = 0.0294
                                   power: MDE(80%) 10.3 pts   power to detect 5 pts = 27%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=4: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=8: judge - random         d = +9.0 pts   naive 95% CI [+4.8, +13.2]   cluster 95% CI [+5.0, +13.0]   deff 0.91   b/c 19/1   McNemar p = 4.01e-05   clustered p = 1.22e-05
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 68%
random N=16: judge - random        d = +16.0 pts   naive 95% CI [+7.8, +24.2]   cluster 95% CI [+7.8, +24.2]   deff 0.99   b/c 18/2   McNemar p = 0.000402   clustered p = 0.000138
                                   power: MDE(80%) 11.8 pts   power to detect 5 pts = 22%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=4: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=8: judge - random        d = +6.5 pts   naive 95% CI [+2.1, +10.9]   cluster 95% CI [+1.7, +11.3]   deff 1.15   b/c 17/4   McNemar p = 0.0072   clustered p = 0.00738
                                   power: MDE(80%) 6.8 pts   power to detect 5 pts = 54%
tourney N=16: judge - random       d = +16.0 pts   naive 95% CI [+8.8, +23.2]   cluster 95% CI [+8.8, +23.2]   deff 0.99   b/c 16/0   McNemar p = 3.05e-05   clustered p = 1.41e-05
                                   power: MDE(80%) 10.3 pts   power to detect 5 pts = 27%   <- underpowered; a null here is NOT evidence of no effect

============================================================================================================
3. ORACLE CEILING   (a correct candidate EXISTS vs the judge FINDS it)
   NOTE: for pruned arms this is pass@k over SURVIVORS, not over all N.
   Only the baseline row is a clean best-of-N ceiling.

baseline   N=1   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
baseline   N=2   ceiling  57.0%   selected  54.5%   gap  2.5 pts   capture  95.6%
baseline   N=4   ceiling  66.2%   selected  63.0%   gap  3.2 pts   capture  95.1%
baseline   N=8   ceiling  73.5%   selected  69.5%   gap  4.0 pts   capture  94.6%
baseline   N=16  ceiling  79.0%   selected  70.0%   gap  9.0 pts   capture  88.6%

rank       N=1   ceiling  47.0%   selected  47.0%   gap  0.0 pts   capture 100.0%
rank       N=2   ceiling  50.0%   selected  50.0%   gap  0.0 pts   capture 100.0%
rank       N=4   ceiling  56.5%   selected  56.5%   gap  0.0 pts   capture 100.0%
rank       N=8   ceiling  65.5%   selected  65.0%   gap  0.5 pts   capture  99.2%
rank       N=16  ceiling  72.0%   selected  66.0%   gap  6.0 pts   capture  91.7%

random     N=1   ceiling  47.2%   selected  47.2%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
random     N=4   ceiling  48.2%   selected  48.2%   gap  0.0 pts   capture 100.0%
random     N=8   ceiling  55.5%   selected  54.5%   gap  1.0 pts   capture  98.2%
random     N=16  ceiling  68.0%   selected  64.0%   gap  4.0 pts   capture  94.1%

tourney    N=1   ceiling  47.0%   selected  47.0%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  49.8%   selected  49.8%   gap  0.0 pts   capture 100.0%
tourney    N=4   ceiling  57.2%   selected  57.2%   gap  0.0 pts   capture 100.0%
tourney    N=8   ceiling  65.5%   selected  63.0%   gap  2.5 pts   capture  96.2%
tourney    N=16  ceiling  73.0%   selected  72.0%   gap  1.0 pts   capture  98.6%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = -0.2 pts   naive 95% CI [-1.7, +1.2]   cluster 95% CI [-1.7, +1.2]   deff 1.00   b/c 4/5   McNemar p = 1   clustered p = 0.74
                                   power: MDE(80%) 2.1 pts   power to detect 5 pts = 100%
                                   non-inferiority (margin 5 pts): lower bound -1.7 -> NON-INFERIOR   one-sided p = 1.44e-10
                                   tokens 6205 vs 5980  (+3.8%, 95% CI [+2.5%, +5.0%])
N=2   rank - random                d = +2.5 pts   naive 95% CI [-1.1, +6.1]   cluster 95% CI [-1.6, +6.6]   deff 1.32   b/c 32/22   McNemar p = 0.22   clustered p = 0.238
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
                                   non-inferiority (margin 5 pts): lower bound -1.6 -> NON-INFERIOR   one-sided p = 0.000198
                                   tokens 9086 vs 9353  (-2.8%, 95% CI [-5.2%, -0.5%])
N=4   rank - random                d = +8.2 pts   naive 95% CI [+4.4, +12.1]   cluster 95% CI [+4.4, +12.1]   deff 1.03   b/c 48/15   McNemar p = 3.76e-05   clustered p = 3.1e-05
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 71%
                                   non-inferiority (margin 5 pts): lower bound +4.4 -> NON-INFERIOR   one-sided p = 1.11e-11
                                   tokens 15276 vs 15666  (-2.5%, 95% CI [-4.0%, -0.9%])
N=8   rank - random                d = +10.5 pts   naive 95% CI [+4.7, +16.3]   cluster 95% CI [+4.4, +16.6]   deff 1.10   b/c 29/8   McNemar p = 0.000753   clustered p = 0.000769
                                   power: MDE(80%) 8.7 pts   power to detect 5 pts = 36%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound +4.4 -> NON-INFERIOR   one-sided p = 3.43e-07
                                   tokens 29866 vs 31665  (-5.7%, 95% CI [-7.3%, -4.0%])
N=16  rank - random                d = +2.0 pts   naive 95% CI [-5.4, +9.4]   cluster 95% CI [-5.4, +9.4]   deff 0.99   b/c 8/6   McNemar p = 0.791   clustered p = 0.594
                                   power: MDE(80%) 10.5 pts   power to detect 5 pts = 26%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -5.4 -> cannot claim parity   one-sided p = 0.0312
                                   tokens 60715 vs 65839  (-7.8%, 95% CI [-9.5%, -6.0%])

N=1   rank - baseline              d = -0.5 pts   naive 95% CI [-3.8, +2.8]   cluster 95% CI [-4.2, +3.2]   deff 1.21   b/c 22/24   McNemar p = 0.883   clustered p = 0.79
                                   power: MDE(80%) 5.3 pts   power to detect 5 pts = 76%
                                   non-inferiority (margin 5 pts): lower bound -4.2 -> NON-INFERIOR   one-sided p = 0.00833
                                   tokens 6205 vs 8417  (-26.3%, 95% CI [-29.9%, -22.7%])
N=2   rank - baseline              d = -4.5 pts   naive 95% CI [-8.0, -1.0]   cluster 95% CI [-8.6, -0.4]   deff 1.34   b/c 17/35   McNemar p = 0.0175   clustered p = 0.0308
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 67%
                                   non-inferiority (margin 5 pts): lower bound -8.6 -> cannot claim parity   one-sided p = 0.405
                                   tokens 9086 vs 17179  (-47.1%, 95% CI [-49.4%, -44.8%])
N=4   rank - baseline              d = -6.5 pts   naive 95% CI [-10.0, -3.0]   cluster 95% CI [-10.6, -2.4]   deff 1.37   b/c 13/39   McNemar p = 0.00041   clustered p = 0.00188
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 67%
                                   non-inferiority (margin 5 pts): lower bound -10.6 -> cannot claim parity   one-sided p = 0.763
                                   tokens 15276 vs 34192  (-55.3%, 95% CI [-57.6%, -53.1%])
N=8   rank - baseline              d = -4.5 pts   naive 95% CI [-9.4, +0.4]   cluster 95% CI [-9.5, +0.5]   deff 1.06   b/c 8/17   McNemar p = 0.108   clustered p = 0.0802
                                   power: MDE(80%) 7.2 pts   power to detect 5 pts = 49%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -9.5 -> cannot claim parity   one-sided p = 0.423
                                   tokens 29866 vs 67682  (-55.9%, 95% CI [-58.2%, -53.6%])
N=16  rank - baseline              d = -4.0 pts   naive 95% CI [-12.8, +4.8]   cluster 95% CI [-12.8, +4.8]   deff 0.99   b/c 8/12   McNemar p = 0.503   clustered p = 0.372
                                   power: MDE(80%) 12.5 pts   power to detect 5 pts = 20%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -12.8 -> cannot claim parity   one-sided p = 0.412
                                   tokens 60715 vs 133659  (-54.6%, 95% CI [-56.7%, -52.4%])

N=1   tourney - baseline           d = -0.5 pts   naive 95% CI [-3.8, +2.8]   cluster 95% CI [-4.2, +3.2]   deff 1.21   b/c 22/24   McNemar p = 0.883   clustered p = 0.79
                                   power: MDE(80%) 5.3 pts   power to detect 5 pts = 76%
                                   non-inferiority (margin 5 pts): lower bound -4.2 -> NON-INFERIOR   one-sided p = 0.00833
                                   tokens 5990 vs 8417  (-28.8%, 95% CI [-32.3%, -25.4%])
N=2   tourney - baseline           d = -4.8 pts   naive 95% CI [-8.2, -1.3]   cluster 95% CI [-8.9, -0.6]   deff 1.48   b/c 15/34   McNemar p = 0.0094   clustered p = 0.0253
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 65%
                                   non-inferiority (margin 5 pts): lower bound -8.9 -> cannot claim parity   one-sided p = 0.453
                                   tokens 8999 vs 17179  (-47.6%, 95% CI [-50.0%, -45.2%])
N=4   tourney - baseline           d = -5.8 pts   naive 95% CI [-9.2, -2.3]   cluster 95% CI [-9.8, -1.7]   deff 1.36   b/c 14/37   McNemar p = 0.00177   clustered p = 0.00542
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 68%
                                   non-inferiority (margin 5 pts): lower bound -9.8 -> cannot claim parity   one-sided p = 0.642
                                   tokens 15501 vs 34192  (-54.7%, 95% CI [-57.0%, -52.3%])
N=8   tourney - baseline           d = -6.5 pts   naive 95% CI [-11.5, -1.5]   cluster 95% CI [-11.5, -1.5]   deff 0.96   b/c 7/20   McNemar p = 0.0192   clustered p = 0.0101
                                   power: MDE(80%) 7.1 pts   power to detect 5 pts = 51%
                                   non-inferiority (margin 5 pts): lower bound -11.5 -> cannot claim parity   one-sided p = 0.724
                                   tokens 30857 vs 67682  (-54.4%, 95% CI [-56.8%, -52.0%])
N=16  tourney - baseline           d = +2.0 pts   naive 95% CI [-5.4, +9.4]   cluster 95% CI [-5.4, +9.4]   deff 0.99   b/c 8/6   McNemar p = 0.791   clustered p = 0.594
                                   power: MDE(80%) 10.5 pts   power to detect 5 pts = 26%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -5.4 -> cannot claim parity   one-sided p = 0.0312
                                   tokens 63473 vs 133659  (-52.5%, 95% CI [-54.8%, -50.2%])

N=1   random - baseline            d = -0.2 pts   naive 95% CI [-3.5, +3.0]   cluster 95% CI [-3.8, +3.3]   deff 1.13   b/c 22/23   McNemar p = 1   clustered p = 0.889
                                   power: MDE(80%) 5.0 pts   power to detect 5 pts = 80%
                                   non-inferiority (margin 5 pts): lower bound -3.8 -> NON-INFERIOR   one-sided p = 0.00405
                                   tokens 5980 vs 8417  (-29.0%, 95% CI [-32.3%, -25.7%])
N=2   random - baseline            d = -7.0 pts   naive 95% CI [-10.7, -3.3]   cluster 95% CI [-11.5, -2.5]   deff 1.46   b/c 15/43   McNemar p = 0.000307   clustered p = 0.00212
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 59%
                                   non-inferiority (margin 5 pts): lower bound -11.5 -> cannot claim parity   one-sided p = 0.81
                                   tokens 9353 vs 17179  (-45.6%, 95% CI [-48.2%, -42.9%])
N=4   random - baseline            d = -14.8 pts   naive 95% CI [-18.9, -10.6]   cluster 95% CI [-19.4, -10.1]   deff 1.25   b/c 10/69   McNemar p = 5.54e-12   clustered p = 4.07e-10
                                   power: MDE(80%) 6.6 pts   power to detect 5 pts = 56%
                                   non-inferiority (margin 5 pts): lower bound -19.4 -> cannot claim parity   one-sided p = 1
                                   tokens 15666 vs 34192  (-54.2%, 95% CI [-56.6%, -51.8%])
N=8   random - baseline            d = -15.0 pts   naive 95% CI [-20.9, -9.1]   cluster 95% CI [-20.5, -9.5]   deff 0.87   b/c 5/35   McNemar p = 1.38e-06   clustered p = 8.27e-08
                                   power: MDE(80%) 7.8 pts   power to detect 5 pts = 43%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -20.5 -> cannot claim parity   one-sided p = 1
                                   tokens 31665 vs 67682  (-53.2%, 95% CI [-55.8%, -50.7%])
N=16  random - baseline            d = -6.0 pts   naive 95% CI [-15.2, +3.2]   cluster 95% CI [-15.2, +3.2]   deff 0.99   b/c 8/14   McNemar p = 0.286   clustered p = 0.199
                                   power: MDE(80%) 13.1 pts   power to detect 5 pts = 19%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -15.2 -> cannot claim parity   one-sided p = 0.585
                                   tokens 65839 vs 133659  (-50.7%, 95% CI [-53.3%, -48.1%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = +4.3 pts   naive 95% CI [+2.6, +6.1]   cluster 95% CI [+2.0, +6.7]   deff 1.82   b/c 121/56   McNemar p = 1.15e-06   clustered p = 0.000279
                                   power: MDE(80%) 3.3 pts   power to detect 5 pts = 99%
                                   equal-weight per N: d = +4.6 pts (from 5 cells: -0.2, +2.5, +8.2, +10.5, +2.0)

pooled rank - baseline (chunk-wtd) d = -3.9 pts   naive 95% CI [-5.7, -2.1]   cluster 95% CI [-6.8, -1.0]   deff 2.53   b/c 68/127   McNemar p = 2.87e-05   clustered p = 0.00789
                                   power: MDE(80%) 4.1 pts   power to detect 5 pts = 92%
                                   equal-weight per N: d = -4.0 pts (from 5 cells: -0.5, -4.5, -6.5, -4.5, -4.0)

pooled tourney - baseline (chunk-wtd) d = -3.7 pts   naive 95% CI [-5.4, -1.9]   cluster 95% CI [-6.5, -0.8]   deff 2.60   b/c 66/121   McNemar p = 7.03e-05   clustered p = 0.0126
                                   power: MDE(80%) 4.1 pts   power to detect 5 pts = 93%
                                   equal-weight per N: d = -3.1 pts (from 5 cells: -0.5, -4.8, -5.8, -6.5, +2.0)

pooled random - baseline (chunk-wtd) d = -8.3 pts   naive 95% CI [-10.3, -6.3]   cluster 95% CI [-11.2, -5.4]   deff 2.08   b/c 60/184   McNemar p = 7.9e-16   clustered p = 2.2e-08
                                   power: MDE(80%) 4.1 pts   power to detect 5 pts = 92%
                                   equal-weight per N: d = -8.6 pts (from 5 cells: -0.2, -7.0, -14.8, -15.0, -6.0)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = -0.5 pts   95% CI [-4.2, +3.2]   win/loss 17/18   p = 0.79   sign p = 1
                                   tokens 6205 vs 8417 (-26.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.2 -> NON-INFERIOR   one-sided p = 0.00833
                                   WARNING: -26% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.3 pts   power to detect 5 pts = 76%
rank N=2 vs baseline N=1           d = +2.5 pts   95% CI [-1.8, +6.8]   win/loss 28/16   p = 0.251   sign p = 0.0961
                                   tokens 9086 vs 8417 (+7.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.8 -> NON-INFERIOR   one-sided p = 0.000284
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
rank N=4 vs baseline N=2           d = +2.0 pts   95% CI [-1.4, +5.4]   win/loss 18/10   p = 0.247   sign p = 0.185
                                   tokens 15276 vs 17179 (-11.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.4 -> NON-INFERIOR   one-sided p = 2.58e-05
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 82%
rank N=8 vs baseline N=4           d = +2.0 pts   95% CI [-2.7, +6.7]   win/loss 17/15   p = 0.4   sign p = 0.86
                                   tokens 29866 vs 34192 (-12.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.7 -> NON-INFERIOR   one-sided p = 0.0016
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 56%
rank N=16 vs baseline N=8          d = -3.5 pts   95% CI [-9.3, +2.3]   win/loss 7/13   p = 0.236   sign p = 0.263
                                   tokens 60715 vs 67682 (-10.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -9.3 -> cannot claim parity   one-sided p = 0.306
                                   power: MDE(80%) 8.3 pts   power to detect 5 pts = 40%   <- underpowered

random N=1 vs baseline N=1         d = -0.2 pts   95% CI [-3.8, +3.3]   win/loss 17/19   p = 0.889   sign p = 0.868
                                   tokens 5980 vs 8417 (-29.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.8 -> NON-INFERIOR   one-sided p = 0.00405
                                   WARNING: -29% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.0 pts   power to detect 5 pts = 80%
random N=2 vs baseline N=1         d = +0.0 pts   95% CI [-4.5, +4.5]   win/loss 21/22   p = 1   sign p = 1
                                   tokens 9353 vs 8417 (+11.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.5 -> NON-INFERIOR   one-sided p = 0.015
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 58%
random N=4 vs baseline N=2         d = -6.2 pts   95% CI [-9.8, -2.7]   win/loss 8/24   p = 0.000615   sign p = 0.007
                                   tokens 15666 vs 17179 (-8.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -9.8 -> cannot claim parity   one-sided p = 0.753
                                   power: MDE(80%) 5.1 pts   power to detect 5 pts = 78%
random N=8 vs baseline N=4         d = -8.5 pts   95% CI [-14.1, -2.9]   win/loss 10/28   p = 0.00306   sign p = 0.0051
                                   tokens 31665 vs 34192 (-7.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -14.1 -> cannot claim parity   one-sided p = 0.889
                                   power: MDE(80%) 8.0 pts   power to detect 5 pts = 41%   <- underpowered
random N=16 vs baseline N=8        d = -5.5 pts   95% CI [-12.7, +1.7]   win/loss 10/15   p = 0.136   sign p = 0.424
                                   tokens 65839 vs 67682 (-2.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -12.7 -> cannot claim parity   one-sided p = 0.554
                                   power: MDE(80%) 10.3 pts   power to detect 5 pts = 27%   <- underpowered

tourney N=1 vs baseline N=1        d = -0.5 pts   95% CI [-4.2, +3.2]   win/loss 17/18   p = 0.79   sign p = 1
                                   tokens 5990 vs 8417 (-28.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.2 -> NON-INFERIOR   one-sided p = 0.00833
                                   WARNING: -29% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.3 pts   power to detect 5 pts = 76%
tourney N=2 vs baseline N=1        d = +2.2 pts   95% CI [-1.9, +6.4]   win/loss 26/16   p = 0.285   sign p = 0.164
                                   tokens 8999 vs 8417 (+6.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.9 -> NON-INFERIOR   one-sided p = 0.000286
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
tourney N=4 vs baseline N=2        d = +2.8 pts   95% CI [-0.9, +6.4]   win/loss 22/10   p = 0.136   sign p = 0.0501
                                   tokens 15501 vs 17179 (-9.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -0.9 -> NON-INFERIOR   one-sided p = 1.3e-05
                                   power: MDE(80%) 5.2 pts   power to detect 5 pts = 77%
tourney N=8 vs baseline N=4        d = +0.0 pts   95% CI [-4.8, +4.8]   win/loss 16/17   p = 1   sign p = 1
                                   tokens 30857 vs 34192 (-9.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.8 -> NON-INFERIOR   one-sided p = 0.0201
                                   power: MDE(80%) 6.8 pts   power to detect 5 pts = 54%
tourney N=16 vs baseline N=8       d = +2.5 pts   95% CI [-2.6, +7.6]   win/loss 11/7   p = 0.336   sign p = 0.481
                                   tokens 63473 vs 67682 (-6.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.6 -> NON-INFERIOR   one-sided p = 0.00195
                                   power: MDE(80%) 7.3 pts   power to detect 5 pts = 49%   <- underpowered

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

############################################################################################################
# CONFIG  plan=4000  prune=4.0
############################################################################################################
============================================================================================================
FILES
  baseline  2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json
  random    2026-07-18_16-37-48_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_4000_prune_4.0.json
  rank      2026-07-18_16-37-05_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_4000_prune_4.0.json
  tourney   2026-07-18_16-38-32_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_4000_prune_4.0.json
  N values: [1, 2, 4, 8, 16]

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16
baseline      47.5%   8417t    54.5%  17179t    63.0%  34192t    69.5%  67682t    70.0% 133659t
rank          47.2%   6157t    51.5%   8980t    55.0%  15253t    65.5%  29890t    70.0%  58814t
random        45.0%   6017t    47.0%   9200t    46.5%  15701t    58.5%  31796t    64.0%  62939t
tourney       47.0%   5989t    51.2%   9002t    59.0%  15393t    63.5%  30956t    64.0%  61566t

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
rank N=2: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=4: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=8: judge - random           d = +6.0 pts   naive 95% CI [+2.7, +9.3]   cluster 95% CI [+2.2, +9.8]   deff 1.28   b/c 12/0   McNemar p = 0.000488   clustered p = 0.00175
                                   power: MDE(80%) 5.4 pts   power to detect 5 pts = 74%
rank N=16: judge - random          d = +15.0 pts   naive 95% CI [+7.4, +22.6]   cluster 95% CI [+7.4, +22.6]   deff 0.99   b/c 16/1   McNemar p = 0.000275   clustered p = 0.000102
                                   power: MDE(80%) 10.8 pts   power to detect 5 pts = 25%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=4: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=8: judge - random         d = +10.0 pts   naive 95% CI [+5.6, +14.4]   cluster 95% CI [+6.1, +13.9]   deff 0.80   b/c 21/1   McNemar p = 1.1e-05   clustered p = 6.53e-07
                                   power: MDE(80%) 5.6 pts   power to detect 5 pts = 70%
random N=16: judge - random        d = +16.0 pts   naive 95% CI [+8.3, +23.7]   cluster 95% CI [+8.3, +23.7]   deff 0.99   b/c 17/1   McNemar p = 0.000145   clustered p = 5.09e-05
                                   power: MDE(80%) 11.1 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=4: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=8: judge - random        d = +5.5 pts   naive 95% CI [+2.0, +9.0]   cluster 95% CI [+2.1, +8.9]   deff 0.95   b/c 12/1   McNemar p = 0.00342   clustered p = 0.00143
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 83%
tourney N=16: judge - random       d = +5.0 pts   naive 95% CI [-2.0, +12.0]   cluster 95% CI [-2.0, +12.0]   deff 0.99   b/c 9/4   McNemar p = 0.267   clustered p = 0.164
                                   power: MDE(80%) 10.1 pts   power to detect 5 pts = 29%   <- underpowered; a null here is NOT evidence of no effect

============================================================================================================
3. ORACLE CEILING   (a correct candidate EXISTS vs the judge FINDS it)
   NOTE: for pruned arms this is pass@k over SURVIVORS, not over all N.
   Only the baseline row is a clean best-of-N ceiling.

baseline   N=1   ceiling  47.5%   selected  47.5%   gap  0.0 pts   capture 100.0%
baseline   N=2   ceiling  57.0%   selected  54.5%   gap  2.5 pts   capture  95.6%
baseline   N=4   ceiling  66.2%   selected  63.0%   gap  3.2 pts   capture  95.1%
baseline   N=8   ceiling  73.5%   selected  69.5%   gap  4.0 pts   capture  94.6%
baseline   N=16  ceiling  79.0%   selected  70.0%   gap  9.0 pts   capture  88.6%

rank       N=1   ceiling  47.2%   selected  47.2%   gap  0.0 pts   capture 100.0%
rank       N=2   ceiling  51.5%   selected  51.5%   gap  0.0 pts   capture 100.0%
rank       N=4   ceiling  55.0%   selected  55.0%   gap  0.0 pts   capture 100.0%
rank       N=8   ceiling  65.5%   selected  65.5%   gap  0.0 pts   capture 100.0%
rank       N=16  ceiling  72.0%   selected  70.0%   gap  2.0 pts   capture  97.2%

random     N=1   ceiling  45.0%   selected  45.0%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  47.0%   selected  47.0%   gap  0.0 pts   capture 100.0%
random     N=4   ceiling  46.5%   selected  46.5%   gap  0.0 pts   capture 100.0%
random     N=8   ceiling  59.5%   selected  58.5%   gap  1.0 pts   capture  98.3%
random     N=16  ceiling  67.0%   selected  64.0%   gap  3.0 pts   capture  95.5%

tourney    N=1   ceiling  47.0%   selected  47.0%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  51.2%   selected  51.2%   gap  0.0 pts   capture 100.0%
tourney    N=4   ceiling  59.0%   selected  59.0%   gap  0.0 pts   capture 100.0%
tourney    N=8   ceiling  65.5%   selected  63.5%   gap  2.0 pts   capture  96.9%
tourney    N=16  ceiling  70.0%   selected  64.0%   gap  6.0 pts   capture  91.4%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = +2.2 pts   naive 95% CI [-1.0, +5.5]   cluster 95% CI [-1.1, +5.6]   deff 1.03   b/c 27/18   McNemar p = 0.233   clustered p = 0.188
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 83%
                                   non-inferiority (margin 5 pts): lower bound -1.1 -> NON-INFERIOR   one-sided p = 1.09e-05
                                   tokens 6157 vs 6017  (+2.3%, 95% CI [-0.3%, +4.9%])
N=2   rank - random                d = +4.5 pts   naive 95% CI [+0.8, +8.2]   cluster 95% CI [+0.5, +8.5]   deff 1.13   b/c 38/20   McNemar p = 0.0247   clustered p = 0.026
                                   power: MDE(80%) 5.7 pts   power to detect 5 pts = 70%
                                   non-inferiority (margin 5 pts): lower bound +0.5 -> NON-INFERIOR   one-sided p = 1.31e-06
                                   tokens 8980 vs 9200  (-2.4%, 95% CI [-4.5%, -0.3%])
N=4   rank - random                d = +8.5 pts   naive 95% CI [+4.5, +12.5]   cluster 95% CI [+3.9, +13.1]   deff 1.32   b/c 51/17   McNemar p = 4.45e-05   clustered p = 0.000274
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 57%
                                   non-inferiority (margin 5 pts): lower bound +3.9 -> NON-INFERIOR   one-sided p = 3.76e-09
                                   tokens 15253 vs 15701  (-2.9%, 95% CI [-4.4%, -1.3%])
N=8   rank - random                d = +7.0 pts   naive 95% CI [+1.7, +12.3]   cluster 95% CI [+1.6, +12.4]   deff 1.03   b/c 22/8   McNemar p = 0.0161   clustered p = 0.011
                                   power: MDE(80%) 7.7 pts   power to detect 5 pts = 44%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound +1.6 -> NON-INFERIOR   one-sided p = 6.6e-06
                                   tokens 29890 vs 31796  (-6.0%, 95% CI [-7.8%, -4.2%])
N=16  rank - random                d = +6.0 pts   naive 95% CI [-2.3, +14.3]   cluster 95% CI [-2.3, +14.3]   deff 0.99   b/c 12/6   McNemar p = 0.238   clustered p = 0.155
                                   power: MDE(80%) 11.8 pts   power to detect 5 pts = 22%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -2.3 -> NON-INFERIOR   one-sided p = 0.00458
                                   tokens 58814 vs 62939  (-6.6%, 95% CI [-8.2%, -4.9%])

N=1   rank - baseline              d = -0.2 pts   naive 95% CI [-3.5, +3.0]   cluster 95% CI [-3.5, +3.0]   deff 0.95   b/c 22/23   McNemar p = 1   clustered p = 0.879
                                   power: MDE(80%) 4.6 pts   power to detect 5 pts = 86%
                                   non-inferiority (margin 5 pts): lower bound -3.5 -> NON-INFERIOR   one-sided p = 0.00197
                                   tokens 6157 vs 8417  (-26.8%, 95% CI [-30.6%, -23.1%])
N=2   rank - baseline              d = -3.0 pts   naive 95% CI [-6.4, +0.4]   cluster 95% CI [-6.3, +0.3]   deff 0.93   b/c 18/30   McNemar p = 0.111   clustered p = 0.0737
                                   power: MDE(80%) 4.7 pts   power to detect 5 pts = 85%
                                   non-inferiority (margin 5 pts): lower bound -6.3 -> cannot claim parity   one-sided p = 0.117
                                   tokens 8980 vs 17179  (-47.7%, 95% CI [-50.1%, -45.4%])
N=4   rank - baseline              d = -8.0 pts   naive 95% CI [-11.4, -4.6]   cluster 95% CI [-12.3, -3.7]   deff 1.57   b/c 10/42   McNemar p = 9.06e-06   clustered p = 0.000305
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
                                   non-inferiority (margin 5 pts): lower bound -12.3 -> cannot claim parity   one-sided p = 0.912
                                   tokens 15253 vs 34192  (-55.4%, 95% CI [-57.6%, -53.2%])
N=8   rank - baseline              d = -4.0 pts   naive 95% CI [-7.9, -0.1]   cluster 95% CI [-7.9, -0.1]   deff 0.97   b/c 4/12   McNemar p = 0.0768   clustered p = 0.0423
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 72%
                                   non-inferiority (margin 5 pts): lower bound -7.9 -> cannot claim parity   one-sided p = 0.306
                                   tokens 29890 vs 67682  (-55.8%, 95% CI [-58.1%, -53.5%])
N=16  rank - baseline              d = +0.0 pts   naive 95% CI [-7.9, +7.9]   cluster 95% CI [-7.9, +7.9]   deff 0.99   b/c 8/8   McNemar p = 1   clustered p = 1
                                   power: MDE(80%) 11.3 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -7.9 -> cannot claim parity   one-sided p = 0.107
                                   tokens 58814 vs 133659  (-56.0%, 95% CI [-58.2%, -53.8%])

N=1   tourney - baseline           d = -0.5 pts   naive 95% CI [-3.8, +2.8]   cluster 95% CI [-4.2, +3.2]   deff 1.21   b/c 22/24   McNemar p = 0.883   clustered p = 0.79
                                   power: MDE(80%) 5.3 pts   power to detect 5 pts = 76%
                                   non-inferiority (margin 5 pts): lower bound -4.2 -> NON-INFERIOR   one-sided p = 0.00833
                                   tokens 5989 vs 8417  (-28.9%, 95% CI [-32.3%, -25.4%])
N=2   tourney - baseline           d = -3.2 pts   naive 95% CI [-6.9, +0.4]   cluster 95% CI [-7.6, +1.1]   deff 1.41   b/c 21/34   McNemar p = 0.105   clustered p = 0.141
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
                                   non-inferiority (margin 5 pts): lower bound -7.6 -> cannot claim parity   one-sided p = 0.214
                                   tokens 9002 vs 17179  (-47.6%, 95% CI [-50.0%, -45.2%])
N=4   tourney - baseline           d = -4.0 pts   naive 95% CI [-7.6, -0.4]   cluster 95% CI [-8.1, +0.1]   deff 1.30   b/c 19/35   McNemar p = 0.0402   clustered p = 0.0561
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 67%
                                   non-inferiority (margin 5 pts): lower bound -8.1 -> cannot claim parity   one-sided p = 0.316
                                   tokens 15393 vs 34192  (-55.0%, 95% CI [-57.3%, -52.7%])
N=8   tourney - baseline           d = -6.0 pts   naive 95% CI [-10.3, -1.7]   cluster 95% CI [-10.2, -1.8]   deff 0.96   b/c 4/16   McNemar p = 0.0118   clustered p = 0.00558
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 64%
                                   non-inferiority (margin 5 pts): lower bound -10.2 -> cannot claim parity   one-sided p = 0.678
                                   tokens 30956 vs 67682  (-54.3%, 95% CI [-56.7%, -51.8%])
N=16  tourney - baseline           d = -6.0 pts   naive 95% CI [-13.8, +1.8]   cluster 95% CI [-13.8, +1.8]   deff 0.99   b/c 5/11   McNemar p = 0.21   clustered p = 0.131
                                   power: MDE(80%) 11.1 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -13.8 -> cannot claim parity   one-sided p = 0.599
                                   tokens 61566 vs 133659  (-53.9%, 95% CI [-56.4%, -51.5%])

N=1   random - baseline            d = -2.5 pts   naive 95% CI [-5.8, +0.8]   cluster 95% CI [-5.9, +0.9]   deff 1.02   b/c 18/28   McNemar p = 0.184   clustered p = 0.147
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 83%
                                   non-inferiority (margin 5 pts): lower bound -5.9 -> cannot claim parity   one-sided p = 0.0733
                                   tokens 6017 vs 8417  (-28.5%, 95% CI [-31.9%, -25.2%])
N=2   random - baseline            d = -7.5 pts   naive 95% CI [-11.5, -3.5]   cluster 95% CI [-12.0, -3.0]   deff 1.22   b/c 20/50   McNemar p = 0.00044   clustered p = 0.00105
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 59%
                                   non-inferiority (margin 5 pts): lower bound -12.0 -> cannot claim parity   one-sided p = 0.863
                                   tokens 9200 vs 17179  (-46.4%, 95% CI [-49.1%, -43.8%])
N=4   random - baseline            d = -16.5 pts   naive 95% CI [-20.8, -12.2]   cluster 95% CI [-21.7, -11.3]   deff 1.45   b/c 11/77   McNemar p = 2.4e-13   clustered p = 5.9e-10
                                   power: MDE(80%) 7.5 pts   power to detect 5 pts = 47%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -21.7 -> cannot claim parity   one-sided p = 1
                                   tokens 15701 vs 34192  (-54.1%, 95% CI [-56.5%, -51.7%])
N=8   random - baseline            d = -11.0 pts   naive 95% CI [-16.3, -5.7]   cluster 95% CI [-16.7, -5.3]   deff 1.12   b/c 5/27   McNemar p = 0.000113   clustered p = 0.000144
                                   power: MDE(80%) 8.1 pts   power to detect 5 pts = 41%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -16.7 -> cannot claim parity   one-sided p = 0.981
                                   tokens 31796 vs 67682  (-53.0%, 95% CI [-55.7%, -50.4%])
N=16  random - baseline            d = -6.0 pts   naive 95% CI [-14.3, +2.3]   cluster 95% CI [-14.3, +2.3]   deff 0.99   b/c 6/12   McNemar p = 0.238   clustered p = 0.155
                                   power: MDE(80%) 11.8 pts   power to detect 5 pts = 22%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -14.3 -> cannot claim parity   one-sided p = 0.594
                                   tokens 62939 vs 133659  (-52.9%, 95% CI [-55.5%, -50.3%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = +5.4 pts   naive 95% CI [+3.5, +7.3]   cluster 95% CI [+3.3, +7.5]   deff 1.22   b/c 150/69   McNemar p = 4.58e-08   clustered p = 6.2e-07
                                   power: MDE(80%) 3.0 pts   power to detect 5 pts = 100%
                                   equal-weight per N: d = +5.7 pts (from 5 cells: +2.2, +4.5, +8.5, +7.0, +6.0)

pooled rank - baseline (chunk-wtd) d = -3.5 pts   naive 95% CI [-5.3, -1.8]   cluster 95% CI [-6.1, -1.0]   deff 2.17   b/c 62/115   McNemar p = 8.3e-05   clustered p = 0.00689
                                   power: MDE(80%) 3.7 pts   power to detect 5 pts = 97%
                                   equal-weight per N: d = -3.0 pts (from 5 cells: -0.2, -3.0, -8.0, -4.0, +0.0)

pooled tourney - baseline (chunk-wtd) d = -3.3 pts   naive 95% CI [-5.1, -1.5]   cluster 95% CI [-6.1, -0.4]   deff 2.45   b/c 71/120   McNemar p = 0.000482   clustered p = 0.0238
                                   power: MDE(80%) 4.0 pts   power to detect 5 pts = 93%
                                   equal-weight per N: d = -4.0 pts (from 5 cells: -0.5, -3.2, -4.0, -6.0, -6.0)

pooled random - baseline (chunk-wtd) d = -8.9 pts   naive 95% CI [-11.0, -6.9]   cluster 95% CI [-11.8, -6.1]   deff 1.98   b/c 60/194   McNemar p = 1.18e-17   clustered p = 1.18e-09
                                   power: MDE(80%) 4.1 pts   power to detect 5 pts = 93%
                                   equal-weight per N: d = -8.7 pts (from 5 cells: -2.5, -7.5, -16.5, -11.0, -6.0)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = -0.2 pts   95% CI [-3.5, +3.0]   win/loss 15/13   p = 0.879   sign p = 0.851
                                   tokens 6157 vs 8417 (-26.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.5 -> NON-INFERIOR   one-sided p = 0.00197
                                   WARNING: -27% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 4.6 pts   power to detect 5 pts = 86%
rank N=2 vs baseline N=1           d = +4.0 pts   95% CI [+0.3, +7.7]   win/loss 27/15   p = 0.0357   sign p = 0.0884
                                   tokens 8980 vs 8417 (+6.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.3 -> NON-INFERIOR   one-sided p = 1.14e-06
                                   power: MDE(80%) 5.3 pts   power to detect 5 pts = 75%
rank N=4 vs baseline N=2           d = +0.5 pts   95% CI [-3.2, +4.2]   win/loss 19/15   p = 0.794   sign p = 0.608
                                   tokens 15253 vs 17179 (-11.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.2 -> NON-INFERIOR   one-sided p = 0.00202
                                   power: MDE(80%) 5.4 pts   power to detect 5 pts = 74%
rank N=8 vs baseline N=4           d = +2.5 pts   95% CI [-2.2, +7.2]   win/loss 20/13   p = 0.302   sign p = 0.296
                                   tokens 29890 vs 34192 (-12.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.2 -> NON-INFERIOR   one-sided p = 0.000983
                                   power: MDE(80%) 6.8 pts   power to detect 5 pts = 54%
rank N=16 vs baseline N=8          d = +0.5 pts   95% CI [-5.7, +6.7]   win/loss 10/11   p = 0.873   sign p = 1
                                   tokens 58814 vs 67682 (-13.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.7 -> cannot claim parity   one-sided p = 0.0398
                                   power: MDE(80%) 8.8 pts   power to detect 5 pts = 36%   <- underpowered

random N=1 vs baseline N=1         d = -2.5 pts   95% CI [-5.9, +0.9]   win/loss 13/20   p = 0.147   sign p = 0.296
                                   tokens 6017 vs 8417 (-28.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.9 -> cannot claim parity   one-sided p = 0.0733
                                   WARNING: -29% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 83%
random N=2 vs baseline N=1         d = -0.5 pts   95% CI [-5.2, +4.2]   win/loss 21/21   p = 0.834   sign p = 1
                                   tokens 9200 vs 8417 (+9.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.2 -> cannot claim parity   one-sided p = 0.0295
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
random N=4 vs baseline N=2         d = -8.0 pts   95% CI [-12.2, -3.8]   win/loss 9/29   p = 0.000209   sign p = 0.00166
                                   tokens 15701 vs 17179 (-8.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -12.2 -> cannot claim parity   one-sided p = 0.918
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 64%
random N=8 vs baseline N=4         d = -4.5 pts   95% CI [-9.1, +0.1]   win/loss 13/21   p = 0.0545   sign p = 0.229
                                   tokens 31796 vs 34192 (-7.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -9.1 -> cannot claim parity   one-sided p = 0.415
                                   power: MDE(80%) 6.6 pts   power to detect 5 pts = 57%
random N=16 vs baseline N=8        d = -5.5 pts   95% CI [-12.2, +1.2]   win/loss 9/14   p = 0.106   sign p = 0.405
                                   tokens 62939 vs 67682 (-7.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -12.2 -> cannot claim parity   one-sided p = 0.558
                                   power: MDE(80%) 9.5 pts   power to detect 5 pts = 31%   <- underpowered

tourney N=1 vs baseline N=1        d = -0.5 pts   95% CI [-4.2, +3.2]   win/loss 17/18   p = 0.79   sign p = 1
                                   tokens 5989 vs 8417 (-28.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.2 -> NON-INFERIOR   one-sided p = 0.00833
                                   WARNING: -29% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.3 pts   power to detect 5 pts = 76%
tourney N=2 vs baseline N=1        d = +3.8 pts   95% CI [-0.6, +8.1]   win/loss 28/15   p = 0.0885   sign p = 0.066
                                   tokens 9002 vs 8417 (+6.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -0.6 -> NON-INFERIOR   one-sided p = 3.52e-05
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
tourney N=4 vs baseline N=2        d = +4.5 pts   95% CI [+0.7, +8.3]   win/loss 23/9   p = 0.0195   sign p = 0.0201
                                   tokens 15393 vs 17179 (-10.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.7 -> NON-INFERIOR   one-sided p = 4.06e-07
                                   power: MDE(80%) 5.4 pts   power to detect 5 pts = 74%
tourney N=8 vs baseline N=4        d = +0.5 pts   95% CI [-4.3, +5.3]   win/loss 17/16   p = 0.837   sign p = 1
                                   tokens 30956 vs 34192 (-9.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.3 -> NON-INFERIOR   one-sided p = 0.012
                                   power: MDE(80%) 6.8 pts   power to detect 5 pts = 54%
tourney N=16 vs baseline N=8       d = -5.5 pts   95% CI [-10.5, -0.5]   win/loss 5/13   p = 0.0311   sign p = 0.0963
                                   tokens 61566 vs 67682 (-9.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -10.5 -> cannot claim parity   one-sided p = 0.578
                                   power: MDE(80%) 7.1 pts   power to detect 5 pts = 50%   <- underpowered

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

============================================================================================================
8. CROSS-CONFIG SUMMARY   (the stable estimate: average over the grid)

   A single config is one noisy draw. Quoting the best cell overstates the
   effect because it is the maximum of many noisy cells. These are means.

   arm          N  configs  acc mean    min    max    tokens  vs base
   baseline     1       12     47.5%     48     48     8,417     0.0%
   rank         1       12     47.8%     46     50     6,135   -27.1%
   random       1       12     46.9%     45     50     5,964   -29.2%
   tourney      1       12     47.1%     44     51     5,965   -29.1%

   baseline     2       12     54.5%     55     55    17,179     0.0%
   rank         2       12     49.2%     46     52     7,967   -53.6%
   random       2       12     46.8%     44     49     8,085   -52.9%
   tourney      2       12     49.6%     46     52     7,966   -53.6%

   baseline     4       12     63.0%     63     63    34,192     0.0%
   rank         4       12     54.9%     46     62    14,132   -58.7%
   random       4       12     51.3%     45     57    14,443   -57.8%
   tourney      4       12     55.6%     47     61    14,258   -58.3%

   baseline     8       12     69.5%     70     70    67,682     0.0%
   rank         8       12     62.7%     55     68    28,569   -57.8%
   random       8       12     59.5%     54     65    29,806   -56.0%
   tourney      8       12     62.3%     56     68    29,307   -56.7%

   baseline    16       12     70.0%     70     70   133,659     0.0%
   rank        16       12     68.2%     64     76    56,949   -57.4%
   random      16       12     65.2%     58     71    60,314   -54.9%
   tourney     16       12     66.6%     60     72    58,939   -55.9%

   ORACLE CEILING COLLAPSE   (what pruning costs you before the judge acts)

   Pruning discards candidates, so a correct answer may never reach the judge.
   A smaller judge gap on a pruned arm is less headroom, not better selection.

   arm          N   ceiling  selected  judge gap  ceiling vs base
   baseline     1     47.5%     47.5%       0.0p             0.0p
   rank         1     47.8%     47.8%       0.0p             0.3p
   random       1     46.9%     46.9%       0.0p            -0.6p
   tourney      1     47.1%     47.1%       0.0p            -0.4p

   baseline     2     57.0%     54.5%       2.5p             0.0p
   rank         2     49.2%     49.2%       0.0p            -7.7p
   random       2     46.8%     46.8%       0.0p           -10.2p
   tourney      2     49.6%     49.6%       0.0p            -7.4p

   baseline     4     66.2%     63.0%       3.2p             0.0p
   rank         4     55.5%     54.9%       0.5p           -10.8p
   random       4     52.3%     51.3%       1.0p           -14.0p
   tourney      4     56.2%     55.6%       0.6p           -10.0p

   baseline     8     73.5%     69.5%       4.0p             0.0p
   rank         8     64.7%     62.7%       2.0p            -8.8p
   random       8     61.5%     59.5%       2.1p           -12.0p
   tourney      8     64.6%     62.3%       2.2p            -8.9p

   baseline    16     79.0%     70.0%       9.0p             0.0p
   rank        16     72.7%     68.2%       4.5p            -6.3p
   random      16     70.4%     65.2%       5.2p            -8.6p
   tourney     16     71.7%     66.6%       5.1p            -7.3p


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
     over 180 equal-N cells:  mean +0.36 pts   median +0.38 pts   positive 99/180   (negative 79, exact ties 2)
       plan=1000  mean -0.31 pts   (60 cells)
       plan=2500  mean +1.15 pts   (60 cells)
       plan=4000  mean +0.25 pts   (60 cells)

   STOP-CORRECTED baseline: arm accuracy minus interpolated baseline accuracy
     over 180 equal-N cells:  mean -1.62 pts   median -1.60 pts   positive 53/180   (negative 127)
       plan=1000  mean -2.21 pts   (60 cells)
       plan=2500  mean -0.92 pts   (60 cells)
       plan=4000  mean -1.73 pts   (60 cells)

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
   arm-contrast          240    100         12     40    80
   judge-vs-random        94     93          5     84    93
   non-inferiority       420    222         21     68   186
   pooled                 48     36          2     24    35
   token-matched         180     27          9      1     6

   78 nominally-significant results do NOT survive BH within their family.
   Do not cite these on their own:
     p=0.00221   [token-matched] plan=4000,prune=2.0  tourney N=4 vs baseline N=2
     p=0.00268   [token-matched] plan=4000,prune=2.0  rank N=4 vs baseline N=2
     p=0.00306   [token-matched] plan=4000,prune=3.0  random N=8 vs baseline N=4
     p=0.00489   [token-matched] plan=2500,prune=2.0  rank N=4 vs baseline N=2
     p=0.0098    [token-matched] plan=2500,prune=3.0  rank N=4 vs baseline N=1
     p=0.0111    [token-matched] plan=4000,prune=1.5  rank N=2 vs baseline N=1
     p=0.017     [arm-contrast] plan=1000,prune=2.0  N=8   tourney - baseline
     p=0.0182    [arm-contrast] plan=2500,prune=1.5  N=16  rank - random
     p=0.0193    [token-matched] plan=2500,prune=3.0  tourney N=8 vs baseline N=2
     p=0.0195    [token-matched] plan=4000,prune=4.0  tourney N=4 vs baseline N=2
     p=0.0203    [arm-contrast] plan=1000,prune=2.0  N=8   rank - baseline
     p=0.0205    [arm-contrast] plan=1000,prune=1.5  N=8   rank - baseline
     p=0.0207    [arm-contrast] plan=2500,prune=2.0  N=2   rank - baseline
     p=0.0208    [arm-contrast] plan=1000,prune=1.5  N=8   tourney - baseline
     p=0.0223    [non-inferiority] plan=4000,prune=1.5  [NI] N=4   rank - baseline
     p=0.0225    [arm-contrast] plan=1000,prune=1.5  N=2   tourney - baseline
     p=0.0225    [non-inferiority] plan=2500,prune=4.0  [NI] N=1   rank - random
     p=0.0232    [token-matched] plan=2500,prune=1.5  tourney N=4 vs baseline N=2
     p=0.0233    [non-inferiority] plan=1000,prune=2.0  [NI] random N=2 vs baseline N=1
     p=0.0239    [token-matched] plan=2500,prune=2.0  random N=16 vs baseline N=8
     ... and 58 more

   217 results survive the strict Holm correction; these are the safe ones to quote.
```
