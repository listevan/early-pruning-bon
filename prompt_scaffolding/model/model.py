from vllm import LLM, SamplingParams

from model.strategies import HypothesisStrategy, PlanStrategy, ConceptStrategy, ReasoningStructureStrategy, CountdownStrategy

class Model:
    def __init__(self, model_name: str):
        self.llm = LLM(model=model_name)

    def generate_responses(self, prompts, best_of_n, temperature, max_tokens=16384, strategy=None):
        if strategy:
            new_request_prompts = strategy.generate_prompts(prompts, best_of_n, temperature)
            sampling_params = SamplingParams(temperature=temperature, top_p=0.95, max_tokens=max_tokens)

            outputs = []
            for diverse_prompts, og_prompt in zip(new_request_prompts, prompts):
                formatted_variants = [[{"role": "user", "content": prompt + og_prompt}] for prompt in diverse_prompts]
                prompt_outputs = self.llm.chat(formatted_variants, sampling_params=sampling_params)
                
                if prompt_outputs:
                    base_output = prompt_outputs[0]
                    base_output.outputs = []
                    for output in prompt_outputs:
                        for completion in output.outputs:
                            completion.text = strategy._extract_content(completion.text)
                            base_output.outputs.append(completion)
                    outputs.append(base_output)
        else:
            sampling_params = SamplingParams(n=best_of_n, temperature=temperature, top_p=0.95, max_tokens=max_tokens)
            outputs = self.llm.chat(prompts, sampling_params=sampling_params)
        return outputs