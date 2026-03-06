from model.model import Model
from model.strategies import HypothesisStrategy, PlanStrategy, ConceptStrategy, ReasoningStructureStrategy, CountdownStrategy, UserStrategy, CompletionStrategy

import reasoning_gym
import re
import random
import sys

import datetime
import json

seed = 42
random.seed(seed)

# dataset hyperparameters
dataset_type = "countdown"
level = 6
num_examples = 2

# model hyperparameters
temperature = 0.9
best_of_ns = [4]# [1,2,4,8,16] # 32 is way too large for A40 right now...
model="Qwen/Qwen3-0.6B"

# initialize model
llm = Model(model, seed=seed)

# model strategy, set to None if not using
# strategy = UserStrategy(llm=llm.llm, seed=seed)
strategy = CountdownStrategy(llm=llm.llm, seed=seed)
# strategy = CompletionStrategy(llm=llm.llm, seed=seed)
# strategy = None

data = reasoning_gym.create_dataset(dataset_type, size=num_examples, min_numbers=level, max_numbers=level, seed=seed)
# load the questions
prompts = [entry["question"] for entry in data]

# generate responses
outputs = Model.generate_responses(llm, prompts, best_of_ns=best_of_ns, temperature=temperature, max_tokens=16384, strategy=strategy)

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
    match = re.search(r'<answer>(.*?)</answer>', text, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    # If no tags exist, return the original string
    return text

def vllm_encoder(obj):
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj) # Fallback for any weird types inside

# loop through best_of_n
for best_of_n in best_of_ns:
    # loop through the different countdown questions
    bon_outputs = outputs[best_of_n]
    outputs[best_of_n]["results"] = []
    outputs[best_of_n]["questions"] = prompts

    for i, request_outputs in enumerate(bon_outputs["responses"]):            
        # get the best score from the selected candidate solutions
        best_score_for_task = -1
        best_response_text = ""
        best_prompt = ""

        # print(request_outputs)
        for j, candidate in enumerate(request_outputs):
            # remove <think></think> tags to get solution
            match = re.search(r"(?<=<\/think>)\s*([\s\S]*)", candidate.text, re.DOTALL)
            candidate_text = match.group(1) if match else candidate.text  
            candidate_text = extract_answer(candidate_text)

            # print(f"===\nFor candidate, found best match : {}\n")
            
            # score the answer
            score = data.score_answer(answer=candidate_text, entry=data[i])
            if score != 1:
                score = 0

            # compare to see if it's the best solution
            if score > best_score_for_task:
                best_score_for_task = score
                best_response_text = candidate_text
                if bon_outputs["generated_diverse_prompts"]:
                    best_prompt = bon_outputs["generated_diverse_prompts"][i][j]
        
        # store best results
        outputs[best_of_n]["results"].append((best_prompt, best_response_text, best_score_for_task))

    print(f"best_of_{best_of_n} score is: {float(sum(result[2] for result in outputs[best_of_n]["results"])) / num_examples} and used average token count of: {float(sum(outputs[best_of_n]["total_tokens"])) / num_examples}")

with open(f"{datetime.datetime.now()}_bon_{'_'.join(list(map(str, best_of_ns)))}_strategy_{strategy.name if strategy else "None"}.json", "w") as f:
    json.dump(outputs, f, indent=4, default=vllm_encoder)