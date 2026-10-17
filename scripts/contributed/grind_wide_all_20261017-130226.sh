#!/usr/bin/env bash
# The wide cut (100,000 uncarried endings) on every installed capture.
#
#   contrib/grind_wide_all.sh
#
# Only ever run on MODWAR7 so far, where the same cores went 36 names on the committed 4,800
# endings and 211 on this list. The exclusion set and the uncarried-ending list have both been
# recomputed since, so this is not a re-sweep of a closed question.
set -u
cd "$(dirname "$0")/.."
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
  bin/windows/confirm_plan.exe "$plan" > "$log" 2>&1
  grep -E "^total:|this run added|found nothing|refus" "$log" | tail -2
done
echo "=== wide-all finished, run submit ==="
