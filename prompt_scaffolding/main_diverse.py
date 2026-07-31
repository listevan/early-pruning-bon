#!/usr/bin/env python3
"""best-of-k (diverse) entrypoint.

Identical pipeline to main.py, but prunes the N drafted plans down to k UNIQUE
approaches -- LLM-clustered so "unique" means a genuinely different strategy, not
just different wording -- before regenerating back to N completions with the
even-with-top allocation. This is the arm that tests whether forcing survivor
diversity closes the oracle-ceiling gap that plain regen leaves open.

It reuses main.run so there is exactly one implementation of the pipeline; this file
only pins the two flags that define best-of-k:
  --diverse : prune to k unique clusters
  --regen   : regenerate the pruned survivors back to N (even-with-top)

All other flags (--max_plan_tokens, --prune_ratio, --cache_fn, --num_examples, ...)
are accepted exactly as main.py defines them. Output files carry the _diverse tag.
"""
import sys

from main import parse_args, run

if __name__ == '__main__':
    args = parse_args()
    args.diverse = True
    args.regen = True                      # bok is defined as regen-to-N from unique survivors
    if args.baseline:
        print("main_diverse.py: --baseline has no diverse/regen stage; run baseline via main.py.",
              file=sys.stderr)
        sys.exit(1)
    run(args)
