"""The beginnings `data/prefixes.txt` cannot express, measured off the corpus.

    python contrib/uncarried_beginnings.py --audit     rank them, write nothing
    python contrib/uncarried_beginnings.py --top 3000  how many to carry

## The gap

METHODS method 22 is *uncarried endings*: `data/suffixes.txt` carries 4,629 endings while the
corpus holds 178,016, and mining the difference returned 6,674 names -- the largest method here.
The same question had never been asked of the beginning list.

Measured 2026-08-23 over the published Cold War tables plus everything confirmed:

    beginnings carried by data/prefixes.txt            700
    distinct beginnings in the corpus            1,127,553
    uncarried                                    1,126,853   heading 7,366,207 names

The commonest are not exotic and not reachable by any generator here:

    twc/ 229,447   jup_ 58,965   m/ 54,088   jup_vm_ 41,154   i_mtl_p8_ 30,100
    tm/ 26,375     i_mtl_p9_ 24,915   i_c_t9_ 21,315   i_c_t8_ 20,529   tw/ 19,579

`i_c_t9_` heads 21,315 names on its own -- the image prefix for Cold War character assets -- and
the list cannot say it.

## Why this is not the dead end METHODS already records

The dead ends table has *uncarried beginnings crossed with the whole corpus*, which returned 7
names, and *doubly uncarried*, which returned 0. Both crossed uncarried beginnings with **Cold
War's own** stems -- a corpus recombined with itself, which cannot leave the region it already
covers. This list is meant to be crossed with stems from **outside**: Modern Warfare 2019's
packed-channel parts, its middles, or any other title's corpus. The beginning list being capped
is what stops external material from being decorated the way Cold War actually decorates it.

## And the character class nobody carries

250,324 Cold War names -- 15.5% of the corpus -- contain an **asterisk**, almost all under
`twc/*` (228,797) and `tw/*` (15,854). `data/prefixes.txt` holds 15 entries containing one. No
generator here emits `*` at all, so every one of those names is unreachable by construction.
Whether they are worth reaching is a separate question -- many carry a `.map_<26 base32>` tail
that is a hash of the thing itself, in the manner of `xmodelmesh` -- but the ones shaped like
`twc/*464n_48n` are ordinary names and are not.
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


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--audit", action="store_true")
    ap.add_argument("--top", type=int, default=3000)
    ap.add_argument("--max-len", type=int, default=40)
    ap.add_argument("--out", default="uncarried_begins_cw.txt")
    args = ap.parse_args()

    carried = {x.strip() for x in (ROOT / "data" / "prefixes.txt")
               .read_text(encoding="utf-8").splitlines() if x.strip()}

    names = {n.lower() for n in snapshot.table_names(*TABLES)}
    names |= {n.lower() for n in snapshot.confirmed_names()}
    names.discard("")

    begins = collections.Counter()
    for n in names:
        for i, ch in enumerate(n):
            # A beginning ends on a segment boundary, and includes the separator: a generator
            # emits `i_c_t9_` and the stem supplies the rest.
            if ch in "_/" and i + 1 <= args.max_len:
                begins[n[: i + 1]] += 1

    uncarried = {b: c for b, c in begins.items() if b not in carried}
    print(f"{len(carried)} carried, {len(begins)} in the corpus, "
          f"{len(uncarried)} uncarried heading {sum(uncarried.values())} names", file=sys.stderr)

    ranked = sorted(uncarried.items(), key=lambda kv: -kv[1])
    if args.audit:
        for b, c in ranked[:40]:
            print(f"  {c:8}  {b}")
        return

    out = ROOT / "contrib" / args.out
    out.write_text("\n".join(b for b, _ in ranked[:args.top]) + "\n", encoding="utf-8")
    print(f"{min(args.top, len(ranked))} -> contrib/{args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
