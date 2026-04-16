from model.strategies import HypothesisStrategy, PlanStrategy, ConceptStrategy, ReasoningStructureStrategy, CountdownStrategy, UserStrategy

from vllm import LLM, SamplingParams
from vllm.sampling_params import StructuredOutputsParams
import random
import sys

answer_instruction = """
    1. Do not attempt to answer with "0" if you do not know the solution. Attempt to solve the problem and provide a feasible answer.
"""

class Model:
    def __init__(self, model_name: str, seed=42):
        self.llm = LLM(model=model_name, tensor_parallel_size=1, max_model_len=65536, gpu_memory_utilization=0.4)
        self.seed = seed

    def generate_responses(self, prompts, best_of_ns, temperature, max_tokens=16384, strategy=None, previous_responses=None):
        # see if user decided to use a strategy
        if strategy:
            organized_outputs = {}

            # loop through the best_of_ns to run diversification and generation for each n
            for i, best_of_n in enumerate(best_of_ns):
                # if so, use the strategy to generate a set of diverse prompts (from the original best_of_n), ignore formatting part of the prompt
                if previous_responses is None:
                    bon_previous_responses = None
                else:
                    bon_previous_responses = previous_responses[str(best_of_n)]
                organized_outputs[best_of_n] = strategy.generate_prompts(prompts, best_of_n, temperature, previous_responses=bon_previous_responses)
                new_request_prompts = organized_outputs[best_of_n]["generated_diverse_prompts"]

                organized_outputs[best_of_n]["responses"] = []
                
                # define sampling parameters with user hyperparameters     
                sampling_params = SamplingParams(temperature=temperature, top_p=0.95, stop=["</answer>"], include_stop_str_in_output=True, max_tokens=max_tokens, seed=self.seed)
                
                # loop through the question prompts and then through diversified prompts to generate the results
                for j, (diverse_request_prompts, og_prompt) in enumerate(zip(new_request_prompts, prompts)):
                    if previous_responses is None: # if we're regenerating
                        if strategy.name == "CompletionStrategy":
                            formatted_variants = [f"<|im_start|>system\nAfter thinking, ensure the final formatted answer is within <answer></answer> tags and follows these instructions: {answer_instruction}.<|im_end|>\n<|im_start|>user\n{og_prompt}<|im_end|>\n<|im_start|>assistant\n{diverse_prompt}" for diverse_prompt in diverse_request_prompts]
                            outputs = self.llm.generate(formatted_variants, sampling_params=sampling_params)
                        else:
                            formatted_variants = [[{"role": "system", "content": f"After thinking, ensure the final formatted answer is within <answer></answer> tags and follows these instructions: {answer_instruction}."}, {"role": "user", "content": og_prompt + "\n" + diverse_prompt + answer_instruction}] for diverse_prompt in diverse_request_prompts]
                            outputs = self.llm.chat(formatted_variants, sampling_params=sampling_params)
                        
                        organized_outputs[best_of_n]["responses"].append([request_output.outputs[0] for request_output in outputs])
                        organized_outputs[best_of_n]["total_tokens"][j] += sum(len(request_output.outputs[0].token_ids) for request_output in outputs)
                    else:
                        # use indexes to choose the responses and get total_tokens
                        organized_outputs[best_of_n]["responses"].append([previous_responses[str(best_of_n)][j][index] for index in organized_outputs[best_of_n]["indexes"][j] if index < len(previous_responses[j])])
                        organized_outputs[best_of_n]["total_tokens"][j] += sum(len(response["token_ids"]) for response in organized_outputs[best_of_n]["responses"][-1])

                    organized_outputs[best_of_n]["full_responses"] = []
                    for e in range(len(outputs)):
                        full_response = diverse_request_prompts[e] + outputs[e].outputs[0].text
                        organized_outputs[best_of_n]["full_responses"].append(full_response)
                    
            return organized_outputs
        else:
            print("Strategy is none...")
            # if not use user hyperparameters to generate results from prompt
            sampling_params = SamplingParams(n=max(best_of_ns), temperature=temperature, top_p=1, max_tokens=max_tokens, seed=self.seed)
            # Pass system prompt and answer_instructions when no strategy is used
            outputs = self.llm.chat([[
                {"role": "system", "content": f"After thinking, ensure the final formatted answer is within <answer></answer> tags and follows these instructions: {answer_instruction}."},
                {"role": "user", "content": prompt + "\n" + answer_instruction}
            ] for prompt in prompts], sampling_params=sampling_params)

            # loop through questions to create a dictionary for each of the best_of_n results
            organized_outputs = {}
            
            for best_of_n in best_of_ns:
                organized_outputs[best_of_n] = {"generated_prompts": [], "indexes": [], "generated_diverse_prompts": [], "total_tokens": [], "responses": []}

                for i, request_output in enumerate(outputs):
                    selected = random.sample(range(max(best_of_ns)), best_of_n)
                    organized_outputs[best_of_n]["responses"].append([request_output.outputs[select] for select in selected])
                    organized_outputs[best_of_n]["total_tokens"].append(sum(len(single_output.token_ids) for single_output in request_output.outputs))

            return organized_outputs