"""The individual image names hidden inside Modern Warfare 2019's packed-channel names.

    python contrib/mw19_channel_parts.py              print the parts
    python contrib/mw19_channel_parts.py --stats      what is in them, confirm nothing
    python contrib/mw19_channel_parts.py --prefix i_  print them wearing a prefix too

## What these are

Modern Warfare 2019 packs several textures into one image by using its colour channels: colour
and specular share a file, normal and gloss and occlusion share another. The loader holds one
asset for the packed file, and its name is **every packed texture's name joined by `&`**, with a
disambiguating `~<decimal>` on the end:

    c_t9_zmb_ndu_zombie_jacket_n&c_t9_zmb_ndu_zombie_jacket_green_g~13414439723048909555

That is not one name and it is not junk. It is two real image names:

    c_t9_zmb_ndu_zombie_jacket_n
    c_t9_zmb_ndu_zombie_jacket_green_g

The first capture of this corpus threw all 121,538 of these away as dump artefacts. They hold
**211,847 distinct names, 211,306 of which appear nowhere else in the corpus** -- 99.7% -- and
57,149 of them mention `t9`, Treyarch's Cold War codename. Discarding them discarded the single
most Cold-War-dense part of the whole capture.

## Why they are worth confirming rather than only harvesting

These are already exactly the shape Cold War uses -- `c_`, `_n`, `_g`, `_c` and the rest -- so
unlike the rest of this corpus they are worth trying close to verbatim. Cold War frequently wears
the same name with `i_` in front of it, which is why `--prefix` exists and why the plan built on
this crosses them with the measured beginning and ending lists as well.
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").exists() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))

import snapshot

# The disambiguator Cordycep appends when it merges the packed textures into one entry.
TILDE = re.compile(r"~\d+$")


def parts():
    """Every individual name packed inside a `&` entry, and every plain name for comparison."""
    packed, plain = set(), set()
    entries = 0
    for _pool, name in snapshot.name_corpus("modwar19"):
        name = name.strip().lower()
        if "&" in name:
            entries += 1
            for piece in TILDE.sub("", name).split("&"):
                piece = piece.strip()
                if piece:
                    packed.add(piece)
        elif name:
            plain.add(TILDE.sub("", name))
    return packed, plain, entries


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--stats", action="store_true")
    parser.add_argument("--prefix", action="append", default=[],
                        help="also print every part wearing this prefix. Repeatable. "
                             "Cold War often carries these names with `i_` in front")
    parser.add_argument("--only-new", action="store_true", default=True,
                        help="skip parts that already appear as a plain name in the corpus")
    args = parser.parse_args()

    packed, plain, entries = parts()
    wanted = sorted(packed - plain if args.only_new else packed)

    if args.stats:
        print(f"packed entries            {entries}")
        print(f"distinct names inside     {len(packed)}")
        print(f"plain names in the corpus {len(plain)}")
        print(f"not present as plain      {len(packed - plain)}")
        print(f"  of those mentioning t9  {sum(1 for p in packed - plain if 't9' in p)}")
        return

    for name in wanted:
        print(name)
        for prefix in args.prefix:
            print(prefix + name)


if __name__ == "__main__":
    main()
