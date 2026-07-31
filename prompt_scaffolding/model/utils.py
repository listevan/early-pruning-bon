import re
import json
import sys

# TOKEN ACCOUNTING IS DECODE-ONLY, DELIBERATELY.
#
# Every counter in this pipeline sums `len(out.token_ids)` -- tokens the model SAMPLED.
# Prompt (prefill) tokens are not counted anywhere, on purpose:
#
#   * vLLM runs with prefix caching enabled by default, so the k continuation requests of
#     one question share their scaffold and only the first actually recomputes it. Any
#     prefill figure we could compute from the prompts is a logical upper bound, not work
#     the GPU did.
#   * Prefill is one parallel forward pass; decode is one serial pass per token. Adding
#     them treats non-fungible quantities as fungible.
#
# So `mean_tokens` in the results means sampled tokens, and nothing else. If prefill is
# ever wanted, measure it -- RequestOutput exposes prompt_token_ids and num_cached_tokens
# -- and report it as its OWN axis rather than folding it into this total.

# The draft/plan request every arm starts from. Defined once because the baseline
# generation and the CompletionStrategy plan generation must use the BYTE-IDENTICAL
# prompt -- a stray space would change the generations.
DRAFT_INSTRUCTION = ("\n\nFirst, write out your step-by-step thoughts on how to solve this in plain text "
                     "without using any tags. Then, provide your final answer strictly inside "
                     "<answer></answer> tags.")


def draft_messages(question):
    """The chat messages for one draft/plan request."""
    return [{"role": "user", "content": f"{question}{DRAFT_INSTRUCTION}"}]


def even_top_allocation(num_plans, target):
    """Distribute `target` completions across `num_plans` ranked plans (best first)
    as evenly as possible, handing the remainder to the TOP-ranked plans.

    Every plan gets floor(target/num_plans); the first `target % num_plans` plans
    (the highest-ranked ones, since plans arrive in preference order) get one extra.
    The result is therefore near-uniform -- the top and bottom differ by at most one
    -- rather than the steep tilt of the old staircase. This is the deliberate
    choice under a weak pruning ranker: it does not over-bet budget on a ranking that
    is barely better than random, while still breaking ties toward the top for free.

    Counts sum to exactly `target` and are non-increasing (top gets >= bottom).

    Examples:
        even_top_allocation(4, 8)   -> [2, 2, 2, 2]        (prune 2:   uniform)
        even_top_allocation(5, 8)   -> [2, 2, 2, 1, 1]     (prune 1.5: remainder to top)
        even_top_allocation(8, 16)  -> [2, 2, 2, 2, 2, 2, 2, 2]
        even_top_allocation(10, 16) -> [2, 2, 2, 2, 2, 2, 1, 1, 1, 1]
    """
    if num_plans <= 0 or target <= 0:
        return []
    base, rem = divmod(target, num_plans)
    # first `rem` (top-ranked) plans get one extra; the rest get `base`.
    return [base + 1 if i < rem else base for i in range(num_plans)]

def extract_answer(text):
    # Pattern looks for everything between <answer> and </answer>
    # re.DOTALL allows the dot (.) to match newlines if the answer is multi-line
    match = re.findall(r'<answer>(.*?)</answer>', text, re.DOTALL)
    
    if match:
        return match[-1].strip()
    
    # If no tags exist, return the original string
    return text

def extract_content(text):
    # extract the <think><\think> tags and return result
    match = re.search(r"(?<=<\/think>)\s*([\s\S]*)", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def vllm_encoder(obj):
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    return str(obj) # Fallback for any weird types inside

def format_json_inplace(filepath, indent=4):
    # 1. Read the existing data
    with open(filepath, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error: {filepath} is not valid JSON.", file=sys.stderr)
            return

    # 2. Create the standard pretty-printed string
    # This ensures strings and objects are on new lines as requested
    pretty_json = json.dumps(data, indent=indent)

    # 3. Use Regex to find numeric arrays and collapse them
    # This matches '[' followed by numbers, commas, and whitespace, ending in ']'
    # It will NOT match ["a", "b"] because of the quote marks.
    numeric_array_pattern = r'\[(?:\s*-?[\d\.]+\s*,?)+\s*\]'

    def collapse_match(match):
        # Remove all newlines and extra spaces, then add a single space after commas
        collapsed = re.sub(r'\s+', '', match.group(0))
        return collapsed.replace(',', ', ')

    fixed_json = re.sub(numeric_array_pattern, collapse_match, pretty_json)

    # 4. Overwrite the original file
    with open(filepath, 'w') as f:
        f.write(fixed_json)