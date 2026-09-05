"""Interior character substitutions for a later BO4 SAB sound-asset seed slice."""
import argparse
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot

START, LIMIT = 29, 223
ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz_-"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--size", action="store_true")
    args = ap.parse_args()
    snap = next(snapshot.read(path) for path in snapshot.snapshots()
                if snapshot.read(path).game.lower() == "blkops04")
    wanted = {aid for aid, pool in snap.records
              if snap.pool_name(pool) == "sound_asset"}
    hasher = snapshot.fnv1a_nofold
    names = set()
    for table in glob.glob(os.path.join(ROOT, "cod-name-db", "csv", "*xsounds*.csv")):
        with open(table, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                _, _, name = line.partition(",")
                name = name.strip()
                if name and hasher(name) & snapshot.ID_MASK in wanted:
                    names.add(name.lower().replace("/", "\\"))
    found = os.path.join(ROOT, "findings", "blkops04", "sound_asset.txt")
    if os.path.exists(found):
        with open(found, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                _, _, name = line.partition(",")
                if name.strip():
                    names.add(name.strip().lower().replace("/", "\\"))
    for name in snapshot.confirmed_names("sound_asset"):
        normalized = name.strip().lower().replace("/", "\\")
        if normalized and hasher(normalized) & snapshot.ID_MASK in wanted:
            names.add(normalized)
    seeds = sorted(name.strip() for name in names if name.strip())[START:START + LIMIT]
    emitted = 0
    for name in seeds:
        cut = max(name.rfind("/"), name.rfind("\\")) + 1
        head, base = name[:cut], name[cut:]
        dot = base.find(".")
        if dot <= 0:
            continue
        core, tail = base[:dot], base[dot:]
        for index, old in enumerate(core[:-4]):
            for char in ALPHABET:
                if char != old:
                    emitted += 1
                    if not args.size:
                        print(head + core[:index] + char + core[index + 1:] + tail)
    print(f"BLKOPS04: seeds {START + 1}-{START + len(seeds)}, {len(seeds)} seeds, "
          f"{emitted:,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
