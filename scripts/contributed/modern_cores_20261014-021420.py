"""Cut cores out of confirmed names, per game: name minus one measured beginning and one measured ending.

    python contrib/modern_cores.py                 every game with a measured vocabulary
    python contrib/modern_cores.py blackop6        one game

A plan's stems have to be material known to be real, and the general pass's stems are scraped
pieces -- a different set from the *middle* of a name some game has already confirmed. Stripping
each name's measured decoration off both ends leaves the core the decoration was wrapped around,
and re-wrapping it in another game's beginnings and endings is the cross-game seam this project
has always mined: Cold War carries a great deal of Black Ops 4's content and the modern titles
share an engine's vocabulary.

Ranked by how many names share a core, most common first, so a head slice is the popular half.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES = ["blackop6", "blackop7", "modwar7", "yamyamok", "modwar22", "blkops04", "blkopscw"]
SHORTEST = 3


def read_lines(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return [line.strip() for line in handle if line.strip()]


def lists_for(game):
    where = os.path.join(ROOT, "data", "modern", game)
    begin, end = os.path.join(where, "prefixes.txt"), os.path.join(where, "suffixes.txt")
    if not (os.path.exists(begin) and os.path.exists(end)):
        begin, end = os.path.join(ROOT, "data", "prefixes.txt"), os.path.join(ROOT, "data", "suffixes.txt")
    # Longest decoration first, so the longest matching one is the one stripped: `s6.op.operator_`
    # is a beginning, and so is `s6/`, and only one of them is right for a given name.
    starts = sorted((s for s in read_lines(begin) if not s.startswith("#")), key=len, reverse=True)
    ends = sorted((s for s in read_lines(end) if not s.startswith("#")), key=len, reverse=True)
    return starts, ends


def cores_of(game, seen):
    folder = os.path.join(ROOT, "all_names", game)
    if not os.path.isdir(folder):
        print(f"{game}: no confirmed names", file=sys.stderr)
        return
    starts, ends = lists_for(game)
    before = len(seen)
    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".txt"):
            continue
        for line in read_lines(os.path.join(folder, filename)):
            name = line.split(",", 1)[-1].strip() if "," in line else line
            core = name
            for start in starts:
                if core.startswith(start):
                    core = core[len(start):]
                    break
            for end in ends:
                if core.endswith(end) and len(core) > len(end) + SHORTEST:
                    core = core[: -len(end)]
                    break
            if SHORTEST <= len(core) <= 120 and " " not in core:
                seen[core] = seen.get(core, 0) + 1
    print(f"{game}: {len(seen) - before} cores ({len(seen)} total)", file=sys.stderr)


def main():
    games = sys.argv[1:] or GAMES
    seen = {}
    for game in games:
        cores_of(game, seen)
    for core, _ in sorted(seen.items(), key=lambda item: (-item[1], item[0])):
        print(core)


if __name__ == "__main__":
    main()
