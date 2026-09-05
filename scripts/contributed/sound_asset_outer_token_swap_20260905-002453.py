"""Swap the outer underscore tokens of verified sound-asset basenames.

The directory and dotted recording tail stay fixed.  BO4 paths retain their
native backslashes; Cold War paths use the normal folded spelling.
"""
import argparse
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot


def seed_names(game):
    snap = snapshot.read(os.path.join(ROOT, "snapshots", game.lower() + ".ids"))
    wanted = {aid for aid, pool in snap.records
              if snap.pool_name(pool) == "sound_asset"}
    nofold = game == "BLKOPS04"
    result = set()
    for path in glob.glob(os.path.join(ROOT, "cod-name-db", "csv", "*xsounds*.csv")):
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                _, _, value = line.partition(",")
                value = value.strip()
                if not value:
                    continue
                spelling = value.lower().replace("/", "\\") if nofold else value.lower().replace("\\", "/")
                hasher = snapshot.fnv1a_nofold if nofold else snapshot.fnv1a
                if hasher(spelling) & snapshot.ID_MASK in wanted:
                    result.add(spelling)
    for value in snapshot.confirmed_names("sound_asset"):
        spelling = value.strip().lower()
        spelling = spelling.replace("/", "\\") if nofold else spelling.replace("\\", "/")
        if hasher(spelling) & snapshot.ID_MASK in wanted:
            result.add(spelling)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", required=True, choices=("BLKOPS04", "BLKOPSCW"))
    args = parser.parse_args()
    seeds = seed_names(args.game)
    output = set()
    for value in seeds:
        cut = max(value.rfind("/"), value.rfind("\\")) + 1
        head, base = value[:cut], value[cut:]
        dot = base.find(".")
        if dot <= 0:
            continue
        core, tail = base[:dot], base[dot:]
        tokens = core.split("_")
        if len(tokens) < 2 or not tokens[0] or not tokens[-1]:
            continue
        tokens[0], tokens[-1] = tokens[-1], tokens[0]
        candidate = head + "_".join(tokens) + tail
        if candidate != value:
            output.add(candidate)
    print("%s: %d seeds, %d outer-token candidates" %
          (args.game, len(seeds), len(output)), file=sys.stderr)
    print("\n".join(sorted(output)))


if __name__ == "__main__":
    main()
