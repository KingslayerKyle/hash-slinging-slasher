"""Candidate names read out of an installed Call of Duty: Modern Warfare III build.

    python scripts/contributed/harvest_mwiii_fastfiles_20261013-162139.py --folder "<install>/cod23" > logs/mwiii_candidates.txt

Reads:  <install>/cod23/*.ff   -- the shipped fast-file names, which are asset names.
Writes: candidate names on standard output, one per line.

METHODS.md's build-harvest section records that Black Ops 4's shipped containers are the
second-best source ever measured here (1 name per 305 strings). Modern Warfare III's own
containers were never surveyed. The payload of these `.ff` files is packed -- measured
7.98 bits/byte of entropy, no zlib stream at any header offset, and four ASCII runs >= 8
characters across the first 8 MB of each of six sampled files, two of which are the
filename repeated. So the file *names* are the whole harvest, and that is this script.
"""
import argparse
import glob
import os
import sys




def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--folder", required=True, help="explicit cod23 fast-file directory")
    args = parser.parse_args()
    if not os.path.isdir(args.folder):
        parser.error("--folder must be an existing directory")
    paths = sorted(glob.glob(os.path.join(args.folder, "*.ff")))
    print("fast files: %d" % len(paths), file=sys.stderr)

    seen = set()
    for path in paths:
        name = os.path.splitext(os.path.basename(path))[0].strip().lower()
        if not name:
            continue
        # The streaming suffix is on 14,468 of the 15,064. The name with it is a real
        # string the build ships; the name without it is the asset the stream belongs to.
        # Both are candidates -- the hash decides which is real.
        for candidate in (name, name[:-3] if name.endswith("_tr") else None):
            if candidate and candidate not in seen:
                seen.add(candidate)
                print(candidate)

    print("candidates: %d" % len(seen), file=sys.stderr)


if __name__ == "__main__":
    main()
