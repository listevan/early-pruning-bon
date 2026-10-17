# Pruned Best-of-N

Best-of-N is the simplest way to spend more compute at inference time: sample N answers, have
a judge pick one. It works, but most of the tokens go into finishing answers that were never
going to be picked. This project asks whether you can cut that waste by pruning early: write
only the first few thousand tokens of each candidate, rank the partial solutions, throw most of
them away, and finish only the survivors.

Short version of what we found: **not really.** At the same number of samples, pruning saves a
lot of tokens but loses accuracy. At the same token budget it comes out about even with plain
best-of-N run at a smaller N. Details below.

This started as a CS 497 project at UIUC (spring/summer 2026).

## Setup

- **Task:** [Countdown](https://github.com/open-thought/reasoning-gym) level 6 from
  `reasoning_gym` (use six numbers and `+ - * /` to hit a target), 100 questions, seed 42.
- **Model:** Qwen3-4B-Instruct-2507 on vLLM. The same model generates, ranks and judges.
- **N:** 1, 2, 4, 8, 16 (and 32 for the baseline in the later runs).
- **Pipeline:** draft N solutions, cut each to its first `max_plan_tokens` tokens, keep
  `N / prune_ratio` of them, force-continue the survivors to full answers, then one judge
  call picks the final answer.
- **Pruning arms**, compared against a plain best-of-N baseline:
  - `rank`: one LLM call ranks all N prefixes, keep the top k
  - `tourney`: rank in groups of 4, keep the top half, repeat
  - `random`: keep k at random (the control)
- **Grid:** `max_plan_tokens` in {1000, 2500, 4000} x `prune_ratio` in {1.5, 2, 3, 4}.

Two follow-up variants are also in here: **regen** (prune to k, then regenerate back up to N
completions from the survivors) and **best-of-k** (prune to k *distinct approaches*, clustered
by the LLM, before regenerating).

## Results

Accuracy at equal N, averaged over all 12 configs (July 2026 sweep):

| N  | best-of-N | pruned (rank) | tokens saved |
|----|-----------|---------------|--------------|
| 2  | 54.5%     | 49.2%         | 54%          |
| 4  | 63.0%     | 54.9%         | 59%          |
| 8  | 69.5%     | 62.7%         | 58%          |
| 16 | 70.0%     | 68.2%         | 57%          |

What the numbers say:

1. **The judge itself works.** Picking with the LLM judge beats picking at random from the same
   pool by 7 points at N=2 and 25 points at N=16. This held up in every arm and survived
   multiple-comparison correction. It was the most solid result we got.
2. **Pruning throws away right answers.** Most of the accuracy loss happens before the judge
   ever runs: in 6 to 14% of questions every correct candidate gets pruned.
3. **Ranking prefixes is better than chance, but not by enough.** `rank` beats `random`
   pruning by about 3 points on average, and by up to 5 points with longer (4000-token)
   prefixes. That's smaller than what pruning costs.
4. **At equal budget it's a wash.** Interpolating the baseline curve to each pruned run's exact
   token spend gives +0.4 points on average. But the baseline had no stop string, so it got
   billed for about 26% junk tokens after the answer. Correcting for that puts the pruned runs
   about 1.6 points *behind*. The 57% savings in the table drop to roughly 40% after the same
   correction.
5. **Regenerating back to N didn't change the picture** (n=100, N=16: 70.2% at 88k tokens vs
   72.0% at 133k for the baseline; about even at matched budget, slightly behind after the
   stop-token correction). Forcing the survivors to be distinct approaches didn't raise the
   ceiling either (n=30).

The best single cell (rank, plan=2500, prune=1.5, N=16) hit 76% vs the baseline's 70% at about
half the tokens. That cell is one draw out of ~60 noisy ones and doesn't survive correction, so
don't read much into it.

The one place it looks promising is large N. At N=16 the single judge call starts to struggle
(it captures only ~89% of the achievable accuracy), so pre-pruning hurts less and gives the
judge an easier job. We didn't get to test that properly.

The full write-up, with confidence intervals and caveats, is in
[`prompt_scaffolding/runs/2026-07-18_prune_only/RESULTS.md`](prompt_scaffolding/runs/2026-07-18_prune_only/RESULTS.md).

## Repo layout

```
prompt_scaffolding/
  main.py                  baseline + pruned arms, writes one result JSON per arm
  main_diverse.py          best-of-k variant
  model/                   generation, ranking, tournament, pruning strategy
  run_experiment.sh        sweep driver: baseline once, then every config
  job_*.slurm              the SLURM jobs we ran (NCSA Delta, A40s)
  analysis.py              stats with question-clustered CIs (stdlib only)
  plot_*.py                accuracy vs token plots
  test_token_accounting.py offline check of the token accounting (no GPU)
  runs/                    July 2026 sweeps: plots, analysis output, write-ups
  archive/                 March to May runs, mostly from before the bug fixes
```

`main_matharena.py` and `main_livecodebench.py` are unfinished ports to other benchmarks and
don't run as-is. `prompt_scaffolding/README.md` has the detailed notes on arms, output format and
how tokens are counted.

## Running it

You need a GPU that can host Qwen3-4B (we used A40s).

```bash
cd prompt_scaffolding
uv venv && uv pip install -r requirements.txt

# smoke test: one config, one GPU, 30 questions
MAX_PLAN_TOKENS="1000" PRUNE_RATIOS="2" NUM_GPUS=1 NUM_EXAMPLES=30 ./run_experiment.sh

# stats and plots for a finished run
python3 analysis.py RUN_DIR --grid
./plot_all_results.sh RUN_DIR
```

The raw result JSONs are too big for git and aren't committed, so `runs/` only has the plots
and the analysis output.

## Caveats

One task, one 4B model, 100 questions. The high-N cells only have 100 to 200 observations, so
a null result there doesn't mean there's no effect. The prefixes are truncated baseline drafts
rather than plans the model was asked to write, which may undersell the idea.
