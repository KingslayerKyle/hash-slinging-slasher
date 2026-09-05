"""Emit explicit typed asset-manifest labels from the frozen ModMe forum archive."""

from pathlib import Path
import re


ROOT = Path("borrowed/ModmeForum")
ROW = re.compile(
    r"(?im)^\s*(?:xmodel|xanim|ximage|xmaterial|material|image)\s*,\s*"
    r"([A-Za-z0-9_./\\-]{3,240})\s*$"
)


def main() -> None:
    names: set[str] = set()
    for source in ROOT.rglob("*.md"):
        names.update(ROW.findall(source.read_text(encoding="utf-8", errors="replace")))
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    main()
