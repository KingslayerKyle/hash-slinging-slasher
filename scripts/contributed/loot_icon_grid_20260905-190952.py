#!/usr/bin/env python3
"""The store's loot-icon grid, filled in from the corner of it the tables already hold.

Black Ops 4 names its store icons on a strict four-part grid:

    <family>_ui_icon_<kind>_<theme>_<tier>_<subject>
    loot02_ui_icon_outfit_northern_lights_legendary3_seraph

Every axis is a closed vocabulary -- there are only so many specialists, only so many rarity
tiers, only so many bundles -- and the grid is almost entirely unobserved: the four axes measured
off the corpus multiply out to roughly a hundred and forty thousand cells, and the published
tables plus everything confirmed here hold about two thousand of them. That gap is not evidence
of absence. It is one bundle shipping for every specialist while the tables happened to catch
three of them.

What makes this worth a pass rather than a guess is the regularity of the counts: the thirteen
specialists appear 19, 19, 20, 20, 20, 20, 21, 21, 22, 22, 23 times. A grid that even is a grid
the game filled in, so the cells nobody has seen are overwhelmingly cells that exist.

Axes are measured from the corpus at run time rather than hardcoded, so the grid grows itself as
names are confirmed -- a new theme recovered by any method widens every later run. The numbered
axes are extended a little past the highest observed index, which is the one place this guesses,
and it guesses cheaply: a tier that does not exist costs one candidate.

    python loot_icon_grid.py | confirm_list - --label "loot icon grid"
"""
import collections
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES = ("fnv1a_ximages.csv", "fnv1a_xmodels.csv", "fnv1a_xmaterials.csv")

# `<family>_ui_icon_<kind>_<rest>`, where rest is `<theme>_<tier><n>_<subject>`.
HEAD = re.compile(r"^(loot\d*)_ui_icon_([a-z_]+?)_(.+)$")
TIER = re.compile(r"^(.*?)_([a-z]+?)(\d+)_(.*)$")

# Rarity words, so a theme containing a digit is not mistaken for a tier. Measured off the
# corpus: these are the only ones that ever carry a trailing index in this family.
RARITIES = {
    "legendary", "epic", "rare", "common", "uncommon", "reactive", "mastercraft", "heroic",
}


def corpus():
    for sub in ("blkops04", "blkopscw"):
        d = os.path.join(ROOT, "all_names", sub)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith(".txt"):
                with open(os.path.join(d, f), encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        yield line.strip().split(",")[-1].lower()
    for f in TABLES:
        p = os.path.join(ROOT, "cod-name-db", "csv", f)
        if os.path.exists(p):
            with open(p, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    yield line.strip().split(",", 1)[-1].lower()


def main():
    families, kinds, themes, tiers, subjects = (collections.Counter() for _ in range(5))
    seen = set()
    for nm in corpus():
        m = HEAD.match(nm)
        if not m:
            continue
        seen.add(nm)
        fam, kind, rest = m.groups()
        t = TIER.match(rest)
        if not t or t.group(2) not in RARITIES:
            continue
        theme, rarity, idx, subject = t.groups()
        families[fam] += 1
        kinds[kind] += 1
        themes[theme] += 1
        tiers[(rarity, int(idx))] += 1
        subjects[subject] += 1

    # Extend the two numbered axes just past what was observed. A bundle numbered one higher than
    # any seen is the cheapest possible guess and the likeliest to be real.
    fam_max = max(int(f[4:] or 1) for f in families)
    fam_axis = ["loot"] + ["loot%02d" % i for i in range(2, fam_max + 3)]
    rar_max = collections.defaultdict(int)
    for (rarity, idx) in tiers:
        rar_max[rarity] = max(rar_max[rarity], idx)
    tier_axis = ["%s%d" % (r, i) for r, n in rar_max.items() for i in range(1, n + 3)]

    print(
        "axes: %d families, %d kinds, %d themes, %d tiers, %d subjects; %d cells observed"
        % (len(fam_axis), len(kinds), len(themes), len(tier_axis), len(subjects), len(seen)),
        file=sys.stderr,
    )

    n = 0
    for fam in fam_axis:
        for kind in kinds:
            for theme in themes:
                for tier in tier_axis:
                    stem = "%s_ui_icon_%s_%s_%s_" % (fam, kind, theme, tier)
                    for subject in subjects:
                        n += 1
                        print(stem + subject)
    print("emitted %d" % n, file=sys.stderr)


if __name__ == "__main__":
    main()
