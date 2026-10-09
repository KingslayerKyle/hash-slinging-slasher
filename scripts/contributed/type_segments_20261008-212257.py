"""Per-type segment plan lists: every underscore-prefix of every known name of one type, and the
1-3 segment endings that type's names carry. The generalisation of alias_segments.py, which
returned ~43,000 BO6/BO7 aliases in its first two rounds.

Stems and endings are measured per type because the vocabularies do not mix: an image ends
`_thermalmap`, `_swatch`, `_backplate`; a material is `<dir>/<base>` and keeps its directory in
the stem; an animation ends `_in`, `_loop`, `_out`. Writes contrib/seg_<kind>_{stems,ends}.txt and
contrib/seg_<kind>.plan.txt.

    python contrib/type_segments.py --kind image --ends 3000
    confirm_plan contrib/seg_image.plan.txt --game BLACKOP7
"""
from pathlib import Path
import argparse
import collections
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
CONTRIB = ROOT / "contrib"
TABLES = {"image": "fnv1a_ximages*.csv", "material": "fnv1a_xmaterials*.csv",
          "xanim": "fnv1a_xanims*.csv", "sound_alias": "fnv1a_soundbanks_aliases*.csv"}


def known(kind):
    for f in sorted((ROOT / "cod-name-db" / "csv").glob(TABLES[kind])):
        for line in f.open(encoding="utf-8", errors="replace"):
            yield line.rstrip("\r\n").partition(",")[2].lower()
    for top in ("all_names", "submissions", "findings"):
        for f in sorted((ROOT / top).rglob(kind + "*.txt")):
            for line in f.open(encoding="utf-8", errors="replace"):
                key, sep, name = line.rstrip("\r\n").partition(",")
                if sep:
                    yield name.lower()


def main():
    CONTRIB.mkdir(parents=True, exist_ok=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", required=True, choices=sorted(TABLES))
    ap.add_argument("--ends", type=int, default=3000)
    ap.add_argument("--min-stem", type=int, default=4)
    a = ap.parse_args()
    stems, ends = set(), collections.Counter()
    for name in set(known(a.kind)):
        if not name or "~" in name or "&" in name or name.startswith("twc/") or "." in name:
            continue
        head, slash, tail = name.rpartition("/")
        parts = tail.split("_")
        lead = head + slash
        for n in range(1, len(parts)):
            stem = lead + "_".join(parts[:n])
            if len(stem) >= a.min_stem:
                stems.add(stem)
        for k in range(1, min(3, len(parts) - 1) + 1):
            ends["_" + "_".join(parts[-k:])] += 1
    top = [e for e, _ in ends.most_common(a.ends)]
    s, e = CONTRIB / f"seg_{a.kind}_stems.txt", CONTRIB / f"seg_{a.kind}_ends.txt"
    s.write_text("".join(x + "\n" for x in sorted(stems)), encoding="utf-8")
    e.write_text("".join(x + "\n" for x in top), encoding="utf-8")
    (CONTRIB / f"seg_{a.kind}.plan.txt").write_text(
        f"label: {a.kind} segment plan -- {a.kind} stems x measured {a.kind} endings\n"
        f"describe: every underscore-prefix of every known {a.kind} name, crossed with the top "
        f"{len(top)} 1-3 segment endings {a.kind} names carry; see contrib/type_segments.py\n"
        f"stem: @contrib/{s.name}\nend: @contrib/{e.name}\n", encoding="utf-8")
    print(f"{a.kind}: {len(stems)} stems, {len(top)} endings", file=sys.stderr)


if __name__ == "__main__":
    main()
