from model.strategies import HypothesisStrategy, PlanStrategy, ConceptStrategy, ReasoningStructureStrategy, CountdownStrategy, UserStrategy
from model.utils import extract_answer
from model.rank import ranker

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
    def __init__(self, model_name: str, num_gpus: int = 1, seed=42):
        self.llm = LLM(model=model_name, tensor_parallel_size=num_gpus, max_model_len=32768)# max_model_len=65536)
        self.seed = seed

        self.ranker = ranker("Solutions", self.llm, self.seed)

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
            
        final_selections, final_sel_reasoning, final_sel_tokens = self.select_solution(
            best_of_n=group_size,  
            prompts=prompts,
            responses_list=subset_responses_list,
            max_tokens=max_tokens,
            max_retries=max_retries
        )
        
        # 5. Resolve final indexes and consolidate returns
        for i in range(N):
            total_tokens[i] += final_sel_tokens[i]
                
            # Log final bracket action
            bracket_history[i].append({
                "round": "Final Selection",
                "group_candidates": active_indices[i],
                "ranked_order": active_indices[i], 
                "kept_candidates": [final_selections[i]],
                "reasoning": final_sel_reasoning
            })

        return final_selections, bracket_history, total_tokens

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

    def generate_responses(self, prompts, best_of_ns, temperature, max_tokens=16384, max_plan_tokens=500, prune_ratio=1, strategy=None, previous_responses=None, group_size=4):
        organized_outputs = {
            "baseline": {},
            "rank": {},
            "random": {},
            "tourney": {}
        }
        
        max_bon = max(best_of_ns)
        
        # We will populate this if we are running the baseline (no cache)
        raw_chunks_cache = {}
        
        # 1. Base Generation: Only if no cache is provided
        if previous_responses is None:
            if strategy is None:
                # Baseline generation
                sampling_params = SamplingParams(n=max_bon, temperature=temperature, top_p=1, max_tokens=max_tokens, seed=self.seed)
                print("Generating Baseline Max BoN Solutions", file=sys.stderr)
                outputs = self.llm.chat([[{"role": "user", "content": f"{prompt}\n\nFirst, write out your step-by-step thoughts on how to solve this in plain text without using any tags. Then, provide your final answer strictly inside <answer></answer> tags."}] for prompt in prompts], sampling_params=sampling_params)
                base_max_responses = [[{"text": out.text, "token_count": len(out.token_ids)} for out in req.outputs] for req in outputs]
            else:
                # Completion strategy initial plan generation
                plan_sampling = SamplingParams(n=max_bon, temperature=temperature, top_p=0.95, max_tokens=max_plan_tokens, seed=self.seed)
                print("Generating Completion Initial Response", file=sys.stderr)
                outputs = self.llm.chat([[{"role": "user", "content": f"{prompt}\n\nFirst, write out your step-by-step thoughts on how to solve this in plain text without using any tags. Then, provide your final answer strictly inside <answer></answer> tags."}] for prompt in prompts], sampling_params=plan_sampling)
                base_max_responses = [[{"text": out.text, "token_count": len(out.token_ids)} for out in req.outputs] for req in outputs]
                
        # 2. Iterate through each BoN
        for bon in sorted(best_of_ns, reverse=True):
            # Initialize storage
            if strategy is None:
                organized_outputs["baseline"][bon] = {"chunks": []}
            else:
                for path in ["rank", "random", "tourney"]:
                    organized_outputs[path][bon] = {"chunks": []}

            # Determine the chunks for this BoN
            if previous_responses is None:
                # We are building the cache: slice base_max_responses into chunks
                num_chunks = min(3, max_bon // bon)
                if num_chunks == 0: continue
                
                chunks_for_bon = []
                for chunk_idx in range(num_chunks):
                    start_idx = chunk_idx * bon
                    end_idx = start_idx + bon
                    current_chunk = [[resp for resp in prompt_resps[start_idx:end_idx]] for prompt_resps in base_max_responses]
                    chunks_for_bon.append(current_chunk)
                
                # Save these chunks for the cache export
                raw_chunks_cache[str(bon)] = chunks_for_bon
            else:
                # We are using the cache: load pre-made chunks directly
                chunks_for_bon = previous_responses.get(str(bon), [])

            # Process each chunk iteratively
            for current_chunk in chunks_for_bon:
                if strategy is None:
                    # Baseline: current_chunk already has final answers
                    chunk_data = self._process_final_selection(prompts, bon, current_chunk, group_size, max_tokens)
                    organized_outputs["baseline"][bon]["chunks"].append(chunk_data)
                else:
                    # Pruning Strategy: Prune plans, finish generation, then select
                    strat_out = strategy.generate_prompts(
                        prompts, bon, temperature, 
                        prune_ratio=prune_ratio, 
                        previous_responses=current_chunk, 
                        group_size=group_size
                    )
                    
                    for path in ["rank", "random", "tourney"]:
                        diverse_prompts = strat_out["paths"][path]["prompts"]
                        path_selection_tokens = strat_out["paths"][path]["tokens"]
                        base_tokens = strat_out["base_tokens"]
                        
                        path_responses = []
                        path_gen_tokens = []
                        
                        # Continue final answer generation
                        sampling_params = SamplingParams(temperature=temperature, top_p=0.95, stop=["</answer>"], include_stop_str_in_output=True, max_tokens=max_tokens, seed=self.seed)
                        
                        for i, diverse_req_prompts in enumerate(diverse_prompts):
                            formatted_variants = [f"<|im_start|>system\nAfter thinking, ensure the final formatted answer is within <answer></answer> tags and follows these instructions: {answer_instruction}.<|im_end|>\n<|im_start|>user\n{prompts[i]}<|im_end|>\n<|im_start|>assistant\n{dp}" for dp in diverse_req_prompts]
                            outputs = self.llm.generate(formatted_variants, sampling_params=sampling_params, use_tqdm=False)
                            
                            # Concatenate the plan with the completion and store token count
                            path_responses.append([{"text": dp + out.outputs[0].text, "token_count": len(out.outputs[0].token_ids)} for dp, out in zip(diverse_req_prompts, outputs)])
                            path_gen_tokens.append(sum(len(out.outputs[0].token_ids) for out in outputs))
                            
                        # Select solutions from completions
                        chunk_data = self._process_final_selection(prompts, len(path_responses[0]), path_responses, group_size, max_tokens)
                        
                        # Tally aggregate tokens ensuring we account for every step in the pipeline
                        chunk_data["total_tokens"] = [b + s + g + c for b, s, g, c in zip(base_tokens, path_selection_tokens, path_gen_tokens, chunk_data["sel_tokens"])]
                        chunk_data["tourney_total_tokens"] = [b + s + g + c for b, s, g, c in zip(base_tokens, path_selection_tokens, path_gen_tokens, chunk_data["tourney_sel_tokens"])]
                        
                        organized_outputs[path][bon]["chunks"].append(chunk_data)

        # Append the successfully built cache so main.py can save it
        if previous_responses is None:
            organized_outputs["raw_base_responses"] = raw_chunks_cache
            
        return organized_outputs
    def _process_final_selection(self, prompts, bon, responses_list, group_size, max_tokens):
        """Helper handling selection and formatting of final completions."""
        final_sel, final_reasons, final_tokens = self.select_solution(bon, prompts, responses_list, max_tokens)
        tourney_sel, tourney_reasons, tourney_tokens = self.tourney_select_solution(bon, group_size, prompts, responses_list)
        
        all_answers = [[resp["text"] for resp in prompt_resps] for prompt_resps in responses_list]
        base_tokens = [sum(resp["token_count"] for resp in prompt_resps) for prompt_resps in responses_list]

        return {
            "Final Answers": final_sel,
            "Selection Reasons": final_reasons,
            "Tourney Answers": tourney_sel,
            "Tourney Selection Reasons": tourney_reasons,
            "All Answers": all_answers,
            "sel_tokens": final_tokens,
            "tourney_sel_tokens": tourney_tokens,
            "total_tokens": [b + f for b, f in zip(base_tokens, final_tokens)],
            "tourney_total_tokens": [b + t for b, t in zip(base_tokens, tourney_tokens)]
        }