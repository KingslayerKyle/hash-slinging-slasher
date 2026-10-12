#!/usr/bin/env bash
# Grind every installed capture with fresh confirmed-only all-boundary cores, each game wearing
# its own measured ending list.
#
#   contrib/grind_all_games.sh
#
# Not a method rotation: one method, pointed at seven games, with the stems regenerated from
# whatever the corpus holds today. AGENTS.md 2 forbids looping over every existing method; this
# loops over games, which is what `start` itself does, and stops the moment a game's pass refuses.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "$0")" && pwd)"
while [ ! -f "$ROOT/scripts/snapshot.py" ] && [ "$ROOT" != / ]; do
  ROOT="$(dirname -- "$ROOT")"
done
if [ ! -f "$ROOT/scripts/snapshot.py" ]; then
  echo "Could not locate the repository root" >&2
  exit 2
fi
cd -- "$ROOT"

if [ ! -f contrib/ab_cores.txt ]; then
  echo "Missing contrib/ab_cores.txt; build the confirmed-only cores first" >&2
  exit 2
fi

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

  echo "=== $game  stems=$(wc -l < contrib/ab_cores.txt)  endings=$(wc -l < "$ends")"
  log=logs/grind_${game,,}.log
  bin/windows/confirm_plan.exe "$plan" --size > "$log" 2>&1
  grep -E "candidates:|unnamed ids|expected to match" "$log" || true

  bin/windows/confirm_plan.exe "$plan" >> "$log" 2>&1
  grep -E "^total:|this run added|fingerprint|new\b" "$log" | tail -4 || true
  bin/windows/submit.exe
done

echo "=== grind finished ==="
