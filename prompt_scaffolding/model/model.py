from model.strategies import HypothesisStrategy, PlanStrategy, ConceptStrategy, ReasoningStructureStrategy, CountdownStrategy

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

            # loop through the best_of_ns to run diversification and generation for each n
            for i, best_of_n in enumerate(best_of_ns):
                # if so, use the strategy to generate a set of diverse prompts (from the original best_of_n)
                new_request_prompts = strategy.generate_prompts(prompts, best_of_n, temperature)

                # define sampling parameters with user hyperparameters
                sampling_params = SamplingParams(temperature=temperature, top_p=0.95, max_tokens=max_tokens)
                
                # import pdb; pdb.set_trace()

                # loop through the question prompts and then through diversified prompts to generate the results
                for diverse_request_prompts, og_prompt in zip(new_request_prompts, prompts):
                    print(f"diverse promtps are: {diverse_request_prompts}", file=sys.stderr)

                    # format the diversified prompt by prepending the original prompt and putting into qwen format
                    formatted_variants = [[{"role": "user", "content": diverse_prompt + og_prompt[0]['content']}] for diverse_prompt in diverse_request_prompts]

                    # generate results from the formatted variants
                    outputs = self.llm.chat(formatted_variants, sampling_params=sampling_params)
                    
                    # store the results, if its the first iteration append to organized_outputs
                    if i == 0:
                        organized_outputs = [{best_of_n: request_output.outputs} for request_output in outputs]
                    # otherwise just add the best_of n results
                    else:
                        for j, request_output in enumerate(outputs):
                            organized_outputs[j][best_of_n] = request_output.outputs

            return organized_outputs
        else:
            # if not use user hyperparameters to generate results from prompt
            sampling_params = SamplingParams(n=max(best_of_ns), temperature=temperature, top_p=0.95, max_tokens=max_tokens)
            outputs = self.llm.chat(prompts, sampling_params=sampling_params)

            # loop through questions to create a dictionary for each of the best_of_n results
            organized_outputs = []
            for i, request_output in enumurate(outputs):
                organized_outputs.append({best_of_n: random.sample(request_output.outputs, best_of_n) for best_of_n in best_of_ns})

            return organized_outputs