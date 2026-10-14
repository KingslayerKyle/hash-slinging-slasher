#!/usr/bin/env bash
# The wide cut (100,000 uncarried endings) on every installed capture.
#
#   contrib/grind_wide_all.sh
#
# Only ever run on MODWAR7 so far, where the same cores went 36 names on the committed 4,800
# endings and 211 on this list. The exclusion set and the uncarried-ending list have both been
# recomputed since, so this is not a re-sweep of a closed question.
set -euo pipefail
root="$(cd "$(dirname "$0")" && pwd)"
while [ ! -f "$root/scripts/snapshot.py" ]; do
  parent="$(dirname "$root")"
  [ "$parent" != "$root" ] || { echo "Repository root not found" >&2; exit 1; }
  root="$parent"
done
cd "$root"
for tool in next_game confirm_plan submit; do
  [ -f "bin/windows/$tool.exe" ] || { echo "Missing bin/windows/$tool.exe" >&2; exit 1; }
done
for seed in ab_cores.txt ab_ends.txt; do
  [ -s "contrib/$seed" ] || { echo "Prepare the measured contrib/$seed input first" >&2; exit 1; }
done
mkdir -p logs plans/grind

for game in BLKOPS04 BLKOPSCW MODWAR22 YAMYAMOK BLACKOP6 BLACKOP7 MODWAR7; do
  bin/windows/next_game.exe --game "$game" > /dev/null
  plan=plans/grind/${game,,}_wide.txt
  {
    echo "label: confirmed-only cores x the 100k uncarried endings, $game"
    echo "describe: 406,113 all-boundary cores from names only this project has confirmed, crossed with the 100,000 endings the committed list caps away"
    echo "stem: @contrib/ab_cores.txt"
    echo "end: @contrib/ab_ends.txt"
    echo "bare: yes"
  } > "$plan"

  echo "=== $game wide"
  log=logs/wideall_${game,,}.log
  bin/windows/confirm_plan.exe "$plan" --game "$game" > "$log" 2>&1
  bin/windows/submit.exe
  grep -E "^total:|this run added|found nothing|refus" "$log" | tail -2 || true
done
echo "=== wide-all finished, submissions sent ==="
