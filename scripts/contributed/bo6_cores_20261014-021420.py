"""Cut cores out of confirmed BO6 names: each name minus one measured beginning and one measured ending.

    python contrib/bo6_cores.py > contrib/bo6_cores.txt

A plan's stems have to be material known to be real, and the general pass's stems are scraped
pieces -- which is a different set from the *middle* of a name the game has already confirmed.
Stripping the measured decoration off both ends of 220k confirmed names leaves the core that the
decoration was wrapped around, and re-wrapping it in the beginnings and endings the corpus is
measured to carry is what a plan is for. Ranked by how many names share the core, most common
first, so a head slice of the file is the popular half rather than an arbitrary one.
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = "blackop6"
NAMES = os.path.join(ROOT, "all_names", GAME)
BEGIN = os.path.join(ROOT, "data", "modern", GAME, "prefixes.txt")
END = os.path.join(ROOT, "data", "modern", GAME, "suffixes.txt")
SHORTEST = 3


def read_lines(path):
    with open(path, encoding="utf-8", errors="replace") as handle:
        return [line.strip() for line in handle if line.strip()]


def main():
    # Longest decoration first, so the longest matching one is the one stripped: `s6.op.operator_`
    # is a beginning, and so is `s6/`, and only one of them is right for a given name.
    starts = sorted((s for s in read_lines(BEGIN) if not s.startswith("#")), key=len, reverse=True)
    ends = sorted((s for s in read_lines(END) if not s.startswith("#")), key=len, reverse=True)
    start_set = set(starts)
    end_set = set(ends)

    seen = {}
    for filename in sorted(os.listdir(NAMES)):
        if not filename.endswith(".txt"):
            continue
        for line in read_lines(os.path.join(NAMES, filename)):
            name = line.split(",", 1)[-1].strip() if "," in line else line
            core = name
            if core[:3] in start_set or True:
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

    for core, _ in sorted(seen.items(), key=lambda item: (-item[1], item[0])):
        print(core)
    print(f"{len(seen)} distinct cores from confirmed names", file=sys.stderr)


if __name__ == "__main__":
    main()
