#!/usr/bin/env bash
# Unattended refill watcher -- NOT a rotation. It runs nothing while upstream is quiet.
#
# The modern seams this clone invented (tail retarget, dialogue chain, alias->file placement) and the
# BO4/CW derivation closure are closed on the corpus as it stands; what has measurably reopened them
# is other contributors' merged names (new seeds). So: every PERIOD seconds, if origin/main has new
# commits, run `start` (nothing else is running -- sequential by construction), refresh the seed
# corpus and named sets, re-run those seeded methods once with an explicit --game each, and submit
# through contrib/safe_submit.sh. Prints one line per cycle (for a monitor) and stops at DEADLINE.
#
#   PYTHON=... bash contrib/refill_watch.sh <hours> [period_seconds]
set -u
cd "$(dirname "$0")/.."
P=${PYTHON:-python}
HOURS=${1:-9}; PERIOD=${2:-2700}
DEADLINE=$(( $(date +%s) + HOURS * 3600 ))
MODERN="BLACKOP7 BLACKOP6 YAMYAMOK MODWAR22 MODWAR7"
added() { grep -ohE 'this run added [0-9]+' "$@" 2>/dev/null | awk '{s+=$4} END{print s+0}'; }
last=$(git rev-parse origin/main 2>/dev/null)
cycle=0
echo "WATCH start $(date +%H:%M) deadline $(date -d @$DEADLINE +%H:%M) at $last"
while [ "$(date +%s)" -lt "$DEADLINE" ]; do
  cycle=$((cycle + 1))
  git fetch -q origin main 2>/dev/null
  now=$(git rev-parse origin/main 2>/dev/null)
  if [ "$now" = "$last" ]; then
    echo "CYCLE $cycle $(date +%H:%M) upstream quiet -- nothing run"
  else
    n=$(git rev-list --count "$last..$now" 2>/dev/null)
    L=logs/watch_$cycle; mkdir -p "$L"
    ./bin/windows/start.exe > "$L/start.log" 2>&1 || { echo "CYCLE $cycle $(date +%H:%M) START BLOCKED -- see $L/start.log"; last=$now; sleep "$PERIOD"; continue; }
    $P scripts/contributed/every_game_transfer_20261008-233429.py > contrib/out/every_name.txt 2>/dev/null
    [ -f contrib/out/external_names.txt ] && cat contrib/out/external_names.txt >> contrib/out/every_name.txt
    PYTHONPATH=scripts $P scripts/contributed/_dump_named_20261011-064534.py $MODERN 2>/dev/null
    for g in $MODERN; do
      ./bin/windows/confirm_list.exe contrib/out/every_name.txt --game $g --anyway --label "cross-game transfer, watcher refill" \
        --script scripts/contributed/every_game_transfer_20261008-233429.py > "$L/egt_$g.log" 2>&1
      $P contrib/sound_tail_retarget_lang.py $g 2>/dev/null
      ./bin/windows/confirm_plan.exe plans/stt2_$g.txt --game $g --anyway > "$L/stt_$g.log" 2>&1
      $P contrib/alias_to_file_placed.py $g 2>/dev/null
      ./bin/windows/confirm_plan.exe plans/atf_$g.txt --game $g --anyway > "$L/atf_$g.log" 2>&1
    done
    PYTHON=$P bash contrib/dx_closure.sh --anyway > "$L/dx.log" 2>&1; cp logs/dxc_*.log "$L/" 2>/dev/null
    for g in BLKOPSCW BLKOPS04; do $P contrib/derive_closure_fixed.py --game $g > "$L/closure_$g.log" 2>&1; done
    found=$(( $(added "$L"/*.log) ))
    closure=$(grep -ohE '[0-9]+ names added in total' "$L"/closure_*.log | awk '{s+=$1} END{print s+0}')
    PYTHON=$P bash contrib/safe_submit.sh > "$L/submit.log" 2>&1
    sent=$(grep -oE '^[0-9]+ names to send' "$L/submit.log" | awk '{s+=$1} END{print s+0}')
    bad=$(grep -cE 'REFUSING|ALREADY NAMED|WRONG-GAME|BAD stored|NOT in capture|CLAIMED' "$L/submit.log")
    echo "CYCLE $cycle $(date +%H:%M) upstream +$n commits: modern +$found, closure +$closure, sent $sent, check-flags $bad ($L)"
    last=$now
  fi
  sleep "$PERIOD"
done
echo "WATCH done $(date +%H:%M)"
