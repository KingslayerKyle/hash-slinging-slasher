"""Solve a bounded BO4 sound-alias four-byte suffix by FNV meet-in-the-middle."""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import snapshot

MASK = (1 << 64) - 1
TOP = 1 << 63
PRIME = 0x100000001B3
INVERSE = pow(PRIME, -1, 1 << 64)


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", required=True, choices=("BLKOPS04", "BLKOPSCW"))
    parser.add_argument("--seeds", type=int, default=1000)
    options = parser.parse_args(argv)
    path = next(p for p in snapshot.snapshots()
                if snapshot.read(p).game.lower() == options.game.lower())
    seeds = sorted(set(snapshot.table_names("fnv1a_soundbanks_aliases")) |
                   set(snapshot.confirmed_names("sound_alias")))
    seeds = [s.strip().lower() for s in seeds if len(s.strip()) >= 5][:options.seeds]
    alphabet = tuple(sorted({ord(ch) for seed in seeds for ch in seed
                             if 0x20 <= ord(ch) < 0x7F}))

    # State after the first two suffix bytes -> (seed prefix, two-byte text).
    forward = {}
    for seed in seeds:
        prefix = seed[:-4]
        base = snapshot.fnv1a(prefix)
        for first in alphabet:
            h = ((base ^ first) * PRIME) & MASK
            for second in alphabet:
                state = ((h ^ second) * PRIME) & MASK
                forward.setdefault(state, []).append((prefix, first, second))

    known = snapshot.known_hashes()
    targets = [aid for aid, pool in snapshot.read(path).unnamed(known).items()
               if pool == "sound_alias"]
    found = set()
    for target0 in targets:
        for target in (target0, target0 | TOP):
            scaled = (target * INVERSE) & MASK
            for fourth in alphabet:
                state3 = (scaled ^ fourth) * INVERSE & MASK
                for third in alphabet:
                    state2 = (state3 ^ third) * INVERSE & MASK
                    for prefix, first, second in forward.get(state2, ()):
                        candidate = prefix + chr(first) + chr(second) + chr(third) + chr(fourth)
                        if snapshot.fnv1a(candidate) == target:
                            found.add(candidate)

    print(f"{len(seeds):,} seeds, {len(targets):,} unnamed sound_alias ids -> "
          f"{len(found):,} exact four-byte candidates", file=sys.stderr)
    for candidate in sorted(found):
        print(candidate)


if __name__ == "__main__":
    main(sys.argv[1:])
