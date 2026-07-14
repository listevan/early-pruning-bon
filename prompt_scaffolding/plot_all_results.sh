#!/bin/bash

# 1. Find the first file matching the None strategy pattern
#    main.py emits "_strat_None_" / "_strat_CompletionStrategy_" (see main.py fname)
NONE_FILE=$(ls *strat_None*.json 2>/dev/null | head -n 1)

# Exit if no 'None' strategy file is found
if [ -z "$NONE_FILE" ]; then
    echo "Error: No 'None' strategy file found matching *strat_None*.json"
    exit 1
fi

echo "================================================================"
echo "Found Baseline (None Strategy): $NONE_FILE"
echo "================================================================"

# 2. Loop through all files matching the Completion strategy pattern
shopt -s nullglob # Ensures the loop doesn't run if no files are found
for COMP_FILE in *strat_CompletionStrategy*.json; do
    echo "Running plot generation for:"
    echo " -> $COMP_FILE"
    
    # 3. Execute the plotting program using uv run
    uv run plot_results.py --none_fn "$NONE_FILE" --completion_fn "$COMP_FILE"
    
    echo "----------------------------------------------------------------"
done

echo "All plotting tasks completed."