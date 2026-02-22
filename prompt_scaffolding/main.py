from model.model import Model
from model.strategies import HypothesisStrategy, PlanStrategy, ConceptStrategy, ReasoningStructureStrategy, CountdownStrategy, UserStrategy

import reasoning_gym
import re
import random
import sys

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
num_examples = 10

# model hyperparameters
temperature = 0.9
best_of_ns = [8]# [1,2,4,8,16] # 32 is way too large for A40 right now...
model="Qwen/Qwen3-0.6B"

# initialize model
llm = Model(model)
# model strategy, set to None if not using
strategy = CountdownStrategy(llm=llm.llm)
strategy_name = "CountdownStrategy"

data = reasoning_gym.create_dataset(dataset_type, size=num_examples, seed=42, min_numbers=level, max_numbers=level)
# load the questions
prompts = [entry["question"] for entry in data]

# generate responses
outputs, intermediate_tokens = Model.generate_responses(llm, prompts, best_of_ns=best_of_ns, temperature=temperature, max_tokens=16384, strategy=strategy)

# initialize result dictionaries
results_per_n = {n: [] for n in best_of_ns}
scores_per_n = {n: [] for n in best_of_ns}
tokens_per_n = {n: [] for n in best_of_ns}

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

# loop through the different countdown questions
for i, request_output in enumerate(outputs):
    # import pdb; pdb.set_trace()
    # get all of the n results for question i
    
    # loop through best_of_n
    for best_of_n in best_of_ns:
        # get the best_of_n result from the candidates
        selected_candidates = request_output[best_of_n]
        
        # get the best score from the selected candidate solutions
        best_score_for_task = -1
        best_response_text = ""
        best_prompt = ""
        best_num_tokens = -1
        
        # get the total number of tokens used for this question
        total_num_tokens = 0

        for prompt, candidate in zip(selected_candidates["prompts"], selected_candidates["responses"]):
            # get number of tokens and intermediate tokens
            num_tokens = len(candidate.token_ids)
            total_num_tokens += num_tokens + intermediate_tokens[best_of_n]
            
            # remove <think></think> tags to get solution
            match = re.search(r"(?<=<\/think>)\s*([\s\S]*)", candidate.text, re.DOTALL)
            candidate_text = match.group(1) if match else candidate.text

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
                        new_score = data.score_answer(answer=line, entry=data[i])
                        # print("\n\n\n\n\n")
                        # print(candidate_text)
                        # print(f"\n===>>>\n\t Reduced:: {line} --> {clean_line}, where TARGET is: {target_number} \n \tFound our number line: {match} with new score: {new_score} vs old score: {score} ===<<<\n")
                        # print("\n\n\n\n\n")
                        break

            # compare to see if it's the best solution
            if score > best_score_for_task:
                best_score_for_task = score
                best_response_text = candidate_text
                best_prompt = prompt
        
        # store best results
        scores_per_n[best_of_n].append(best_score_for_task)
        results_per_n[best_of_n].append(f"Task {i}, Num Tokens: {total_num_tokens}, Score: {best_score_for_task}\n------------------------\nQuestion {best_prompt[0]["content"]}\n------------------------\nResponse {best_response_text}\n-------------------------------------------")

        # store number of tokens used in total for task
        tokens_per_n[best_of_n].append(total_num_tokens)

from datetime import datetime
now = datetime.now()
formatted_datetime = now.strftime("%Y-%m-%d-%H-%M")

# save results to file
for best_of_n in best_of_ns:
    filename = f"{model.replace('.', '_').replace('/', '_')}_n={best_of_n}_t={temperature}_{dataset_type}_n={num_examples}_{strategy_name}_{formatted_datetime}.txt"
    with open(filename, "w") as f:
        f.write("\n".join(results_per_n[best_of_n]))
    
    print(f"best_of_{best_of_n} score is: {float(sum(scores_per_n[best_of_n])) / len(outputs)} and used average token count of: {float(sum(tokens_per_n[best_of_n])) / len(outputs)}")
