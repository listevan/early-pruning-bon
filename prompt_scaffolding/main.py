from vllm import LLM, SamplingParams
import reasoning_gym

num_examples = 1
data = reasoning_gym.create_dataset("countdown", size=num_examples, seed=42)

prompts = []
for entry in data:
    prompts.append([{"role": "user", "content": entry["question"]}])

sampling_params = SamplingParams(temperature=0, max_tokens=1024)
llm = LLM(model="Qwen/Qwen3-1.7B")

total_score = 0
for i, prompt in enumerate(prompts):
    outputs = llm.chat(prompt, sampling_params = sampling_params)
    output_text = outputs[0].outputs[0].text
    score = data.score_answer(answer=output_text, entry=data[i])
    total_score += score
    print(f"Task {i} Score: {score}")
    print(f"Question {data[i]['question']}\n----------------\nResponse {output_text}")

print(total_score / len(outputs))
