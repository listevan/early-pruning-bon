from model.strategies import HypothesisStrategy, PlanStrategy, ConceptStrategy, ReasoningStructureStrategy, CountdownStrategy, UserStrategy

from vllm import LLM, SamplingParams
from vllm.sampling_params import StructuredOutputsParams
import random
import sys
import re

def extract_answer(text):
    # Pattern looks for everything between <answer> and </answer>
    # re.DOTALL allows the dot (.) to match newlines if the answer is multi-line
    match = re.findall(r'<answer>(.*?)</answer>', text, re.DOTALL)
    
    if match:
        return match[-1].strip()
    
    # If no tags exist, return the original string
    return text

answer_instruction = """
    \n\nEach number must be used at most once.\n
    1. Provide your solution as a arithmetic expression (no '=' sign).\n
    2. Do not include the target number in the expression.\n
    3. Use '*' for multiplication.\n
    4. Use '/' for division.\n
    Do not include any other text or formatting for the final answer.
"""

class Model:
    def __init__(self, model_name: str, seed=42):
        self.llm = LLM(model=model_name, tensor_parallel_size=1, max_model_len=60000)# max_model_len=65536)
        self.seed = seed

    def select_solution(self, best_of_n, prompts, responses_list, max_tokens=16384):
        sampling_params = SamplingParams(temperature=0.7, top_p=0.8, top_k=20, max_tokens=max_tokens, seed=self.seed)

        all_eval_messages = []
        all_candidates_text = [[
                extract_answer(resp.text if hasattr(resp, 'text') else resp.get("text", "")) 
                for resp in prompt_responses
            ] for prompt_responses in responses_list]

        # 1. Format batched prompts efficiently without heavy nested comprehensions
        for i, prompt in enumerate(prompts):
            
            # Extract the text for each candidate belonging to this prompt
            candidates_text = all_candidates_text[i]
            
            # Shuffle indices to prevent position bias
            indices = list(range(candidates_text))
            random.shuffle(indices)
            
            # Build the examples string using the shuffled mappings
            examples_str = "".join([
                f"<example id='{idx}'>\n{candidates_text[idx]}\n</example>\n" 
                for idx in indices
            ])
            
            # Construct the message for this specific prompt
            eval_content = f"""You are an expert evaluator. Do NOT solve the problem from scratch. Your task is to select the single most likely correct final solution from the provided options.

                ### The Problem:
                {prompt}

                ### The Proposed Solutions:
                {examples_str}

                ### Instructions:
                1. Analyze the underlying logic, methodology, and final answer of each proposed solution.
                2. Assess which approach and conclusion is the most accurate. 
                3. You MUST pick exactly ONE solution. Even if you believe all the provided options are flawed, incomplete, or entirely incorrect, you are strictly required to select the single "least wrong" or most reasonable solution among them.

                Provide your brief evaluation, then output ONLY the single chosen index inside <results> tags."""

            all_eval_messages.append([{"role": "user", "content": eval_content}])

        # 2. Execute a single, batched VLLM chat generation for all prompts at once
        outputs = self.llm.chat(all_eval_messages, sampling_params=sampling_params)

        # 3. Extract the chosen index and un-shuffle it to get the original candidate index
        final_selections = []
        total_tokens = []
        for i, request_output in enumerate(outputs):
            res_match = re.search(r'<results>\s*(.*?)\s*</results>', request_output.outputs[0].text)
            total_tokens.append(len(request_output.outputs[0].token_ids))
            
            chosen_idx = random.randrange(best_of_n)
            try:
                parsed_idx = int(res_match.group(1).strip())
                if 0<= parsed_idx < best_of_n:
                    chosen_idx = parsed_idx
            except (AttributeError, ValueError):
                pass
                
            final_selections.append(all_candidates_text[i][chosen_idx])
        
        return final_selections, total_tokens

    def generate_responses(self, prompts, best_of_ns, temperature, max_tokens=16384, max_plan_tokens=500, prune_ratio=1, strategy=None, previous_responses=None):
        # see if user decided to use a strategy
        if strategy:
            organized_outputs = {}
            ranked_indexes = None
            reasonings = None

            # loop through the best_of_ns to run diversification and generation for each n
            for i, best_of_n in enumerate(sorted(best_of_ns, reverse=True)):
                filtered_ranked_indexes = None
                if ranked_indexes is not None:
                    filtered_ranked_indexes = [[idx for idx in prompt_ranks if idx < best_of_n] for prompt_ranks in ranked_indexes]

                # if so, use the strategy to generate a set of diverse prompts (from the original best_of_n), ignore formatting part of the prompt
                if previous_responses is None:
                    bon_previous_responses = None
                else:
                    bon_previous_responses = previous_responses[str(best_of_n)]
                organized_outputs[best_of_n] = strategy.generate_prompts(prompts, best_of_n, temperature, max_plan_tokens=max_plan_tokens, prune_ratio=prune_ratio, previous_responses=bon_previous_responses, ranked_indexes=filtered_ranked_indexes, reasonings=reasonings)
                if ranked_indexes is None:
                    ranked_indexes = organized_outputs[best_of_n]["indexes"]
                    reasonings = organized_outputs[best_of_n]["reasonings"]
                
                new_request_prompts = organized_outputs[best_of_n]["generated_diverse_prompts"]

                organized_outputs[best_of_n]["responses"] = []
                
                # define sampling parameters with user hyperparameters, TODO 4/10: try top_p=1     
                sampling_params = SamplingParams(temperature=temperature, top_p=0.95, stop=["</answer>"], include_stop_str_in_output=True, max_tokens=max_tokens, seed=self.seed)
                
                # loop through the question prompts and then through diversified prompts to generate the results
                for j, (diverse_request_prompts, og_prompt) in enumerate(zip(new_request_prompts, prompts)):
                    if previous_responses is None or strategy.name != "CompletionStrategy": # if we're regenerating
                        if strategy.name == "CompletionStrategy":
                            print("Completion Continuing Generation", file=sys.stderr)
                            formatted_variants = [f"<|im_start|>system\nAfter thinking, ensure the final formatted answer is within <answer></answer> tags and follows these instructions: {answer_instruction}.<|im_end|>\n<|im_start|>user\n{og_prompt}<|im_end|>\n<|im_start|>assistant\n{diverse_prompt}" for diverse_prompt in diverse_request_prompts]
                            outputs = self.llm.generate(formatted_variants, sampling_params=sampling_params)
                        else:
                            print("Non-Completion Generating Solutions", file=sys.stderr)
                            formatted_variants = [[{"role": "system", "content": f"After thinking, ensure the final formatted answer is within <answer></answer> tags and follows these instructions: {answer_instruction}."}, {"role": "user", "content": og_prompt + "\n" + diverse_prompt + answer_instruction}] for diverse_prompt in diverse_request_prompts]
                            outputs = self.llm.chat(formatted_variants, sampling_params=sampling_params)
                    
                        organized_outputs[best_of_n]["responses"].append([request_output.outputs[0] for request_output in outputs])
                        organized_outputs[best_of_n]["total_tokens"][j] += sum(len(request_output.outputs[0].token_ids) for request_output in outputs)
                    else:
                        # use indexes to choose the responses and get total_tokens
                        organized_outputs[best_of_n]["responses"].append([previous_responses[str(best_of_n)][j][index] for index in organized_outputs[best_of_n]["indexes"][j] if index < len(previous_responses[str(best_of_n)][j])])
                        organized_outputs[best_of_n]["total_tokens"][j] += sum(max(len(response["token_ids"])-max_plan_tokens, 0) for response in organized_outputs[best_of_n]["responses"][-1])
        else: # TODO: don't use system prompt just add to user prompt in none-strat generation, add text to make it think/reason step-by-step
            print("Strategy is none...", file=sys.stderr)
            # if not use user hyperparameters to generate results from prompt
            sampling_params = SamplingParams(n=max(best_of_ns), temperature=temperature, top_p=1, max_tokens=max_tokens, seed=self.seed)
            # Pass system prompt and answer_instructions when no strategy is used
            print("None Generating Solutions", file=sys.stderr)
            outputs = self.llm.chat([[
                {"role": "user", "content": (
                    f"{prompt}\n\n"
                    "First, write out your step-by-step thoughts on how to solve this in plain text without using any tags. "
                    "Then, provide your final answer strictly inside <answer></answer> tags."
                )}
            ] for prompt in prompts], sampling_params=sampling_params)

            # loop through questions to create a dictionary for each of the best_of_n results
            organized_outputs = {}
            
            for best_of_n in best_of_ns:
                organized_outputs[best_of_n] = {"generated_prompts": [], "indexes": [], "generated_diverse_prompts": [], "total_tokens": [], "responses": []}

                for i, request_output in enumerate(outputs):
                    selected = random.sample(range(max(best_of_ns)), best_of_n)
                    organized_outputs[best_of_n]["responses"].append([request_output.outputs[select] for select in selected])
                    organized_outputs[best_of_n]["total_tokens"].append(sum(len(request_output.outputs[select].token_ids) for select in selected))

        
        # Extract and select single answer
        for best_of_n in best_of_ns:
            # responses_list shape: [num_prompts, best_of_n]
            responses_list = organized_outputs[best_of_n]["responses"]
            
            final_selections, selection_tokens = self.select_solution(best_of_n, prompts, responses_list, max_tokens)

            organized_outputs[best_of_n]["Final Answers"] = final_selections
            organized_outputs[best_of_n]["total_tokens"] = [a+b for a,b in zip(selection_tokens, organized_outputs[best_of_n]["total_tokens"])]

        return organized_outputs