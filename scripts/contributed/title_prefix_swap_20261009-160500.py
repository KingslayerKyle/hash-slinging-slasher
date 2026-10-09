"""Names re-issued under another title's codename prefix, or with it added or dropped.

Modern content is carried from title to title and re-prefixed on the way: BO7 holds
`ui_playercard_138`, `cer_ui_playercard_552` and `jup_playercard_...` side by side, and 7,634 /
6,992 / 3,937 of its named images start `jup_` / `sat_` / `cer_`. Every known name of the kind is
offered with its leading codename swapped for every other, removed, or (when it has none) added.
`slot_swap` cannot reach this: its fixed beginning is at least one token, so the first token never
varies.

    python contrib/title_prefix_swap.py --kind image

Spent by: the corpus of the kind as it stands; re-run after it grows.
"""
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parent.parent
TABLES = {"image": "fnv1a_ximages*.csv", "material": "fnv1a_xmaterials*.csv",
          "sound_alias": "fnv1a_soundbanks_aliases*.csv", "xanim": "fnv1a_xanims*.csv"}
CODES = ["jup", "sat", "cer", "saw", "iw9", "iw8", "t10", "t9", "s6", "s4", "mp", "zm", "wz",
         "br", "sp", "cp", "mtl", "veh9", "veh8", "sgon", "ee"]


def names(kind):
    srcs = list((ROOT / "cod-name-db" / "csv").glob(TABLES[kind]))
    for folder in ("findings", "submissions"):
        srcs += list((ROOT / folder).rglob(f"{kind}*.txt"))
    for p in srcs:
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            k, sep, v = line.partition(",")
            v = (v if sep else k).strip().lower()
            if v and "~" not in v and "," not in v:
                yield v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", default="image")
    a = ap.parse_args()
    known = set(names(a.kind))
    out = set()
    for n in known:
        d, slash, rest = n.rpartition("/")
        head = d + slash
        first, _, tail = rest.partition("_")
        bodies = [tail] if first in CODES and tail else []
        bodies.append(rest)
        for body in bodies:
            out.add(head + body)
            for c in CODES:
                out.add(f"{head}{c}_{body}")
    out -= known
    sys.stdout.write("\n".join(sorted(out)) + "\n")
    print(f"{len(known):,} names, {len(out):,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
