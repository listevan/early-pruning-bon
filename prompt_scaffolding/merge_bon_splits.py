#!/usr/bin/env python3
"""Recombine the bon-split sweep outputs into one JSON per (config, arm).

job_sweep_n100.slurm runs best_of_ns in three groups per config -- {16}, {8}, {4,2,1} --
each writing its own result JSON (keyed by the bons it evaluated). This unions those
bon-keyed dicts back into a single file per (plan, prune, arm) that looks exactly like a
one-shot run, so analysis.py / plot_results.py need no changes.

Each group JSON's bon entry is already complete (computed over all 100 examples), so this
is a plain key-union -- no per-example concatenation or recomputation.

Usage:  python3 merge_bon_splits.py [DIR] [-o OUTDIR]   (DIR default: current directory)

In the run-directory layout the split pieces live in `<run>/partials/` and the merged
files belong one level up, next to the baseline, so that a plain
`<run>/*strat_CompletionStrategy*.json` glob sees each config exactly once:

    python3 merge_bon_splits.py runs/<run>/partials -o runs/<run>
"""
import argparse
import glob
import json
import os
import re
import sys

ARMS = ["rank", "random", "tourney"]


def parse(path):
    b = os.path.basename(path)
    m = re.search(r"_(rank|random|tourney)_bon_([\d_]+)_strat_.*_plan_(\d+)_prune_([\d.]+)(_regen|_diverse)?\.json$", b)
    if not m:
        return None
    return {"arm": m.group(1), "bons": m.group(2), "plan": m.group(3),
            "prune": m.group(4), "variant": m.group(5) or "", "path": path}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("directory", nargs="?", default=".", help="directory of split result JSONs")
    ap.add_argument("-o", "--out", help="where to write merged files (default: DIR)")
    args = ap.parse_args()

    directory = args.directory
    outdir = args.out or directory
    os.makedirs(outdir, exist_ok=True)
    files = [p for p in (parse(f) for f in glob.glob(os.path.join(directory, "*_bon_*.json"))) if p]

    # Group by (arm, plan, prune, VARIANT) so prune-only / regen / diverse sweeps are merged
    # separately. Skip already-merged files (the full 1_2_4_8_16 span) and any "merged_" file.
    groups = {}
    for f in files:
        if os.path.basename(f["path"]).startswith("merged_") or f["bons"] == "1_2_4_8_16":
            continue
        groups.setdefault((f["arm"], f["plan"], f["prune"], f["variant"]), []).append(f["path"])

    if not groups:
        print("No bon-split files to merge.", file=sys.stderr)
        return

    for (arm, plan, prune, variant), paths in sorted(groups.items()):
        merged = {}
        for p in sorted(paths):
            with open(p) as fh:
                d = json.load(fh)
            for bon, block in d.items():
                if bon in merged:
                    print(f"  WARNING: bon={bon} seen twice for {arm} plan={plan}; keeping first",
                          file=sys.stderr)
                    continue
                merged[bon] = block

        bons_sorted = sorted(merged, key=int)
        if not bons_sorted:
            continue
        bons_str = "_".join(bons_sorted)
        # name it like a normal one-shot run (carry the same variant suffix) so
        # discovery/plotting treat it identically to a single-process sweep.
        out = os.path.join(
            outdir,
            f"merged_{arm}_bon_{bons_str}_strat_CompletionStrategy_plan_{plan}_prune_{prune}{variant}.json")
        with open(out, "w") as fh:
            json.dump(merged, fh, indent=4)
        vlabel = variant or "(prune-only)"
        print(f"merged {arm} plan={plan} prune={prune} {vlabel}: bons {bons_sorted} -> {os.path.basename(out)}")


if __name__ == "__main__":
    main()
