"""
run_custom.py
=============
Entry-point script that wires CustomModelSolver into matharena's Runner.

Usage
-----
    cd /u/stevex2/prompt_scaffolding/CS497/prompt_scaffolding
    python run_custom.py \
        --comp hmmt/hmmt_feb_2025 \
        --model qwen3_4b_bon \
        --n 1 \
        [--problems 1 2 3] \
        [--redo-all]

Arguments
---------
--comp    : Competition name relative to matharena's configs/competitions dir
              e.g. hmmt/hmmt_feb_2025
--model   : Solver config name (without .yaml) relative to this script's
              configs/models dir  e.g. qwen3_4b_bon
--n       : Number of matharena *runs* per problem (independent end-to-end
              evaluations).  best_of_n inside the YAML controls how many vLLM
              candidates are generated *within* each run.
--problems: (optional) 1-based problem indices to restrict evaluation
--redo-all: (optional) Ignore existing saved runs and redo everything

Note: the matharena Runner saves per-problem JSON.zst files to
      outputs/<comp>/<model>/
"""

import argparse
import os
import sys

# ---------------------------------------------------------------------------
# Path setup – make both matharena and prompt_scaffolding importable.
# ---------------------------------------------------------------------------
HERE          = os.path.dirname(os.path.abspath(__file__))
MATHARENA_SRC = os.path.abspath(os.path.join(HERE, "../matharena/src"))
MATHARENA_DIR = os.path.abspath(os.path.join(HERE, "../matharena"))

for p in [HERE, MATHARENA_SRC]:
    if p not in sys.path:
        sys.path.insert(0, p)

from loguru import logger
from matharena.runner import Runner

# Our custom solver lives in this directory.
from custom_model_solver import CustomModelSolver


# ---------------------------------------------------------------------------
# Monkey-patch Runner._initialize_solver to handle type: custom_model
# ---------------------------------------------------------------------------
_original_initialize_solver = Runner._initialize_solver


def _patched_initialize_solver(self, solver_config, default_prompt_template,
                                default_api_client_args, last_chance_prompt):
    if solver_config.get("type") == "custom_model":
        problem_answers = {p["problem_idx"]: p["answer"] for p in getattr(self, "problems", [])}
        return CustomModelSolver(
            solver_config, default_prompt_template,
            default_api_client_args, last_chance_prompt,
            problem_answers=problem_answers
        )
    return _original_initialize_solver(
        self, solver_config, default_prompt_template,
        default_api_client_args, last_chance_prompt,
    )


Runner._initialize_solver = _patched_initialize_solver


# ---------------------------------------------------------------------------
# Monkey-patch Runner.load_solver_config to handle type: custom_model
# ---------------------------------------------------------------------------
import yaml as _yaml

_original_load_solver_config = Runner.load_solver_config


def _patched_load_solver_config(self, solver_config_path):
    with open(solver_config_path, "r") as f:
        raw = _yaml.safe_load(f)

    if raw.get("type") != "custom_model":
        return _original_load_solver_config(self, solver_config_path)

    # For custom_model type, pass everything through as model_config.
    human_readable_id = raw.pop("human_readable_id")
    raw.pop("type")
    return {
        "human_readable_id": human_readable_id,
        "type": "custom_model",
        "model_config": raw,
        "scaffold_config": None,
    }


Runner.load_solver_config = _patched_load_solver_config


# ---------------------------------------------------------------------------
# Monkey-patch Runs.validate_history to allow history=None for custom_model
# ---------------------------------------------------------------------------
from matharena.runs import Runs

_original_validate_history = Runs.validate_history


def _patched_validate_history(self, history):
    if self.solver_type == "custom_model":
        assert history is None, f"History should be None for custom_model but got: {history}"
        return
    _original_validate_history(self, history)


Runs.validate_history = _patched_validate_history


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Run CustomModelSolver (vLLM + best-of-N) via matharena Runner"
    )
    parser.add_argument("--comp",     required=True,
                        help="Competition name, e.g. hmmt/hmmt_feb_2025")
    parser.add_argument("--model",    required=True,
                        help="Solver config filename (no .yaml), e.g. qwen3_4b_bon")
    parser.add_argument("--n",        type=int, default=1,
                        help="Number of end-to-end runs per problem (default: 1)")
    parser.add_argument("--problems", type=int, nargs="+", default=None,
                        help="1-based problem indices to run (default: all)")
    parser.add_argument("--redo-all", action="store_true",
                        help="Redo all runs even if outputs already exist")
    parser.add_argument("--comp-configs-dir", default=None,
                        help="Path to competition configs dir "
                             "(default: matharena/configs/competitions)")
    parser.add_argument("--model-configs-dir", default=None,
                        help="Path to solver configs dir "
                             "(default: this script's configs/models)")
    parser.add_argument("--output-dir", default="outputs",
                        help="Where to write run outputs (default: outputs/)")
    args = parser.parse_args()

    # Default config dirs
    comp_configs_dir  = args.comp_configs_dir  or os.path.join(MATHARENA_DIR, "configs", "competitions")
    model_configs_dir = args.model_configs_dir or os.path.join(HERE, "configs", "models")

    logger.info(f"Competition      : {args.comp}")
    logger.info(f"Solver config    : {args.model}")
    logger.info(f"Runs per problem : {args.n}")
    logger.info(f"Problems         : {args.problems or 'all'}")
    logger.info(f"Comp configs     : {comp_configs_dir}")
    logger.info(f"Model configs    : {model_configs_dir}")
    logger.info(f"Output dir       : {args.output_dir}")

    runner = Runner(
        comp_name         = args.comp,
        runs_per_problem  = args.n,
        problem_ids       = args.problems,
        comp_configs_dir  = comp_configs_dir,
        solver_configs_dir= model_configs_dir,
        output_dir        = args.output_dir,
        redo_all          = args.redo_all,
    )

    runner.run(args.model)

    # -----------------------------------------------------------------------
    # Log summary metrics
    # -----------------------------------------------------------------------
    output_dir = os.path.join(args.output_dir, args.comp, args.model)
    print("Putting to output dir:", output_dir)
    from matharena.runs import Runs
    
    total_problems = 0
    total_runs = 0
    total_correct = 0

    for problem in runner.problems:
        runs = Runs(
            comp_name=args.comp,
            is_fa=runner.is_fa_comp,
            solver_name=args.model,
            solver_type="custom_model",
            problem=problem,
            output_dir=output_dir,
        )
        # runs.load_from_file()
        # if runs.N > 0:
            # total_problems += 1
            # total_runs += runs.N
            # total_correct += sum(c for c in runs.correct if c is True)

    if total_runs > 0:
        logger.info("=== Final Metrics ===")
        logger.info(f"Total problems evaluated: {total_problems}")
        logger.info(f"Total runs completed: {total_runs}")
        logger.info(f"Total correct runs: {total_correct}")
        logger.info(f"Overall Accuracy (Pass@1): {total_correct / total_runs:.2%}")
        logger.info("=====================")


if __name__ == "__main__":
    main()
