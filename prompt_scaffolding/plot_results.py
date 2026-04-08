import json
import matplotlib.pyplot as plt

def parse_results(results_fn):
    with open(results_fn, "r") as f:
        results = json.load(f)
    
    x = []
    y = []
    labels = []
    for bon in results.keys():
        x.append(float(sum(results[bon]["total_tokens"])) / len(results[bon]["total_tokens"]))
        y.append(float(sum([score[2] for score in results[bon]["results"]])) / len(results[bon]["results"]))
        labels.append(bon)
    
    return x, y, labels

if __name__ == "__main__":
    none_x, none_y, none_labels = parse_results("2026-04-07 04:31:58.307539_bon_1_2_4_8_strategy_None.json")
    completion_x, completion_y, completion_labels = parse_results("2026-04-07 17:13:46.722758_bon_1_2_4_8_strategy_CompletionStrategy.json")
    
    plt.scatter(none_x, none_y, color="blue", label="None Strategy")
    plt.scatter(completion_x, completion_y, color="red", label="Completion Strategy")

    for i, txt in enumerate(none_labels):
        plt.annotate(txt, (none_x[i], none_y[i]))

    for i, txt in enumerate(completion_labels):
        plt.annotate(txt, (completion_x[i], completion_y[i]))

    plt.title('Score vs Token Usage for None and Completion Strategies')
    plt.xlabel('Average Token Used')
    plt.ylabel('Average Score')
    plt.legend()

    plt.savefig("graph_comparison.png")


        