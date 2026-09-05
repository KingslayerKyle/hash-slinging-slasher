"""Offer confirmed names from the other title as verbatim cross-game candidates.

Cold War and Black Ops 4 use the same FNV-1a name hash, but their shipped asset corpora
are different.  This deliberately does no spelling or decoration: it tests the small,
high-confidence cross-title seam using only names already confirmed in the other title.
The target game's confirmer supplies exclusion against its own tables and findings.
"""
from pathlib import Path
import argparse
import re
import sys

ROOT = Path(__file__).resolve().parent.parent


def names_for(game):
    folder = ROOT / "findings" / game.lower()
    out = set()
    if not folder.exists():
        return out
    for path in folder.rglob("*.txt"):
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            key, sep, value = line.partition(",")
            name = (value if sep else key).strip()
            # Finding rows are hash,name; ignore malformed bookkeeping lines.
            if name and not name.startswith("#"):
                out.add(name)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=("blkops04", "blkopscw"), default="blkopscw")
    args = parser.parse_args()
    names = names_for(args.source)
    print(f"{len(names):,} confirmed names from {args.source} findings", file=sys.stderr)
    for name in sorted(names):
        print(name)


if __name__ == "__main__":
    main()
