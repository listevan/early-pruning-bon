
############################################################################################################
# CONFIG  plan=1000  prune=2.0
############################################################################################################
============================================================================================================
FILES
  baseline  2026-07-25_11-42-12_baseline_bon_1_2_4_8_16_32_strat_None_plan_4000_prune_2.json
  random    2026-07-31_12-15-25_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_2.0.json
  rank      2026-07-31_12-14-27_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_2.0.json
  tourney   2026-07-31_12-16-22_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_2.0.json
  N values: [1, 2, 4, 8, 16, 32]
  questions: baseline=100, random=100, rank=100, tourney=100

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16            N=32
baseline      47.2%   8238t    57.0%  16890t    63.7%  33840t    68.5%  67278t    72.0% 133186t    75.0% 264452t
rank          46.2%   6320t    46.2%   6944t    55.0%  14057t    62.5%  27494t    66.5%  53726t               -
random        47.2%   5955t    43.8%   7006t    53.2%  13910t    61.0%  28091t    66.5%  55354t               -
tourney       46.0%   6010t    47.2%   6972t    55.2%  13931t    60.5%  28089t    64.0%  55882t               -

============================================================================================================
2. JUDGE vs RANDOM PICK, WITHIN THE SAME POOL   (does selection beat chance?)

baseline N=1: judge - random       d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
baseline N=2: judge - random       d = +7.0 pts   naive 95% CI [+4.1, +9.9]   cluster 95% CI [+3.9, +10.1]   deff 1.18   b/c 32/4   McNemar p = 1.94e-06   clustered p = 1.1e-05
                                   power: MDE(80%) 4.5 pts   power to detect 5 pts = 88%
baseline N=4: judge - random       d = +16.0 pts   naive 95% CI [+12.0, +20.0]   cluster 95% CI [+11.1, +20.9]   deff 1.43   b/c 71/7   McNemar p = 1.93e-14   clustered p = 1.02e-10
                                   power: MDE(80%) 6.9 pts   power to detect 5 pts = 52%
baseline N=8: judge - random       d = +20.5 pts   naive 95% CI [+15.9, +25.1]   cluster 95% CI [+15.0, +26.0]   deff 1.40   b/c 93/11   McNemar p = 2.49e-17   clustered p = 1.79e-13
                                   power: MDE(80%) 7.8 pts   power to detect 5 pts = 43%   <- underpowered; a null here is NOT evidence of no effect
baseline N=16: judge - random      d = +22.0 pts   naive 95% CI [+14.9, +29.1]   cluster 95% CI [+14.6, +29.4]   deff 1.08   b/c 53/9   McNemar p = 1.05e-08   clustered p = 5.99e-09
                                   power: MDE(80%) 10.6 pts   power to detect 5 pts = 26%   <- underpowered; a null here is NOT evidence of no effect
baseline N=32: judge - random      d = +23.0 pts   naive 95% CI [+13.0, +33.0]   cluster 95% CI [+13.0, +33.0]   deff 0.99   b/c 27/4   McNemar p = 3.4e-05   clustered p = 6.38e-06
                                   power: MDE(80%) 14.3 pts   power to detect 5 pts = 16%   <- underpowered; a null here is NOT evidence of no effect

rank N=1: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=2: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=4: judge - random           d = +9.2 pts   naive 95% CI [+6.2, +12.3]   cluster 95% CI [+5.7, +12.8]   deff 1.42   b/c 39/2   McNemar p = 7.84e-10   clustered p = 4.6e-07
                                   power: MDE(80%) 5.1 pts   power to detect 5 pts = 78%
rank N=8: judge - random           d = +16.8 pts   naive 95% CI [+12.7, +20.8]   cluster 95% CI [+11.7, +21.8]   deff 1.53   b/c 73/6   McNemar p = 1e-15   clustered p = 6.42e-11
                                   power: MDE(80%) 7.2 pts   power to detect 5 pts = 50%   <- underpowered; a null here is NOT evidence of no effect
rank N=16: judge - random          d = +18.0 pts   naive 95% CI [+11.4, +24.6]   cluster 95% CI [+10.3, +25.7]   deff 1.33   b/c 44/8   McNemar p = 4.04e-07   clustered p = 4.55e-06
                                   power: MDE(80%) 11.0 pts   power to detect 5 pts = 25%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=4: judge - random         d = +10.5 pts   naive 95% CI [+7.3, +13.7]   cluster 95% CI [+7.1, +13.9]   deff 1.11   b/c 45/3   McNemar p = 1.31e-10   clustered p = 1.86e-09
                                   power: MDE(80%) 4.9 pts   power to detect 5 pts = 82%
random N=8: judge - random         d = +15.2 pts   naive 95% CI [+11.2, +19.3]   cluster 95% CI [+10.6, +19.9]   deff 1.29   b/c 70/9   McNemar p = 7.78e-13   clustered p = 1.5e-10
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 56%
random N=16: judge - random        d = +17.0 pts   naive 95% CI [+10.6, +23.4]   cluster 95% CI [+10.3, +23.7]   deff 1.09   b/c 41/7   McNemar p = 6.24e-07   clustered p = 6.9e-07
                                   power: MDE(80%) 9.6 pts   power to detect 5 pts = 31%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=4: judge - random        d = +8.5 pts   naive 95% CI [+5.6, +11.4]   cluster 95% CI [+5.3, +11.7]   deff 1.21   b/c 36/2   McNemar p = 5.4e-09   clustered p = 2.07e-07
                                   power: MDE(80%) 4.6 pts   power to detect 5 pts = 86%
tourney N=8: judge - random        d = +14.0 pts   naive 95% CI [+10.3, +17.7]   cluster 95% CI [+9.6, +18.4]   deff 1.35   b/c 61/5   McNemar p = 2.63e-13   clustered p = 3.32e-10
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 61%
tourney N=16: judge - random       d = +16.5 pts   naive 95% CI [+10.6, +22.4]   cluster 95% CI [+10.7, +22.3]   deff 0.95   b/c 37/4   McNemar p = 1.03e-07   clustered p = 1.89e-08
                                   power: MDE(80%) 8.2 pts   power to detect 5 pts = 40%   <- underpowered; a null here is NOT evidence of no effect

============================================================================================================
3. ORACLE CEILING   (a correct candidate EXISTS vs the judge FINDS it)
   NOTE: for pruned arms this is pass@k over SURVIVORS, not over all N.
   Only the baseline row is a clean best-of-N ceiling.

baseline   N=1   ceiling  47.2%   selected  47.2%   gap  0.0 pts   capture 100.0%
baseline   N=2   ceiling  59.0%   selected  57.0%   gap  2.0 pts   capture  96.6%
baseline   N=4   ceiling  66.8%   selected  63.7%   gap  3.0 pts   capture  95.5%
baseline   N=8   ceiling  75.8%   selected  68.5%   gap  7.2 pts   capture  90.4%
baseline   N=16  ceiling  80.5%   selected  72.0%   gap  8.5 pts   capture  89.4%
baseline   N=32  ceiling  87.0%   selected  75.0%   gap 12.0 pts   capture  86.2%

rank       N=1   ceiling  46.2%   selected  46.2%   gap  0.0 pts   capture 100.0%
rank       N=2   ceiling  46.2%   selected  46.2%   gap  0.0 pts   capture 100.0%
rank       N=4   ceiling  56.5%   selected  55.0%   gap  1.5 pts   capture  97.3%
rank       N=8   ceiling  65.2%   selected  62.5%   gap  2.7 pts   capture  95.8%
rank       N=16  ceiling  74.5%   selected  66.5%   gap  8.0 pts   capture  89.3%

random     N=1   ceiling  47.2%   selected  47.2%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  43.8%   selected  43.8%   gap  0.0 pts   capture 100.0%
random     N=4   ceiling  55.5%   selected  53.2%   gap  2.3 pts   capture  95.9%
random     N=8   ceiling  65.8%   selected  61.0%   gap  4.7 pts   capture  92.8%
random     N=16  ceiling  72.5%   selected  66.5%   gap  6.0 pts   capture  91.7%

tourney    N=1   ceiling  46.0%   selected  46.0%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  47.2%   selected  47.2%   gap  0.0 pts   capture 100.0%
tourney    N=4   ceiling  56.2%   selected  55.2%   gap  1.0 pts   capture  98.2%
tourney    N=8   ceiling  62.7%   selected  60.5%   gap  2.2 pts   capture  96.4%
tourney    N=16  ceiling  70.0%   selected  64.0%   gap  6.0 pts   capture  91.4%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = -1.0 pts   naive 95% CI [-5.2, +3.2]   cluster 95% CI [-5.1, +3.1]   deff 0.94   b/c 35/39   McNemar p = 0.728   clustered p = 0.634
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
                                   non-inferiority (margin 5 pts): lower bound -5.1 -> cannot claim parity   one-sided p = 0.0284
                                   tokens 6320 vs 5955  (+6.1%, 95% CI [+0.9%, +11.4%])
N=2   rank - random                d = +2.5 pts   naive 95% CI [-1.7, +6.7]   cluster 95% CI [-1.6, +6.6]   deff 0.93   b/c 42/32   McNemar p = 0.295   clustered p = 0.231
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 67%
                                   non-inferiority (margin 5 pts): lower bound -1.6 -> NON-INFERIOR   one-sided p = 0.000163
                                   tokens 6944 vs 7006  (-0.9%, 95% CI [-5.1%, +3.4%])
N=4   rank - random                d = +1.8 pts   naive 95% CI [-2.1, +5.6]   cluster 95% CI [-2.7, +6.2]   deff 1.31   b/c 35/28   McNemar p = 0.45   clustered p = 0.443
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 59%
                                   non-inferiority (margin 5 pts): lower bound -2.7 -> NON-INFERIOR   one-sided p = 0.00155
                                   tokens 14057 vs 13910  (+1.1%, 95% CI [-2.2%, +4.3%])
N=8   rank - random                d = +1.5 pts   naive 95% CI [-2.7, +5.7]   cluster 95% CI [-2.7, +5.7]   deff 0.99   b/c 39/33   McNemar p = 0.556   clustered p = 0.481
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 65%
                                   non-inferiority (margin 5 pts): lower bound -2.7 -> NON-INFERIOR   one-sided p = 0.00112
                                   tokens 27494 vs 28091  (-2.1%, 95% CI [-4.7%, +0.4%])
N=16  rank - random                d = +0.0 pts   naive 95% CI [-5.6, +5.6]   cluster 95% CI [-5.2, +5.2]   deff 0.87   b/c 16/16   McNemar p = 1   clustered p = 1
                                   power: MDE(80%) 7.4 pts   power to detect 5 pts = 47%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -5.2 -> cannot claim parity   one-sided p = 0.03
                                   tokens 53726 vs 55354  (-2.9%, 95% CI [-5.4%, -0.5%])

N=1   rank - baseline              d = -1.0 pts   naive 95% CI [-5.3, +3.3]   cluster 95% CI [-5.2, +3.2]   deff 0.97   b/c 36/40   McNemar p = 0.731   clustered p = 0.643
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 64%
                                   non-inferiority (margin 5 pts): lower bound -5.2 -> cannot claim parity   one-sided p = 0.032
                                   tokens 6320 vs 8238  (-23.3%, 95% CI [-28.3%, -18.2%])
N=2   rank - baseline              d = -10.8 pts   naive 95% CI [-15.1, -6.4]   cluster 95% CI [-15.7, -5.8]   deff 1.28   b/c 20/63   McNemar p = 2.43e-06   clustered p = 1.98e-05
                                   power: MDE(80%) 7.1 pts   power to detect 5 pts = 51%
                                   non-inferiority (margin 5 pts): lower bound -15.7 -> cannot claim parity   one-sided p = 0.989
                                   tokens 6944 vs 16890  (-58.9%, 95% CI [-61.3%, -56.5%])
N=4   rank - baseline              d = -8.8 pts   naive 95% CI [-12.7, -4.8]   cluster 95% CI [-13.4, -4.1]   deff 1.38   b/c 16/51   McNemar p = 2.17e-05   clustered p = 0.000219
                                   power: MDE(80%) 6.6 pts   power to detect 5 pts = 56%
                                   non-inferiority (margin 5 pts): lower bound -13.4 -> cannot claim parity   one-sided p = 0.943
                                   tokens 14057 vs 33840  (-58.5%, 95% CI [-60.3%, -56.7%])
N=8   rank - baseline              d = -6.0 pts   naive 95% CI [-10.0, -2.0]   cluster 95% CI [-10.0, -2.0]   deff 0.99   b/c 22/46   McNemar p = 0.0049   clustered p = 0.00335
                                   power: MDE(80%) 5.7 pts   power to detect 5 pts = 69%
                                   non-inferiority (margin 5 pts): lower bound -10.0 -> cannot claim parity   one-sided p = 0.688
                                   tokens 27494 vs 67278  (-59.1%, 95% CI [-60.6%, -57.7%])
N=16  rank - baseline              d = -5.5 pts   naive 95% CI [-11.7, +0.7]   cluster 95% CI [-11.7, +0.7]   deff 0.98   b/c 15/26   McNemar p = 0.117   clustered p = 0.0827
                                   power: MDE(80%) 8.9 pts   power to detect 5 pts = 35%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -11.7 -> cannot claim parity   one-sided p = 0.563
                                   tokens 53726 vs 133186  (-59.7%, 95% CI [-61.1%, -58.3%])

N=1   tourney - baseline           d = -1.2 pts   naive 95% CI [-5.4, +2.9]   cluster 95% CI [-5.4, +2.9]   deff 0.99   b/c 33/38   McNemar p = 0.635   clustered p = 0.554
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
                                   non-inferiority (margin 5 pts): lower bound -5.4 -> cannot claim parity   one-sided p = 0.038
                                   tokens 6010 vs 8238  (-27.0%, 95% CI [-31.4%, -22.6%])
N=2   tourney - baseline           d = -9.8 pts   naive 95% CI [-13.8, -5.7]   cluster 95% CI [-13.9, -5.6]   deff 1.07   b/c 16/55   McNemar p = 3.75e-06   clustered p = 4.65e-06
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 65%
                                   non-inferiority (margin 5 pts): lower bound -13.9 -> cannot claim parity   one-sided p = 0.987
                                   tokens 6972 vs 16890  (-58.7%, 95% CI [-60.9%, -56.5%])
N=4   tourney - baseline           d = -8.5 pts   naive 95% CI [-12.5, -4.5]   cluster 95% CI [-12.9, -4.1]   deff 1.20   b/c 18/52   McNemar p = 5.85e-05   clustered p = 0.000162
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 60%
                                   non-inferiority (margin 5 pts): lower bound -12.9 -> cannot claim parity   one-sided p = 0.94
                                   tokens 13931 vs 33840  (-58.8%, 95% CI [-60.7%, -57.0%])
N=8   tourney - baseline           d = -8.0 pts   naive 95% CI [-12.0, -4.0]   cluster 95% CI [-12.6, -3.4]   deff 1.27   b/c 19/51   McNemar p = 0.000166   clustered p = 0.000586
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 57%
                                   non-inferiority (margin 5 pts): lower bound -12.6 -> cannot claim parity   one-sided p = 0.901
                                   tokens 28089 vs 67278  (-58.2%, 95% CI [-59.8%, -56.7%])
N=16  tourney - baseline           d = -8.0 pts   naive 95% CI [-13.8, -2.2]   cluster 95% CI [-14.2, -1.8]   deff 1.13   b/c 10/26   McNemar p = 0.0113   clustered p = 0.0112
                                   power: MDE(80%) 8.8 pts   power to detect 5 pts = 35%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -14.2 -> cannot claim parity   one-sided p = 0.829
                                   tokens 55882 vs 133186  (-58.0%, 95% CI [-59.8%, -56.3%])

N=1   random - baseline            d = +0.0 pts   naive 95% CI [-4.3, +4.3]   cluster 95% CI [-4.3, +4.3]   deff 1.00   b/c 39/39   McNemar p = 1   clustered p = 1
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
                                   non-inferiority (margin 5 pts): lower bound -4.3 -> NON-INFERIOR   one-sided p = 0.0121
                                   tokens 5955 vs 8238  (-27.7%, 95% CI [-32.4%, -23.0%])
N=2   random - baseline            d = -13.2 pts   naive 95% CI [-17.6, -8.9]   cluster 95% CI [-18.3, -8.2]   deff 1.34   b/c 16/69   McNemar p = 5.24e-09   clustered p = 2.63e-07
                                   power: MDE(80%) 7.2 pts   power to detect 5 pts = 49%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -18.3 -> cannot claim parity   one-sided p = 0.999
                                   tokens 7006 vs 16890  (-58.5%, 95% CI [-60.8%, -56.3%])
N=4   random - baseline            d = -10.5 pts   naive 95% CI [-14.7, -6.3]   cluster 95% CI [-15.2, -5.8]   deff 1.22   b/c 18/60   McNemar p = 1.97e-06   clustered p = 1.1e-05
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
                                   non-inferiority (margin 5 pts): lower bound -15.2 -> cannot claim parity   one-sided p = 0.989
                                   tokens 13910 vs 33840  (-58.9%, 95% CI [-60.9%, -56.9%])
N=8   random - baseline            d = -7.5 pts   naive 95% CI [-11.8, -3.2]   cluster 95% CI [-12.1, -2.9]   deff 1.14   b/c 25/55   McNemar p = 0.00105   clustered p = 0.00156
                                   power: MDE(80%) 6.6 pts   power to detect 5 pts = 56%
                                   non-inferiority (margin 5 pts): lower bound -12.1 -> cannot claim parity   one-sided p = 0.854
                                   tokens 28091 vs 67278  (-58.2%, 95% CI [-60.1%, -56.4%])
N=16  random - baseline            d = -5.5 pts   naive 95% CI [-11.6, +0.6]   cluster 95% CI [-11.6, +0.6]   deff 0.98   b/c 14/25   McNemar p = 0.108   clustered p = 0.075
                                   power: MDE(80%) 8.7 pts   power to detect 5 pts = 37%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -11.6 -> cannot claim parity   one-sided p = 0.564
                                   tokens 55354 vs 133186  (-58.4%, 95% CI [-60.2%, -56.7%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = +1.1 pts   naive 95% CI [-0.9, +3.0]   cluster 95% CI [-0.9, +3.0]   deff 1.01   b/c 167/148   McNemar p = 0.31   clustered p = 0.29
                                   power: MDE(80%) 2.8 pts   power to detect 5 pts = 100%
                                   equal-weight per N: d = +0.9 pts (from 5 cells: -1.0, +2.5, +1.8, +1.5, +0.0)

pooled rank - baseline (chunk-wtd) d = -6.5 pts   naive 95% CI [-8.5, -4.5]   cluster 95% CI [-9.2, -3.8]   deff 1.84   b/c 109/226   McNemar p = 1.53e-10   clustered p = 2.09e-06
                                   power: MDE(80%) 3.8 pts   power to detect 5 pts = 95%
                                   equal-weight per N: d = -6.4 pts (from 5 cells: -1.0, -10.8, -8.8, -6.0, -5.5)

pooled tourney - baseline (chunk-wtd) d = -7.0 pts   naive 95% CI [-8.9, -5.1]   cluster 95% CI [-9.8, -4.2]   deff 2.09   b/c 96/222   McNemar p = 1.22e-12   clustered p = 8e-07
                                   power: MDE(80%) 4.0 pts   power to detect 5 pts = 94%
                                   equal-weight per N: d = -7.1 pts (from 5 cells: -1.2, -9.8, -8.5, -8.0, -8.0)

pooled random - baseline (chunk-wtd) d = -7.6 pts   naive 95% CI [-9.6, -5.5]   cluster 95% CI [-10.5, -4.6]   deff 2.08   b/c 112/248   McNemar p = 5.96e-13   clustered p = 5.4e-07
                                   power: MDE(80%) 4.2 pts   power to detect 5 pts = 91%
                                   equal-weight per N: d = -7.3 pts (from 5 cells: +0.0, -13.2, -10.5, -7.5, -5.5)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = -1.0 pts   95% CI [-5.2, +3.2]   win/loss 19/18   p = 0.643   sign p = 1
                                   tokens 6320 vs 8238 (-23.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.2 -> cannot claim parity   one-sided p = 0.032
                                   WARNING: -23% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 64%
rank N=2 vs baseline N=1           d = -1.0 pts   95% CI [-5.7, +3.7]   win/loss 20/21   p = 0.678   sign p = 1
                                   tokens 6944 vs 8238 (-15.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.7 -> cannot claim parity   one-sided p = 0.0483
                                   WARNING: -16% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
rank N=4 vs baseline N=2           d = -2.0 pts   95% CI [-6.0, +2.0]   win/loss 16/21   p = 0.332   sign p = 0.511
                                   tokens 14057 vs 16890 (-16.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -6.0 -> cannot claim parity   one-sided p = 0.0729
                                   WARNING: -17% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 68%
rank N=8 vs baseline N=4           d = -1.2 pts   95% CI [-5.2, +2.7]   win/loss 14/18   p = 0.53   sign p = 0.597
                                   tokens 27494 vs 33840 (-18.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.2 -> cannot claim parity   one-sided p = 0.0298
                                   WARNING: -19% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.6 pts   power to detect 5 pts = 71%
rank N=16 vs baseline N=8          d = -2.0 pts   95% CI [-7.8, +3.8]   win/loss 19/21   p = 0.497   sign p = 0.875
                                   tokens 53726 vs 67278 (-20.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -7.8 -> cannot claim parity   one-sided p = 0.154
                                   WARNING: -20% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 8.2 pts   power to detect 5 pts = 40%   <- underpowered

random N=1 vs baseline N=1         d = +0.0 pts   95% CI [-4.3, +4.3]   win/loss 21/18   p = 1   sign p = 0.749
                                   tokens 5955 vs 8238 (-27.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.3 -> NON-INFERIOR   one-sided p = 0.0121
                                   WARNING: -28% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
random N=2 vs baseline N=1         d = -3.5 pts   95% CI [-7.8, +0.8]   win/loss 16/23   p = 0.11   sign p = 0.337
                                   tokens 7006 vs 8238 (-15.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -7.8 -> cannot claim parity   one-sided p = 0.247
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
random N=4 vs baseline N=2         d = -3.8 pts   95% CI [-8.3, +0.8]   win/loss 14/24   p = 0.105   sign p = 0.143
                                   tokens 13910 vs 16890 (-17.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -8.3 -> cannot claim parity   one-sided p = 0.294
                                   WARNING: -18% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 58%
random N=8 vs baseline N=4         d = -2.8 pts   95% CI [-7.1, +1.6]   win/loss 15/24   p = 0.215   sign p = 0.2
                                   tokens 28091 vs 33840 (-17.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -7.1 -> cannot claim parity   one-sided p = 0.155
                                   WARNING: -17% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
random N=16 vs baseline N=8        d = -2.0 pts   95% CI [-7.1, +3.1]   win/loss 18/22   p = 0.447   sign p = 0.636
                                   tokens 55354 vs 67278 (-17.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -7.1 -> cannot claim parity   one-sided p = 0.127
                                   WARNING: -18% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 7.4 pts   power to detect 5 pts = 48%   <- underpowered

tourney N=1 vs baseline N=1        d = -1.2 pts   95% CI [-5.4, +2.9]   win/loss 17/19   p = 0.554   sign p = 0.868
                                   tokens 6010 vs 8238 (-27.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.4 -> cannot claim parity   one-sided p = 0.038
                                   WARNING: -27% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
tourney N=2 vs baseline N=1        d = +0.0 pts   95% CI [-4.1, +4.1]   win/loss 21/19   p = 1   sign p = 0.875
                                   tokens 6972 vs 8238 (-15.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.1 -> NON-INFERIOR   one-sided p = 0.00869
                                   WARNING: -15% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
tourney N=4 vs baseline N=2        d = -1.8 pts   95% CI [-5.9, +2.4]   win/loss 15/19   p = 0.413   sign p = 0.608
                                   tokens 13931 vs 16890 (-17.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.9 -> cannot claim parity   one-sided p = 0.0644
                                   WARNING: -18% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 65%
tourney N=8 vs baseline N=4        d = -3.2 pts   95% CI [-7.2, +0.7]   win/loss 14/24   p = 0.104   sign p = 0.143
                                   tokens 28089 vs 33840 (-17.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -7.2 -> cannot claim parity   one-sided p = 0.191
                                   WARNING: -17% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.6 pts   power to detect 5 pts = 71%
tourney N=16 vs baseline N=8       d = -4.5 pts   95% CI [-9.5, +0.5]   win/loss 16/23   p = 0.0773   sign p = 0.337
                                   tokens 55882 vs 67278 (-16.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -9.5 -> cannot claim parity   one-sided p = 0.422
                                   WARNING: -17% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 7.1 pts   power to detect 5 pts = 50%

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

############################################################################################################
# CONFIG  plan=2500  prune=2.0
############################################################################################################
============================================================================================================
FILES
  baseline  2026-07-25_11-42-12_baseline_bon_1_2_4_8_16_32_strat_None_plan_4000_prune_2.json
  random    2026-07-31_09-29-46_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_2.0.json
  rank      2026-07-31_09-28-49_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_2.0.json
  tourney   2026-07-31_09-30-43_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_2.0.json
  N values: [1, 2, 4, 8, 16, 32]
  questions: baseline=100, random=100, rank=100, tourney=100

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16            N=32
baseline      47.2%   8238t    57.0%  16890t    63.7%  33840t    68.5%  67278t    72.0% 133186t    75.0% 264452t
rank          46.2%   6137t    50.2%   7928t    57.8%  16255t    59.2%  31452t    69.5%  61813t               -
random        48.5%   5799t    45.8%   8188t    56.2%  16475t    59.5%  33307t    68.0%  65871t               -
tourney       47.8%   5861t    49.8%   7931t    58.0%  15977t    64.2%  32399t    65.5%  63985t               -

============================================================================================================
2. JUDGE vs RANDOM PICK, WITHIN THE SAME POOL   (does selection beat chance?)

baseline N=1: judge - random       d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
baseline N=2: judge - random       d = +7.0 pts   naive 95% CI [+4.1, +9.9]   cluster 95% CI [+3.9, +10.1]   deff 1.18   b/c 32/4   McNemar p = 1.94e-06   clustered p = 1.1e-05
                                   power: MDE(80%) 4.5 pts   power to detect 5 pts = 88%
baseline N=4: judge - random       d = +16.0 pts   naive 95% CI [+12.0, +20.0]   cluster 95% CI [+11.1, +20.9]   deff 1.43   b/c 71/7   McNemar p = 1.93e-14   clustered p = 1.02e-10
                                   power: MDE(80%) 6.9 pts   power to detect 5 pts = 52%
baseline N=8: judge - random       d = +20.5 pts   naive 95% CI [+15.9, +25.1]   cluster 95% CI [+15.0, +26.0]   deff 1.40   b/c 93/11   McNemar p = 2.49e-17   clustered p = 1.79e-13
                                   power: MDE(80%) 7.8 pts   power to detect 5 pts = 43%   <- underpowered; a null here is NOT evidence of no effect
baseline N=16: judge - random      d = +22.0 pts   naive 95% CI [+14.9, +29.1]   cluster 95% CI [+14.6, +29.4]   deff 1.08   b/c 53/9   McNemar p = 1.05e-08   clustered p = 5.99e-09
                                   power: MDE(80%) 10.6 pts   power to detect 5 pts = 26%   <- underpowered; a null here is NOT evidence of no effect
baseline N=32: judge - random      d = +23.0 pts   naive 95% CI [+13.0, +33.0]   cluster 95% CI [+13.0, +33.0]   deff 0.99   b/c 27/4   McNemar p = 3.4e-05   clustered p = 6.38e-06
                                   power: MDE(80%) 14.3 pts   power to detect 5 pts = 16%   <- underpowered; a null here is NOT evidence of no effect

rank N=1: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=2: judge - random           d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
rank N=4: judge - random           d = +7.2 pts   naive 95% CI [+4.6, +9.9]   cluster 95% CI [+4.4, +10.1]   deff 1.12   b/c 30/1   McNemar p = 2.98e-08   clustered p = 4.32e-07
                                   power: MDE(80%) 4.0 pts   power to detect 5 pts = 94%
rank N=8: judge - random           d = +11.8 pts   naive 95% CI [+8.2, +15.3]   cluster 95% CI [+7.4, +16.1]   deff 1.49   b/c 52/5   McNemar p = 6.4e-11   clustered p = 9.69e-08
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
rank N=16: judge - random          d = +18.5 pts   naive 95% CI [+12.1, +24.9]   cluster 95% CI [+11.9, +25.1]   deff 1.07   b/c 43/6   McNemar p = 5.73e-08   clustered p = 4.52e-08
                                   power: MDE(80%) 9.5 pts   power to detect 5 pts = 31%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=4: judge - random         d = +7.2 pts   naive 95% CI [+4.4, +10.1]   cluster 95% CI [+4.0, +10.5]   deff 1.35   b/c 32/3   McNemar p = 4.18e-07   clustered p = 1.55e-05
                                   power: MDE(80%) 4.7 pts   power to detect 5 pts = 85%
random N=8: judge - random         d = +12.8 pts   naive 95% CI [+9.1, +16.4]   cluster 95% CI [+8.8, +16.7]   deff 1.15   b/c 57/6   McNemar p = 1.64e-11   clustered p = 3.08e-10
                                   power: MDE(80%) 5.7 pts   power to detect 5 pts = 69%
random N=16: judge - random        d = +22.5 pts   naive 95% CI [+16.2, +28.8]   cluster 95% CI [+15.6, +29.4]   deff 1.19   b/c 48/3   McNemar p = 1.97e-11   clustered p = 1.43e-10
                                   power: MDE(80%) 9.8 pts   power to detect 5 pts = 30%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=4: judge - random        d = +9.0 pts   naive 95% CI [+6.0, +12.0]   cluster 95% CI [+5.6, +12.4]   deff 1.33   b/c 38/2   McNemar p = 1.49e-09   clustered p = 3.14e-07
                                   power: MDE(80%) 4.9 pts   power to detect 5 pts = 81%
tourney N=8: judge - random        d = +13.8 pts   naive 95% CI [+10.1, +17.4]   cluster 95% CI [+8.9, +18.6]   deff 1.74   b/c 59/4   McNemar p = 1.38e-13   clustered p = 2.64e-08
                                   power: MDE(80%) 6.9 pts   power to detect 5 pts = 53%
tourney N=16: judge - random       d = +13.5 pts   naive 95% CI [+7.7, +19.3]   cluster 95% CI [+7.5, +19.5]   deff 1.06   b/c 33/6   McNemar p = 1.43e-05   clustered p = 1.22e-05
                                   power: MDE(80%) 8.6 pts   power to detect 5 pts = 37%   <- underpowered; a null here is NOT evidence of no effect

============================================================================================================
3. ORACLE CEILING   (a correct candidate EXISTS vs the judge FINDS it)
   NOTE: for pruned arms this is pass@k over SURVIVORS, not over all N.
   Only the baseline row is a clean best-of-N ceiling.

baseline   N=1   ceiling  47.2%   selected  47.2%   gap  0.0 pts   capture 100.0%
baseline   N=2   ceiling  59.0%   selected  57.0%   gap  2.0 pts   capture  96.6%
baseline   N=4   ceiling  66.8%   selected  63.7%   gap  3.0 pts   capture  95.5%
baseline   N=8   ceiling  75.8%   selected  68.5%   gap  7.2 pts   capture  90.4%
baseline   N=16  ceiling  80.5%   selected  72.0%   gap  8.5 pts   capture  89.4%
baseline   N=32  ceiling  87.0%   selected  75.0%   gap 12.0 pts   capture  86.2%

rank       N=1   ceiling  46.2%   selected  46.2%   gap  0.0 pts   capture 100.0%
rank       N=2   ceiling  50.2%   selected  50.2%   gap  0.0 pts   capture 100.0%
rank       N=4   ceiling  58.2%   selected  57.8%   gap  0.5 pts   capture  99.1%
rank       N=8   ceiling  62.3%   selected  59.2%   gap  3.0 pts   capture  95.2%
rank       N=16  ceiling  74.0%   selected  69.5%   gap  4.5 pts   capture  93.9%

random     N=1   ceiling  48.5%   selected  48.5%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  45.8%   selected  45.8%   gap  0.0 pts   capture 100.0%
random     N=4   ceiling  57.8%   selected  56.2%   gap  1.5 pts   capture  97.4%
random     N=8   ceiling  62.3%   selected  59.5%   gap  2.8 pts   capture  95.6%
random     N=16  ceiling  72.0%   selected  68.0%   gap  4.0 pts   capture  94.4%

tourney    N=1   ceiling  47.8%   selected  47.8%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  49.8%   selected  49.8%   gap  0.0 pts   capture 100.0%
tourney    N=4   ceiling  58.8%   selected  58.0%   gap  0.8 pts   capture  98.7%
tourney    N=8   ceiling  66.2%   selected  64.2%   gap  2.0 pts   capture  97.0%
tourney    N=16  ceiling  71.0%   selected  65.5%   gap  5.5 pts   capture  92.3%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = -2.2 pts   naive 95% CI [-4.4, -0.1]   cluster 95% CI [-4.6, +0.1]   deff 1.18   b/c 5/14   McNemar p = 0.0636   clustered p = 0.0573
                                   power: MDE(80%) 3.3 pts   power to detect 5 pts = 99%
                                   non-inferiority (margin 5 pts): lower bound -4.6 -> NON-INFERIOR   one-sided p = 0.0101
                                   tokens 6137 vs 5799  (+5.8%, 95% CI [+3.8%, +7.9%])
N=2   rank - random                d = +4.5 pts   naive 95% CI [+0.7, +8.3]   cluster 95% CI [+1.1, +7.9]   deff 0.79   b/c 39/21   McNemar p = 0.0273   clustered p = 0.00882
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 83%
                                   non-inferiority (margin 5 pts): lower bound +1.1 -> NON-INFERIOR   one-sided p = 1.61e-08
                                   tokens 7928 vs 8188  (-3.2%, 95% CI [-6.0%, -0.3%])
N=4   rank - random                d = +1.5 pts   naive 95% CI [-2.4, +5.4]   cluster 95% CI [-2.1, +5.1]   deff 0.84   b/c 35/29   McNemar p = 0.532   clustered p = 0.415
                                   power: MDE(80%) 5.2 pts   power to detect 5 pts = 78%
                                   non-inferiority (margin 5 pts): lower bound -2.1 -> NON-INFERIOR   one-sided p = 0.000206
                                   tokens 16255 vs 16475  (-1.3%, 95% CI [-3.6%, +0.9%])
N=8   rank - random                d = -0.2 pts   naive 95% CI [-4.0, +3.5]   cluster 95% CI [-4.2, +3.7]   deff 1.10   b/c 28/29   McNemar p = 1   clustered p = 0.9
                                   power: MDE(80%) 5.6 pts   power to detect 5 pts = 71%
                                   non-inferiority (margin 5 pts): lower bound -4.2 -> NON-INFERIOR   one-sided p = 0.00861
                                   tokens 31452 vs 33307  (-5.6%, 95% CI [-7.4%, -3.7%])
N=16  rank - random                d = +1.5 pts   naive 95% CI [-4.3, +7.3]   cluster 95% CI [-4.0, +7.0]   deff 0.88   b/c 19/16   McNemar p = 0.736   clustered p = 0.591
                                   power: MDE(80%) 7.8 pts   power to detect 5 pts = 43%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -4.0 -> NON-INFERIOR   one-sided p = 0.00999
                                   tokens 61813 vs 65871  (-6.2%, 95% CI [-8.2%, -4.1%])

N=1   rank - baseline              d = -1.0 pts   naive 95% CI [-4.5, +2.5]   cluster 95% CI [-4.4, +2.4]   deff 0.92   b/c 24/28   McNemar p = 0.678   clustered p = 0.565
                                   power: MDE(80%) 4.9 pts   power to detect 5 pts = 82%
                                   non-inferiority (margin 5 pts): lower bound -4.4 -> NON-INFERIOR   one-sided p = 0.0107
                                   tokens 6137 vs 8238  (-25.5%, 95% CI [-29.6%, -21.4%])
N=2   rank - baseline              d = -6.8 pts   naive 95% CI [-10.3, -3.2]   cluster 95% CI [-10.6, -2.9]   deff 1.20   b/c 13/40   McNemar p = 0.000269   clustered p = 0.000627
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 72%
                                   non-inferiority (margin 5 pts): lower bound -10.6 -> cannot claim parity   one-sided p = 0.812
                                   tokens 7928 vs 16890  (-53.1%, 95% CI [-55.3%, -50.8%])
N=4   rank - baseline              d = -6.0 pts   naive 95% CI [-9.6, -2.4]   cluster 95% CI [-10.2, -1.8]   deff 1.36   b/c 16/40   McNemar p = 0.00184   clustered p = 0.00558
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 64%
                                   non-inferiority (margin 5 pts): lower bound -10.2 -> cannot claim parity   one-sided p = 0.678
                                   tokens 16255 vs 33840  (-52.0%, 95% CI [-53.9%, -50.0%])
N=8   rank - baseline              d = -9.2 pts   naive 95% CI [-13.4, -5.1]   cluster 95% CI [-14.1, -4.4]   deff 1.33   b/c 19/56   McNemar p = 2.24e-05   clustered p = 0.000163
                                   power: MDE(80%) 6.9 pts   power to detect 5 pts = 53%
                                   non-inferiority (margin 5 pts): lower bound -14.1 -> cannot claim parity   one-sided p = 0.958
                                   tokens 31452 vs 67278  (-53.3%, 95% CI [-55.0%, -51.5%])
N=16  rank - baseline              d = -2.5 pts   naive 95% CI [-8.0, +3.0]   cluster 95% CI [-7.6, +2.6]   deff 0.86   b/c 13/18   McNemar p = 0.473   clustered p = 0.336
                                   power: MDE(80%) 7.3 pts   power to detect 5 pts = 49%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -7.6 -> cannot claim parity   one-sided p = 0.168
                                   tokens 61813 vs 133186  (-53.6%, 95% CI [-55.3%, -51.9%])

N=1   tourney - baseline           d = +0.5 pts   naive 95% CI [-3.2, +4.2]   cluster 95% CI [-3.0, +4.0]   deff 0.89   b/c 29/27   McNemar p = 0.894   clustered p = 0.778
                                   power: MDE(80%) 5.0 pts   power to detect 5 pts = 80%
                                   non-inferiority (margin 5 pts): lower bound -3.0 -> NON-INFERIOR   one-sided p = 0.000978
                                   tokens 5861 vs 8238  (-28.8%, 95% CI [-32.8%, -24.9%])
N=2   tourney - baseline           d = -7.2 pts   naive 95% CI [-11.1, -3.4]   cluster 95% CI [-11.3, -3.2]   deff 1.12   b/c 17/46   McNemar p = 0.000337   clustered p = 0.000494
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 67%
                                   non-inferiority (margin 5 pts): lower bound -11.3 -> cannot claim parity   one-sided p = 0.86
                                   tokens 7931 vs 16890  (-53.0%, 95% CI [-55.3%, -50.7%])
N=4   tourney - baseline           d = -5.8 pts   naive 95% CI [-9.3, -2.2]   cluster 95% CI [-9.7, -1.8]   deff 1.23   b/c 15/38   McNemar p = 0.00219   clustered p = 0.00414
                                   power: MDE(80%) 5.6 pts   power to detect 5 pts = 70%
                                   non-inferiority (margin 5 pts): lower bound -9.7 -> cannot claim parity   one-sided p = 0.646
                                   tokens 15977 vs 33840  (-52.8%, 95% CI [-54.6%, -51.0%])
N=8   tourney - baseline           d = -4.2 pts   naive 95% CI [-8.1, -0.4]   cluster 95% CI [-8.4, -0.1]   deff 1.12   b/c 23/40   McNemar p = 0.043   clustered p = 0.0434
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
                                   non-inferiority (margin 5 pts): lower bound -8.4 -> cannot claim parity   one-sided p = 0.361
                                   tokens 32399 vs 67278  (-51.8%, 95% CI [-53.7%, -50.0%])
N=16  tourney - baseline           d = -6.5 pts   naive 95% CI [-12.4, -0.6]   cluster 95% CI [-12.0, -1.0]   deff 0.86   b/c 12/25   McNemar p = 0.047   clustered p = 0.0208
                                   power: MDE(80%) 7.9 pts   power to detect 5 pts = 43%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -12.0 -> cannot claim parity   one-sided p = 0.703
                                   tokens 63985 vs 133186  (-52.0%, 95% CI [-53.7%, -50.2%])

N=1   random - baseline            d = +1.2 pts   naive 95% CI [-2.5, +5.0]   cluster 95% CI [-2.4, +4.9]   deff 0.93   b/c 32/27   McNemar p = 0.603   clustered p = 0.501
                                   power: MDE(80%) 5.2 pts   power to detect 5 pts = 77%
                                   non-inferiority (margin 5 pts): lower bound -2.4 -> NON-INFERIOR   one-sided p = 0.000387
                                   tokens 5799 vs 8238  (-29.6%, 95% CI [-33.4%, -25.8%])
N=2   random - baseline            d = -11.2 pts   naive 95% CI [-15.5, -7.0]   cluster 95% CI [-15.9, -6.6]   deff 1.19   b/c 18/63   McNemar p = 5.2e-07   clustered p = 2.6e-06
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
                                   non-inferiority (margin 5 pts): lower bound -15.9 -> cannot claim parity   one-sided p = 0.995
                                   tokens 8188 vs 16890  (-51.5%, 95% CI [-53.9%, -49.1%])
N=4   random - baseline            d = -7.5 pts   naive 95% CI [-11.7, -3.3]   cluster 95% CI [-11.7, -3.3]   deff 0.99   b/c 23/53   McNemar p = 0.000765   clustered p = 0.000476
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 64%
                                   non-inferiority (margin 5 pts): lower bound -11.7 -> cannot claim parity   one-sided p = 0.878
                                   tokens 16475 vs 33840  (-51.3%, 95% CI [-53.5%, -49.1%])
N=8   random - baseline            d = -9.0 pts   naive 95% CI [-13.0, -5.0]   cluster 95% CI [-13.6, -4.4]   deff 1.33   b/c 17/53   McNemar p = 1.92e-05   clustered p = 0.000147
                                   power: MDE(80%) 6.6 pts   power to detect 5 pts = 56%
                                   non-inferiority (margin 5 pts): lower bound -13.6 -> cannot claim parity   one-sided p = 0.954
                                   tokens 33307 vs 67278  (-50.5%, 95% CI [-52.6%, -48.4%])
N=16  random - baseline            d = -4.0 pts   naive 95% CI [-10.0, +2.0]   cluster 95% CI [-9.7, +1.7]   deff 0.88   b/c 15/23   McNemar p = 0.256   clustered p = 0.168
                                   power: MDE(80%) 8.1 pts   power to detect 5 pts = 41%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -9.7 -> cannot claim parity   one-sided p = 0.365
                                   tokens 65871 vs 133186  (-50.5%, 95% CI [-52.8%, -48.2%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = +0.9 pts   naive 95% CI [-0.7, +2.6]   cluster 95% CI [-0.8, +2.7]   deff 1.07   b/c 126/109   McNemar p = 0.297   clustered p = 0.287
                                   power: MDE(80%) 2.5 pts   power to detect 5 pts = 100%
                                   equal-weight per N: d = +1.0 pts (from 5 cells: -2.2, +4.5, +1.5, -0.2, +1.5)

pooled rank - baseline (chunk-wtd) d = -5.4 pts   naive 95% CI [-7.2, -3.6]   cluster 95% CI [-8.2, -2.6]   deff 2.45   b/c 85/182   McNemar p = 2.86e-09   clustered p = 0.000141
                                   power: MDE(80%) 4.0 pts   power to detect 5 pts = 94%
                                   equal-weight per N: d = -5.1 pts (from 5 cells: -1.0, -6.8, -6.0, -9.2, -2.5)

pooled tourney - baseline (chunk-wtd) d = -4.4 pts   naive 95% CI [-6.2, -2.7]   cluster 95% CI [-7.0, -1.9]   deff 2.03   b/c 96/176   McNemar p = 1.41e-06   clustered p = 0.000643
                                   power: MDE(80%) 3.6 pts   power to detect 5 pts = 97%
                                   equal-weight per N: d = -4.7 pts (from 5 cells: +0.5, -7.2, -5.8, -4.2, -6.5)

pooled random - baseline (chunk-wtd) d = -6.3 pts   naive 95% CI [-8.3, -4.4]   cluster 95% CI [-9.0, -3.7]   deff 1.84   b/c 105/219   McNemar p = 2.26e-10   clustered p = 2.69e-06
                                   power: MDE(80%) 3.8 pts   power to detect 5 pts = 96%
                                   equal-weight per N: d = -6.1 pts (from 5 cells: +1.2, -11.2, -7.5, -9.0, -4.0)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = -1.0 pts   95% CI [-4.4, +2.4]   win/loss 16/20   p = 0.565   sign p = 0.618
                                   tokens 6137 vs 8238 (-25.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.4 -> NON-INFERIOR   one-sided p = 0.0107
                                   WARNING: -26% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 4.9 pts   power to detect 5 pts = 82%
rank N=2 vs baseline N=1           d = +3.0 pts   95% CI [-1.0, +7.0]   win/loss 23/13   p = 0.137   sign p = 0.132
                                   tokens 7928 vs 8238 (-3.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.0 -> NON-INFERIOR   one-sided p = 3.71e-05
                                   power: MDE(80%) 5.7 pts   power to detect 5 pts = 70%
rank N=4 vs baseline N=2           d = +0.8 pts   95% CI [-3.5, +5.0]   win/loss 18/13   p = 0.73   sign p = 0.473
                                   tokens 16255 vs 16890 (-3.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.5 -> NON-INFERIOR   one-sided p = 0.0041
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
rank N=8 vs baseline N=4           d = -4.5 pts   95% CI [-8.3, -0.7]   win/loss 12/23   p = 0.0216   sign p = 0.0895
                                   tokens 31452 vs 33840 (-7.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -8.3 -> cannot claim parity   one-sided p = 0.399
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 72%
rank N=16 vs baseline N=8          d = +1.0 pts   95% CI [-3.7, +5.7]   win/loss 20/17   p = 0.675   sign p = 0.743
                                   tokens 61813 vs 67278 (-8.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.7 -> NON-INFERIOR   one-sided p = 0.00588
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 56%

random N=1 vs baseline N=1         d = +1.2 pts   95% CI [-2.4, +4.9]   win/loss 20/17   p = 0.501   sign p = 0.743
                                   tokens 5799 vs 8238 (-29.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.4 -> NON-INFERIOR   one-sided p = 0.000387
                                   WARNING: -30% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.2 pts   power to detect 5 pts = 77%
random N=2 vs baseline N=1         d = -1.5 pts   95% CI [-5.8, +2.8]   win/loss 21/23   p = 0.492   sign p = 0.88
                                   tokens 8188 vs 8238 (-0.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.8 -> cannot claim parity   one-sided p = 0.0546
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
random N=4 vs baseline N=2         d = -0.8 pts   95% CI [-5.0, +3.5]   win/loss 17/19   p = 0.727   sign p = 0.868
                                   tokens 16475 vs 16890 (-2.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.0 -> NON-INFERIOR   one-sided p = 0.0238
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 64%
random N=8 vs baseline N=4         d = -4.2 pts   95% CI [-8.2, -0.3]   win/loss 12/23   p = 0.0346   sign p = 0.0895
                                   tokens 33307 vs 33840 (-1.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -8.2 -> cannot claim parity   one-sided p = 0.355
                                   power: MDE(80%) 5.6 pts   power to detect 5 pts = 70%
random N=16 vs baseline N=8        d = -0.5 pts   95% CI [-5.7, +4.7]   win/loss 19/19   p = 0.849   sign p = 1
                                   tokens 65871 vs 67278 (-2.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.7 -> cannot claim parity   one-sided p = 0.0438
                                   power: MDE(80%) 7.4 pts   power to detect 5 pts = 48%   <- underpowered

tourney N=1 vs baseline N=1        d = +0.5 pts   95% CI [-3.0, +4.0]   win/loss 19/16   p = 0.778   sign p = 0.736
                                   tokens 5861 vs 8238 (-28.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.0 -> NON-INFERIOR   one-sided p = 0.000978
                                   WARNING: -29% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.0 pts   power to detect 5 pts = 80%
tourney N=2 vs baseline N=1        d = +2.5 pts   95% CI [-1.7, +6.7]   win/loss 22/15   p = 0.244   sign p = 0.324
                                   tokens 7931 vs 8238 (-3.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.7 -> NON-INFERIOR   one-sided p = 0.000238
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 64%
tourney N=4 vs baseline N=2        d = +1.0 pts   95% CI [-3.0, +5.0]   win/loss 18/14   p = 0.624   sign p = 0.597
                                   tokens 15977 vs 16890 (-5.4% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.0 -> NON-INFERIOR   one-sided p = 0.00163
                                   power: MDE(80%) 5.7 pts   power to detect 5 pts = 69%
tourney N=8 vs baseline N=4        d = +0.5 pts   95% CI [-3.1, +4.1]   win/loss 15/16   p = 0.786   sign p = 1
                                   tokens 32399 vs 33840 (-4.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.1 -> NON-INFERIOR   one-sided p = 0.00144
                                   power: MDE(80%) 5.2 pts   power to detect 5 pts = 77%
tourney N=16 vs baseline N=8       d = -3.0 pts   95% CI [-7.8, +1.8]   win/loss 15/19   p = 0.224   sign p = 0.608
                                   tokens 63985 vs 67278 (-4.9% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -7.8 -> cannot claim parity   one-sided p = 0.209
                                   power: MDE(80%) 6.9 pts   power to detect 5 pts = 53%

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

============================================================================================================
8. CROSS-CONFIG SUMMARY   (the stable estimate: average over the grid)

   A single config is one noisy draw. Quoting the best cell overstates the
   effect because it is the maximum of many noisy cells. These are means.

   arm          N  configs  acc mean    min    max    tokens  vs base
   baseline     1        2     47.2%     47     47     8,238     0.0%
   rank         1        2     46.2%     46     46     6,228   -24.4%
   random       1        2     47.9%     47     48     5,877   -28.7%
   tourney      1        2     46.9%     46     48     5,936   -27.9%

   baseline     2        2     57.0%     57     57    16,890     0.0%
   rank         2        2     48.2%     46     50     7,436   -56.0%
   random       2        2     44.8%     44     46     7,597   -55.0%
   tourney      2        2     48.5%     47     50     7,452   -55.9%

   baseline     4        2     63.7%     64     64    33,840     0.0%
   rank         4        2     56.4%     55     58    15,156   -55.2%
   random       4        2     54.8%     53     56    15,192   -55.1%
   tourney      4        2     56.6%     55     58    14,954   -55.8%

   baseline     8        2     68.5%     68     68    67,278     0.0%
   rank         8        2     60.9%     59     62    29,473   -56.2%
   random       8        2     60.2%     60     61    30,699   -54.4%
   tourney      8        2     62.4%     60     64    30,244   -55.0%

   baseline    16        2     72.0%     72     72   133,186     0.0%
   rank        16        2     68.0%     66     70    57,769   -56.6%
   random      16        2     67.3%     66     68    60,612   -54.5%
   tourney     16        2     64.8%     64     66    59,933   -55.0%

   baseline    32        2     75.0%     75     75   264,452     0.0%

   ORACLE CEILING COLLAPSE   (what pruning costs you before the judge acts)

   Pruning discards candidates, so a correct answer may never reach the judge.
   A smaller judge gap on a pruned arm is less headroom, not better selection.

   arm          N   ceiling  selected  judge gap  ceiling vs base
   baseline     1     47.2%     47.2%       0.0p             0.0p
   rank         1     46.2%     46.2%       0.0p            -1.0p
   random       1     47.9%     47.9%       0.0p             0.6p
   tourney      1     46.9%     46.9%       0.0p            -0.4p

   baseline     2     59.0%     57.0%       2.0p             0.0p
   rank         2     48.2%     48.2%       0.0p           -10.7p
   random       2     44.8%     44.8%       0.0p           -14.2p
   tourney      2     48.5%     48.5%       0.0p           -10.5p

   baseline     4     66.8%     63.7%       3.0p             0.0p
   rank         4     57.4%     56.4%       1.0p            -9.4p
   random       4     56.6%     54.8%       1.9p           -10.1p
   tourney      4     57.5%     56.6%       0.9p            -9.3p

   baseline     8     75.8%     68.5%       7.2p             0.0p
   rank         8     63.7%     60.9%       2.9p           -12.0p
   random       8     64.0%     60.2%       3.7p           -11.7p
   tourney      8     64.5%     62.4%       2.1p           -11.2p

   baseline    16     80.5%     72.0%       8.5p             0.0p
   rank        16     74.2%     68.0%       6.2p            -6.3p
   random      16     72.2%     67.3%       5.0p            -8.3p
   tourney     16     70.5%     64.8%       5.8p           -10.0p

   baseline    32     87.0%     75.0%      12.0p             0.0p


============================================================================================================
9. ISO-TOKEN CONTRASTS   (baseline curve INTERPOLATED to each cell's actual spend)

   Section 6 snaps each cell to the nearest baseline N, leaving budget gaps up to
   +49%. Here the baseline accuracy-vs-token curve is log-interpolated to the exact
   budget each cell spent, so there is no mismatch left to warn about.

   baseline stop-tail correction: 26.25% of generated tokens
   fall after the first </answer>, which the baseline is charged for and the arms
   are not (no stop string on the baseline; stop=['</answer>'] on the arms).

      N  baseline acc   tokens raw  tokens corrected
      1         47.2%        8,238             6,073
      2         57.0%       16,890            12,560
      4         63.7%       33,840            25,181
      8         68.5%       67,278            49,959
     16         72.0%      133,186            98,549
     32         75.0%      264,452           195,176

   RAW baseline: arm accuracy minus interpolated baseline accuracy
     over 30 equal-N cells:  mean -0.45 pts   median -0.43 pts   positive 11/30   (negative 17, exact ties 2)
       plan=1000  mean -0.83 pts   (15 cells)
       plan=2500  mean -0.07 pts   (15 cells)

   STOP-CORRECTED baseline: arm accuracy minus interpolated baseline accuracy
     over 30 equal-N cells:  mean -2.52 pts   median -2.15 pts   positive 2/30   (negative 27, exact ties 1)
       plan=1000  mean -2.85 pts   (15 cells)
       plan=2500  mean -2.19 pts   (15 cells)

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
   arm-contrast           40     21          2     14    20
   judge-vs-random        23     23          1     23    23
   non-inferiority        70     33          4      7    23
   pooled                  8      6          0      6     6
   token-matched          30      2          2      0     0

   13 nominally-significant results do NOT survive BH within their family.
   Do not cite these on their own:
     p=0.0216    [token-matched] plan=2500,prune=2.0  rank N=8 vs baseline N=4
     p=0.0238    [non-inferiority] plan=2500,prune=2.0  [NI] random N=4 vs baseline N=2
     p=0.0284    [non-inferiority] plan=1000,prune=2.0  [NI] N=1   rank - random
     p=0.0298    [non-inferiority] plan=1000,prune=2.0  [NI] rank N=8 vs baseline N=4
     p=0.03      [non-inferiority] plan=1000,prune=2.0  [NI] N=16  rank - random
     p=0.032     [non-inferiority] plan=1000,prune=2.0  [NI] N=1   rank - baseline
     p=0.032     [non-inferiority] plan=1000,prune=2.0  [NI] rank N=1 vs baseline N=1
     p=0.0346    [token-matched] plan=2500,prune=2.0  random N=8 vs baseline N=4
     p=0.038     [non-inferiority] plan=1000,prune=2.0  [NI] N=1   tourney - baseline
     p=0.038     [non-inferiority] plan=1000,prune=2.0  [NI] tourney N=1 vs baseline N=1
     p=0.0434    [arm-contrast] plan=2500,prune=2.0  N=8   tourney - baseline
     p=0.0438    [non-inferiority] plan=2500,prune=2.0  [NI] random N=16 vs baseline N=8
     p=0.0483    [non-inferiority] plan=1000,prune=2.0  [NI] rank N=2 vs baseline N=1

   50 results survive the strict Holm correction; these are the safe ones to quote.
