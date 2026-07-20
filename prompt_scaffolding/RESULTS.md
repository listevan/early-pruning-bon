# Prompt Scaffolding — Measurements

Numbers recomputed from the raw JSON files. Code claims cite `file:line`.

**Interval methods used below**, stated explicitly because they are mixed:
Wald = `p̂ ± 1.96·√(p̂(1−p̂)/n)`. CP = Clopper-Pearson exact. Boot = bootstrap percentile, 20k resamples.
McNemar = exact binomial on discordant pairs. Cluster-robust = SE with questions as clusters.

> **Status, 2026-07-19.** Three defects that invalidated earlier sweeps have been fixed and the whole grid
> re-run (SLURM array `20276744`, 12 configs × 3 arms, all COMPLETED). The current numbers are **§5.0**;
> everything from §5.1 down is retained as a record of what the earlier, defective runs produced. §7 marks
> which code defects are now fixed. §9 is new: the statistical validity of the analysis itself.
>
> **Headline, stated carefully.** Two findings, in order of how well the data supports them.
>
> **1. Informed pruning beats random pruning** (§5.0.4b): `rank − random` = **+2.4 to +3.7 points** at every
> bon ≥ 2, bootstrap CIs excluding zero, at equal-or-lower token cost — with a built-in placebo at bon=1 that
> correctly returns null. This is the only contrast that varies the pruning rule alone, and it is the cleanest
> result in the sweep.
>
> **2. Pruning trades accuracy for tokens.** At equal N and **bon ≥ 2** (excluding the 36 degenerate bon=1
> cells, where no pruning occurs), the deficit vs baseline is **−6.60 points** for **50–60% fewer tokens**.
> Quoting the all-cell mean (−5.32) alongside a token saving that only exists at bon ≥ 2 splices two sets. It is a real and useful cost/accuracy tradeoff, but it is **not free**, and the
> earlier framing ("comparable accuracy at 45–60% fewer tokens") does not survive scrutiny — see §5.0.5.
> The mechanism is **narrowing, not bad pruning** (§5.0.3): completing `k` candidates instead of `N` costs
> 5–9 points of oracle ceiling, while the pruning *decision* is slightly better than sampling `k` fresh
> (+2.5 to +4.2p for `rank`). The lever is how many candidates survive, not which ones.

---

## 1. Setup

| Item | Value |
|---|---|
| Task | `countdown` from `reasoning_gym`, level 6 (6 numbers, 1 target) |
| Example prompt | `"Calculate 114 using all of these numbers: 18, 32, 36, 4, 29, 95."` |
| Model | `Qwen/Qwen3-4B-Instruct-2507` (vLLM, `max_model_len=65536` since 2026-07-14, was 32768; `Model.__init__`) |
| Hardware | 12-task SLURM array, **1 A40 per task, TP=1** (was TP=4 over A100s; see §7.8) |
| Sampling | generation temperature 1.0, seed 42, `max_tokens=16384`; the ranking and judging stages use their own sampling params (`ranker.rank` (sampling params), `model.py`) |
| Grading | `reasoning_gym` `data.score_answer`, thresholded: `if score != 1: score = 0` |
| Roles | The same model is generator, ranker, and final judge |
| bon values | 1, 2, 4, 8, 16 (stored as top-level keys within one file) |
| Grid | `max_plan_tokens` ∈ {1000, 2500, 4000} × `prune_ratio` ∈ {1.5, 2, 3, 4} = 12 configs |

`max_plan_tokens` 6500 and 9000 were **dropped** from the grid: the rank prompt concatenates every candidate
plan, so it needs ≈ `bon × max_plan_tokens` of context. At bon=16 those settings need 100k and 133k tokens,
past even the raised 65536 limit. The ceiling at bon=16 is ≈4071 tokens per plan (§7.7).

---

## 2. Pipeline

`CompletionStrategy`, five stages:

1. **Draft** — sample `N` full CoT solutions, or load from a cache.
2. **Truncate** — cut each draft to its first `max_plan_tokens` tokens (`CompletionStrategy.generate_prompts` (truncation branch), `tokenizer.encode`/`decode`; guard at (that function) is `if resp["token_count"] <= max_plan_tokens`).
3. **Prune** — keep `int(max(1, N // prune_ratio))` prefixes (`CompletionStrategy.generate_prompts` (`number_choices`)).
4. **Complete** — force-continue each survivor by pre-filling the assistant turn (`Model.generate_responses` (completion stage); the prompt is built at (that function)).
5. **Select** — LLM judge picks one winner (`Model.select_solution`); candidates shuffled ((that function)); 3 retries; fallback to candidate 0 ((that function)).

**Paths** (`main.py` (`paths_to_process`)): `paths_to_process = ["baseline"] if strategy is None else ["rank", "random", "tourney"]`.
One strategy invocation writes three files; one `--baseline` invocation writes one.

| Path | Pruning rule | Pruning LLM calls |
|---|---|---|
| `rank` | LLM ranks all N prefixes, keep top `N // prune_ratio` (`CompletionStrategy.generate_prompts` (PATH 1)) | 1 per chunk, unconditional |
| `random` | Uniform random subset (`CompletionStrategy.generate_prompts` (PATH 2)) | 0 |
| `tourney` | Group into 4s, rank each group, keep top half, repeat — then a final ranking pass trims to **exactly** `target_count` (`ranker.tourney_rank`, fixed 2026-07-17; see §7.6) | 0 when `N == target_count` |
| `baseline` | No truncation, no pruning; full BoN rollout, then judge | 0 |

**Four scored curves per run** (`main.py` (grading loop)):

| Curve | Definition |
|---|---|
| `results` | The judge's pick |
| `random_results` | Random pick among **that file's own survivors** |
| `best_results` | 1 if any candidate was correct (pass@k over survivors) |
| `tourney_results` | The bracket judge's pick |

`random_results` and the `random` **file** are different quantities. At bon=16 the `rank` file's `random_results` is
0.500; the `random` file's `results` is 0.690.

**Survivor counts** — `int(max(1, bon // prune_ratio))`:

| prune | bon=1 | bon=2 | bon=4 | bon=8 | bon=16 |
|---:|---|---|---|---|---|
| 1.5 | 1 | 1 | 2 | 5 | 10 |
| 2.0 | 1 | 1 | 2 | 4 | 8 |
| 3.0 | 1 | 1 | 1 | 2 | 5 |
| 4.0 | 1 | 1 | 1 | 2 | 4 |

Distinct `(bon, survivors)` pairs: `{(1,1),(2,1),(4,1),(4,2),(8,2),(8,4),(8,5),(16,4),(16,5),(16,8),(16,10)}` — **11
distinct configurations** across the 5×4 grid.

### Behavior at bon=1

`number_choices = int(max(1, 1 // 1.5)) = 1`: each path's survivor set is the single drafted candidate.

- The judge runs anyway. `_process_final_selection` is invoked unconditionally (`Model._process_final_selection` call site) and calls
  `select_solution` (`Model._process_final_selection`); there is no `bon == 1` short-circuit. Measured: baseline bon=1 `mean_tokens` =
  8,417.40 vs. a cached-draft mean of 8,247.10 (≈170 judge tokens per problem).
- `rank` calls `ranker.rank(...)` unconditionally (`strategies.py`). `tourney` issues **zero** LLM calls
  (the per-prompt guard `if len(current_active) <= target_count: continue` at `ranker.tourney_rank` (per-prompt guard) skips the prompt, so no
batch is built and the loop breaks). `random` issues none. *(Pre-fix this was the `while any(len(idx_list) >
target_count)` loop condition; that line no longer exists — see §7.6.)*

The three paths are therefore **not** identical in executed code at bon=1. Measured consequences in §5.1.

---

## 3. Filename format

`2026-05-30_07-14-44_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_1.5.json`

Written at `main.py` (output-filename block); the f-string is `main.py` (output-filename f-string). The block sits inside the `for path in paths_to_process`
loop.

| Token | Source |
|---|---|
| timestamp | `strftime('%Y-%m-%d_%H-%M-%S')` at write time |
| `rank` | the path |
| `bon_1_2_4_8_16` | `--best_of_ns` |
| `strat_CompletionStrategy` | `strategy.name`, or `None` |
| `plan_1000` | value of `--max_plan_tokens` as parsed; not forwarded to generation (§7.1) |
| `prune_1.5` | `prune_ratio = max(1, args.prune_ratio)` (`main.py` (`prune_ratio = max(1, ...)`)) — the clamped value |

Pre-May-28 files use `{datetime}` (space + microseconds) and the word `strategy` rather than `strat`, and carry no
path token.

---

## 4. File inventory

Counts as of 2026-07-19, after the §5.0 re-run.

| Path | JSON count | n | Dates |
|---|---|---|---|
| root, `_strat_CompletionStrategy_` (12 configs × rank/random/tourney) | 36 | 100 | July 18–19 |
| root, `_strat_None_` (shared baseline) | 1 | 100 | May 28 |
| root, plots (`*_grid*.png`, 2 per result file) | — | — | 72 files |
| `archive/broken_tourney_preFix/` | 12 | 100 | July 14; superseded by §7.6, retained as record |
| `baseline_cache.json` | 1 | — | Generation cache, 115 MB; contains no score fields |
| `model_select_ranked_selection_countdown/` | 21 | 100 | May 4; ~1.8 GB |
| `model_select_tourney_..._countdown/` | 0 | — | 40 PNGs only; no source JSONs in repo |
| `ranked_selection_results/` | 10 | 30 | April 28 |
| `non_ranked_selection_results/` | 11 | 30 | April 24 |
| `archive/` | 9 | 2–100 | March – early April (3 files dated 2026-04-03) |
| `archive/bad_none_results/` | 12 | 30 | April 7–13 |
| `archive/bad_selection/` | 10 | 30 | April 20 |

`archive/` also contains pre-JSON `.txt` dumps (model: Qwen3-0.6B / Qwen3-1.7B) and SLURM logs.

`ranked_selection_results/` and `non_ranked_selection_results/` both contain
`2026-04-18 04:51:52.952847_bon_1_2_4_8_strategy_None_plan_4000_prune_1.json`, md5
`e4bbb91371e03745da87b3f7a540a106` in both; `cmp` reports zero differences. Distinct inodes.

### `baseline_cache.json`

Written at `main.py` (only under `--baseline`), read at `main.py` via `--cache_fn`.

Shape: `{ "16"|"8"|"4"|"2"|"1" : [chunk][prompt][candidate] → {"text": str, "token_count": int} }`

Chunk counts 1/2/4/4/4 for bon 16/8/4/2/1 (`num_chunks = min(4, max_bon // bon)`, `Model.generate_responses` (chunking)). 6,000 completion
records. `token_count`: mean 8,247.1, min 345, max 16,384; 5,976/6,000 (99.60%) exceed 500 tokens, 5,569/6,000
(92.82%) exceed 1,000, 4,372/6,000 (72.87%) exceed 2,500.

### Schema eras

| Era | Directories | `results[q]` | Score index |
|---|---|---|---|
| March – April | `archive/`, `bad_none_results/`, `bad_selection/`, `ranked_`, `non_ranked_` | `[plan, answer, score]` (3-element) | `[2]` |
| May 4 | `model_select_ranked_selection_countdown/` | `[answer, score]` (2-element) | `[1]` |
| May 28+ | root | `chunks_data.results[c] = {"answer", "score"}` | `["score"]` |

Independent check: `plot_results.py` sums `score[1]`. It raises `TypeError` on all March–April files (`score[1]` is
the answer string) and gets past that line on May-4 files.

**Current (May 28+) schema:**

```
"<bon>": {
  "questions":       [100 x str],
  "dataset_metrics": {average_score, mean_tokens, std_tokens, num_chunks_averaged},
  "prompt_metrics":  [100 x {
      mean_score, mean_tokens, std_tokens,
      chunks_data: {results, random_results, best_results, tourney_results}
        # each = [num_chunks x {"answer": str, "score": 0|1}]
  }]
}
```

`num_chunks_averaged` = 4/4/4/2/1 for bon 1/2/4/8/16.

In `results` and `tourney_results`, `answer` is the extracted expression. In `random_results` and `best_results` it
is the full raw response text (`main.py`).

---

## 5. Measurements

### 5.0 July 2026, n=100 — current, post-fix

SLURM array `20276744`, 12 tasks, all `COMPLETED` (exit 0), 36 result JSONs, zero errors in any task log.
Reuses `baseline_cache.json` (unchanged since 2026-05-28), so the baseline arm is the same reference
throughout. Regenerated by `analysis.py --grid`; full output in `analysis_results.md`.

This is the **first run in which `--max_plan_tokens` actually varies** (§7.1) and the first in which all three
arms prune to the same number of survivors (§7.6). Earlier sweeps are not comparable to it.

#### 5.0.1 Accuracy and cost, averaged over the 12 configs

Per-config numbers at n=100 are single noisy draws; the grid mean is the stable estimate. Quoting the best
cell instead is a maximum-of-60-noisy-cells overestimate — the bon=16 `rank` cells span 64–76%.

| bon | baseline | rank | random | tourney |
|---:|---|---|---|---|
| 1 | 47.5% (8,417t) | 47.8% (6,135t) | 46.9% (5,964t) | 47.1% (5,965t) |
| 2 | 54.5% (17,179t) | 49.2% (7,967t) | 46.8% (8,085t) | 49.6% (7,966t) |
| 4 | 63.0% (34,192t) | 54.9% (14,132t) | 51.3% (14,443t) | 55.6% (14,258t) |
| 8 | 69.5% (67,682t) | 62.7% (28,569t) | 59.5% (29,806t) | 62.3% (29,307t) |
| 16 | **70.0%** (133,659t) | **68.2%** (56,949t) | 65.2% (60,314t) | 66.6% (58,939t) |

Token reduction vs baseline is **53–59%** measured as *cross-config means* at bon ≥ 2; individual cells span
roughly 26–75% and are anticorrelated with accuracy, so this is not a per-cell guarantee. Arm ordering (cross-config means) is `rank > tourney > random` at bon=1, 8 and 16; it is **violated at bon=2
and bon=4**, where tourney edges rank (49.6 vs 49.2, and 55.6 vs 54.9). `random` is last at every bon.

**Do not read the bon=16 row as "−1.8 pts for −57% tokens".** That row averages 12 configs whose individual
95% intervals mostly extend past −10 pts; the means carry no interval of their own, and all 12 share a single
baseline realization, so averaging does not shrink baseline noise. Per config, at equal N and bon=16, only
**2 of 12** `rank` cells have a cluster CI lower bound above −5:

| lower bound of `rank − baseline` at bon=16 | configs |
|---|---|
| above −5 (parity defensible) | 2 |
| −6.6 to −14.7 | 10 |

The honest per-cell summary is §5.0.5.

#### 5.0.2 Token-matched contrasts

Comparing arms at equal `bon` compares unequal compute (rank bon=16 costs 57k, baseline bon=16 costs 134k).
Matching each pruned cell to the baseline `bon` of nearest token cost, paired at the question level:

| | result |
|---|---|
| `rank` bon=16 vs baseline bon=8, best config (plan 2500 / prune 1.5) | **+6.5 pts**, 95% CI [−0.1, +13.1], p = 0.055 |
| `rank` bon=16 rows returning NON-INFERIOR (margin 5 pts) | 6 / 12 — but see below |
| …of which the cell is actually within the 15% budget-matching tolerance | **3 / 12** |
| Token-matched cells (of 180) whose 95% CI is strictly **above** 0 | **21–22**, spanning **7 / 12** configs |
| …at bon=16 specifically | **0** |

Two corrections to earlier drafts of this section:

**Superiority does occur, at low bon.** 21 of the 180 token-matched cells have a CI strictly above zero — e.g.
`plan 4000 / prune 1.5, rank bon=4 vs baseline bon=2`: **+7.8 pts**, CI [+3.5, +12.0], p = 3.2e-04, at 18,071
vs 17,179 tokens (a 5.2% budget gap, comfortably matched). 14–15 of them remain inside the 15% tolerance. (The one-cell ranges reflect boundary cells that flip depending
on whether the printed rounded CI or the full-precision value is used.)
Under within-family BH only 6 of 180 survive, 4 of them positive. What is true is the **narrower** claim: at
**bon=16** no cell shows superiority.

**Half the parity verdicts are not matched-budget results.** Of the 6 `rank` bon=16 NON-INFERIOR rows, 3 carry
`analysis.py`'s own inline warning that the cell is not token-matched — mismatches of −22.6%, **+46.9%** and
**+37.6%**; in the latter two the pruned arm spends 37–47% *more* than the baseline it is being compared to,
which biases toward parity. The defensible count is **3 / 12**.

Note also that the non-inferiority test certifies equivalence only ~19% of the time even when two arms are
*exactly* equal (§9.2), so failures are weak evidence of a real gap.

#### 5.0.3 Oracle ceiling collapse — the binding constraint

`best_results` is 1 if **any** surviving candidate was correct. For pruned arms this is pass@k over survivors,
so it measures what pruning threw away before the judge ever ran.

| bon | baseline ceiling | rank ceiling | Δ | baseline judge gap | rank judge gap |
|---:|---|---|---|---|---|
| 2 | 57.0% | 49.2% | −7.7p | 2.5p | 0.0p |
| 4 | 66.2% | 55.5% | −10.8p | 3.2p | 0.5p |
| 8 | 73.5% | 64.7% | −8.8p | 4.0p | 2.0p |
| 16 | **79.0%** | **72.7%** | **−6.3p** | 9.0p | 4.5p |

**Averaged over the 12 configs** the `rank` ceiling at bon=16 is 72.7% against a baseline 79.0%. These are grid
means, not per-arm bounds — individual configs range 68–78%. Within a single config the ceiling is a hard cap
on that arm.

**But the cause is narrowing, not bad pruning.** The table above compares an arm's pass@k against the
baseline's pass@**N** — different pool sizes, so it charges the arm for carrying fewer candidates. The correct
counterfactual for an arm keeping `k` survivors is baseline pass@**k**. Decomposing (plan 2500):

| arm | bon | k | arm ceiling | baseline pass@k | **decision** | narrowing (pass@k − pass@N) |
|---|---:|---:|---|---|---|---|
| rank | 8 | 4 | 70.5% | 66.2% | **+4.2p** | −7.3p |
| rank | 16 | 8 | 76.0% | 73.5% | **+2.5p** | −5.5p |
| tourney | 4 | 2 | 60.2% | 57.0% | +3.3p | −9.3p |
| random | 8 | 4 | 64.5% | 66.2% | −1.7p | −7.3p |
| random | 16 | 8 | 74.0% | 73.5% | +0.5p | −5.5p |

The `random` arm sits at ≈0 by construction, which calibrates the decomposition. The informed arms are
**above** it: a rank-selected pool of k plans is *better* than k fresh full samples (+2.5 to +4.2p). So the
ranker is not throwing away correct answers — the ceiling loss is the arithmetic consequence of completing
`k` candidates instead of `N`.

Restated: **the limit is how many candidates survive, not which ones.** The lever is `k` (or making pruning
cheap enough to keep more), not a better pruner. The pruned arms' smaller judge gap (4.5p vs 9.0p) is
therefore *less headroom*, not better selection. `random` loses the most ceiling (−8.6p at bon=16), `rank` the
least (−6.3p), which is the mechanism behind the arm ordering in §5.0.1.

So the actionable lever is `k` — how many candidates survive — rather than a better pruner or a better judge.

#### 5.0.4 Judge vs random pick

The most robust result in the sweep (84 of 94 tests in its family survive Holm; §9.4): within an identical candidate pool the judge beats a
random pick by **+7.2 / +14.2 / +21.0 / +25.0 pts** at bon 2/4/8/16 on the baseline arm, with clustered
p of 2.36e-05 / 2.6e-10 / 1.86e-09 / 1.51e-06. Of the 94 tests in this family (after deduplicating the shared
baseline, §9.4) **93 are nominally significant and 84 survive Holm**. Selection works; pruning is what costs
accuracy.

#### 5.0.4b Informed pruning beats random pruning — the cleanest result in the sweep

`rank` vs `random` is the only contrast that holds **everything** fixed — same questions, same cached base
generations, same survivor count `k`, same downstream completion and judge — and varies *only which* candidates
survive. It is therefore the one place the pruning rule is measured in isolation.

Paired per question, pooled over all 12 configs, 20k-resample bootstrap:

| bon | `rank − random` | 95% CI | P(Δ>0) |
|---:|---|---|---|
| 1 | +0.88p | [−0.10, +1.85] | 0.958 ← **placebo** |
| 2 | **+2.42p** | [+1.25, +3.58] | 1.000 |
| 4 | **+3.65p** | [+2.46, +4.88] | 1.000 |
| 8 | **+3.25p** | [+1.71, +4.83] | 1.000 |
| 16 | **+3.00p** | [+0.83, +5.25] | 0.996 |

The bon=1 row is a **built-in placebo**: there `k = N = 1`, so no pruning decision exists and the two arms are
the same procedure. It correctly comes back null (CI straddles zero), which is what licenses reading the
bon ≥ 2 rows as a real effect rather than a pipeline artifact.

The effect is not bought with compute — the informed arm is *cheaper*: at bon=16, `rank` 56,949 tokens vs
`random` 60,314. `tourney − random` is similar (+2.8p pooled).

**This was missing from earlier drafts of this document**, whose only `rank − random` figure was the stale
null (+0.9p, p = 0.544) from the superseded, defective May run (§5.1). A reader would have concluded that
informed pruning is no better than chance. The current data says the opposite, with intervals excluding zero
at every bon ≥ 2.

#### 5.0.5 The two estimands must not be spliced

The claim "comparable accuracy at 45–60% fewer tokens" is not supported, because its two halves come from two
different comparisons that never hold at once. Verified by enumerating **all 180 equal-N arm-vs-baseline cells
(12 configs x 5 bon x 3 arms — rank, tourney AND random)**. Earlier drafts of this section covered only 120
cells because `analysis.py` omitted the `random`-vs-baseline pair entirely; random is the weakest arm, so that
subset was optimistic. The pair has been added and the numbers below are the complete set:

| | equal-N (§5.0.1) | token-matched (§5.0.2) |
|---|---|---|
| Token reduction | **50–60%** | at most ~31% |
| Accuracy | **mean −5.32 pts** (−6.60 for N≥2) | parity licensed in **3/12** well-matched configs (§5.0.2) |
| Cells worse than −4 pts | **98 / 180** | — |

Per arm, the equal-N mean deficit is `rank` **−4.33**, `tourney` **−4.67**, `random` **−6.97** pts (60 cells each).

Losses at equal N are not noise: `plan=1000/prune=1.5, N=4, rank − baseline` is **−10.8 pts**, cluster CI
[−15.2, −6.3], clustered p ≈ 2e-06 (the exact value shifts slightly with the finite-sample correction), and it survives
within-family BH.

Token-matching achieves a smaller saving *by construction* — each pruned cell is matched to a **smaller**
baseline N, so the budget gap it closes is exactly the saving it gives up.

**Cells satisfying both criteria (non-inferiority lower bound > −5 **and** token cut ≥ 45%): 3 of 120.**

| config | bon | arm | d | lower bound | tokens |
|---|---|---|---|---|---|
| plan 1000 / prune 2.0 | 16 | rank | +5.0 | −2.0 | −60.8% |
| plan 2500 / prune 1.5 | 16 | rank | +6.0 | −1.8 | −47.3% |
| plan 4000 / prune 1.5 | 4 | rank | −0.8 | −4.9 | −47.1% |

Two of the three are bon=16, which has a **single chunk** per question (bon ≤ 4 has 4 chunks, bon=8 has 2) —
the least-replicated cells in the grid. The third is knife-edge against the margin. Selecting 3 of 120 is
precisely the winner's curse described in §9.5.

**Defensible statement:** *at equal N, pruning costs ~4.5–5.6 accuracy points and saves 50–60% of tokens.*
Whether that trade is worthwhile is a deployment decision, not a statistical one.

---

### 5.1 May 28–30, n=100

Baseline: `strat_None`. Paths: one `CompletionStrategy` run, `plan_1000`, `prune_1.5`.

Recomputed two ways — from `dataset_metrics.average_score`, and from raw
`prompt_metrics[*].chunks_data.results[*].score` averaged over all prompts and chunks. All 20 accuracy cells agree
to 0.0.

Accuracy (mean tokens per problem):

| bon | baseline | rank | random | tourney | chunks |
|---:|---|---|---|---|---|
| 1  | 0.475 (8,417) | 0.430 (6,220) | 0.435 (6,117) | 0.435 (6,118) | 4 |
| 2  | 0.545 (17,179) | 0.460 (6,625) | 0.450 (6,339) | 0.420 (6,644) | 4 |
| 4  | 0.630 (34,192) | 0.555 (13,070) | 0.5425 (12,927) | 0.565 (12,993) | 4 |
| 8  | 0.695 (67,682) | 0.635 (31,140) | 0.630 (31,410) | 0.625 (26,560) | 2 |
| 16 | 0.700 (133,659) | 0.690 (61,665) | 0.690 (61,272) | 0.680 (52,847) | 1 |

Oracle ceiling (`best_results`) at bon=16: baseline 0.790, rank 0.770, random 0.740, tourney 0.750.

Token change vs baseline at bon=16: rank −53.86%, random −54.16%, tourney −60.46%.

Baseline `results` vs `best_results`: 0.545/0.570, 0.630/0.6625, 0.695/0.735, 0.700/0.790 at bon 2/4/8/16.

**Within-file selection control at bon=16** (`results` − `random_results`):

| file | `results` | `random_results` | difference |
|---|---|---|---|
| baseline | 0.700 | 0.450 | +25.0 pp |
| rank | 0.690 | 0.500 | +19.0 pp |
| random | 0.690 | 0.470 | +22.0 pp |
| tourney | 0.680 | 0.450 | +23.0 pp |

#### bon=1 (survivor set = the single draft on every path)

| pair | identical answers | identical scores |
|---|---|---|
| random vs tourney | 400/400 | 400/400 |
| rank vs random | 65/400 | 310/400 (score-discordant on **90/400 = 22.5%**; b=44, c=46) |

`random` and `tourney` are output-identical on all 400 prompt-chunks; their `mean_tokens` differ on 88/100 prompts
(dataset means 6,116.77 vs 6,118.47).

Candidate texts in the rank and random files share a byte-identical prefix of **≥500 tokens in 385/385** differing
pairs (minimum exactly 500). Divergence point: median token 607, mean 662, max 1367; 11.9% diverge within [495, 520].

`strategies.py` (the ranker call) executes once inside `generate_prompts` (`Model.generate_responses` (strategy call)), **before** the
`for path in ["rank","random","tourney"]` loop (`Model.generate_responses` (per-path loop)). The same call precedes all three paths'
continuations. **No mechanism for the rank/random divergence was established.** The observed pattern
(path 1 ≠ path 2 == path 3) tracks execution order in that loop.

Treating the 22.5% score-discordant items as independent Bernoulli(0.5) disagreements: SE(Δ) = √(0.225/100) = 0.047;
95% interval ±0.093. Per-chunk McNemar SEs: 0.0458, 0.0469, 0.0480, 0.0490 (mean 0.047).

#### Overlap between path files

| bon | pair | identical final answers | identical `best_results` text |
|---|---|---|---|
| 16 | rank vs random | 16/100 | 2/100 |
| 16 | rank vs tourney | 17/100 | 2/100 |
| 16 | random vs tourney | 14/100 | 0/100 |
| 8 | rank vs random | 30/200 | 5/200 |

(Survivor sets are not persisted in the May-28+ schema; `All Answers` (`model.py`) is not written to the results
JSON. The right-hand column measures `best_results` answer-text identity.)

#### Statistics

Pooled over bon ∈ {2,4,8,16}, n = 100 × (4+4+2+1) = 1,100 paired items. The items are **not independent** — they
reuse the same 100 questions — so cluster-robust intervals (clusters = questions) are given alongside the naive ones.

| contrast | Δ | naive 95% CI | **cluster-robust 95% CI** | design effect | McNemar p (naive) | clustered p |
|---|---|---|---|---|---|---|
| rank − baseline | −0.0700 | [−0.096, −0.044] | **[−0.104, −0.037]** | 1.68 | 1.2e-7 | **7.2e-5** |
| random − baseline | −0.0791 | — | **[−0.115, −0.043]** | 1.81 | < 1e-4 | < 1e-3 |
| tourney − baseline | −0.0836 | — | **[−0.117, −0.050]** | 1.73 | < 1e-4 | < 1e-3 |
| rank − random | +0.0091 | [−0.017, +0.036] | [−0.016, +0.034] | 0.87 | 0.544 | 0.544 |

The pooled exact McNemar test assumes the discordant pairs are independent (211 pairs for rank−baseline); there are
100 clusters. It is anticonservative for the baseline contrasts. The rank−random design effect is below 1, so its
p = 0.544 is unaffected.

The chunk counts (4,4,2,1) weight bon=2 four times as heavily as bon=16. The effect is heterogeneous across bon:

| contrast | bon=2 | bon=4 | bon=8 | bon=16 | chunk-weighted pool | equal-weight per bon |
|---|---|---|---|---|---|---|
| rank − baseline | −0.085 | −0.075 | −0.060 | **−0.010** | −0.0700 | **−0.0575** |
| random − baseline | −0.095 | −0.0875 | −0.065 | −0.010 | −0.0791 | −0.0644 |
| tourney − baseline | −0.125 | −0.065 | −0.070 | −0.020 | −0.0836 | −0.0700 |

At bon=16 (the only cell that is a single unaveraged 100-question trial):

| contrast | Δ | McNemar | exact p |
|---|---|---|---|
| rank − baseline | −0.010 | b=9, c=10, 19 discordant | **1.000** |
| rank − random | 0.000 | b=9, c=9, 18 discordant | **1.000** |

rank − random by bon (2/4/8/16): +0.010, +0.0125, +0.005, 0.000. At bon=1: −0.005.
Paired SE at bon=16 = √18/100 = 0.043; 95% CI on Δ = ±0.084.

### 5.2 May 4, n=100, 21 files

#### What executed

`main.py` at commit `3969235` (the May-4-era code) hardcodes
`previous_responses_fn = "2026-05-01 08:31:55.062600_..._strategy_None_plan_4000_prune_2.json"`. May-4-era
`model.py` branches `if previous_responses is None or strategy.name != "CompletionStrategy":` → regenerate;
**else** `model.py` take `previous_responses[bon][j][index]` through unchanged and impute tokens.

Measured, in `2026-05-04 06:11:09.130793_..._plan_1000_prune_1.5.json` at bon=16: **1000/1000 surviving completions
are byte-identical in both `text` and `token_ids`** to the May-4 `strategy_None` file's cached candidates at the same
`indexes` (16 // 1.5 = 10 survivors × 100 questions = 1000). Verified on two further files (prune 2.0/plan 1000;
prune 3.0/plan 9000): identical at every bon (800/800, 400/400, 200/200, 100/100, 100/100).

`baseline_cache.json` is **not** the referent: it shares 3 of 1600 candidate texts with the May-4 data.

**Stages 1, 2, 3 and 5 ran; stage 4 (force-complete) did not.** Truncation executed: 1595/1600 `generated_prompts`
are exact 500-token prefixes of the cached candidates (the 5 misses are encode/decode round-trip artifacts). The
stored `responses[q][k]` are the full cached rollouts, not plan+continuation.

The stored token total equals this closed-form expression exactly:

```
Σ_{all N} min(500, len) + Σ_{survivors} max(len − 500, 0) + rank + judge
    = 799,706 + 7,564,818 + 217,124 = 8,581,648      (= sum(total_tokens) as stored)
```

The 799,706 term matching exactly is an independent confirmation that `max_plan_tokens` was 500 in every "plan"
variant (§7.1).

Accuracy is computed from the cached full-length rollouts (mean 8,247 tokens, §4).

#### Accuracy (mean of the 5 plan values) / total tokens over 100 problems

All 25 cells reproduce from raw JSON.

| prune | bon=1 | bon=2 | bon=4 | bon=8 | bon=16 |
|---:|---|---|---|---|---|
| 1.5 | 0.440 / 0.87M | 0.470 / 0.90M | 0.582 / 1.86M | 0.632 / 4.45M | 0.700 / 8.58M |
| 2.0 | 0.440 / 0.87M | 0.470 / 0.90M | 0.582 / 1.86M | 0.622 / 3.64M | 0.682 / 7.01M |
| 3.0 | 0.440 / 0.87M | 0.470 / 0.90M | 0.502 / 1.04M | 0.558 / 2.03M | 0.650 / 4.70M |
| 4.0 | 0.440 / 0.87M | 0.470 / 0.90M | 0.506 / 1.04M | 0.560 / 2.03M | 0.644 / 3.97M |
| baseline | 0.440 / 0.85M | 0.570 / 1.69M | 0.620 / 3.38M | 0.660 / 6.74M | 0.700 / 13.31M |

Baseline token totals: 847,439 / 1,688,877 / 3,383,567 / 6,736,277 / 13,310,991 (ratios 1.99, 2.00, 1.99, 1.98).
8,581,648 / 13,310,991 = 35.53%.

At bon=4, prune 1.5 and 2.0 are the same configuration (2 survivors). Their mean accuracies are equal (0.5820), but
per-plan accuracies differ ([.58,.58,.59,.58,.58] vs [.58,.58,.58,.59,.58]) and per-plan token totals differ (at
plan=4000: 1,873,540 vs 1,850,696 — a 22,844-token gap); means 1,860,688.6 vs 1,860,612.0. Both round to 1.86M.

At bon=4, prune 3.0 and 4.0 are also the same configuration (1 survivor); stored accuracies 0.502 and 0.506. Same at
bon=8 (2 survivors): 0.558 and 0.560. Accuracy is monotone in prune at bon=16 and not at bon ≤ 8.

At bon=1, the strategy's Final Answers are 100/100 identical to the baseline's; token totals 867,363 vs 847,439.

#### Independent re-scoring of all 16 candidates per question

(`reasoning_gym` 0.1.19 + `model.utils.extract_answer`; questions regenerate identically from seed 42.)

| bon | selected | oracle | mean per-candidate | 1−(1−p)^N | selected == oracle |
|---|---|---|---|---|---|
| 1 | 0.440 | 0.440 | 0.4400 | 0.4400 | 100/100 |
| 2 | 0.570 | 0.570 | 0.4800 | 0.7296 | 100/100 |
| 4 | 0.620 | 0.650 | 0.4825 | 0.9283 | 97/100 |
| 8 | 0.660 | 0.720 | 0.4825 | 0.9949 | 94/100 |
| 16 | 0.700 | 0.790 | 0.4881 | 1.0000 | 91/100 |

selected/oracle ratio: 1.000 / 0.954 / 0.917 / 0.886 at bon 2/4/8/16.

**bon=2 selectors** (keep 1 of 2 by ranker score; `select_solution` not invoked):

| selector | accuracy |
|---|---|
| LLM ranker on 500-token prefixes | 0.470 |
| random | 0.480 |
| judge on full text (baseline) | 0.570 |

#### Statistics

McNemar exact, baseline vs all 20 cells at bon=16: p ∈ [0.238, 1.000]; **0 of 20 have p < 0.05.**

Paired bootstrap (20k resamples over the 100 questions), bon=16:

| contrast | Δ | Boot 95% CI |
|---|---|---|
| prune1.5 − baseline | −0.000 | [−0.062, +0.060] |
| prune2.0 − baseline | −0.018 | [−0.086, +0.050] |
| prune3.0 − baseline | −0.050 | [−0.130, +0.030] |
| prune4.0 − baseline | −0.056 | [−0.136, +0.022] |
| prune2.0 bon16 − baseline bon8 | +0.022 | [−0.044, +0.090] |
| prune1.5 − prune4.0 | +0.056 | [+0.004, +0.112] |

The last row excludes zero (bootstrap two-sided p = 0.034, Wilcoxon p = 0.026). That bootstrap runs on the
per-question **mean over the 5 plan values**. Run per-run instead, on each matched single-run pair:

| plan | Δ @ bon16 | b | c | exact McNemar p |
|---|---|---|---|---|
| 1000 | +0.070 | 9 | 2 | 0.065 |
| 2500 | +0.030 | 7 | 4 | 0.549 |
| 4000 | +0.050 | 6 | 1 | 0.125 |
| 6500 | +0.060 | 8 | 2 | 0.109 |
| 9000 | +0.070 | 9 | 2 | 0.065 |

**0 of 5 have p < 0.05.** prune1.5-vs-prune4.0 is the max-vs-min of a 4-arm family (6 pairwise comparisons). No
multiplicity correction is applied anywhere in this section (20 McNemar tests + 6 bootstrap contrasts).

Absolute 95% CI on 0.700 at n=100: Wald [0.610, 0.790]; **CP exact [0.600, 0.788]**; Wilson [0.604, 0.781].
(The doc's earlier [0.610, 0.784] for prune1.5 was a bootstrap CI on the plan-averaged score, narrower only because
averaging 5 correlated replicates shrinks run-to-run noise.)

Binomial SE at p=0.70, n=100: √(0.7·0.3/100) = 0.0458.

Cells ≥ baseline at bon=16: 3 of 20 (prune=1.5 at plan 1000/6500/9000 = .71/.70/.71). Strictly greater: 2 of 20.

**Spread across the 5 plan values at bon=16** (sd, ddof=1): prune1.5 **0.0100**, prune2.0 0.0084, prune3.0 **0.0000**,
prune4.0 0.0089; mean across rows **0.0068**. At bon=1 and bon=2 the sd is 0.0000 for every prune row.

All 5 plan runs share the same questions, the same 16 cached generations, and seed=42. The shuffles are **seeded**:
May-4-era `main.py` sets `random.seed(42)`, and the ranker/judge `SamplingParams` carry `seed=42`
(`ranker.rank` (sampling params), `model.py`). The residual cross-plan variation is not attributable to shuffle order.

### 5.3 April, n=30

Score at `results[i][2]` (3-element schema). Observed score values: {0, 1.0}. The 30 questions are byte-identical
across all 21 files (single md5 over 84 question-lists).

At bon=8:

| run | acc | tokens | vs baseline |
|---|---|---|---|
| baseline | 22/30 = 0.733 | 1,962,896 | — |
| ranked, plan4000 prune1.5 | 22/30 = 0.733 | 1,316,588 | −32.93% |
| non-ranked, plan4000 prune2.0 | 21/30 = 0.700 | 1,072,260 | −45.37% |

Head-to-head (ranked − non-ranked), 4 matching plan=4000 configs: `+0.000 / −0.050 / +0.017 / −0.033` at bon
1/2/4/8. Over bon ∈ {2,4,8} × 4 configs: ranked < non-ranked in **7** cells, ranked > non-ranked in **3**, equal in
**2**. Sign test on the 10 non-ties: **p = 0.344**.

The ranked `prune_2` (13:12) and `prune_2.0` (13:43) files are the same configuration (`--prune_ratio` is
`type=float, default=2`; `8//2 == 8//2.0 == 4`; `len(indexes)` = 1/1/2/4 in both). Substituting the 13:43 twin gives
`+0.000 / −0.042 / +0.017 / −0.042`; the cell tally is unchanged.

#### Statistics

The compared runs share the same 30 questions **and** the same cached drafts, so they are paired. Paired (McNemar)
SEs, not independent-two-sample SEs:

| comparison | discordant (b, c) | paired SE | exact p |
|---|---|---|---|
| baseline vs ranked-p1.5 | 0 (b=0, c=0) | 0.000 | **degenerate** |
| baseline vs non-ranked-p2.0 | 1 (b=1, c=0) | 0.033 | 1.00 |
| non-ranked vs ranked | 1 (b=0, c=1) | 0.033 | 1.00 |

McNemar with b = c = 0 is a binomial test on zero trials; `scipy.stats.binomtest(0, 0, 0.5)` raises. The first row
has zero power and is not a test result. Baseline and ranked-p1.5 have **bit-identical score vectors on all 30
questions**, while their final answer strings agree on only 12/30.

Single-arm uncertainty at n=30:

| quantity | value |
|---|---|
| Binomial SE at p=0.70 | √(0.7·0.3/30) = 0.0837 |
| Binomial SE at p̂=0.733 | 0.0807 |
| Wald 95% CI on 22/30 | [0.575, 0.892] |
| **CP exact 95% CI on 22/30** | **[0.541, 0.877]** |
| Wilson 95% CI on 22/30 | [0.556, 0.858] |

Replicate sd at bon=8 over the 6 effective replicates (5 plan values + 1 duplicate): ranked **1.72 pp**, non-ranked
**1.36 pp**. With df=5 the 95% CI on those sds is [1.07, 4.22] pp and [0.85, 3.34] pp. The 6 ranked replicates are
all at prune=2 and the 6 non-ranked at prune=1 — different configurations. All 6 ranked values lie in
{0.6333, 0.6667}, i.e. two adjacent multiples of the 1/30 quantization step.

Max-over-configuration accuracy at bon=8: ranked 0.733, non-ranked 0.700 (11 configurations each).

### 5.4 Archive

| Date | Strategy | bon | n | acc |
|---|---|---|---|---|
| 03-06 13:50 | None | 4 | 2 | 1.000 |
| 03-06 14:34 | Countdown | 4 | 2 | 0.000 |
| 03-08 18:39 | Completion | 4 | 2 | 0.500 |
| 03-10 02:43 | Completion | 8 | 100 | 0.320 |
| 03-30 13:01 | None | 8 | 30 | 0.000 |
| 03-30 13:42 | Completion | 8 | 30 | 0.267 |
| 04-03 12:55 | None | 8 | 10 | 0.600 |
| 04-03 14:27 | None | 8 | 10 | 0.900 |
| 04-03 15:08 | Completion | 8 | 10 | 0.900 |

Commit `6f3a549`, dated 03-30, has the message "Fix bad llm answer format for None strategy".

**`CountdownStrategy`, 2026-03-06 14:34 (n=2):** stored scores `[0, 0]`. Re-scored with `reasoning_gym` 0.1.19:

| q | stored answer | arithmetic | score as stored | score with trailing `= N` stripped |
|---|---|---|---|---|
| 0 | `95 - 32 - 18 + 36 + 29 + 4 = 114` | = 114 ✓ | 0.01 → 0 | **1.0** |
| 1 | (expression) `75 * 8 + 22 + 38 + 24 + 8` = 692 ✓, uses each number once | = 692 ✓ | 0.01 → 0 | **1.0** |

Both stored expressions are arithmetically correct and use each number once. Both score 0 as stored because the
answer extractor does not handle the trailing `= N`. Under an extraction fix the run is **2/2**, not 0/2.
Commit `9790b32`, dated 03-08 (two days later), has the message "should be answering with correct format now".

On the same two questions `CompletionStrategy` scores 1/2; its q0 answer (`95 + 29 + 36 - 32 - 18 - 4` = 106) is
arithmetically wrong (target 114).

A 100-example `CountdownStrategy` evaluation exists at
`archive/Qwen_Qwen3-0_6B_n=4_t=0.9_countdown_n=100_CountdownStrategy.txt` (100,560 bytes).

---

## 6. `archive/bad_none_results/` and `archive/bad_selection/`

(Directory names as they exist in the repo.)

### 6.1 `bad_none_results` (April 7–13, n=30)

At commit `89a0dc6`, `main.py` scores the None path as the **maximum over the N candidates** ((that function)
`best_score_for_task = 0`; (that function) `if score > best_score_for_task:`), and the None path has no selector. `89a0dc6`
added 2 of this directory's 12 JSONs; the ten April-13 files were committed later.

Measured None curve: 4/30, 11/30, 14/30, 17/30 = **0.1333 / 0.3667 / 0.4667 / 0.5667** at bon 1/2/4/8.

Relative error of `1−(1−0.133)ⁿ` against the observed curve (convention: |obs − pred| / pred):

| n | observed | 1−(1−0.133)ⁿ | rel. err |
|---|---|---|---|
| 1 | 0.1333 | 0.1333 | 0.0% |
| 2 | 0.3667 | 0.2489 | 47.3% |
| 4 | 0.4667 | 0.4358 | 7.1% |
| 8 | 0.5667 | 0.6817 | 16.9% |

Observed pass@2 = 0.3667 exceeds the union bound 2p = 0.2667. Candidate sets are not nested across bon: 9/30
first-candidates match between bon=1 and bon=2.

Of the 44 Completion cells (11 files × 4 bon) in this directory, **0 exceed the None curve.** In this era the
Completion score is also a maximum — over its surviving candidates — so this compares pass@k(survivors) against
pass@n(all N).

Empty `indexes` counts:

| file | bon=1 | bon=2 | bon=4 | bon=8 |
|---|---|---|---|---|
| `plan_500_prune_1` (17:51) | 29/30 | 27/30 | 25/30 | 23/30 |
| `plan_500_prune_1` (18:12) | 29/30 | 26/30 | 24/30 | 24/30 |
| `plan_1000_prune_1` | 29/30 | 28/30 | 26/30 | 23/30 |
| `plan_500_prune_1.5` | 19/30 | 11/30 | 2/30 | 7/30 |

**Commit attribution:** the diffs of `6f3a549` and `44845f2` (Mar 30–31) contain the string `indexes` **zero times**.
`6f3a549` adds a system prompt and `answer_instruction` to the None-path `llm.chat` call. `44845f2` changes the
`max_plan_tokens` default 500→100 and adds `chat_template_kwargs={"enable_thinking": True}`. The max-over-candidates
scoring is still present at `b724a3c` (Apr 13), `94ee13a` (Apr 21) and `c538171` (Apr 28) — all of which postdate
those commits, as do the files in this directory.

### 6.2 `bad_selection` (April 20, n=30)

Of the 10 JSONs, 6 end in `prune_1.json`. All six show exactly **27/30** empty `indexes` at bon=1; all 27 store
`['', '', 0]`. Upper bound on accuracy is (30−27)/30 = 0.100; observed 0.0667. `main.py` documents
`--prune_ratio` as "at 1, will let model decide"; commit `c538171` (Apr 28) has the message "prune_ratio=1 does not
work properly anymore".

Accuracies across the plan values (the 5 distinct plan settings; a 6th duplicate `plan_4000` run at 15:51 gives
.067/.233/**.233**/.233, disagreeing with the 12:xx `plan_4000` run at bon=4):

| plan | bon=1 | bon=2 | bon=4 | bon=8 |
|---|---|---|---|---|
| 1000 | 0.067 | 0.200 | 0.233 | 0.233 |
| 2500 | 0.067 | 0.233 | 0.233 | 0.233 |
| 4000 | 0.067 | 0.233 | 0.167 | 0.233 |
| 6500 | 0.067 | 0.200 | 0.233 | 0.200 |
| 9000 | 0.067 | 0.233 | 0.333 | 0.233 |

bon=1 is identical across plan values; bon=2/4/8 are not. bon=4 spans 0.167–0.333.

**Surviving-index counts over 30 questions.** The lists do not sum to `keep × 30` because many prompts retain fewer
than `keep` candidates (e.g. at bon=8/keep-5 the `len(indexes)` distribution is {1: 6, 2: 1, 5: 23}):

| config | file | per-index counts | sum | uniform expectation |
|---|---|---|---|---|
| bon=2, keep 1 | prune1.5 | `{0:16, 1:9}` | 25 | 12.5 |
| bon=2, keep 1 | prune2.0 | `{0:21, 1:8}` | 29 | 14.5 |
| bon=2, keep 1 | prune3.0 | `{0:19, 1:10}` | 29 | 14.5 |
| bon=2, keep 1 | prune4.0 | `{0:20, 1:7}` | 27 | 13.5 |
| bon=4, keep 2 | prune1.5 | `[19,10,5,25]` | 59 | 14.75 |
| bon=4, keep 2 | prune2.0 | `[20,8,5,26]` | 59 | 14.75 |
| bon=4, keep 1 | prune3.0 | `[4,3,5,17]` | 29 | 7.25 |
| bon=4, keep 1 | prune4.0 | `[2,3,5,19]` | 29 | 7.25 |
| bon=8, keep 4 | — | `[12,11,15,18,12,13,13,9]` | 103 | 12.875 |
| bon=8, keep 5 | — | `[16,15,19,21,18,11,10,13]` | 123 | 15.375 |

At bon=4/keep-2 the modal surviving set is `{0,3}` (17/30 and 19/30). At bon=4/keep-1, index 0 is kept 2–4 times of
30. At bon=8 the per-index counts span 9–18 and 10–21.

`ranker.rank` (positional-bias shuffle) calls `random.shuffle(shuffled_indices)` under the comment "Create a list of original indices and
shuffle them to combat positional bias".

The "Selection Accuracy" metric plotted in this period was `Completion_score / None_score` — a ratio of two maxima
(§6.1). `plot_results.py` (axis label) now labels it "Ratio Selected / Best".

---

## 7. Code behavior

### 7.1 `--max_plan_tokens` is not passed to generation — **FIXED 2026-07-11**

**Fix:** the value is now forwarded at both dropped hops — `main.py` (`generate_responses` call) into `generate_responses`, and
`Model.generate_responses` (forwarding to the strategy) into `strategy.generate_prompts`. `group_size` was dropped the same way and is also forwarded
(previously harmless only because its argparse default matched the function default). Verified with a stubbed
harness: pre-fix every requested value collapsed to 500; post-fix plans truncate at exactly the requested
length. §5.0 is the first sweep in which this parameter actually varies.

**Original finding, retained:**

`main.py` reads it; `main.py` (output-filename f-string) writes it into the filename; `main.py` calls `generate_responses(...)`
without it. It falls back to `Model.generate_responses` signature's default `500`, which calls `strategy.generate_prompts(...)` also
without it, reaching `strategies.py`'s default `500`.

- Repository has **81 commits**; **79 contain a `main.py`**. The value is passed into `generate_responses` in **0 of
  the 79**. `b724a3c` (Apr 13) and `4e6ed63` (May 4) forward it from `model.py` into `generate_prompts`, but forward
  an un-overridden constant 500.
- `main.py` argparse default is **4000**.
- The only files whose `plan_` label equals the effective value are `bad_none_results/*_plan_500_*` (6 files).
- `MAX_PLAN_TOKENS=(1000 2500 4000 6500 9000)` is set at `run_experiment.sh:5` and passed at (that function).

**Truncation binds.** Full population of 3,100 plan strings in the May-4 `plan_1000/prune_1.5` file, tokenized with
`Qwen/Qwen3-4B-Instruct-2507`:

| metric | value |
|---|---|
| token length, mean | 499.84 |
| token min / max | 386 / 500 |
| exactly 500 tokens | **3,091 / 3,100 = 99.71%** |
| char length, mean | 1,119 |
| chars per token | 2.24 |

April plans (n=400 sampled per directory): mean 499.63; 397/400 = 99.2% exactly 500 tokens.

`generated_prompts` are byte-identical (sha256) across all 5 plan values in every sweep directory: 100/100
`(prune, bon)` groups match.

The downstream `responses` blobs are byte-identical across plan values in **38 of 40** `(prune, bon∈{8,16})` cells.
Two cells drift: prune=2.0/bon=8 (plan 6500 differs from 1000/2500/4000/9000) and prune=3.0/bon=8 (plan 2500 differs
from the rest). Since `generated_prompts` are bit-identical across plan values, plan length cannot be the cause; the
drift is run-to-run nondeterminism.

`--group_size` is likewise not passed (`main.py`, (that function)); its argparse default (4) equals the function default
(`Model.generate_responses` signature).

### 7.2 The `CompletionStrategy.generate_prompts` (ranked-index filter) index filter is a no-op

`CompletionStrategy.generate_prompts` (ranked-index filter) filters ranked indices with `if idx < len(new_prompts[i])`. This filter cannot remove anything:

- `ranker.rank` (index bound) already bounds parsed indices: `unique_ints = [x for x in parsed_ints if ... and x < expected_length]`.
- `ranker.rank` (length check) requires `len(unique_ints) == expected_length` for success — i.e. a full permutation.
- `ranker.rank` (random padding fallback) is a deterministic fallback ("Randomly padding"): any index failing all 3 retries gets
  `final_indexes[i] = valid_ints + missing_ints`, again a full permutation.

So `ranked_indexes[i]` is always a complete permutation of `range(len(new_prompts[i]))`. Measured: across all 20
May-4 `CompletionStrategy` files, **10,000/10,000 stored `ranked_indexes` lists are full permutations** (zero short,
zero empty), and **0/10,000 `generated_diverse_prompts` lists are empty**.

`rank()` is shared by the rank and tourney paths (`ranker.tourney_rank`, `Model` (rank call)); `Model` (tourney fallback) is a second
fallback on the tourney path.

(`main.py` (grading loop, `random.randrange`) calls `random.randrange(len(all_answers))`, which would raise `ValueError` on an empty list. No empty
list is reachable on the `CompletionStrategy` path. The abstract base `Strategy.generate_prompts`
(`strategies.py`) can produce an empty list at `:67-68`, but `main.py` only instantiates
`CompletionStrategy`, which overrides it.)

### 7.3 `plot_results.py` raises an exception on 77 of 77 JSON files — **FIXED 2026-07-11**

**Fix:** two independent breakages. `parse_results` was rewritten against the current schema
(`prompt_metrics[*].chunks_data.*[*].score`, averaged over chunks then summed over prompts), and
`plot_all_results.sh` globbed `*strategy_None*` while `main.py` emits `_strat_None_` — so the glob matched
**zero** files. Both corrected; the parser now reproduces §5.1's published numbers exactly. 72 plots
regenerate cleanly for the §5.0 run.

**Original finding, retained:**

`parse_results()` run against every results JSON in the repo (excluding `.venv` and `baseline_cache.json`):

| exception | count | files |
|---|---|---|
| `TypeError: unsupported operand type(s) for +: 'int' and 'str'` | 52 | `archive/` 9 + `bad_none_results/` 12 + `bad_selection/` 10 + `non_ranked_` 11 + `ranked_` 10 — in this schema `score[1]` is the answer string |
| `KeyError: 'random_results'` | 21 | May 4 |
| `KeyError: 'results'` | 4 | root |
| **completed** | **0** | |

`plot_all_results.sh:4`/(that function) glob `*strategy_None*.json` / `*strategy_CompletionStrategy*.json`; `main.py` (output-filename f-string)
emits `_strat_None_` / `_strat_CompletionStrategy_`.

### 7.4 `tourney_total_tokens` is written and never read — **FIXED 2026-07-17**

**Fix:** `main.py` (grading loop) now unpacks `chunk["tourney_total_tokens"]` alongside `total_tokens` and records a
separate per-question series, surfaced as `tourney_mean_tokens` (`main.py` (`tourney_mean_tokens`)). `plot_results.py` charges the
Tourney curve its own cost, falling back to `mean_tokens` for pre-fix files. The Selected and Tourney curves are now each costed with the tokens they actually spent (the Random and Best
curves still use the shared total, `plot_results.xtok`); the two differ only in the selection component, so the effect on
the x-axis is small but was systematic.

**Original finding, retained:**

Two occurrences in the repo, both writes: `Model.generate_responses` (token tally) and `Model._process_final_selection` (token tally). Zero reads. It is not serialized —
`grep -c tourney_total_tokens` on the 37 MB May-30 rank file returns 0.

`main.py` consumes `chunk["total_tokens"]`. `model.py` adds each path's own `path_selection_tokens` into
that path's `total_tokens`, inside the `for path in [...]` loop (`Model.generate_responses` (per-path loop)). Measured `mean_tokens` at bon=16:
rank 61,664.75, random 61,272.28, tourney 52,847.47.

No token field is emitted for the `tourney_results` curve.

### 7.5 `main_matharena.py` and `main_livecodebench.py`

`python -m py_compile main_matharena.py` → `SyntaxError` at **line 14**
(`dataset_path = "MathArena/hmmt_feb_2025"Example subset, ...`). `main_matharena.py` reads
`bon_outputs["responses"]`; `generate_responses` now returns `organized_outputs[path][bon]["chunks"]`.

`main_livecodebench.py` imports only `re, random, datetime, json, datasets, vllm` — it does not import `model/`. Its
extraction regex at (that function) is `` r'```python ... (.*?)```' `` — the `...` is a literal.

Neither file is imported by `main.py` or invoked by `run_experiment.sh`.

### 7.6 `tourney_rank` kept fewer survivors than the other arms — **FIXED 2026-07-17**

The halving loop pruned every prompt with more than `target_count` candidates by ~half per round, so it could
step **past** the target and stop below it. The `[:target_count]` slice at the end can only truncate, never
restore. Measured by executing the loop over the full grid — exactly three cells diverged:

| cell | rank/random kept | tourney kept |
|---|---|---|
| bon=8, prune=1.5 | 5 | **4** |
| bon=16, prune=1.5 | 10 | **8** |
| bon=16, prune=3.0 | 5 | **4** |

At those cells the tourney arm generated completions and computed accuracy, oracle ceiling and token cost over
a smaller pool than the arms it was being compared against — a silent bias in the three-way comparison, and
tokens under-charged by **2.7% to 13.5%** (measured pre- vs post-fix at the three cells).

**Fix** (`ranker.tourney_rank`): a prompt now stops halving as soon as one more full round *would* cross below
`target_count`; the remainder (then in `(target, 2·target]`) is ranked in one final pass and cut to exactly
`target_count`. Verified across all 20 grid cells: every cell returns exactly `number_choices` survivors, all
indices valid and unique. The worst-case final trim ranks ≤16 candidates — the same load the rank path already
carries. Confirmed empirically after the re-run: every previously-biased cell now costs **+2.8% to +15.5%**
more tokens, the signature of retaining more survivors.

The defect is independent of §7.1 — it depends only on `bon` and `prune_ratio`, so it was present in the
pre-fix runs too. It went unnoticed because the tourney arm's survivor count was never compared against the
other arms'.

### 7.7 The sweep grid exceeded the context window

`ranker.rank` (prompt template) concatenates **every** candidate plan into one ranking prompt, so context ≈ `bon × max_plan_tokens`.
With `max_model_len=32768`, only `max_plan_tokens=1000` fit at bon=16:

Max rank-prompt length at bon=16, rebuilt from `baseline_cache.json` with the `ranker.rank` (prompt template) template, the
truncation at `CompletionStrategy.generate_prompts` (truncation branch), and the model's chat template applied (max over 30 sampled questions):

| `max_plan_tokens` | bon=16 prompt | vs 32768 | vs 65536 |
|---:|---|---|---|
| 1,000 | 16,465 | fits | fits |
| 2,500 | 40,461 | overflow | fits |
| 4,000 | 64,462 | overflow | fits (≈1k headroom) |
| 6,500 | 104,462 | overflow | overflow |
| 9,000 | 143,555 | overflow | overflow |

Every config with `max_plan_tokens ≥ 2500` died at bon=16 with
`ValueError: The decoder prompt (length 38399) is longer than the maximum model length of 32768`.

**This was never runnable.** While §7.1 pinned the value at 500, every ranking prompt was ~8,000 tokens and
always fit; fixing §7.1 is what exposed it. Resolved by raising `max_model_len` to 65536 (`Model.__init__`), which
caps `max_plan_tokens` at ≈4071 for bon=16, and dropping 6500/9000 from the grid.

### 7.8 Concurrent single-GPU workers corrupt the torch compile cache

Under TP=4, vLLM was one process with four ranks, each writing its own
`~/.cache/vllm/torch_compile_cache/<hash>/rank_N_0/`. Switching to data parallelism (one TP=1 process per GPU)
made every worker believe it was `rank_0`, hash to the same key, and write the same artifact files
concurrently. The interleaved writes produced torn bytes and the next run died at engine start with
`RuntimeError: Bytes object is corrupted, checksum does not match`, in all 20 configs within seconds.

Diagnostic signature: the *producing* run appears healthy for hours (it compiles in memory and corrupts on the
way out); the *next* run fails instantly.

**Fix:** each worker gets its own `VLLM_CACHE_ROOT`, keyed by GPU **and** `SLURM_ARRAY_TASK_ID` (two array
tasks can land on one node). `run_experiment.sh` sets it per worker.

---

## 8. Verification record

Every table above was recomputed from the raw JSON files by an independent pass instructed to refute rather than
confirm. Items that pass verification:

| Area | Result |
|---|---|
| §5.1, 20 accuracy cells | Reconcile two ways to 0.0 |
| §5.1 oracle ceilings, token reductions, within-file controls | Exact |
| §5.2, all 25 cells; 1000/1000 byte-identity; token imputation to the unit | Exact |
| §5.2 independent re-scoring with `reasoning_gym` | Reproduces all stored scores |
| §5.3, all figures; discordant counts 0/1/1 | Exact |
| §5.4 CountdownStrategy re-score under live `reasoning_gym` | Confirmed (both questions) |
| §6.1 max-over-candidates at `89a0dc6:main.py:85-114` | Confirmed |
| §6.2, all 20 plan-sweep cells; all index histograms | Exact |
| §7.1, 0 of 79 commits pass the value; tokenizer measurements | Confirmed |
| §7.3, 77/77 | Confirmed (52 TypeError, 21+4 KeyError) |
| §7.4, `tourney_total_tokens` 0 reads; three distinct `mean_tokens` | Confirmed |
| §2, all 10 pipeline line citations; survivor table; 11 distinct configs | Exact |
| §4, all 9 directory counts; md5; 6 `baseline_cache` statistics | Exact |
| §5.0, 12/12 tasks COMPLETED, 36 JSONs, 0 errors in any task log | Confirmed |
| §5.0 tourney token increase at the 3 previously-biased cells | Confirmed (+2.8% to +15.5%) |
| §7.6 survivor counts, all 20 grid cells post-fix | Exact (`target_count` everywhere) |
| §7.7 context arithmetic against the live tokenizer | **Corrected 2026-07-19** — the first pass omitted the chat template and understated the two largest rows by 4–8%; table now rebuilt |
| §9.2 test calibration against synthetic known-truth data | Confirmed (see table) |
| §5.0/§7/§9 re-verified by an independent adversarial pass, 2026-07-19 | 23 errors found and corrected; see §9.8 |

---

## 9. Validity of the analysis itself

`analysis.py` regenerates every number in §5.0. This section records whether its **tests** are sound, which is
a separate question from whether the pipeline is.

### 9.1 Design and tests

All arms share the same 100 questions and the same cached base generations, so contrasts are **paired** —
exact McNemar on discordant pairs, plus a cluster-robust SE with **questions as clusters** (a hard Countdown
instance is hard in every chunk and at every bon). The effective sample size is ~100 questions, not the ~400
(question, chunk) observations; `deff` is reported so the inflation is visible.

Cross-bon comparisons (§5.0.2) cannot use `(question, chunk)` keys because different bon have different chunk
counts and `paired_contrast` would silently drop observations. Those collapse to a per-question mean first.

### 9.2 Calibration against known ground truth

The tests were run on synthetic data where the true answer is known. A test that does not reject at ~α under
the null, or cannot detect a real effect, is decoration.

| check | result | verdict |
|---|---|---|
| Null, independent questions | clustered rejects 5.35% | ~5%, correct |
| Null, heterogeneous questions | clustered rejects 5.95% | ~5%, correct |
| Null, arms correlated within question | clustered **4.95%** (McNemar 2.55%) | clustering works |
| Holm / BH on 500 pure-null tests | 0 survive each | correct |
| Non-inferiority at the margin boundary | fires 2.4% | correct (2.5% expected) |
| Non-inferiority when truly 15 pts worse | fires **0%** | will not certify a real regression |
| Non-inferiority when arms are truly **equal** | fires only **19.4%** | valid but low power |

**The machinery is sound.** McNemar is mildly conservative, the clustered test is near-exact, and the
corrections behave.

### 9.3 The study is underpowered — the main caveat on every null result

| true effect | detected |
|---|---|
| +5 pts | **23%** |
| +10 pts | **~70%** |
| +20 pts | 99.6% |

Power collapses as bon rises. The table below is computed over the **arm-contrast family** (every
`rank`/`tourney`/`random` vs baseline equal-N contrast — 36 cells per bon), which is the family the headline
pruning claims live in. Ranges, not point values, because power varies across configs:

| bon | power to detect 5 pts | MDE (80%) | cells |
|---:|---|---|---|
| 1 | 54–90% | 4.3–6.8p | 36 |
| 2 | 54–87% | 4.6–6.8p | 36 |
| 4 | 40–82% | 4.9–8.2p | 36 |
| 8 | 33–72% | 5.5–9.2p | 36 |
| 16 | **18–29%** | **10.1–13.4p** | 36 |

(An earlier draft printed a single column here — 83/60/30/16% and MDE 4.8/6.3/9.8/14.6p. Those figures are the
*baseline judge-vs-random* contrast only, not the pruning contrasts, and stating them as the study's per-bon
power overstated the caveat. The token-matched family is more favourable still: MDE 6.7–11.2p at bon=16.)

Two consequences, both now printed inline by `analysis.py`:

1. A non-significant result at bon=16 is a **power failure, not evidence of no difference**. In the
   arm-contrast family nothing smaller than ~10–13 points was reliably detectable there (80% power).
2. Any effect that *is* detected at such power is likely **exaggerated** (Type M error). The +6.5 pts in
   §5.0.2 should be read as an upper-ish estimate, not a point estimate.

More questions would buy more than more grid cells.

### 9.4 Multiple comparisons, corrected within families

The grid produces 850 tests. Correcting them as one family is wrong — the enormous judge-vs-random effects
inflate `m` and consume the α the borderline arm contrasts need. Corrected **within** family:

| family | tests | p<.05 | expected by chance | Holm | BH |
|---|---:|---:|---:|---:|---:|
| judge-vs-random | 94 | 93 | 5 | **84** | 93 |
| arm-contrast | 180 | 65 | 9 | 23 | 44 |
| **non-inferiority** | **360** | **214** | 18 | **67** | 183 |
| pooled | 36 | 24 | 2 | 14 | 23 |
| token-matched | 180 | 27 | 9 | **1** | 6 |

The judge-vs-random result (§5.0.4) is overwhelming and survives everything. The token-matched family is the
opposite: **1 of 180 survives Holm**. 74 nominally-significant results do not survive within-family BH and are
listed in `analysis_results.md`; they must not be cited individually.

Two corrections were applied to this table after an adversarial review (§9.7):

- The **360 non-inferiority tests were previously omitted from the correction entirely** — they were computed,
  printed, and never recorded. Since the NI verdicts are exactly what a reader quotes, the only uncorrected
  numbers in the report were the load-bearing ones. Of the 183 `NON-INFERIOR` verdicts, only **67 survive
  Holm**; the three cells in §5.0.5 have one-sided NI p of roughly 0.003 / 0.003 / 0.02, and Holm over 360 tests
  requires p ≤ 1.4e-04, so **none of the three clears strict correction**.
- The baseline arm is shared by all 12 configs, so baseline-only tests were byte-identical duplicates counted
  12 times (judge-vs-random fell from 138 to 94 once deduplicated).

### 9.5 Selection on the grid maximum

Holm/BH correct individual tests; they do **not** correct for choosing the best of ~60 (config × bon) cells.
The bon=16 `rank` cells span 64–76%, so the 76% maximum is an upward-biased estimate of what a re-run would
produce. §5.0.1 therefore reports grid means, not the best cell.

### 9.6 Known limitations, not yet addressed

- Token-matched cells report a **budget mismatch** spanning −31.1% to +48.9%; 82 of 180 exceed 15% and are
  flagged inline as not matched-budget results. Interpolating the baseline's accuracy-vs-token curve would be tighter than snapping to the nearest bon.
- `random_results` stores **one** random draw per (question, chunk) — an unbiased but high-variance estimator of
  expected random-pick accuracy. The exact pool average is not recoverable from the saved JSON; `main.py` would
  need to store the full candidate score vector.
- The same baseline arm is reused in all 12 config comparisons, which induces dependence across those contrasts
  (deduplicated in the correction, but the 12 config-level deltas remain positively correlated).
- **Only the bon=1 cells are unpruned** (4 of 20 (bon, prune) combinations): `number_choices == bon` holds
  nowhere else. At bon=2 exactly half the candidates are discarded (2→1) at every prune ratio, and at bon=4 with
  prune ≥ 3 three quarters are (4→1) — see the survivor table in §2. What *is* true is that survivor counts vary
  sharply across the grid, and the bon=1 cells are degenerate: `k = N = 1`, so no pruning decision exists. (The arms are not bit-identical
  there — sampling still differs, giving ~11.6% discordance — which is exactly what makes bon=1 a usable
  noise floor and placebo, see §5.0.4b.) Those cells should be excluded before averaging over the grid.
- Non-inferiority is the wrong frame for `rank − random`: it is an **equal-cost** contrast, so the interesting
  question is superiority, which §5.0.4b now tests directly (and finds).
- **The "partial plan" premise is violated at large `max_plan_tokens`.** A draft shorter than the cut is passed
  through whole, so it is a finished solution, not a plan: **7.2% / 26.9% / 38.3%** of drafts are never
  truncated at plan = 1000 / 2500 / 4000. The plan=4000 arm is therefore closer to "best-of-k full solutions"
  than to plan-then-complete, which partly explains why it scores best.
- **The token metric is decode-only.** `total_tokens` sums generated tokens; it omits prefill. The pruned arms
  re-prefill each survivor's plan before completing it, and that term is not counted — so the true cost
  advantage is smaller than the reported 50–60%, by an amount this data cannot quantify.
- The judge sees only the extracted `<answer>` expression, not the reasoning, so §5.0.4's "selection works"
  is a statement about verifying arithmetic, not about assessing reasoning quality.

### 9.7 Adversarial review of `analysis.py` (2026-07-19)

51 agents, 45 raw findings, 21 confirmed after independent verification. The statistics were found sound —
cluster-robust SEs, explicit non-inferiority rather than treating non-significance as equivalence, within-family
correction, power/MDE lines. The confirmed defects were in **reporting and bookkeeping**, and the two critical
ones are fixed above:

| finding | status |
|---|---|
| Headline splices the §4 token number with the §6 parity verdict (§5.0.5) | **Fixed** — headline restated; §5.0.5 added |
| 360 non-inferiority tests never entered the multiplicity correction | **Fixed** — recorded as their own family |
| `token_contrast` percentage CI divided difference bounds by the denominator mean, which is not a ratio interval | **Fixed** — delta method with paired covariance |
| `se_cluster_fc` computed but never used, so clustered CIs were fractionally narrow | **Fixed** — now applied |
| Shared baseline injected duplicate p-values into the correction | **Fixed** — recorded once |
| §6 cells with large budget mismatch presented as "token-matched" (up to +48.9%; 82/180 exceed 15%) | **Partly fixed** — cells >15% now flagged inline; nearest-N matching not yet replaced by interpolation |
| "N results survive Holm — the safe ones to quote" is misleading; most are the judge-vs-random sanity check | Open |
| `discover()` cannot match the baseline in non-grid mode (baseline `prune_2` vs strategy `prune_2.0`) | Open — pass `--baseline` explicitly |

### 9.8 Adversarial verification of this document (2026-07-19)

27 agents re-derived every factual claim in §1, §2, §5.0, §7 and §9 from the raw JSONs and the current code
rather than from the document. **24 alleged errors, 23 confirmed.** All are corrected above. The material ones:

| § | was | is |
|---|---|---|
| 5.0.2 | "0/12 configs superior; no cell demonstrates superiority" | **21 of 180 cells across 7 configs** have a CI above 0; the claim holds only at bon=16 |
| 5.0.2 | "6/12 non-inferior at matched budget" | 3 of those 6 are **not** token-matched (up to +46.9% mismatch); defensible count **3/12** |
| 5.0.4 | "137 of 138 significant, 128 survive Holm" | **93 of 94, 84 survive Holm** (stale pre-deduplication figures) |
| 7.7 | context table 100,082 / 132,533 at bon=16 | **104,462 / 143,555** (first pass omitted the chat template) |
| 9.4 | "the grid produces 534 tests" | **850** — the row totals printed directly beneath it |
| 5.0.1 | "ordering consistent at every bon ≥ 4" | violated at bon=4 (tourney 55.6 > rank 54.9) |
| 7.6 | "~20% under-charged tokens" | **2.7–13.5%** |
| 7.4 | "every curve is now costed with the tokens it spent" | only Selected and Tourney; Random and Best still share the total |

The remainder were stale p-values (pre finite-sample-correction), wrong `file:line` citations in §2 — including
one quoting a loop condition that the §7.6 fix deleted — a wrong cross-reference, and a date error.

### 9.9 Independent blind verification (2026-07-19)

The two passes above shared a flaw: they were given this document's claims and asked to check them, which grades
arithmetic but cannot catch a wrong *choice* of what to report. This pass removed the anchor. Three analysts
received only the raw JSONs, the code and a description of the experiment, and were instructed **not** to open
this file or `analysis_results.md`; they derived their own conclusions. Two further agents then diffed those
derivations against this document.

**Arithmetic: clean.** Both diff agents independently reproduced every table — the §5.0.1 accuracy/token grid to
the token, the per-arm deficits (−4.33 / −4.67 / −6.97), the §5.0.3 ceilings, the §5.0.4 judge gaps, the
§5.0.5 three-cell table, the bon=16 spread. No numeric error was found.

**Framing: two substantive corrections**, both now applied above, and both in the direction of having been *too
harsh* on the method:

| | was | is |
|---|---|---|
| `rank − random` | absent; the only figure was a stale null from the superseded May run | **§5.0.4b** — +2.4 to +3.7p at every bon ≥ 2, CIs excluding zero, with a passing placebo at bon=1 |
| ceiling loss | "pruning destroys correct candidates… the approach is limited by what pruning destroys" | **narrowing**, not damage: the decision is +2.5 to +4.2p *better* than sampling `k` fresh (§5.0.3) |

Plus: the headline was diluted by the 36 degenerate bon=1 cells; "53–59%" was a range of config means over
per-cell values spanning ~26–75%; and three measurement caveats were unrecorded (untruncated drafts,
decode-only tokens, what the judge actually sees) — all now in §9.6.

**Process note.** Three passes, three different failure modes. Passes 1–2 found ~49 numeric and citation errors,
each time in a document already declared finished; both shared one shape — a true statement about a narrow slice
restated as general. Pass 3 found the arithmetic clean but the *conclusions* mis-framed, including one omitted
result that reversed a headline. The lesson is that checking a document against its own claims cannot find what
the document failed to ask; only an independent derivation can. Numbers here should be treated as provisional
until re-derived from the JSONs by code that does not read this file.
