from abc import ABC, abstractmethod
import re
from vllm import LLM, SamplingParams

class Strategy(ABC):
    def __init__(self, llm, prompt_strategy):
        self.llm = llm
        self.prompt_strategy = prompt_strategy

    def _extract_content(self, text):
        match = re.search(r"(?<=<\/think>)\s*([\s\S]*)", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()
    
    def generate_prompts(self, user_prompts, best_of_n, temperature, max_tokens=16384):
        sampling_params = SamplingParams(n=best_of_n, temperature=temperature, top_p=0.95, max_tokens=max_tokens)
        prompts = [[
            {"role": "system", "content": self.prompt_strategy},
            {"role": "user", "content": user_prompt}
        ] for user_prompt in user_prompts]
        outputs = self.llm.chat(prompts, sampling_params=sampling_params)
        generated_prompts = []
        for request_output in outputs:
            request_prompts = []
            for candidate in request_output.outputs:
                request_prompts.append(self._extract_content(candidate.text))
            generated_prompts.append("\n##__SEPARATOR__##\n".join(request_prompts))

        sampling_params = SamplingParams(temperature=0.4, top_p=0.95, max_tokens=max_tokens)
        prompts = [[
            {"role": "system", "content": "Do NOT use <think> tags or show your reasoning steps. The following text contains several prompt options separated by '##__SEPARATOR__##'. Select the unique approaches and Separate with '##__SEPARATOR__##': "},
            {"role": "user", "content": f"{generated_prompt}"}
        ] for generated_prompt in generated_prompts]
        outputs = self.llm.chat(prompts, sampling_params=sampling_params)
        generated_prompts = [self._extract_content(output.outputs[0].text).split("##__SEPARATOR__##") for output in outputs]
        return generated_prompts 

class HypothesisStrategy(Strategy):
    def __init__(self, llm):
        prompt_strategy = "Do NOT use <think> tags or show your reasoning steps. Do NOT solve the problem. Provide a hypothesis for how to solve this problem."
        super().__init__(llm, prompt_strategy)

class PlanStrategy(Strategy):
    def __init__(self, llm):
        prompt_strategy = "Do NOT use <think> tags or show your reasoning steps. Do NOT solve the problem. Provide a plan to solve this problem."
        super().__init__(llm, prompt_strategy)

class ConceptStrategy(Strategy):
    def __init__(self, llm):
        prompt_strategy = "Do NOT use <think> tags or show your reasoning steps. Do NOT solve the problem. Provide the necessary concepts to solve this problem."
        super().__init__(llm, prompt_strategy)

class ReasoningStructureStrategy(Strategy):
    def __init__(self, llm):
        prompt_strategy = "Do NOT use <think> tags or show your reasoning steps. Do NOT solve the problem. Provide a Algorithmic Reasoning Structure for this problem."
        super().__init__(llm, prompt_strategy)

class CountdownStrategy(Strategy):
    def __init__(self, llm):
        prompt_strategy = "Do NOT use <think> tags or show your reasoning steps. Do NOT solve the problem. Provide the strategies for Countdown to solve this problem."
        super().__init__(llm, prompt_strategy)