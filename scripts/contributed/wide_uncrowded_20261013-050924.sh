#!/usr/bin/env bash
# The wide (100,000 uncarried endings) cut, where it has never been run.
#
#   contrib/wide_uncrowded.sh
#
# Justified by a measurement, not a schedule: on MODWAR7 the same cores with the committed 4,800
# endings returned 36 names and with the 100,000 uncarried ones returned 211, six times the yield
# for the same stems. The two legacy titles have only ever had the narrow cut here.
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

for game in BLKOPSCW BLKOPS04; do
  bin/windows/next_game.exe --game "$game" > /dev/null
  plan=plans/grind/${game,,}_wide.txt
  {
    echo "label: grown confirmed-only cores x the 100k uncarried endings, $game"
    echo "describe: 405,943 all-boundary cores from names only this project has confirmed, crossed with the 100,000 endings data/suffixes.txt caps away"
    echo "stem: @contrib/ab_cores.txt"
    echo "end: @contrib/ab_ends.txt"
    echo "bare: yes"
  } > "$plan"

  echo "=== $game wide general"
  log=logs/wide_${game,,}.log
  bin/windows/confirm_plan.exe "$plan" --game "$game" > "$log" 2>&1
  bin/windows/submit.exe
  grep -E "^total:|this run added|found nothing" "$log" | tail -2 || true
done

echo "=== MODWAR7 closure over the 211 fresh names"
python scripts/derive_closure.py --game MODWAR7 > logs/closure_modwar7.log 2>&1
bin/windows/submit.exe
grep -E "round [0-9]+ added|names added in total" logs/closure_modwar7.log | tail -3 || true
echo "=== done, submissions sent ==="
