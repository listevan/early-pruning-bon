#!/usr/bin/env python3
"""Headline bon-vs-bok figure: one axes per (plan, prune).

All three pruning arms (rank/random/tourney) overlaid as curves, bon (regen) SOLID and
bok (diverse) DASHED, colour by arm, with the baseline for reference. x = mean tokens
per question, y = accuracy. Produces two figures: the model-Selected accuracy (the
headline) and the Best/oracle ceiling (the diagnostic for whether unique-pruning put
more correct answers in front of the judge).

Pruning method (rank/random/tourney) is the CURVE; it is distinct from the selection
method inside each file -- here we read only the `Selected` and `Best` selection keys.
"""
import argparse
import glob
import os

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from plot_results import parse_results

ARMS = ["rank", "random", "tourney"]
ARM_COLOR = {"rank": "#d62728", "random": "#1f77b4", "tourney": "#2ca02c"}
# (variant tag on disk, display name, linestyle, marker)
VARIANTS = [("regen", "bon", "-", "o"), ("diverse", "bok", "--", "^")]


def find(directory, arm, plan, prune, variant):
    g = glob.glob(os.path.join(directory, f"*_{arm}_bon_*_plan_{plan}_prune_{prune}_{variant}.json"))
    return sorted(g)[-1] if g else None


def draw(ax, metrics, color, ls, marker, metric_key, lw=2):
    bons = list(metrics.keys())
    if not bons:
        return
    xs = [metrics[b]["tokens"] for b in bons]
    ys = [metrics[b]["acc"][metric_key] for b in bons]
    ax.plot(xs, ys, color=color, linestyle=ls, marker=marker, linewidth=lw, alpha=0.9, zorder=3)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", default=".")
    ap.add_argument("--none_fn", required=True, help="baseline (None strategy) result JSON")
    ap.add_argument("--plan", required=True)
    ap.add_argument("--prune", required=True)
    args = ap.parse_args()

    base = parse_results(args.none_fn)

    for metric_key, tag, nice in [("Selected", "selected", "Selected (model judge)"),
                                  ("Best", "ceiling", "Best (oracle ceiling)")]:
        fig, ax = plt.subplots(figsize=(11, 7))

        # baseline reference, with N labels so the reader can map x -> N
        if base:
            bb = list(base.keys())
            draw(ax, base, "black", ":", "s", metric_key, lw=1.5)
            for b in bb:
                ax.annotate(f"N={b}", (base[b]["tokens"], base[b]["acc"][metric_key]),
                            textcoords="offset points", xytext=(0, 6), ha="center", fontsize=7,
                            color="black")

        for arm in ARMS:
            for variant, _disp, ls, mk in VARIANTS:
                fn = find(args.dir, arm, args.plan, args.prune, variant)
                if fn:
                    draw(ax, parse_results(fn), ARM_COLOR[arm], ls, mk, metric_key)

        # Two legends: colour = pruning arm, line style = variant. Clearer than 7 combined
        # entries, and makes the solid/dashed = bon/bok convention explicit.
        arm_handles = [Line2D([0], [0], color=ARM_COLOR[a], lw=2, label=a) for a in ARMS]
        arm_handles.append(Line2D([0], [0], color="black", ls=":", marker="s", lw=1.5, label="baseline"))
        var_handles = [Line2D([0], [0], color="gray", ls=ls, marker=mk, lw=2, label=f"{disp} ({v})")
                       for v, disp, ls, mk in VARIANTS]
        leg1 = ax.legend(handles=arm_handles, title="pruning arm (colour)",
                         loc="lower right", fontsize=9)
        ax.add_artist(leg1)
        ax.legend(handles=var_handles, title="variant (line style)", loc="upper left", fontsize=9)

        ax.set_title(f"{nice}  —  plan {args.plan}, prune {args.prune}  (bon vs bok)",
                     fontsize=13, weight="bold")
        ax.set_xlabel("Mean Tokens per Question")
        ax.set_ylabel("Average Accuracy")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle=":", alpha=0.6)
        fig.tight_layout()

        out = f"headline_plan_{args.plan}_prune_{args.prune}_{tag}.png"
        fig.savefig(out, dpi=150)
        print(f"Saved {out}")


if __name__ == "__main__":
    main()
