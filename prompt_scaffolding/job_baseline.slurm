#!/bin/bash
#SBATCH --mem=64g
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --partition=gpuA40x4
#SBATCH --account=bfvr-delta-gpu
#SBATCH --job-name=scaffold_base32
#SBATCH --time=48:00:00
#SBATCH --constraint="scratch"
#SBATCH -e slurm-base32-%j.err
#SBATCH -o slurm-base32-%j.out
### GPU options ###
# One monolithic baseline generation over all prompts -> TP across the whole node (this is
# how the original baseline_cache was built). 4B model, TP=4 pools KV cache across 4 A40s
# for big batches over the 100 x 32 completions.
#SBATCH --gpus-per-node=4
#SBATCH --gpu-bind=none
##SBATCH --mail-user=sl212@illinois.edu
##SBATCH --mail-type="BEGIN,END"

module reset
module list
echo "Job is starting on $(hostname)"
echo "Using uv from: $(which uv)"

cd ~/CS497/prompt_scaffolding
export VLLM_LOGGING_LEVEL=ERROR

# Regenerate the baseline at max_bon=32 over all 100 problems. Generating 32 completions
# per question deepens the chunking: num_chunks = min(4, 32 // bon), so bon=8 -> 4 chunks
# (was 2) and bon=16 -> 2 chunks (was 1). That halves the per-question noise at the high-N
# cells that were previously single-draw. Writes baseline_cache.json + a baseline result
# JSON with the curve up to bon=32.
uv run --no-sync main.py \
    --baseline \
    --num_examples 100 \
    --best_of_ns 1 2 4 8 16 32 \
    --num_gpus 4

echo "Baseline done. Cache: $(ls -la baseline_cache.json 2>/dev/null)"
