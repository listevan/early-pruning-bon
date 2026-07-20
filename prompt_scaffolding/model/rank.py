from vllm import LLM, SamplingParams

import random
import sys
import re

from model.utils import extract_content

class ranker():
    def __init__(self, item: str, llm, seed):
        self.item = item # what are we ranking
        self.llm = llm
        self.seed = seed

    def rank(self, user_prompts, rankees, max_selection_tokens=16000, max_retries=3): # TODO: 3/27/26: let max_selection_tokens be sufficiently enough
        # create sampling params for model to determine if it's unique
        sampling_params = SamplingParams(temperature=0.7, top_p=0.8, top_k=20, max_tokens=max_selection_tokens, seed=self.seed)
        
        # 1. Pre-build all the prompts
        all_prompts = []
        for user_prompt, problem_rankee in zip(user_prompts, rankees):
            # Create a list of original indices and shuffle them to combat positional bias
            shuffled_indices = list(range(len(problem_rankee)))
            random.shuffle(shuffled_indices)
            
            # Build the examples string in the randomized order, but keep the original ID tags
            examples_str = "".join([
                f"<example id='i{idx}'>\n{problem_rankee[idx].replace('<think>', '')}\n</example>\n" 
                for idx in shuffled_indices
            ])

            num_candidates = len(problem_rankee) 
            valid_indices = ", ".join([f"i{j}" for j in range(num_candidates)])
            prompt_content = f"""Rank the {num_candidates} {self.item.lower()} based on how likely they are to lead to the correct answer.

            ### Problem:
            {user_prompt}

            ### {self.item}:
            {examples_str}

            ### Instructions:
            1. Briefly evaluate the best approaches.
            2. Rank ALL {num_candidates} solutions from best to worst.
            3. You must use exactly these indices: {valid_indices}. No duplicates and no omissions.

            Output your response EXACTLY in this format:
            <evaluation>
            [Your brief evaluation here]
            </evaluation>
            <results>
            iX
            iY
            ...
            </results>"""

            all_prompts.append([{"role": "user", "content": prompt_content}])

        N = len(user_prompts)
        
        # Arrays to hold the final resolved data in the original order
        final_indexes = [None] * N
        final_reasonings = [""] * N
        final_tokens = [0] * N

        # Queue of indices that still need to be processed successfully
        pending_indices = list(range(N))
        attempts = 0

        while pending_indices and attempts < max_retries:
            print(f"Attempt {attempts + 1}/{max_retries}. Pending: {len(pending_indices)}", file=sys.stderr)
            
            # Extract only the prompts that need to be re-run
            current_prompts = [all_prompts[i] for i in pending_indices]
            
            outputs = self.llm.chat(current_prompts, sampling_params=sampling_params, chat_template_kwargs={"enable_thinking": False})
            
            new_pending_indices = []

            for j, output in enumerate(outputs):
                original_i = pending_indices[j]  # Map batch index back to original index
                text = extract_content(output.outputs[0].text)
                
                # Accumulate tokens across retries
                final_tokens[original_i] += len(output.outputs[0].token_ids)
                
                # 1. Isolate the results block
                results_match = re.findall(r'<results>(.*?)</results>', text, re.DOTALL)
                results_text = results_match[-1].strip() if results_match else text 
                
                # 2. Extract indices and preserve LLM rank order (remove duplicates)
                expected_length = len(rankees[original_i])
                parsed_ints = [int(match) for match in re.findall(r'(?:i)?(\d+)', results_text)] 
                seen = set()
                unique_ints = [x for x in parsed_ints if not (x in seen or seen.add(x)) and x < expected_length]

                # 3. Check if the LLM output length matches expected length
                if len(unique_ints) == expected_length:
                    # Success: Store it and don't add to new_pending_indices
                    final_indexes[original_i] = unique_ints
                    final_reasonings[original_i] = text
                else:
                    # Failure: Save current state just in case we hit max retries, then queue for retry
                    # print(text, file=sys.stderr)
                    final_indexes[original_i] = unique_ints
                    final_reasonings[original_i] = text
                    new_pending_indices.append(original_i)
            
            # Update the queue for the next loop iteration
            pending_indices = new_pending_indices
            attempts += 1

        # Fallback: If any prompts hit max retries and STILL failed length check, randomly fill the missing parts
        for i in pending_indices:
            print(f"Index {i} failed length validation after {max_retries} attempts. Randomly padding.", file=sys.stderr)
            expected_length = len(rankees[i])
            current_ints = final_indexes[i] or []
            
            # Keep only valid indices within bounds
            valid_ints = [x for x in current_ints if x < expected_length]
            
            # Find what is missing and shuffle them
            missing_ints = [x for x in range(expected_length) if x not in valid_ints]
            random.shuffle(missing_ints)
            
            # Append missing random indices to the end of whatever the LLM successfully ranked
            final_indexes[i] = valid_ints + missing_ints

        return final_indexes, final_reasonings, final_tokens
    def tourney_rank(self, user_prompts, rankees, group_size, target_count, max_retries=3):
        """
        Tournament style ranking for partial plans.
        Groups candidates, ranks them, keeps the top half, and repeats until close to
        target_count, then ranks the remaining survivors once to trim to EXACTLY
        target_count.

        The plain halving loop can only ever undershoot: a round takes every prompt with
        more than target_count candidates down by ~half, so a set of 8 with target 5 drops
        straight to 4, skipping the target and leaving the tourney path with fewer survivors
        than the rank/random paths (which keep exactly number_choices). To avoid that, a
        prompt stops halving as soon as one more full round WOULD cross below target_count;
        the leftover (which is then in (target_count, 2*target_count]) is ranked in a single
        final pass and cut to exactly target_count.
        """
        N = len(user_prompts)
        active_indices = [list(range(len(rankees[i]))) for i in range(N)]
        total_tokens = [0] * N

        def halved_size(n):
            # survivors after one grouping round of `n` candidates in chunks of group_size
            total = 0
            for j in range(0, n, group_size):
                clen = min(group_size, n - j)
                total += (clen + 1) // 2 if clen > 1 else clen
            return total

        while True:
            batch_prompts = []
            batch_rankees = []
            chunk_metadata = []
            # Default: carry each prompt's set forward unchanged; only prompts we actively
            # halve this round get rebuilt from their ranked chunks.
            next_active_indices = [list(a) for a in active_indices]
            pruned_any = False

            for i in range(N):
                current_active = active_indices[i]
                # Already at/below target, or one more round would undershoot -> leave for
                # the final trim below rather than dropping below target_count here.
                if len(current_active) <= target_count:
                    continue
                if halved_size(len(current_active)) < target_count:
                    continue

                next_active_indices[i] = []
                for j in range(0, len(current_active), group_size):
                    chunk = current_active[j:j+group_size]
                    if len(chunk) > 1:
                        batch_prompts.append(user_prompts[i])
                        batch_rankees.append([rankees[i][idx] for idx in chunk])
                        chunk_metadata.append((i, chunk))
                        pruned_any = True
                    else:
                        next_active_indices[i].extend(chunk)

            if not pruned_any:
                break

            chunk_final_indexes, _, chunk_tokens = self.rank(batch_prompts, batch_rankees, max_retries=max_retries)

            for k, (i, chunk) in enumerate(chunk_metadata):
                total_tokens[i] += chunk_tokens[k]
                ranked_local_indices = chunk_final_indexes[k]

                # Keep top half (ceiling division to favor keeping more on odd sizes)
                num_to_keep = (len(chunk) + 1) // 2
                valid_local_indices = [idx for idx in ranked_local_indices if idx < len(chunk)]

                # Fallback if VLLM missed indices
                if len(valid_local_indices) < num_to_keep:
                    missing = [idx for idx in range(len(chunk)) if idx not in valid_local_indices]
                    valid_local_indices.extend(missing)

                kept_local = valid_local_indices[:num_to_keep]
                kept_global = [chunk[idx] for idx in kept_local]
                next_active_indices[i].extend(kept_global)

            active_indices = next_active_indices

        # Final trim: any prompt still above target_count gets its remaining survivors ranked
        # in one pass and cut to exactly target_count, matching the rank path's keep semantics.
        trim_prompts = []
        trim_rankees = []
        trim_meta = []
        for i in range(N):
            if len(active_indices[i]) > target_count:
                trim_prompts.append(user_prompts[i])
                trim_rankees.append([rankees[i][idx] for idx in active_indices[i]])
                trim_meta.append(i)

        if trim_prompts:
            trim_indexes, _, trim_tokens = self.rank(trim_prompts, trim_rankees, max_retries=max_retries)
            for k, i in enumerate(trim_meta):
                total_tokens[i] += trim_tokens[k]
                local = active_indices[i]
                ranked_local = [idx for idx in trim_indexes[k] if idx < len(local)]
                # rank() pads to a full permutation, but guard anyway
                missing = [idx for idx in range(len(local)) if idx not in ranked_local]
                ranked_local.extend(missing)
                active_indices[i] = [local[idx] for idx in ranked_local[:target_count]]

        # Any prompt at/below target_count is already correct; slice is a no-op for those.
        final_indexes = [indices[:target_count] for indices in active_indices]
        return final_indexes, total_tokens