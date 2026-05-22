#!/bin/bash
#SBATCH --mem=16g
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --partition=gpuA100x4
#SBATCH --account=bfvr-delta-gpu
#SBATCH --job-name=ut_h1_pretrain
#SBATCH --time=48:00:00
#SBATCH --constraint="scratch"
#SBATCH -e slurm-%j.err
#SBATCH -o slurm-%j.out
### GPU options ###
#SBATCH --gpus-per-node=1
#SBATCH --gpu-bind=none
##SBATCH --mail-user=sl212@illinois.edu
##SBATCH --mail-type="BEGIN,END"

module reset
module list
echo "Job is starting on $(hostname)"
echo "Using uv from: $(which uv)"

# --- EXECUTION ---
cd ~/CS497/prompt_scaffolding
# uv run main.py
./run_experiment.sh
# sleep 5h
