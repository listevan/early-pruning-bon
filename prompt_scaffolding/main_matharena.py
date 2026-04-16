from model.model import Model
from model.strategies import HypothesisStrategy, PlanStrategy, ConceptStrategy, ReasoningStructureStrategy, CountdownStrategy, UserStrategy, CompletionStrategy

from datasets import load_dataset
import re
import random
import sys
import datetime
import json

matharena_path = "/u/stevex2/prompt_scaffolding/CS497/matharena/src"
if matharena_path not in sys.path:
    sys.path.append(matharena_path)
from matharena.parser import extract_answer, parse_answer, check_answers

seed = 42
random.seed(seed)

dataset_path = "MathArena/hmmt_feb_2025"
dataset_split = "train" # no test set...
num_examples = 30

temperature = 1.0
best_of_ns = [2]
model = "Qwen/Qwen3-4B-Instruct-2507" 

llm = Model(model, seed=seed)

strategy = None # CompletionStrategy(llm=llm.llm, seed=seed)

data = load_dataset(dataset_path, split=dataset_split)

if len(data) > num_examples:
    data = data.shuffle(seed=seed).select(range(num_examples)) # random shuffle, but 30 problems max

prompts = [entry["problem"] for entry in data]
true_answers = [str(entry["answer"]) for entry in data]

outputs = llm.generate_responses(prompts, best_of_ns=best_of_ns, temperature=temperature, max_tokens=16384, strategy=strategy)


def vllm_encoder(obj):
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)

for best_of_n in best_of_ns:
    bon_outputs = outputs[best_of_n]
    outputs[best_of_n]["results"] = []
    outputs[best_of_n]["questions"] = prompts
    outputs[best_of_n]["true_answers"] = true_answers

    for i, request_outputs in enumerate(bon_outputs["responses"]):            
        best_score_for_task = -1
        best_response_text = ""
        best_prompt = ""

        for j, candidate in enumerate(request_outputs):
            match = re.search(r"(?<=<\/think>)\s*([\s\S]*)", candidate.text, re.DOTALL)
            candidate_text = match.group(1) if match else candidate.text  
            
            match_answer = re.search(r'<answer>(.*?)</answer>', candidate_text, re.DOTALL)
            # import pdb; pdb.set_trace()
            if match_answer:
                candidate_text = candidate_text.replace(match_answer.group(0), f"\\boxed{{{match_answer.group(1).strip()}}}")
            
            pred_val, _ = extract_answer(candidate_text, strict_parsing=False, parse=True)
            expected_val, _ = parse_answer(str(true_answers[i]))
            
            score = 1 if check_answers(pred_val, expected_val) else 0

            if score != 1:
                score = 0

            if score > best_score_for_task:
                best_score_for_task = score
                best_response_text = candidate_text
                if bon_outputs["generated_diverse_prompts"]:
                    best_prompt = bon_outputs["generated_diverse_prompts"][i][j]
        print("Best response text:", pred_val, " with score", score, "-> ans is: ", true_answers[i])
        outputs[best_of_n]["results"].append((best_prompt, best_response_text, best_score_for_task))

    print(f"best_of_{best_of_n} score is: {float(sum(result[2] for result in outputs[best_of_n]['results'])) / num_examples} and used average token count of: {float(sum(outputs[best_of_n]['total_tokens'])) / num_examples}")

fname = f"{datetime.datetime.now()}_bon_{'_'.join(list(map(str, best_of_ns)))}_strategy_{strategy.name if strategy else 'None'}.json"
with open(fname, "w") as f:
    json.dump(outputs, f, indent=4, default=vllm_encoder)
    
def format_json_inplace(filepath, indent=4):
    with open(filepath, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: {filepath} is not valid JSON.")
            return

    pretty_json = json.dumps(data, indent=indent)
    numeric_array_pattern = r'\[(?:\s*-?[\d\.]+\s*,?)+\s*\]'

    def collapse_match(match):
        collapsed = re.sub(r'\s+', '', match.group(0))
        return collapsed.replace(',', ', ')

    fixed_json = re.sub(numeric_array_pattern, collapse_match, pretty_json)

    with open(filepath, 'w') as f:
        f.write(fixed_json)

format_json_inplace(fname)
