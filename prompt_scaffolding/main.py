from vllm import LLM, SamplingParams
import reasoning_gym

import re

dataset_type = "countdown"
num_examples = 100
temperature = 0.7 # 0.4
best_of_ns = [1,2,4,8,16,32]
model="Qwen/Qwen3-1.7B"

data = reasoning_gym.create_dataset(dataset_type, size=num_examples, seed=42, min_numbers=5, max_numbers=5)

prompts = []
for entry in data:
    prompts.append([{"role": "user", "content": entry["question"]}])

llm = LLM(model=model)

for best_of_n in best_of_ns:
    sampling_params = SamplingParams(n=best_of_n, temperature=temperature, top_p=0.95, max_tokens=16384)

    outputs = llm.chat(prompts, sampling_params = sampling_params)

    total_score = 0
    lines = []
    for i, output in enumerate(outputs):
        best_score_for_task=-1
        best_response_text=""

        for candidate in output.outputs:
            match = re.search(r"(?<=<\/think>)\s*([\s\S]*)", candidate.text, re.DOTALL)
            candidate_text = match.group(1) if match else candidate.text
            score = data.score_answer(answer=candidate_text, entry=data[i])
            
            if score > best_score_for_task:
                best_score_for_task = score
                best_response_text = candidate_text
                
        total_score += best_score_for_task
        lines.append(f"Task {i} Score: {best_score_for_task}\n------------------------\nQuestion {data[i]['question']}\n------------------------\nResponse {candidate_text}\n-------------------------------------------")

    filename = f"{model.replace(".", "_").replace("/", "_")}_n={best_of_n}_t={temperature}_{dataset_type}_n={num_examples}.txt"
    with open(filename, "w") as f:
        f.write("\n".join(lines))

    print(f"best_of_{best_of_n} score is: {total_score / len(outputs)}")
