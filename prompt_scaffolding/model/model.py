from model.strategies import HypothesisStrategy, PlanStrategy, ConceptStrategy, ReasoningStructureStrategy, CountdownStrategy, UserStrategy

from vllm import LLM, SamplingParams
import random
import sys

class Model:
    def __init__(self, model_name: str):
        self.llm = LLM(model=model_name, tensor_parallel_size=1)

    def generate_responses(self, prompts, best_of_ns, temperature, max_tokens=16384, strategy=None):
        # see if user decided to use a strategy
        if strategy:
            organized_outputs = []
            organized_total_tokens = {}

            # loop through the best_of_ns to run diversification and generation for each n
            for i, best_of_n in enumerate(best_of_ns):
                # if so, use the strategy to generate a set of diverse prompts (from the original best_of_n), ignore formatting part of the prompt
                if type(strategy) is UserStrategy:
                    new_request_prompts, total_tokens = strategy.generate_manual_prompts([[{"role": "user", "content": prompt.split("\n")[0]}] for prompt in prompts], best_of_n, temperature)
                else:
                    new_request_prompts, total_tokens = strategy.generate_prompts([[{"role": "user", "content": prompt.split("\n")[0]}] for prompt in prompts], best_of_n, temperature)
                
                # save the intermediate total_tokens used for this best_of_n
                organized_total_tokens[best_of_n] = total_tokens

                # define sampling parameters with user hyperparameters
                sampling_params = SamplingParams(temperature=temperature, top_p=0.95, max_tokens=max_tokens)
                

                # loop through the question prompts and then through diversified prompts to generate the results
                for j, (diverse_request_prompts, og_prompt) in enumerate(zip(new_request_prompts, prompts)):
                    # format the diversified prompt by prepending the original prompt and putting into qwen format
                    formatted_variants = [[{"role": "user", "content": og_prompt + "\n" + diverse_prompt + ". Do not use special symbols or LaTeX symbols in your answer. Only use the symbols: *, /, -, +."}] for diverse_prompt in diverse_request_prompts]
                    # print("====\nFormatted variants: \n", formatted_variants, "====\n\n")

                    # generate results from the formatted variants
                    outputs = self.llm.chat(formatted_variants, sampling_params=sampling_params)
                    
                    # store the results, if its the first iteration append to organized_outputs
                    if i == 0:
                        organized_outputs.append({best_of_n: [request_output.outputs[0] for request_output in outputs]})
                    # otherwise just add the best_of n results
                    else:
                        organized_outputs[j][best_of_n] = [request_output.outputs[0] for request_output in outputs]

            return organized_outputs, organized_total_tokens
        else:
            # if not use user hyperparameters to generate results from prompt
            sampling_params = SamplingParams(n=max(best_of_ns), temperature=temperature, top_p=0.95, max_tokens=max_tokens)
            outputs = self.llm.chat(prompts, sampling_params=sampling_params)

            # loop through questions to create a dictionary for each of the best_of_n results
            organized_outputs = []
            for i, request_output in enumerate(outputs):
                organized_outputs.append({best_of_n: random.sample(request_output.outputs, best_of_n) for best_of_n in best_of_ns})

            return organized_outputs, None