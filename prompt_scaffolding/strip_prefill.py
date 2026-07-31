#!/usr/bin/env python3
"""Put a result JSON back on a DECODE-ONLY token basis.

WHY
---
Prompt (prefill) tokens were folded into `mean_tokens` by a since-removed patch. Charging
them is not obviously right: vLLM has prefix caching on by default, so the k continuation
requests of one question share their scaffold and only the first recomputes it -- the
charged figure was a logical upper bound, not measured work. Prefill is also one parallel
forward pass against decode's one serial pass per token, so summing the two treats
non-fungible things as fungible.

The pipeline now counts decode only, and this script brings already-written results onto
that same basis so old and new files can share a plot.

WHAT IT DOES, per best-of-N block
---------------------------------
    mean_tokens          <- decode_mean_tokens          (the sampled tokens alone)
    tourney_mean_tokens  <- tourney_decode_mean_tokens
    std_tokens             unchanged -- it was ALWAYS decode-only, so this also repairs the
                           mean/std mismatch the patch left behind
    decode_* / prefill_*   deleted

Idempotent: a file with no decode_/prefill_ keys is already decode-only and is left alone,
so it is safe to re-run over a whole tree.

HARD LINKS
----------
Rewrites the existing inode rather than replacing the file, so a result JSON that is
hardlinked into several run directories (the shared baseline is) stays consistent across
all of its names instead of silently diverging. Link counts are reported.

USAGE
-----
    python3 strip_prefill.py FILE_OR_DIR [FILE_OR_DIR ...]
    python3 strip_prefill.py --dry-run runs/archive        # show what would change
"""
import argparse
import glob
import json
import os
import sys

DERIVED = ("decode_mean_tokens", "prefill_mean_tokens",
           "tourney_decode_mean_tokens", "tourney_prefill_mean_tokens")


def decode_only(block):
    """Rewrite one best-of-N block in place. Returns (changed, note) for reporting."""
    changed = False
    for holder in [block.get("dataset_metrics", {})] + list(block.get("prompt_metrics", [])):
        if not any(k in holder for k in DERIVED):
            continue
        # Prefer the recorded decode subtotal; fall back to total - prefill if only the
        # prefill half survived. Never derive from mean_tokens alone -- that is the value
        # being corrected.
        if "decode_mean_tokens" in holder:
            holder["mean_tokens"] = holder["decode_mean_tokens"]
        elif "prefill_mean_tokens" in holder:
            holder["mean_tokens"] = holder["mean_tokens"] - holder["prefill_mean_tokens"]
        if "tourney_mean_tokens" in holder:
            if "tourney_decode_mean_tokens" in holder:
                holder["tourney_mean_tokens"] = holder["tourney_decode_mean_tokens"]
            elif "tourney_prefill_mean_tokens" in holder:
                holder["tourney_mean_tokens"] -= holder["tourney_prefill_mean_tokens"]
        for k in DERIVED:
            holder.pop(k, None)
        changed = True
    return changed


def process(path, dry_run):
    with open(path) as fh:
        try:
            data = json.load(fh)
        except json.JSONDecodeError:
            print(f"  skip (not JSON): {path}", file=sys.stderr)
            return None
    if not isinstance(data, dict) or not data:
        return None

    before = {}
    changed = False
    for bon, block in data.items():
        if not isinstance(block, dict) or "dataset_metrics" not in block:
            return None                                    # not a result file
        before[bon] = block["dataset_metrics"].get("mean_tokens")
        changed |= decode_only(block)

    if not changed:
        print(f"  already decode-only: {os.path.basename(path)}")
        return False

    links = os.stat(path).st_nlink
    tag = f" [{links} hard links -> all updated]" if links > 1 else ""
    deltas = ", ".join(
        f"N={bon}: {before[bon]:,.0f} -> {data[bon]['dataset_metrics']['mean_tokens']:,.0f}"
        for bon in sorted(data, key=int))
    print(f"  {'WOULD STRIP' if dry_run else 'stripped'}: {os.path.basename(path)}{tag}\n    {deltas}")

    if not dry_run:
        # Truncate the existing inode so every hard link to this file sees the change.
        with open(path, "w") as fh:
            json.dump(data, fh, indent=4)
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("targets", nargs="+", help="result JSONs, or directories to search")
    ap.add_argument("--dry-run", action="store_true", help="report without writing")
    args = ap.parse_args()

    files = []
    for t in args.targets:
        if os.path.isdir(t):
            files += sorted(glob.glob(os.path.join(t, "**", "*_bon_*.json"), recursive=True))
        else:
            files.append(t)
    # One inode may carry several names; strip it once.
    seen, unique = set(), []
    for f in files:
        key = os.stat(f).st_ino
        if key not in seen:
            seen.add(key)
            unique.append(f)

    print(f"{len(unique)} distinct result file(s) from {len(files)} path(s)\n")
    stripped = sum(1 for f in unique if process(f, args.dry_run) is True)
    print(f"\n{stripped} file(s) {'would be' if args.dry_run else ''} put on a decode-only basis; "
          f"{len(unique) - stripped} already were or were skipped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
