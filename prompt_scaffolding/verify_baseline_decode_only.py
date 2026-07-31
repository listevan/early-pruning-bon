#!/usr/bin/env python3
"""Verify a baseline result JSON is on a DECODE-ONLY token basis, against a reference
baseline that never had prompt tokens folded in.

    TARGET     the file under test  (defaults to the bon=1..32 baseline)
    REFERENCE  a baseline known to be decode-only (defaults to the May run)

WHAT CARRIES THE VERDICT
------------------------
The cross-file token comparison is the WEAKEST of these checks, and it is important to say
so: the two baselines are independent samples, and their per-question token counts have a
standard deviation of ~6,300. The prefill that was removed is ~139 tokens at N=1 (1.7% of
the total). That is a small fraction of the standard error of the cross-run difference, so
a "means agree" result could never have proved anything on its own. It is reported for
magnitude and direction only.

The verdict rests on two internal checks that are exact rather than statistical:

  [schema]   No prefill/decode field exists anywhere in the file, and the key set matches
             the reference exactly. Binary; cannot be faked.

  [mean/std] Reconstructing the dataset-wide std from the per-question means and stds must
             reproduce the stored std_tokens EXACTLY. This identity holds only when
             mean_tokens and std_tokens describe the same series of numbers. Folding
             prefill into the mean while leaving the std alone -- which is exactly what the
             old patch did -- breaks it. This is the fingerprint of the defect, and it is
             checked at every N including N=32, which the reference file does not contain.

A POSITIVE CONTROL runs at the end: prefill is re-injected into an in-memory copy and the
same checks are re-run. They must FAIL there. Without that, "all checks passed" would not
be evidence that the checks can detect anything.

USAGE
-----
    python3 verify_baseline_decode_only.py
    python3 verify_baseline_decode_only.py TARGET.json REFERENCE.json
"""
import argparse
import copy
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TARGET = os.path.join(
    HERE, "2026-07-25_11-42-12_baseline_bon_1_2_4_8_16_32_strat_None_plan_4000_prune_2.json")
DEFAULT_REFERENCE = os.path.join(
    HERE, "2026-05-28_14-04-13_baseline_bon_1_2_4_8_16_strat_None_plan_4000_prune_2.json")

BANNED = ("prefill", "prompt_token", "decode_mean_tokens", "decode_tokens")

FAILS = []
CONTROL = False          # inside the positive control a False result is the DESIRED outcome


def check(cond, msg, fatal=True):
    if CONTROL:
        # not a verdict line: we are proving the check can fire, so cond==False is success
        print(("  ctrl  no-fire: " if cond else "  ctrl  FIRED  : ") + msg)
    else:
        print(("  PASS  " if cond else "  FAIL  ") + msg)
        if not cond and fatal:
            FAILS.append(msg)
    return cond


def note(msg):
    print("        " + msg)


def pooled_std(means, stds, n_per):
    """Exact sample std of the pooled population from per-group mean/std, equal group size.

    Every question contributes n_per observations (the chunks). Total sum of squares is the
    within-question part plus the between-question part; this is an identity, not an
    approximation, so a mismatch means the mean and the std were computed over different
    numbers.
    """
    N = len(means) * n_per
    if N < 2:
        return 0.0
    grand = statistics.mean(means)
    ss = sum((n_per - 1) * s * s + n_per * (m - grand) ** 2 for m, s in zip(means, stds))
    return math.sqrt(ss / (N - 1))


def walk_keys(doc):
    """Every dict key appearing anywhere in the document."""
    out = set()
    stack = [doc]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            out |= set(cur)
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
    return out


def schema_of(doc):
    """(dataset_metrics keys, prompt_metrics keys) for the lowest N present."""
    bon = min(doc, key=int)
    blk = doc[bon]
    return (tuple(sorted(blk["dataset_metrics"])),
            tuple(sorted(k for k in blk["prompt_metrics"][0] if k != "chunks_data")))


def check_no_prefill_fields(doc, label, fatal=True):
    keys = walk_keys(doc)
    hits = sorted(k for k in keys if any(b in k for b in BANNED))
    return check(not hits, f"{label}: no prefill/decode field anywhere in the file"
                           + (f" -- FOUND {hits}" if hits else ""), fatal)


def check_mean_std_identity(doc, label, fatal=True):
    ok = True
    for bon in sorted(doc, key=int):
        dm, pm = doc[bon]["dataset_metrics"], doc[bon]["prompt_metrics"]
        n = dm["num_chunks_averaged"]
        recon = pooled_std([p["mean_tokens"] for p in pm], [p["std_tokens"] for p in pm], n)
        stored = dm["std_tokens"]
        agree = abs(recon - stored) <= 1e-9 * max(1.0, stored)
        ok &= check(agree,
                    f"{label} N={bon:>2}: std_tokens {stored:,.4f} == reconstruction "
                    f"{recon:,.4f} from the same numbers mean_tokens averages"
                    + ("" if agree else f"  [off by {abs(recon - stored):,.4f}]"),
                    fatal)
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", nargs="?", default=DEFAULT_TARGET)
    ap.add_argument("reference", nargs="?", default=DEFAULT_REFERENCE)
    args = ap.parse_args()

    tgt_path, ref_path = os.path.abspath(args.target), os.path.abspath(args.reference)
    print("=" * 92)
    print("VERIFYING (target)   :", tgt_path)
    print("AGAINST   (reference):", ref_path)
    print("=" * 92)

    tgt, ref = json.load(open(tgt_path)), json.load(open(ref_path))
    tgt_bons = sorted(tgt, key=int)
    ref_bons = sorted(ref, key=int)
    shared = [b for b in tgt_bons if b in ref]
    only_tgt = [b for b in tgt_bons if b not in ref]
    print(f"\ntarget N    : {[int(b) for b in tgt_bons]}")
    print(f"reference N : {[int(b) for b in ref_bons]}")
    print(f"shared      : {[int(b) for b in shared]}    target-only: {[int(b) for b in only_tgt]}")

    # ---------------------------------------------------------------- 1. schema (decisive)
    print("\n[1] SCHEMA -- decisive, binary")
    check_no_prefill_fields(tgt, "target")
    check_no_prefill_fields(ref, "reference")
    t_ds, t_pm = schema_of(tgt)
    r_ds, r_pm = schema_of(ref)
    check(t_ds == r_ds, f"dataset_metrics keys match the reference exactly: {list(t_ds)}")
    check(set(t_pm) >= set(r_pm) and not (set(t_pm) - set(r_pm) - {"tourney_mean_tokens"}),
          f"prompt_metrics keys are the reference's plus at most tourney_mean_tokens: {list(t_pm)}")
    note(f"reference prompt_metrics keys: {list(r_pm)}")
    # the schema must be uniform across N, N=32 included
    uniform = all(schema_of({b: tgt[b]}) == (t_ds, t_pm) for b in tgt_bons)
    check(uniform, "every N in the target carries that same schema (N=32 included)")

    # ------------------------------------------------- 2. mean/std identity (decisive)
    print("\n[2] MEAN/STD IDENTITY -- decisive; this is the fingerprint of a folded-in prefill")
    check_mean_std_identity(tgt, "target")

    # ---------------------------------------------------------------- 3. same questions
    print("\n[3] COMPARABILITY")
    tq, rq = tgt[tgt_bons[0]]["questions"], ref[ref_bons[0]]["questions"]
    check(tq == rq, f"the two runs pose byte-identical questions (n={len(tq)}) -> "
                    f"token counts are directly comparable")
    check(all(tgt[b]["questions"] == tq for b in tgt_bons),
          "the target poses the same questions at every N")

    # --------------------------------------------- 4. cross-file magnitude (weak, reported)
    print("\n[4] CROSS-FILE TOKEN COMPARISON -- sanity only; see the power analysis below")
    print(f"    {'N':>3} | {'target':>10} {'reference':>10} {'diff':>9} {'ratio':>7} | "
          f"{'SE(diff)':>9} {'|diff|/SE':>9}")
    for b in shared:
        tpm = [p["mean_tokens"] for p in tgt[b]["prompt_metrics"]]
        rpm = [p["mean_tokens"] for p in ref[b]["prompt_metrics"]]
        tmean, rmean = statistics.mean(tpm), statistics.mean(rpm)
        # independent runs: SE of the difference of the two dataset means, over questions
        nq = len(tpm)
        se = math.sqrt(statistics.variance(tpm) / nq + statistics.variance(rpm) / nq)
        d = tmean - rmean
        print(f"    {int(b):>3} | {tmean:>10,.0f} {rmean:>10,.0f} {d:>+9,.0f} "
              f"{tmean / rmean:>7.4f} | {se:>9,.0f} {abs(d) / se:>9.2f}")

    b1 = shared[0]
    tpm = [p["mean_tokens"] for p in tgt[b1]["prompt_metrics"]]
    rpm = [p["mean_tokens"] for p in ref[b1]["prompt_metrics"]]
    se1 = math.sqrt(statistics.variance(tpm) / len(tpm) + statistics.variance(rpm) / len(rpm))
    note("")
    note(f"POWER: at N={int(b1)} the cross-run difference has SE ~{se1:,.0f} tokens. The prefill")
    note(f"       that a patched file folds in is ~139 tokens there -- about {139 / se1:.2f} SE.")
    note( "       So this table CANNOT distinguish decode-only from decode+prefill on its own.")
    note( "       It is reported for direction and magnitude; checks [1] and [2] carry the verdict.")
    check(all(tgt[b]["dataset_metrics"]["mean_tokens"] > 0 for b in tgt_bons),
          "every N reports a positive token count")

    # ----------------------------------------------------- 5. the target-only N (e.g. 32)
    if only_tgt:
        print(f"\n[5] N={', '.join(only_tgt)} -- absent from the reference, so verified internally")
        for b in only_tgt:
            dm, pm = tgt[b]["dataset_metrics"], tgt[b]["prompt_metrics"]
            check(not [k for k in walk_keys({b: tgt[b]}) if any(x in k for x in BANNED)],
                  f"N={b}: carries no prefill/decode field")
            n = dm["num_chunks_averaged"]
            recon = pooled_std([p["mean_tokens"] for p in pm], [p["std_tokens"] for p in pm], n)
            check(abs(recon - dm["std_tokens"]) <= 1e-9 * max(1.0, dm["std_tokens"]),
                  f"N={b}: mean/std identity holds ({dm['std_tokens']:,.2f})")
            check(abs(dm["mean_tokens"] - statistics.mean(p["mean_tokens"] for p in pm)) < 1e-6,
                  f"N={b}: dataset mean_tokens == mean of the per-question means")
        # per-sample cost should sit on the trend the shared Ns establish, not jump
        print(f"\n    per-sample cost (mean_tokens / N) -- a folded-in prefill inflates the tail")
        print(f"    {'N':>3} | {'target':>10} | {'reference':>10}")
        for b in tgt_bons:
            t = tgt[b]["dataset_metrics"]["mean_tokens"] / int(b)
            r = (f"{ref[b]['dataset_metrics']['mean_tokens'] / int(b):>10,.0f}"
                 if b in ref else f"{'--':>10}")
            print(f"    {int(b):>3} | {t:>10,.0f} | {r}")
        costs = [tgt[b]["dataset_metrics"]["mean_tokens"] / int(b) for b in tgt_bons]
        check(all(costs[i] >= costs[i + 1] - 1e-9 for i in range(2, len(costs) - 1)),
              "per-sample cost is monotonically non-increasing from N=4 up -> no tail inflation")

    # ------------------------------------------------------------- 6. positive control
    print("\n[6] POSITIVE CONTROL -- re-inject prefill; every decisive check MUST fail")
    poisoned = copy.deepcopy(tgt)
    for b in poisoned:
        blk = poisoned[b]
        pre = []
        for i, p in enumerate(blk["prompt_metrics"]):
            # a plausible per-question prefill: question length plus a judge prompt that
            # grows with N, exactly the shape the old patch produced
            pf = 139.0 + 11.0 * int(b) + (i % 7)
            p["decode_mean_tokens"] = p["mean_tokens"]
            p["prefill_mean_tokens"] = pf
            p["mean_tokens"] = p["mean_tokens"] + pf      # std_tokens deliberately untouched
            pre.append(pf)
        dm = blk["dataset_metrics"]
        dm["decode_mean_tokens"] = dm["mean_tokens"]
        dm["prefill_mean_tokens"] = statistics.mean(pre)
        dm["mean_tokens"] = dm["mean_tokens"] + statistics.mean(pre)

    global CONTROL
    CONTROL = True
    ctrl_schema = check_no_prefill_fields(poisoned, "poisoned copy")
    ctrl_ident = check_mean_std_identity(poisoned, "poisoned")
    CONTROL = False
    check(not ctrl_schema, "control: the schema check DID fire on a patched file")
    check(not ctrl_ident, "control: the mean/std identity DID break on a patched file")
    note("-> both decisive checks have power; passing them on the target is meaningful.")

    print("\n" + "=" * 92)
    if FAILS:
        print(f"VERDICT: {len(FAILS)} CHECK(S) FAILED")
        for f in FAILS:
            print("   -", f)
    else:
        print("VERDICT: the target is on a DECODE-ONLY basis at every N, N=32 included,")
        print("         and matches the reference baseline's schema exactly.")
    print("=" * 92)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
