class ranker():
    def __init__(item: str, llm, seed):
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