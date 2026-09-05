#!/usr/bin/env python3
"""Cross-generation tag transposition expanding p7, p8, p9, t7, t8, t9.

Includes Black Ops 3 legacy tags (p7, t7) mapped to Black Ops 4 (p8, t8) and Cold War (p9, t9),
plus bi-directional transposition between BO4 and Cold War.
"""
import os
import re
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_root, "scripts"))
import snapshot

TRANSFORMS = [
    # P7 -> P8, P7 -> P9
    (re.compile(r"(^|[/_])p7([/_])"), r"\g<1>p8\g<2>"),
    (re.compile(r"(^|[/_])p7([/_])"), r"\g<1>p9\g<2>"),
    # T7 -> T8, T7 -> T9
    (re.compile(r"(^|[/_])t7([/_])"), r"\g<1>t8\g<2>"),
    (re.compile(r"(^|[/_])t7([/_])"), r"\g<1>t9\g<2>"),
    # T8 <-> T9
    (re.compile(r"(^|[/_])t8([/_])"), r"\g<1>t9\g<2>"),
    (re.compile(r"(^|[/_])t9([/_])"), r"\g<1>t8\g<2>"),
    # P8 <-> P9
    (re.compile(r"(^|[/_])p8([/_])"), r"\g<1>p9\g<2>"),
    (re.compile(r"(^|[/_])p9([/_])"), r"\g<1>p8\g<2>"),
]

def main():
    known = set()
    for table in ["fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims"]:
        known.update(snapshot.table_names(table))
    for pool in ["xmodel", "material", "image", "xanim"]:
        known.update(snapshot.confirmed_names(pool))

    candidates = set()
    for name in known:
        name = name.strip().lower().replace("\\", "/")
        for pattern, replacement in TRANSFORMS:
            if pattern.search(name):
                new_name = pattern.sub(replacement, name)
                if new_name != name and new_name not in known:
                    candidates.add(new_name)

    for cand in sorted(candidates):
        sys.stdout.write(cand + "\n")

    sys.stderr.write(
        f"Generated {len(candidates):,} cross-generation tag candidates from {len(known):,} seeds.\n"
    )

if __name__ == "__main__":
    main()
