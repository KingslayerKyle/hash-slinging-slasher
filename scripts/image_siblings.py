"""Every image a known material implies, under each measured image prefix and channel ending.

A method, not a report. Pipe it into `confirm_list`.

    python scripts/image_siblings.py | bin\\windows\\confirm_list.exe - ^
        --label "image siblings of confirmed materials" --script scripts/image_siblings.py

## Why this file is in `scripts/` and not `contrib/`

`derive_closure.py` has named this derivation first in its round since it was written -- "the
strongest measured cross-type seam: 15,770 shared cores, 12.8% of image's" -- but its entry
pointed at `contrib/image_siblings.py`, and `contrib/` is gitignored. So the only clone that ever
ran it was the one that happened to hold that staging file. Every other contributor's closure
printed `skipped: contrib/image_siblings.py is not here` in a seven-line round summary and carried
on, which is why the top of the snowball has looked quieter than the seam it is built on.

This is the generator that seam needs, promoted from the copy `submit` already carries in the
pull-request library as `scripts/contributed/image_siblings_wide_20260902-120635.py`.

## How it generates

For each material name -- confirmed on this machine plus every published one: drop the directory,
drop one leading image/material prefix, drop one trailing channel ending if it carries a common one.
What is left is the core an image would share. Offer that core under every prefix and every ending
measured from the published image tables, and skip anything the tables already name.

The prefix and ending lists are the 2026-09-02 measurement, kept verbatim so a re-run is comparable
with the registry rows that measurement produced. `scripts/seams.py` re-measures the relation itself
and `derive_lists.py` re-measures what the committed lists carry; neither re-measures these two
lists, and changing them changes what this reaches.

`--game` is accepted and ignored, like the other derivations that build vocabulary from every
capture: the candidates come from materials of all games, and the game being solved is
`confirm_list`'s business.
"""
import argparse
import os
import sys

_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _root)

import snapshot

# Top image endings measured across fnv1a_ximages + the confirmed image corpus.
SUFFIXES = [
    "", "_c", "_n", "_g", "_o", "_m", "_s", "_r", "_e", "_col", "_nml",
    "_icon", "_large", "_spc", "_gls", "_ao", "_d", "_h", "_a", "_mask",
    "_small", "_thermalmap", "_cm", "_v2", "_normal", "_depth", "_albedo",
    "_specular", "_cos", "_geo", "_render", "_xl", "_sm", "_swatch", "_dmg",
]

# Top image prefixes measured across fnv1a_ximages.
PREFIXES = [
    "i_", "", "mtl_", "i_c_", "i_t8_", "i_t9_", "i_mtl_", "ui_", "uie_",
    "i_p8_", "i_p9_", "i_vm_", "i_wpn_", "i_weap_",
]

STRIP = ["mtl_", "i_", "i_c_", "i_t8_", "i_t9_", "i_mtl_"]


def core(name):
    """A material name reduced to the part an image would share with it."""
    _, _, rest = name.rpartition("/")
    for lead in STRIP:
        if rest.startswith(lead):
            rest = rest[len(lead):]
            break
    if rest.endswith(("_c", "_n", "_m", "_s")):
        rest = rest[:-2]
    return rest.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", help="accepted and ignored -- see the module docstring")
    parser.parse_args()

    materials = set(snapshot.confirmed_names("material")) | set(snapshot.table_names("fnv1a_xmaterials"))
    known = set()
    for table in ("fnv1a_ximages", "fnv1a_ximages_v2"):
        known |= {n.strip().lower().replace("\\", "/") for n in snapshot.table_names(table)}
    known |= {n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names("image")}

    cores = {c for c in (core(n) for n in materials) if len(c) >= 3}

    seen = set()
    for core_name in sorted(cores):
        for prefix in PREFIXES:
            for suffix in SUFFIXES:
                candidate = prefix + core_name + suffix
                if candidate not in known and candidate not in seen:
                    seen.add(candidate)
                    print(candidate)


if __name__ == "__main__":
    main()
