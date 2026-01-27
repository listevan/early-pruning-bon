from vllm import LLM, SamplingParams
import reasoning_gym

llm = LLM(model="Qwen/Qwen3-1.7B")

data = reasoning_gym.create_dataset("countdown", size=1000, seed=42)
prompts = [item["question"] for item in data]

sampling_params = SamplingParams(temperature=0.9, max_tokens=2048)
outputs = llm.generate(prompts, sampling_params)

for i, output in enumerate(outputs):
    output_text = output.outputs[0].text
    score = data.score_answer(answer=output_text, entry=data[i])
    print(f"Task {i} Score: {score}")