from abc import ABC, abstractmethod
import re
import sys
import random
from vllm import LLM, SamplingParams
from vllm.sampling_params import StructuredOutputsParams

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
    
    def generate_prompts(self, user_prompts, best_of_n, temperature, max_tokens=16384, max_plan_tokens=500):
        total_tokens = 0

        print(f"best_of_n: {best_of_n}")
        # generate random number for random question to print
        random_question = random.randrange(len(user_prompts))
        print(f"results for a random question {random_question}")

        # format prompts for qwen, define system prompt with strategy text
        # add tags (plan, sol, answer) and stop at plan tag
        prompts = [
            [
                {"role": "system", "content": r"use <plan></plan>, <solution></solution>, <answer></answer> tags to structure your answer"}, 
                {"role": "user", "content": self.prompt_strategy} # + user_prompt[0]['content']}
            ] for user_prompt in user_prompts
        ]
 
        # set up sampling parameters with user given hyperparameters
        custom_tag_regex = r"<plan>[\s\S]*?</plan>" # <solution>[\s\S]*?</solution><answer>[\s\S]*?</answer>"
        structured_params = StructuredOutputsParams(regex=custom_tag_regex)
        sampling_params = SamplingParams(n=best_of_n, temperature=temperature, top_p=0.95, stop=["</plan>"], include_stop_str_in_output=True, max_tokens=max_plan_tokens, structured_outputs=structured_params)
        # generate strategy results without thinking
        outputs = self.llm.chat(prompts, sampling_params=sampling_params, chat_template_kwargs={"enable_thinking": False})
        total_tokens += sum([len(plan.token_ids) for request_output in outputs for plan in request_output.outputs])

        # loop through the different questions and combine the generated ideas with separator tokens
        generated_prompts = []
        for request_output in outputs:
            # loop through the generated ideas
            request_prompts = []
            for candidate in request_output.outputs:
                # if the plan phase is not finished skip it
                text = self._extract_content(candidate.text)
                if "<plan>" not in text or "</plan>" not in text:
                    continue
                text = text.split("<plan>")[1].split("</plan>")[0]
                request_prompts.append(text)
            # and separate with a new line
            generated_prompts.append(request_prompts) 
        print(f"original plans are: {generated_prompts[random_question]}")

        # create sampling params for model to determine if it's unique
        sampling_params = SamplingParams(temperature=0.7, top_p=0.95, max_tokens=max_tokens)

        # format prompts for qwen with system prompt to tell model of separator and ask for diverse prompts
        prompts = [[
            {"role": "user", "content": f"Do NOT solve the problem. The following text contains several prompt options separated by \\n. Only select the unique approaches and return their number (just number and no punctuation). Separate with \\n': {"\n".join([f"{i}. "+request_generated_prompt.replace("\n", " ") for i, request_generated_prompt in enumerate(generated_prompt)])}"}
        ] for generated_prompt in generated_prompts]

        # get diverse prompts
        outputs = self.llm.chat(prompts, sampling_params=sampling_params, chat_template_kwargs={"enable_thinking": False})
        total_tokens += sum([len(request_output.outputs[0].token_ids) for request_output in outputs])

        # return the prompts but as a list (questions) of lists (unique prompts)
        indexes = [list(map(int, re.findall(r'\d+', self._extract_content(output.outputs[0].text)))) for output in outputs]
        generated_diverse_prompts = [[generated_prompts[i][diverse_index] for diverse_index in diverse_indexes if diverse_index < len(generated_prompts[i])] for i, diverse_indexes in enumerate(indexes)]
        print(f"diverse plans are: {generated_diverse_prompts[random_question]}")
        print(f"------------------------------------------------------------------------------------------------------------")
        return generated_diverse_prompts, total_tokens

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
        prompt_strategy = "Provide the strategies to solve a Countdown problem (use basic arithmetic to combine six selected numbers in order to calculate a randomly generated target)."
        super().__init__(llm, prompt_strategy)