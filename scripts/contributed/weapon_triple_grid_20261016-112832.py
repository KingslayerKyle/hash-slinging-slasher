"""Image/material names with their `p<NN>_<class>_<weapon>` triple swapped for every same-class weapon.

Modern weapon art names carry the weapon as a triple: `cm_att_t10_p03_dm_sgeorge550_pgrip_sprint1_sec`,
`cm_wpn_t10_p21_sm_pparis90_rail_s2blk_pri`, `icon_..._p01_ar_mike16_...`. Measured 2026-10-16: BO6's
`cm_att_t10_` family alone is 56 weapons x its class's suffixes = 27,705 cells, 4,266 resolved.
Each resolved name becomes a template; templates sharing the text before the triple and the class
form a family, and every template is offered with every weapon triple that family has used.

    python contrib/weapon_triple_grid.py <GAME> <pool> | confirm_list - --game <GAME>
"""
from collections import defaultdict
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

TRIPLE = re.compile(r"(?<![a-z0-9])(p\d{2})_([a-z]{2})_([a-z0-9]+)(?![a-z0-9])")
MAX_TEMPLATES = 20000


def main():
    game, pool = sys.argv[1].upper(), sys.argv[2]
    temps = defaultdict(set)
    weapons = defaultdict(set)
    for g in ("BLACKOP6", "BLACKOP7", "YAMYAMOK", "MODWAR22", "MODWAR7"):
        for line in (ROOT / "state" / "an" / f"{g}_{pool}.named").open(encoding="utf-8"):
            n = line.strip()
            m = TRIPLE.search(n)
            if not m:
                continue
            key = (n[:m.start()], m.group(2))
            weapons[key].add(f"{m.group(1)}_{m.group(2)}_{m.group(3)}")
            if g == game:
                temps[key].add(n[:m.start()] + "{}" + n[m.end():])
    out = sys.stdout
    seen = set()
    for key, ts in temps.items():
        if len(ts) > MAX_TEMPLATES:
            continue
        for t in ts:
            for w in weapons[key]:
                c = t.replace("{}", w)
                if c not in seen:
                    seen.add(c)
                    out.write(c + "\n")
    print(f"{game} {pool}: {len(temps):,} families -> {len(seen):,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
