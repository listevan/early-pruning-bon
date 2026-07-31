#!/usr/bin/env python3
"""Combined bon-vs-bok grid: the original 6-subplot layout, with bon and bok overlaid.

TWO LAYERS (do not confuse them):
  - PRUNING method  = which survivors are kept -> a separate file: rank / random / tourney
  - SELECTION method = how the final answer is picked from that pool -> the 4 keys inside
    every file: Selected (model judge) / Random / Best (oracle) / Tourney

Per (plan, prune) this writes two 6-subplot figures (accuracy-vs-tokens and
selection-efficiency-vs-N). In each:
  - subplots 0-3 fix the SELECTION method and overlay 7 lines: baseline + the three
    PRUNING arms for bon (solid) and for bok (dashed).
  - subplots 4-5 are the per-variant all-selection-paths summaries (rank pruning as the
    representative arm; change with --summary_arm).

Differentiation: colour = pruning arm (rank red / random blue / tourney green / baseline
black); line style + marker = variant (bon solid o, bok dashed ^).
"""
import argparse
import glob
import os

import matplotlib.pyplot as plt

from plot_results import parse_results

ARMS = ["rank", "random", "tourney"]
ARM_COLOR = {"rank": "#d62728", "random": "#1f77b4", "tourney": "#2ca02c"}
# (variant tag on disk, display name, linestyle, marker)
VARIANTS = [("regen", "bon", "-", "o"), ("diverse", "bok", "--", "^")]
CATS = ["Selected", "Random", "Best", "Tourney"]           # final-answer SELECTION methods
SUMMARY_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]


def find(directory, arm, plan, prune, variant):
    g = glob.glob(os.path.join(directory, f"*_{arm}_bon_*_plan_{plan}_prune_{prune}_{variant}.json"))
    return sorted(g)[-1] if g else None


def xtok(m, b, cat):
    # the Tourney SELECTION curve is charged its own token cost; others use the shared total
    return m[b]["tourney_tokens"] if cat == "Tourney" else m[b]["tokens"]


def build_series(base, comp):
    """The 7 overlay lines for subplots 0-3: (label, metrics, color, linestyle, marker)."""
    series = [("baseline", base, "black", ":", "s")]
    for arm in ARMS:
        for variant, disp, ls, mk in VARIANTS:
            series.append((f"{arm} · {disp}", comp[(arm, variant)], ARM_COLOR[arm], ls, mk))
    return series


def grid(figpath, title, base, comp, series, summary_arm, xkind):
    """One 6-subplot figure. xkind='tokens' (accuracy vs tokens) or 'bon' (sel-eff vs N)."""
    fig, axes = plt.subplots(2, 3, figsize=(21, 12))
    axes = axes.flatten()

    for idx, cat in enumerate(CATS):
        ax = axes[idx]
        for label, m, color, ls, mk in series:
            if not m:
                continue
            bons = list(m.keys())
            if xkind == "tokens":
                xs = [xtok(m, b, cat) for b in bons]
                ys = [m[b]["acc"][cat] for b in bons]
            else:
                xs = bons
                ys = [m[b]["sel_acc"][cat] for b in bons]
            ax.plot(xs, ys, color=color, linestyle=ls, marker=mk, markersize=7,
                    linewidth=2.2, alpha=0.9, zorder=3, label=label)
        # N labels on the baseline only, so x -> N stays readable without 7x clutter
        if base:
            for b in base:
                bx = xtok(base, b, cat) if xkind == "tokens" else b
                by = base[b]["acc"][cat] if xkind == "tokens" else base[b]["sel_acc"][cat]
                ax.annotate(f"N={b}", (bx, by), textcoords="offset points", xytext=(0, 6),
                            ha="center", fontsize=7, color="black")
        ax.set_title(f"{cat} selection", fontsize=12, weight="bold")
        ax.set_xlabel("Mean Tokens per Question" if xkind == "tokens" else "Best of N")
        ax.set_ylabel("Average Accuracy" if xkind == "tokens" else "Accuracy relative to Best")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle=":", alpha=0.6)
        # Per-subplot legend (the 7 overlay series) in the empty lower band.
        ax.legend(fontsize=7, loc="lower right", ncol=2, framealpha=0.9)

    # Subplots 4-5: per-variant all-selection-paths summary (representative pruning arm).
    for slot, (variant, disp, _ls, mk) in enumerate(VARIANTS):
        ax = axes[4 + slot]
        m = comp[(summary_arm, variant)]
        if m:
            bons = list(m.keys())
            for cat, col in zip(CATS, SUMMARY_COLORS):
                if xkind == "tokens":
                    xs = [xtok(m, b, cat) for b in bons]
                    ys = [m[b]["acc"][cat] for b in bons]
                else:
                    xs = bons
                    ys = [m[b]["sel_acc"][cat] for b in bons]
                ax.plot(xs, ys, color=col, marker=mk, linewidth=2, label=cat)
        ax.set_title(f"All selection paths: {disp} ({summary_arm} prune)", fontsize=12, weight="bold")
        ax.set_xlabel("Mean Tokens per Question" if xkind == "tokens" else "Best of N")
        ax.set_ylabel("Average Accuracy" if xkind == "tokens" else "Ratio Selected / Best")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(fontsize=8, loc="lower right" if xkind == "tokens" else "lower left")

    fig.suptitle(title, fontsize=15, weight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    fig.savefig(figpath, dpi=150)
    print(f"Saved {figpath}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", default=".")
    ap.add_argument("--none_fn", required=True, help="baseline (None strategy) result JSON")
    ap.add_argument("--plan", required=True)
    ap.add_argument("--prune", required=True)
    ap.add_argument("--summary_arm", default="rank",
                    help="pruning arm used for the two summary subplots (default rank)")
    args = ap.parse_args()

    base = parse_results(args.none_fn)
    comp = {}
    for arm in ARMS:
        for variant, *_ in VARIANTS:
            fn = find(args.dir, arm, args.plan, args.prune, variant)
            comp[(arm, variant)] = parse_results(fn) if fn else {}

    series = build_series(base, comp)
    tag = f"plan {args.plan}, prune {args.prune}"
    grid(f"combined_plan_{args.plan}_prune_{args.prune}_accuracy_grid.png",
         f"Accuracy vs Token Footprint — {tag}  (bon vs bok, all pruning arms)",
         base, comp, series, args.summary_arm, "tokens")
    grid(f"combined_plan_{args.plan}_prune_{args.prune}_selection_grid.png",
         f"Selection Efficiency — {tag}  (bon vs bok, all pruning arms)",
         base, comp, series, args.summary_arm, "bon")


if __name__ == "__main__":
    main()
