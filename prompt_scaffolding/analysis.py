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
          { "mean_tokens": float,
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

No third-party dependencies. Standard library only.
"""

import argparse
import glob
import json
import math
import os
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


def discover(directory, plan, prune):
    """Find one file per arm in a directory, optionally filtered by plan/prune."""
    found = {}
    for arm in ARMS:
        pat = os.path.join(directory, f"*_{arm}_bon_*.json")
        cands = sorted(glob.glob(pat))
        if plan is not None:
            cands = [c for c in cands if f"_plan_{plan}_" in c]
        if prune is not None:
            cands = [c for c in cands if c.endswith(f"_prune_{prune}.json")]
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


def accuracy(scores):
    """Plain mean over observations."""
    return sum(scores.values()) / len(scores) if scores else float("nan")


# ---------------------------------------------------------------- reporting

def pp(x):
    """Format a proportion as percentage points."""
    return f"{100 * x:+.1f}" if x == x else "  n/a"


def report_contrast(label, st):
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
    for arm in ARMS:
        ap.add_argument(f"--{arm}", help=f"explicit path to the {arm} JSON")
    args = ap.parse_args()

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
            files = {**discover(args.directory, args.plan, args.prune), **files}
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

    print("=" * 108)
    print("FILES")
    for arm, p in sorted(files.items()):
        print(f"  {arm:<9} {os.path.basename(p)}")
    ns = sorted({n for d in data.values() for n in d})
    print(f"  N values: {ns}")

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
            report_contrast(f"{arm} N={n}: judge - random", st)
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
    pairs = [("rank", "random"), ("rank", "baseline"), ("tourney", "baseline")]
    for a, b in pairs:
        if a not in data or b not in data:
            continue
        for n in ns:
            if n not in data[a] or n not in data[b]:
                continue
            st = paired_contrast(data[a][n]["scores"]["results"],
                                 data[b][n]["scores"]["results"])
            report_contrast(f"N={n:<3} {a} - {b}", st)

            ta = sum(data[a][n]["tokens"].values()) / len(data[a][n]["tokens"])
            tb = sum(data[b][n]["tokens"].values()) / len(data[b][n]["tokens"])
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
        report_contrast(f"pooled {a} - {b} (chunk-wtd)", st)
        if per_n:
            eq = sum(per_n) / len(per_n)
            print(f"{'':<34} equal-weight per N: d = {pp(eq)} pts "
                  f"(from {len(per_n)} cells: {', '.join(pp(d) for d in per_n)})")
        print()

    print("=" * 108)
    print("Clusters are questions. deff > 1 means the naive interval was too narrow.")


if __name__ == "__main__":
    main()
