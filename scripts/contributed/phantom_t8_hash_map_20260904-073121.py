"""Emit literal labels from Lurkzy/phantom-t8's versioned BO4 hash map."""

from pathlib import Path
import re


SOURCE = Path("borrowed/phantom-t8/hashes.txt")
NAME = re.compile(r"^[A-Za-z0-9_./\\-]{3,240}$")


def main() -> None:
    names: set[str] = set()
    for raw in SOURCE.read_text(encoding="utf-8", errors="replace").splitlines():
        _hash, separator, name = raw.partition(",")
        name = name.strip()
        if separator and NAME.fullmatch(name) and sum(char.isalpha() for char in name) >= 3:
            names.add(name)
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    main()
