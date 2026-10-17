# Prompt Scaffolding — Measurements

> Audit of the March to May 2026 runs, most of which ran before the July pipeline fixes.
> For current results see [`runs/2026-07-18_prune_only/RESULTS.md`](../runs/2026-07-18_prune_only/RESULTS.md).
> Paths below are relative to `prompt_scaffolding/`, and code citations point at the code as it
> was in May. The four April/May result folders listed in §4 (`ranked_selection_results/`,
> `non_ranked_selection_results/`, `model_select_*`) now live in `archive/`.

Numbers recomputed from the raw JSON files. Code claims cite `file:line`.

**Interval methods used below**, stated explicitly because they are mixed:
Wald = `p̂ ± 1.96·√(p̂(1−p̂)/n)`. CP = Clopper-Pearson exact. Boot = bootstrap percentile, 20k resamples.
McNemar = exact binomial on discordant pairs. Cluster-robust = SE with questions as clusters.

---

## 1. Setup

| Item | Value |
|---|---|
| Task | `countdown` from `reasoning_gym`, level 6 (6 numbers, 1 target) |
| Example prompt | `"Calculate 114 using all of these numbers: 18, 32, 36, 4, 29, 95."` |
| Model | `Qwen/Qwen3-4B-Instruct-2507` (vLLM, `max_model_len=32768`, TP over 4×A100) |
| Sampling | temperature 1.0, seed 42, `max_tokens=16384` |
| Grading | `reasoning_gym` `data.score_answer`, thresholded: `if score != 1: score = 0` |
| Roles | The same model is generator, ranker, and final judge |
| bon values | 1, 2, 4, 8, 16 (stored as top-level keys within one file) |

---

## 2. Pipeline

`CompletionStrategy`, five stages:

1. **Draft** — sample `N` full CoT solutions, or load from a cache.
2. **Truncate** — cut each draft to its first `max_plan_tokens` tokens (`strategies.py:176-177`, `tokenizer.encode`/`decode`; guard at `:171` is `if resp["token_count"] <= max_plan_tokens`).
3. **Prune** — keep `int(max(1, N // prune_ratio))` prefixes (`strategies.py:184`).
4. **Complete** — force-continue each survivor by pre-filling the assistant turn (`model.py:348-356`).
5. **Select** — LLM judge picks one winner (`model.py:153-266`); candidates shuffled (`:168`); 3 retries; fallback to candidate 0 (`:263`).

**Paths** (`main.py:148`): `paths_to_process = ["baseline"] if strategy is None else ["rank", "random", "tourney"]`.
One strategy invocation writes three files; one `--baseline` invocation writes one.

| Path | Pruning rule | Pruning LLM calls |
|---|---|---|
| `rank` | LLM ranks all N prefixes, keep top `N // prune_ratio` (`strategies.py:187-189`) | 1 per chunk, unconditional |
| `random` | Uniform random subset (`strategies.py:192-193`) | 0 |
| `tourney` | Group into 4s, rank each group, keep top half, repeat (`rank.py:130`) | 0 when `N == target_count` (`rank.py:139` loop condition false) |
| `baseline` | No truncation, no pruning; full BoN rollout, then judge | 0 |

**Four scored curves per run** (`main.py:169-193`):

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

- The judge runs anyway. `_process_final_selection` is invoked unconditionally (`model.py:359`) and calls
  `select_solution` (`model.py:374`); there is no `bon == 1` short-circuit. Measured: baseline bon=1 `mean_tokens` =
  8,417.40 vs. a cached-draft mean of 8,247.10 (≈170 judge tokens per problem).
- `rank` calls `ranker.rank(...)` unconditionally (`strategies.py:187`). `tourney` issues **zero** LLM calls
  (`rank.py:139`: `while any(len(idx_list) > target_count)` is false when 1 candidate targets 1). `random` issues none.

The three paths are therefore **not** identical in executed code at bon=1. Measured consequences in §5.1.

---

## 3. Filename format

`2026-05-30_07-14-44_rank_bon_1_2_4_8_16_strat_CompletionStrategy_plan_1000_prune_1.5.json`

Written at `main.py:243-254`; the f-string is `main.py:248`. The block sits inside the `for path in paths_to_process`
loop.

| Token | Source |
|---|---|
| timestamp | `strftime('%Y-%m-%d_%H-%M-%S')` at write time |
| `rank` | the path |
| `bon_1_2_4_8_16` | `--best_of_ns` |
| `strat_CompletionStrategy` | `strategy.name`, or `None` |
| `plan_1000` | value of `--max_plan_tokens` as parsed; not forwarded to generation (§7.1) |
| `prune_1.5` | `prune_ratio = max(1, args.prune_ratio)` (`main.py:104`) — the clamped value |

Pre-May-28 files use `{datetime}` (space + microseconds) and the word `strategy` rather than `strat`, and carry no
path token.

---

## 4. File inventory

| Path | JSON count | n | Dates |
|---|---|---|---|
| root, dated files | 4 | 100 | May 28–30 |
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

Written at `main.py:139-143` (only under `--baseline`), read at `main.py:121-124` via `--cache_fn`.

Shape: `{ "16"|"8"|"4"|"2"|"1" : [chunk][prompt][candidate] → {"text": str, "token_count": int} }`

Chunk counts 1/2/4/4/4 for bon 16/8/4/2/1 (`num_chunks = min(4, max_bon // bon)`, `model.py:308`). 6,000 completion
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
is the full raw response text (`main.py:189-190`).

---

## 5. Measurements

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

`strategies.py:187` (the ranker call) executes once inside `generate_prompts` (`model.py:332`), **before** the
`for path in ["rank","random","tourney"]` loop (`model.py:339`). The same call precedes all three paths'
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

(Survivor sets are not persisted in the May-28+ schema; `All Answers` (`model.py:385`) is not written to the results
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

`main.py:91` at commit `3969235` (the May-4-era code) hardcodes
`previous_responses_fn = "2026-05-01 08:31:55.062600_..._strategy_None_plan_4000_prune_2.json"`. May-4-era
`model.py:131` branches `if previous_responses is None or strategy.name != "CompletionStrategy":` → regenerate;
**else** `model.py:144-146` take `previous_responses[bon][j][index]` through unchanged and impute tokens.

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
May-4-era `main.py:13-14` sets `random.seed(42)`, and the ranker/judge `SamplingParams` carry `seed=42`
(`rank.py:17`, `model.py:35`). The residual cross-plan variation is not attributable to shuffle order.

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

At commit `89a0dc6`, `main.py:85-114` scores the None path as the **maximum over the N candidates** (`:87`
`best_score_for_task = 0`; `:107` `if score > best_score_for_task:`), and the None path has no selector. `89a0dc6`
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
`['', '', 0]`. Upper bound on accuracy is (30−27)/30 = 0.100; observed 0.0667. `main.py:65` documents
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

`rank.py:22-24` calls `random.shuffle(shuffled_indices)` under the comment "Create a list of original indices and
shuffle them to combat positional bias".

The "Selection Accuracy" metric plotted in this period was `Completion_score / None_score` — a ratio of two maxima
(§6.1). `plot_results.py:201` now labels it "Ratio Selected / Best".

---

## 7. Code behavior

### 7.1 `--max_plan_tokens` is not passed to generation

`main.py:103` reads it; `main.py:248` writes it into the filename; `main.py:136` calls `generate_responses(...)`
without it. It falls back to `model.py:268`'s default `500`, which calls `strategy.generate_prompts(...)` also
without it, reaching `strategies.py:144`'s default `500`.

- Repository has **81 commits**; **79 contain a `main.py`**. The value is passed into `generate_responses` in **0 of
  the 79**. `b724a3c` (Apr 13) and `4e6ed63` (May 4) forward it from `model.py` into `generate_prompts`, but forward
  an un-overridden constant 500.
- `main.py:58` argparse default is **4000**.
- The only files whose `plan_` label equals the effective value are `bad_none_results/*_plan_500_*` (6 files).
- `MAX_PLAN_TOKENS=(1000 2500 4000 6500 9000)` is set at `run_experiment.sh:5` and passed at `:41`.

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

`--group_size` is likewise not passed (`main.py:71`, `:105`); its argparse default (4) equals the function default
(`model.py:268`).

### 7.2 The `strategies.py:189` index filter is a no-op

`strategies.py:189` filters ranked indices with `if idx < len(new_prompts[i])`. This filter cannot remove anything:

- `rank.py:95` already bounds parsed indices: `unique_ints = [x for x in parsed_ints if ... and x < expected_length]`.
- `rank.py:98` requires `len(unique_ints) == expected_length` for success — i.e. a full permutation.
- `rank.py:113-127` is a deterministic fallback ("Randomly padding"): any index failing all 3 retries gets
  `final_indexes[i] = valid_ints + missing_ints`, again a full permutation.

So `ranked_indexes[i]` is always a complete permutation of `range(len(new_prompts[i]))`. Measured: across all 20
May-4 `CompletionStrategy` files, **10,000/10,000 stored `ranked_indexes` lists are full permutations** (zero short,
zero empty), and **0/10,000 `generated_diverse_prompts` lists are empty**.

`rank()` is shared by the rank and tourney paths (`rank.py:163`, `model.py:78`); `model.py:97-106` is a second
fallback on the tourney path.

(`main.py:175` calls `random.randrange(len(all_answers))`, which would raise `ValueError` on an empty list. No empty
list is reachable on the `CompletionStrategy` path. The abstract base `Strategy.generate_prompts`
(`strategies.py:31-92`) can produce an empty list at `:67-68`, but `main.py:118` only instantiates
`CompletionStrategy`, which overrides it.)

### 7.3 `plot_results.py` raises an exception on 77 of 77 JSON files

`parse_results()` run against every results JSON in the repo (excluding `.venv` and `baseline_cache.json`):

| exception | count | files |
|---|---|---|
| `TypeError: unsupported operand type(s) for +: 'int' and 'str'` | 52 | `archive/` 9 + `bad_none_results/` 12 + `bad_selection/` 10 + `non_ranked_` 11 + `ranked_` 10 — in this schema `score[1]` is the answer string |
| `KeyError: 'random_results'` | 21 | May 4 |
| `KeyError: 'results'` | 4 | root |
| **completed** | **0** | |

`plot_all_results.sh:4`/`:18` glob `*strategy_None*.json` / `*strategy_CompletionStrategy*.json`; `main.py:248`
emits `_strat_None_` / `_strat_CompletionStrategy_`.

### 7.4 `tourney_total_tokens` is written and never read

Two occurrences in the repo, both writes: `model.py:363` and `model.py:389`. Zero reads. It is not serialized —
`grep -c tourney_total_tokens` on the 37 MB May-30 rank file returns 0.

`main.py:170` consumes `chunk["total_tokens"]`. `model.py:362` adds each path's own `path_selection_tokens` into
that path's `total_tokens`, inside the `for path in [...]` loop (`model.py:339`). Measured `mean_tokens` at bon=16:
rank 61,664.75, random 61,272.28, tourney 52,847.47.

No token field is emitted for the `tourney_results` curve.

### 7.5 `main_matharena.py` and `main_livecodebench.py`

`python -m py_compile main_matharena.py` → `SyntaxError` at **line 14**
(`dataset_path = "MathArena/hmmt_feb_2025"Example subset, ...`). `main_matharena.py:72` reads
`bon_outputs["responses"]`; `generate_responses` now returns `organized_outputs[path][bon]["chunks"]`.

`main_livecodebench.py` imports only `re, random, datetime, json, datasets, vllm` — it does not import `model/`. Its
extraction regex at `:58` is `` r'```python ... (.*?)```' `` — the `...` is a literal.

Neither file is imported by `main.py` or invoked by `run_experiment.sh`.

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
