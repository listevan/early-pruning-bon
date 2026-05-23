from model.strategies import HypothesisStrategy, PlanStrategy, ConceptStrategy, ReasoningStructureStrategy, CountdownStrategy, UserStrategy
from model.utils import extract_answer

from vllm import LLM, SamplingParams
from vllm.sampling_params import StructuredOutputsParams
import random
import sys
import re

answer_instruction = """
    \n\nEach number must be used at most once.\n
    1. Provide your solution as a arithmetic expression (no '=' sign).\n
    2. Do not include the target number in the expression.\n
    3. Use '*' for multiplication.\n
    4. Use '/' for division.\n
    Do not include any other text or formatting for the final answer.
"""

class Model:
    def __init__(self, model_name: str, seed=42, group_size=4):
        self.llm = LLM(model=model_name, tensor_parallel_size=1, max_model_len=32768)# max_model_len=65536)
        self.seed = seed

        self.ranker = ranker("Solutions", self.llm, self.seed)
        self.group_size=group_size

    def tourney_select_solution(self, best_of_n, group_size, prompts, responses_list, max_tokens=16384, max_retries=3):
        # 1. Validate constraints and ensure group size is legal
        group_size = max(2, group_size)
        N = len(prompts)
        
        # Pre-extract all candidate texts to match select_solution and avoid re-extracting
        all_candidates_text = [[
            extract_answer(resp.text if hasattr(resp, 'text') else resp.get("text", "")) 
            for resp in prompt_responses
        ] for prompt_responses in responses_list]

        # Arrays to hold current state and final tracking data
        active_indices = [list(range(len(all_candidates_text[i]))) for i in range(N)]
        total_tokens = [0] * N
        bracket_history = [[] for _ in range(N)]
        round_num = 1

        # 2. Tournament loop: Repeat until the remaining group < group_size
        while any(len(idx_list) >= group_size for idx_list in active_indices):
            batch_prompts = []
            batch_rankees = []
            chunk_metadata = []  # Maps flat batches back to (prompt_idx, original_indices_chunk)
            
            next_active_indices = [[] for _ in range(N)]
            
            # Chunking logic
            for i in range(N):
                current_active = active_indices[i]
                
                # If a prompt's group is already strictly less than group_size, it advances without ranking
                if len(current_active) < group_size:
                    next_active_indices[i].extend(current_active)
                    continue
                    
                # Separate into smaller groups of group_size
                for j in range(0, len(current_active), group_size):
                    chunk = current_active[j:j+group_size]
                    
                    if len(chunk) > 1:
                        batch_prompts.append(prompts[i])
                        batch_rankees.append([all_candidates_text[i][idx] for idx in chunk])
                        chunk_metadata.append((i, chunk))
                    else:
                        # Leftover chunk of 1 automatically advances
                        next_active_indices[i].extend(chunk)
                        
            if not batch_prompts:
                break  # Safety break if no groups were formed
                
            # Execute batch ranking
            print(f"Tournament Round {round_num} - Ranking {len(batch_prompts)} groups...", file=sys.stderr)
            chunk_final_indexes, chunk_reasonings, chunk_tokens = self.ranker.rank(
                user_prompts=batch_prompts, 
                rankees=batch_rankees, 
                max_retries=max_retries
            )
            
            # 3. Process rankings and prune off half
            for k, (i, chunk) in enumerate(chunk_metadata):
                total_tokens[i] += chunk_tokens[k]
                
                ranked_local_indices = chunk_final_indexes[k]
                reasoning = chunk_reasonings[k]
                
                # Determine top half (ceiling division to favor keeping more on odd sizes)
                num_to_keep = (len(chunk) + 1) // 2
                
                # Ensure parsed indices are within the valid bounds of this chunk
                valid_local_indices = [idx for idx in ranked_local_indices if idx < len(chunk)]
                
                # Deterministic fallback if ranker output is incomplete
                if len(valid_local_indices) < num_to_keep:
                    missing = [idx for idx in range(len(chunk)) if idx not in valid_local_indices]
                    valid_local_indices.extend(missing)
                    
                kept_local = valid_local_indices[:num_to_keep]
                
                # Map local chunk indices back to global candidates index
                kept_global = [chunk[idx] for idx in kept_local]
                ranked_global = [chunk[idx] for idx in valid_local_indices]
                
                next_active_indices[i].extend(kept_global)
                
                # Record organized tracking of selection
                bracket_history[i].append({
                    "round": round_num,
                    "group_candidates": chunk,
                    "ranked_order": ranked_global,
                    "kept_candidates": kept_global,
                    "reasoning": reasoning
                })
                
            active_indices = next_active_indices
            round_num += 1

        # 4. Final selection for the remaining candidates using select_solution
        print(f"Tournament Complete. Running final select_solution for remaining candidates...", file=sys.stderr)
        
        subset_responses_list = []
        for i in range(N):
            subset = [responses_list[i][idx] for idx in active_indices[i]]
            subset_responses_list.append(subset)
            
        final_selections, final_sel_tokens = self.select_solution(
            best_of_n=group_size,  
            prompts=prompts,
            responses_list=subset_responses_list,
            max_tokens=max_tokens,
            max_retries=max_retries
        )
        
        # 5. Resolve final indexes and consolidate returns
        final_indexes = [None] * N
        
        for i in range(N):
            total_tokens[i] += final_sel_tokens[i]
            chosen_text = final_selections[i]
            
            # Map the text selected by select_solution back to the original index
            subset_texts = [all_candidates_text[i][idx] for idx in active_indices[i]]
            try:
                local_idx = subset_texts.index(chosen_text)
                final_indexes[i] = active_indices[i][local_idx]
            except ValueError:
                # Deterministic fallback just in case text mapping fails
                print(f"Index {i} failed final text resolution. Defaulting to first active.", file=sys.stderr)
                final_indexes[i] = active_indices[i][0]
                
            # Log final bracket action
            bracket_history[i].append({
                "round": "Final Selection",
                "group_candidates": active_indices[i],
                "ranked_order": active_indices[i], 
                "kept_candidates": [final_indexes[i]],
                "reasoning": "Determined via select_solution module (text match back to index)."
            })

        return final_indexes, bracket_history, total_tokens

    def select_solution(self, best_of_n, prompts, responses_list, max_tokens=16384, max_retries=3):
        sampling_params = SamplingParams(temperature=0.7, top_p=0.8, top_k=20, max_tokens=max_tokens, seed=self.seed)

        all_candidates_text = [[
            extract_answer(resp.text if hasattr(resp, 'text') else resp.get("text", "")) 
            for resp in prompt_responses
        ] for prompt_responses in responses_list]

        # 1. Pre-build all the prompts
        all_eval_messages = []
        for i, prompt in enumerate(prompts):
            candidates_text = all_candidates_text[i]
            
            # Shuffle indices to prevent position bias
            shuffled_indices = list(range(len(candidates_text)))
            random.shuffle(shuffled_indices)
            
            # Build the examples string using the 'iX' format for clearer parsing
            examples_str = "".join([
                f"<example id='i{idx}'>\n{candidates_text[idx]}\n</example>\n" 
                for idx in shuffled_indices
            ])
            
            num_candidates = len(candidates_text)
            valid_indices = ", ".join([f"i{j}" for j in range(num_candidates)])
            
            eval_content = f"""You are an expert evaluator. Your task is to select the single best solution from the provided options.

            ### The Problem:
            {prompt}

            ### The Proposed Solutions:
            {examples_str}

            ### Instructions:
            1. Analyze the logic, methodology, and final answer of each proposed solution.
            2. Assess which approach is the most accurate. 
            3. You MUST pick exactly ONE solution using its exact ID.
            4. You must use one of these specific indices: {valid_indices}.

            Output your response EXACTLY in this format:
            <evaluation>
            [Your brief evaluation here]
            </evaluation>
            <results>
            iX
            </results>"""

            all_eval_messages.append([{"role": "user", "content": eval_content}])

        N = len(prompts)
        
        # Arrays to hold the final resolved data in the original order
        final_selections = [None] * N
        final_reasons = [""] * N  # <-- Added array to hold reasonings
        total_tokens = [0] * N
        
        # Queue of indices that still need to be processed successfully
        pending_indices = list(range(N))
        attempts = 0

        # 2. Execute batched VLLM chat generation with retries
        while pending_indices and attempts < max_retries:
            print(f"Selecting Solutions - Attempt {attempts + 1}/{max_retries}. Pending: {len(pending_indices)}", file=sys.stderr)
            
            current_messages = [all_eval_messages[i] for i in pending_indices]
            
            outputs = self.llm.chat(current_messages, sampling_params=sampling_params)
            
            new_pending_indices = []

            for j, request_output in enumerate(outputs):
                original_i = pending_indices[j]
                text = request_output.outputs[0].text
                
                # Accumulate tokens across retries
                total_tokens[original_i] += len(request_output.outputs[0].token_ids)
                
                # Try to isolate the results block
                res_match = re.search(r'<results>\s*(.*?)\s*</results>', text, re.DOTALL)
                results_text = res_match.group(1).strip() if res_match else text
                
                # Extract the index, looking for 'iX' or just 'X'
                idx_match = re.search(r'(?:i)?(\d+)', results_text)
                
                success = False
                if idx_match:
                    try:
                        parsed_idx = int(idx_match.group(1))
                        # Validate the parsed index is within bounds
                        if 0 <= parsed_idx < len(all_candidates_text[original_i]):
                            final_selections[original_i] = all_candidates_text[original_i][parsed_idx]
                            
                            eval_match = re.search(r'<evaluation>\s*(.*?)\s*</evaluation>', text, re.DOTALL)
                            final_reasons[original_i] = eval_match.group(1).strip() if eval_match else text
                            
                            success = True
                    except (AttributeError, ValueError):
                        pass
                
                if not success:
                    # Failure: queue for retry
                    new_pending_indices.append(original_i)
            
            pending_indices = new_pending_indices
            attempts += 1

        # 3. Handle any complete failures without resorting to random
        for i in pending_indices:
            print(f"Index {i} failed validation after {max_retries} attempts. Defaulting to first candidate.", file=sys.stderr)
            final_selections[i] = all_candidates_text[i][0] # Deterministic fallback. Absolutely NO random choosing.
            final_reasons[i] = "Failed to parse output after max retries. Defaulted to first candidate." # <-- Added fallback reason

        return final_selections, final_reasons, total_tokens

    def generate_responses(self, prompts, best_of_ns, temperature, max_tokens=16384, max_plan_tokens=500, prune_ratio=1, strategy=None, previous_responses=None, use_tourney=False):
        # see if user decided to use a strategy
        if strategy:
            organized_outputs = {}
            

            # loop through the best_of_ns to run diversification and generation for each n
            for i, best_of_n in enumerate(sorted(best_of_ns, reverse=True)):
                ranked_indexes = None # can move outside if you want the ranking to be reused, but then token usage may be incorrect
                reasonings = None

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
                    ranked_indexes = organized_outputs[best_of_n]["ranked_indexes"]
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

            if use_tourney:
                final_selections, selection_reasons, selection_tokens = self.tourney_select_solution(self, best_of_n, self.group_size, prompts, responses_list)
            else:
                final_selections, selection_reasons, selection_tokens = self.select_solution(best_of_n, prompts, responses_list, max_tokens)

            organized_outputs[best_of_n]["Final Answers"] = final_selections
            organized_outputs[best_of_n]["Selection Reasons"] = selection_reasons
            organized_outputs[best_of_n]["All Answers"] = responses_list
            organized_outputs[best_of_n]["total_tokens"] = [a+b for a,b in zip(selection_tokens, organized_outputs[best_of_n]["total_tokens"])]

        return organized_outputs