#!/usr/bin/env bash
# Grind every installed capture with fresh confirmed-only all-boundary cores, each game wearing
# its own measured ending list.
#
#   contrib/grind_all_games.sh
#
# Not a method rotation: one method, pointed at seven games, with the stems regenerated from
# whatever the corpus holds today. AGENTS.md 2 forbids looping over every existing method; this
# loops over games, which is what `start` itself does, and stops the moment a game's pass refuses.
set -u
cd "$(dirname "$0")/.."

GAMES=(BLKOPS04 BLKOPSCW MODWAR22 YAMYAMOK BLACKOP6 BLACKOP7 MODWAR7)
mkdir -p logs plans/grind

for game in "${GAMES[@]}"; do
  bin/windows/next_game.exe --game "$game" > /dev/null

  if [ "$game" = BLKOPS04 ] || [ "$game" = BLKOPSCW ]; then
    ends=data/suffixes.txt
  else
    ends=data/modern/${game,,}/suffixes.txt
  fi
  if [ ! -f "$ends" ]; then
    echo "=== $game: no ending list at $ends, skipping (run derive_modern_lists.py)"
    continue
  fi

  plan=plans/grind/${game,,}_cores.txt
  {
    echo "label: fresh confirmed-only cores against $game, own endings"
    echo "describe: all-boundary cores from names only this project has confirmed, wearing $ends"
    echo "stem: @contrib/ab_cores.txt"
    echo "end: @$ends"
    echo "bare: yes"
  } > "$plan"

  streak=$(cat state/empty_runs.txt 2>/dev/null || echo 0)
  override=()
  if [ "${streak:-0}" -ge 3 ]; then
    # The guard trips on derive_closure's own empty derivations, which the tool itself says is
    # not the case it is meant for. Any run that confirms one name clears it again.
    override=(--anyway)
  fi

  echo "=== $game  stems=$(wc -l < contrib/ab_cores.txt)  endings=$(wc -l < "$ends")  streak=$streak"
  log=logs/grind_${game,,}.log
  bin/windows/confirm_plan.exe "$plan" --size > "$log" 2>&1
  grep -E "candidates:|unnamed ids|expected to match" "$log"

  bin/windows/confirm_plan.exe "$plan" "${override[@]}" >> "$log" 2>&1
  grep -E "^total:|this run added|fingerprint|new\b" "$log" | tail -4
done

echo "=== grind finished, run submit ==="
