#!/bin/bash
#SBATCH --mem=32g
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --partition=gpuA40x4
#SBATCH --account=bfvr-delta-gpu
#SBATCH --job-name=scaffold_sweep
#SBATCH --time=48:00:00
#SBATCH --constraint="scratch"
#SBATCH -e slurm-%A_%a.err
#SBATCH -o slurm-%A_%a.out
### GPU options ###
# One config per array task, one GPU per task. A single config runs ~17-21h, so packing
# several onto one GPU serially would exceed the 48h partition cap.
#SBATCH --gpus-per-node=1
#SBATCH --gpu-bind=none
### 3 max_plan_tokens (1000 2500 4000) x 4 prune_ratios (1.5 2 3 4) = 12 configs
#SBATCH --array=0-11
##SBATCH --mail-user=sl212@illinois.edu
##SBATCH --mail-type="BEGIN,END"

module reset
module list
echo "Job is starting on $(hostname)"
echo "Array task ${SLURM_ARRAY_TASK_ID} of job ${SLURM_ARRAY_JOB_ID}"
echo "Using uv from: $(which uv)"

# --- EXECUTION ---
cd ~/CS497/prompt_scaffolding

# Every task reuses the shared baseline_cache.json; none of them regenerate it.
# (run_experiment.sh hard-fails in array mode if the cache is missing, so 12 tasks
#  can never race to rewrite it.)
export SKIP_BASELINE=1
export CONFIG_INDEX=${SLURM_ARRAY_TASK_ID}

# Full rerun: all three pruning paths (rank/random/tourney) off the cached baseline,
# with the fixed tourney survivor count and correct per-path token accounting.
# (ONLY_PATHS unset -> main.py runs all three.)

./run_experiment.sh
