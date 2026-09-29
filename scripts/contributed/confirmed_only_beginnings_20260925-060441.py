"""All-boundary endings, crossed with BEGINNINGS this project alone discovered -- the third
member of the confirmed-only family (cores done, endings done, beginnings not yet tried).

A beginning here is the leading segment up to and including the first `_` or `/`, same
convention `uncarried.py`/`redecorations.py` use. One that appears only on names this project
confirmed, never on any published name, is evidence this project's own finds carry a directory or
prefix the general search's committed `data/prefixes.txt` never had -- worth trying against every
core/ending combination the corpus can build, not just the handful of names it was first seen on.
"""
import collections
import pathlib
import sys
import argparse

ROOT = pathlib.Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").exists() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

parser = argparse.ArgumentParser()
parser.add_argument("--sound", action="store_true")
parser.add_argument("--min-names", type=int, default=3)
args = parser.parse_args()

SOUND_TABLES = ["fnv1a_xsounds", "fnv1a_xsounds_v2",
                "fnv1a_soundbanks_aliases", "fnv1a_soundbanks_aliases_v2"]
GENERAL_TABLES = ["fnv1a_xmaterials", "fnv1a_xmaterials_v2", "fnv1a_ximages", "fnv1a_ximages_v2",
                  "fnv1a_xmodels", "fnv1a_xanims", "fnv1a_xanims_v2"]

published = snapshot.table_names(*(SOUND_TABLES if args.sound else GENERAL_TABLES))
confirmed = snapshot.confirmed_names()


def leading_segment(name):
    cut = len(name)
    for delimiter in ("/", "_"):
        position = name.find(delimiter)
        if position != -1:
            cut = min(cut, position + 1)
    return name[:cut] if cut < len(name) else ""


published_beginnings = set()
for name in published:
    b = leading_segment(name)
    if b:
        published_beginnings.add(b)

confirmed_counted = collections.Counter()
for name in confirmed:
    b = leading_segment(name)
    if not b or b in published_beginnings:
        continue
    confirmed_counted[b] += 1

beginnings = [b for b, n in confirmed_counted.items() if n >= args.min_names]

stem = "sound_" if args.sound else ""
begins_path = ROOT / "contrib" / f"confirmedonly_begins_{stem}.txt"
begins_path.write_text(chr(10).join(beginnings) + chr(10), encoding="utf-8")
print(f"{len(confirmed_counted)} beginnings appear only on confirmed names, "
      f"{len(beginnings)} with >= {args.min_names} names, "
      f"heading {sum(n for b, n in confirmed_counted.items() if n >= args.min_names)} confirmed names",
      file=sys.stderr)
print(f"wrote {begins_path.name}", file=sys.stderr)
