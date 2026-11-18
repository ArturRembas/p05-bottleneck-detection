#!/usr/bin/env bash
set -euo pipefail
arg="${1:-}"
case "$arg" in
  EXP-01|EXP-02|EXP-03|EXP-04|EXP-05|EXP-06|EXP-07|EXP-08|EXP-09|EXP-10) ;;
  verify) exec python /opt/p05/check-research-manifest.py /research-source ;;
  *) echo "Usage: research EXP-01..EXP-10 | verify" >&2; exit 2 ;;
esac
if [ ! -f /research-source/results/audit/baseline_v0.1.json ]; then
  echo "Research baseline not found. Set P05_RESEARCH_SOURCE to PR #8 worktree directory." >&2
  exit 2
fi
num="${arg#EXP-}"
case "$num" in
  01) script=exp01_dfg.py;;
  02) script=exp02_performance_dfg.py;;
  03) script=exp03_variants_rework.py;;
  04) script=exp04_parallelism.py;;
  05) script=exp05_capacity_waiting.py;;
  06) script=exp06_bottleneck_candidates.py;;
  07) script=exp07_generalization.py;;
  08) script=exp08_transient_vs_persistent.py;;
  09) script=exp09_queue_patterns.py;;
  10) script=exp10_log_capabilities.py;;
esac
run_id="$(date -u +%Y%m%dT%H%M%SZ)-${arg}-$$"
scratch="$(mktemp -d /tmp/p05-research.XXXXXX)"
trap 'rm -rf "$scratch"' EXIT
cp -a /research-source/. "$scratch/"
# Keep the archived results only in the read-only source, not in the new run output.
rm -rf "$scratch/results"
mkdir -p "$scratch/results" "/runs/$run_id"
# Research scripts use paths relative to __file__; running from scratch preserves their expectations.
set +e
(cd "$scratch" && python "scripts/$script") > "/runs/$run_id/console.log" 2>&1
status=$?
set -e
cp -a "$scratch/results/." "/runs/$run_id/" || true
python -V > "/runs/$run_id/environment.txt" 2>&1
python -c 'import pm4py,pandas;print("pm4py",pm4py.__version__);print("pandas",pandas.__version__)' >> "/runs/$run_id/environment.txt"
printf '%s\n' "$arg" > "/runs/$run_id/experiment.txt"
printf 'exit_status=%s\n' "$status" > "/runs/$run_id/status.txt"
cat "/runs/$run_id/console.log"
echo "Output: /runs/$run_id (exit=$status)"
exit "$status"
