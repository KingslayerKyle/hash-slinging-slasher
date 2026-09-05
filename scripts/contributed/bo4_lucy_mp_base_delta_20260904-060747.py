#!/usr/bin/env python3
"""Emit BO4 Lucy MP Base identifiers absent from earlier BO4 source trees.

Unlike the menu-source extractors, this also reads the resolved textual
identifiers after the hash comma in the project's hashes.txt file.  The prior
trees are compared using the same quoted-literal convention used by the
fresh-source delta, keeping this a provenance-preserving source delta.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "borrowed" / "BO4-Lucy-MP-Base"
OLD = (
    "bo4-source", "bo4-source-lua", "t8-src", "BO4-BlackoutBots",
    "bo4-lucy-menu", "BO4-BlackOps4ShieldMenu", "BlackoutBotsBO4",
    "Abomination-Unofficial", "Synergy-BO4-GSC-Menu", "t8-tests",
    "Shield-Menu-BO4", "bo4-pap-mod", "demo_mods", "shield_mods",
    "Aurora-BO4-Lucy-Menu", "BlackOps4Shop", "BO4-Director-s-Cut",
    "Bo4HashFinder", "t8-atian-menu", "t8-custom-ee",
    "SyndiShanX-COD-GSC-Source/BO4-GSC",
    "SyndiShanX-COD-GSC-Source/BO4-LUA",
)
LITERAL = re.compile(r'(?:#)?["\']([A-Za-z0-9_./\\-]{6,160})["\']')
VALID = re.compile(r'^[a-z0-9_./-]{6,160}$')
TEXT_EXTENSIONS = {".gsc", ".csc", ".lua", ".txt", ".md", ".cfg", ".json"}


def clean(value: str) -> str | None:
    value = value.strip().lower().replace("\\", "/")
    if VALID.fullmatch(value) and ("_" in value or "/" in value):
        return value
    return None


def old_literals() -> set[str]:
    names = set()
    for item in OLD:
        base = ROOT / "borrowed" / item
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            names.update(value for raw in LITERAL.findall(text) if (value := clean(raw)))
    return names


def main() -> None:
    names = set()
    for path in NEW.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        names.update(value for raw in LITERAL.findall(text) if (value := clean(raw)))
        if path.name == "hashes.txt":
            for line in text.splitlines():
                if "," in line:
                    value = clean(line.split(",", 1)[1])
                    if value:
                        names.add(value)
    print("\n".join(sorted(names - old_literals())))


if __name__ == "__main__":
    main()
