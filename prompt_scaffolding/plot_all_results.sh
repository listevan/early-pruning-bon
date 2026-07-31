#!/bin/bash

# Plot one sweep's results.
#
# USAGE:  ./plot_all_results.sh [RUN_DIR]        (RUN_DIR default: current directory)
#         VARIANT=regen ./plot_all_results.sh runs/2026-07-28_bon_regen_n100
#
# RUN-DIRECTORY LAYOUT
# --------------------
# A sweep whose best_of_ns were split across array tasks (job_sweep_n100.slurm runs the
# bon groups {16} {8} {4,2,1} on separate GPUs) lands as PARTIAL result JSONs, each keyed
# by only the bons it evaluated. Those pieces live in RUN_DIR/partials/ and are recombined
# here into one merged_*.json per (arm, plan, prune) before anything is plotted:
#
#     runs/<run>/
#       partials/                     <- bon-split pieces, one per (arm, plan, bon-group)
#       merged_<arm>_bon_1_2_4_8_16_..._regen.json   <- built from partials/ (this script)
#       *_baseline_..._strat_None_....json           <- shared baseline
#       *.png                                        <- written here
#
# A sweep that was NOT split (one task per config, e.g. job_sweep_n100_pruneonly.slurm)
# has no partials/ and its result JSONs already span the full 1_2_4_8_16 range. Both
# layouts are handled: the completion glob below matches merged_ and unsplit files alike,
# and a file is skipped only when a merged_ counterpart for the same
# (arm, plan, prune, variant) supersedes it.
#
# Which sweep to plot. prune-only, best-of-N regen (_regen), and best-of-k diverse
# (_diverse) are separate experiments, so by default only one is plotted per invocation
# rather than all being swept into one undifferentiated batch of PNGs.
#   VARIANT=plain    (default) prune-only runs (no suffix)
#   VARIANT=regen              best-of-N regen runs
#   VARIANT=diverse            best-of-k diverse runs
#   VARIANT=all                every completion file (one plot each)
#   VARIANT=compare            OVERLAY bon (_regen) and bok (_diverse) on one plot per
#                              matching (arm, plan, prune)
#   VARIANT=headline           ONE axes per (plan, prune): all 3 pruning arms as curves,
#                              bon solid / bok dashed, + baseline (via plot_headline.py)
#   VARIANT=combined           the original 6-subplot grid per (plan, prune), subplots 0-3
#                              overlay baseline + 3 bon + 3 bok (via plot_combined.py)
VARIANT=${VARIANT:-regen}

# Run from the project dir (uv needs it) but read/write results in RUN_DIR, so the
# plot_*.py helpers stay importable no matter where the run directory sits.
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
DIR=${1:-${DIR:-.}}
DIR=$(cd -- "$DIR" && pwd) || { echo "Error: run dir '${1:-${DIR}}' not found"; exit 1; }
cd "$SCRIPT_DIR" || exit 1

shopt -s nullglob # Ensures the loops don't run if no files are found

# 0. Recombine bon-split partials, if this run has any. Cheap key-union, and rerunning it
#    just overwrites the merged files, so it is safe to do on every invocation.
if [[ -d "$DIR/partials" ]]; then
    echo "================================================================"
    echo "Merging bon-split partials: $DIR/partials -> $DIR"
    echo "================================================================"
    uv run merge_bon_splits.py "$DIR/partials" -o "$DIR" || exit 1
fi

# 1. Find the file matching the None strategy pattern
#    main.py emits "_strat_None_" / "_strat_CompletionStrategy_" (see main.py fname)
#    The baseline has no regen variant, so it is shared by both sweeps.
#
#    REFUSE to guess when a directory holds more than one. This used to `head -n 1`, which
#    silently picked the alphabetically-first baseline: run flat against the project root,
#    that chose the 2026-05-28 baseline (built from a max_bon=16 cache, so different chunk
#    counts and no N=32) over the 2026-07-25 one the sweep actually shares a cache with,
#    and every curve was drawn against the wrong reference. One baseline per run directory.
NONE_FILES=("$DIR"/*strat_None*.json)
if [ ${#NONE_FILES[@]} -eq 0 ]; then
    echo "Error: No 'None' strategy file found matching $DIR/*strat_None*.json"
    exit 1
fi
if [ ${#NONE_FILES[@]} -gt 1 ]; then
    echo "Error: ${#NONE_FILES[@]} baselines in $DIR -- refusing to guess which one this sweep used:"
    printf '  %s\n' "${NONE_FILES[@]##*/}"
    echo "Keep exactly one baseline per run directory (see the layout note at the top)."
    exit 1
fi
NONE_FILE=${NONE_FILES[0]}

echo "================================================================"
echo "Run directory:                  $DIR"
echo "Found Baseline (None Strategy): $(basename "$NONE_FILE")"
echo "================================================================"

# True when a merged_ file already covers this file's (arm, plan, prune, variant), i.e.
# the file is a leftover partial sitting next to its own merge. Keeps a run from being
# plotted twice when partials and merged output share one directory.
superseded_by_merge() {
    local f=$1 base arm pp var
    base=$(basename "$f")
    [[ "$base" == merged_* ]] && return 1
    arm=$(sed -E 's/.*_([a-z]+)_bon_.*/\1/' <<<"$base")
    pp=$(grep -oE '_plan_[0-9]+_prune_[0-9.]+' <<<"$base")
    var=""
    [[ "$base" == *_regen.json ]] && var="_regen"
    [[ "$base" == *_diverse.json ]] && var="_diverse"
    compgen -G "$DIR/merged_${arm}_bon_*${pp}${var}.json" >/dev/null
}

# compare mode: overlay the regen (bon) and diverse (bok) curves for each matching
# (arm, plan, prune) on a single set of axes, alongside the baseline.
if [[ "$VARIANT" == "compare" ]]; then
    for REGEN_FILE in "$DIR"/*_regen.json; do
        superseded_by_merge "$REGEN_FILE" && continue
        arm=$(basename "$REGEN_FILE" | sed -E 's/.*_([a-z]+)_bon_.*/\1/')
        pp=$(basename "$REGEN_FILE" | grep -oE '_plan_[0-9]+_prune_[0-9.]+')
        DIVERSE_FILE=$(ls "$DIR"/*_"${arm}"_bon_*"${pp}"_diverse.json 2>/dev/null | head -n 1)
        if [[ -z "$DIVERSE_FILE" ]]; then
            echo "No diverse counterpart for $(basename "$REGEN_FILE") (arm=$arm$pp) -- skipping"
            continue
        fi
        echo "Overlaying arm=$arm$pp:"
        echo "  bon -> $(basename "$REGEN_FILE")"
        echo "  bok -> $(basename "$DIVERSE_FILE")"
        uv run plot_results.py --none_fn "$NONE_FILE" \
            --completion_fn "$REGEN_FILE" --completion_fn2 "$DIVERSE_FILE"
        echo "----------------------------------------------------------------"
    done
    echo "All plotting tasks completed."
    exit 0
fi

# headline mode: one axes per unique (plan, prune) with all pruning arms overlaid,
# bon solid / bok dashed. Delegates to plot_headline.py, which finds the arm files.
if [[ "$VARIANT" == "headline" ]]; then
    seen=" "
    for f in "$DIR"/*_regen.json; do
        superseded_by_merge "$f" && continue
        plan=$(basename "$f" | sed -E 's/.*_plan_([0-9]+)_prune_.*/\1/')
        prune=$(basename "$f" | sed -E 's/.*_prune_([0-9.]+)_regen\.json/\1/')
        key="${plan}|${prune}"
        [[ "$seen" == *" $key "* ]] && continue    # one figure per (plan,prune)
        seen="$seen$key "
        echo "Headline: plan=$plan prune=$prune"
        uv run plot_headline.py --dir "$DIR" --none_fn "$NONE_FILE" --plan "$plan" --prune "$prune"
        echo "----------------------------------------------------------------"
    done
    echo "All plotting tasks completed."
    exit 0
fi

# combined mode: original 6-subplot grid per (plan, prune), bon + bok overlaid.
if [[ "$VARIANT" == "combined" ]]; then
    seen=" "
    for f in "$DIR"/*_regen.json; do
        superseded_by_merge "$f" && continue
        plan=$(basename "$f" | sed -E 's/.*_plan_([0-9]+)_prune_.*/\1/')
        prune=$(basename "$f" | sed -E 's/.*_prune_([0-9.]+)_regen\.json/\1/')
        key="${plan}|${prune}"
        [[ "$seen" == *" $key "* ]] && continue
        seen="$seen$key "
        echo "Combined grid: plan=$plan prune=$prune"
        uv run plot_combined.py --dir "$DIR" --none_fn "$NONE_FILE" --plan "$plan" --prune "$prune"
        echo "----------------------------------------------------------------"
    done
    echo "All plotting tasks completed."
    exit 0
fi

# 2. Loop through all files matching the Completion strategy pattern. Matches merged_ and
#    unsplit files alike; superseded_by_merge() drops any partial whose merge is present.
for COMP_FILE in "$DIR"/*strat_CompletionStrategy*.json; do
    # Keep the sweeps apart: select only files of the requested variant.
    case "$VARIANT" in
        regen)   [[ "$COMP_FILE" == *_regen.json ]]   || continue ;;
        diverse) [[ "$COMP_FILE" == *_diverse.json ]] || continue ;;
        all)     ;;
        *)       # plain: exclude both regen and diverse
                 [[ "$COMP_FILE" == *_regen.json || "$COMP_FILE" == *_diverse.json ]] && continue ;;
    esac

    superseded_by_merge "$COMP_FILE" && continue

    echo "Running plot generation for:"
    echo " -> $(basename "$COMP_FILE")"

    # 3. Execute the plotting program using uv run
    uv run plot_results.py --none_fn "$NONE_FILE" --completion_fn "$COMP_FILE"

    echo "----------------------------------------------------------------"
done

echo "All plotting tasks completed."
