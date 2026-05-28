#!/bin/bash

export VLLM_LOGGING_LEVEL=ERROR

MAX_PLAN_TOKENS=(1000 2500 4000 6500 9000)
PRUNE_RATIOS=(1.5 2 3 4)

TEMP_FILE=$(mktemp)

echo "======================================================"
echo " PHASE 1: Running Baseline Generation"
echo "======================================================"

# Run baseline and save output to temp file
uv run main.py --num_gpus 4 --baseline > "$TEMP_FILE"

# Extract the nicely formatted JSON filename using awk for cross-platform safety
BASELINE_JSON=$(grep "Saving format fixed JSON to:" "$TEMP_FILE" | awk -F': ' '{print $2}')

# Verify cache creation
if [[ ! -f "baseline_cache.json" ]]; then
    echo "Error: Baseline cache (baseline_cache.json) failed to generate."
    cat "$TEMP_FILE"
    exit 1
fi

echo "Baseline Formatted JSON: $BASELINE_JSON"
echo "Baseline Cache ready at: baseline_cache.json"

echo ""
echo "======================================================"
echo " PHASE 2: Starting Nested Sweep (Tokens & Prune Ratio)"
echo "======================================================"

for mpt in "${MAX_PLAN_TOKENS[@]}"; do
    for pr in "${PRUNE_RATIOS[@]}"; do
        echo "------------------------------------------------------"
        echo "Running: max_plan_tokens=${mpt} | prune_ratio=${pr}"
        
        # Pass the cache file, mpt, and pr to the script
        uv run main.py --num_gpus 4 --cache_fn "baseline_cache.json" --max_plan_tokens "$mpt" --prune_ratio "$pr" > "$TEMP_FILE"
        
        # Extract the saved JSON filename
        CLEAN_FILENAME=$(grep "Saving format fixed JSON to:" "$TEMP_FILE" | awk -F': ' '{print $2}')
        
        if [[ -n "$CLEAN_FILENAME" ]]; then
            echo "Saved Strategy Files to: $CLEAN_FILENAME"
        else
            echo "Warning: No .json filename found in output for max_plan_tokens=${mpt}, prune_ratio=${pr}"
        fi
    done
done

# Clean up
rm -f "$TEMP_FILE"

echo "======================================================"
echo " Experiment Sweep Complete!"
echo "======================================================"