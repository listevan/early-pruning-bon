import re
import random
import datetime
import json
from datasets import load_dataset
from vllm import LLM, SamplingParams

seed = 42
random.seed(seed)

# dataset hyperparameters
num_examples = 30

# model hyperparameters
temperature = 0.9
best_of_ns = [1, 2, 4, 8]
model_name = "Qwen/Qwen3-4B-Instruct-2507"

# 1. Initialize vLLM model
print(f"Loading model {model_name}...")
llm = LLM(model=model_name, seed=seed, trust_remote_code=True)
tokenizer = llm.get_tokenizer()

# 2. Load LiveCodeBench Dataset
print("Loading LiveCodeBench dataset...")
# Make sure you are authenticated with huggingface if accessing a private/restricted LCB release
dataset = load_dataset("livecodebench/livecodebench", "release_v4", split="test")
dataset = dataset.select(range(num_examples))

# 3. Format prompts using the model's chat template
prompts = []
for entry in dataset:
    messages = [
        {"role": "system", "content": "You are an expert Python programmer. Write a Python function to solve the following problem. Think step by step, then enclose your final code in a ```python ... ``` block."},
        {"role": "user", "content": entry["content"]} # 'content' holds the problem description in LCB
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    prompts.append(prompt)

# 4. Generate responses with vLLM
max_n = max(best_of_ns)
sampling_params = SamplingParams(
    n=max_n,
    temperature=temperature,
    max_tokens=4096,
    seed=seed
)

print(f"Generating responses with vLLM for {num_examples} prompts...")
vllm_outputs = llm.generate(prompts, sampling_params)

def extract_python_code(text):
    # Remove <think></think> tags to get the solution portion
    match = re.search(r"(?<=<\/think>)\s*([\s\S]*)", text, re.DOTALL)
    content = match.group(1) if match else text  
    
    # Extract code from ```python ... ``` blocks
    code_match = re.search(r'```python ... (.*?)```', content, re.DOTALL | re.IGNORECASE)
    if code_match:
        return code_match.group(1).strip()
    
    # Fallback to any generic code block
    fallback_match = re.search(r'```(.*?)```', content, re.DOTALL)
    if fallback_match:
        return fallback_match.group(1).strip()
        
    return content.strip()

def vllm_encoder(obj):
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj)

# 5. Process and format results
outputs = {n: {"results": [], "questions": prompts, "total_tokens": []} for n in best_of_ns}

for i, request_output in enumerate(vllm_outputs):
    # vLLM returns a list of outputs corresponding to the n parameter
    candidates = request_output.outputs
    prompt_tokens = len(request_output.prompt_token_ids)
    
    for n in best_of_ns:
        # Isolate the first 'n' candidate generations
        n_candidates = candidates[:n]
        
        extracted_codes = []
        gen_tokens = 0
        
        for candidate in n_candidates:
            raw_text = candidate.text
            code = extract_python_code(raw_text)
            extracted_codes.append(code)
            gen_tokens += len(candidate.token_ids)
            
        outputs[n]["results"].append({
            "question_id": dataset[i].get("question_id", str(i)),
            "candidates": extracted_codes # To compute Pass@K later in a sandbox
        })
        
        outputs[n]["total_tokens"].append(prompt_tokens + gen_tokens)

for n in best_of_ns:
    avg_tokens = float(sum(outputs[n]["total_tokens"])) / num_examples
    print(f"best_of_{n} used average token count of: {avg_tokens:.1f}")

# 6. Save generations to file
fname = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_lcb_bon_{'_'.join(map(str, best_of_ns))}.json"
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
print(f"Outputs saved and formatted in {fname}")