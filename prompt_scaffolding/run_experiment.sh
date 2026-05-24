#!/bin/bash

export VLLM_LOGGING_LEVEL=ERROR

MAX_PLAN_TOKENS=(1000 2500 4000 6500 9000)
PRUNE_RATIOS=(1.5 2 3 4)

# Create a temporary file to hold the output
TEMP_FILE=$(mktemp)

# ==========================================
# NESTED SWEEP: Testing all combinations
# ==========================================
echo "------------------------------------------------------"
echo "Starting Nested Sweep: max_plan_tokens and prune_ratio"

for mpt in "${MAX_PLAN_TOKENS[@]}"; do
    for pr in "${PRUNE_RATIOS[@]}"; do
        echo "------------------------------------------------------"
        echo "Running: max_plan_tokens=${mpt} | prune_ratio=${pr}"
        
        # Pass both arguments to main.py
        uv run main.py --max_plan_tokens "$mpt" --prune_ratio "$pr" > "$TEMP_FILE"
        
        # Extract the JSON filename
        CLEAN_FILENAME=$(grep -m 1 '\.json' "$TEMP_FILE")
        
        # # Run the plotting script if a filename was found
        # if [[ -n "$CLEAN_FILENAME" ]]; then
        #     uv run plot_results.py --completion_fn "$CLEAN_FILENAME"
        # else
        #     echo "Warning: No .json filename found in output for max_plan_tokens=${mpt}, prune_ratio=${pr}"
        # fi
    done
done

# Clean up the temporary file
rm -f "$TEMP_FILE"

echo "------------------------------------------------------"
echo "Nested sweep complete!"