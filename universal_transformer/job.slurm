#!/bin/bash
#SBATCH --mem=64g
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1    # Run 1 main task (torchrun handles the 8 subprocesses)
#SBATCH --cpus-per-task=32     # Give plenty of CPU cores for data loading (4*8)
#SBATCH --partition=gpuA100x8  # <- CHANGED: CPU partition won't work for 8-GPU training
#SBATCH --account=bfvr-delta-gpu
#SBATCH --job-name=ut_h1_pretrain
#SBATCH --time=04:00:00
#SBATCH --constraint="scratch"
#SBATCH -e slurm-%j.err
#SBATCH -o slurm-%j.out

### GPU options ###
#SBATCH --gpus-per-node=8
#SBATCH --gpu-bind=none        # Let torchrun handle binding

##SBATCH --mail-user=sl212@illinois.edu
##SBATCH --mail-type="BEGIN,END"

# --- MODULES ---
module reset
module load pythonmodule list

# --- UV SETUP ---
# 1. Ensure uv is found (since you installed it in your home directory)
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:$PATH"

# 2. Set cache to scratch (avoids filling home quota)
# export UV_CACHE_DIR="$SCRATCH/.uv_cache" 

echo "Job is starting on $(hostname)"
echo "Using uv from: $(which uv)"

# --- EXECUTION ---
cd ~/CS497/universal_transformer/hierarchical-reasoning-model-analysis
uv run --frozen torchrun --nproc-per-node 8 pretrain.py arch=hrm_v2_params_matched arch.H_cycles=1
