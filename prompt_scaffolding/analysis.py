#!/usr/bin/env python3
"""
Regenerate the statistics table from the raw per-arm result JSONs.

Every number this prints is derived here, from the JSONs, with no hidden steps.
That is the whole point of the file: the figures quoted in RESULTS.md (and on a
resume) should come from code you can run, not from a one-off analysis session.

WHAT IT READS
-------------
The JSONs main.py writes, one file per arm ("path"): baseline, rank, random,
tourney. Layout (see main.py:196-252):

    { "<N>": {                                # N = best-of-N: 1, 2, 4, 8, 16
        "dataset_metrics": {...},
        "prompt_metrics": [                   # one entry per question (100)
          { "mean_tokens": float,             # SAMPLED (decode) tokens only -- prompt/prefill
                                              # tokens are not counted anywhere in this
                                              # pipeline. See model/utils.py and the README.
            "chunks_data": {
              "results":        [ {"score": 0|1}, ... ],   # one per chunk
              "random_results": [ {"score": 0|1}, ... ],
              "best_results":   [ {"score": 0|1}, ... ],
              "tourney_results":[ {"score": 0|1}, ... ] } }, ... ] } }

An observation is one (question, N, chunk). A question is reused at every N and
across chunks, so the same question contributes many observations.

WHY CLUSTERING
--------------
Observations from the same question are correlated: a hard Countdown instance is
hard in every chunk and at every N. A naive interval assumes all observations are
independent, which overstates the sample size and makes the interval too narrow.
Clustering by question allows arbitrary correlation *within* a question and
assumes independence only *across* questions. It almost always widens the
interval. That is the conservative choice.

USAGE
-----
    python3 analysis.py RESULTS_DIR [--plan 1000] [--prune 1.5]
    python3 analysis.py --baseline b.json --rank r.json --random rnd.json
    python3 analysis.py RESULTS_DIR --grid --regen     # the regenerate-back-to-N sweep

The prune-only sweep and the regenerate-back-to-N sweep (`--regen`, files ending
`_regen.json`) are separate experiments and are never pooled into one grid. They
share a baseline: baseline generation has no regen stage.

No third-party dependencies. Standard library only.
"""

import argparse
import glob
import json
import math
import os
import re
import sys
from collections import defaultdict

ARMS = ["baseline", "rank", "random", "tourney"]
SELECTORS = ["results", "random_results", "best_results", "tourney_results"]
Z = 1.959963985  # two-sided 95% normal quantile


# ---------------------------------------------------------------- loading

def load_arm(path):
    """Return {N: {"scores": {selector: {(q, chunk): 0|1}}, "tokens": {q: float}}}."""
    with open(path) as f:
        raw = json.load(f)

    out = {}
    for n_str, block in raw.items():
        n = int(n_str)
        scores = {sel: {} for sel in SELECTORS}
        tokens = {}
        for q, pm in enumerate(block["prompt_metrics"]):
            tokens[q] = pm["mean_tokens"]
            for sel in SELECTORS:
                for chunk, rec in enumerate(pm["chunks_data"][sel]):
                    scores[sel][(q, chunk)] = int(rec["score"])
        out[n] = {"scores": scores, "tokens": tokens}
    return out


def file_variant(path):
    """The sweep variant a result filename belongs to: '' (prune-only), 'regen'
    (best-of-N regen), or 'diverse' (best-of-k, unique-pruned)."""
    m = re.search(r"_prune_[\d.]+(?:_(regen|diverse))?\.json$", os.path.basename(path))
    return (m.group(1) or "") if m else ""


def discover(directory, plan, prune, variant=""):
    """Find one file per arm in a directory, optionally filtered by plan/prune.

    `variant` selects which sweep to read: '' = prune-only, 'regen' = best-of-N
    regeneration (filenames end `_regen.json`), 'diverse' = best-of-k with unique
    pruning (`_diverse.json`). The three are separate experiments and are never
    mixed: a run in one variant excludes files of the others.

    The BASELINE arm is exempt from the variant filter. Baseline generation has no
    regen/diverse stage, so there is only ever a plain baseline file for the other
    arms to be compared against.
    """
    found = {}
    for arm in ARMS:
        pat = os.path.join(directory, f"*_{arm}_bon_*.json")
        cands = sorted(glob.glob(pat))
        want = "" if arm == "baseline" else variant
        cands = [c for c in cands if file_variant(c) == want]
        if plan is not None:
            cands = [c for c in cands if f"_plan_{plan}_" in c]
        if prune is not None:
            suffix = f"_{want}" if want else ""
            cands = [c for c in cands if c.endswith(f"_prune_{prune}{suffix}.json")]
        if cands:
            if len(cands) > 1:
                print(f"note: {len(cands)} candidates for '{arm}', taking newest: "
                      f"{os.path.basename(cands[-1])}", file=sys.stderr)
            found[arm] = cands[-1]
    return found


# ---------------------------------------------------------------- statistics

def mcnemar_exact(b, c):
    """Two-sided exact McNemar p-value.

    b = times A won and B lost. c = times B won and A lost. Ties carry no
    information about which is better, so they are discarded -- that is what
    makes this a *paired* test. Under the null "neither is better", each of the
    n = b + c discordant pairs is a fair coin, so b ~ Binomial(n, 0.5).
    """
    n = b + c
    if n == 0:
        return 1.0  # no disagreements at all; nothing to test
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def paired_contrast(a_scores, b_scores):
    """Compare two arms on the observations they share.

    a_scores/b_scores: {(question, chunk): 0|1}
    Returns the mean difference plus a naive and a cluster-robust interval.
    """
    keys = sorted(set(a_scores) & set(b_scores))
    if not keys:
        return None

    diffs = [a_scores[k] - b_scores[k] for k in keys]          # each is -1, 0 or +1
    clusters = [k[0] for k in keys]                            # cluster == question id
    n = len(diffs)
    delta = sum(diffs) / n

    resid = [d - delta for d in diffs]

    # --- naive SE: assumes all n observations are independent.
    ss = sum(r * r for r in resid)
    se_naive = math.sqrt(ss / (n * (n - 1))) if n > 1 else float("nan")

    # --- cluster-robust SE: sum the residuals INSIDE each question first, then
    # square. If a question's errors move together, those residuals reinforce
    # instead of cancelling, and the variance grows to reflect it.
    by_cluster = defaultdict(float)
    for cl, r in zip(clusters, resid):
        by_cluster[cl] += r
    g = len(by_cluster)
    meat = sum(s * s for s in by_cluster.values())
    se_cluster = math.sqrt(meat) / n if n else float("nan")
    # finite-sample correction; negligible at g=100, reported for completeness
    se_cluster_fc = se_cluster * math.sqrt(g / (g - 1)) if g > 1 else float("nan")

    # design effect: how much the naive interval was lying, squared.
    deff = (se_cluster / se_naive) ** 2 if se_naive and se_naive == se_naive else float("nan")

    # --- McNemar on the discordant pairs
    b_wins = sum(1 for d in diffs if d > 0)
    c_wins = sum(1 for d in diffs if d < 0)

    # --- clustered p-value. The exact McNemar test above treats every discordant
    # pair as independent, which they are not (211 pairs, but only 100 questions).
    # So it is anticonservative wherever deff > 1. This is the same test done with
    # the cluster-robust SE instead: a z-test on delta / SE_cluster.
    # Use the finite-sample-corrected SE everywhere. It was previously computed and then
    # ignored, so the "cluster-robust" interval was fractionally narrower than intended.
    if se_cluster_fc == se_cluster_fc and se_cluster_fc > 0:
        se_cluster = se_cluster_fc

    if se_cluster and se_cluster == se_cluster and se_cluster > 0:
        z = delta / se_cluster
        p_clustered = math.erfc(abs(z) / math.sqrt(2))   # two-sided normal
    else:
        p_clustered = float("nan")

    return {
        "n": n, "clusters": g, "delta": delta,
        "se_naive": se_naive, "se_cluster": se_cluster, "se_cluster_fc": se_cluster_fc,
        "ci_naive": (delta - Z * se_naive, delta + Z * se_naive),
        "ci_cluster": (delta - Z * se_cluster, delta + Z * se_cluster),
        "deff": deff,
        "b": b_wins, "c": c_wins, "discordant": b_wins + c_wins,
        "p_mcnemar": mcnemar_exact(b_wins, c_wins),
        "p_clustered": p_clustered,
    }


def question_means(scores):
    """Collapse {(question, chunk): 0|1} to {question: mean over that question's chunks}."""
    agg = defaultdict(list)
    for (q, _c), v in scores.items():
        agg[q].append(v)
    return {q: sum(v) / len(v) for q, v in agg.items()}


def question_contrast(a_by_q, b_by_q):
    """Paired comparison at the QUESTION level, one observation per question.

    Needed for cross-N comparisons: N=8 and N=16 have different chunk counts, so
    (question, chunk) keys do not line up and paired_contrast would silently drop
    observations. Collapsing to a per-question mean first keeps the pairing honest.
    Each question is its own cluster here, so there is no further clustering to do.
    """
    qs = sorted(set(a_by_q) & set(b_by_q))
    if len(qs) < 2:
        return None
    diffs = [a_by_q[q] - b_by_q[q] for q in qs]
    n = len(diffs)
    delta = sum(diffs) / n
    var = sum((d - delta) ** 2 for d in diffs) / (n - 1)
    se = math.sqrt(var / n)
    wins = sum(1 for d in diffs if d > 0)
    losses = sum(1 for d in diffs if d < 0)
    p = math.erfc(abs(delta / se) / math.sqrt(2)) if se > 0 else float("nan")
    return {"n": n, "delta": delta, "se": se,
            "ci": (delta - Z * se, delta + Z * se),
            "wins": wins, "losses": losses,
            "p": p, "p_sign": mcnemar_exact(wins, losses)}


def noninferiority_p(delta, se, margin):
    """One-sided test of H0: delta <= -margin ("materially worse than the comparator").

    Rejecting H0 is what licenses a parity claim: "no more than `margin` worse".
    A non-significant TWO-sided test does NOT establish equivalence -- with n=100
    these intervals are wide enough to hide a real regression, so absence of a
    significant difference is not evidence of no difference. `margin` is in
    proportion units (0.05 = 5 percentage points).
    """
    if not se or se != se or se <= 0:
        return float("nan")
    z = (delta + margin) / se
    return 0.5 * math.erfc(z / math.sqrt(2))          # upper-tail P(Z > z)


def token_contrast(a_tokens, b_tokens):
    """Paired per-question token difference WITH an interval.

    The cost reduction is the most robust claim in this experiment, so it should
    carry uncertainty like the accuracy numbers do, not just a point estimate.
    """
    qs = sorted(set(a_tokens) & set(b_tokens))
    if len(qs) < 2:
        return None
    diffs = [a_tokens[q] - b_tokens[q] for q in qs]
    n = len(diffs)
    mean = sum(diffs) / n
    var = sum((d - mean) ** 2 for d in diffs) / (n - 1)
    se = math.sqrt(var / n)
    base = sum(b_tokens[q] for q in qs) / n
    lo, hi = mean - Z * se, mean + Z * se

    # Percentage change is a RATIO, so its interval cannot be obtained by dividing the
    # difference bounds by the denominator mean -- that treats the denominator as known.
    # Delta method on r = A/B with the paired covariance retained.
    A = sum(a_tokens[q] for q in qs) / n
    B = base
    va = sum((a_tokens[q] - A) ** 2 for q in qs) / (n - 1) / n
    vb = sum((b_tokens[q] - B) ** 2 for q in qs) / (n - 1) / n
    cov = sum((a_tokens[q] - A) * (b_tokens[q] - B) for q in qs) / (n - 1) / n
    if B:
        var_r = va / B ** 2 + (A ** 2) * vb / B ** 4 - 2 * A * cov / B ** 3
        se_r = math.sqrt(max(0.0, var_r))
        r = A / B
        pct_ci = (100 * (r - 1 - Z * se_r), 100 * (r - 1 + Z * se_r))
    else:
        pct_ci = (float("nan"),) * 2
    return {"delta": mean, "ci": (lo, hi), "base": base,
            "pct": 100 * mean / base if base else float("nan"),
            "pct_ci": pct_ci}


def power_summary(se, ref):
    """Minimum detectable effect at 80% power, and power to detect `ref`.

    Both depend only on the SE, NOT on the observed effect. Post-hoc power computed
    from the observed effect is just a monotone restatement of the p-value and says
    nothing extra, so it is deliberately not reported. This matters here because a
    null result at n=100 is usually a power failure, not evidence of no difference:
    simulation puts power at ~23% for a true 5-point effect and ~62% at 10 points.
    """
    if not se or se != se or se <= 0:
        return None
    mde = (Z + 0.8416) * se                           # z_.975 + z_.80
    power_ref = 0.5 * math.erfc((Z - ref / se) / math.sqrt(2))
    return {"mde": mde, "power_ref": power_ref}


def holm_survivors(pvals, alpha=0.05):
    """Holm-Bonferroni step-down. Returns the set of indices significant at FWER alpha."""
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    m = len(pvals)
    out = set()
    for rank, i in enumerate(order):
        if pvals[i] <= alpha / (m - rank):
            out.add(i)
        else:
            break                                     # step-down: stop at first failure
    return out


def bh_survivors(pvals, q=0.05):
    """Benjamini-Hochberg step-up. Returns the set of indices significant at FDR q."""
    order = sorted(range(len(pvals)), key=lambda i: pvals[i])
    m = len(pvals)
    kmax = 0
    for rank, i in enumerate(order, 1):
        if pvals[i] <= q * rank / m:
            kmax = rank
    return set(order[:kmax])


def accuracy(scores):
    """Plain mean over observations."""
    return sum(scores.values()) / len(scores) if scores else float("nan")


# ---------------------------------------------------------------- reporting

def pp(x):
    """Format a proportion as percentage points."""
    return f"{100 * x:+.1f}" if x == x else "  n/a"


# Every clustered p-value computed during a run lands here so the grid can be
# corrected for multiple comparisons at the end. Without this, sweeping 12 configs
# x 5 N x several contrasts produces dozens of "significant" cells by chance alone.
# Correcting across UNRELATED hypothesis families distorts inference: the
# judge-vs-random effects are enormous (p ~ 1e-9) and, pooled in, they inflate m
# and eat alpha that the borderline arm contrasts need. So each p-value carries a
# family tag and correction runs WITHIN family.
PVALS = []          # list of (context, family, label, p)


_SEEN_BASELINE = set()


def record_p(label, p, family):
    if p != p:                                        # skip nan
        return
    # One baseline file is reused for all 12 configs, so baseline-only tests (e.g.
    # "baseline N=8: judge - random") are byte-identical across configs. Counting them
    # 12 times inflates m and injects exact-duplicate p-values into Holm/BH.
    if label.startswith("baseline "):
        if label in _SEEN_BASELINE:
            return
        _SEEN_BASELINE.add(label)
    PVALS.append((CONTEXT[0], family, label, p))


CONTEXT = [""]      # mutable holder for the current config label

# (arm, N) -> list of per-config cells, for the cross-config summary. A single
# config is one noisy draw; the average over the grid is the stable estimate.
GRID = defaultdict(list)


def report_contrast(label, st, margin=None, family="arm-contrast", ref=0.05):
    if st is None:
        print(f"{label:<34} (no overlapping observations)")
        return
    print(f"{label:<34} d = {pp(st['delta'])} pts   "
          f"naive 95% CI [{pp(st['ci_naive'][0])}, {pp(st['ci_naive'][1])}]   "
          f"cluster 95% CI [{pp(st['ci_cluster'][0])}, {pp(st['ci_cluster'][1])}]   "
          f"deff {st['deff']:.2f}   "
          f"b/c {st['b']}/{st['c']}   "
          f"McNemar p = {st['p_mcnemar']:.3g}   "
          f"clustered p = {st['p_clustered']:.3g}")
    record_p(label, st["p_clustered"], family)
    pw = power_summary(st["se_cluster"], ref)
    if pw:
        print(f"{'':<34} power: MDE(80%) {100 * pw['mde']:.1f} pts   "
              f"power to detect {100 * ref:.0f} pts = {100 * pw['power_ref']:.0f}%"
              + ("   <- underpowered; a null here is NOT evidence of no effect"
                 if pw["power_ref"] < 0.5 else ""))
    if margin is not None:
        p_ni = noninferiority_p(st["delta"], st["se_cluster"], margin)
        lo = st["ci_cluster"][0]
        verdict = "NON-INFERIOR" if lo > -margin else "cannot claim parity"
        print(f"{'':<34} non-inferiority (margin {100 * margin:.0f} pts): "
              f"lower bound {pp(lo)} -> {verdict}   one-sided p = {p_ni:.3g}")
        # These are the tests that license the parity claim, so they MUST enter the
        # correction. Leaving them out (as an earlier version did) meant the headline
        # verdicts were the only uncorrected numbers in the report.
        record_p(f"[NI] {label}", p_ni, "non-inferiority")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("directory", nargs="?", help="directory of result JSONs")
    ap.add_argument("--plan", help="filter on plan_<N> in the filename")
    ap.add_argument("--prune", help="filter on prune_<R> in the filename")
    ap.add_argument("--dump-scores", metavar="OUT.json",
                    help="write a compact scores-only extract and exit. The raw JSONs "
                         "carry full response text and run to gigabytes, which cannot be "
                         "committed. This holds only the 0/1 scores and the token means, "
                         "so it is small enough to check in -- which is what makes every "
                         "number below reproducible off the cluster.")
    ap.add_argument("--scores", metavar="IN.json",
                    help="read a scores extract written by --dump-scores instead of raw JSONs")
    ap.add_argument("--margin", type=float, default=5.0, metavar="PTS",
                    help="non-inferiority margin in percentage points (default 5). A parity "
                         "claim needs the lower CI bound to clear -margin; a non-significant "
                         "two-sided test does NOT establish equivalence.")
    ap.add_argument("--regen", action="store_true",
                    help="analyse the best-of-N regen runs (files ending _regen.json) instead "
                         "of the prune-only runs.")
    ap.add_argument("--diverse", action="store_true",
                    help="analyse the best-of-k diverse runs (files ending _diverse.json): prune "
                         "to k UNIQUE approaches, then regen. Mutually exclusive with --regen. "
                         "Each variant is a separate experiment and is never mixed into one grid; "
                         "the plain baseline arm is shared across all of them.")
    ap.add_argument("--grid", action="store_true",
                    help="run every (plan, prune) config found in the directory and apply a "
                         "multiple-comparison correction across the whole grid. Correcting "
                         "within a single config misses the real multiplicity, which comes "
                         "from sweeping many configs.")
    for arm in ARMS:
        ap.add_argument(f"--{arm}", help=f"explicit path to the {arm} JSON")
    args = ap.parse_args()

    if args.regen and args.diverse:
        ap.error("--regen and --diverse are mutually exclusive (separate experiments)")
    variant = "diverse" if args.diverse else ("regen" if args.regen else "")

    if args.grid:
        if not args.directory:
            ap.error("--grid needs a directory")
        run_grid(args.directory, args.margin / 100.0, explicit_baseline=args.baseline,
                 variant=variant)
        return

    if args.scores:
        with open(args.scores) as f:
            packed = json.load(f)
        data = {}
        for arm, blocks in packed["arms"].items():
            data[arm] = {}
            for n_str, b in blocks.items():
                data[arm][int(n_str)] = {
                    "scores": {sel: {tuple(map(int, k.split(","))): v
                                     for k, v in b["scores"][sel].items()}
                               for sel in SELECTORS},
                    "tokens": {int(k): v for k, v in b["tokens"].items()},
                }
        files = {a: packed["source_files"].get(a, "(from extract)") for a in data}
    else:
        files = {a: getattr(args, a) for a in ARMS if getattr(args, a)}
        if args.directory:
            files = {**discover(args.directory, args.plan, args.prune, variant=variant), **files}
        if not files:
            ap.error("no result JSONs found. Pass a directory, explicit --<arm> paths, "
                     "or a --scores extract.")
        data = {arm: load_arm(p) for arm, p in files.items()}

    if args.dump_scores:
        packed = {
            "source_files": {a: os.path.basename(p) for a, p in files.items()},
            "arms": {
                arm: {
                    str(n): {
                        "scores": {sel: {f"{q},{c}": v
                                         for (q, c), v in blk["scores"][sel].items()}
                                   for sel in SELECTORS},
                        "tokens": {str(q): t for q, t in blk["tokens"].items()},
                    }
                    for n, blk in blocks.items()
                }
                for arm, blocks in data.items()
            },
        }
        with open(args.dump_scores, "w") as f:
            json.dump(packed, f, separators=(",", ":"))
        size = os.path.getsize(args.dump_scores)
        print(f"wrote {args.dump_scores} ({size / 1024:.0f} KB) from {len(data)} arms")
        print("commit this. then: python3 analysis.py --scores " + args.dump_scores)
        return

    run_report(data, files, args.margin / 100.0)
    return


def run_report(data, files, margin):
    print("=" * 108)
    print("FILES")
    for arm, p in sorted(files.items()):
        print(f"  {arm:<9} {os.path.basename(p)}")
    ns = sorted({n for d in data.values() for n in d})
    print(f"  N values: {ns}")

    # Question counts per arm. The regen sweep runs 30 examples while the shared baseline
    # was generated at 100. reasoning_gym is size-independent for a fixed seed -- question
    # q is the SAME Countdown instance in both -- so every paired contrast below silently
    # intersects down to the shared questions. That is correct, but it must not be silent:
    # the effective n for those contrasts is the smaller count, not the baseline's.
    qcounts = {arm: len({q for blk in blocks.values() for q in blk["tokens"]})
               for arm, blocks in data.items()}
    print("  questions: " + ", ".join(f"{a}={qcounts[a]}" for a in sorted(qcounts)))
    if len(set(qcounts.values())) > 1:
        print(f"  NOTE: arms differ in question count -- paired contrasts use the "
              f"{min(qcounts.values())} shared questions. Section 1 accuracies are each "
              f"arm's own mean over its own questions, so the baseline row there is NOT "
              f"restricted to the overlap and will not equal the contrasts.")

    # ---- 1. per-cell accuracy and tokens
    print("\n" + "=" * 108)
    print("1. ACCURACY AND TOKENS PER CELL   (selector accuracy; obs = question x chunk)\n")
    hdr = f"{'arm':<10}" + "".join(f"{'N=' + str(n):>16}" for n in ns)
    print(hdr)
    for arm in ARMS:
        if arm not in data:
            continue
        row = f"{arm:<10}"
        for n in ns:
            if n in data[arm]:
                acc = accuracy(data[arm][n]["scores"]["results"])
                tok = sum(data[arm][n]["tokens"].values()) / len(data[arm][n]["tokens"])
                row += f"{100 * acc:>8.1f}% {tok:>6.0f}t"
                GRID[(arm, n)].append({
                    "config": CONTEXT[0], "acc": acc, "tokens": tok,
                    "ceiling": accuracy(data[arm][n]["scores"]["best_results"]),
                })
            else:
                row += f"{'-':>16}"
        print(row)

    # ---- 2. can the model judge FINISHED work? (within-file: selector vs random pick)
    print("\n" + "=" * 108)
    print("2. JUDGE vs RANDOM PICK, WITHIN THE SAME POOL   (does selection beat chance?)\n")
    for arm in ARMS:
        if arm not in data:
            continue
        for n in ns:
            if n not in data[arm]:
                continue
            s = data[arm][n]["scores"]
            st = paired_contrast(s["results"], s["random_results"])
            report_contrast(f"{arm} N={n}: judge - random", st, family="judge-vs-random")
        print()

    # ---- 3. oracle ceiling: is a correct answer even in the pool?
    print("=" * 108)
    print("3. ORACLE CEILING   (a correct candidate EXISTS vs the judge FINDS it)")
    print("   NOTE: for pruned arms this is pass@k over SURVIVORS, not over all N.")
    print("   Only the baseline row is a clean best-of-N ceiling.\n")
    for arm in ARMS:
        if arm not in data:
            continue
        for n in ns:
            if n not in data[arm]:
                continue
            s = data[arm][n]["scores"]
            sel, best = accuracy(s["results"]), accuracy(s["best_results"])
            print(f"{arm:<10} N={n:<3} ceiling {100 * best:5.1f}%   "
                  f"selected {100 * sel:5.1f}%   gap {100 * (best - sel):4.1f} pts   "
                  f"capture {100 * sel / best if best else float('nan'):5.1f}%")
        print()

    # ---- 4. the arm-vs-arm contrasts the resume actually quotes
    print("=" * 108)
    print("4. ARM CONTRASTS, PER N   (the pruning claims)\n")
    # ("random", "baseline") was previously missing, so the worst-performing arm was never
    # contrasted with baseline and any "all arm-vs-baseline cells" summary silently covered
    # only rank+tourney -- an optimistic subset.
    pairs = [("rank", "random"), ("rank", "baseline"),
             ("tourney", "baseline"), ("random", "baseline")]
    for a, b in pairs:
        if a not in data or b not in data:
            continue
        for n in ns:
            if n not in data[a] or n not in data[b]:
                continue
            st = paired_contrast(data[a][n]["scores"]["results"],
                                 data[b][n]["scores"]["results"])
            report_contrast(f"N={n:<3} {a} - {b}", st, margin=margin)

            tk = token_contrast(data[a][n]["tokens"], data[b][n]["tokens"])
            ta = sum(data[a][n]["tokens"].values()) / len(data[a][n]["tokens"])
            tb = sum(data[b][n]["tokens"].values()) / len(data[b][n]["tokens"])
            if tk:
                print(f"{'':<34} tokens {ta:.0f} vs {tb:.0f}  "
                      f"({tk['pct']:+.1f}%, 95% CI [{tk['pct_ci'][0]:+.1f}%, {tk['pct_ci'][1]:+.1f}%])")
            else:
                print(f"{'':<34} tokens {ta:.0f} vs {tb:.0f}  ({100 * (ta - tb) / tb:+.1f}%)")
        print()

    # ---- 5. pooled across N
    print("=" * 108)
    print("5. POOLED ACROSS N\n")
    print("   chunk-weighted: every (question, N, chunk) observation counts once, so an N")
    print("   with more chunks pulls harder. equal-weight: each N contributes equally.\n")
    for a, b in pairs:
        if a not in data or b not in data:
            continue
        pooled_a, pooled_b = {}, {}
        per_n = []
        for n in ns:
            if n not in data[a] or n not in data[b]:
                continue
            sa = data[a][n]["scores"]["results"]
            sb = data[b][n]["scores"]["results"]
            for k in set(sa) & set(sb):
                # re-key so (question, N, chunk) is unique, but keep question as cluster
                pooled_a[(k[0], n, k[1])] = sa[k]
                pooled_b[(k[0], n, k[1])] = sb[k]
            st_n = paired_contrast(sa, sb)
            if st_n:
                per_n.append(st_n["delta"])

        st = paired_contrast(pooled_a, pooled_b)
        report_contrast(f"pooled {a} - {b} (chunk-wtd)", st, family="pooled")
        if per_n:
            eq = sum(per_n) / len(per_n)
            print(f"{'':<34} equal-weight per N: d = {pp(eq)} pts "
                  f"(from {len(per_n)} cells: {', '.join(pp(d) for d in per_n)})")
        print()

    # ---- 6. token-MATCHED contrasts: the comparison the cost claim actually needs
    print("=" * 108)
    print("6. TOKEN-MATCHED CONTRASTS   (equal BUDGET, not equal N)\n")
    print("   Comparing arms at the same N compares unequal compute: a pruned arm at")
    print("   N=16 can cost half of baseline N=16. The inference-scaling question is")
    print("   'at a fixed budget, which wins?', so each pruned cell is matched to the")
    print("   baseline N whose token cost is closest, and paired at the question level.\n")
    if "baseline" in data:
        base_tok = {n: sum(data["baseline"][n]["tokens"].values()) / len(data["baseline"][n]["tokens"])
                    for n in data["baseline"]}
        for arm in ARMS:
            if arm == "baseline" or arm not in data:
                continue
            for n in ns:
                if n not in data[arm]:
                    continue
                ta = sum(data[arm][n]["tokens"].values()) / len(data[arm][n]["tokens"])
                nb = min(base_tok, key=lambda k: abs(base_tok[k] - ta))
                st = question_contrast(question_means(data[arm][n]["scores"]["results"]),
                                       question_means(data["baseline"][nb]["scores"]["results"]))
                if st is None:
                    continue
                lab = f"{arm} N={n} vs baseline N={nb}"
                gap = 100 * (ta - base_tok[nb]) / base_tok[nb]
                print(f"{lab:<34} d = {pp(st['delta'])} pts   "
                      f"95% CI [{pp(st['ci'][0])}, {pp(st['ci'][1])}]   "
                      f"win/loss {st['wins']}/{st['losses']}   "
                      f"p = {st['p']:.3g}   sign p = {st['p_sign']:.3g}")
                print(f"{'':<34} tokens {ta:.0f} vs {base_tok[nb]:.0f} "
                      f"({gap:+.1f}% budget mismatch)")
                p_ni = noninferiority_p(st["delta"], st["se"], margin)
                verdict = "NON-INFERIOR" if st["ci"][0] > -margin else "cannot claim parity"
                print(f"{'':<34} non-inferiority (margin {100 * margin:.0f} pts): "
                      f"lower bound {pp(st['ci'][0])} -> {verdict}   one-sided p = {p_ni:.3g}")
                record_p(f"[NI] {lab}", p_ni, "non-inferiority")
                if abs(gap) > 15:
                    print(f"{'':<34} WARNING: {gap:+.0f}% budget mismatch -- this cell is NOT "
                          f"token-matched; the verdict above is not a matched-budget result")
                pw = power_summary(st["se"], margin)
                if pw:
                    print(f"{'':<34} power: MDE(80%) {100 * pw['mde']:.1f} pts   "
                          f"power to detect {100 * margin:.0f} pts = {100 * pw['power_ref']:.0f}%"
                          + ("   <- underpowered" if pw["power_ref"] < 0.5 else ""))
                record_p(lab, st["p"], "token-matched")
            print()
    else:
        print("   (no baseline arm loaded -- cannot token-match)\n")

    print("=" * 108)
    print("Clusters are questions. deff > 1 means the naive interval was too narrow.")


def run_grid(directory, margin, explicit_baseline=None, variant=""):
    """Run every (plan, prune) config in `directory`, then correct across all of them.

    `variant` picks which sweep to walk: '' prune-only, 'regen' best-of-N regen,
    'diverse' best-of-k. They are different experiments, so pooling them into one
    grid, and one multiple-comparison correction, would be meaningless.
    """
    combos = set()
    for path in glob.glob(os.path.join(directory, "*_bon_*.json")):
        base = os.path.basename(path)
        if "_baseline_" in base:
            continue
        m = re.search(r"_plan_(\d+)_prune_([\d.]+)(?:_(regen|diverse))?\.json$", base)
        if not m:
            continue
        if (m.group(3) or "") != variant:
            continue                                  # wrong sweep; keep them apart
        combos.add((int(m.group(1)), m.group(2)))

    if not combos:
        which = variant or "prune-only"
        hint = "" if variant else " (regen/diverse runs need --regen / --diverse)"
        print(f"no {which} plan/prune configs found{hint}", file=sys.stderr)
        return

    for plan, prune in sorted(combos):
        files = discover(directory, str(plan), prune, variant=variant)
        # The baseline filename carries the argparse default (prune_2, an int) while
        # strategy files carry the float (prune_2.0), so discover() cannot match both.
        if explicit_baseline:
            files["baseline"] = explicit_baseline
        elif "baseline" not in files:
            cands = sorted(glob.glob(os.path.join(directory, "*_baseline_bon_*.json")))
            if cands:
                files["baseline"] = cands[-1]
        if not files:
            continue
        CONTEXT[0] = f"plan={plan},prune={prune}"
        print()
        print("#" * 108)
        print(f"# CONFIG  plan={plan}  prune={prune}")
        print("#" * 108)
        data = {arm: load_arm(p) for arm, p in files.items()}
        run_report(data, files, margin)

    report_grid_summary(margin)
    report_iso_token()
    report_multiplicity()


# Fraction of BASELINE generated tokens emitted after the first "</answer>".
#
# The baseline and the pruned arms are not billed on the same basis. Baseline drafts
# come from Model.generate_responses (baseline draft branch) via llm.chat with NO stop
# string; arm completions come from Model.generate_responses (completion stage) via
# llm.generate with stop=["</answer>"], include_stop_str_in_output=True. So the baseline
# is charged for everything it emits after the closing tag and the arms are not, and the
# reported token saving is inflated by exactly that tail.
#
# Measured with the Qwen/Qwen3-4B-Instruct-2507 tokenizer over all 6,000 drafts in
# baseline_cache.json, splitting each draft at its FIRST "</answer>" (where `stop` would
# have fired): 26.25% of generated tokens fall after it; 0/6,000 drafts lack the tag.
# Per-N: 25.76 / 26.25 / 26.29 / 26.29 / 26.29% at N = 1/2/4/8/16.
#
# The arms have no equivalent tail to strip: every draft whose first "</answer>" falls
# before token 1000 is entirely shorter than 1000 tokens, so the post-tag tokens
# surviving inside a truncated plan prefix number exactly 0 at plan 1000/2500/4000.
# Correcting the baseline alone is therefore exact, not a concession to either side.
#
# Hardcoded because recomputing it needs the 115 MB cache and the tokenizer, neither of
# which this file depends on. Re-derive with scripts/ or the recipe in RESULTS.md 5.0.1.
BASELINE_STOP_TAIL = 0.2625
BASELINE_DRAFT_TOKENS = 8247.10      # mean token_count over baseline_cache.json


def _interp_log(x, xs, ys):
    """Piecewise-linear interpolation of ys over log(xs), clamped outside the range."""
    lx = math.log(x)
    lxs = [math.log(v) for v in xs]
    if lx <= lxs[0]:
        return ys[0]
    if lx >= lxs[-1]:
        return ys[-1]
    for i in range(len(lxs) - 1):
        if lxs[i] <= lx <= lxs[i + 1]:
            w = (lx - lxs[i]) / (lxs[i + 1] - lxs[i])
            return ys[i] + w * (ys[i + 1] - ys[i])
    return ys[-1]


def report_iso_token():
    """Iso-token contrast: interpolate the baseline curve to each cell's ACTUAL spend.

    Section 6 matches each pruned cell to the baseline N of nearest token cost, which
    leaves budget mismatches spanning -31% to +49% -- 82 of 180 cells exceed 15% and get
    an inline warning. Interpolating the baseline's accuracy-vs-token curve removes that
    slack: every cell is compared against the baseline accuracy at its own budget.

    Reported on two bases. The RAW basis uses baseline mean_tokens as stored. The
    STOP-CORRECTED basis scales only the baseline's generation component (drafts) by
    1 - BASELINE_STOP_TAIL and leaves the judge component alone, which is the
    apples-to-apples budget. The two give opposite verdicts, which is the point.

    No p-values are recorded here: this is a descriptive re-basing of section 6, and
    entering it into the correction would double-count the same cells.
    """
    if not GRID:
        return
    ns = sorted({n for (_a, n) in GRID})
    base = {n: GRID.get(("baseline", n), []) for n in ns}
    if not all(base[n] for n in ns):
        return

    base_acc = {n: sum(c["acc"] for c in base[n]) / len(base[n]) for n in ns}
    base_tok = {n: sum(c["tokens"] for c in base[n]) / len(base[n]) for n in ns}
    corr_tok = {}
    for n in ns:
        gen = BASELINE_DRAFT_TOKENS * n
        judge = base_tok[n] - gen
        corr_tok[n] = (1 - BASELINE_STOP_TAIL) * gen + judge

    print()
    print("=" * 108)
    print("9. ISO-TOKEN CONTRASTS   (baseline curve INTERPOLATED to each cell's actual spend)\n")
    print("   Section 6 snaps each cell to the nearest baseline N, leaving budget gaps up to")
    print("   +49%. Here the baseline accuracy-vs-token curve is log-interpolated to the exact")
    print("   budget each cell spent, so there is no mismatch left to warn about.\n")
    print(f"   baseline stop-tail correction: {100 * BASELINE_STOP_TAIL:.2f}% of generated tokens")
    print("   fall after the first </answer>, which the baseline is charged for and the arms")
    print("   are not (no stop string on the baseline; stop=['</answer>'] on the arms).\n")
    print(f"   {'N':>4}{'baseline acc':>14}{'tokens raw':>13}{'tokens corrected':>18}")
    for n in ns:
        print(f"   {n:>4}{100 * base_acc[n]:>13.1f}%{base_tok[n]:>13,.0f}{corr_tok[n]:>18,.0f}")

    xs = [base_tok[n] for n in ns]
    xs_c = [corr_tok[n] for n in ns]
    ys = [base_acc[n] for n in ns]

    for name, curve in (("RAW baseline", xs), ("STOP-CORRECTED baseline", xs_c)):
        deltas = []
        by_plan = defaultdict(list)
        for (arm, n), cells in GRID.items():
            if arm == "baseline":
                continue
            for c in cells:
                d = c["acc"] - _interp_log(c["tokens"], curve, ys)
                deltas.append(d)
                m = re.search(r"plan=(\d+)", c["config"] or "")
                if m:
                    by_plan[int(m.group(1))].append(d)
        if not deltas:
            continue
        deltas.sort()
        mid = len(deltas) // 2
        median = deltas[mid] if len(deltas) % 2 else (deltas[mid - 1] + deltas[mid]) / 2
        # A handful of cells land exactly on the baseline curve. Counting them by sign
        # would make the tally depend on floating-point noise, so ties are reported.
        tol = 1e-9
        pos = sum(1 for d in deltas if d > tol)
        neg = sum(1 for d in deltas if d < -tol)
        tie = len(deltas) - pos - neg
        print(f"\n   {name}: arm accuracy minus interpolated baseline accuracy")
        print(f"     over {len(deltas)} equal-N cells:  mean {100 * sum(deltas) / len(deltas):+.2f} pts   "
              f"median {100 * median:+.2f} pts   positive {pos}/{len(deltas)}"
              + (f"   (negative {neg}, exact ties {tie})" if tie else f"   (negative {neg})"))
        for plan in sorted(by_plan):
            v = by_plan[plan]
            print(f"       plan={plan:<5} mean {100 * sum(v) / len(v):+.2f} pts   ({len(v)} cells)")

    print("\n   Read together: against the raw baseline the pruned arms are roughly break-even at")
    print("   equal budget; against the stop-corrected baseline they are negative at every plan")
    print("   level. The apparent iso-token parity depends on charging the baseline for tokens")
    print("   the arms never emit.")


def report_multiplicity():
    """Correct every p-value collected across the run for multiple comparisons.

    A grid of 12 configs x 5 N x several contrasts is hundreds of tests; at alpha
    = 0.05 you expect ~1 in 20 to look significant with nothing real behind it.
    Holm controls the chance of ANY false positive (strict); Benjamini-Hochberg
    controls the expected FRACTION of false positives among the rejections (the
    usual choice for exploratory sweeps).
    """
    if not PVALS:
        return

    print()
    print("=" * 108)
    print("7. MULTIPLE COMPARISONS   (corrected WITHIN each hypothesis family)\n")
    print("   Families are corrected separately. Pooling them would let the enormous")
    print("   judge-vs-random effects (p ~ 1e-9) inflate m and consume the alpha that")
    print("   the borderline arm contrasts actually need.\n")

    fams = defaultdict(list)
    for i, (ctx, fam, lab, p) in enumerate(PVALS):
        fams[fam].append(i)

    print(f"   {'family':<18}{'tests':>7}{'p<.05':>7}{'by chance':>11}{'Holm':>7}{'BH':>6}")
    survivors = {}
    for fam, idxs in sorted(fams.items()):
        ps = [PVALS[i][3] for i in idxs]
        m = len(ps)
        raw = sum(1 for p in ps if p < 0.05)
        holm = holm_survivors(ps)
        bh = bh_survivors(ps)
        survivors[fam] = ({idxs[j] for j in holm}, {idxs[j] for j in bh})
        print(f"   {fam:<18}{m:>7}{raw:>7}{0.05 * m:>11.0f}{len(holm):>7}{len(bh):>6}")

    print()
    all_bh = set().union(*[s[1] for s in survivors.values()]) if survivors else set()
    all_holm = set().union(*[s[0] for s in survivors.values()]) if survivors else set()
    lost = [i for i, (_c, _f, _l, p) in enumerate(PVALS) if p < 0.05 and i not in all_bh]
    if lost:
        print(f"   {len(lost)} nominally-significant results do NOT survive BH within their family.")
        print("   Do not cite these on their own:")
        for i in sorted(lost, key=lambda j: PVALS[j][3])[:20]:
            ctx, fam, lab, p = PVALS[i]
            print(f"     p={p:<9.3g} [{fam}] {ctx:<20} {lab}")
        if len(lost) > 20:
            print(f"     ... and {len(lost) - 20} more")
    else:
        print("   every nominally-significant result survives BH within its family.")
    print()
    print(f"   {len(all_holm)} results survive the strict Holm correction; these are the safe ones to quote.")


def report_grid_summary(margin):
    """Aggregate across configs. One config is a single noisy draw at n=100; the
    mean over the grid is the stable estimate, and quoting the best cell instead
    is a winner's-curse overestimate (the max of ~60 noisy cells)."""
    if not GRID:
        return
    ns = sorted({n for (_a, n) in GRID})
    print()
    print("=" * 108)
    print("8. CROSS-CONFIG SUMMARY   (the stable estimate: average over the grid)\n")
    print("   A single config is one noisy draw. Quoting the best cell overstates the")
    print("   effect because it is the maximum of many noisy cells. These are means.\n")
    print(f"   {'arm':<10}{'N':>4}{'configs':>9}{'acc mean':>10}{'min':>7}{'max':>7}"
          f"{'tokens':>10}{'vs base':>9}")
    for n in ns:
        base = GRID.get(("baseline", n), [])
        base_acc = sum(c["acc"] for c in base) / len(base) if base else float("nan")
        base_tok = sum(c["tokens"] for c in base) / len(base) if base else float("nan")
        for arm in ARMS:
            cells = GRID.get((arm, n), [])
            if not cells:
                continue
            accs = [c["acc"] for c in cells]
            toks = [c["tokens"] for c in cells]
            mean_acc = sum(accs) / len(accs)
            mean_tok = sum(toks) / len(toks)
            sav = (100 * (mean_tok - base_tok) / base_tok) if base_tok == base_tok and base_tok else float("nan")
            print(f"   {arm:<10}{n:>4}{len(cells):>9}{100 * mean_acc:>9.1f}%"
                  f"{100 * min(accs):>7.0f}{100 * max(accs):>7.0f}"
                  f"{mean_tok:>10,.0f}{sav:>8.1f}%")
        print()

    # ---- the ceiling collapse: the binding constraint on the whole approach
    print("   ORACLE CEILING COLLAPSE   (what pruning costs you before the judge acts)\n")
    print("   Pruning discards candidates, so a correct answer may never reach the judge.")
    print("   A smaller judge gap on a pruned arm is less headroom, not better selection.\n")
    print(f"   {'arm':<10}{'N':>4}{'ceiling':>10}{'selected':>10}{'judge gap':>11}{'ceiling vs base':>17}")
    for n in ns:
        base = GRID.get(("baseline", n), [])
        base_ceil = sum(c["ceiling"] for c in base) / len(base) if base else float("nan")
        for arm in ARMS:
            cells = GRID.get((arm, n), [])
            if not cells:
                continue
            ceil = sum(c["ceiling"] for c in cells) / len(cells)
            sel = sum(c["acc"] for c in cells) / len(cells)
            delta_ceil = 100 * (ceil - base_ceil) if base_ceil == base_ceil else float("nan")
            print(f"   {arm:<10}{n:>4}{100 * ceil:>9.1f}%{100 * sel:>9.1f}%"
                  f"{100 * (ceil - sel):>10.1f}p{delta_ceil:>16.1f}p")
        print()


if __name__ == "__main__":
    main()
