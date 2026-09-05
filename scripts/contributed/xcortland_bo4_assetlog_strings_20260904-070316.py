"""Emit literal BO4 build strings from xCortlandx/fnvHashFinder's AssetLog archive.

The archive's Anim, Image, Material, Model, and Sound records are mostly generated
hash labels.  Its String records, in contrast, are literal names extracted from the
BO4 build and include structured asset-family fragments.  Keep only ordinary
asset-name characters so confirm_list receives the source text unchanged.
"""

from pathlib import Path
import re


SOURCE = Path("borrowed/fnvHashFinder/AssetLogs/AssetLog_BO4.txt")
NAME = re.compile(r"^[A-Za-z0-9_./\\-]+$")


def main() -> None:
    seen: set[str] = set()
    with SOURCE.open("r", encoding="utf-8", errors="replace") as source:
        for raw in source:
            kind, separator, name = raw.rstrip("\r\n").partition(",")
            if (
                kind != "String"
                or not separator
                or not 3 <= len(name) <= 240
                or not NAME.fullmatch(name)
                or sum(character.isalpha() for character in name) < 3
                or name in seen
            ):
                continue
            seen.add(name)
            print(name)


if __name__ == "__main__":
    main()
