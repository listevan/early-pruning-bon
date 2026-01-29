from vllm import LLM, SamplingParams
import reasoning_gym

import re

num_examples = 100
data = reasoning_gym.create_dataset("countdown", size=num_examples, seed=42)

prompts = []
for entry in data:
    prompts.append([{"role": "user", "content": entry["question"]}])

sampling_params = SamplingParams(temperature=0.4, max_tokens=16384)
llm = LLM(model="Qwen/Qwen3-1.7B")

outputs = llm.chat(prompts, sampling_params = sampling_params)

total_score = 0
for i, output in enumerate(outputs):
    output_text = re.search(r"(?<=<\/think>)\s*([\s\S]*)", output.outputs[0].text, re.DOTALL)
    if output_text:
        output_text = output_text.group(1)
        score = data.score_answer(answer=output_text, entry=data[i])
    else:
        output_text = ""
        score = 0
    total_score += score
    print(f"Task {i} Score: {score}")
    print(f"Question {data[i]['question']}\n----------------\nResponse {output_text}")

print(total_score / len(outputs))
