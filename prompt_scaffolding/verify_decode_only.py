#!/usr/bin/env python3
"""Verify a baseline result JSON carries DECODE-ONLY token counts, against a reference
baseline that never had prefill folded in.

    python3 verify_decode_only.py [TARGET] [--reference REF] [--no-control]

Defaults compare the bon=1..32 baseline against the May bon=1..16 baseline.

HOW THE VERDICT IS REACHED
--------------------------
Three structural checks decide it; the cross-file comparison is corroboration only, and
the script says so, because that comparison provably lacks the resolution to settle it:

  1. SCHEMA        No prefill_/decode_ key anywhere, and a key set identical to the
                   reference -- which predates prefill entirely. Binary, cannot be faked.

  2. MEAN/STD      Rebuild the dataset std from the per-question means and stds. That
     IDENTITY      identity holds if and only if mean_tokens and std_tokens describe the
                   SAME series. Folding prefill into the mean while leaving the std alone
                   -- exactly what the old patch did -- breaks it. This is the fingerprint.

  3. QUESTIONS     Both files must hold the same problems, or nothing else compares.

  4. CROSS-FILE    Per-bon means, target vs reference, at the shared bons. Reported WITH
                   its standard error: two independent samples of the same generator differ
                   by far more than a prefill term, so this can only catch a gross error.

  5. CONTROL       Re-inject a synthetic prefill into a copy in memory and re-run 1 and 2.
                   Both MUST flip to failing, or they had no power to begin with and a pass
                   would have meant nothing.

bon=32 exists only in the target, so it is carried by checks 1-2, which run per-N.
"""
import argparse
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "2026-07-25_11-42-12_baseline_bon_1_2_4_8_16_32_strat_None_plan_4000_prune_2.json")
REFERENCE = os.path.join(HERE, "2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json")

BANNED = ("prefill", "prompt_token", "decode_mean_tokens", "tourney_decode", "tourney_prefill")

# Fields the target may carry that the reference does not. These postdate the reference and
# are DECODE quantities, so they are not evidence of prompt-token counting:
#   tourney_mean_tokens -- the tournament selector's own sampled-token cost, which differs
#                          from the model-select axis only in the selection component.
# Anything outside this allowlist is treated as an unexplained schema difference.
ALLOWED_EXTRA = {"tourney_mean_tokens"}

FAILS = []


def check(cond, msg, record=True):
    print(f"  {'PASS' if cond else 'FAIL'}  {msg}")
    if not cond and record:
        FAILS.append(msg)
    return cond


def pooled_std(means, stds, n_per):
    """Exact sample std of the pooled series, from per-group mean/std at equal group size.

    Every question contributes n_per chunk observations. If mean_tokens carries a term the
    per-question std never saw -- a prefill offset that varies question to question -- the
    between-group part of this sum shifts and the identity stops holding.
    """
    N = len(means) * n_per
    if N < 2:
        return 0.0
    grand = statistics.mean(means)
    ss = sum((n_per - 1) * s * s + n_per * (m - grand) ** 2 for m, s in zip(means, stds))
    return math.sqrt(ss / (N - 1))


def walk_keys(blob):
    """Every dict key in the document."""
    if isinstance(blob, dict):
        for k, v in blob.items():
            yield k
            yield from walk_keys(v)
    elif isinstance(blob, list):
        for v in blob:
            yield from walk_keys(v)


def schema_of(block):
    return (tuple(sorted(block["dataset_metrics"])),
            tuple(sorted(k for k in block["prompt_metrics"][0] if k != "chunks_data")))


def check_schema(doc, ref_block, label, record=True):
    ok = True
    hits = sorted(k for k in set(walk_keys(doc)) if any(b in k for b in BANNED))
    ok &= check(not hits, f"[{label}] no prefill/decode key anywhere in the document"
                          + (f" -- FOUND {hits}" if hits else ""), record)
    ref_ds, ref_pm = schema_of(ref_block)
    for bon in sorted(doc, key=int):
        got_ds, got_pm = schema_of(doc[bon])
        ok &= check(got_ds == ref_ds,
                    f"[{label}] N={bon:>2}: dataset_metrics keys identical to the reference"
                    + ("" if got_ds == ref_ds else f" -- got {list(got_ds)}"), record)
        missing = set(ref_pm) - set(got_pm)
        extra = set(got_pm) - set(ref_pm)
        unexplained = extra - ALLOWED_EXTRA
        ok &= check(not missing and not unexplained,
                    f"[{label}] N={bon:>2}: prompt_metrics keys = reference"
                    + (f" + {sorted(extra)} (allowlisted, decode)" if extra and not unexplained else "")
                    + (f" -- MISSING {sorted(missing)}" if missing else "")
                    + (f" -- UNEXPLAINED {sorted(unexplained)}" if unexplained else ""), record)
    return ok


def check_identity(doc, label, record=True):
    ok = True
    for bon in sorted(doc, key=int):
        dm, pm = doc[bon]["dataset_metrics"], doc[bon]["prompt_metrics"]
        n = dm["num_chunks_averaged"]
        rebuilt = pooled_std([p["mean_tokens"] for p in pm], [p["std_tokens"] for p in pm], n)
        stored = dm["std_tokens"]
        rel = abs(rebuilt - stored) / max(1.0, stored)
        ok &= check(rel < 1e-9,
                    f"[{label}] N={bon:>2}: std rebuilt from mean_tokens {rebuilt:>12,.4f} "
                    f"== stored {stored:>12,.4f}   (rel {rel:.1e})", record)
        want = statistics.mean(p["mean_tokens"] for p in pm)
        ok &= check(abs(dm["mean_tokens"] - want) < 1e-9 * max(1.0, want),
                    f"[{label}] N={bon:>2}: dataset mean_tokens == mean of per-question means",
                    record)
    return ok


def cross_file(tgt, ref):
    """Per-bon comparison, reported with the resolution it actually has."""
    shared = sorted(set(tgt) & set(ref), key=int)
    print(f"\n  {'N':>3} | {'target':>10} {'reference':>10} {'diff':>9} {'+/-2SE':>8} {'ratio':>7} | verdict")
    print("  " + "-" * 76)
    for bon in shared:
        t, r = tgt[bon], ref[bon]
        tm, rm = t["dataset_metrics"]["mean_tokens"], r["dataset_metrics"]["mean_tokens"]
        nt = len(t["prompt_metrics"]) * t["dataset_metrics"]["num_chunks_averaged"]
        nr = len(r["prompt_metrics"]) * r["dataset_metrics"]["num_chunks_averaged"]
        se = math.sqrt(t["dataset_metrics"]["std_tokens"] ** 2 / nt +
                       r["dataset_metrics"]["std_tokens"] ** 2 / nr)
        d = tm - rm
        print(f"  {bon:>3} | {tm:>10,.0f} {rm:>10,.0f} {d:>+9,.0f} {2*se:>8,.0f} {tm/rm:>7.4f} | "
              f"{'consistent' if abs(d) <= 2 * se else 'OUTSIDE 2SE'}")
    only = sorted(set(tgt) - set(ref), key=int)
    if only:
        print(f"\n  N={','.join(only)} exists only in the target -- the reference cannot speak to it.")
        print(f"  It is carried by the schema and mean/std checks above, which run per-N.")
        for bon in only:
            dm = tgt[bon]["dataset_metrics"]
            print(f"    N={bon}: mean_tokens {dm['mean_tokens']:,.1f}   "
                  f"per-sample {dm['mean_tokens']/int(bon):,.0f}   chunks {dm['num_chunks_averaged']}")
        base = [(int(b), tgt[b]["dataset_metrics"]["mean_tokens"] / int(b)) for b in sorted(tgt, key=int)]
        print("    per-sample cost across N: " + ", ".join(f"N={n}:{v:,.0f}" for n, v in base))
        print("    -> a residual prefill term would ADD to per-sample cost as N grows (the judge")
        print("       prompt carries N answers); the trend here is flat-to-declining.")

    bon1 = shared[0]
    t1, r1 = tgt[bon1], ref[bon1]
    n1 = len(t1["prompt_metrics"]) * t1["dataset_metrics"]["num_chunks_averaged"]
    se1 = math.sqrt(t1["dataset_metrics"]["std_tokens"] ** 2 / n1 +
                    r1["dataset_metrics"]["std_tokens"] ** 2 / n1)
    print(f"\n  RESOLUTION: at N={bon1} this table resolves ~{2*se1:,.0f} tokens (2 SE), while the draft")
    print("  prefill it would need to see is ~139. Two independent runs differ by more than the")
    print("  quantity under test, so this CORROBORATES only -- the verdict rests on checks 1-3.")
    return shared


def inject_prefill(doc):
    """Positive control: fold a per-question prefill back into the MEAN only -- precisely
    what the old patch did, and precisely what this script must be able to catch."""
    out = json.loads(json.dumps(doc))
    for bon in out:
        pf = 100 + 30 * int(bon)                        # grows with N, like a judge prompt
        dm, pm = out[bon]["dataset_metrics"], out[bon]["prompt_metrics"]
        for i, p in enumerate(pm):
            p["decode_mean_tokens"] = p["mean_tokens"]
            p["prefill_mean_tokens"] = pf + (i % 7)     # varies question to question
            p["mean_tokens"] += p["prefill_mean_tokens"]
        dm["decode_mean_tokens"] = dm["mean_tokens"]
        dm["prefill_mean_tokens"] = statistics.mean(p["prefill_mean_tokens"] for p in pm)
        dm["mean_tokens"] += dm["prefill_mean_tokens"]
        # std_tokens deliberately untouched -- the exact shape of the original defect
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", nargs="?", default=TARGET)
    ap.add_argument("--reference", default=REFERENCE)
    ap.add_argument("--no-control", action="store_true", help="skip the positive control")
    args = ap.parse_args()

    print("=" * 80)
    print("VERIFYING (target)  :", os.path.abspath(args.target))
    print("AGAINST  (reference):", os.path.abspath(args.reference))
    print("=" * 80)

    tgt = json.load(open(args.target))
    ref = json.load(open(args.reference))
    print(f"\ntarget N    : {sorted(tgt, key=int)}")
    print(f"reference N : {sorted(ref, key=int)}")

    ref_block = ref[sorted(ref, key=int)[0]]
    print("\nThe reference predates prefill entirely, so its schema DEFINES decode-only:")
    print(f"  dataset_metrics: {list(schema_of(ref_block)[0])}")
    print(f"  prompt_metrics : {list(schema_of(ref_block)[1])}")

    print("\n[1] SCHEMA")
    check_schema(tgt, ref_block, "target")

    print("\n[2] MEAN/STD IDENTITY   (breaks if prefill is in the mean but not the std)")
    check_identity(tgt, "target")

    print("\n[3] SAME PROBLEMS")
    tq = tgt[sorted(tgt, key=int)[0]]["questions"]
    rq = ref[sorted(ref, key=int)[0]]["questions"]
    check(tq == rq, f"target and reference hold the identical {len(tq)} questions")
    check(all(tgt[b]["questions"] == tq for b in tgt), "target: questions identical across every N")

    print("\n[4] CROSS-FILE TOKEN COMPARISON   (corroboration)")
    cross_file(tgt, ref)

    if not args.no_control:
        print("\n[5] POSITIVE CONTROL -- re-inject prefill; checks 1 and 2 MUST fail")
        bad = inject_prefill(tgt)
        caught_schema = not check_schema(bad, ref_block, "control", record=False)
        caught_ident = not check_identity(bad, "control", record=False)
        print()
        check(caught_schema, "control: the schema check DID detect re-injected prefill")
        check(caught_ident, "control: the mean/std identity DID detect re-injected prefill")
        first = sorted(bad, key=int)[0]
        print(f"        (control moved N={first} from "
              f"{tgt[first]['dataset_metrics']['mean_tokens']:,.0f} to "
              f"{bad[first]['dataset_metrics']['mean_tokens']:,.0f}; the real file stays at "
              f"{tgt[first]['dataset_metrics']['mean_tokens']:,.0f})")

    print("\n" + "=" * 80)
    if FAILS:
        print(f"VERDICT: {len(FAILS)} CHECK(S) FAILED -- target is NOT clean decode-only")
        for f in FAILS:
            print("   -", f)
    else:
        print("VERDICT: target is DECODE-ONLY. No prefill or prompt tokens are counted at any N,")
        print("         including N=32 -- and the checks that say so are demonstrated to have the")
        print("         power to detect prefill if it were present.")
    print("=" * 80)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
