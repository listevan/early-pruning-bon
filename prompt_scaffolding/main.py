from model.model import Model
from model.strategies import HypothesisStrategy, PlanStrategy, ConceptStrategy, ReasoningStructureStrategy, CountdownStrategy, UserStrategy

import reasoning_gym
import re
import random
import sys

# TODO: try removing formatting instruction, try bringing formatting instruction to end (maybe), run on 100 examples
# TODO: use user ideas or information (simple and lightweight 8 ideas, maybe solution to countdown level 3) to bias the model and also compare solutions to diverse best-of-8 approach and non-scaffolding best of 8

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

            # score the answer
            score = data.score_answer(answer=candidate_text, entry=data[i])
            # import pdb; pdb.set_trace()

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
