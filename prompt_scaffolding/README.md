# prompt_scaffolding

Does **pruning partial reasoning early** beat plain best-of-N at the same budget?

The pipeline drafts N candidate plans for a problem, prunes them down to `k = N / prune_ratio`
by some selection rule, finishes only the survivors into full answers, and picks one. The
comparison is against a baseline that drafts N complete answers and picks one. Task is
`reasoning_gym` **countdown** at level 6 (six numbers), model is **Qwen/Qwen3-4B-Instruct-2507**
served by vLLM, seed 42 throughout.

## Arms

Each run writes one JSON per arm ("path"):

| arm | how the N drafts are cut to k |
|---|---|
| `baseline` | no pruning — N complete answers, then one judge call |
| `rank` | one LLM call ranks all N plans; keep the top k |
| `random` | keep k at random — no LLM call, the control for whether ranking adds anything |
| `tourney` | bracket of `group_size`-way rank calls, halving until k survive |

Three variants, distinguished by a filename tag so analysis never mixes them:

| variant | tag | after pruning to k |
|---|---|---|
| prune-only | *(none)* | finish each of the k survivors once → **k** completions |
| regen | `_regen` | regenerate back to **N** completions, spread over the k survivors ([`even_top_allocation`](model/utils.py)) |
| diverse / best-of-k | `_diverse` | prune to k *unique approaches* (LLM-clustered), then regen to N |

Within each arm, four selectors are scored on the same completions: the model's own pick,
a random pick, the oracle ceiling (was *any* candidate right?), and the tournament pick.

## Running

```bash
# One config, one GPU, smoke test
MAX_PLAN_TOKENS="1000" PRUNE_RATIOS="2" NUM_GPUS=1 NUM_EXAMPLES=30 ./run_experiment.sh

# Full sweep: 3 max_plan_tokens x 4 prune_ratios, one config per array task
sbatch job_sweep_n100.slurm
```

`run_experiment.sh` runs the baseline once, caches it, then sweeps every
`(max_plan_tokens, prune_ratio)` config against that cache. Useful knobs:
`MAX_PLAN_TOKENS`, `PRUNE_RATIOS`, `NUM_EXAMPLES`, `NUM_GPUS`, `SKIP_BASELINE=1`,
`REGEN=1`, `MAIN=main_diverse.py`, `CONFIG_INDEX` (array mode), and `ONLY_PATHS=tourney`
to re-run a single arm off the cache.

Entry points: `main.py` (best-of-N), `main_diverse.py` (best-of-k; pins `--diverse --regen`).

### baseline_cache.json

The baseline's N drafts are the *shared input to every arm*, so they are generated once and
cached. `reasoning_gym` is size-independent — the first M questions of a size-M' dataset are
identical for a fixed seed — so a 100-prompt cache is sliced in-memory for smaller runs, and
never needs regenerating for a lower `--num_examples`.

Each cached draft records just `text` and `token_count` (sampled tokens). The existing
`baseline_cache.json` needs no regeneration.

## Output format

```
{ "<N>": {                                  # N = best-of-N
    "questions":      [ str, ... ],         # the prompts, one per question
    "dataset_metrics": { "average_score", "mean_tokens", "std_tokens", "num_chunks_averaged" },
    "prompt_metrics": [                     # one entry per question
      { "mean_score", "mean_tokens", "std_tokens", "tourney_mean_tokens",
        "chunks_data": { "results", "random_results", "best_results", "tourney_results" } },
      ... ] } }
```

Each `chunks_data` list holds one `{answer, score}` per **chunk**. A chunk is one independent
best-of-N replicate: `min(4, max_bon // N)` of them are averaged, so small N gets 4 replicates
and `N == max_bon` gets 1. An observation is a (question, N, chunk) triple.

The tournament selector is charged its **own** cost (`tourney_*`), which differs from the
other selectors in the selection component.

## Token accounting

**`mean_tokens` counts sampled (decode) tokens only. Prompt/prefill tokens are not counted
anywhere in this pipeline, deliberately.** Two reasons:

* vLLM runs with **prefix caching enabled by default** (`CacheConfig.enable_prefix_caching`,
  not disabled here), so the k continuation requests of one question share their scaffold and
  only the first actually recomputes it. Any prefill figure derived from the prompts is a
  *logical upper bound*, not work the GPU did.
* Prefill is one parallel forward pass; decode is one serial pass per token. Per token the
  FLOPs are comparable, but the wall-clock is not, so adding them treats non-fungible
  quantities as fungible.

If prefill is ever wanted, **measure** it — `RequestOutput` exposes `prompt_token_ids` and
`num_cached_tokens` — and report it as its own axis rather than folding it into this total.
See the note at the top of [model/utils.py](model/utils.py).

What a pruned arm charges, per question at best-of-N with k = N/`prune_ratio` survivors:

| stage | sampled tokens charged |
|---|---|
| drafting | **N × `max_plan_tokens`** — all N plans, including the ones pruned away (they cost real time), each capped at the plan budget |
| prune | the rank / bracket / clustering reply; **zero for the `random` arm**, which makes no LLM call |
| continuation | **N** completions under `--regen` (spread over k requests), or **k** under prune-only |
| final judge | one reply, at every N including N=1 (there is no single-candidate short-circuit) |

`std_tokens` is the spread of the same values `mean_tokens` averages, so the two always
describe the same quantity.

### What this basis says about pruning

Measured on the n=100 sweeps, `rank` arm, prune 2 (so k = N/2):

| N | baseline | regen (N continuations) | prune-only (k continuations) | regen/base | prune-only/base |
|---|---|---|---|---|---|
| 2 | 16,890 | 11,880 | 6,969 | 0.70x | 0.41x |
| 4 | 33,840 | 23,145 | 13,914 | 0.68x | 0.41x |
| 8 | 67,278 | 46,248 | 27,577 | 0.69x | 0.41x |
| 16 | 133,186 | 89,248 | 53,467 | 0.67x | 0.40x |

(`max_plan_tokens=1000`; at 2500 the ratios are 0.66x / 0.47x.)

**regen − prune-only is exactly (N−k) continuations**, as designed: dividing that gap by
(N−k) gives a stable per-continuation length at every N — 4,911 / 4,615 / 4,668 / 4,473 at
plan=1000, and 3,254 / 3,144 / 3,184 / 3,076 at plan=2500. That is the structural check that
the regen staircase is charged for every branch it generates.

**regen does not cost the same as the baseline** — it runs about **0.67–0.70x**, not 1.0x, even
though both decode N plans and N completions. The gap is behavioural, not an accounting
artifact: a branch costs `max_plan_tokens` + ~4,473 continuation ≈ 5,473 tokens at plan=1000,
while a free-running baseline solution to the same question averages 8,324. Conditioning on a
truncated plan plus an explicit "produce the final answer in tags" system prompt makes the
model converge ~34% sooner. So the regen arm is *not* iso-token with the baseline; it is
cheaper, and the accuracy comparison at matched N is "less compute, different behaviour"
rather than "same compute, better selection".

### Token basis of existing results

| file / tree | `mean_tokens` is |
|---|---|
| `2026-07-25_11-42-12_baseline_bon_1_2_4_8_16_32_...json` | decode only (stripped — see below) |
| `2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_...json` | decode only (never had prefill) |
| `runs/2026-07-18_prune_only/`, `runs/2026-07-24_*` | decode only |
| `runs/archive/**` (incl. `partials/`) | **decode + prefill — not yet stripped** |
| anything generated from now on | decode only |

Both root baselines are now on the same basis and are directly comparable (they agree to
within 2%). The July file was put there by `strip_prefill.py`; it had been patched by a
since-removed `prefill_tokens.py` that *estimated* prefill, with three known gaps — it counted
the question and instruction as raw text without the `<|im_start|>user … assistant\n` wrapper
(~18 tokens short per request), it estimated survivor plan lengths instead of measuring them,
and it skipped the judge whenever there was a single candidate (so N=1 under-counted by ~250).
Stripping also repaired the mean/std mismatch that patch left behind: `std_tokens` had stayed
decode-only while `mean_tokens` became a total.

> **`runs/archive/**` is currently mixed.** Its arm files still carry decode+prefill, while the
> baseline inside it is the same inode as the stripped root file (3 hard links), so it is now
> decode-only. `analysis.py` contrasts arms against that baseline, so put the tree on one basis
> before using it: `python3 strip_prefill.py runs/archive`. That deletes the prefill estimates
> (the decode subtotals are preserved as `mean_tokens`), so it is deliberate, not automatic.

### Checking a written file is on this basis

```bash
python3 verify_baseline_decode_only.py                      # the two root baselines
python3 verify_baseline_decode_only.py TARGET.json REF.json
```

Checks a baseline against a reference baseline known to be decode-only. The cross-file token
comparison is the *weakest* part and the script says so: at N=1 the cross-run difference has
a standard error of ~716 tokens while a folded-in prefill is only ~139 (0.19 SE), so that
table could never settle the question on its own. The verdict rests on two exact checks —
no prefill/decode key anywhere plus a schema match against the reference, and the identity
that reconstructing `std_tokens` from the per-question means and stds must reproduce the
stored value exactly (it does not when prefill is folded into the mean but not the std,
which is precisely what the old patch did). Both are checked at N=32, which the reference
does not contain. A **positive control** then re-injects prefill into an in-memory copy and
confirms both checks fire, so a clean pass is evidence rather than a vacuous one.

### Verifying a file really is on this basis

```bash
python3 verify_decode_only.py                       # the bon=1..32 baseline vs the May one
python3 verify_decode_only.py TARGET --reference REF
```

Checks a target against a reference baseline that predates prefill entirely, so the
reference's schema *defines* decode-only. The verdict rests on three structural checks — no
`prefill_`/`decode_` key anywhere, a key set matching the reference (plus an allowlist for
later decode-only additions like `tourney_mean_tokens`), and the mean/std identity: rebuild
the dataset std from the per-question means and stds, which matches only if `mean_tokens`
and `std_tokens` describe the same series. Folding prefill into the mean and not the std —
exactly what the old patch did — breaks that identity, which makes it the fingerprint to
test for. All three run per-N, so they cover N=32 even though the reference stops at 16.

A cross-file token table is printed too, but labelled as corroboration only: at N=1 it
resolves ~893 tokens (2 SE) while the prefill under test is ~139, so two independent runs
differ by more than the quantity being detected. A **positive control** closes the loop —
prefill is re-injected into an in-memory copy and the checks must flip to failing, or a pass
would have meant nothing.

### Putting an already-written file on this basis

```bash
python3 strip_prefill.py --dry-run runs/archive     # report what would change
python3 strip_prefill.py FILE_OR_DIR ...            # rewrite in place
```

`mean_tokens ← decode_mean_tokens`, `tourney_mean_tokens ← tourney_decode_mean_tokens`, then
every `decode_*`/`prefill_*` key is dropped. `std_tokens` is left alone — it was always
decode-only, so it ends up agreeing with the mean. Idempotent, so it is safe over a whole
tree, and it rewrites the existing inode rather than replacing the file, so a result JSON
hardlinked into several run directories stays consistent across all its names.

## Testing

```bash
.venv/bin/python test_token_accounting.py     # ~40s, no GPU
```

Drives the real `main.run()` — real chunking, real selection and ranking control flow, real
aggregation, real JSON writer — against a stub LLM that reports the token counts vLLM would
and keeps a ledger of every token it charged. Covers baseline, all three arms, `--regen` and
`--diverse`. Asserts that:

* the four stages sum **exactly** to the emitted `mean_tokens`, so no stage can be dropped or
  counted twice;
* drafting lands on `N × max_plan_tokens` — all N drafts, not just the k survivors;
* `--regen` decodes N continuations from k requests while prune-only decodes k, and the
  difference is exactly (N−k) continuations;
* `random` pays nothing at the prune stage, and the judge is charged even at N=1;
* `std_tokens` is the spread of the values `mean_tokens` averages;
* **no `prefill`/`prompt_token`/`decode_mean_tokens` field appears anywhere in the output** —
  a prefill count coming back is a regression;
* `strip_prefill.py` restores a patched block correctly and is idempotent.

## Analysis

```bash
python3 analysis.py RUN_DIR --plan 2500 --prune 2      # stats table, question-clustered CIs
python3 analysis.py RUN_DIR --dump-scores scores.json  # portable extract, survives off-cluster
./plot_all_results.sh RUN_DIR                          # accuracy-vs-tokens grids
python3 merge_bon_splits.py RUN_DIR/partials -o RUN_DIR # recombine bon-split array tasks
```

Observations from one question are correlated — a hard countdown instance is hard at every N
and in every chunk — so `analysis.py` clusters by question rather than assuming independence.

## Layout

```
main.py                  pipeline + grading/aggregation; writes one JSON per arm
main_diverse.py          best-of-k entry point (--diverse --regen)
model/model.py           generation, judge selection, tournament selection
model/rank.py            ranker: rank / cluster / tourney_rank
model/strategies.py      CompletionStrategy (plan drafting + the three prunings)
model/utils.py           draft prompt, answer extraction, allocation, accounting note
strip_prefill.py         put already-written results back on the decode-only basis
verify_decode_only.py    prove a result file counts no prompt tokens, vs a reference
verify_baseline_decode_only.py  prove a baseline is decode-only, against a reference
analysis.py              statistics with question-clustered intervals
plot_results.py          accuracy-vs-token curves
test_token_accounting.py offline end-to-end token-accounting check
runs/                    archived sweeps (result JSONs, plots, reports)
```

The legacy `HypothesisStrategy` / `PlanStrategy` / `ConceptStrategy` /
`ReasoningStructureStrategy` / `CountdownStrategy` / `UserStrategy` classes are unreachable
from `main.py`, which only ever builds `CompletionStrategy`; their `generate_prompts` does not
accept `group_size`/`diverse` or return the `paths` dict the pipeline expects.
