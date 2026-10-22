#!/usr/bin/env bash
# The games nobody else is fighting for tonight, with cores regenerated an hour later.
#
#   contrib/grind_uncrowded.sh
#
# Chosen from a measured duplication rate, not a ranking: the last submit dropped 16,200 of
# 16,360 MWIII names, 9,615 of 9,661 BO6 and 14,802 of 14,854 BO7 as already claimed, but only
# 244 of 874 for MW7. Ground that is contested returns other people's names however fresh the
# stems are, so MW7 and the two legacy titles run here and the contested three do not.
set -euo pipefail
repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
while [ ! -f "$repo_root/scripts/snapshot.py" ]; do
  parent=$(dirname -- "$repo_root")
  if [ "$parent" = "$repo_root" ]; then
    echo "Cannot locate the solver checkout" >&2
    exit 2
  fi
  repo_root=$parent
done
cd -- "$repo_root"
mkdir -p logs plans/grind

for game in MODWAR7 BLKOPS04 BLKOPSCW; do
  bin/windows/next_game.exe --game "$game" > /dev/null
  if [ "$game" = BLKOPS04 ] || [ "$game" = BLKOPSCW ]; then
    ends=data/suffixes.txt
  else
    ends=data/modern/${game,,}/suffixes.txt
  fi

  plan=plans/grind/${game,,}_grown.txt
  {
    echo "label: grown confirmed-only cores against $game, own endings"
    echo "describe: 405,943 all-boundary cores from names only this project has confirmed, crossed with $ends"
    echo "stem: @contrib/ab_cores.txt"
    echo "end: @$ends"
    echo "bare: yes"
  } > "$plan"

  echo "=== $game general  stems=$(wc -l < contrib/ab_cores.txt) endings=$(wc -l < "$ends")"
  log=logs/grown_${game,,}.log
  bin/windows/confirm_plan.exe "$plan" > "$log" 2>&1
  grep -E "^total:|this run added|found nothing" "$log" | tail -2

  printf "label: grown confirmed-only sound cores against $game\ndescribe: all-boundary sound cores crossed with the game's own sound endings\nstem: @contrib/ab_sound_cores.txt\nend: @%s\nbare: yes\n" \
    "$([ "$game" = BLKOPS04 ] || [ "$game" = BLKOPSCW ] && echo data/sound.suffixes.txt || echo data/modern/${game,,}/sound.suffixes.txt)" \
    > "plans/grind/${game,,}_grown_sound.txt"
  echo "=== $game sound"
  log=logs/grown_${game,,}_sound.log
  bin/windows/confirm_plan.exe "plans/grind/${game,,}_grown_sound.txt" >> "$log" 2>&1
  grep -E "^total:|this run added|found nothing" "$log" | tail -2
done
echo "=== uncrowded grind finished, run submit ==="
