from abc import ABC, abstractmethod
import re
import sys
import random
from vllm import LLM, SamplingParams

class Strategy(ABC):
    def __init__(self, llm, prompt_strategy):
        self.llm = llm
        self.prompt_strategy = prompt_strategy

    def _extract_content(self, text):
        # extract the <think><\think> tags and return result
        match = re.search(r"(?<=<\/think>)\s*([\s\S]*)", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()
    
    def generate_prompts(self, user_prompts, best_of_n, temperature, max_tokens=16384):
        total_tokens = 0

        print(f"best_of_n: {best_of_n}")
        # generate random number for random question to print
        random_question = random.randrange(len(user_prompts))
        print(f"results for a random question {random_question}")

        # set up sampling parameters with user given hyperparameters
        sampling_params = SamplingParams(n=best_of_n, temperature=temperature, top_p=0.95, max_tokens=max_tokens)

        # format prompts for qwen, define system prompt with strategy text
        # TODO: remove the wrapper asking for solution formatting (keep only necessary parts), change to .generate() and use chat template (enable_thinking is part of this) from huggingface
        prompts = [
            [
                {"role": "user", "content": self.prompt_strategy + user_prompt[0]['content']}
            ] for user_prompt in user_prompts
        ]

        # generate strategy results without thinking
        outputs = self.llm.chat(prompts, sampling_params=sampling_params, chat_template_kwargs={"enable_thinking": False})
        total_tokens += sum([len(plan.token_ids) for request_output in outputs for plan in request_output.outputs])
        print(f"original plans are: {outputs[random_question].outputs}")

        # loop through the different questions and combine the generated ideas with separator tokens
        generated_prompts = []
        for request_output in outputs:
            # loop through the generated ideas
            request_prompts = []
            for candidate in request_output.outputs:
                request_prompts.append(self._extract_content(candidate.text))
            # and separate with a separator token
            generated_prompts.append("##__SEPARATOR__##".join(request_prompts)) # should we have newline here?

        # create sampling params for model to determine if it's unique
        sampling_params = SamplingParams(temperature=0.7, top_p=0.95, max_tokens=max_tokens)

        # format prompts for qwen with system prompt to tell model of separator and ask for diverse prompts
        prompts = [[
            {"role": "user", "content": f"Do NOT solve the problem. The following text contains several prompt options separated by '##__SEPARATOR__##'. Only select the unique approaches and Separate with '##__SEPARATOR__##': {generated_prompt}"}
        ] for generated_prompt in generated_prompts]

        # get diverse prompts
        outputs = self.llm.chat(prompts, sampling_params=sampling_params, chat_template_kwargs={"enable_thinking": False})
        total_tokens += sum([len(request_output.outputs[0].token_ids) for request_output in outputs])

        # return the prompts but as a list (questions) of lists (unique prompts)
        generated_prompts = [self._extract_content(output.outputs[0].text).split("##__SEPARATOR__##") for output in outputs]
        print(f"diverse plans are: {outputs[random_question].outputs}")
        print(f"------------------------------------------------------------------------------------------------------------")
        return generated_prompts, total_tokens

class HypothesisStrategy(Strategy):
    def __init__(self, llm):
        prompt_strategy = "Do NOT solve the problem. Provide a hypothesis for how to solve this problem."
        super().__init__(llm, prompt_strategy)

class PlanStrategy(Strategy):
    def __init__(self, llm):
        prompt_strategy = "Do NOT solve the problem. Provide a plan to solve this problem."
        super().__init__(llm, prompt_strategy)

class ConceptStrategy(Strategy):
    def __init__(self, llm):
        prompt_strategy = "Do NOT solve the problem. Provide the necessary concepts to solve this problem."
        super().__init__(llm, prompt_strategy)

class ReasoningStructureStrategy(Strategy):
    def __init__(self, llm):
        prompt_strategy = "Do NOT solve the problem. Provide a Algorithmic Reasoning Structure for this problem."
        super().__init__(llm, prompt_strategy)

class CountdownStrategy(Strategy):
    def __init__(self, llm):
        prompt_strategy = "Do NOT solve the problem. Provide the strategies for Countdown to solve this problem."
        super().__init__(llm, prompt_strategy)