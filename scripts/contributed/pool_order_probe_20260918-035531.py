"""Does the order assets sit in a snapshot carry any information about their names? No.

    python contrib/pool_order_probe.py

The idea worth one measurement: if `snapshots/<game>.ids` kept assets in the loader's slot order,
an unnamed asset's neighbours would have been loaded from the same zone, and a named neighbour
would be a family hint from the game itself rather than from the corpus -- a new source, which
is the only kind METHODS says still moves anything.

## Measured 2026-09-14: the order is id order, and the locality in it is the final byte

    BLKOPS04: 1,153,208 records, consecutive ids increasing 99.9%
    BLKOPSCW: 1,677,099 records, consecutive ids increasing 91.3%

                  mean shared prefix, adjacent named pair vs random pair
    image         18.7 vs 2.7 (BO4)    19.9 vs 2.2 (CW)
    xanim          9.1 vs 0.9          8.6 vs 0.9
    xmodel         6.2 vs 1.6          4.9 vs 0.9
    sound_asset   15.4 vs 15.4        10.0 vs 10.0   <- no locality at all

That looks like a strong seam and is not one. The snapshot is sorted by id, and two names that
differ only in their **last character** hash within a small multiple of the prime of each other
(METHODS, "The hash runs backwards for the final byte") -- ~1e12 apart in 9.2e18 -- so they sort
next to each other: `ui_icon_rank_zm_level42 | level41 | level40 | level47`. Every adjacent pair
the table shows is that. `scripts/final_byte.py` already solves that relation exactly, for all 256
bytes, so nothing about slot order is left to exploit. Sound files show no locality because their
last characters are a fixed encoding tail.

Kept as a probe so the next person who notices adjacent names in a snapshot does not build on it.
"""
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot  # noqa: E402


def shared(a, b):
    i = 0
    while i < min(len(a), len(b)) and a[i] == b[i]:
        i += 1
    return i


def main():
    mask = snapshot.ID_MASK
    names = {}
    folder = snapshot.settings.tables_csv()
    for table in sorted(os.listdir(folder)):
        if table.endswith(".csv") and "_v2" not in table:
            for n in snapshot.table_names(table[:-4]):
                names.setdefault(snapshot.fnv1a(n) & mask, n.lower())
                if "\\" in n:
                    names.setdefault(snapshot.fnv1a_nofold(n) & mask, n.lower())
    for n in snapshot.confirmed_names():
        names.setdefault(snapshot.fnv1a(n) & mask, n.lower())
        names.setdefault(snapshot.fnv1a_nofold(n) & mask, n.lower())

    random.seed(1)
    for path in snapshot.snapshots():
        snap = snapshot.read(path)
        recs = snap.records
        rising = sum(1 for a, b in zip(recs, recs[1:]) if b[0] > a[0]) / max(len(recs) - 1, 1)
        print("%s: %d records, consecutive ids increasing %.1f%%" % (snap.game, len(recs), 100 * rising))
        for pool in sorted(snapshot.IMPORTANT):
            seq = [i for i, p in recs if snap.pool_name(p) == pool]
            adjacent = [(names[a], names[b]) for a, b in zip(seq, seq[1:]) if a in names and b in names]
            named = [names[i] for i in seq if i in names]
            if not adjacent:
                continue
            rand = [(random.choice(named), random.choice(named)) for _ in adjacent]
            print("  %-12s adjacent %.1f vs random %.1f" % (
                pool,
                sum(shared(a, b) for a, b in adjacent) / len(adjacent),
                sum(shared(a, b) for a, b in rand) / len(rand)))


if __name__ == "__main__":
    main()
