"""Modern weapon sound files re-made for every sibling weapon of the same title and class.

A modern weapon sound lives at `<title>/wpn/<class>/<weapon>/[sub/]<basename>.<tail>` and the
weapon's codename recurs inside the basename (`t10/wpn/ar/able18/reloads/vm_p22_ar_able18_reload_
empty_rotate2.tnn.75.48000.all`). Reloads, inspects, fire layers and foley are built per weapon from
one shared list of actions, so each named file becomes a template with the codename held out, and
the template is filled with every other weapon its title and class are known to hold. A weapon's
`pNN_` platform code stays attached to it: templates carrying one take the sibling's own code.

Spent by: the weapon sound-file corpus as it stands; re-run after it grows.
"""
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAIL = re.compile(r"^(.*)(\.[a-z]+\.\d+\.\d+\.[a-z_]+)$")
PCODE = re.compile(r"(?<![a-z0-9])p\d\d(?=_)")


def names():
    srcs = list((ROOT / "cod-name-db" / "csv").glob("*sound*.csv"))
    for folder in ("findings", "submissions"):
        srcs += list((ROOT / folder).rglob("sound_asset*.txt"))
    for p in srcs:
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            k, sep, v = line.partition(",")
            v = (v if sep else k).strip().lower()
            if "/wpn/" in v:
                yield v


def main():
    templates = collections.defaultdict(set)   # (title, class) -> templates
    weapons = collections.defaultdict(set)     # (title, class) -> weapons
    pcode = {}                                 # (title, weapon) -> pNN
    for n in set(names()):
        m = TAIL.match(n)
        if not m:
            continue
        path, tail = m.groups()
        parts = path.split("/")
        if len(parts) < 5 or parts[1] != "wpn":
            continue
        title, cls, weapon = parts[0], parts[2], parts[3]
        base = parts[-1]
        if len(weapon) < 4 or weapon not in base:
            continue
        key = (title, cls)
        weapons[key].add(weapon)
        pm = PCODE.search(base)
        if pm:
            pcode[(title, weapon)] = pm.group(0)
            base = base[:pm.start()] + "{P}" + base[pm.end():]
        tpl = "/".join(parts[:3] + ["{W}"] + parts[4:-1] + [base.replace(weapon, "{W}")]) + tail
        templates[key].add(tpl)
    out = 0
    for key, tpls in templates.items():
        for w in weapons[key]:
            p = pcode.get((key[0], w))
            for t in tpls:
                if "{P}" in t:
                    if not p:
                        continue
                    t = t.replace("{P}", p)
                print(t.replace("{W}", w))
                out += 1
    print(f"{sum(map(len, templates.values())):,} templates, {out:,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
