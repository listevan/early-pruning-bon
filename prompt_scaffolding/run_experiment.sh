#!/bin/bash
set -u

export VLLM_LOGGING_LEVEL=ERROR

# Override either grid from the environment to smoke-test a single config, e.g.
#   MAX_PLAN_TOKENS="1000" PRUNE_RATIOS="1.5" NUM_GPUS=1 SKIP_BASELINE=1 ./run_experiment.sh
# 6500 and 9000 are dropped: at bon=16 their rank() prompts are 100k / 133k tokens, well past
# max_model_len=65536 (model.py). The ceiling at bon=16 is ~4071 tokens per plan.
read -ra MAX_PLAN_TOKENS <<< "${MAX_PLAN_TOKENS:-1000 2500 4000}"
read -ra PRUNE_RATIOS    <<< "${PRUNE_RATIOS:-1.5 2 3 4}"

# Data parallelism, not tensor parallelism: each GPU hosts its own single-GPU vLLM
# instance (TP=1, no cross-GPU all-reduce) and works through its own slice of the
# sweep. Qwen3-4B is ~8GB in bf16 and fits on one A40 (48GB) with room for KV cache.
NUM_GPUS=${NUM_GPUS:-${SLURM_GPUS_ON_NODE:-4}}

# The baseline is one monolithic generation over all prompts, so it cannot be split
# across configs the way the sweep can. It keeps whatever GPU count you give it
# (TP applies here, and only here). It is skipped entirely when a cache already exists.
BASELINE_GPUS=${BASELINE_GPUS:-$NUM_GPUS}

LOG_DIR=${LOG_DIR:-sweep_logs}
mkdir -p "$LOG_DIR"

# Each worker is an independent TP=1 process, so every one of them thinks it is rank_0 and
# hashes to the SAME torch_compile_cache key. Sharing a cache root means N processes write
# the same artifact files at once -> torn bytes -> "checksum does not match" on the next
# load. (Under TP=4 this never happened: one process, one rank_N_0 dir per rank.)
# Key the cache root by array task as well as GPU: two array tasks can land on one node.
CACHE_ROOT=${CACHE_ROOT:-$PWD/.vllm_cache/${SLURM_ARRAY_TASK_ID:-main}}

# Resolve the venv once up front so the concurrent workers below don't race on `uv sync`.
# This project runs out of a bare .venv with no pyproject.toml, so `uv sync` has nothing
# to do (and errors); only call it if a project file actually exists.
if [[ -z "${UV:-}" ]]; then
    [[ -f pyproject.toml ]] && uv sync --quiet
    UV="uv run --no-sync"
fi

echo "======================================================"
echo " PHASE 1: Baseline Generation"
echo "======================================================"

# The baseline cache is independent of --max_plan_tokens: baseline generation runs at
# max_tokens=16384 and plan truncation happens later, inside the strategy. So an existing
# cache can be reused across sweeps. SKIP_BASELINE=1 reuses it.
if [[ "${SKIP_BASELINE:-0}" == "1" && -f "baseline_cache.json" ]]; then
    echo "SKIP_BASELINE=1: reusing existing baseline_cache.json"
else
    $UV main.py --num_gpus "$BASELINE_GPUS" --baseline > "$LOG_DIR/baseline.log" 2>&1

    if [[ ! -f "baseline_cache.json" ]]; then
        echo "Error: Baseline cache (baseline_cache.json) failed to generate."
        cat "$LOG_DIR/baseline.log"
        exit 1
    fi

    BASELINE_JSON=$(grep "Saving format fixed JSON to:" "$LOG_DIR/baseline.log" | awk -F': ' '{print $2}')
    echo "Baseline Formatted JSON: $BASELINE_JSON"
fi

echo "Baseline Cache ready at: baseline_cache.json"

echo ""
echo "======================================================"
echo " PHASE 2: Sweep (${NUM_GPUS} GPUs in parallel, TP=1 each)"
echo "======================================================"

# Flatten the sweep into a single work list.
CONFIGS=()
for mpt in "${MAX_PLAN_TOKENS[@]}"; do
    for pr in "${PRUNE_RATIOS[@]}"; do
        CONFIGS+=("$mpt $pr")
    done
done
# Array mode: this task runs exactly ONE config, on one GPU. A single config takes ~17-21h,
# so 12 of them queued 3-deep on 4 GPUs would blow past the 48h cap; one per task fits.
if [[ -n "${CONFIG_INDEX:-}" ]]; then
    if (( CONFIG_INDEX < 0 || CONFIG_INDEX >= ${#CONFIGS[@]} )); then
        echo "Error: CONFIG_INDEX=$CONFIG_INDEX out of range (0..$(( ${#CONFIGS[@]} - 1 )))"
        exit 1
    fi
    if [[ ! -f "baseline_cache.json" ]]; then
        echo "Error: array mode needs an existing baseline_cache.json (tasks must not each regenerate it)."
        exit 1
    fi
    echo "Array task: config $CONFIG_INDEX of ${#CONFIGS[@]} -> ${CONFIGS[$CONFIG_INDEX]}"
    CONFIGS=("${CONFIGS[$CONFIG_INDEX]}")
    NUM_GPUS=1
fi

echo "${#CONFIGS[@]} config(s) across $NUM_GPUS GPU(s); logs in $LOG_DIR/"
echo ""

# Worker g takes configs g, g+NUM_GPUS, g+2*NUM_GPUS, ... and runs them back to back,
# pinned to GPU g. Output filenames embed mpt/prune, so concurrent workers never collide.
run_gpu_worker() {
    local gpu=$1
    local i mpt pr log
    mkdir -p "$CACHE_ROOT/gpu${gpu}"
    for (( i=gpu; i<${#CONFIGS[@]}; i+=NUM_GPUS )); do
        read -r mpt pr <<< "${CONFIGS[$i]}"
        log="$LOG_DIR/mpt${mpt}_prune${pr}.log"
        echo "[gpu $gpu] START max_plan_tokens=$mpt prune_ratio=$pr"

        if CUDA_VISIBLE_DEVICES="$gpu" \
           VLLM_CACHE_ROOT="$CACHE_ROOT/gpu${gpu}" \
           $UV main.py \
                --num_gpus 1 \
                --cache_fn "baseline_cache.json" \
                --max_plan_tokens "$mpt" \
                --prune_ratio "$pr" > "$log" 2>&1; then
            grep "Saving format fixed JSON to:" "$log" | awk -F': ' -v g="$gpu" '{print "[gpu " g "] SAVED " $2}'
            echo "[gpu $gpu] DONE  max_plan_tokens=$mpt prune_ratio=$pr"
        else
            echo "[gpu $gpu] FAIL  max_plan_tokens=$mpt prune_ratio=$pr -- see $log"
        fi
    done
}

for (( g=0; g<NUM_GPUS; g++ )); do
    run_gpu_worker "$g" &
done
wait

echo ""
echo "======================================================"
echo " Experiment Sweep Complete"
echo "======================================================"
echo "Result files written: $(ls -1 *strat_CompletionStrategy*.json 2>/dev/null | wc -l)"
FAILED=$(grep -l "Traceback\|Error" "$LOG_DIR"/mpt*.log 2>/dev/null | wc -l)
[[ "$FAILED" -gt 0 ]] && echo "WARNING: $FAILED config log(s) contain errors -- check $LOG_DIR/"
exit 0
