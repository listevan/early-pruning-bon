#!/bin/bash

export VLLM_LOGGING_LEVEL=ERROR

MAX_PLAN_TOKENS=(1000 2500 4000 6500 9000)
PRUNE_RATIOS=(1 1.5 2 3 4)

# Create a temporary file to hold the output
TEMP_FILE=$(mktemp)

# ==========================================
# SWEEP 1: Testing max_plan_tokens
# ==========================================
echo "------------------------------------------------------"
echo "Starting Sweep 1: max_plan_tokens (prune_ratio defaults to 1)"
for mpt in "${MAX_PLAN_TOKENS[@]}"; do
    echo "Running: max_plan_tokens=${mpt}"
    uv run main.py --max_plan_tokens "$mpt" > "$TEMP_FILE"
    
    CLEAN_FILENAME=$(grep -m 1 '\.json' "$TEMP_FILE")
    uv run plot_results.py --completion_fn "$CLEAN_FILENAME"
done

# ==========================================
# SWEEP 2: Testing prune_ratio
# ==========================================
echo "------------------------------------------------------"
echo "Starting Sweep 2: prune_ratio (max_plan_tokens defaults to 500)"
for pr in "${PRUNE_RATIOS[@]}"; do
    echo "Running: prune_ratio=${pr}"
    uv run main.py --prune_ratio "$pr" > "$TEMP_FILE"
    
    CLEAN_FILENAME=$(grep -m 1 '\.json' "$TEMP_FILE")
    uv run plot_results.py --completion_fn "$CLEAN_FILENAME"
done

# Clean up the temporary file
rm -f "$TEMP_FILE"

echo "------------------------------------------------------"
echo "Both sweeps complete!"