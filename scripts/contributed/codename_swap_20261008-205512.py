"""Every known name with its game codename token swapped for every other game's.

Content carried from one title into the next is often renamed by its codename only:
`jup_card_b2068_7` (MWIII) beside `sat_...` (BO7) and `t10_...` (BO6), `iw9_` beside `iw8_`,
`veh9_` beside `veh8_`, `ai_t9_zm_` beside `ai_t10_zm_`. Cross-game transfer only tries the
spelling as published; this tries each codename occurrence (as a whole `_`/`/`-delimited token,
optionally followed by digits/underscore) replaced by each other codename in its group.

    python contrib/codename_swap.py | confirm_list - --game BLACKOP7 --script contrib/codename_swap.py
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

GROUPS = [
    ["iw7", "iw8", "iw9", "jup", "t7", "t8", "t9", "t10", "sat", "s4", "h1", "h2", "s2"],
    ["veh7", "veh8", "veh9", "veh10"],
]
TOKEN = {g: re.compile(r"(?<![a-z0-9])(" + "|".join(sorted(grp, key=len, reverse=True)) + r")(?=[_/]|$)")
         for g, grp in enumerate(GROUPS)}


def names():
    for f in sorted((ROOT / "cod-name-db" / "csv").glob("*.csv")):
        for line in f.open(encoding="utf-8", errors="replace"):
            yield line.rstrip("\r\n").partition(",")[2]
    for top in ("all_names", "submissions", "findings", "contrib/open_pr_names"):
        for f in sorted((ROOT / top).rglob("*.txt")):
            for line in f.open(encoding="utf-8", errors="replace"):
                key, sep, name = line.rstrip("\r\n").partition(",")
                if sep:
                    yield name


def main():
    seen = set()
    out = sys.stdout
    for name in names():
        name = name.strip().lower()
        if not name or name in seen:
            continue
        seen.add(name)
        for g, rx in TOKEN.items():
            for m in rx.finditer(name):
                for alt in GROUPS[g]:
                    if alt != m.group(1):
                        out.write(name[: m.start()] + alt + name[m.end():] + "\n")


if __name__ == "__main__":
    main()
