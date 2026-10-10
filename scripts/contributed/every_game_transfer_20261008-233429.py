"""Every name known for any game, offered verbatim to one target game.

The modern titles share a great deal of content with each other and with the older two, but each
hashes its ordinary assets and aliases under its own policy, so a name published for one game says
nothing about the others until it is rehashed under theirs. This prints every name anybody knows --
all cod-name-db tables (v1 and v2), every merged submission, the `all_names/` lists and this
machine's findings -- once each, and lets `confirm_list --game <TAG>` apply the target's hash,
exclusion and pools.

Spent by: a target whose snapshot has already been offered the corpus as it stands; re-run it only
after the tables or the submissions have grown.
"""
from pathlib import Path
import sys

ROOT = next((p for p in Path(__file__).resolve().parents
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run this generator from a solver checkout')


def rows(path):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    for line in text.splitlines():
        key, sep, value = line.partition(",")
        name = (value if sep else key).strip()
        if name and not name.startswith("#") and len(name) < 256:
            yield name


def sources():
    yield from sorted((ROOT / "cod-name-db" / "csv").glob("fnv1a_*.csv"))
    for folder in ("all_names", "submissions", "findings"):
        base = ROOT / folder
        if base.exists():
            yield from sorted(base.rglob("*.txt"))


def main():
    seen = set()
    out = sys.stdout
    for path in sources():
        for name in rows(path):
            lowered = name.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            out.write(name + "\n")
    print(f"{len(seen):,} distinct names offered", file=sys.stderr)


if __name__ == "__main__":
    main()
