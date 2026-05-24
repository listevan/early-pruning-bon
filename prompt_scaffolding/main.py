from model.model import Model
from model.strategies import HypothesisStrategy, PlanStrategy, ConceptStrategy, ReasoningStructureStrategy, CountdownStrategy, UserStrategy, CompletionStrategy

import reasoning_gym
import re
import random
import sys

import datetime
import json
import argparse

seed = 42
random.seed(seed)

def parse_args():
    parser = argparse.ArgumentParser(description="Parse dataset and model hyperparameters.")

    # Dataset hyperparameters
    parser.add_argument(
        "--dataset_type", 
        type=str, 
        default="countdown", 
        help="Type of dataset being used (default: 'countdown')"
    )
    parser.add_argument(
        "--level", 
        type=int, 
        default=6, 
        help="Difficulty level or stage of the dataset (default: 6)"
    )
    parser.add_argument(
        "--num_examples", 
        type=int, 
        default=100, 
        help="Number of examples to process (default: 30)"
    )

    # Model hyperparameters
    parser.add_argument(
        "--temperature", 
        type=float, 
        default=1.0,  
        help="Sampling temperature for the model (default: 1.0)"
    )
    parser.add_argument(
        "--best_of_ns", 
        type=int, 
        nargs='+', 
        default=[1, 2, 4, 8, 16], 
        help="List of integers for best-of-N sampling (default: 1 2 4 8). Provide space-separated values."
    )
    parser.add_argument(
        "--max_plan_tokens", 
        type=int, 
        default=4000, 
        help="Number of tokens to generate before diversifying."
    )
    parser.add_argument(
        "--prune_ratio", 
        type=float, 
        default=2, 
        help="Will prune down to bon // prune_ratio results (at 1, will let model decide)"
    )
    parser.add_argument(
        "--group_size",
        type=int,
        default=4,
        help="Group sizes for tourney"
    )
    parser.add_argument(
        "--num_gpus",
        type=int,
        default=1, # Change to however many A100s you are requesting in Slurm
        help="Number of GPUs to use for Data Parallelism"
    )

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    # dataset hyperparameters
    dataset_type = args.dataset_type
    level = args.level
    num_examples = args.num_examples

    # model hyperparameters
    temperature = args.temperature
    best_of_ns = args.best_of_ns
    max_plan_tokens = args.max_plan_tokens
    prune_ratio = max(1, args.prune_ratio)
    group_size = args.group_size

    num_gpus = args.num_gpus

    # initialize model
    model="Qwen/Qwen3-4B-Instruct-2507"
    # model = "Qwen/Qwen3-0.6B"
    llm = Model(model, num_gpus, seed=seed)

    # model strategy, set to None if not using
    # strategy = CompletionStrategy(llm=llm.llm, seed=seed)
    strategy = None

    previous_responses_fn = "2026-05-04 05:24:58.543955_bon_1_2_4_8_16_strategy_None_plan_4000_prune_2.json"
    try:
        with open(previous_responses_fn, "r") as f:
            # dict of best of n to "responses" (list of dicts)
            previous_responses = {best_of_n: data["responses"] for best_of_n, data in json.load(f).items()} 
    except FileNotFoundError:
        previous_responses = None

    data = reasoning_gym.create_dataset(dataset_type, size=num_examples, min_numbers=level, max_numbers=level, seed=seed)
    # load the questions
    prompts = [entry["question"] for entry in data]

    # generate responses
    outputs = llm.generate_responses(prompts, best_of_ns=best_of_ns, temperature=temperature, max_tokens=16384, strategy=strategy, prune_ratio=prune_ratio, previous_responses=previous_responses)

    def clean_math_string(line):
        # 1. Remove \boxed{ and the closing }
        # This looks for the literal string "\boxed{" and "}" and removes them
        line = re.sub(r'\\boxed\{', '', line)
        line = re.sub(r'\}', '', line)
        
        # 2. Replace LaTeX operators with standard symbols
        line = line.replace(r'\times', '*')
        line = line.replace(r'\cdot', '*')
        line = line.replace(r'\div', '/')
        line = line.replace(r'\frac', '/')
        
        # 3. Clean up extra whitespace
        return line.strip()

    def extract_answer(text):
        # Pattern looks for everything between <answer> and </answer>
        # re.DOTALL allows the dot (.) to match newlines if the answer is multi-line
        match = re.findall(r'<answer>(.*?)</answer>', text, re.DOTALL)
        
        if match:
            return match[-1].strip()
        
        # If no tags exist, return the original string
        return text

    def vllm_encoder(obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj) # Fallback for any weird types inside

    # MAIN GRADING LOOP
    # loop through best_of_n
    for best_of_n in best_of_ns:
        # loop through the different countdown questions
        bon_outputs = outputs[best_of_n]
        bon_outputs["results"] = []
        bon_outputs["random_results"] = []
        bon_outputs["best_results"] = []
        bon_outputs["tourney_results"] = []
        bon_outputs["questions"] = prompts

        for i, (answer, all_answers, tourney_answer) in enumerate(zip(bon_outputs["Final Answers"], bon_outputs["All Answers"], bon_outputs["Tourney Answers"])):

            # model select score
            score = 1 if data.score_answer(answer=answer, entry=data[i]) == 1 else 0
            bon_outputs["results"].append((answer, score))

            # random score
            random_select = random.randrange(len(all_answers))
            random_score = 1 if data.score_answer(answer=all_answers[random_select], entry=data[i]) == 1 else 0
            bon_outputs["random_results"].append((all_answers[random_select], random_score))
            
            # best score
            best_ans, best_score = all_answers[0], 0  # Fallback if none are correct
            for ans in all_answers:
                if data.score_answer(answer=ans, entry=data[i]):
                    best_ans, best_score = ans, 1
                    break  # Stop immediately! We found a perfect score.
            bon_outputs["best_results"].append((best_ans, best_score)) 

            # tourney score
            tourney_score = 1 if data.score_answer(answer=tourney_answer, entry=data[i]) == 1 else 0
            bon_outputs["tourney_results"].append((tourney_answer, tourney_score)) 
            
        print(f"best_of_{best_of_n} score is: {float(sum(result[1] for result in bon_outputs["results"])) / num_examples} and used average token count of: {float(sum(bon_outputs["total_tokens"])) / num_examples}", file=sys.stderr)

    fname = f"{datetime.datetime.now()}_bon_{'_'.join(list(map(str, best_of_ns)))}_strategy_{strategy.name if strategy else "None"}_plan_{str(max_plan_tokens)}_prune_{str(prune_ratio)}.json"
    print(fname)
    with open(fname, "w") as f:
        json.dump(outputs, f, indent=4, default=vllm_encoder)
        
    def format_json_inplace(filepath, indent=4):
        # 1. Read the existing data
        with open(filepath, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"Error: {filepath} is not valid JSON.", file=sys.stderr)
                return

        # 2. Create the standard pretty-printed string
        # This ensures strings and objects are on new lines as requested
        pretty_json = json.dumps(data, indent=indent)

        # 3. Use Regex to find numeric arrays and collapse them
        # This matches '[' followed by numbers, commas, and whitespace, ending in ']'
        # It will NOT match ["a", "b"] because of the quote marks.
        numeric_array_pattern = r'\[(?:\s*-?[\d\.]+\s*,?)+\s*\]'

        def collapse_match(match):
            # Remove all newlines and extra spaces, then add a single space after commas
            collapsed = re.sub(r'\s+', '', match.group(0))
            return collapsed.replace(',', ', ')

        fixed_json = re.sub(numeric_array_pattern, collapse_match, pretty_json)

        # 4. Overwrite the original file
        with open(filepath, 'w') as f:
            f.write(fixed_json)

    format_json_inplace(fname)