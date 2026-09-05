"""Emit exact labels from NotNierPea's BO4 Shield-support hash map only."""

from pathlib import Path
import re


SOURCE = Path(
    "borrowed/shield-support-mod/ShieldConfig/project-bo4/mods/"
    "T8ShieldSupport/SupportUtils/SupportHashes.txt"
)
NAME = re.compile(r"^[A-Za-z0-9_./\\-]{3,240}$")


def main() -> None:
    names: set[str] = set()
    for raw in SOURCE.read_text(encoding="utf-8", errors="replace").splitlines():
        _hash, separator, name = raw.partition(",")
        name = name.strip()
        if separator and NAME.fullmatch(name) and sum(character.isalpha() for character in name) >= 3:
            names.add(name)
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    main()
