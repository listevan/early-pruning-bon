from model.utils import extract_content
from model.rank import ranker

from abc import ABC, abstractmethod
import re
import sys
import random
from vllm import LLM, SamplingParams
from vllm.sampling_params import StructuredOutputsParams
import json

answer_instruction = """
    \n\nEach number must be used at most once.\n
    1. Provide your solution as a arithmetic expression (no '=' sign).\n
    2. Do not include the target number in the expression.\n
    3. Use '*' for multiplication.\n
    4. Use '/' for division.\n
    Do not include any other text or formatting for the final answer.
"""

class Strategy(ABC):
    def __init__(self, llm, prompt_strategy, name="Strategy", seed=42):
        self.name = name
        self.seed = seed

        self.llm = llm
        self.prompt_strategy = prompt_strategy

        self.ranker = ranker("Partial Solutions", self.llm, self.seed)
    
    def generate_prompts(self, user_prompts, best_of_n, temperature, max_selection_tokens=100, max_plan_tokens=1000, prune_ratio=1, previous_responses=None, ranked_indexes=None, reasonings=None):
        # TODO 3/27/26: Get 8 full solutions(full solutions) --> and then truncate each of the full solutions so no need to rerun "generate_prompts"
            # TODO: to do the above, tokenize full solutions --> then truncate to first 500 tokens
        total_tokens = []

        # print(f"best_of_n: {best_of_n}")
        # generate random number for random question to print
        random_question = random.randrange(len(user_prompts))
        # print(f"results for a random question {random_question}")
        
        # format prompts for qwen, define system prompt with strategy text
        # add tags (plan, sol, answer) and stop at plan tag
        prompts = [
            [
                {"role": "system", "content": r"use <plan></plan>, <solution></solution>, <answer></answer> tags to structure your answer."}, 
                {"role": "user", "content": "Do not say anything about formatting" +self.prompt_strategy} # + user_prompt.split("\n\n")[0]}
            ] for user_prompt in user_prompts
        ]
 
        # set up sampling parameters with user given hyperparameters
        custom_tag_regex = r"<plan>[\s\S]*?</plan>" # <solution>[\s\S]*?</solution><answer>[\s\S]*?</answer>"
        structured_params = StructuredOutputsParams(regex=custom_tag_regex)
        sampling_params = SamplingParams(n=best_of_n, temperature=temperature, top_p=0.95, stop=["</plan>"], include_stop_str_in_output=True, max_tokens=max_plan_tokens, structured_outputs=structured_params, seed=self.seed)
        # generate strategy results without thinking
        print("Generating Initial Prompts", file=sys.stderr)
        outputs = self.llm.chat(prompts, sampling_params=sampling_params, chat_template_kwargs={"enable_thinking": False})
        total_tokens = [sum([len(plan.token_ids) for plan in request_output.outputs]) for request_output in outputs]

        # loop through the different questions and combine the generated ideas with separator tokens
        generated_prompts = []
        for request_output in outputs:
            # loop through the generated ideas
            request_prompts = []
            for candidate in request_output.outputs:
                # if the plan phase is not finished skip it
                text = extract_content(candidate.text)
                if "<plan>" not in text or "</plan>" not in text:
                    continue
                text = text.split("<plan>")[1].split("</plan>")[0]
                listing_pattern = r"\d+[ .)]"
                text = re.sub(listing_pattern, "-", text)
                text = text.replace("\n", " ")
                request_prompts.append(text)
            # and separate with a new line
            generated_prompts.append(request_prompts) 
        # print(f"original plans are: {generated_prompts[random_question]}")
        
        ranked_indexes, reasonings, diversity_tokens = self.ranker.rank(user_prompts, generated_prompts, max_selection_tokens)

        total_tokens = [a + b for a, b in zip(total_tokens, diversity_tokens)]

        number_choices = int(max(1, best_of_n // prune_ratio))
        final_processed_indexes = []
        for i in range(len(user_prompts)):
            # Take top 'number_choices'
            selected_slice = ranked_indexes[i][:number_choices]
            # Your original code sorts them here:
            final_processed_indexes.append(selected_slice)

        generated_diverse_prompts = [[generated_prompts[i][diverse_index] for diverse_index in diverse_indexes if diverse_index < len(generated_prompts[i])] for i, diverse_indexes in enumerate(final_processed_indexes)]
        
        return {"generated_prompts": generated_prompts, "indexes": ranked_indexes, "reasonings": reasonings, "generated_diverse_prompts": generated_diverse_prompts, "total_tokens": total_tokens}

class HypothesisStrategy(Strategy):
    def __init__(self, llm, seed=42):
        prompt_strategy = "Do NOT solve the problem. Provide a hypothesis for how to solve this problem."
        super().__init__(llm, prompt_strategy, "HypothesisStrategy", seed)

class PlanStrategy(Strategy):
    def __init__(self, llm, seed=42):
        prompt_strategy = "Do NOT solve the problem. Provide a plan to solve this problem." # TODO: more detail, maybe try to directly ask for 8 unique plans instead of sampling with n
        super().__init__(llm, prompt_strategy, "PlanStrategy", seed)

class ConceptStrategy(Strategy):
    def __init__(self, llm, seed=42):
        prompt_strategy = "Do NOT solve the problem. Provide the necessary concepts to solve this problem."
        super().__init__(llm, prompt_strategy, "ConceptStrategy", seed)

class ReasoningStructureStrategy(Strategy):
    def __init__(self, llm, seed=42):
        prompt_strategy = "Do NOT solve the problem. Provide a Algorithmic Reasoning Structure for this problem."
        super().__init__(llm, prompt_strategy, "ReasoningStructureStrategy", seed)

class CountdownStrategy(Strategy):
    def __init__(self, llm, seed=42):
        prompt_strategy = "Provide the strategies to solve a Countdown problem (use basic arithmetic to combine six selected numbers in order to calculate a randomly generated target)."
        super().__init__(llm, prompt_strategy, "CountdownStrategy", seed)

class UserStrategy(Strategy):
    def __init__(self, llm, seed=42):
        super().__init__(llm, "", "UserStrategy", seed)
    
    def generate_prompts(self, user_prompts, best_of_n, temperature, max_selection_tokens=16000, max_plan_tokens=500, prune_ratio=1, previous_responses=None, ranked_indexes=None, reasonings=None):        # need to fill in with user created prompts
        tokenizer = self.llm.get_tokenizer()
        new_prompts = [
            [
                "Identify the mathematical factors of the target value to guide your operations. Multiply two smaller tile combinations together to reach one of these specific factor multiples.",
                "Calculate a product that lands slightly above or below the ultimate target. Add or subtract the exact remaining difference using your leftover tiles.",
                "Start directly from the target goal and apply reverse arithmetic operations. Continue this backward deduction until you successfully match the available starting tiles.",
                "Program a computer script to systematically generate every possible equation tree. Evaluate each generated recursive path until the correct target value successfully appears.",
                "Subtract a tile from an identical tile to create a zero, or divide identical tiles to create a one. Apply these neutral values to discard unwanted tiles without altering your current total.",
                "Multiply your largest available tiles together first to establish a heavy baseline. Adjust this baseline incrementally downward using your remaining smaller tiles.",
                "Group all starting tiles into distinct pairs and calculate their initial sums or products. Combine these newly formed subtotal groups together to build toward the final goal.",
                "Locate a single tile that perfectly matches the gap between a reachable milestone and your target. Set this specific tile aside safely until the very final addition or subtraction step."
            ]
        ] * len(user_prompts)

        return {"generated_prompts": new_prompts, "indexes": [range(len(new_prompts[0]))]*len(user_prompts), "reasonings": [], "generated_diverse_prompts": new_prompts, "total_tokens": [0] * len(user_prompts)}

class CompletionStrategy(Strategy):
    def __init__(self, llm, seed=42):
        super().__init__(llm, "", "CompletionStrategy", seed)
    
    def generate_prompts(self, user_prompts, best_of_n, temperature, max_selection_tokens=16000, max_plan_tokens=500, prune_ratio=1, previous_responses=None, ranked_indexes=None, reasonings=None):
        # TODO: test with different mumber of max_plan_tokens (first few 100 is even better)
        # TODO: 3/27/26: Vary max_plan_tokens and make sure essence of solution is within these 500 tokens(so make sure that 500 is enough) --> treat as hyperparameter and just test around(no good way to test it)
        # TODO: 3/27/26: Thinking models tend to do bad with <think></think> because training doesn't condition on it
        new_prompts = []
        total_tokens = []
        indexes = []

        if previous_responses is None:
            sampling_params = SamplingParams(n=best_of_n, temperature=temperature, top_p=0.95, max_tokens=max_plan_tokens, seed=self.seed)
            print("Generating Completion Initial Response", file=sys.stderr)
            outputs = self.llm.chat([[
                {"role": "user", "content": (
                    f"{prompt}\n\n"
                    "First, write out your step-by-step thoughts on how to solve this in plain text without using any tags. "
                    "Then, provide your final answer strictly inside <answer></answer> tags."
                )}
            ] for prompt in user_prompts], sampling_params=sampling_params)

            # import pdb; pdb.set_trace()

            for i, request_output in enumerate(outputs):
                new_prompts.append([single_output.text for single_output in request_output.outputs])
                total_tokens.append(sum(len(single_output.token_ids) for single_output in request_output.outputs))
                # with open("newprompts_temp.txt", "+a") as f:
                    # f.write(f"{new_prompts}\n")
        else:
            tokenizer = self.llm.get_tokenizer()
            for i, request_output in enumerate(previous_responses):
                new_prompts.append([tokenizer.decode(response["token_ids"][:max_plan_tokens]) for response in request_output])
                total_tokens.append(sum([min(max_plan_tokens, len(response["token_ids"])) for response in request_output]))
        
        if ranked_indexes is None:
            ranked_indexes, reasonings, diversity_tokens = self.ranker.rank(user_prompts, new_prompts, max_selection_tokens)

            total_tokens = [a + b for a, b in zip(total_tokens, diversity_tokens)]
            print(f"selection takes {sum(diversity_tokens) / len(diversity_tokens)} tokens", file=sys.stderr)

        number_choices = int(max(1, best_of_n // prune_ratio))
        final_processed_indexes = []
        for i in range(len(user_prompts)):
            # Take top 'number_choices'
            selected_slice = ranked_indexes[i][:number_choices]
            # Your original code sorts them here:
            final_processed_indexes.append(selected_slice)

        generated_diverse_prompts = [[new_prompts[i][diverse_index] for diverse_index in diverse_indexes if diverse_index < len(new_prompts[i])] for i, diverse_indexes in enumerate(final_processed_indexes)]       
        
        return {"generated_prompts": new_prompts, "ranked_indexes": ranked_indexes, "indexes": final_processed_indexes, "reasonings": reasonings, "generated_diverse_prompts": generated_diverse_prompts, "total_tokens": total_tokens}
        
