#!/bin/bash
#SBATCH --mem=48g
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpuA40x4
#SBATCH --account=bfvr-delta-gpu
#SBATCH --job-name=scaffold_n100rg
#SBATCH --time=47:00:00
#SBATCH --constraint="scratch"
#SBATCH -e slurm-n100rg-%A_%a.err
#SBATCH -o slurm-n100rg-%A_%a.out
### bon-split parallelism: each (config, bon-group) runs on its OWN GPU in parallel, so no
### single task carries all of best_of_N. 2 configs (plan 1000/2500) x 3 bon-groups
### ({16},{8},{4,2,1}) = 6 tasks. Each is well under 48h; a merge step (merge_bon_splits.py)
### recombines the per-bon JSONs afterward. bon-only (bok archived as worse).
#SBATCH --gpus-per-node=1
#SBATCH --gpu-bind=none
#SBATCH --array=0-5
##SBATCH --mail-user=sl212@illinois.edu
##SBATCH --mail-type="BEGIN,END"

module reset
module list
echo "Job is starting on $(hostname)"
echo "Array task ${SLURM_ARRAY_TASK_ID} of job ${SLURM_ARRAY_JOB_ID}"

cd ~/CS497/prompt_scaffolding
export VLLM_LOGGING_LEVEL=ERROR
export VLLM_CACHE_ROOT="$PWD/.vllm_cache/n100rg_${SLURM_ARRAY_TASK_ID}"
mkdir -p "$VLLM_CACHE_ROOT"

if [[ ! -f baseline_cache.json ]]; then
    echo "ERROR: baseline_cache.json missing -- run job_baseline.slurm first."
    exit 1
fi

# task -> (plan, bon-group). Chunk counts come from the cache (bon=8 -> 4, bon=16 -> 2),
# so splitting best_of_ns does NOT change chunking. bon=32 is intentionally excluded
# (ranking 32 plans at plan=2500 would exceed max_model_len).
# NOTE: do NOT name this array GROUPS -- that is a reserved bash builtin (the user's
# group IDs) and silently clobbers the assignment.
PLANS=(1000 1000 1000 2500 2500 2500)
BON_GROUPS=("16" "8" "4 2 1" "16" "8" "4 2 1")
PLAN=${PLANS[$SLURM_ARRAY_TASK_ID]}
GROUP=${BON_GROUPS[$SLURM_ARRAY_TASK_ID]}
echo "Config: plan=$PLAN prune=2 bon-group=[$GROUP] num_examples=100"

# $GROUP is intentionally unquoted so "4 2 1" expands to three --best_of_ns args.
uv run --no-sync main.py \
    --cache_fn baseline_cache.json \
    --num_examples 100 \
    --max_plan_tokens "$PLAN" \
    --prune_ratio 2 \
    --regen \
    --num_gpus 1 \
    --best_of_ns $GROUP

echo "=== plan=$PLAN bon-group=[$GROUP] exit: $? ==="
