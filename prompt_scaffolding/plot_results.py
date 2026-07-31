import json
import matplotlib.pyplot as plt
import argparse
import os
import re
import statistics

def parse_args():
    parser = argparse.ArgumentParser(description="Parse result filenames and plot comparative metrics.")

    parser.add_argument(
        "--none_fn",
        type=str,
        default="2026-05-04 05:24:58.543955_bon_1_2_4_8_16_strategy_None_plan_4000_prune_2.json",
        help="Filename of results for no strategy completion"
    )
    parser.add_argument(
        "--completion_fn",
        type=str,
        default="2026-04-07 17:13:46.722758_bon_1_2_4_8_strategy_CompletionStrategy.json",
        help="Filename of results for completion strategy completion"
    )
    parser.add_argument(
        "--completion_fn2",
        type=str,
        default="",
        help="Optional SECOND completion file, overlaid on the same axes as --completion_fn "
             "(e.g. plot the diverse/bok run against the regen/bon run for one plan+prune). "
             "Empty (default) reproduces the original two-curve baseline-vs-completion plot."
    )

    return parser.parse_args()

def parse_results(results_fn):
    if not results_fn or not os.path.exists(results_fn):
        if results_fn:
            print(f"Warning: File {results_fn} not found. Returning empty metrics.")
        return {}

    with open(results_fn, "r") as f:
        results = json.load(f)

    metrics = {}

    # Sort the dictionary keys (best_of_n values) numerically
    sorted_bons = sorted(results.keys(), key=lambda x: int(x))

    for bon in sorted_bons:
        bon_data = results[bon]
        prompt_metrics = bon_data["prompt_metrics"]
        num_examples = len(prompt_metrics)

        # Each prompt holds one entry per chunk; average over chunks, then sum over prompts.
        def score_sum(key):
            return sum(
                statistics.mean([r["score"] for r in pm["chunks_data"][key]])
                for pm in prompt_metrics
            )

        # PER-QUESTION MEAN, not a dataset sum. These curves compare files that may hold
        # different numbers of questions -- the regen sweep runs 30 while the shared baseline
        # was generated at 100 -- and a sum silently scales each file by its own question
        # count, inflating the 100-question baseline 3.33x against a 30-question arm (a
        # plotted 5.8x token ratio where the true per-question ratio is 1.74x). Averaging
        # makes the x-axis a per-question cost that is comparable across files, and matches
        # what analysis.py reports.
        # The tourney selection curve is charged its own cost (tourney_mean_tokens); older files
        # without that key fall back to mean_tokens.
        total_tokens = statistics.mean([pm["mean_tokens"] for pm in prompt_metrics])
        tourney_tokens = statistics.mean([pm.get("tourney_mean_tokens", pm["mean_tokens"]) for pm in prompt_metrics])

        score_selected = score_sum("results")
        score_random   = score_sum("random_results")
        score_best     = score_sum("best_results")
        score_tourney  = score_sum("tourney_results")

        metrics[bon] = {
            "tokens": total_tokens,
            "tourney_tokens": tourney_tokens,
            "acc": {
                "Selected": float(score_selected) / num_examples,
                "Random": float(score_random) / num_examples,
                "Best": float(score_best) / num_examples,
                "Tourney": float(score_tourney) / num_examples,
            },
            "sel_acc": {
                "Selected": float(score_selected) / max(1, score_best),
                "Random": float(score_random) / max(1, score_best),
                "Tourney": float(score_tourney) / max(1, score_best),
                "Best": 1.0  # By definition
            }
        }
    return metrics


def comp_label(fn):
    """Name a completion curve from its filename variant tag."""
    if fn.endswith("_diverse.json"):
        return "bok: unique-k"
    if fn.endswith("_regen.json"):
        return "bon: regen to N"
    return "Completion Strategy"


def plan_prune(fn):
    """(plan, prune) parsed from a result filename, or (None, None)."""
    m = re.search(r"_plan_(\d+)_prune_([\d.]+)", os.path.basename(fn or ""))
    return (m.group(1), m.group(2)) if m else (None, None)


def arm_of(fn):
    """Pruning arm (rank/random/tourney) parsed from a result filename, or ''.
    NOTE: this is the PRUNING method named in the filename, distinct from the
    Selected/Random/Best/Tourney SELECTION categories plotted within each file."""
    m = re.search(r"_([a-z]+)_bon_", os.path.basename(fn or ""))
    return m.group(1) if m else ""


if __name__ == "__main__":
    args = parse_args()
    none_fn = args.none_fn
    completion_fn = args.completion_fn
    completion_fn2 = args.completion_fn2

    none_metrics = parse_results(none_fn)
    comp_metrics = parse_results(completion_fn)
    comp2_metrics = parse_results(completion_fn2) if completion_fn2 else {}
    has2 = bool(comp2_metrics)

    categories = ["Selected", "Random", "Best", "Tourney"]
    summary_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    # OVERLAY series drawn together in the per-category subplots (0-3): baseline plus one
    # or two completion curves. Each is (label, metrics, color, linestyle, marker, annot_dy).
    overlay = [("None (baseline)", none_metrics, "blue", "--", "o", 6),
               (comp_label(completion_fn), comp_metrics, "red", "-", "s", -14)]
    if has2:
        overlay.append((comp_label(completion_fn2), comp2_metrics, "green", "-", "^", -26))

    # SUMMARY panels (subplots 4,5): each shows one strategy's four paths overlaid.
    # Backwards compatible: with a single completion, keep None + Completion (as before);
    # with a second completion, show the two completions side by side (baseline paths are
    # already visible per-category above).
    if has2:
        summary = [(comp_label(completion_fn), comp_metrics, "s"),
                   (comp_label(completion_fn2), comp2_metrics, "^")]
    else:
        summary = [("None Strategy", none_metrics, "o"),
                   (comp_label(completion_fn), comp_metrics, "s")]

    present = [m for _, m, *_ in overlay if m]

    # ----------------------------------------------------
    # UNIFY AXIS LIMITS ACROSS ALL GRAPH ELEMENTS
    # ----------------------------------------------------
    all_tokens = [m[b]["tokens"] for m in present for b in m]
    x_min, x_max = (min(all_tokens) * 0.9, max(all_tokens) * 1.1) if all_tokens else (0, 100000)

    # The Tourney curve is charged its own token cost; all others use the shared total.
    def xtok(m, b, cat):
        return m[b]["tourney_tokens"] if cat == "Tourney" else m[b]["tokens"]

    # ====================================================
    # PLOT SET 1: ACCURACY VS TOKENS USED (6 SUBPLOTS)
    # ====================================================
    fig_acc, axes_acc = plt.subplots(2, 3, figsize=(18, 11), sharex=False, sharey=False)
    axes_acc = axes_acc.flatten()

    # Subplots 0-3: every overlay series (baseline + completions) per selection type.
    for idx, cat in enumerate(categories):
        ax = axes_acc[idx]
        for label, m, color, ls, marker, dy in overlay:
            bons = list(m.keys())
            if not bons:
                continue
            xs = [xtok(m, b, cat) for b in bons]
            ys = [m[b]["acc"][cat] for b in bons]
            ax.scatter(xs, ys, color=color, label=label, marker=marker, zorder=3)
            ax.plot(xs, ys, color=color, linestyle=ls, alpha=0.5)
            for b, x, y in zip(bons, xs, ys):
                ax.annotate(f"N={b}", (x, y), textcoords="offset points", xytext=(0, dy), ha='center', fontsize=8)
        ax.set_title(f"{cat} Accuracy")
        ax.set_xlabel("Mean Tokens per Question")
        ax.set_ylabel("Average Accuracy")
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="lower right")

    # Subplots 4-5: all-paths overlay for each summary strategy.
    for slot, (title, m, marker) in enumerate(summary):
        ax = axes_acc[4 + slot]
        if m:
            bons = list(m.keys())
            for cat, col in zip(categories, summary_colors):
                xs = [xtok(m, b, cat) for b in bons]
                ys = [m[b]["acc"][cat] for b in bons]
                ax.plot(xs, ys, marker=marker, label=cat, color=col)
        ax.set_title(f"All Paths: {title}")
        ax.set_xlabel("Mean Tokens per Question")
        ax.set_ylabel("Average Accuracy")
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="lower right")

    plt.suptitle("Accuracy vs Token Footprint Evaluation Grid", fontsize=16, weight='bold')
    plt.tight_layout()

    # Output name: for a two-completion overlay derive a plan/prune-based name so the file
    # is not misleadingly tied to just one variant; otherwise keep the original scheme.
    if has2:
        plan, prune = plan_prune(completion_fn)
        arm = arm_of(completion_fn) or "arm"
        # arm belongs in the name: rank/random/tourney share a (plan, prune) and would
        # otherwise overwrite each other.
        stem = f"bon_vs_bok_{arm}_plan_{plan}_prune_{prune}" if plan else f"bon_vs_bok_{arm}"
    else:
        stem = completion_fn.replace(".json", "")
    out_acc_name = f"{stem}_accuracy_grid_comparison.png"
    plt.savefig(out_acc_name, dpi=150)
    print(f"Saved accuracy plot layout to: {out_acc_name}")

    # ====================================================
    # PLOT SET 2: SELECTION ACCURACY VS BEST-OF-N (6 SUBPLOTS)
    # ====================================================
    fig_sel, axes_sel = plt.subplots(2, 3, figsize=(18, 11))
    axes_sel = axes_sel.flatten()

    # Subplots 0-3: selection efficiency per category, every overlay series.
    for idx, cat in enumerate(categories):
        ax = axes_sel[idx]
        for label, m, color, ls, marker, _dy in overlay:
            bons = list(m.keys())
            if not bons:
                continue
            ys = [m[b]["sel_acc"][cat] for b in bons]
            ax.scatter(bons, ys, color=color, label=label, marker=marker, s=80, zorder=3)
            ax.plot(bons, ys, color=color, linestyle=ls, alpha=0.5)
        ax.set_title(f"{cat} Selection Efficiency")
        ax.set_xlabel("Best of N Options")
        ax.set_ylabel("Accuracy Relative to Best (%)")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="lower left")

    # Subplots 4-5: all-paths selection overlay for each summary strategy.
    for slot, (title, m, marker) in enumerate(summary):
        ax = axes_sel[4 + slot]
        if m:
            bons = list(m.keys())
            for cat, col in zip(categories, summary_colors):
                ys = [m[b]["sel_acc"][cat] for b in bons]
                ax.plot(bons, ys, marker=marker, label=cat, color=col)
        ax.set_title(f"Selection Acc: {title}")
        ax.set_xlabel("Best of N Options")
        ax.set_ylabel("Ratio Selected / Best")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="lower left")

    plt.suptitle("Selection Accuracy Comparison Matrix (Correct Selection / Best Available)", fontsize=16, weight='bold')
    plt.tight_layout()
    out_sel_name = f"{stem}_selection_accuracy_grid.png"
    plt.savefig(out_sel_name, dpi=150)
    print(f"Saved selection efficiency layout to: {out_sel_name}")
