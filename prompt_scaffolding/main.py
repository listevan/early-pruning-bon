from model.model import Model
from model.strategies import HypothesisStrategy, PlanStrategy, ConceptStrategy, ReasoningStructureStrategy, CountdownStrategy

import reasoning_gym
import re
import random

dataset_type = "countdown"
level = 6
num_examples = 100

temperature = 0.9 
# best_of_ns = [1,2,4,8,16,32]
best_of_ns = [1,2,4,8,16] # 32 is way too large for A40 right now...
model="Qwen/Qwen3-0.6B"

data = reasoning_gym.create_dataset(dataset_type, size=num_examples, seed=42, min_numbers=level, max_numbers=level)

prompts = []
for entry in data:
    prompts.append([{"role": "user", "content": entry["question"]}])

llm = Model(model)
strategy = HypothesisStrategy(llm=llm.llm)
strategy_name = "HypothesisStrategy"

outputs = Model.generate_responses(llm, prompts, best_of_n=max(best_of_ns), temperature=temperature, max_tokens=16384, strategy=strategy)

results_per_n = {n: [] for n in best_of_ns}
scores_per_n = {n: 0 for n in best_of_ns}

for i, request_output in enumerate(outputs):
    all_candidates = request_output.outputs
    
    for best_of_n in best_of_ns:
        # import pdb; pdb.set_trace()
        # if best_of_n < len(all_candidates):
            # selected_candidates = random.sample(all_candidates, best_of_n)
        # else:
        selected_candidates = random.sample(all_candidates, 1)
        
        best_score_for_task = -1
        best_response_text = ""
        best_num_tokens = -1

        for candidate in selected_candidates:
            num_tokens = len(candidate.token_ids)
            match = re.search(r"(?<=<\/think>)\s*([\s\S]*)", candidate.text, re.DOTALL)
            candidate_text = match.group(1) if match else candidate.text
            score = data.score_answer(answer=candidate_text, entry=data[i])
            
            if score > best_score_for_task:
                best_score_for_task = score
                best_response_text = candidate_text
                best_num_tokens = num_tokens
        
        scores_per_n[best_of_n] += best_score_for_task
        results_per_n[best_of_n].append(f"Task {i}, Num Tokens: {best_num_tokens}, Score: {best_score_for_task}\n------------------------\nQuestion {data[i]['question']}\n------------------------\nResponse {best_response_text}\n-------------------------------------------")
    print(f"Finished {i}")
    

for best_of_n in best_of_ns:
    filename = f"{model.replace('.', '_').replace('/', '_')}_n={best_of_n}_t={temperature}_{dataset_type}_n={num_examples}_{strategy_name}.txt"
    with open(filename, "w") as f:
        f.write("\n".join(results_per_n[best_of_n]))
    
    print(f"best_of_{best_of_n} score is: {scores_per_n[best_of_n] / len(outputs)}")