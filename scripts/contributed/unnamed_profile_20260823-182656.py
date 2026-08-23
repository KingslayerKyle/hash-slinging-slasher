"""What the *unnamed* names look like -- read off the ones this project has already recovered.

    python contrib/unnamed_profile.py            the profile and the over-represented affixes
    python contrib/unnamed_profile.py --grid     which families are grid-shaped and how sparse

## The idea

Every method here is aimed by looking at what is *known*: the published tables, the confirmed
names, the affix lists measured off them. But the target is what is **unknown**, and those two
populations are not the same shape. Nobody had checked how different.

There is a direct sample of the unknown population sitting in `findings/`: every name this
project has confirmed **was unnamed until somebody found it**. Profiling it against the published
tables says where the remaining unnamed mass actually is.

Measured 2026-08-23 over 1,560,882 published names and the 54,875 confirmed ones that are not
among them:

                        published   confirmed
    median segments             8           6
    contains `/`            44.6%       14.2%
    contains `*`            16.0%        0.0%
    contains a digit        93.2%       45.6%
    average length           38.1        29.9

**The unnamed names are shorter, flatter and far less numeric than the corpus every list here is
measured from.** A generator tuned on the published tables is tuned on the wrong distribution.

And the beginnings tell you exactly where to point:

    vox_           42.70% of confirmed   against  0.02% published
    mcdp/           5.69%                          0.04%
    fly_            5.19%                          0.00%
    evt_            2.58%                          0.00%
    callingcards_   2.26%                          0.00%
    amb_            2.10%                          0.00%

`vox_` alone is **forty-two percent of everything this project has ever recovered**, and it is
two hundredths of a percent of the published tables. The endings say the same thing -- `_mtxitem`
10.41% against 0.00%, then `_use`, `_threat`, `_dyn`, `_dstr`, `_npc`, `_plr`, `_vox`.

Those are sound aliases and UI strings. Cold War's largest unnamed pool is `sound_alias` at
43,603, and this is why.

## The grid that falls out of it

Those families are not free text, they are **grids**: `vox_<speaker>_<line>` over 439 speaker
codes and 13,012 lines -- `wood` is Woods, `ami6` is MI6, `adlr` is Adler -- and every speaker
records broadly the same lines. The grid is 5.6 M cells and only 37,983 are named, so the unseen
cells are candidates by construction. Same shape for `fly_`, `evt_`, `amb_`, `callingcards_`,
`p7_`/`p8_`/`p9_`, `wpn_`, `veh_`, `zmb_`.

Measured: 5.56 M unseen `vox_` cells returned **34 names in 12 seconds**, and 50.3 M cells across
all families returned **10 more**. A low rate per candidate, but the candidates cost nothing --
and unlike a cross product over the published corpus, this is aimed at the distribution the
unnamed names actually have.

**This is reconnaissance, not a method.** Run it before choosing where to point a night.
"""

import argparse
import collections
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").exists() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))

import snapshot

TABLES = ["fnv1a_xmaterials", "fnv1a_xmaterials_v2", "fnv1a_ximages", "fnv1a_ximages_v2",
          "fnv1a_xmodels", "fnv1a_xanims", "fnv1a_xanims_v2"]


def shape(names, label):
    n = len(names) or 1
    segs = sorted(len(x.replace("/", "_").split("_")) for x in names)
    print(f"  {label:11} {segs[len(segs)//2]:>6}   "
          f"{sum('/' in x for x in names)/n:>7.1%}  {sum('*' in x for x in names)/n:>6.1%}  "
          f"{sum(any(c.isdigit() for c in x) for x in names)/n:>8.1%}  "
          f"{sum(len(x) for x in names)/n:>6.1f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--grid", action="store_true", help="rank families by how grid-shaped they are")
    ap.add_argument("--top", type=int, default=16)
    args = ap.parse_args()

    published = {n.lower() for n in snapshot.table_names(*TABLES)}
    confirmed = {n.lower() for n in snapshot.confirmed_names()} - published
    published.discard("")
    confirmed.discard("")

    print(f"published {len(published)}   confirmed and not published {len(confirmed)}\n")
    print(f"  {'':11} {'segs':>6}   {'has /':>7}  {'has *':>6}  {'digits':>8}  {'len':>6}")
    shape(published, "published")
    shape(confirmed, "confirmed")

    def firsts(names):
        c = collections.Counter()
        for x in names:
            for i, ch in enumerate(x):
                if ch in "_/" and i <= 24:
                    c[x[:i + 1]] += 1
                    break
        return c

    p, q = firsts(published), firsts(confirmed)
    pt, qt = sum(p.values()) or 1, sum(q.values()) or 1
    over = sorted(q.items(), key=lambda kv: -(kv[1] / qt - p.get(kv[0], 0) / pt))[:args.top]
    print("\nbeginnings over-represented among the recovered -- where the unnamed live:")
    for a, c in over:
        print(f"   {c:7} ({c/qt:6.2%})  published {p.get(a,0)/pt:6.2%}   {a}")

    if not args.grid:
        return

    have = published | confirmed
    have |= {n.lower() for n in snapshot.table_names(
        "fnv1a_soundbanks_aliases", "fnv1a_soundbanks_aliases_v2",
        "fnv1a_xsounds", "fnv1a_xsounds_v2")}
    fam = collections.defaultdict(list)
    for n in have:
        if n.count("_") >= 2 and "/" not in n and "." not in n:
            fam[n.split("_", 1)[0]].append(n)

    print("\nfamilies shaped like a grid, by how many cells are unseen:")
    rows = []
    for head, names in fam.items():
        if len(names) < 200:
            continue
        axis, tails = set(), set()
        for n in names:
            parts = n.split("_", 2)
            if len(parts) == 3:
                axis.add(parts[1])
                tails.add(parts[2])
        if len(axis) < 3 or len(tails) < 20:
            continue
        rows.append((head, len(axis), len(tails), len(axis) * len(tails) - len(names)))
    for head, a, t, unseen in sorted(rows, key=lambda r: -r[3])[:args.top]:
        print(f"   {head:16} {a:5} x {t:6} = {a*t:>12,}   unseen {unseen:>12,}")


if __name__ == "__main__":
    main()
