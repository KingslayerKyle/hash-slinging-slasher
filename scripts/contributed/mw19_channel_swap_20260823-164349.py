"""Strip Modern Warfare 2019's channel code off an image name, so Cold War's can go on instead.

    python contrib/mw19_channel_swap.py --audit    the channel vocabulary, measured
    python contrib/mw19_channel_swap.py            write the stems

## The observation

Modern Warfare 2019 packs textures into colour channels and names the packed asset after every
texture in it, joined by `&` (see `snapshot.unpack`). Splitting those gives 211,306 individual
image names, and the last segment of almost all of them is a **channel code** saying which map
it is. Measured off the corpus rather than assumed:

    _c  56,049    _g  47,371    _n  46,870    _s  40,644    _o  3,083    _u  1,630
    _r1  995      _col  917     _r2  907      _r  901       _nml  817    _cos  731
    _spc  457     _mask  335    _r3  260      _m  247

191,017 of the 211,306 end in one of the top five alone.

## Why that is a method rather than a curiosity

The channel code is the *only* part of these names that is about the file format. Everything in
front of it is the asset -- the character, the weapon, the variant. Cold War holds the same
assets and decorates them its own way, so the stem is the shared thing and the code is not.

So: cut the channel code off, and let the engine put **every ending Cold War is measured to
use** back on, under every beginning it uses. That reaches the same asset spelled Cold War's way
rather than Modern Warfare's, which the verbatim pass by construction cannot.

The stems this writes are deliberately *not* filtered to names whose code is one of the common
five. A name ending `_mask` or `_r2` has the same shape and the same argument applies; guessing
which codes count is the mistake that lost the packed names in the first place.
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

# How long a last segment can be and still plausibly be a channel code rather than a word. `_mask`
# and `_nml` are codes; `_infiltration` is part of the asset's name. Measured off the corpus: every
# code in the top twenty is four characters or fewer.
MAX_CODE = 4


def packed_names():
    out = set()
    for _pool, name in snapshot.name_corpus("modwar19"):
        if "&" not in name:
            continue
        for piece in snapshot.unpack(name):
            piece = piece.strip().lower()
            if piece:
                out.add(piece)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--audit", action="store_true",
                        help="print the measured channel vocabulary and stop")
    parser.add_argument("--max-code", type=int, default=MAX_CODE)
    parser.add_argument("--min-stem", type=int, default=8)
    parser.add_argument("--out", default="mw19_swap_stems.txt")
    args = parser.parse_args()

    names = packed_names()
    codes = collections.Counter()
    stems = set()

    for name in names:
        stem, sep, code = name.rpartition("_")
        if not sep or not stem:
            continue
        if len(code) > args.max_code:
            continue
        codes[code] += 1
        if len(stem) >= args.min_stem:
            # The stem with its separator gone; the engine supplies the ending, `_` included.
            stems.add(stem)

    if args.audit:
        print(f"{len(names)} packed-channel names")
        print(f"{len(codes)} distinct channel codes at <= {args.max_code} characters\n")
        for code, count in codes.most_common(25):
            print(f"  {count:7}  _{code}")
        print(f"\nstems that would be written: {len(stems)}")
        return

    out = ROOT / "contrib" / args.out
    out.write_text("\n".join(sorted(stems)) + "\n", encoding="utf-8")
    print(f"{len(names)} packed names -> {len(stems)} stems, "
          f"{len(codes)} channel codes seen", file=sys.stderr)
    print(f"-> contrib/{args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
