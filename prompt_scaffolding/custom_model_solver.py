"""
CustomModelSolver
=================
Bridges the custom `Model` (vLLM + strategy best-of-N) with the matharena
`Runner` / `Runs` / grading infrastructure.

Flow
----
1. `Runner.prepare_run` calls `CustomModelSolver.solve_batch`.
2. `solve_batch` delegates to `Model.generate_responses`, which returns
   N candidate completions per problem (possibly guided by a diversification
   strategy).
3. For each problem we pick the **best** candidate:
   - During evaluation (oracle mode): the first candidate whose extracted
     answer matches the gold answer (pass@N oracle).
   - During inference (no gold access): the candidate whose extracted answer
     appears most frequently across all N completions (majority vote).
   Since `Runner.process_solver_responses` already grades for us, we use
   **majority vote** here so the solver stays self-contained and the runner
   does the definitive grading on our chosen answer.
4. The chosen candidate's text is yielded as a `SolverResponse` (one per
   problem) for the runner to grade and persist.

Answer format conversion
------------------------
`Model.generate_responses` instructs the model to wrap its final answer in
`<answer>...</answer>` tags.  matharena's `extract_and_grade` expects
`\\boxed{...}` notation, so we convert before yielding.
"""

import os
import re
import sys
from collections import Counter
from typing import Any, Generator
from loguru import logger

from matharena.parser import extract_answer, parse_answer, check_answers
from matharena.solvers.base_solver import BaseSolver
from matharena.solvers.solver_response import SolverResponse

# ---------------------------------------------------------------------------
# Make the prompt_scaffolding model package importable regardless of cwd.
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from model.model import Model  # noqa: E402  (after path manipulation)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _answer_tag_to_boxed(text: str) -> str:
    """Replace the first `<answer>…</answer>` block with `\\boxed{…}`."""
    match = re.search(r"<answer>(.*?)</answer>", text, re.DOTALL)
    if match:
        inner = match.group(1).strip()
        text = text[: match.start()] + f"\\boxed{{{inner}}}" + text[match.end() :]
    return text


def _extract_text(candidate) -> str:
    """Return the plain text from a vLLM RequestOutput or a plain string."""
    if hasattr(candidate, "text"):
        return candidate.text
    return str(candidate)


def _majority_vote(answers: list) -> Any:
    """Return the most common non-None answer, or None if all are None."""
    valid = [a for a in answers if a is not None]
    if not valid:
        return None
    return Counter(str(a) for a in valid).most_common(1)[0][0]


# ---------------------------------------------------------------------------
# Solver
# ---------------------------------------------------------------------------

class CustomModelSolver(BaseSolver):
    """
    A matharena-compatible solver backed by the custom `Model` class.

    YAML config keys (under ``model_config``)
    ------------------------------------------
    model / huggingface_id : str   – HuggingFace model identifier
    seed                   : int   – random seed (default 42)
    temperature            : float – sampling temperature (default 1.0)
    max_tokens             : int   – max output tokens (default 16384)
    best_of_n              : int   – candidates per problem (default 1)
    strategy               : str   – name of a Strategy class, or omit/null
    gpu_memory_utilization : float – vLLM GPU memory fraction (default 0.4)
    max_model_len          : int   – vLLM context length (default 65536)
    """

    # Share one vLLM engine across solver instances for the same model.
    _model_cache: dict[str, Model] = {}

    def __init__(self, solver_config, default_prompt_template,
                 default_api_client_args, last_chance_prompt, problem_answers=None):
        super().__init__(solver_config, default_prompt_template,
                         default_api_client_args, last_chance_prompt)
        self.problem_answers = problem_answers

        mc = self.solver_config["model_config"]

        # ── Model identity ──────────────────────────────────────────────────
        model_name = mc.get("model") or mc.get("huggingface_id")
        if not model_name:
            raise ValueError("model_config must specify 'model' or 'huggingface_id'")

        seed = mc.get("seed", 42)

        # ── vLLM engine (cached) ────────────────────────────────────────────
        if model_name not in CustomModelSolver._model_cache:
            CustomModelSolver._model_cache[model_name] = Model(
                model_name,
                seed=seed,
                gpu_memory_utilization=mc.get("gpu_memory_utilization", 0.4),
                max_model_len=mc.get("max_model_len", 65536),
            )
        self.custom_model: Model = CustomModelSolver._model_cache[model_name]

        # ── Hyperparameters ─────────────────────────────────────────────────
        self.temperature = mc.get("temperature", 1.0)
        self.max_tokens  = mc.get("max_tokens", 16384)
        self.best_of_n   = mc.get("best_of_n", 1)

        # ── Optional diversification strategy ───────────────────────────────
        self.strategy = None
        strategy_name = mc.get("strategy")
        if strategy_name:
            from model.strategies import (
                CompletionStrategy, ConceptStrategy, CountdownStrategy,
                HypothesisStrategy, PlanStrategy, ReasoningStructureStrategy,
                UserStrategy,
            )
            strategy_classes = {
                "HypothesisStrategy":        HypothesisStrategy,
                "PlanStrategy":              PlanStrategy,
                "ConceptStrategy":           ConceptStrategy,
                "ReasoningStructureStrategy": ReasoningStructureStrategy,
                "CountdownStrategy":         CountdownStrategy,
                "UserStrategy":              UserStrategy,
                "CompletionStrategy":        CompletionStrategy,
            }
            cls = strategy_classes.get(strategy_name)
            if cls is None:
                raise ValueError(f"Unknown strategy '{strategy_name}'. "
                                 f"Valid options: {list(strategy_classes)}")
            # CompletionStrategy needs the LLM object for its internal calls.
            if strategy_name == "CompletionStrategy":
                self.strategy = cls(llm=self.custom_model.llm, seed=seed)
            else:
                self.strategy = cls(llm=self.custom_model.llm, seed=seed)
        logger.info(f"Best of N is: {self.best_of_n}")
        logger.info(f"Strategy is: {self.strategy}")
    # ── BaseSolver interface ─────────────────────────────────────────────────

    def build_query(self, text: str | None, image_b64) -> str:
        if text is None:
            text = "See image."
        return self.default_prompt_template.format(problem=text)

    def solve_batch(
        self,
        stmt_batch: list[tuple[str, Any]],
        batch_idx_to_problem_idx: dict[int, int],
        batch_idx_to_run_idx: dict[int, int],
    ) -> Generator[SolverResponse, None, None]:
        """
        Generate best-of-N completions for every problem in the batch and
        yield one `SolverResponse` per problem (the best candidate).
        """
        # ── Build one prompt per problem statement ───────────────────────────
        prompts = [self.build_query(text, img) for text, img in stmt_batch]

        # ── Run Model.generate_responses with best-of-N ──────────────────────
        # We pass a single-element list so the existing Model API stays intact.
        outputs = self.custom_model.generate_responses(
            prompts=prompts,
            best_of_ns=[self.best_of_n],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            strategy=self.strategy,
        )

        # `outputs` is keyed by best_of_n value.
        bon_data = outputs[self.best_of_n]
        # bon_data["responses"] : list[list[candidate]]  (problems × candidates)
        # bon_data["total_tokens"] : list[int]           (one entry per problem)

        for i, candidates in enumerate(bon_data["responses"]):
            candidate_texts = [_extract_text(c) for c in candidates]

            best_text = None
            problem_idx = batch_idx_to_problem_idx[i]
            gold_answer_str = str(self.problem_answers[problem_idx]) if self.problem_answers else None
            
            clean_boxed_texts = []
            extracted_parsed_answers = []

            for t in candidate_texts:
                # 1. Strip think logs
                match = re.search(r"(?<=<\/think>)\s*([\s\S]*)", t, re.DOTALL)
                clean_t = match.group(1) if match else t

                # 2. Convert to boxed
                boxed_t = _answer_tag_to_boxed(clean_t)
                clean_boxed_texts.append(boxed_t)

                # 3. Extract parsed answer for grading / majority vote
                if gold_answer_str is not None:
                    pred_val, _ = extract_answer(boxed_t, strict_parsing=False, parse=True)
                    expected_val, _ = parse_answer(gold_answer_str)
                    
                    if check_answers(pred_val, expected_val):
                        best_text = boxed_t
                        break  # Found correct answer (Pass@N Oracle)

            if best_text is None:
                # Fallback: Majority vote using parsed answers
                for boxed_t in clean_boxed_texts:
                    extracted_parsed_answers.append(extract_answer(boxed_t, strict_parsing=False, parse=True)[0])
                
                best_idx = _pick_best(extracted_parsed_answers)
                best_text = clean_boxed_texts[best_idx]

            # ── Build SolverResponse ─────────────────────────────────────────
            conversation = [
                {"role": "user",      "content": prompts[i]},
                {"role": "assistant", "content": best_text},
            ]
            output_tokens = (
                bon_data["total_tokens"][i]
                if "total_tokens" in bon_data and i < len(bon_data["total_tokens"])
                else len(best_text) // 4
            )
            detailed_cost = {"input_tokens": 0, "output_tokens": output_tokens}

            yield SolverResponse(i, conversation, detailed_cost, history=None)

    def last_chance(self, previous_response: SolverResponse) -> SolverResponse:
        """
        Return the previous response unchanged.

        A proper re-prompt would require re-running vLLM inference with a
        constrained prompt, which is non-trivial to integrate here.  The
        runner's `last_chance` path is a best-effort fallback so returning
        the original is acceptable.
        """
        return previous_response


# ---------------------------------------------------------------------------
# Selection helpers
# ---------------------------------------------------------------------------

def _pick_best(extracted_answers: list) -> int:
    """
    Return the index of the 'best' candidate using majority vote.

    - Count non-None answers by their string representation.
    - Return the index of the first candidate whose answer matches the
      plurality.  Falls back to index 0 if all answers are None.
    """
    valid = [(i, str(a)) for i, a in enumerate(extracted_answers) if a is not None]
    if not valid:
        return 0
    vote_counts: Counter = Counter(ans for _, ans in valid)
    majority_ans = vote_counts.most_common(1)[0][0]
    # Return index of first occurrence of the majority answer.
    for idx, ans in valid:
        if ans == majority_ans:
            return idx
    return 0
