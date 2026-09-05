"""Solve exact three-digit terminal variants for sound_asset names.

The stem is required to be an already verified sound-file name with its last
three bytes removed; only the terminal decimal triplet is synthesized.  This
is deliberately narrower than a general suffix cross-product.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import snapshot

MASK = (1 << 64) - 1
PRIME = 0x100000001B3
INV = pow(PRIME, -1, 1 << 64)


def undo(h, byte):
    return ((h * INV) ^ byte) & MASK


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--no-fold", action="store_true")
    args = ap.parse_args()
    snap = next(snapshot.read(p) for p in snapshot.snapshots()
                if args.game.lower() in os.path.basename(p).lower())
    hasher = snapshot.fnv1a_nofold if args.no_fold else snapshot.fnv1a
    known = set(snapshot.table_names("fnv1a_xsounds"))
    known.update(snapshot.confirmed_names("sound_asset"))
    stems = {}
    for seed in known:
        seed = seed.strip().lower()
        if len(seed) < 4:
            continue
        stem = seed[:-3]
        stems.setdefault(hasher(stem), []).append(stem)
    wanted = [i for i, p in snap.records if snap.pool_name(p) == "sound_asset"]
    found = set()
    for target in wanted:
        for number in range(1000):
            suffix = f"{number:03d}"
            h = target
            for byte in reversed(suffix.encode("ascii")):
                h = undo(h, byte)
            for stem in stems.get(h, ()):
                candidate = stem + suffix
                if hasher(candidate) == target:
                    found.add(candidate)
    print(f"{args.game}: {len(known):,} seeds, {len(wanted):,} targets, "
          f"{len(found):,} exact candidates", file=sys.stderr)
    print("\n".join(sorted(found)))


if __name__ == "__main__":
    main()
