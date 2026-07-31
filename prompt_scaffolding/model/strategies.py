from model.utils import extract_content, draft_messages
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
        total_tokens = [sum(len(plan.token_ids) for plan in request_output.outputs) for request_output in outputs]

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

def first_k_unique(ordering, labels, k):
    """Take the first `k` plan indices of DISTINCT clusters, walking `ordering`
    (a full permutation of a question's plan indices, in a path's preference order).

    A plan whose cluster (labels[idx]) is already represented is skipped and held
    aside. If the pool has fewer than k distinct clusters, the held-aside duplicates
    backfill (in preference order) so exactly min(k, len(ordering)) indices come back.
    """
    seen = set()
    chosen = []
    dupes = []
    for idx in ordering:
        lab = labels[idx] if idx < len(labels) else idx
        if lab in seen:
            dupes.append(idx)
        else:
            seen.add(lab)
            chosen.append(idx)
            if len(chosen) >= k:
                return chosen
    for idx in dupes:                      # fewer than k clusters exist -> backfill
        if len(chosen) >= k:
            break
        chosen.append(idx)
    return chosen[:k]


class CompletionStrategy(Strategy):
    def __init__(self, llm, seed=42):
        super().__init__(llm, "", "CompletionStrategy", seed)

    def generate_prompts(self, user_prompts, best_of_n, temperature, max_selection_tokens=16000, max_plan_tokens=500, prune_ratio=1, previous_responses=None, group_size=4, diverse=False):
        new_prompts = []
        base_tokens = []
        
        # 1. Generate or load base plans, immediately stripping VLLM objects to save memory
        if previous_responses is None:
            sampling_params = SamplingParams(n=best_of_n, temperature=temperature, top_p=0.95, max_tokens=max_plan_tokens, seed=self.seed)
            print("Generating Completion Initial Response", file=sys.stderr)
            outputs = self.llm.chat([draft_messages(prompt) for prompt in user_prompts],
                                    sampling_params=sampling_params)

            for request_output in outputs:
                new_prompts.append([single_output.text for single_output in request_output.outputs])
                base_tokens.append(sum(len(single_output.token_ids) for single_output in request_output.outputs))
        else:
            # previous_responses are now expected to be stripped dicts: {"text": ..., "token_count": ...}
            tokenizer = self.llm.get_tokenizer()
            for request_output in previous_responses:
                prompt_texts = []
                prompt_tokens = 0
                for resp in request_output:
                    # If the response is already short enough, keep it as is
                    if resp["token_count"] <= max_plan_tokens:
                        prompt_texts.append(resp["text"])
                        prompt_tokens += resp["token_count"]
                    else:
                        # Re-tokenize, truncate exactly to max_plan_tokens, and decode
                        encoded = tokenizer.encode(resp["text"], add_special_tokens=False)
                        truncated_text = tokenizer.decode(encoded[:max_plan_tokens])
                        prompt_texts.append(truncated_text)
                        prompt_tokens += max_plan_tokens

                new_prompts.append(prompt_texts)
                base_tokens.append(prompt_tokens)

        number_choices = int(max(1, best_of_n // prune_ratio))
        n_prompts = len(user_prompts)

        # DIVERSE (best-of-k): cluster each question's plans by approach ONCE, so every
        # path can prune to k UNIQUE approaches instead of the top-k by score. The one
        # clustering call is charged to every arm that uses it (each arm's standalone
        # cost includes it). Non-diverse leaves all this untouched -> bon is unchanged.
        if diverse:
            cluster_labels, cluster_tokens = self.ranker.cluster(user_prompts, new_prompts, max_selection_tokens)
        else:
            cluster_labels, cluster_tokens = None, [0] * n_prompts

        # 2. PATH 1: Ranked Pruning
        ranked_indexes, reasonings, rank_tokens = self.ranker.rank(user_prompts, new_prompts, max_selection_tokens)
        if diverse:
            # ranked_indexes[i] is a full permutation -> first-k-unique directly.
            final_ranked_indexes = [first_k_unique(ranked_indexes[i], cluster_labels[i], number_choices) for i in range(n_prompts)]
        else:
            final_ranked_indexes = [indices[:number_choices] for indices in ranked_indexes]
        ranked_diverse_prompts = [[new_prompts[i][idx] for idx in diverse_indexes if idx < len(new_prompts[i])] for i, diverse_indexes in enumerate(final_ranked_indexes)]

        # 3. PATH 2: Random Pruning
        if diverse:
            # first-k-unique over a full RANDOM permutation (unique approaches, random order)
            final_random_indexes = [first_k_unique(random.sample(range(len(new_prompts[i])), len(new_prompts[i])), cluster_labels[i], number_choices) for i in range(n_prompts)]
        else:
            final_random_indexes = [random.sample(range(len(new_prompts[i])), min(number_choices, len(new_prompts[i]))) for i in range(n_prompts)]
        random_diverse_prompts = [[new_prompts[i][idx] for idx in diverse_indexes] for i, diverse_indexes in enumerate(final_random_indexes)]

        # 4. PATH 3: Tournament Pruning
        tourney_indexes, tourney_tokens = self.ranker.tourney_rank(user_prompts, new_prompts, group_size, number_choices)
        if diverse:
            # tourney only yields k survivors; extend to a full ordering (survivors first,
            # then the rest in quality-rank order) so dedup has spares to backfill from.
            final_tourney_indexes = []
            for i in range(n_prompts):
                surv = list(tourney_indexes[i])
                tail = [j for j in ranked_indexes[i] if j not in surv]
                final_tourney_indexes.append(first_k_unique(surv + tail, cluster_labels[i], number_choices))
        else:
            final_tourney_indexes = tourney_indexes
        tourney_diverse_prompts = [[new_prompts[i][idx] for idx in diverse_indexes if idx < len(new_prompts[i])] for i, diverse_indexes in enumerate(final_tourney_indexes)]

        # Per-arm selection cost. In diverse mode each arm also bears the one clustering call.
        rank_cost = [rank_tokens[i] + cluster_tokens[i] for i in range(n_prompts)] if diverse else rank_tokens
        random_cost = [cluster_tokens[i] for i in range(n_prompts)] if diverse else [0] * n_prompts
        tourney_cost = [tourney_tokens[i] + cluster_tokens[i] for i in range(n_prompts)] if diverse else tourney_tokens

        # Return all paths and base generation tokens
        return {
            "base_prompts": new_prompts,
            "base_tokens": base_tokens,
            "paths": {
                "rank": {"prompts": ranked_diverse_prompts, "tokens": rank_cost},
                "random": {"prompts": random_diverse_prompts, "tokens": random_cost},
                "tourney": {"prompts": tourney_diverse_prompts, "tokens": tourney_cost}
            }
        }