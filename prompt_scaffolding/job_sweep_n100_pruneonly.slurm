#!/bin/bash
#SBATCH --mem=32g
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpuA40x4
#SBATCH --account=bfvr-delta-gpu
#SBATCH --job-name=scaffold_n100po
#SBATCH --time=48:00:00
#SBATCH --constraint="scratch"
#SBATCH -e slurm-n100po-%A_%a.err
#SBATCH -o slurm-n100po-%A_%a.out
### GPU options ###
# One config per array task, one GPU per task. Prune-only finishes only k = N/2 survivors
# (vs regen's N), so a whole config runs ~26-32h even with the deeper bon=32 chunking --
# comfortably under the 48h cap. No bon-split is needed here; that is only required for the
# much heavier regen sweep (job_sweep_n100_regen.slurm), and the last prune-only run at
# this exact config completed inside one task.
#SBATCH --gpus-per-node=1
#SBATCH --gpu-bind=none
### 2 max_plan_tokens (1000 2500) x prune_ratio 2 = 2 tasks.
#SBATCH --array=0-1
##SBATCH --mail-user=sl212@illinois.edu
##SBATCH --mail-type="BEGIN,END"

module reset
module list
echo "Job is starting on $(hostname)"
echo "Array task ${SLURM_ARRAY_TASK_ID} of job ${SLURM_ARRAY_JOB_ID}"
echo "Using uv from: $(which uv)"

cd ~/CS497/prompt_scaffolding
export VLLM_LOGGING_LEVEL=ERROR
export VLLM_CACHE_ROOT="$PWD/.vllm_cache/n100po_${SLURM_ARRAY_TASK_ID}"
mkdir -p "$VLLM_CACHE_ROOT"

# Shared bon=32 / 100-prompt cache built by job_baseline.slurm. Identical cache to the
# regen sweep, so the two arrays are directly comparable: chunk counts come from the CACHE
# (bon=1,2,4,8 -> 4 chunks, bon=16 -> 2), not from this array's best_of_ns.
if [[ ! -f baseline_cache.json ]]; then
    echo "ERROR: baseline_cache.json missing -- run job_baseline.slurm first."
    exit 1
fi

PLANS=(1000 2500)
PLAN=${PLANS[$SLURM_ARRAY_TASK_ID]}
echo "Config: plan=$PLAN prune=2 bons=[1 2 4 8 16] num_examples=100 regen=NO"

# Every parameter is pinned on the command line rather than left to a main.py default.
# Defaults have drifted before (--num_examples moved 100 -> 30 for an unrelated experiment
# and silently changed a sweep), so nothing here inherits one.
#
# PRUNE-ONLY: no --regen, so main.py prunes to k = N/prune_ratio survivors and finishes
# each once. Output files carry no variant suffix.
uv run --no-sync main.py \
    --cache_fn baseline_cache.json \
    --num_examples 100 \
    --max_plan_tokens "$PLAN" \
    --prune_ratio 2 \
    --num_gpus 1 \
    --best_of_ns 1 2 4 8 16

echo "=== plan=$PLAN prune-only exit: $? ==="
