import json
import matplotlib.pyplot as plt
import argparse
import os
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

    return parser.parse_args()

def parse_results(results_fn):
    if not os.path.exists(results_fn):
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

        # mean_tokens is already the per-prompt mean over chunks; summing gives the dataset total
        total_tokens = sum(pm["mean_tokens"] for pm in prompt_metrics)

        score_selected = score_sum("results")
        score_random   = score_sum("random_results")
        score_best     = score_sum("best_results")
        score_tourney  = score_sum("tourney_results")

        metrics[bon] = {
            "tokens": total_tokens,
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

if __name__ == "__main__":
    args = parse_args()
    none_fn = args.none_fn
    completion_fn = args.completion_fn

    none_metrics = parse_results(none_fn)
    comp_metrics = parse_results(completion_fn)
    
    # Extract keys and structures safely
    bons_none = list(none_metrics.keys())
    bons_comp = list(comp_metrics.keys())
    
    # ----------------------------------------------------
    # UNIFY AXIS LIMITS ACROSS ALL GRAPH ELEMENTS
    # ----------------------------------------------------
    all_tokens = [none_metrics[b]["tokens"] for b in bons_none] + [comp_metrics[b]["tokens"] for b in bons_comp]
    x_min, x_max = (min(all_tokens) * 0.9, max(all_tokens) * 1.1) if all_tokens else (0, 100000)
    
    # Setup categories for mapping
    categories = ["Selected", "Random", "Best", "Tourney"]
    colors = {"None": "blue", "Completion": "red"}
    
    # ====================================================
    # PLOT SET 1: ACCURACY VS TOTAL TOKENS USED (6 SUBPLOTS)
    # ====================================================
    fig_acc, axes_acc = plt.subplots(2, 3, figsize=(18, 11), sharex=False, sharey=False)
    axes_acc = axes_acc.flatten()
    
    # Subplots 0-3: Strategy Side-by-Side comparison per selection type
    for idx, cat in enumerate(categories):
        ax = axes_acc[idx]
        
        # Plot None Strategy
        if bons_none:
            x_n = [none_metrics[b]["tokens"] for b in bons_none]
            y_n = [none_metrics[b]["acc"][cat] for b in bons_none]
            ax.scatter(x_n, y_n, color=colors["None"], label="None Strategy", zorder=3)
            ax.plot(x_n, y_n, color=colors["None"], linestyle="--", alpha=0.5)
            for b, x, y in zip(bons_none, x_n, y_n):
                ax.annotate(f"N={b}", (x, y), textcoords="offset points", xytext=(0,5), ha='center', fontsize=8)
                
        # Plot Completion Strategy
        if bons_comp:
            x_c = [comp_metrics[b]["tokens"] for b in bons_comp]
            y_c = [comp_metrics[b]["acc"][cat] for b in bons_comp]
            ax.scatter(x_c, y_c, color=colors["Completion"], label="Completion Strategy", zorder=3)
            ax.plot(x_c, y_c, color=colors["Completion"], linestyle="-", alpha=0.5)
            for b, x, y in zip(bons_comp, x_c, y_c):
                ax.annotate(f"N={b}", (x, y), textcoords="offset points", xytext=(0,-12), ha='center', fontsize=8)
                
        ax.set_title(f"{cat} Accuracy")
        ax.set_xlabel("Total Tokens Used")
        ax.set_ylabel("Average Accuracy")
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="lower right")

    # Subplot 4: Summary of all decision pathways for None Strategy
    ax_summary_none = axes_acc[4]
    summary_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    if bons_none:
        x_n = [none_metrics[b]["tokens"] for b in bons_none]
        for cat, col in zip(categories, summary_colors):
            y_n = [none_metrics[b]["acc"][cat] for b in bons_none]
            ax_summary_none.plot(x_n, y_n, marker='o', label=cat, color=col)
    ax_summary_none.set_title("All Paths: None Strategy")
    ax_summary_none.set_xlabel("Total Tokens Used")
    ax_summary_none.set_ylabel("Average Accuracy")
    ax_summary_none.set_xlim(x_min, x_max)
    ax_summary_none.set_ylim(-0.05, 1.05)
    ax_summary_none.grid(True, linestyle=":", alpha=0.6)
    ax_summary_none.legend(loc="lower right")

    # Subplot 5: Summary of all decision pathways for Completion Strategy
    ax_summary_comp = axes_acc[5]
    if bons_comp:
        x_c = [comp_metrics[b]["tokens"] for b in bons_comp]
        for cat, col in zip(categories, summary_colors):
            y_c = [comp_metrics[b]["acc"][cat] for b in bons_comp]
            ax_summary_comp.plot(x_c, y_c, marker='s', label=cat, color=col)
    ax_summary_comp.set_title("All Paths: Completion Strategy")
    ax_summary_comp.set_xlabel("Total Tokens Used")
    ax_summary_comp.set_ylabel("Average Accuracy")
    ax_summary_comp.set_xlim(x_min, x_max)
    ax_summary_comp.set_ylim(-0.05, 1.05)
    ax_summary_comp.grid(True, linestyle=":", alpha=0.6)
    ax_summary_comp.legend(loc="lower right")

    plt.suptitle("Accuracy vs Token Footprint Evaluation Grid", fontsize=16, weight='bold')
    plt.tight_layout()
    out_acc_name = f"{completion_fn.replace('.json', '')}_accuracy_grid_comparison.png"
    plt.savefig(out_acc_name, dpi=150)
    print(f"Saved accuracy plot layout to: {out_acc_name}")


    # ====================================================
    # PLOT SET 2: SELECTION ACCURACY VS BEST-OF-N (6 SUBPLOTS)
    # ====================================================
    fig_sel, axes_sel = plt.subplots(2, 3, figsize=(18, 11))
    axes_sel = axes_sel.flatten()
    
    # Get a unified categorical X-axis scale based on unique Best of N values across both runs
    all_bons_str = sorted(list(set(bons_none + bons_comp)), key=lambda x: int(x))

    # Subplots 0-3: Side-by-Side comparison of selection efficiency per category
    for idx, cat in enumerate(categories):
        ax = axes_sel[idx]
        
        if bons_none:
            y_n = [none_metrics[b]["sel_acc"][cat] for b in bons_none]
            ax.scatter(bons_none, y_n, color=colors["None"], label="None Strategy", s=80, zorder=3)
            ax.plot(bons_none, y_n, color=colors["None"], linestyle="--", alpha=0.5)
            
        if bons_comp:
            y_c = [comp_metrics[b]["sel_acc"][cat] for b in bons_comp]
            ax.scatter(bons_comp, y_c, color=colors["Completion"], label="Completion Strategy", marker='s', s=80, zorder=3)
            ax.plot(bons_comp, y_c, color=colors["Completion"], linestyle="-", alpha=0.5)
            
        ax.set_title(f"{cat} Selection Efficiency")
        ax.set_xlabel("Best of N Options")
        ax.set_ylabel("Accuracy Relative to Best (%)")
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="lower left")

    # Subplot 4: Selection Accuracy overlay for None Strategy
    ax_sel_none = axes_sel[4]
    if bons_none:
        for cat, col in zip(categories, summary_colors):
            y_n = [none_metrics[b]["sel_acc"][cat] for b in bons_none]
            ax_sel_none.plot(bons_none, y_n, marker='o', label=cat, color=col)
    ax_sel_none.set_title("Selection Acc: None Strategy")
    ax_sel_none.set_xlabel("Best of N Options")
    ax_sel_none.set_ylabel("Ratio Selected / Best")
    ax_sel_none.set_ylim(-0.05, 1.05)
    ax_sel_none.grid(True, linestyle=":", alpha=0.6)
    ax_sel_none.legend(loc="lower left")

    # Subplot 5: Selection Accuracy overlay for Completion Strategy
    ax_sel_comp = axes_sel[5]
    if bons_comp:
        for cat, col in zip(categories, summary_colors):
            y_c = [comp_metrics[b]["sel_acc"][cat] for b in bons_comp]
            ax_sel_comp.plot(bons_comp, y_c, marker='s', label=cat, color=col)
    ax_sel_comp.set_title("Selection Acc: Completion Strategy")
    ax_sel_comp.set_xlabel("Best of N Options")
    ax_sel_comp.set_ylabel("Ratio Selected / Best")
    ax_sel_comp.set_ylim(-0.05, 1.05)
    ax_sel_comp.grid(True, linestyle=":", alpha=0.6)
    ax_sel_comp.legend(loc="lower left")

    plt.suptitle("Selection Accuracy Comparison Matrix (Correct Selection / Best Available)", fontsize=16, weight='bold')
    plt.tight_layout()
    out_sel_name = f"{completion_fn.replace('.json', '')}_selection_accuracy_grid.png"
    plt.savefig(out_sel_name, dpi=150)
    print(f"Saved selection efficiency layout to: {out_sel_name}")