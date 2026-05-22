Aimport json
import matplotlib.pyplot as plt
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Parse result filenames.")

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
    with open(results_fn, "r") as f:
        results = json.load(f)
    
    x = []
    y = []
    y_scores = []
    labels = []
    
    # Sort the dictionary keys here
    for bon in sorted(results.keys()):
        x.append(sum(results[bon]["total_tokens"]))
        y.append(float(sum([score[1] for score in results[bon]["results"]])) / len(results[bon]["results"]))
        y_scores.append(sum([score[1] for score in results[bon]["results"]]))
        labels.append(bon)
    
    return x, y, y_scores, labels

if __name__ == "__main__":
    args = parse_args()
    none_fn = args.none_fn
    completion_fn = args.completion_fn
    print(completion_fn)

    none_x, none_y, none_y_scores, none_labels = parse_results(none_fn)
    completion_x, completion_y, completion_y_scores, completion_labels = parse_results(completion_fn)
    
    # result comparison plot
    plt.figure()

    plt.scatter(none_x, none_y, color="blue", label="None Strategy")
    plt.scatter(completion_x, completion_y, color="red", label="Completion Strategy")

    for i, txt in enumerate(none_labels):
        plt.annotate(txt, (none_x[i], none_y[i]))

    for i, txt in enumerate(completion_labels):
        plt.annotate(txt, (completion_x[i], completion_y[i]))

    plt.title('Score vs Token Usage for None and Completion Strategies')
    plt.xlabel('Total Token Used')
    plt.ylabel('Average Score')
    plt.legend()

    plt.savefig(f"{completion_fn.replace(".json", "")}_graph_comparison.png")

    # true positive comparison plot
    plt.figure()

    plt.scatter(completion_labels, [float(a) / b for a, b in zip(completion_y_scores, none_y_scores)])

    plt.title('Selection Accuracy for Completion Strategies')
    plt.xlabel('Best of N')
    plt.ylabel('Selection Accuracy')
    plt.legend()

    plt.savefig(f"{completion_fn.replace(".json", "")}_selection_accuracy.png")