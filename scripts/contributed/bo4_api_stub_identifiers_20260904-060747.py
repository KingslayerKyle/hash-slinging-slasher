#!/usr/bin/env python3
"""Emit asset-shaped identifiers in the BO4 service-response fixtures.

The public callofdutyapi project retains captured BO4 profile and match API
responses.  These contain a small, separate vocabulary of map, playlist and
specialist identifiers, distinct from game-script source trees.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUBS = ROOT / "borrowed" / "callofdutyapi" / "packages" / "api" / "stubs"
TOKEN = re.compile(r'"([a-z0-9_./-]{6,160})"')


def main() -> None:
    names = set()
    for path in STUBS.glob("bo4.*.json"):
        for value in TOKEN.findall(path.read_text(encoding="utf-8")):
            if "_" in value or "/" in value:
                names.add(value)
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    main()
