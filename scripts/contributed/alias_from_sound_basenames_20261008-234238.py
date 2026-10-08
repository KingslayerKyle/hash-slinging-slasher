"""Sound-alias candidates read off every known modern sound file's basename.

A modern sound file is `dir/.../<basename>.<codec>.<rate>.<lang>`; in the published v2 tables 1,029
of 23,137 known aliases are exactly a file's basename with its trailing take number removed, and
313 are the whole basename. Both spellings are offered for every sound file anybody knows (the v2
table plus merged submissions and local findings), and `confirm_list --game <TAG>` keeps the ones
the target game holds as aliases.

Spent by: the sound-file corpus as it stands; re-run after new sound files are confirmed.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
TAKE = re.compile(r"_\d+$")


def sound_files():
    yield ROOT / "cod-name-db" / "csv" / "fnv1a_xsounds_v2.csv"
    for folder in ("submissions", "findings"):
        base = ROOT / folder
        if base.exists():
            yield from base.rglob("sound_asset*.txt")
            yield from base.rglob("sndasset*.txt")


def main():
    seen = set()
    for path in sound_files():
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            name = line.partition(",")[2].strip().lower().replace("\\", "/")
            base = name.rsplit("/", 1)[-1].split(".", 1)[0]
            for candidate in (base, TAKE.sub("", base)):
                if candidate and candidate not in seen:
                    seen.add(candidate)
                    print(candidate)
    print(f"{len(seen):,} alias candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
