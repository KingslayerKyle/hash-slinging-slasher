"""Emit bounded quoted asset-shaped literals from NotNierPea/t8-spawn-patch."""

from pathlib import Path
import re


ROOT = Path("borrowed/t8-spawn-patch/Scripts")
FILES = ("detours.gsc", "includes.gsc", "main.gsc", "utils.gsc")
LITERAL = re.compile(r'"([A-Za-z0-9_./-]{3,240})"')
PLACEHOLDER = re.compile(r"^hash_[0-9a-f]+$", re.I)


def main() -> None:
    names: set[str] = set()
    for filename in FILES:
        for name in LITERAL.findall((ROOT / filename).read_text(encoding="utf-8", errors="replace")):
            if (
                not PLACEHOLDER.fullmatch(name)
                and ("_" in name or "/" in name)
                and sum(character.isalpha() for character in name) >= 3
            ):
                names.add(name)
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    main()
