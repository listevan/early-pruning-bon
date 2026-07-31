
############################################################################################################
# CONFIG  plan=1000  prune=2.0
############################################################################################################
============================================================================================================
FILES
  baseline  2026-07-25_11-42-12_baseline_bon_1_2_4_8_16_32_strat_None_plan_4000_prune_2.json
  random    merged_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_2.0_regen.json
  rank      merged_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_2.0_regen.json
  tourney   merged_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_2.0_regen.json
  N values: [1, 2, 4, 8, 16, 32]
  questions: baseline=100, random=100, rank=100, tourney=100

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16            N=32
baseline      47.2%   8238t    57.0%  16890t    63.7%  33840t    68.5%  67278t    72.0% 133186t    75.0% 264452t
rank          46.2%   6214t    53.2%  11941t    61.0%  23492t    65.5%  46531t    68.5%  90298t               -
random        45.8%   5930t    56.2%  12089t    58.5%  24714t    65.8%  47884t    70.5%  93745t               -
tourney       46.5%   6013t    55.5%  11924t    62.3%  23417t    66.0%  46307t    66.0%  92213t               -

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
rank N=2: judge - random           d = +9.0 pts   naive 95% CI [+5.9, +12.1]   cluster 95% CI [+5.6, +12.4]   deff 1.20   b/c 40/4   McNemar p = 1.71e-08   clustered p = 3.14e-07
                                   power: MDE(80%) 4.9 pts   power to detect 5 pts = 81%
rank N=4: judge - random           d = +14.0 pts   naive 95% CI [+10.2, +17.8]   cluster 95% CI [+9.5, +18.5]   deff 1.40   b/c 62/6   McNemar p = 8.18e-13   clustered p = 1.39e-09
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 58%
rank N=8: judge - random           d = +18.8 pts   naive 95% CI [+14.5, +23.0]   cluster 95% CI [+13.4, +24.1]   deff 1.58   b/c 82/7   McNemar p = 2.43e-17   clustered p = 7.49e-12
                                   power: MDE(80%) 7.7 pts   power to detect 5 pts = 45%   <- underpowered; a null here is NOT evidence of no effect
rank N=16: judge - random          d = +22.0 pts   naive 95% CI [+15.8, +28.2]   cluster 95% CI [+15.3, +28.7]   deff 1.15   b/c 47/3   McNemar p = 3.71e-11   clustered p = 1.45e-10
                                   power: MDE(80%) 9.6 pts   power to detect 5 pts = 31%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +9.0 pts   naive 95% CI [+6.0, +12.0]   cluster 95% CI [+5.7, +12.3]   deff 1.22   b/c 38/2   McNemar p = 1.49e-09   clustered p = 9.43e-08
                                   power: MDE(80%) 4.7 pts   power to detect 5 pts = 84%
random N=4: judge - random         d = +13.5 pts   naive 95% CI [+9.4, +17.6]   cluster 95% CI [+8.9, +18.1]   deff 1.25   b/c 66/12   McNemar p = 3.49e-10   clustered p = 1.2e-08
                                   power: MDE(80%) 6.6 pts   power to detect 5 pts = 56%
random N=8: judge - random         d = +21.2 pts   naive 95% CI [+16.6, +25.9]   cluster 95% CI [+15.6, +26.9]   deff 1.43   b/c 97/12   McNemar p = 1.1e-17   clustered p = 1.4e-13
                                   power: MDE(80%) 8.0 pts   power to detect 5 pts = 41%   <- underpowered; a null here is NOT evidence of no effect
random N=16: judge - random        d = +27.5 pts   naive 95% CI [+20.4, +34.6]   cluster 95% CI [+19.8, +35.2]   deff 1.17   b/c 61/6   McNemar p = 1.49e-12   clustered p = 2.2e-12
                                   power: MDE(80%) 11.0 pts   power to detect 5 pts = 25%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +11.5 pts   naive 95% CI [+8.1, +14.9]   cluster 95% CI [+7.6, +15.4]   deff 1.29   b/c 50/4   McNemar p = 3.8e-11   clustered p = 7.75e-09
                                   power: MDE(80%) 5.6 pts   power to detect 5 pts = 71%
tourney N=4: judge - random        d = +16.8 pts   naive 95% CI [+12.7, +20.8]   cluster 95% CI [+11.6, +21.9]   deff 1.59   b/c 73/6   McNemar p = 1e-15   clustered p = 1.44e-10
                                   power: MDE(80%) 7.3 pts   power to detect 5 pts = 48%   <- underpowered; a null here is NOT evidence of no effect
tourney N=8: judge - random        d = +19.8 pts   naive 95% CI [+15.3, +24.2]   cluster 95% CI [+14.6, +24.9]   deff 1.36   b/c 88/9   McNemar p = 2e-17   clustered p = 7.75e-14
                                   power: MDE(80%) 7.4 pts   power to detect 5 pts = 47%   <- underpowered; a null here is NOT evidence of no effect
tourney N=16: judge - random       d = +20.5 pts   naive 95% CI [+13.7, +27.3]   cluster 95% CI [+12.7, +28.3]   deff 1.27   b/c 49/8   McNemar p = 2.72e-08   clustered p = 2.3e-07
                                   power: MDE(80%) 11.1 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect

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
rank       N=2   ceiling  54.8%   selected  53.2%   gap  1.5 pts   capture  97.3%
rank       N=4   ceiling  64.2%   selected  61.0%   gap  3.2 pts   capture  94.9%
rank       N=8   ceiling  70.8%   selected  65.5%   gap  5.2 pts   capture  92.6%
rank       N=16  ceiling  77.5%   selected  68.5%   gap  9.0 pts   capture  88.4%

random     N=1   ceiling  45.8%   selected  45.8%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  57.8%   selected  56.2%   gap  1.5 pts   capture  97.4%
random     N=4   ceiling  63.2%   selected  58.5%   gap  4.7 pts   capture  92.5%
random     N=8   ceiling  71.2%   selected  65.8%   gap  5.5 pts   capture  92.3%
random     N=16  ceiling  78.5%   selected  70.5%   gap  8.0 pts   capture  89.8%

tourney    N=1   ceiling  46.5%   selected  46.5%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  58.5%   selected  55.5%   gap  3.0 pts   capture  94.9%
tourney    N=4   ceiling  65.5%   selected  62.3%   gap  3.2 pts   capture  95.0%
tourney    N=8   ceiling  71.5%   selected  66.0%   gap  5.5 pts   capture  92.3%
tourney    N=16  ceiling  75.5%   selected  66.0%   gap  9.5 pts   capture  87.4%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = +0.5 pts   naive 95% CI [-3.8, +4.8]   cluster 95% CI [-4.1, +5.1]   deff 1.15   b/c 39/37   McNemar p = 0.909   clustered p = 0.832
                                   power: MDE(80%) 6.6 pts   power to detect 5 pts = 56%
                                   non-inferiority (margin 5 pts): lower bound -4.1 -> NON-INFERIOR   one-sided p = 0.0098
                                   tokens 6214 vs 5930  (+4.8%, 95% CI [-0.1%, +9.6%])
N=2   rank - random                d = -3.0 pts   naive 95% CI [-7.2, +1.2]   cluster 95% CI [-7.5, +1.5]   deff 1.18   b/c 30/42   McNemar p = 0.195   clustered p = 0.194
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 58%
                                   non-inferiority (margin 5 pts): lower bound -7.5 -> cannot claim parity   one-sided p = 0.193
                                   tokens 11941 vs 12089  (-1.2%, 95% CI [-5.3%, +2.8%])
N=4   rank - random                d = +2.5 pts   naive 95% CI [-1.8, +6.8]   cluster 95% CI [-1.5, +6.5]   deff 0.86   b/c 43/33   McNemar p = 0.302   clustered p = 0.217
                                   power: MDE(80%) 5.7 pts   power to detect 5 pts = 69%
                                   non-inferiority (margin 5 pts): lower bound -1.5 -> NON-INFERIOR   one-sided p = 0.000107
                                   tokens 23492 vs 24714  (-4.9%, 95% CI [-8.0%, -1.9%])
N=8   rank - random                d = -0.2 pts   naive 95% CI [-4.2, +3.7]   cluster 95% CI [-4.5, +4.0]   deff 1.15   b/c 32/33   McNemar p = 1   clustered p = 0.909
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
                                   non-inferiority (margin 5 pts): lower bound -4.5 -> NON-INFERIOR   one-sided p = 0.0145
                                   tokens 46531 vs 47884  (-2.8%, 95% CI [-5.1%, -0.6%])
N=16  rank - random                d = -2.0 pts   naive 95% CI [-7.6, +3.6]   cluster 95% CI [-8.1, +4.1]   deff 1.18   b/c 14/18   McNemar p = 0.597   clustered p = 0.518
                                   power: MDE(80%) 8.7 pts   power to detect 5 pts = 37%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -8.1 -> cannot claim parity   one-sided p = 0.166
                                   tokens 90298 vs 93745  (-3.7%, 95% CI [-5.9%, -1.5%])

N=1   rank - baseline              d = -1.0 pts   naive 95% CI [-5.4, +3.4]   cluster 95% CI [-5.1, +3.1]   deff 0.87   b/c 38/42   McNemar p = 0.738   clustered p = 0.634
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
                                   non-inferiority (margin 5 pts): lower bound -5.1 -> cannot claim parity   one-sided p = 0.0284
                                   tokens 6214 vs 8238  (-24.6%, 95% CI [-29.4%, -19.8%])
N=2   rank - baseline              d = -3.8 pts   naive 95% CI [-7.6, +0.1]   cluster 95% CI [-7.5, +0.0]   deff 0.97   b/c 23/38   McNemar p = 0.0722   clustered p = 0.0515
                                   power: MDE(80%) 5.4 pts   power to detect 5 pts = 74%
                                   non-inferiority (margin 5 pts): lower bound -7.5 -> cannot claim parity   one-sided p = 0.258
                                   tokens 11941 vs 16890  (-29.3%, 95% CI [-32.6%, -26.0%])
N=4   rank - baseline              d = -2.8 pts   naive 95% CI [-6.8, +1.3]   cluster 95% CI [-6.5, +1.0]   deff 0.86   b/c 28/39   McNemar p = 0.222   clustered p = 0.15
                                   power: MDE(80%) 5.4 pts   power to detect 5 pts = 74%
                                   non-inferiority (margin 5 pts): lower bound -6.5 -> cannot claim parity   one-sided p = 0.119
                                   tokens 23492 vs 33840  (-30.6%, 95% CI [-33.0%, -28.2%])
N=8   rank - baseline              d = -3.0 pts   naive 95% CI [-7.0, +1.0]   cluster 95% CI [-7.3, +1.3]   deff 1.13   b/c 28/40   McNemar p = 0.182   clustered p = 0.172
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
                                   non-inferiority (margin 5 pts): lower bound -7.3 -> cannot claim parity   one-sided p = 0.181
                                   tokens 46531 vs 67278  (-30.8%, 95% CI [-32.8%, -28.9%])
N=16  rank - baseline              d = -3.5 pts   naive 95% CI [-9.8, +2.8]   cluster 95% CI [-9.9, +2.9]   deff 1.04   b/c 17/24   McNemar p = 0.349   clustered p = 0.285
                                   power: MDE(80%) 9.2 pts   power to detect 5 pts = 33%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -9.9 -> cannot claim parity   one-sided p = 0.324
                                   tokens 90298 vs 133186  (-32.2%, 95% CI [-34.1%, -30.3%])

N=1   tourney - baseline           d = -0.8 pts   naive 95% CI [-5.1, +3.6]   cluster 95% CI [-4.8, +3.3]   deff 0.87   b/c 38/41   McNemar p = 0.822   clustered p = 0.719
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 67%
                                   non-inferiority (margin 5 pts): lower bound -4.8 -> NON-INFERIOR   one-sided p = 0.0208
                                   tokens 6013 vs 8238  (-27.0%, 95% CI [-31.6%, -22.4%])
N=2   tourney - baseline           d = -1.5 pts   naive 95% CI [-6.0, +3.0]   cluster 95% CI [-6.0, +3.0]   deff 0.99   b/c 39/45   McNemar p = 0.586   clustered p = 0.514
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 59%
                                   non-inferiority (margin 5 pts): lower bound -6.0 -> cannot claim parity   one-sided p = 0.0639
                                   tokens 11924 vs 16890  (-29.4%, 95% CI [-32.8%, -26.0%])
N=4   tourney - baseline           d = -1.5 pts   naive 95% CI [-5.4, +2.4]   cluster 95% CI [-4.9, +1.9]   deff 0.74   b/c 29/35   McNemar p = 0.532   clustered p = 0.387
                                   power: MDE(80%) 4.9 pts   power to detect 5 pts = 82%
                                   non-inferiority (margin 5 pts): lower bound -4.9 -> NON-INFERIOR   one-sided p = 0.0218
                                   tokens 23417 vs 33840  (-30.8%, 95% CI [-33.1%, -28.5%])
N=8   tourney - baseline           d = -2.5 pts   naive 95% CI [-6.7, +1.7]   cluster 95% CI [-6.7, +1.7]   deff 1.01   b/c 31/41   McNemar p = 0.289   clustered p = 0.244
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 64%
                                   non-inferiority (margin 5 pts): lower bound -6.7 -> cannot claim parity   one-sided p = 0.122
                                   tokens 46307 vs 67278  (-31.2%, 95% CI [-33.1%, -29.2%])
N=16  tourney - baseline           d = -6.0 pts   naive 95% CI [-11.8, -0.2]   cluster 95% CI [-11.6, -0.4]   deff 0.92   b/c 12/24   McNemar p = 0.0652   clustered p = 0.0364
                                   power: MDE(80%) 8.0 pts   power to detect 5 pts = 41%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -11.6 -> cannot claim parity   one-sided p = 0.636
                                   tokens 92213 vs 133186  (-30.8%, 95% CI [-32.8%, -28.7%])

N=1   random - baseline            d = -1.5 pts   naive 95% CI [-5.7, +2.7]   cluster 95% CI [-5.9, +2.9]   deff 1.13   b/c 33/39   McNemar p = 0.556   clustered p = 0.509
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 60%
                                   non-inferiority (margin 5 pts): lower bound -5.9 -> cannot claim parity   one-sided p = 0.0616
                                   tokens 5930 vs 8238  (-28.0%, 95% CI [-32.2%, -23.8%])
N=2   random - baseline            d = -0.8 pts   naive 95% CI [-4.8, +3.3]   cluster 95% CI [-5.4, +3.9]   deff 1.35   b/c 32/35   McNemar p = 0.807   clustered p = 0.754
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
                                   non-inferiority (margin 5 pts): lower bound -5.4 -> cannot claim parity   one-sided p = 0.038
                                   tokens 12089 vs 16890  (-28.4%, 95% CI [-32.1%, -24.7%])
N=4   random - baseline            d = -5.2 pts   naive 95% CI [-9.6, -0.9]   cluster 95% CI [-9.5, -1.0]   deff 0.96   b/c 29/50   McNemar p = 0.0238   clustered p = 0.0155
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
                                   non-inferiority (margin 5 pts): lower bound -9.5 -> cannot claim parity   one-sided p = 0.546
                                   tokens 24714 vs 33840  (-27.0%, 95% CI [-30.0%, -23.9%])
N=8   random - baseline            d = -2.8 pts   naive 95% CI [-7.1, +1.6]   cluster 95% CI [-7.0, +1.5]   deff 0.96   b/c 34/45   McNemar p = 0.26   clustered p = 0.209
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
                                   non-inferiority (margin 5 pts): lower bound -7.0 -> cannot claim parity   one-sided p = 0.152
                                   tokens 47884 vs 67278  (-28.8%, 95% CI [-31.1%, -26.6%])
N=16  random - baseline            d = -1.5 pts   naive 95% CI [-7.3, +4.3]   cluster 95% CI [-6.6, +3.6]   deff 0.77   b/c 16/19   McNemar p = 0.736   clustered p = 0.565
                                   power: MDE(80%) 7.3 pts   power to detect 5 pts = 48%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -6.6 -> cannot claim parity   one-sided p = 0.0897
                                   tokens 93745 vs 133186  (-29.6%, 95% CI [-32.0%, -27.2%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = -0.3 pts   naive 95% CI [-2.2, +1.7]   cluster 95% CI [-2.4, +1.9]   deff 1.22   b/c 158/163   McNemar p = 0.823   clustered p = 0.802
                                   power: MDE(80%) 3.1 pts   power to detect 5 pts = 99%
                                   equal-weight per N: d = -0.4 pts (from 5 cells: +0.5, -3.0, +2.5, -0.2, -2.0)

pooled rank - baseline (chunk-wtd) d = -2.7 pts   naive 95% CI [-4.7, -0.8]   cluster 95% CI [-5.1, -0.3]   deff 1.54   b/c 134/183   McNemar p = 0.00693   clustered p = 0.0272
                                   power: MDE(80%) 3.5 pts   power to detect 5 pts = 98%
                                   equal-weight per N: d = -2.8 pts (from 5 cells: -1.0, -3.8, -2.8, -3.0, -3.5)

pooled tourney - baseline (chunk-wtd) d = -2.1 pts   naive 95% CI [-4.0, -0.1]   cluster 95% CI [-4.5, +0.3]   deff 1.44   b/c 149/186   McNemar p = 0.049   clustered p = 0.0933
                                   power: MDE(80%) 3.4 pts   power to detect 5 pts = 98%
                                   equal-weight per N: d = -2.5 pts (from 5 cells: -0.8, -1.5, -1.5, -2.5, -6.0)

pooled random - baseline (chunk-wtd) d = -2.4 pts   naive 95% CI [-4.4, -0.5]   cluster 95% CI [-5.1, +0.2]   deff 1.72   b/c 144/188   McNemar p = 0.0181   clustered p = 0.0664
                                   power: MDE(80%) 3.7 pts   power to detect 5 pts = 96%
                                   equal-weight per N: d = -2.4 pts (from 5 cells: -1.5, -0.8, -5.2, -2.8, -1.5)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = -1.0 pts   95% CI [-5.1, +3.1]   win/loss 16/17   p = 0.634   sign p = 1
                                   tokens 6214 vs 8238 (-24.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.1 -> cannot claim parity   one-sided p = 0.0284
                                   WARNING: -25% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.9 pts   power to detect 5 pts = 66%
rank N=2 vs baseline N=1           d = +6.0 pts   95% CI [+1.7, +10.3]   win/loss 27/12   p = 0.00624   sign p = 0.0237
                                   tokens 11941 vs 8238 (+45.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +1.7 -> NON-INFERIOR   one-sided p = 2.67e-07
                                   WARNING: +45% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
rank N=4 vs baseline N=2           d = +4.0 pts   95% CI [-0.7, +8.7]   win/loss 23/17   p = 0.0923   sign p = 0.43
                                   tokens 23492 vs 16890 (+39.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -0.7 -> NON-INFERIOR   one-sided p = 7.61e-05
                                   WARNING: +39% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 56%
rank N=8 vs baseline N=4           d = +1.8 pts   95% CI [-2.1, +5.6]   win/loss 18/13   p = 0.371   sign p = 0.473
                                   tokens 46531 vs 33840 (+37.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.1 -> NON-INFERIOR   one-sided p = 0.000277
                                   WARNING: +38% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 73%
rank N=16 vs baseline N=8          d = +0.0 pts   95% CI [-5.1, +5.1]   win/loss 19/18   p = 1   sign p = 1
                                   tokens 90298 vs 67278 (+34.2% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.1 -> cannot claim parity   one-sided p = 0.0266
                                   WARNING: +34% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 7.2 pts   power to detect 5 pts = 49%   <- underpowered

random N=1 vs baseline N=1         d = -1.5 pts   95% CI [-5.9, +2.9]   win/loss 17/19   p = 0.509   sign p = 0.868
                                   tokens 5930 vs 8238 (-28.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.9 -> cannot claim parity   one-sided p = 0.0616
                                   WARNING: -28% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 60%
random N=2 vs baseline N=1         d = +9.0 pts   95% CI [+4.3, +13.7]   win/loss 30/8   p = 0.000174   sign p = 0.000472
                                   tokens 12089 vs 8238 (+46.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +4.3 -> NON-INFERIOR   one-sided p = 2.61e-09
                                   WARNING: +47% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
random N=4 vs baseline N=2         d = +1.5 pts   95% CI [-3.2, +6.2]   win/loss 24/20   p = 0.533   sign p = 0.652
                                   tokens 24714 vs 16890 (+46.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.2 -> NON-INFERIOR   one-sided p = 0.00344
                                   WARNING: +46% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
random N=8 vs baseline N=4         d = +2.0 pts   95% CI [-2.4, +6.4]   win/loss 21/21   p = 0.378   sign p = 1
                                   tokens 47884 vs 33840 (+41.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.4 -> NON-INFERIOR   one-sided p = 0.00101
                                   WARNING: +41% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 60%
random N=16 vs baseline N=8        d = +2.0 pts   95% CI [-2.9, +6.9]   win/loss 23/14   p = 0.42   sign p = 0.188
                                   tokens 93745 vs 67278 (+39.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.9 -> NON-INFERIOR   one-sided p = 0.00238
                                   WARNING: +39% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.9 pts   power to detect 5 pts = 52%

tourney N=1 vs baseline N=1        d = -0.8 pts   95% CI [-4.8, +3.3]   win/loss 17/17   p = 0.719   sign p = 1
                                   tokens 6013 vs 8238 (-27.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.8 -> NON-INFERIOR   one-sided p = 0.0208
                                   WARNING: -27% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 67%
tourney N=2 vs baseline N=1        d = +8.2 pts   95% CI [+3.4, +13.1]   win/loss 33/12   p = 0.000917   sign p = 0.00246
                                   tokens 11924 vs 8238 (+44.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +3.4 -> NON-INFERIOR   one-sided p = 5.08e-08
                                   WARNING: +45% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 7.0 pts   power to detect 5 pts = 52%
tourney N=4 vs baseline N=2        d = +5.2 pts   95% CI [+0.8, +9.7]   win/loss 25/14   p = 0.0215   sign p = 0.108
                                   tokens 23417 vs 16890 (+38.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.8 -> NON-INFERIOR   one-sided p = 3.58e-06
                                   WARNING: +39% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 59%
tourney N=8 vs baseline N=4        d = +2.2 pts   95% CI [-2.3, +6.8]   win/loss 18/18   p = 0.335   sign p = 1
                                   tokens 46307 vs 33840 (+36.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.3 -> NON-INFERIOR   one-sided p = 0.000942
                                   WARNING: +37% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.5 pts   power to detect 5 pts = 57%
tourney N=16 vs baseline N=8       d = -2.5 pts   95% CI [-8.1, +3.1]   win/loss 22/22   p = 0.381   sign p = 1
                                   tokens 92213 vs 67278 (+37.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -8.1 -> cannot claim parity   one-sided p = 0.191
                                   WARNING: +37% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 8.0 pts   power to detect 5 pts = 42%   <- underpowered

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

############################################################################################################
# CONFIG  plan=2500  prune=2.0
############################################################################################################
============================================================================================================
FILES
  baseline  2026-07-25_11-42-12_baseline_bon_1_2_4_8_16_32_strat_None_plan_4000_prune_2.json
  random    merged_random_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_2.0_regen.json
  rank      merged_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_2.0_regen.json
  tourney   merged_tourney_bon_1_2_4_8_16_strat_CompletionStrategy_plan_2500_prune_2.0_regen.json
  N values: [1, 2, 4, 8, 16, 32]
  questions: baseline=100, random=100, rank=100, tourney=100

============================================================================================================
1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)

arm                    N=1             N=2             N=4             N=8            N=16            N=32
baseline      47.2%   8238t    57.0%  16890t    63.7%  33840t    68.5%  67278t    72.0% 133186t    75.0% 264452t
rank          46.2%   6139t    54.2%  11297t    62.0%  22520t    66.0%  44176t    72.0%  86189t               -
random        48.5%   5799t    52.5%  11984t    59.2%  24104t    65.0%  48731t    69.0%  95223t               -
tourney       47.8%   5861t    55.2%  11044t    59.0%  22225t    66.0%  45049t    69.5%  88802t               -

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
rank N=2: judge - random           d = +3.8 pts   naive 95% CI [+1.8, +5.7]   cluster 95% CI [+1.7, +5.8]   deff 1.02   b/c 16/1   McNemar p = 0.000275   clustered p = 0.000266
                                   power: MDE(80%) 2.9 pts   power to detect 5 pts = 100%
rank N=4: judge - random           d = +10.2 pts   naive 95% CI [+6.8, +13.7]   cluster 95% CI [+5.9, +14.6]   deff 1.54   b/c 48/7   McNemar p = 1.31e-08   clustered p = 3.96e-06
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 61%
rank N=8: judge - random           d = +16.8 pts   naive 95% CI [+12.5, +21.0]   cluster 95% CI [+11.7, +21.8]   deff 1.41   b/c 76/9   McNemar p = 2.41e-14   clustered p = 6.42e-11
                                   power: MDE(80%) 7.2 pts   power to detect 5 pts = 50%   <- underpowered; a null here is NOT evidence of no effect
rank N=16: judge - random          d = +21.5 pts   naive 95% CI [+15.5, +27.5]   cluster 95% CI [+14.6, +28.4]   deff 1.28   b/c 45/2   McNemar p = 1.6e-11   clustered p = 8.11e-10
                                   power: MDE(80%) 9.8 pts   power to detect 5 pts = 30%   <- underpowered; a null here is NOT evidence of no effect

random N=1: judge - random         d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
random N=2: judge - random         d = +4.0 pts   naive 95% CI [+1.8, +6.2]   cluster 95% CI [+1.8, +6.2]   deff 1.00   b/c 18/2   McNemar p = 0.000402   clustered p = 0.000305
                                   power: MDE(80%) 3.1 pts   power to detect 5 pts = 99%
random N=4: judge - random         d = +12.8 pts   naive 95% CI [+8.8, +16.7]   cluster 95% CI [+8.5, +17.0]   deff 1.16   b/c 61/10   McNemar p = 4.64e-10   clustered p = 4.63e-09
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
random N=8: judge - random         d = +19.5 pts   naive 95% CI [+15.3, +23.7]   cluster 95% CI [+14.7, +24.3]   deff 1.30   b/c 83/5   McNemar p = 2.69e-19   clustered p = 1.78e-15
                                   power: MDE(80%) 6.9 pts   power to detect 5 pts = 53%
random N=16: judge - random        d = +24.0 pts   naive 95% CI [+17.3, +30.7]   cluster 95% CI [+16.2, +31.8]   deff 1.35   b/c 53/5   McNemar p = 3.5e-11   clustered p = 1.75e-09
                                   power: MDE(80%) 11.2 pts   power to detect 5 pts = 24%   <- underpowered; a null here is NOT evidence of no effect

tourney N=1: judge - random        d = +0.0 pts   naive 95% CI [+0.0, +0.0]   cluster 95% CI [+0.0, +0.0]   deff nan   b/c 0/0   McNemar p = 1   clustered p = nan
tourney N=2: judge - random        d = +4.0 pts   naive 95% CI [+1.6, +6.4]   cluster 95% CI [+1.6, +6.4]   deff 1.00   b/c 20/4   McNemar p = 0.00154   clustered p = 0.00101
                                   power: MDE(80%) 3.4 pts   power to detect 5 pts = 98%
tourney N=4: judge - random        d = +8.5 pts   naive 95% CI [+5.3, +11.7]   cluster 95% CI [+4.8, +12.2]   deff 1.31   b/c 40/6   McNemar p = 3.1e-07   clustered p = 6.7e-06
                                   power: MDE(80%) 5.3 pts   power to detect 5 pts = 75%
tourney N=8: judge - random        d = +17.0 pts   naive 95% CI [+12.9, +21.1]   cluster 95% CI [+12.5, +21.5]   deff 1.16   b/c 75/7   McNemar p = 1.73e-15   clustered p = 7.28e-14
                                   power: MDE(80%) 6.4 pts   power to detect 5 pts = 60%
tourney N=16: judge - random       d = +17.5 pts   naive 95% CI [+11.2, +23.8]   cluster 95% CI [+10.3, +24.7]   deff 1.28   b/c 41/6   McNemar p = 1.77e-07   clustered p = 1.63e-06
                                   power: MDE(80%) 10.2 pts   power to detect 5 pts = 28%   <- underpowered; a null here is NOT evidence of no effect

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
rank       N=2   ceiling  54.8%   selected  54.2%   gap  0.5 pts   capture  99.1%
rank       N=4   ceiling  64.5%   selected  62.0%   gap  2.5 pts   capture  96.1%
rank       N=8   ceiling  70.5%   selected  66.0%   gap  4.5 pts   capture  93.6%
rank       N=16  ceiling  77.5%   selected  72.0%   gap  5.5 pts   capture  92.9%

random     N=1   ceiling  48.5%   selected  48.5%   gap  0.0 pts   capture 100.0%
random     N=2   ceiling  53.2%   selected  52.5%   gap  0.7 pts   capture  98.6%
random     N=4   ceiling  63.5%   selected  59.2%   gap  4.2 pts   capture  93.3%
random     N=8   ceiling  69.5%   selected  65.0%   gap  4.5 pts   capture  93.5%
random     N=16  ceiling  77.0%   selected  69.0%   gap  8.0 pts   capture  89.6%

tourney    N=1   ceiling  47.8%   selected  47.8%   gap  0.0 pts   capture 100.0%
tourney    N=2   ceiling  56.8%   selected  55.2%   gap  1.5 pts   capture  97.4%
tourney    N=4   ceiling  62.3%   selected  59.0%   gap  3.3 pts   capture  94.8%
tourney    N=8   ceiling  70.8%   selected  66.0%   gap  4.7 pts   capture  93.3%
tourney    N=16  ceiling  76.5%   selected  69.5%   gap  7.0 pts   capture  90.8%

============================================================================================================
4. ARM CONTRASTS, PER N   (the pruning claims)

N=1   rank - random                d = -2.2 pts   naive 95% CI [-4.4, -0.1]   cluster 95% CI [-4.6, +0.1]   deff 1.18   b/c 5/14   McNemar p = 0.0636   clustered p = 0.0573
                                   power: MDE(80%) 3.3 pts   power to detect 5 pts = 99%
                                   non-inferiority (margin 5 pts): lower bound -4.6 -> NON-INFERIOR   one-sided p = 0.0101
                                   tokens 6139 vs 5799  (+5.9%, 95% CI [+3.8%, +7.9%])
N=2   rank - random                d = +1.8 pts   naive 95% CI [-2.0, +5.5]   cluster 95% CI [-2.6, +6.1]   deff 1.30   b/c 33/26   McNemar p = 0.435   clustered p = 0.426
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
                                   non-inferiority (margin 5 pts): lower bound -2.6 -> NON-INFERIOR   one-sided p = 0.00107
                                   tokens 11297 vs 11984  (-5.7%, 95% CI [-9.7%, -1.7%])
N=4   rank - random                d = +2.8 pts   naive 95% CI [-1.1, +6.6]   cluster 95% CI [-1.1, +6.6]   deff 1.02   b/c 36/25   McNemar p = 0.2   clustered p = 0.164
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 72%
                                   non-inferiority (margin 5 pts): lower bound -1.1 -> NON-INFERIOR   one-sided p = 4.36e-05
                                   tokens 22520 vs 24104  (-6.6%, 95% CI [-9.3%, -3.8%])
N=8   rank - random                d = +1.0 pts   naive 95% CI [-2.8, +4.8]   cluster 95% CI [-3.1, +5.1]   deff 1.13   b/c 32/28   McNemar p = 0.699   clustered p = 0.629
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 68%
                                   non-inferiority (margin 5 pts): lower bound -3.1 -> NON-INFERIOR   one-sided p = 0.00187
                                   tokens 44176 vs 48731  (-9.3%, 95% CI [-12.0%, -6.7%])
N=16  rank - random                d = +3.0 pts   naive 95% CI [-2.7, +8.7]   cluster 95% CI [-3.4, +9.4]   deff 1.23   b/c 20/14   McNemar p = 0.392   clustered p = 0.355
                                   power: MDE(80%) 9.1 pts   power to detect 5 pts = 34%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -3.4 -> NON-INFERIOR   one-sided p = 0.00681
                                   tokens 86189 vs 95223  (-9.5%, 95% CI [-12.0%, -7.0%])

N=1   rank - baseline              d = -1.0 pts   naive 95% CI [-4.5, +2.5]   cluster 95% CI [-4.4, +2.4]   deff 0.92   b/c 24/28   McNemar p = 0.678   clustered p = 0.565
                                   power: MDE(80%) 4.9 pts   power to detect 5 pts = 82%
                                   non-inferiority (margin 5 pts): lower bound -4.4 -> NON-INFERIOR   one-sided p = 0.0107
                                   tokens 6139 vs 8238  (-25.5%, 95% CI [-29.6%, -21.4%])
N=2   rank - baseline              d = -2.8 pts   naive 95% CI [-6.6, +1.1]   cluster 95% CI [-6.8, +1.3]   deff 1.11   b/c 25/36   McNemar p = 0.2   clustered p = 0.184
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 68%
                                   non-inferiority (margin 5 pts): lower bound -6.8 -> cannot claim parity   one-sided p = 0.138
                                   tokens 11297 vs 16890  (-33.1%, 95% CI [-35.8%, -30.5%])
N=4   rank - baseline              d = -1.8 pts   naive 95% CI [-5.5, +2.0]   cluster 95% CI [-5.6, +2.1]   deff 1.03   b/c 26/33   McNemar p = 0.435   clustered p = 0.371
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 73%
                                   non-inferiority (margin 5 pts): lower bound -5.6 -> cannot claim parity   one-sided p = 0.0482
                                   tokens 22520 vs 33840  (-33.5%, 95% CI [-35.6%, -31.3%])
N=8   rank - baseline              d = -2.5 pts   naive 95% CI [-6.5, +1.5]   cluster 95% CI [-6.3, +1.3]   deff 0.93   b/c 28/38   McNemar p = 0.268   clustered p = 0.203
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 72%
                                   non-inferiority (margin 5 pts): lower bound -6.3 -> cannot claim parity   one-sided p = 0.101
                                   tokens 44176 vs 67278  (-34.3%, 95% CI [-36.1%, -32.6%])
N=16  rank - baseline              d = +0.0 pts   naive 95% CI [-6.1, +6.1]   cluster 95% CI [-5.9, +5.9]   deff 0.94   b/c 19/19   McNemar p = 1   clustered p = 1
                                   power: MDE(80%) 8.4 pts   power to detect 5 pts = 38%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -5.9 -> cannot claim parity   one-sided p = 0.0486
                                   tokens 86189 vs 133186  (-35.3%, 95% CI [-37.0%, -33.6%])

N=1   tourney - baseline           d = +0.5 pts   naive 95% CI [-3.2, +4.2]   cluster 95% CI [-3.0, +4.0]   deff 0.89   b/c 29/27   McNemar p = 0.894   clustered p = 0.778
                                   power: MDE(80%) 5.0 pts   power to detect 5 pts = 80%
                                   non-inferiority (margin 5 pts): lower bound -3.0 -> NON-INFERIOR   one-sided p = 0.000978
                                   tokens 5861 vs 8238  (-28.8%, 95% CI [-32.8%, -24.9%])
N=2   tourney - baseline           d = -1.8 pts   naive 95% CI [-5.2, +1.7]   cluster 95% CI [-5.1, +1.6]   deff 0.91   b/c 22/29   McNemar p = 0.401   clustered p = 0.307
                                   power: MDE(80%) 4.8 pts   power to detect 5 pts = 83%
                                   non-inferiority (margin 5 pts): lower bound -5.1 -> cannot claim parity   one-sided p = 0.0289
                                   tokens 11044 vs 16890  (-34.6%, 95% CI [-37.0%, -32.2%])
N=4   tourney - baseline           d = -4.8 pts   naive 95% CI [-8.7, -0.8]   cluster 95% CI [-9.1, -0.4]   deff 1.20   b/c 23/42   McNemar p = 0.0248   clustered p = 0.0316
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
                                   non-inferiority (margin 5 pts): lower bound -9.1 -> cannot claim parity   one-sided p = 0.455
                                   tokens 22225 vs 33840  (-34.3%, 95% CI [-36.2%, -32.4%])
N=8   tourney - baseline           d = -2.5 pts   naive 95% CI [-6.8, +1.8]   cluster 95% CI [-6.7, +1.7]   deff 0.96   b/c 33/43   McNemar p = 0.302   clustered p = 0.244
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 64%
                                   non-inferiority (margin 5 pts): lower bound -6.7 -> cannot claim parity   one-sided p = 0.122
                                   tokens 45049 vs 67278  (-33.0%, 95% CI [-34.8%, -31.2%])
N=16  tourney - baseline           d = -2.5 pts   naive 95% CI [-8.8, +3.8]   cluster 95% CI [-8.6, +3.6]   deff 0.94   b/c 18/23   McNemar p = 0.533   clustered p = 0.424
                                   power: MDE(80%) 8.8 pts   power to detect 5 pts = 36%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -8.6 -> cannot claim parity   one-sided p = 0.212
                                   tokens 88802 vs 133186  (-33.3%, 95% CI [-34.9%, -31.7%])

N=1   random - baseline            d = +1.2 pts   naive 95% CI [-2.5, +5.0]   cluster 95% CI [-2.4, +4.9]   deff 0.93   b/c 32/27   McNemar p = 0.603   clustered p = 0.501
                                   power: MDE(80%) 5.2 pts   power to detect 5 pts = 77%
                                   non-inferiority (margin 5 pts): lower bound -2.4 -> NON-INFERIOR   one-sided p = 0.000387
                                   tokens 5799 vs 8238  (-29.6%, 95% CI [-33.4%, -25.8%])
N=2   random - baseline            d = -4.5 pts   naive 95% CI [-8.8, -0.2]   cluster 95% CI [-8.9, -0.1]   deff 1.07   b/c 29/47   McNemar p = 0.0505   clustered p = 0.0463
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 60%
                                   non-inferiority (margin 5 pts): lower bound -8.9 -> cannot claim parity   one-sided p = 0.412
                                   tokens 11984 vs 16890  (-29.0%, 95% CI [-32.2%, -25.9%])
N=4   random - baseline            d = -4.5 pts   naive 95% CI [-8.5, -0.5]   cluster 95% CI [-8.5, -0.5]   deff 0.99   b/c 25/43   McNemar p = 0.0385   clustered p = 0.0284
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 68%
                                   non-inferiority (margin 5 pts): lower bound -8.5 -> cannot claim parity   one-sided p = 0.404
                                   tokens 24104 vs 33840  (-28.8%, 95% CI [-31.2%, -26.4%])
N=8   random - baseline            d = -3.5 pts   naive 95% CI [-7.6, +0.6]   cluster 95% CI [-7.6, +0.6]   deff 0.98   b/c 28/42   McNemar p = 0.12   clustered p = 0.0913
                                   power: MDE(80%) 5.8 pts   power to detect 5 pts = 67%
                                   non-inferiority (margin 5 pts): lower bound -7.6 -> cannot claim parity   one-sided p = 0.235
                                   tokens 48731 vs 67278  (-27.6%, 95% CI [-29.9%, -25.2%])
N=16  random - baseline            d = -3.0 pts   naive 95% CI [-9.2, +3.2]   cluster 95% CI [-9.0, +3.0]   deff 0.94   b/c 17/23   McNemar p = 0.43   clustered p = 0.331
                                   power: MDE(80%) 8.6 pts   power to detect 5 pts = 37%   <- underpowered; a null here is NOT evidence of no effect
                                   non-inferiority (margin 5 pts): lower bound -9.0 -> cannot claim parity   one-sided p = 0.258
                                   tokens 95223 vs 133186  (-28.5%, 95% CI [-30.8%, -26.2%])

============================================================================================================
5. POOLED ACROSS N

   chunk-weighted: every (question, N, chunk) observation counts once, so an N
   with more chunks pulls harder. equal-weight: each N contributes equally.

pooled rank - random (chunk-wtd)   d = +1.1 pts   naive 95% CI [-0.6, +2.7]   cluster 95% CI [-0.7, +2.8]   deff 1.08   b/c 126/107   McNemar p = 0.238   clustered p = 0.233
                                   power: MDE(80%) 2.5 pts   power to detect 5 pts = 100%
                                   equal-weight per N: d = +1.2 pts (from 5 cells: -2.2, +1.8, +2.8, +1.0, +3.0)

pooled rank - baseline (chunk-wtd) d = -1.8 pts   naive 95% CI [-3.6, +0.0]   cluster 95% CI [-4.0, +0.4]   deff 1.47   b/c 122/154   McNemar p = 0.0618   clustered p = 0.114
                                   power: MDE(80%) 3.2 pts   power to detect 5 pts = 99%
                                   equal-weight per N: d = -1.6 pts (from 5 cells: -1.0, -2.8, -1.8, -2.5, +0.0)

pooled tourney - baseline (chunk-wtd) d = -2.2 pts   naive 95% CI [-4.0, -0.3]   cluster 95% CI [-4.6, +0.3]   deff 1.78   b/c 125/164   McNemar p = 0.0252   clustered p = 0.0869
                                   power: MDE(80%) 3.5 pts   power to detect 5 pts = 98%
                                   equal-weight per N: d = -2.2 pts (from 5 cells: +0.5, -1.8, -4.8, -2.5, -2.5)

pooled random - baseline (chunk-wtd) d = -2.8 pts   naive 95% CI [-4.8, -0.9]   cluster 95% CI [-5.5, -0.2]   deff 1.90   b/c 131/182   McNemar p = 0.00463   clustered p = 0.0369
                                   power: MDE(80%) 3.8 pts   power to detect 5 pts = 96%
                                   equal-weight per N: d = -2.8 pts (from 5 cells: +1.2, -4.5, -4.5, -3.5, -3.0)

============================================================================================================
6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)

   Comparing arms at the same N compares unequal compute: a pruned arm at
   N=16 can cost half of baseline N=16. The inference-scaling question is
   'at a fixed budget, which wins?', so each pruned cell is matched to the
   baseline N whose token cost is closest, and paired at the question level.

rank N=1 vs baseline N=1           d = -1.0 pts   95% CI [-4.4, +2.4]   win/loss 16/20   p = 0.565   sign p = 0.618
                                   tokens 6139 vs 8238 (-25.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.4 -> NON-INFERIOR   one-sided p = 0.0107
                                   WARNING: -25% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 4.9 pts   power to detect 5 pts = 82%
rank N=2 vs baseline N=1           d = +7.0 pts   95% CI [+2.3, +11.7]   win/loss 31/11   p = 0.00335   sign p = 0.00289
                                   tokens 11297 vs 8238 (+37.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +2.3 -> NON-INFERIOR   one-sided p = 2.45e-07
                                   WARNING: +37% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
rank N=4 vs baseline N=2           d = +5.0 pts   95% CI [+0.7, +9.3]   win/loss 22/10   p = 0.0242   sign p = 0.0501
                                   tokens 22520 vs 16890 (+33.3% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.7 -> NON-INFERIOR   one-sided p = 3.3e-06
                                   WARNING: +33% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.2 pts   power to detect 5 pts = 62%
rank N=8 vs baseline N=4           d = +2.2 pts   95% CI [-1.4, +5.9]   win/loss 21/13   p = 0.232   sign p = 0.229
                                   tokens 44176 vs 33840 (+30.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.4 -> NON-INFERIOR   one-sided p = 5.92e-05
                                   WARNING: +31% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.3 pts   power to detect 5 pts = 76%
rank N=16 vs baseline N=8          d = +3.5 pts   95% CI [-1.5, +8.5]   win/loss 20/15   p = 0.172   sign p = 0.5
                                   tokens 86189 vs 67278 (+28.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -1.5 -> NON-INFERIOR   one-sided p = 0.000456
                                   WARNING: +28% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 7.2 pts   power to detect 5 pts = 50%   <- underpowered

random N=1 vs baseline N=1         d = +1.2 pts   95% CI [-2.4, +4.9]   win/loss 20/17   p = 0.501   sign p = 0.743
                                   tokens 5799 vs 8238 (-29.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.4 -> NON-INFERIOR   one-sided p = 0.000387
                                   WARNING: -30% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.2 pts   power to detect 5 pts = 77%
random N=2 vs baseline N=1         d = +5.2 pts   95% CI [+0.6, +9.9]   win/loss 28/15   p = 0.0281   sign p = 0.066
                                   tokens 11984 vs 8238 (+45.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +0.6 -> NON-INFERIOR   one-sided p = 9.09e-06
                                   WARNING: +45% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.7 pts   power to detect 5 pts = 55%
random N=4 vs baseline N=2         d = +2.2 pts   95% CI [-2.0, +6.5]   win/loss 22/15   p = 0.305   sign p = 0.324
                                   tokens 24104 vs 16890 (+42.7% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.0 -> NON-INFERIOR   one-sided p = 0.000474
                                   WARNING: +43% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
random N=8 vs baseline N=4         d = +1.2 pts   95% CI [-2.6, +5.1]   win/loss 18/17   p = 0.523   sign p = 1
                                   tokens 48731 vs 33840 (+44.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.6 -> NON-INFERIOR   one-sided p = 0.000708
                                   WARNING: +44% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.5 pts   power to detect 5 pts = 72%
random N=16 vs baseline N=8        d = +0.5 pts   95% CI [-5.0, +6.0]   win/loss 22/15   p = 0.859   sign p = 0.324
                                   tokens 95223 vs 67278 (+41.5% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -5.0 -> cannot claim parity   one-sided p = 0.0256
                                   WARNING: +42% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 7.9 pts   power to detect 5 pts = 43%   <- underpowered

tourney N=1 vs baseline N=1        d = +0.5 pts   95% CI [-3.0, +4.0]   win/loss 19/16   p = 0.778   sign p = 0.736
                                   tokens 5861 vs 8238 (-28.8% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -3.0 -> NON-INFERIOR   one-sided p = 0.000978
                                   WARNING: -29% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 5.0 pts   power to detect 5 pts = 80%
tourney N=2 vs baseline N=1        d = +8.0 pts   95% CI [+3.8, +12.2]   win/loss 28/9   p = 0.000209   sign p = 0.00256
                                   tokens 11044 vs 8238 (+34.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound +3.8 -> NON-INFERIOR   one-sided p = 8.49e-10
                                   WARNING: +34% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.0 pts   power to detect 5 pts = 64%
tourney N=4 vs baseline N=2        d = +2.0 pts   95% CI [-2.3, +6.3]   win/loss 19/12   p = 0.359   sign p = 0.281
                                   tokens 22225 vs 16890 (+31.6% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.3 -> NON-INFERIOR   one-sided p = 0.000665
                                   WARNING: +32% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.1 pts   power to detect 5 pts = 63%
tourney N=8 vs baseline N=4        d = +2.2 pts   95% CI [-2.2, +6.7]   win/loss 21/22   p = 0.317   sign p = 1
                                   tokens 45049 vs 33840 (+33.1% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -2.2 -> NON-INFERIOR   one-sided p = 0.000636
                                   WARNING: +33% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 6.3 pts   power to detect 5 pts = 60%
tourney N=16 vs baseline N=8       d = +1.0 pts   95% CI [-4.3, +6.3]   win/loss 21/15   p = 0.709   sign p = 0.405
                                   tokens 88802 vs 67278 (+32.0% budget mismatch)
                                   non-inferiority (margin 5 pts): lower bound -4.3 -> NON-INFERIOR   one-sided p = 0.0126
                                   WARNING: +32% budget mismatch -- this cell is NOT token-matched; the verdict above is not a matched-budget result
                                   power: MDE(80%) 7.5 pts   power to detect 5 pts = 46%   <- underpowered

============================================================================================================
Clusters are questions. deff > 1 means the naive interval was too narrow.

============================================================================================================
8. CROSS-CONFIG SUMMARY   (the stable estimate: average over the grid)

   A single config is one noisy draw. Quoting the best cell overstates the
   effect because it is the maximum of many noisy cells. These are means.

   arm          N  configs  acc mean    min    max    tokens  vs base
   baseline     1        2     47.2%     47     47     8,238     0.0%
   rank         1        2     46.2%     46     46     6,177   -25.0%
   random       1        2     47.1%     46     48     5,865   -28.8%
   tourney      1        2     47.1%     46     48     5,937   -27.9%

   baseline     2        2     57.0%     57     57    16,890     0.0%
   rank         2        2     53.8%     53     54    11,619   -31.2%
   random       2        2     54.4%     52     56    12,036   -28.7%
   tourney      2        2     55.4%     55     56    11,484   -32.0%

   baseline     4        2     63.7%     64     64    33,840     0.0%
   rank         4        2     61.5%     61     62    23,006   -32.0%
   random       4        2     58.9%     58     59    24,409   -27.9%
   tourney      4        2     60.6%     59     62    22,821   -32.6%

   baseline     8        2     68.5%     68     68    67,278     0.0%
   rank         8        2     65.8%     66     66    45,353   -32.6%
   random       8        2     65.4%     65     66    48,308   -28.2%
   tourney      8        2     66.0%     66     66    45,678   -32.1%

   baseline    16        2     72.0%     72     72   133,186     0.0%
   rank        16        2     70.2%     68     72    88,243   -33.7%
   random      16        2     69.8%     69     70    94,484   -29.1%
   tourney     16        2     67.8%     66     70    90,508   -32.0%

   baseline    32        2     75.0%     75     75   264,452     0.0%

   ORACLE CEILING COLLAPSE   (what pruning costs you before the judge acts)

   Pruning discards candidates, so a correct answer may never reach the judge.
   A smaller judge gap on a pruned arm is less headroom, not better selection.

   arm          N   ceiling  selected  judge gap  ceiling vs base
   baseline     1     47.2%     47.2%       0.0p             0.0p
   rank         1     46.2%     46.2%       0.0p            -1.0p
   random       1     47.1%     47.1%       0.0p            -0.1p
   tourney      1     47.1%     47.1%       0.0p            -0.1p

   baseline     2     59.0%     57.0%       2.0p             0.0p
   rank         2     54.8%     53.8%       1.0p            -4.2p
   random       2     55.5%     54.4%       1.1p            -3.5p
   tourney      2     57.6%     55.4%       2.2p            -1.4p

   baseline     4     66.8%     63.7%       3.0p             0.0p
   rank         4     64.4%     61.5%       2.9p            -2.4p
   random       4     63.4%     58.9%       4.5p            -3.4p
   tourney      4     63.9%     60.6%       3.3p            -2.9p

   baseline     8     75.8%     68.5%       7.2p             0.0p
   rank         8     70.6%     65.8%       4.9p            -5.1p
   random       8     70.4%     65.4%       5.0p            -5.4p
   tourney      8     71.1%     66.0%       5.1p            -4.6p

   baseline    16     80.5%     72.0%       8.5p             0.0p
   rank        16     77.5%     70.2%       7.3p            -3.0p
   random      16     77.8%     69.8%       8.0p            -2.7p
   tourney     16     76.0%     67.8%       8.3p            -4.5p

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
     over 30 equal-N cells:  mean +0.24 pts   median +0.12 pts   positive 16/30   (negative 14)
       plan=1000  mean -0.05 pts   (15 cells)
       plan=2500  mean +0.53 pts   (15 cells)

   STOP-CORRECTED baseline: arm accuracy minus interpolated baseline accuracy
     over 30 equal-N cells:  mean -1.87 pts   median -1.71 pts   positive 3/30   (negative 27)
       plan=1000  mean -2.17 pts   (15 cells)
       plan=2500  mean -1.58 pts   (15 cells)

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
   judge-vs-random        29     29          1     29    29
   non-inferiority        70     46          4     25    43
   pooled                  8      2          0      0     0
   token-matched          30      8          2      3     5

   13 nominally-significant results do NOT survive BH within their family.
   Do not cite these on their own:
     p=0.0155    [arm-contrast] plan=1000,prune=2.0  N=4   random - baseline
     p=0.0215    [token-matched] plan=1000,prune=2.0  tourney N=4 vs baseline N=2
     p=0.0242    [token-matched] plan=2500,prune=2.0  rank N=4 vs baseline N=2
     p=0.0272    [pooled] plan=1000,prune=2.0  pooled rank - baseline (chunk-wtd)
     p=0.0281    [token-matched] plan=2500,prune=2.0  random N=2 vs baseline N=1
     p=0.0284    [arm-contrast] plan=2500,prune=2.0  N=4   random - baseline
     p=0.0316    [arm-contrast] plan=2500,prune=2.0  N=4   tourney - baseline
     p=0.0364    [arm-contrast] plan=1000,prune=2.0  N=16  tourney - baseline
     p=0.0369    [pooled] plan=2500,prune=2.0  pooled random - baseline (chunk-wtd)
     p=0.038     [non-inferiority] plan=1000,prune=2.0  [NI] N=2   random - baseline
     p=0.0463    [arm-contrast] plan=2500,prune=2.0  N=2   random - baseline
     p=0.0482    [non-inferiority] plan=2500,prune=2.0  [NI] N=4   rank - baseline
     p=0.0486    [non-inferiority] plan=2500,prune=2.0  [NI] N=16  rank - baseline

   57 results survive the strict Holm correction; these are the safe ones to quote.
