import copy
from vllm import LLM, SamplingParams

from model.strategies import HypothesisStrategy, PlanStrategy, ConceptStrategy, ReasoningStructureStrategy, CountdownStrategy

class Model:
    def __init__(self, model_name: str):
        self.llm = LLM(model=model_name)

    def generate_responses(self, prompts, best_of_n, temperature, max_tokens=16384, strategy=None):
        if strategy:
            new_request_prompts = strategy.generate_prompts(prompts, best_of_n, temperature)
            sampling_params = SamplingParams(temperature=temperature, top_p=0.95, max_tokens=max_tokens)
            
            import pdb; pdb.set_trace()

            outputs = []
            all_prompt_outputs = []
            for diverse_prompts, og_prompt in zip(new_request_prompts, prompts):
                new_best_of_n = len(diverse_prompts)
                formatted_variants = [[{"role": "user", "content": prompt + og_prompt[0]['content']}] for prompt in diverse_prompts]
                prompt_outputs = self.llm.chat(formatted_variants, sampling_params=sampling_params)
                all_prompt_outputs.append(prompt_outputs)
            
            if all_prompt_outputs:
                for output in all_prompt_outputs:
                    if len(output[0].outputs) > 1:
                        print(f">>>> OUTPUT.OUTPUTS IS {len(output[0].outputs)} WHAT")
                    base_output = output[0].outputs[0]
                    outputs.append(copy.deepcopy(base_output))
            return outputs
        else:
            sampling_params = SamplingParams(n=best_of_n, temperature=temperature, top_p=0.95, max_tokens=max_tokens)
            outputs = self.llm.chat(prompts, sampling_params=sampling_params)
            return outputs