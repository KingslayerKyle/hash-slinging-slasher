"""Probe the unmined map-set/faction seam in confirmed BO4 xmodels.

Map assets use p7_/p8_/p9_ families while their body often carries a mode/faction token.
Only observed map heads and observed faction tokens are recombined; no arbitrary words are
introduced.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
heads = ("p7", "p8", "p9")
factions = ("mp", "zm", "wz", "cp", "sp")
seen = set()
for path in (ROOT / "findings" / "blkops04").rglob("*.txt"):
    if path.stem.split("_")[0] not in ("xmodel", "xanim", "image", "material"):
        continue
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        name = line.partition(",")[2].strip()
        bits = name.split("_")
        if len(bits) < 3 or bits[0] not in heads:
            continue
        for head in heads:
            for faction in factions:
                candidate = "_".join((head, faction, *bits[2:]))
                if candidate != name:
                    seen.add(candidate)
print(f"{len(seen):,} BO4 map-set/faction candidates", file=sys.stderr)
for candidate in sorted(seen):
    print(candidate)
