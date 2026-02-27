from model.model import Model
from model.strategies import HypothesisStrategy, PlanStrategy, ConceptStrategy, ReasoningStructureStrategy, CountdownStrategy, UserStrategy

import reasoning_gym
import re
import random
import sys

import datetime
import json

# TODO: set seed for vllm, save everything (intermediate steps like the prompts, selections/indexes), plot score vs token counts, try user strategy, maybe try skipping structure outputs
# "\n\nProvide your solution as a arithmetic expression (no '=' sign).\n"
#         "2. Do not include the target number in the expression.\n"
#         "3. Use '*' for multiplication.\n"
#         "4. Use '/' for division.\n"
#         # "5.\n\n"
#         # "Additional format requirements:\n"
#         # "Show your thinking in <think> your reasoning here </think> followed by the final answer in <answer></answer>.\n"
#         # "Do not include any other text or formatting for the final answer."
#     )

# dataset hyperparameters
dataset_type = "countdown"
level = 6
num_examples = 100

# model hyperparameters
temperature = 0.9
best_of_ns = [8]# [1,2,4,8,16] # 32 is way too large for A40 right now...
model="Qwen/Qwen3-0.6B"

# initialize model
llm = Model(model)
# model strategy, set to None if not using
# strategy_name = "UserStrategy"
# strategy = UserStrategy(llm=llm.llm)

strategy_name = "None" # "CountdownStrategy"
strategy = None # CountdownStrategy(llm=llm.llm)

data = reasoning_gym.create_dataset(dataset_type, size=num_examples, seed=42, min_numbers=level, max_numbers=level)
# load the questions
prompts = [entry["question"] for entry in data]

# generate responses
outputs = Model.generate_responses(llm, prompts, best_of_ns=best_of_ns, temperature=temperature, max_tokens=16384)

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
        best_num_tokens = -1
        
        # get the total number of tokens used for this question
        total_num_tokens = 0

        for prompt, candidate in zip(bon_outputs["generated_diverse_prompts"], request_outputs):
            # remove <think></think> tags to get solution
            match = re.search(r"(?<=<\/think>)\s*([\s\S]*)", candidate.text, re.DOTALL)
            candidate_text = match.group(1) if match else candidate.text  
            candidate_text = extract_answer(candidate_text)

            # print(f"===\nFor candidate, found best match : {}\n")
            
            # score the answer
            score = data.score_answer(answer=candidate_text, entry=data[i])
            target_number = data[i]['metadata']['target']
            ground_truth_expr = data[i]['metadata']['expression'] # 3 + 56 - 10 / 8 + 43
            ground_truth_num_list = data[i]['metadata']['numbers'] # [3, 56, 10, 43, 8]
            if score < 1:
                lines = candidate_text.strip().split('\n')
                for line in reversed(lines):
                    match = re.findall(r'\d+', line)
                    if 3 <= len(match) <= 6 and ("*" in line or "/" in line or "+" in line or "-" in line or ("(" in line and ")" in line) or "\\times" in line or "\\boxed" in line):
                        clean_line = clean_math_string(line)
                        score = data.score_answer(answer=line, entry=data[i])
                        # print("\n\n\n\n\n")
                        # print(candidate_text)
                        # print(f"\n===>>>\n\t Reduced:: {line} --> {clean_line}, where TARGET is: {target_number} \n \tFound our number line: {match} with new score: {new_score} vs old score: {score} ===<<<\n")
                        # print("\n\n\n\n\n")
                        break
                if score != 1:
                    score = 0

            # compare to see if it's the best solution
            if score > best_score_for_task:
                best_score_for_task = score
                best_response_text = candidate_text
                best_prompt = prompt
        
        # store best results
        outputs[best_of_n]["results"].append((best_prompt, best_response_text, best_score_for_task))

    print(f"best_of_{best_of_n} score is: {float(sum(result[0] for result in outputs[best_of_n]["results"])) / len(outputs)} and used average token count of: {float(sum(outputs[best_of_n]["total_tokens"])) / len(outputs)}")

with open(f"{}_bon_{"_".join(best_of_ns)}.json", "w") as f:
    json.dumps(outputs, indent=4)