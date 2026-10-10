"""Every known head x every tail shared by >= N heads, for any kind -- as a compiled plan.

`alias_heads_shared_tails` does this for aliases only (526 BO7 aliases on its first run). Images,
materials and anims are underscore-joined the same way, so the same product applies: a head is a
name cut after an underscore (kept with the `_`), a tail is what follows the cut, and a tail is
carried only when at least `--support` distinct heads attest it. Material directories (`tm/`) stay
on the head, so a material tail lands back under its own directory.

    python contrib/heads_shared_tails_any.py --kind image --support 3 --out plans/hst_image

Spent by: the corpus of the kind as it stands, per support; re-run after it grows.
"""
from collections import defaultdict
from pathlib import Path
import argparse
import sys

ROOT = next((p for p in Path(__file__).resolve().parents
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run this generator from a solver checkout')
TABLES = {"image": "fnv1a_ximages*.csv", "material": "fnv1a_xmaterials*.csv",
          "xanim": "fnv1a_xanims*.csv", "sound_alias": "fnv1a_soundbanks_aliases*.csv", "sound_asset": "fnv1a_xsounds_v2.csv"}


def names(kind):
    srcs = list((ROOT / "cod-name-db" / "csv").glob(TABLES[kind]))
    for folder in ("findings", "submissions"):
        srcs += list((ROOT / folder).rglob(f"{kind}*.txt"))
    for p in srcs:
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            k, sep, v = line.partition(",")
            v = (v if sep else k).strip().lower()
            if v and "~" not in v and "," not in v and "*" not in v:
                yield v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", default="image")
    ap.add_argument("--support", type=int, default=3)
    ap.add_argument("--max-depth", type=int, default=4, help="tails of at most this many tokens")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    heads, tail_heads = set(), defaultdict(int)
    for n in set(names(a.kind)):
        t = n.split("_")
        for i in range(1, len(t)):
            h = "_".join(t[:i]) + "_"
            heads.add(h)
            if len(t) - i <= a.max_depth:
                tail_heads["_".join(t[i:])] += 1
    tails = sorted(t for t, c in tail_heads.items() if c >= a.support)
    out = Path(a.out)
    (ROOT / f"{out}_heads.txt").write_text("\n".join(sorted(heads)) + "\n")
    (ROOT / f"{out}_tails.txt").write_text("\n".join(tails) + "\n")
    (ROOT / f"{out}.txt").write_text(
        f"label: {a.kind} heads x tails shared by >= {a.support} heads\n"
        f"stem: @{out}_heads.txt\nend: @{out}_tails.txt\nbare: yes\n")
    print(f"{len(heads):,} heads x {len(tails):,} tails", file=sys.stderr)


if __name__ == "__main__":
    main()
