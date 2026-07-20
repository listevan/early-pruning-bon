from model.model import Model
from model.strategies import HypothesisStrategy, PlanStrategy, ConceptStrategy, ReasoningStructureStrategy, CountdownStrategy, UserStrategy, CompletionStrategy
from model.utils import extract_answer, vllm_encoder, format_json_inplace

import reasoning_gym
import re
import random
import sys

import datetime
import json
import argparse
import statistics
import os

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
    parser.add_argument(
        "--baseline", 
        action="store_true", 
        help="Run baseline generation (no strategy)."
    )
    parser.add_argument(
        "--cache_fn", 
        type=str, 
        default="", 
        help="Path to raw baseline cache file."
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

    # Optional path gating: ONLY_PATHS="tourney" reruns just the tourney pruning path off the
    # cache (rank/random completions are skipped). Defaults to all three.
    ALL_PATHS = ["rank", "random", "tourney"]
    only_paths_env = os.environ.get("ONLY_PATHS", "").strip()
    if only_paths_env:
        active_paths = [p.strip() for p in only_paths_env.split(",") if p.strip()]
        invalid = [p for p in active_paths if p not in ALL_PATHS]
        if invalid or not active_paths:
            print(f"Error: ONLY_PATHS={only_paths_env!r} invalid; choose from {ALL_PATHS}", file=sys.stderr)
            sys.exit(1)
    else:
        active_paths = ALL_PATHS

    # initialize model
    model="Qwen/Qwen3-4B-Instruct-2507"
    # model = "Qwen/Qwen3-0.6B"
    llm = Model(model, num_gpus, seed=seed)

    # Configure strategy based on command line flag
    if args.baseline:
        strategy = None
    else:
        strategy = CompletionStrategy(llm=llm.llm, seed=seed)

    # Load from cache file if provided
    if args.cache_fn:
        try:
            with open(args.cache_fn, "r") as f:
                previous_responses = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Cache file {args.cache_fn} not found. Running from scratch.", file=sys.stderr)
            previous_responses = None
    else:
        previous_responses = None

    data = reasoning_gym.create_dataset(dataset_type, size=num_examples, min_numbers=level, max_numbers=level, seed=seed)
    # load the questions
    prompts = [entry["question"] for entry in data]

    # generate responses
    outputs = llm.generate_responses(prompts, best_of_ns=best_of_ns, temperature=temperature, max_tokens=16384, max_plan_tokens=max_plan_tokens, strategy=strategy, prune_ratio=prune_ratio, previous_responses=previous_responses, group_size=group_size, active_paths=active_paths)
    
    # Intercept and save the raw baseline cache if in baseline mode
    raw_base = outputs.pop("raw_base_responses", None)
    if args.baseline and raw_base:
        with open("baseline_cache.json", "w") as f:
            json.dump(raw_base, f)
        print("Saved raw baseline generations to baseline_cache.json", file=sys.stderr)

    # MAIN GRADING LOOP
    
    # Process only relevant output branches based on strategy choice
    paths_to_process = ["baseline"] if strategy is None else active_paths
    
    for path in paths_to_process:
        path_outputs = {}
        print(f"\n--- Evaluating Path: {path} ---", file=sys.stderr)
        
        for best_of_n in best_of_ns:
            bon_data = outputs[path].get(best_of_n)
            if not bon_data: continue
            
            chunks = bon_data["chunks"]
            num_chunks = len(chunks)
            
            # Aggregate storage mapping to each individual prompt
            agg_results = [[] for _ in range(num_examples)]
            agg_random_results = [[] for _ in range(num_examples)]
            agg_best_results = [[] for _ in range(num_examples)]
            agg_tourney_results = [[] for _ in range(num_examples)]
            prompt_token_usage = [[] for _ in range(num_examples)]
            tourney_token_usage = [[] for _ in range(num_examples)]

            # 1. Gather scores dynamically across all chunks for this BoN
            for chunk in chunks:
                # total_tokens costs the model-select path; the tourney curve must be charged
                # its OWN cost (tourney_total_tokens), which differs in the selection component.
                for i, (answer, all_answers, tourney_answer, tokens, tourney_tokens) in enumerate(zip(chunk["Final Answers"], chunk["All Answers"], chunk["Tourney Answers"], chunk["total_tokens"], chunk["tourney_total_tokens"])):
                    # Model final select score
                    score = 1 if data.score_answer(answer=answer, entry=data[i]) == 1 else 0
                    
                    # Random selection score
                    random_select = random.randrange(len(all_answers))
                    random_score = 1 if data.score_answer(answer=extract_answer(all_answers[random_select]), entry=data[i]) == 1 else 0
                    
                    # Best possible score (ceiling)
                    best_ans, best_score = all_answers[0], 0
                    for ans in all_answers:
                        if data.score_answer(answer=extract_answer(ans), entry=data[i]) == 1:
                            best_ans, best_score = ans, 1
                            break
                            
                    # Tourney logic selection score
                    tourney_score = 1 if data.score_answer(answer=tourney_answer, entry=data[i]) == 1 else 0
                    
                    agg_results[i].append({"answer": answer, "score": score})
                    agg_random_results[i].append({"answer": all_answers[random_select], "score": random_score})
                    agg_best_results[i].append({"answer": best_ans, "score": best_score})
                    agg_tourney_results[i].append({"answer": tourney_answer, "score": tourney_score})

                    prompt_token_usage[i].append(tokens)
                    tourney_token_usage[i].append(tourney_tokens)

            # 2. Compile metrics into the uniform JSON layout requested
            final_metrics = {
                "questions": prompts,
                "dataset_metrics": {},
                "prompt_metrics": []
            }
            
            all_dataset_tokens = []
            total_score = 0
            
            for i in range(num_examples):
                scores = [res["score"] for res in agg_results[i]]
                tokens = prompt_token_usage[i]
                tourney_tokens = tourney_token_usage[i]

                mean_score = statistics.mean(scores)
                total_score += mean_score

                mean_tokens = statistics.mean(tokens)
                std_tokens = statistics.stdev(tokens) if len(tokens) > 1 else 0.0
                tourney_mean_tokens = statistics.mean(tourney_tokens) if tourney_tokens else mean_tokens

                final_metrics["prompt_metrics"].append({
                    "mean_score": mean_score,
                    "mean_tokens": mean_tokens,
                    "std_tokens": std_tokens,
                    "tourney_mean_tokens": tourney_mean_tokens,
                    "chunks_data": {
                        "results": agg_results[i],
                        "random_results": agg_random_results[i],
                        "best_results": agg_best_results[i],
                        "tourney_results": agg_tourney_results[i]
                    }
                })
                
                all_dataset_tokens.extend(tokens)
                
            # Dataset-wide global token distributions
            dataset_mean_tokens = statistics.mean(all_dataset_tokens) if all_dataset_tokens else 0
            dataset_std_tokens = statistics.stdev(all_dataset_tokens) if len(all_dataset_tokens) > 1 else 0.0
            
            final_metrics["dataset_metrics"] = {
                "average_score": total_score / num_examples,
                "mean_tokens": dataset_mean_tokens,
                "std_tokens": dataset_std_tokens,
                "num_chunks_averaged": num_chunks
            }
            
            path_outputs[best_of_n] = final_metrics
            print(f"Path: {path} | best_of_{best_of_n} avg score: {final_metrics['dataset_metrics']['average_score']:.4f} | avg tokens: {dataset_mean_tokens:.2f}", file=sys.stderr)

        # 3. Save isolated, perfectly formatted JSON file for each valid path
        time_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        strat_name = strategy.name if strategy else "None"
        bons_str = '_'.join(map(str, best_of_ns))
        
        fname = f"{time_str}_{path}_bon_{bons_str}_strat_{strat_name}_plan_{max_plan_tokens}_prune_{prune_ratio}.json"
        print(f"Saving format fixed JSON to: {fname}")
        
        with open(fname, "w") as f:
            json.dump(path_outputs, f, indent=4, default=vllm_encoder)

        format_json_inplace(fname)