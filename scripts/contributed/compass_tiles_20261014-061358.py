"""Big-map compass tile grids: <prefix>compass_map_<map>[_ob]_<row>_<col>, every known map.

Warzone-size maps carry their minimap as a grid of tiles, `compass_map_mp_saw_sierra_01_01` ..
`_16_16`. On 2026-10-14 the material->image template run turned up two whole 256-tile grids nobody
had (`compass_map_mp_jup_bigmap_ob_*`, `codcaster_compass_map_mp_jup_bigmap_*`) while only three
maps were known with tiles. This crosses every map name any compass image is known under (and each
with `_ob` added/removed) with the three compass prefixes and a 00..32 x 00..32 two-digit grid.

    python contrib/compass_tiles.py | confirm_list - --game YAMYAMOK
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
names = set()
for f in (ROOT / "state" / "an").glob("*_image.named"):
    for line in open(f, encoding="utf-8"):
        m = re.match(r"^(?:br)?(?:codcaster_)?compass_map_(.+?)(?:_\d+_\d+)?$", line.strip())
        if m:
            names.add(m.group(1))
for top in ("findings",):
    for f in (ROOT / top).rglob("image*.txt"):
        for line in open(f, encoding="utf-8", errors="replace"):
            m = re.match(r"^(?:br)?(?:codcaster_)?compass_map_(.+?)(?:_\d+_\d+)?$", line.strip().partition(",")[2])
            if m:
                names.add(m.group(1))
maps = set()
for n in names:
    maps.add(n)
    maps.add(n[:-3] if n.endswith("_ob") else n + "_ob")
tiles = [f"_{r:02d}_{c:02d}" for r in range(33) for c in range(33)]
for m in sorted(maps):
    for p in ("compass_map_", "codcaster_compass_map_", "brcodcaster_compass_map_"):
        for t in tiles:
            print(p + m + t)
