from abc import ABC, abstractmethod
import re
import sys
import random
from vllm import LLM, SamplingParams
from vllm.sampling_params import StructuredOutputsParams
import json

answer_instruction = ""

class Strategy(ABC):
    def __init__(self, llm, prompt_strategy, name="Strategy", seed=42):
        self.name = name
        self.seed = seed

        self.llm = llm
        self.prompt_strategy = prompt_strategy

    def _extract_content(self, text):
        # extract the <think><\think> tags and return result
        match = re.search(r"(?<=<\/think>)\s*([\s\S]*)", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()
    
    def _get_diverse_prompts(self, user_prompts, generated_prompts, max_selection_tokens=16000): # TODO: 3/27/26: let max_selection_tokens be sufficiently enough
        # create sampling params for model to determine if it's unique
        sampling_params = SamplingParams(temperature=0.1, top_p=0.95, max_tokens=max_selection_tokens, seed=self.seed)

        number_choices = 4
        prompts = [[
            {
                "role": "user", 
                "content": f"""
                    You are an expert evaluator. Do NOT solve the problem. Your task is to identify the unique logical approaches from a set of partial solutions.

                    ### The Problem:
                    {user_prompt}

                    ### The Partial Solutions:
                    {"".join([f"<example id='i{i}'>\n{request_generated_prompt.replace('<think>', '')}\n</example>\n" for i, request_generated_prompt in enumerate(generated_prompt)])}

                    ### Instructions:
                    1. Analyze the underlying method or algorithm of each partial solution. Ignore superficial differences (like different variable names or slight phrasing changes).
                    2. Compare each approach to the others to group them by core logic. 
                    3. Prune solutions that might lead to the same outcome.
                    4. Select {number_choices} of the most diverse approaches.

                    ### Output Format:
                    First, provide your step-by-step comparison inside <reasoning> tags.
                    Then, output ONLY the selected indices inside <results> tags, with each index on a new line. 

                    Example Output:
                    <reasoning>
                    i0 uses a dynamic programming approach. i1 uses the exact same approach but renames the array, so it is a duplicate. i2 introduces a unique recursive approach.
                    </reasoning>
                    <results>
                    i0
                    i2
                    </results>
                """
            }
        ] for user_prompt, generated_prompt in zip(user_prompts, generated_prompts)]

        # get diverse prompts
        outputs = self.llm.chat(prompts, sampling_params=sampling_params, chat_template_kwargs={"enable_thinking": False})
        # print("Diverse prompt outputs:", [out.outputs[0].text for out in outputs])
        total_tokens = [len(request_output.outputs[0].token_ids) for request_output in outputs]

        # return the prompts but as a list (questions) of lists (unique prompts)
        indexes = []
        for output in outputs:
            text = self._extract_content(output.outputs[0].text)
            
            # 1. Isolate the results block to avoid picking up reasoning indices
            results_match = re.search(r'<results>(.*?)</results>', text, re.DOTALL)
            results_text = results_match.group(1) if results_match else text # fallback to full text if tags fail
            
            # 2. Extract indices only from the results block
            indexes_2_int = [int(t.replace("i", "")) for t in re.findall(r'i\d+', results_text)] 
            indexes.append(sorted(list(set(indexes_2_int))))

        # print("Picked indicies: ", indexes)
        
        return indexes, total_tokens
    
    def generate_prompts(self, user_prompts, best_of_n, temperature, max_selection_tokens=100, max_plan_tokens=1000, previous_responses=None):
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
        outputs = self.llm.chat(prompts, sampling_params=sampling_params, chat_template_kwargs={"enable_thinking": False})
        total_tokens = [sum([len(plan.token_ids) for plan in request_output.outputs]) for request_output in outputs]

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
                listing_pattern = r"\d+[ .)]"
                text = re.sub(listing_pattern, "-", text)
                text = text.replace("\n", " ")
                request_prompts.append(text)
            # and separate with a new line
            generated_prompts.append(request_prompts) 
        # print(f"original plans are: {generated_prompts[random_question]}")

        indexes, diversity_tokens = self._get_diverse_prompts(user_prompts, generated_prompts, max_selection_tokens)
        total_tokens = [a + b for a, b in zip(total_tokens, diversity_tokens)]

        generated_diverse_prompts = [[generated_prompts[i][diverse_index] for diverse_index in diverse_indexes if diverse_index < len(generated_prompts[i])] for i, diverse_indexes in enumerate(indexes)]
        # print(f"diverse plans are: {generated_diverse_prompts[random_question]}")
        # print(f"------------------------------------------------------------------------------------------------------------")
        
        return {"generated_prompts": generated_prompts, "indexes": indexes, "generated_diverse_prompts": generated_diverse_prompts, "total_tokens": total_tokens}

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
    
    def generate_prompts(self, user_prompts, best_of_n, temperature, max_selection_tokens=100, max_plan_tokens=1000, previous_responses=None):
        # need to fill in with user created prompts
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

        return {"generated_prompts": new_prompts, "indexes": range(len(new_prompts)), "generated_diverse_prompts": new_prompts, "total_tokens": 0}

class CompletionStrategy(Strategy):
    def __init__(self, llm, seed=42):
        super().__init__(llm, "", "CompletionStrategy", seed)
    
    def generate_prompts(self, user_prompts, best_of_n, temperature, max_selection_tokens=16000, max_plan_tokens=500, previous_responses=None):
        # TODO: test with different mumber of max_plan_tokens (first few 100 is even better)
        # TODO: 3/27/26: Vary max_plan_tokens and make sure essence of solution is within these 500 tokens(so make sure that 500 is enough) --> treat as hyperparameter and just test around(no good way to test it)
        # TODO: 3/27/26: Thinking models tend to do bad with <think></think> because training doesn't condition on it
        new_prompts = []
        total_tokens = []
        indexes = []

        if previous_responses is None:
            sampling_params = SamplingParams(n=best_of_n, temperature=temperature, top_p=0.95, max_tokens=max_plan_tokens, seed=self.seed)
            outputs = self.llm.chat([
                [
                    {
                        "role": "system", "content": f"Solve this problem step by step. Ensure the final formatted answer is within <answer></answer> tags and follows these instructions: {answer_instruction}."
                    }, 
                    {
                        "role": "user", "content": prompt
                    }
                ] 
            for prompt in user_prompts], sampling_params=sampling_params) # , chat_template_kwargs={"enable_thinking": True})

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
        
        indexes, diversity_tokens = self._get_diverse_prompts(user_prompts, new_prompts, max_selection_tokens)
        total_tokens = [a + b for a, b in zip(total_tokens, diversity_tokens)]

        generated_diverse_prompts = [[new_prompts[i][diverse_index] for diverse_index in diverse_indexes if diverse_index < len(new_prompts[i])] for i, diverse_indexes in enumerate(indexes)]       
        
        return {"generated_prompts": new_prompts, "indexes": indexes, "generated_diverse_prompts": generated_diverse_prompts, "total_tokens": total_tokens}
        
