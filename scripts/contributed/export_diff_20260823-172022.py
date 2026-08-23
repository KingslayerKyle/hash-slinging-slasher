"""Read Saluki export trees from two titles and measure how each spells the same asset.

    python contrib/export_diff.py <dir-a> <dir-b>
    python contrib/export_diff.py <dir-a> <dir-b> --token woods --token mi6

A Saluki export tree is already a labelled corpus and nothing here was reading it:

    <model name>/
        _images/
            <material name>/
                <image name>.png          -- often `a&b~<decimal>.png`, two packed textures

So a pair of trees, one per title, gives the model, material and image names for the *same*
asset under two naming schemes. That is exactly the mapping every cross-title method here needs
and has been guessing at.

## What it measures

The premise being tested is that **the descriptive middle survives between titles while the
leading and trailing words change**. So for the names on each side it reports:

  - the segments shared by both titles, which are the ones a method should key on
  - the leading and trailing segments unique to each, which are what a method must strip and
    replace
  - and, when `--token` is given, the affixes that actually wrap that token on each side

The affix lists it prints are the useful output: `data/prefixes.txt` is the global Cold War
beginning list, and a mapping measured off matched pairs is far tighter than crossing everything
with everything.

## A caution the first run of this taught

Default skins are the worst possible sample. `woods_infiltration` and `mi6_infiltration` share
their only descriptor, so a template read off that pair looks far more rigid than it is, and the
descriptor vocabulary -- the thing actually wanted -- is absent by construction. Feed it
non-default skins, and more than two.
"""

import argparse
import collections
import os
import pathlib
import re
import sys

TILDE = re.compile(r"~\d+$")
SEG = re.compile(r"[_/\\.&]")


def walk(root):
    """(models, materials, images) named by an export tree's own directory layout."""
    models, materials, images = set(), set(), set()
    root = pathlib.Path(root)
    if not root.exists():
        return models, materials, images

    for model_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        models.add(model_dir.name.lower())
        img_root = model_dir / "_images"
        if not img_root.is_dir():
            continue
        for mat_dir in sorted(p for p in img_root.iterdir() if p.is_dir()):
            materials.add(mat_dir.name.lower())
            for f in mat_dir.iterdir():
                if f.is_file():
                    stem = TILDE.sub("", f.stem.lower())
                    for piece in stem.split("&"):
                        if piece.strip():
                            images.add(piece.strip())
    return models, materials, images


def segments(names):
    out = collections.Counter()
    for n in names:
        for s in SEG.split(n):
            if s:
                out[s] += 1
    return out


def affixes(names, token):
    """What wraps `token` in these names: everything before it, and everything after."""
    before, after = collections.Counter(), collections.Counter()
    for n in names:
        i = n.find(token)
        if i == -1:
            continue
        before[n[:i]] += 1
        after[n[i + len(token):]] += 1
    return before, after


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--token", action="append", default=[],
                    help="a descriptor believed shared between the titles. Repeatable")
    ap.add_argument("--top", type=int, default=25)
    args = ap.parse_args()

    a = walk(args.a)
    b = walk(args.b)
    for label, tree, path in (("A", a, args.a), ("B", b, args.b)):
        print(f"{label}  {path}")
        print(f"     {len(tree[0])} models, {len(tree[1])} materials, {len(tree[2])} images")
    if not any(a) or not any(b):
        raise SystemExit("\none of the trees held nothing -- check the paths")

    for kind, i in (("model", 0), ("material", 1), ("image", 2)):
        sa, sb = segments(a[i]), segments(b[i])
        shared = set(sa) & set(sb)
        print(f"\n--- {kind} name segments ---")
        print(f"  A only {len(set(sa)-shared):5}   shared {len(shared):5}   B only {len(set(sb)-shared):5}")
        top_shared = sorted(shared, key=lambda s: -(sa[s] + sb[s]))[:args.top]
        print(f"  shared, commonest: {top_shared}")
        print(f"  A only, commonest: {[s for s,_ in sa.most_common() if s not in shared][:args.top]}")
        print(f"  B only, commonest: {[s for s,_ in sb.most_common() if s not in shared][:args.top]}")

    for token in args.token:
        print(f"\n=== how each title wraps {token!r} ===")
        for label, tree in (("A", a), ("B", b)):
            names = tree[0] | tree[1] | tree[2]
            before, after = affixes(names, token)
            if not before and not after:
                print(f"  {label}: not present")
                continue
            print(f"  {label} before: {[x for x,_ in before.most_common(8)]}")
            print(f"  {label} after : {[x for x,_ in after.most_common(8)]}")


if __name__ == "__main__":
    main()
