"""Modern sound files re-rooted under every other title's codename, in both separator styles.

Modern sound paths are rooted at a codename folder -- `iw9/`, `jup/`, `s6/`, `t10/`, `sat/`, `rex/`,
`core/` -- and the same content is reused from one title to the next. Each known sound file (the v2
table, merged submissions, local findings) is offered with its root folder, and every codename
token in its path, swapped for each other root, spelled with `/` and with `.` (titles differ in
which separator their hash sees; MW7's finds keep `/`, MWII/MWIII's keep `.`).

Spent by: the sound-file corpus as it stands; re-run after new sound files are confirmed.
"""
from pathlib import Path
import re
import sys

ROOT = next((p for p in Path(__file__).resolve().parents
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run this generator from a solver checkout')
CODES = ["iw9", "jup", "s6", "t10", "sat", "rex", "core", "iw8", "s4", "t9"]
TOKEN = re.compile(r"(?<![a-z0-9])(" + "|".join(CODES) + r")(?![a-z0-9])")


def files():
    sources = [ROOT / "cod-name-db" / "csv" / "fnv1a_xsounds_v2.csv"]
    for folder in ("submissions", "findings"):
        base = ROOT / folder
        if base.exists():
            sources.extend(base.rglob("sound_asset*.txt"))
            sources.extend(base.rglob("sndasset*.txt"))
    for path in sources:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            name = line.partition(",")[2].strip().lower().replace("\\", "/")
            if name and "/" in name:
                yield name


def main():
    seen = set()
    for name in files():
        if not TOKEN.search(name):
            continue
        for code in CODES:
            swapped = TOKEN.sub(code, name)
            if swapped == name:
                continue
            for spelled in (swapped, swapped.replace("/", ".")):
                if spelled not in seen:
                    seen.add(spelled)
                    print(spelled)
    print(f"{len(seen):,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
