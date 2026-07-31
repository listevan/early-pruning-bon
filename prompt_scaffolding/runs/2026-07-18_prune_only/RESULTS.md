# Prompt Scaffolding: Pruned Best-of-N for Inference-Time Scaling

**Full report on the work in this directory.** All numbers are reproducible from the raw
per-arm JSONs via `analysis.py` (stdlib-only): `python3 analysis.py . --grid` regenerates
`analysis_results.md` (generated 2026-07-19 over SLURM array `20276744`), from which every
figure here is taken. Section references like §1–§9 point into that file.

---

## Contents

1. [Introduction](#1-introduction)
2. [Method](#2-method)
3. [Results](#3-results)
4. [Analysis](#4-analysis)
5. [Conclusion](#5-conclusion)
6. [Discussion](#6-discussion)
7. [Appendix A: per-config results](#appendix-a-per-config-results)
8. [Appendix B: directory map & reproduction](#appendix-b-directory-map--reproduction)

---

## 1. Introduction

Best-of-N sampling is the simplest inference-time scaling method: sample N independent
solutions, pick one with an LLM judge. Accuracy climbs with N, but token cost climbs
linearly — most of the budget is spent fully generating candidates that were never going
to be selected.

This project asks: **can we recover most of best-of-N's accuracy at a fraction of its
cost by pruning candidates early, before they are fully generated?** Concretely: generate
only a short *prefix* (a partial solution) of each of the N candidates, have the same
model judge the prefixes and discard most of them, complete only the survivors to full
solutions, and run final selection over that smaller pool.

Three questions structure the experiment:

1. **Does LLM-as-judge final selection work at all?** (Is picking with a judge better
   than picking a random candidate from the same pool?)
2. **Do partial-solution prefixes carry rankable signal?** (Does a model-guided prune
   keep more correct candidates than a random prune of the same size?)
3. **Is the whole pipeline compute-positive?** (Does pruned best-of-N beat plain
   best-of-N at equal N, and — the question that actually matters — at equal token
   budget?)

## 2. Method

### 2.1 Task and data

- **Task:** Countdown (via `reasoning_gym`): combine six given numbers with `+ − * /`
  (each number used at most once) to reach a target; the answer is an arithmetic
  expression, graded exact by `reasoning_gym`'s `score_answer`.
- **Instances:** 100 questions, difficulty `level 6` (six numbers), dataset seed 42.
- Answers are extracted from the last `<answer>…</answer>` span of each response
  (`model/utils.py:extract_answer`).

### 2.2 Model and decoding

- **Model:** `Qwen/Qwen3-4B-Instruct-2507` under vLLM, `max_model_len=65536` (the
  ranking prompt concatenates all N prefixes, so context ≈ N × prefix length; at N=16
  this caps usable prefixes at ~4,071 tokens — plan lengths 6500/9000 were dropped as
  infeasible, their N=16 rank prompts would be 100k/133k tokens).
- **Draft sampling:** temperature 1.0, `max_tokens=16384`; baseline drafts top_p=1.0,
  arm drafts top_p=0.95.
- **Judge/ranker sampling:** temperature 0.7, top_p 0.8, top_k 20, fixed seed 42.

### 2.3 Best-of-N design and observations

N ∈ {1, 2, 4, 8, 16}. One max-N=16 generation per question is sliced into
`min(4, 16/N)` disjoint chunks per N, so every N reuses the same base drafts and an
**observation is one (question, N, chunk) triple**:

| N | chunks | obs per cell |
|---|-------:|-------------:|
| 1 | 4 | 400 |
| 2 | 4 | 400 |
| 4 | 4 | 400 |
| 8 | 2 | 200 |
| 16 | 1 | 100 |

### 2.4 Arms and pipeline

**baseline** — plain best-of-N: N full drafts per question (no stop string), then the
LLM judge (`Model.select_solution`) picks one. The judge prompt presents all candidates
in shuffled order (to fight position bias) with stable `iX` ids, demands an
`<evaluation>` + `<results>` block, retries malformed output up to 3×, then falls back
deterministically to the first candidate — never randomly. Alongside the judge pick,
each pool also records a **random pick** (chance control) and the **oracle pick**
(pass@N ceiling: was any candidate correct?).

**Pruned pipeline** (`CompletionStrategy`, `model/strategies.py`) — five stages:

1. **Prefix:** cached drafts longer than `max_plan_tokens` are truncated to exactly
   that length (re-tokenize, cut, decode); drafts already at or under the cap are kept
   whole and billed at their true token count.
2. **Prune** down to `k = max(1, ⌊N / prune_ratio⌋)` survivors, by one of three methods:
   - **rank** — one list-wise LLM call ranks all N prefixes (`ranker.rank`,
     `model/rank.py`); keep the top k. Requires a full permutation of indices; malformed
     rankings retry up to 3×, then missing indices are random-padded at the tail.
   - **random** — keep k uniformly at random (the control that isolates the ranker's
     contribution).
   - **tourney** — tournament pruning (`ranker.tourney_rank`): groups of 4, rank within
     each group, keep the top half (ceiling division), repeat; halving stops before it
     would undershoot k, and a final one-pass trim cuts to exactly k so all three paths
     keep identical survivor counts.
3. **Complete:** each surviving prefix is continued to a full solution
   (`llm.generate` on the raw chat template, `stop=["</answer>"]`).
4. **Select:** the same LLM judge picks the final answer from the completed survivors.
5. A **tournament-style final selection** (`Model.tourney_select_solution`: bracket of
   groups of 4, then a final judge call) is also recorded and charged its own cost.

Survivor counts `k` by cell (`prune_ratio` ∈ {1.5, 2, 3, 4}):

| prune_ratio | N=1 | N=2 | N=4 | N=8 | N=16 |
|------------:|----:|----:|----:|----:|-----:|
| 1.5 | 1 | 1 | 2 | 5 | 10 |
| 2 | 1 | 1 | 2 | 4 | 8 |
| 3 | 1 | 1 | 1 | 2 | 5 |
| 4 | 1 | 1 | 1 | 2 | 4 |

Note that at N ≤ 2 every ratio keeps a single survivor — there the "judge" has nothing
to select among (judge − random ≡ 0 within pruned arms), and any accuracy difference vs
baseline reflects pruning alone.

**Grid:** `max_plan_tokens` ∈ {1000, 2500, 4000} × `prune_ratio` ∈ {1.5, 2, 3, 4} =
**12 configs × 3 pruning arms + one shared baseline** = 37 result files, 180 pruned
(config, arm, N) cells.

### 2.5 Token accounting

Every path is charged for every stage it actually incurs, per question:

- **baseline:** draft tokens (all N drafts, full length — no stop string) + final-judge
  tokens.
- **pruned arms:** prefix tokens (all N prefixes) + pruning-selection tokens (rank: one
  list-wise call; random: 0; tourney: all bracket calls) + completion tokens (survivors
  only) + final-selection tokens. The tournament-select curve is charged its own
  selection cost (`tourney_total_tokens`) instead of the judge's.

**A known accounting asymmetry, measured and corrected in analysis (§9):** baseline
drafts were generated *without* a stop string while arm completions stop at
`</answer>`. Measured with the Qwen3-4B tokenizer over all 6,000 drafts in
`baseline_cache.json`: **26.25%** of baseline generated tokens fall *after* the first
`</answer>` (per-N: 25.76/26.25/26.29/26.29/26.29%; 0 of 6,000 drafts lack the tag).
The arms have no equivalent tail (a prefix truncated at ≥1000 tokens contains zero
post-tag tokens), so correcting the baseline alone is exact. Corrected baseline budget
= 0.7375 × (8,247.1 × N draft tokens) + judge tokens.

### 2.6 Infrastructure

- **Shared baseline cache:** the baseline generation (one monolithic pass, ~115 MB
  `baseline_cache.json`) is produced once; all 12 sweep configs re-truncate and re-prune
  off it (`--cache_fn`). This saves 12 regenerations and keeps the baseline arm
  bit-identical across configs.
- **SLURM array** `20276744` on NCSA Delta (`gpuA40x4` partition), 12 tasks, one
  (plan, prune) config per task on one A40 (`job.slurm`); a config takes ~17–21 h, so
  one-per-task fits the 48 h cap. Sweep ran 2026-07-18 → 2026-07-19.
- **Data parallelism, not tensor parallelism:** each worker is its own TP=1 vLLM
  instance pinned to one GPU (Qwen3-4B is ~8 GB bf16; fits an A40 with KV-cache room).
- **vLLM compile-cache isolation:** independent TP=1 workers all hash to the same
  `rank_0` compile-cache key; concurrent writers produced torn artifacts ("checksum
  does not match"). Fixed by keying `VLLM_CACHE_ROOT` per array task *and* per GPU
  (`run_experiment.sh`).
- **RNG discipline for reruns:** `ONLY_PATHS=tourney` re-runs a single path off the
  cache, but the strategy still *computes* all three prunings so the RNG state feeding
  `tourney_rank` matches a full run — a path-only rerun is bit-for-bit identical to the
  full-run path (`model/model.py`).
- **Environment:** bare `uv`-managed venv (`uv run --no-sync`), `VLLM_LOGGING_LEVEL=ERROR`.

### 2.7 Statistical methodology (`analysis.py`, stdlib-only)

- **Pairing:** every contrast is paired at the observation level (same question, same
  chunk) or, for cross-N comparisons where chunk counts differ, at the question level
  after collapsing to per-question means (`question_contrast`) so pairing never
  silently drops observations.
- **Clustering:** observations from the same question are correlated (a hard instance
  is hard in every chunk and at every N). All primary inference uses cluster-robust
  SEs with clusters = questions and a finite-sample correction; the design effect
  `deff` (reported per contrast, typically 1.0–2.6) quantifies how much the naive
  interval understated uncertainty.
- **Tests:** exact McNemar on discordant pairs, plus a clustered z-test (the McNemar
  treats discordant pairs as independent and is anticonservative whenever deff > 1).
- **Non-inferiority:** one-sided test of H0 "≥ 5 points worse"; a parity claim
  requires the clustered lower CI bound to clear −5 pts. A non-significant two-sided
  test does *not* establish equivalence — at n=100, simulation puts power at ~23% for
  a true 5-point effect.
- **Power:** MDE at 80% power and power-to-detect-5-pts reported per cell from the SE
  (never post-hoc power from the observed effect); underpowered cells are flagged
  inline and their nulls are explicitly *not* evidence of no effect.
- **Token costs carry uncertainty too:** paired per-question token contrasts with
  delta-method CIs on the percentage change.
- **Multiplicity (§7):** every clustered p-value in the grid run is collected with a
  family tag — `arm-contrast`, `judge-vs-random`, `non-inferiority`, `pooled`,
  `token-matched` — and Holm (FWER) and Benjamini–Hochberg (FDR) corrections run
  *within* family (pooling families would let the enormous judge-vs-random effects,
  p ~ 1e-9, eat the alpha the borderline arm contrasts need). Baseline-only tests are
  deduplicated across the 12 configs rather than counted 12 times.
- **Budget-matched views:** §6 matches each pruned cell to the nearest-cost baseline N
  (cells with >15% budget mismatch — 82 of 180, spanning −31% to +49% — get inline
  warnings that they are *not* matched-budget results); §9 removes the slack entirely
  by log-interpolating the baseline accuracy-vs-token curve to each cell's exact
  spend, on both the raw and the stop-corrected baseline. §9 records no p-values (it
  re-describes the same cells as §6; entering it into the correction would
  double-count).
- **Portability:** `--dump-scores` writes a compact 0/1-scores + token-means extract
  (the raw JSONs run to gigabytes and can't be committed), so every number is
  reproducible off-cluster via `--scores`.

### 2.8 Project history (earlier iterations preserved here)

The pipeline above is the end state of several earlier designs, visible in
`model/strategies.py` and `archive/` (Feb–May artifacts):

- **Strategy-prompted planning:** Hypothesis / Plan / Concept / ReasoningStructure /
  Countdown strategies asked the model *not* to solve but to emit a plan inside
  structured `<plan></plan>` tags (enforced with vLLM structured-output regex), ranked
  plans for diversity, then completed from the selected plans.
- **UserStrategy:** a hand-written library of 8 Countdown plans (factor-targeting,
  overshoot-and-adjust, work-backwards, pair-and-combine, …) injected identically for
  every question.
- Early runs used **Qwen3-0.6B** at t=0.9 (`archive/*.txt`, per-N result dumps), before
  moving to Qwen3-4B.
- `main_livecodebench.py` and `main_matharena.py` are entry points for extending the
  same machinery to LiveCodeBench and MathArena.
- `archive/broken_tourney_preFix/`, `bad_selection/`, `pre_plan_fix/`, `failed_run/`
  document superseded runs from before the defect fixes (see §6, "Defects found and
  fixed").

## 3. Results

> **Read this first — two estimands, do not splice them.** §3.3 compares arms at
> **equal N**: that is where the 50–60% raw token reduction lives, and there accuracy
> is significantly *worse*. §3.7–3.8 compare at **matched budget**: that is where
> parity is licensed, but the realized saving is much smaller. Quoting the token number
> from the first and the parity verdict from the second combines two different
> comparisons. Furthermore the raw equal-N token reduction is inflated by the baseline
> stop-tail (§2.5): corrected, it is **38–45%** at N ≥ 2, not 50–60%.

### 3.1 Baseline best-of-N scaling

| N | accuracy | tokens (raw) | tokens (stop-corrected) | oracle ceiling | judge gap | capture |
|---|---------:|-------------:|------------------------:|---------------:|----------:|--------:|
| 1 | 47.5% | 8,417 | 6,253 | 47.5% | 0.0 | 100.0% |
| 2 | 54.5% | 17,179 | 12,849 | 57.0% | 2.5 | 95.6% |
| 4 | 63.0% | 34,192 | 25,532 | 66.2% | 3.2 | 95.1% |
| 8 | 69.5% | 67,682 | 50,363 | 73.5% | 4.0 | 94.6% |
| 16 | 70.0% | 133,659 | 99,021 | 79.0% | 9.0 | 88.6% |

Best-of-N works but the **judge saturates**: +22.0 points from N=1→8, then only +0.5
from N=8→16 even though the ceiling keeps rising (73.5→79.0). At N=16 the judge captures
only 88.6% of achievable accuracy — the judge, not the pool, becomes the bottleneck.

### 3.2 The judge is real: selection beats chance (§2)

Within the same candidate pool, judge-picked minus random-picked (baseline arm;
clustered 95% CIs):

| N | judge − random | cluster 95% CI | clustered p |
|---|---------------:|:--------------:|------------:|
| 2 | +7.2 pts | [+3.9, +10.6] | 2.4e-05 |
| 4 | +14.2 pts | [+9.8, +18.7] | 2.6e-10 |
| 8 | +21.0 pts | [+14.2, +27.8] | 1.9e-09 |
| 16 | +25.0 pts | [+14.8, +35.2] | 1.5e-06 |

The same pattern holds inside every pruned arm's survivor pool wherever there is more
than one survivor (e.g. rank N=16 at plan=1000/prune=2: +25.0 pts, p = 9.2e-09). In §7
this family survives correction almost intact (93 of 94 nominal, 84 after Holm). **This
is the most robust positive finding of the project.**

### 3.3 Pruned arms vs baseline at equal N — cross-config means (§8)

Averaged over all 12 configs (a single config is one noisy draw; quoting the best cell
is a winner's-curse overestimate — the max of ~60 noisy cells):

| N | baseline | rank (min–max) | random (min–max) | tourney (min–max) | rank tokens | vs base |
|---|---------:|:--------------:|:----------------:|:-----------------:|------------:|--------:|
| 1 | 47.5% | 47.8% (46–50) | 46.9% (45–50) | 47.1% (44–51) | 6,135 | −27.1% |
| 2 | 54.5% | 49.2% (46–52) | 46.8% (44–49) | 49.6% (46–52) | 7,967 | −53.6% |
| 4 | 63.0% | 54.9% (46–62) | 51.3% (45–57) | 55.6% (47–61) | 14,132 | −58.7% |
| 8 | 69.5% | 62.7% (55–68) | 59.5% (54–65) | 62.3% (56–68) | 28,569 | −57.8% |
| 16 | 70.0% | 68.2% (64–76) | 65.2% (58–71) | 66.6% (60–72) | 56,949 | −57.4% |

- **At equal N, pruning loses accuracy** — the deficit peaks at N=4 (−8.1 pts for rank)
  and narrows to −1.8 at N=16. The per-config pooled contrasts (§5; Appendix A.2) are
  significant in most configs.
- **N=1 is a clean sanity check:** with one candidate no pruning happens; the arms sit
  within 0.6 pts of baseline (rank +0.3, random −0.6, tourney −0.4) and the −27–29%
  "saving" there is almost exactly the 26.25% stop-tail — confirming the pipeline itself adds ~no cost and the raw equal-N
  savings above are inflated by roughly that amount.
- **Random pruning is consistently the worst arm**, rank the best, tourney in between —
  see §3.5.

### 3.4 Why pruning loses: oracle-ceiling collapse (§3, §8)

Pruning discards candidates before any judge acts, and it discards correct ones:

| N | baseline ceiling (gap) | rank ceiling (gap) | random ceiling (gap) | tourney ceiling (gap) |
|---|:--:|:--:|:--:|:--:|
| 2 | 57.0% (2.5) | 49.2% (0.0) — **−7.7** | 46.8% (0.0) — −10.2 | 49.6% (0.0) — −7.4 |
| 4 | 66.2% (3.2) | 55.5% (0.5) — **−10.8** | 52.3% (1.0) — −14.0 | 56.2% (0.6) — −10.0 |
| 8 | 73.5% (4.0) | 64.7% (2.0) — **−8.8** | 61.5% (2.1) — −12.0 | 64.6% (2.2) — −8.9 |
| 16 | 79.0% (9.0) | 72.7% (4.5) — **−6.3** | 70.4% (5.2) — −8.6 | 71.7% (5.1) — −7.3 |

(gap = ceiling − selected within the arm; bold = ceiling loss vs baseline.)

The judge gap *within* the surviving pool is small (0–5 pts) for every pruned arm; the
accuracy deficit at equal N is almost entirely **ceiling collapse** — for the pruned
arms the "ceiling" is pass@k over survivors, and pruning has already thrown the correct
candidate away in 6–14% of cases. A smaller judge gap on a pruned arm is less headroom,
not better selection. Note rank/tourney ceilings sit 2–4 points above random's at every
N: the ranker keeps correct candidates alive at a measurably higher rate than chance.

These are grid means; single configs vary, and at the mildest-pruning corner the
collapse can vanish entirely — in the plan=2500/prune=1.5 config the rank survivor
ceiling at N=16 is **80.0%, above baseline's 79.0%** (possible because survivors are
completed from truncated prefixes, so their final answers are not a subset of the
baseline's).

### 3.5 Prefix ranking beats random pruning — and the margin has structure (§5)

Pooled (chunk-weighted) rank − random per config, in points:

| prune_ratio | plan=1000 | plan=2500 | plan=4000 |
|------------:|----------:|----------:|----------:|
| 1.5 | −2.1 | +1.5 | **+3.7** |
| 2.0 | +2.0 | +2.8 | **+4.5** |
| 3.0 | +0.8 | +1.5 | **+4.3** |
| 4.0 | +1.6 | +3.7 | **+5.4** |

Two clean gradients: the ranker's edge over random pruning **grows with prefix length**
(more visible reasoning to judge: mean ≈ +0.6 pts at plan=1000 → ≈ +4.5 at plan=4000;
the plan=4000 cells are individually significant, e.g. +5.4 [+3.3, +7.5],
p = 6.2e-07) and tends to grow with **pruning aggressiveness** (the more you discard,
the more the choice of what to keep matters). At plan=1000/prune=1.5 the ranker is
indistinguishable from — even nominally worse than — chance; 1000 tokens of Countdown
arithmetic apparently ranks poorly. Cross-config, rank beats random by +2.4 to +3.6
grid-mean points at N ≥ 2 (§3.3); tourney is statistically comparable to rank.

### 3.6 Pruned vs baseline at equal N, per config (§5)

Pooled (chunk-weighted) rank − baseline per config, in points:

| prune_ratio | plan=1000 | plan=2500 | plan=4000 |
|------------:|----------:|----------:|----------:|
| 1.5 | −6.5 | −2.5 | **−1.1** |
| 2.0 | −4.7 | −2.7 | −2.1 |
| 3.0 | −9.3 | −4.9 | −3.9 |
| 4.0 | −8.8 | −4.1 | −3.5 |

(tourney − baseline follows the same pattern within ~1 pt; random − baseline is 2–5 pts
worse everywhere: −4.0 to −10.4.) The deficit shrinks with longer prefixes and milder
pruning; the best cell, plan=4000/prune=1.5, is a statistically indistinguishable
−1.1 pts [−3.5, +1.4] — but bought with the *least* pruning, i.e. the least savings.
The short-prefix / aggressive-prune corner (plan=1000, prune ∈ {3,4}) is
unambiguously bad: ~−9 pts, p < 1e-7.

### 3.7 Token-matched contrasts — nearest baseline N (§6)

Matching each pruned cell to the baseline N of nearest token cost (e.g. rank N=8 vs
baseline N=4, rank N=16 vs baseline N=8) yields mostly small, non-significant
differences, with a fair number of NON-INFERIOR verdicts at the 5-pt margin (e.g.
plan=4000/prune=4: rank N=4 vs baseline N=2 +0.5 [−3.2, +4.2], NI p = 0.002; rank N=8
vs baseline N=4 +2.5 [−2.2, +7.2], NI p = 0.001; tourney N=4 vs baseline N=2
+4.5 [+0.7, +8.3]). Three caveats keep this from being a clean win:

1. **82 of 180 cells exceed 15% budget mismatch** (span −31% to +49%) and are flagged
   inline as not genuinely token-matched — including every N=1 row.
2. The matched baseline is a *smaller* N, so the realized saving in this comparison is
   the residual mismatch (typically −5 to −15%), not the 50%+ equal-N number.
3. After multiplicity correction (§3.9) the nominally significant token-matched wins
   essentially vanish: 27 nominal → **1 survives Holm**, 6 survive BH — about what 180
   tests produce by chance (9 expected).

Underpowered high-N cells (MDE ≈ 8–12 pts) are flagged throughout; their nulls are not
evidence of parity.

### 3.8 Iso-token contrasts — the cleanest budget comparison (§9)

The baseline accuracy-vs-token curve is log-interpolated to each pruned cell's *exact*
spend (no mismatch left to warn about), on two bases, over all 180 cells:

| basis | mean | median | positive cells | per-plan means |
|---|---:|---:|:--:|:--|
| **RAW baseline** (as billed) | **+0.36 pts** | +0.38 | 99/180 (79 neg, 2 ties) | 1000: −0.31 · 2500: **+1.15** · 4000: +0.25 |
| **STOP-CORRECTED baseline** | **−1.62 pts** | −1.60 | 53/180 (127 neg) | 1000: −2.21 · 2500: **−0.92** · 4000: −1.73 |

Read together: against the raw baseline the pruned arms are roughly **break-even at
equal budget**; against the stop-corrected baseline they are **negative at every plan
length**. The apparent iso-token parity depends on charging the baseline for tokens the
arms never emit. plan=2500 is the least-bad prefix length on both bases.

### 3.9 Multiplicity accounting (§7)

| family | tests | p<.05 | expected by chance | Holm | BH |
|---|---:|---:|---:|---:|---:|
| arm-contrast | 240 | 100 | 12 | 40 | 80 |
| judge-vs-random | 94 | 93 | 5 | 84 | 93 |
| non-inferiority | 420 | 222 | 21 | 68 | 186 |
| pooled | 48 | 36 | 2 | 24 | 35 |
| token-matched | 180 | 27 | 9 | **1** | 6 |

217 results survive strict Holm correction (safe to quote); 78 nominally significant
results fail BH within their family and should not be cited alone — the list is
dominated by exactly the cells one would be tempted to quote (isolated token-matched
wins and single-config arm contrasts). The contrast between families is the story:
judge-vs-random survives correction nearly intact; token-matched wins do not.

### 3.10 Headline cells, properly caveated

- Best single cell: **rank, plan=2500/prune=1.5, N=16: 76.0% at 70,448 tokens** vs
  baseline 70.0% at 133,659 — +6 pts at 53% of the raw cost. It is one config, 100
  observations, the max over ~60 noisy cells, and it does not survive correction. The
  grid-mean N=16 estimate (68.2% at 43% of cost, −1.8 pts) is the honest version.
- Honest equal-N summary: **38–45% fewer tokens (stop-corrected) for ~5–8 points of
  accuracy at N ∈ {2,4,8}**, narrowing to ~2 points at N=16.

## 4. Analysis

**Selection and pruning are different problems, and only one of them works here.** The
final-selection judge adds +7 to +25 points over chance, scaling with pool size, and
survives every statistical control. The pipeline's failure is upstream: pruning on
partial prefixes throws away correct trajectories (6–14 pts of ceiling), and no
downstream judge can recover an answer that no longer exists in its pool.

**Prefix ranking extracts real but insufficient signal.** Rank/tourney keep correct
candidates at a measurably higher rate than random (+2–4 pts of ceiling and accuracy),
and the effect strengthens exactly as theory predicts — with longer prefixes (more
evidence per candidate) and more aggressive pruning (more consequence per decision),
peaking at +5.4 pts (plan=4000/prune=4). But the ranker's edge over chance is smaller
than the ceiling cost of pruning itself at every N except 16, so the pipeline's net
equal-N effect stays negative.

**The economics only look favorable under asymmetric accounting.** Three successive
corrections each shrank the claim: (1) equal-N savings of 50–60% are inflated by the
baseline's post-`</answer>` tail → 38–45%; (2) nearest-N budget matching leaves up to
49% mismatch and its wins die under multiplicity correction (1/180 survives Holm);
(3) exact iso-token interpolation shows +0.36 pts against the as-billed baseline but
−1.62 pts once the baseline is billed fairly. The sign of the headline conclusion
flips with the accounting basis — which is itself the finding: **pruned best-of-N is
approximately equivalent to plain best-of-N run at a smaller N**, minus a small tax.

**The interesting regime is large N, where the judge drowns.** Baseline selection
capture falls from ~95% to 88.6% between N=8 and N=16 while the ceiling keeps climbing
— one judge call over 16 long solutions is past its useful width. There, pre-pruning
costs little (ceiling −6.3) and helps the judge (gap 4.5 vs 9.0; rank captures up to
98.7% of its ceiling in the best cell), leaving rank within ~2 points of baseline at
~43% of raw cost. At small N there is no headroom to prune and the arms simply lose.

**Design choices that made the numbers trustworthy.** Chunked reuse of one N=16
generation gives 400 paired observations per cell at small N; clustering by question
(deff up to 2.6 — naive CIs would be up to ~40% too narrow) prevents the correlated-
question trap; family-wise multiplicity correction over the 982 recorded tests
separates the robust finding (judge-vs-random) from noise (token-matched wins);
power reporting stops nulls at N=16 (MDE ≈ 12–15 pts) from being read as parity; and
the N=1 arms recovering exactly the stop-tail percentage is a built-in end-to-end
sanity check of the token accounting.

## 5. Conclusion

On Countdown (level 6, 100 questions) with Qwen3-4B-Instruct:

1. **LLM-as-judge best-of-N selection robustly beats chance** — +7.2 pts at N=2 rising
   to +25.0 at N=16 (all p < 1e-4, surviving Holm). This component works.
2. **Early pruning of partial solutions is model-guided but not compute-positive.**
   Ranked/tournament pruning beats random pruning by ~3 grid-mean points (up to +5.4
   with long prefixes and aggressive pruning), yet at equal N the pipeline loses
   5–8 points to plain best-of-N at N ∈ {2,4,8} (−1.8 at N=16), and at genuinely
   matched budget it is break-even against a favorably-billed baseline and ~1.6 points
   behind a fairly-billed one.
3. **The loss mechanism is oracle-ceiling collapse:** pruning discards the correct
   candidate before selection in 6–14% of cases — faster than the ranker's signal
   compensates.
4. **Claimed savings depend on accounting:** 38–45% at equal N after stop-tail
   correction (not the raw 50–60%), and ~nothing at matched accuracy.
5. The one regime with genuine promise is **large N**, where the single-call judge
   saturates and pre-pruning nearly pays for itself.

## 6. Discussion

### Limitations and threats to validity

- **Single task, single model, n=100.** Countdown level 6 with Qwen3-4B; nothing here
  establishes transfer. High-N cells have 1–2 chunks (100–200 obs) and are explicitly
  underpowered (MDE ≈ 8–15 pts) — nulls there are not evidence of no effect.
- **The baseline lacked a stop string.** The 26.25% correction is measured and exact
  per §2.5, but a regenerated stopped baseline would remove the issue at the source
  rather than in analysis.
- **Prefixes are truncated baseline drafts,** not natively-generated plans: the
  completion resumes mid-thought from an arbitrary cut. This is what makes the sweep
  cache-reusable and the arms perfectly paired with baseline, but it may understate
  what a purpose-built planning prefix could achieve (the earlier `<plan>`-tag
  strategies in §2.8 were that attempt).
- **Draft sampling differs slightly** (baseline top_p 1.0 vs arms 0.95).
- **Judge cost couples to N × prefix length** (one concatenated list-wise call),
  capping prefixes at ~4k tokens at N=16 — precisely where longer prefixes were
  showing the strongest ranking signal.
- **Selection-failure fallbacks** (first-candidate default after 3 malformed-output
  retries; random padding of incomplete rankings) are deterministic and logged but
  slightly blur what the "judge" measures in the worst case.

### Defects found and fixed during the project (recorded in-repo)

- **Tournament survivor undershoot:** the plain halving loop could skip past the
  target survivor count (8 → 4 with target 5), giving tourney fewer survivors than
  rank/random and corrupting the comparison. Fixed with stop-before-undershoot +
  exact final trim (`model/rank.py:tourney_rank` docstring); pre-fix runs archived in
  `archive/broken_tourney_preFix/`.
- **Per-path token misbilling:** the tournament-select curve was being charged the
  judge's selection cost; it now carries its own (`tourney_total_tokens`,
  `main.py`, `plot_results.py`).
- **vLLM compile-cache race** under data parallelism (torn artifacts, checksum
  failures) — fixed by per-task/per-GPU cache roots (`run_experiment.sh`).
- **Analysis-layer fixes noted in `analysis.py` comments:** the random arm was
  originally never contrasted against baseline (making "all arms" summaries an
  optimistic rank+tourney subset); non-inferiority tests originally escaped
  multiplicity correction (the headline verdicts were the only uncorrected numbers);
  the finite-sample cluster correction was computed but unused; duplicate
  baseline-only tests inflated the correction's m.

### Future directions

- **Attack ceiling collapse directly:** softer pruning (score-weighted sampling rather
  than hard top-k), adaptive prune ratios (`prune_ratio=1` "let the model decide" is
  already plumbed through `main.py`), or pruning only on high ranker confidence.
- **Decouple judge cost from N:** pairwise or small-group tournaments over *short*
  prefixes were meant to be that (and tourney matches rank at equal survivor count);
  cheaper signals — a value head, sequence log-probs, self-consistency of the prefix's
  partial arithmetic — could push pruning earlier than 1000 tokens where a full
  ranking call can't go.
- **Target the large-N regime** where the baseline judge demonstrably saturates:
  hierarchical selection over unpruned pools (tournament-select over all 16) isolates
  the selection improvement from the ceiling cost, and this pipeline already computes
  it.
- **Broader benchmarks and models:** `main_livecodebench.py` / `main_matharena.py`
  entry points exist; harder, longer-horizon tasks may make prefixes more predictive
  (Countdown solutions are search-heavy — an early prefix genuinely may not determine
  success, which would explain the weak signal at plan=1000).
- **Regenerate the baseline with `stop=["</answer>"]`** so no correction is needed.

### Engineering deliverables

Beyond the experimental verdicts, this directory contains reusable infrastructure: a
cached-baseline design that lets a 12-config sweep reuse one generation pass with a
bit-identical shared control arm; a data-parallel SLURM-array sweep runner with vLLM
compile-cache isolation and per-path RNG reproducibility; per-stage token accounting
including separately-billed selection variants; a dependency-free statistical analysis
(clustered inference, non-inferiority, power, Holm/BH, budget matching, iso-token
interpolation) that regenerates every reported number from raw JSONs or a committable
scores extract; and per-config figure generation.

---

## Appendix A: per-config results

### A.1 Accuracy and mean total tokens per cell (§1 of each config block)

Format: `accuracy% tokens`. The baseline row is identical in every config (shared
cache) and shown once.

```
baseline (all configs)   N=1: 47.5% 8417   N=2: 54.5% 17179   N=4: 63.0% 34192   N=8: 69.5% 67682   N=16: 70.0% 133659

plan=1000 prune=1.5      N=1              N=2              N=4              N=8              N=16
  rank                   46.5%  6099t    46.0%  7065t    52.2% 13847t    63.5% 32495t    65.0%  63229t
  random                 46.8%  5858t    48.8%  6705t    56.2% 14011t    62.5% 32907t    71.0%  63967t
  tourney                45.8%  5920t    49.5%  6843t    53.0% 14242t    63.0% 32627t    69.0%  63679t
plan=1000 prune=2.0
  rank                   47.0%  6106t    48.5%  6889t    54.2% 14284t    62.5% 27529t    75.0%  52407t
  random                 45.2%  5889t    47.5%  6927t    52.5% 14310t    59.5% 28314t    69.0%  55328t
  tourney                44.5%  6076t    46.2%  6896t    56.0% 13991t    62.5% 27580t    68.0%  55450t
plan=1000 prune=3.0
  rank                   46.0%  6132t    46.2%  6856t    46.5%  9037t    55.0% 17204t    65.0%  38015t
  random                 45.0%  6129t    44.5%  6967t    46.8%  8758t    53.5% 17896t    66.0%  40614t
  tourney                45.0%  6035t    46.5%  7046t    47.2%  9308t    56.0% 18282t    63.0%  41085t
plan=1000 prune=4.0
  rank                   46.0%  6132t    45.8%  6933t    48.0%  8840t    57.0% 16992t    64.0%  33380t
  random                 45.0%  6039t    45.8%  7128t    45.0%  8854t    56.0% 17700t    58.0%  35916t
  tourney                45.2%  5801t    46.0%  6926t    48.0%  9228t    57.0% 18469t    60.0%  37322t
plan=2500 prune=1.5
  rank                   50.0%  6110t    49.2%  7979t    55.5% 16330t    68.0% 35727t    76.0%  70448t
  random                 50.0%  5921t    46.2%  8212t    56.8% 16750t    64.5% 36447t    68.0%  73759t
  tourney                48.8%  5963t    50.0%  8013t    59.2% 16036t    64.5% 35764t    70.0%  70080t
plan=2500 prune=2.0
  rank                   48.0%  6194t    49.5%  8001t    59.5% 16221t    67.0% 31058t    67.0%  62187t
  random                 47.2%  6031t    46.5%  8162t    56.5% 16660t    62.5% 32762t    61.0%  67224t
  tourney                47.8%  5980t    51.7%  7959t    58.0% 16353t    63.5% 32431t    66.0%  63974t
plan=2500 prune=3.0
  rank                   49.8%  6093t    49.8%  7997t    53.8% 12137t    58.5% 23974t    66.0%  50214t
  random                 50.2%  5815t    47.5%  8032t    50.0% 12472t    58.0% 25334t    66.0%  54652t
  tourney                50.7%  5925t    52.0%  7952t    52.8% 12478t    60.5% 25192t    68.0%  52725t
plan=2500 prune=4.0
  rank                   49.5%  6000t    50.7%  7927t    55.5% 12154t    59.0% 24021t    66.0%  47036t
  random                 49.8%  5864t    46.8%  8137t    47.5% 12531t    56.5% 25399t    62.0%  50887t
  tourney                49.8%  5869t    50.2%  7984t    55.0% 12525t    59.5% 25051t    69.0%  49978t
plan=4000 prune=1.5
  rank                   48.2%  6194t    52.2%  8933t    62.3% 18071t    67.5% 38611t    67.0%  76481t
  random                 45.8%  6011t    48.5%  9019t    55.8% 18661t    65.0% 40211t    67.0%  79499t
  tourney                46.5%  6048t    50.5%  8943t    61.3% 17884t    67.0% 38569t    66.0%  75978t
plan=4000 prune=2.0
  rank                   48.2%  6194t    51.5%  8952t    60.0% 18137t    64.0% 35465t    71.0%  70465t
  random                 45.8%  6010t    45.5%  9178t    53.5% 18947t    62.5% 37241t    66.0%  73139t
  tourney                47.0%  5989t    51.7%  9026t    60.0% 18156t    68.0% 35900t    64.0%  71954t
plan=4000 prune=3.0
  rank                   47.0%  6205t    50.0%  9086t    56.5% 15276t    65.0% 29866t    66.0%  60715t
  random                 47.2%  5980t    47.5%  9353t    48.2% 15666t    54.5% 31665t    64.0%  65839t
  tourney                47.0%  5990t    49.8%  8999t    57.2% 15501t    63.0% 30857t    72.0%  63473t
plan=4000 prune=4.0
  rank                   47.2%  6157t    51.5%  8980t    55.0% 15253t    65.5% 29890t    70.0%  58814t
  random                 45.0%  6017t    47.0%  9200t    46.5% 15701t    58.5% 31796t    64.0%  62939t
  tourney                47.0%  5989t    51.2%  9002t    59.0% 15393t    63.5% 30956t    64.0%  61566t
```

### A.2 Pooled contrasts per config (§5, chunk-weighted, points)

| config | rank−random | rank−baseline | tourney−baseline | random−baseline |
|---|---:|---:|---:|---:|
| 1000/1.5 | −2.1 | −6.5 | −5.4 | −4.4 |
| 1000/2.0 | +2.0 | −4.7 | −5.9 | −6.7 |
| 1000/3.0 | +0.8 | −9.3 | −9.3 | −10.1 |
| 1000/4.0 | +1.6 | −8.8 | −9.2 | −10.4 |
| 2500/1.5 | +1.5 | −2.5 | −2.5 | −4.0 |
| 2500/2.0 | +2.8 | −2.7 | −3.1 | −5.5 |
| 2500/3.0 | +1.5 | −4.9 | −3.9 | −6.4 |
| 2500/4.0 | +3.7 | −4.1 | −4.1 | −7.9 |
| 4000/1.5 | +3.7 | −1.1 | −2.4 | −4.8 |
| 4000/2.0 | +4.5 | −2.1 | −2.3 | −6.6 |
| 4000/3.0 | +4.3 | −3.9 | −3.7 | −8.3 |
| 4000/4.0 | +5.4 | −3.5 | −3.3 | −8.9 |

## Appendix B: directory map & reproduction

### Code

| file | role |
|---|---|
| `main.py` | Experiment driver: args, dataset, arm dispatch, grading loop, JSON export |
| `model/model.py` | vLLM wrapper; baseline drafts; judge (`select_solution`); tournament final select; path orchestration & token tallies |
| `model/strategies.py` | `CompletionStrategy` (current pipeline) + legacy plan-tag strategies |
| `model/rank.py` | `ranker`: list-wise ranking and `tourney_rank` bracket pruning |
| `model/utils.py` | Answer/`</think>` extraction, JSON pretty-printing |
| `run_experiment.sh` | Baseline-then-sweep runner; data-parallel workers; cache isolation; array mode |
| `job.slurm` | 12-task SLURM array (one config per A40, 48 h cap) |
| `analysis.py` | All statistics; `--grid` regenerates `analysis_results.md`; `--dump-scores`/`--scores` for off-cluster reproduction |
| `plot_results.py`, `plot_all_results.sh` | Per-config figure pairs (see below) |
| `grade_output.py` | Early ad-hoc inspection tool (wrong-answer dump, selection-index histogram) |
| `main_livecodebench.py`, `main_matharena.py` | Entry points for other benchmarks |

### Data artifacts

- `baseline_cache.json` (115 MB) — 6,000 raw baseline drafts, reused by every config.
- 36 sweep JSONs + 1 baseline JSON — `<timestamp>_<path>_bon_1_2_4_8_16_strat_<S>_plan_<P>_prune_<R>.json`, ~33–40 MB each (gitignored; full response texts included).
- Two PNGs per sweep JSON: `*_accuracy_grid_comparison.png` (accuracy vs token
  footprint, 6 panels: Selected/Random/Best/Tourney + per-strategy overlays) and
  `*_selection_accuracy_grid.png` (selected/oracle capture ratio vs N).
- `analysis_results.md` — the generated statistics report (§1–§9).
- `sweep_logs/`, `slurm-20276744_*.{out,err}` — run logs.
- `archive/` — superseded runs and pre-fix artifacts.

### Reproduction

```bash
# full pipeline (baseline once, then the 12-config sweep):
sbatch job.slurm                       # or: ./run_experiment.sh on a GPU node
# smoke-test one config:
MAX_PLAN_TOKENS="1000" PRUNE_RATIOS="1.5" NUM_GPUS=1 SKIP_BASELINE=1 ./run_experiment.sh
# regenerate all statistics (this report's numbers):
python3 analysis.py . --grid > analysis_results.md
# portable extract for off-cluster verification (pass --baseline explicitly: the
# baseline filename ends _prune_2.json, not _prune_2.0.json, so the non-grid
# discovery path cannot match it on its own):
python3 analysis.py . --plan 4000 --prune 2.0 \
    --baseline 2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json \
    --dump-scores scores.json
python3 analysis.py --scores scores.json
# figures:
./plot_all_results.sh
```
