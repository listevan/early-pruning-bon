from model.strategies import HypothesisStrategy, PlanStrategy, ConceptStrategy, ReasoningStructureStrategy, CountdownStrategy, UserStrategy

from vllm import LLM, SamplingParams
import random
import sys

answer_instruction = """
    \n\nProvide your solution as a arithmetic expression (no '=' sign).\n
    2. Do not include the target number in the expression.\n
    3. Use '*' for multiplication.\n
    4. Use '/' for division.\n
    5. Do not use × for multiplication\n
    6. Additional format requirements:\n
    Show your thinking in <think> your reasoning here </think> followed by the final answer in <answer></answer>.\n
    Do not include any other text or formatting for the final answer.
"""

# TODO: control generation with <answer></answer> token
class Model:
    def __init__(self, model_name: str):
        self.llm = LLM(model=model_name, tensor_parallel_size=1)

    def generate_responses(self, prompts, best_of_ns, temperature, max_tokens=16384, strategy=None):
        # see if user decided to use a strategy
        if strategy:
            organized_outputs = {}

            # loop through the best_of_ns to run diversification and generation for each n
            for i, best_of_n in enumerate(best_of_ns):
                # if so, use the strategy to generate a set of diverse prompts (from the original best_of_n), ignore formatting part of the prompt
                organized_outputs[best_of_n] = strategy.generate_prompts([[{"role": "user", "content": prompt.split("\n")[0]}] for prompt in prompts], best_of_n, temperature)
                new_request_prompts, total_tokens = organized_outputs[best_of_n]["new_request_prompts"], organized_outputs[best_of_n]["total_tokens"]

                organized_outputs[best_of_n]["responses"] = []
                
                # define sampling parameters with user hyperparameters
                sampling_params = SamplingParams(temperature=temperature, top_p=0.95, max_tokens=max_tokens)
                
                # loop through the question prompts and then through diversified prompts to generate the results
                for j, (diverse_request_prompts, og_prompt) in enumerate(zip(new_request_prompts, prompts)):
                    # format the diversified prompt by prepending the original prompt and putting into qwen format
                    formatted_variants = [[{"role": "user", "content": og_prompt + "\n" + diverse_prompt + answer_instruction}] for diverse_prompt in diverse_request_prompts]
                    # print("====\nFormatted variants: \n", formatted_variants, "====\n\n")

                    # generate results from the formatted variants
                    outputs = self.llm.chat(formatted_variants, sampling_params=sampling_params)
                    
                    organized_outputs[best_of_n]["responses"].append([request_output.outputs[0] for request_output in outputs])
                    organized_outputs[best_of_n]["total_tokens"] += sum(len(request_output.outputs[0].token_ids) for request_output in outputs)

            return organized_outputs
        else:
            print("Strategy is none...")
            # if not use user hyperparameters to generate results from prompt
            sampling_params = SamplingParams(n=max(best_of_ns), temperature=temperature, top_p=0.95, max_tokens=max_tokens)
            print(prompts)
            outputs = self.llm.chat([[{"role": "user", "content": prompt}] for prompt in prompts], sampling_params=sampling_params)

            # loop through questions to create a dictionary for each of the best_of_n results
            organized_outputs = {}
            
            for best_of_n in best_of_ns:
                organized_outputs[best_of_ns] = {"generated_prompts": [], "indexes": [], "generated_diverse_prompts": [], "total_tokens": 0, "responses": []}

                for i, request_output in enumerate(outputs):
                    selected = random.sample(range(max(best_of_ns)), best_of_n)
                    organized_outputs[best_of_n]["responses"].append([request_output.outputs[select] for select in selected])
                    organized_outputs[best_of_n]["total_tokens"] += sum(len(bon_output.token_ids) for bon_output in organized_outputs[best_of_n]["responses"])

            return organized_outputs