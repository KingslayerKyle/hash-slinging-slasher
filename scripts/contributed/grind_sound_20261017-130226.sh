#!/usr/bin/env bash
# The sound half of the corpus, per game: confirmed-only all-boundary SOUND cores worn by each
# game's own measured sound endings.
#
#   contrib/grind_sound.sh
#
# Separate from grind_all_games.sh because sound names share no vocabulary with the rest -- an
# alias ending tried against an xmodel id can only coincide, never match -- so this gets its own
# core list (535,239 cut at every boundary AND every path separator) and its own ending list.
set -u
cd "$(dirname "$0")/.."

GAMES=(BLKOPS04 BLKOPSCW MODWAR22 YAMYAMOK BLACKOP6 BLACKOP7 MODWAR7)
mkdir -p logs plans/grind

for game in "${GAMES[@]}"; do
  bin/windows/next_game.exe --game "$game" > /dev/null

  if [ "$game" = BLKOPS04 ] || [ "$game" = BLKOPSCW ]; then
    ends=data/sound.suffixes.txt
  else
    ends=data/modern/${game,,}/sound.suffixes.txt
  fi
  if [ ! -f "$ends" ]; then
    echo "=== $game: no sound ending list at $ends, skipping"
    continue
  fi

  plan=plans/grind/${game,,}_sound.txt
  {
    echo "label: fresh confirmed-only sound cores against $game, own sound endings"
    echo "describe: sound cores cut at every boundary and separator from names only this project has confirmed, wearing $ends"
    echo "stem: @contrib/ab_sound_cores.txt"
    echo "end: @$ends"
    echo "bare: yes"
  } > "$plan"

  echo "=== $game  stems=$(wc -l < contrib/ab_sound_cores.txt)  sound-endings=$(wc -l < "$ends")"
  log=logs/sound_${game,,}.log
  bin/windows/confirm_plan.exe "$plan" --size > "$log" 2>&1
  grep -E "candidates:|unnamed ids|expected to match" "$log"

  bin/windows/confirm_plan.exe "$plan" >> "$log" 2>&1
  grep -E "^total:|this run added|found nothing new" "$log" | tail -3
done

echo "=== sound grind finished, run submit ==="
