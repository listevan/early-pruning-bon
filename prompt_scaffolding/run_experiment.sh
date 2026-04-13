#!/bin/bash

ERR_FILE="slurm-${SLURM_JOB_ID:-$$}.err"

MAX_PLAN_TOKENS=(500 750 1000 1250 1500)
PRUNE_RATIOS=(1 1.5 2 3 4)

echo "Starting independent hyperparameter sweeps..."
echo "Errors will be appended to $ERR_FILE"

# ==========================================
# SWEEP 1: Testing max_plan_tokens
# ==========================================
echo "------------------------------------------------------"
echo "Starting Sweep 1: max_plan_tokens (prune_ratio defaults to 1)"
for mpt in "${MAX_PLAN_TOKENS[@]}"; do
    echo "Running: max_plan_tokens=${mpt}"
    
    uv run main.py \
        --max_plan_tokens "$mpt" \
        2>> "$ERR_FILE" \
    | uv run plot_results.py \
        --completion /dev/stdin
done

# ==========================================
# SWEEP 2: Testing prune_ratio
# ==========================================
echo "------------------------------------------------------"
echo "Starting Sweep 2: prune_ratio (max_plan_tokens defaults to 500)"
for pr in "${PRUNE_RATIOS[@]}"; do
    echo "Running: prune_ratio=${pr}"
    
    uv run main.py \
        --prune_ratio "$pr" \
        2>> "$ERR_FILE" \
    | uv run plot_results.py \
        --completion /dev/stdin
done

echo "------------------------------------------------------"
echo "Both sweeps complete!"