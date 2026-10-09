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


SEED_DIRS = []
CRLF = chr(13) + chr(10)


def known(kind):
    for d in SEED_DIRS:
        for f in sorted(Path(d).rglob("*" + kind + "*.txt")):
            for line in f.open(encoding="utf-8", errors="replace"):
                key, sep, name = line.rstrip(CRLF).partition(",")
                if sep:
                    yield name.lower()
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", required=True, choices=sorted(TABLES))
    ap.add_argument("--ends", type=int, default=3000)
    ap.add_argument("--min-stem", type=int, default=4)
    ap.add_argument("--heads", action="store_true",
                    help="mirror: top 1-2 segment beginnings x every known remainder")
    ap.add_argument("--all-cuts", action="store_true",
                    help="cut at letter/digit boundaries too (method 25's all-boundary cut), "
                         "so `mpapa5` and `v10` split; writes seg_<kind>_ab_* files")
    ap.add_argument("--seed-dir", action="append", default=[],
                    help="extra folder of hash,name files (e.g. open pull requests' names) to seed from")
    a = ap.parse_args()
    SEED_DIRS.extend(a.seed_dir)
    if a.heads:
        return heads(a)
    if a.all_cuts:
        return all_cuts(a)
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


def cuts(tail):
    """Every cut point: before each `_`, and at each letter/digit transition."""
    for i in range(1, len(tail)):
        if tail[i] == "_" or (tail[i - 1].isdigit() != tail[i].isdigit()
                              and tail[i - 1] != "_" and tail[i] != "_"):
            yield i


def all_cuts(a):
    stems, ends = set(), collections.Counter()
    for name in set(known(a.kind)):
        if not name or "~" in name or "&" in name or name.startswith("twc/") or "." in name:
            continue
        head, slash, tail = name.rpartition("/")
        lead = head + slash
        for i in cuts(tail):
            stem, end = lead + tail[:i], tail[i:]
            if len(stem) >= a.min_stem:
                stems.add(stem)
            if end.count("_") <= 3:
                ends[end] += 1
    top = [e for e, _ in ends.most_common(a.ends)]
    s, e = CONTRIB / f"seg_{a.kind}_ab_stems.txt", CONTRIB / f"seg_{a.kind}_ab_ends.txt"
    s.write_text("".join(x + "\n" for x in sorted(stems)), encoding="utf-8")
    e.write_text("".join(x + "\n" for x in top), encoding="utf-8")
    (CONTRIB / f"seg_{a.kind}_ab.plan.txt").write_text(
        f"label: {a.kind} all-boundary segment plan -- cut at underscores and letter/digit edges\n"
        f"describe: every known {a.kind} name cut at every underscore and letter/digit boundary; "
        f"stems x the top {len(top)} endings; see contrib/type_segments.py --all-cuts\n"
        f"stem: @contrib/{s.name}\nend: @contrib/{e.name}\n", encoding="utf-8")
    print(f"{a.kind} all-cuts: {len(stems)} stems, {len(top)} endings", file=sys.stderr)


def heads(a):
    """`cer_ui_emblem_168` -> head `cer_ui` + rest `_emblem_168`; every head x every rest."""
    begins, rests = collections.Counter(), set()
    for name in set(known(a.kind)):
        if not name or "~" in name or "&" in name or name.startswith("twc/") or "." in name:
            continue
        head, slash, tail = name.rpartition("/")
        parts = tail.split("_")
        for k in range(1, min(2, len(parts) - 1) + 1):
            begins[head + slash + "_".join(parts[:k])] += 1
            rests.add("_" + "_".join(parts[k:]))
    top = [b for b, _ in begins.most_common(a.ends)]
    b, r = CONTRIB / f"head_{a.kind}_begins.txt", CONTRIB / f"head_{a.kind}_rests.txt"
    b.write_text("".join(x + "\n" for x in top), encoding="utf-8")
    r.write_text("".join(x + "\n" for x in sorted(rests)), encoding="utf-8")
    # The heads go in as stems and the remainders as endings: the same bare-beginning shape as
    # the segment plan, which the engine peels from the ending side.
    (CONTRIB / f"head_{a.kind}.plan.txt").write_text(
        f"label: {a.kind} head swap -- measured {a.kind} beginnings x every known remainder\n"
        f"describe: top {len(top)} 1-2 segment beginnings of known {a.kind} names, crossed with every "
        f"remainder a known {a.kind} name leaves after its first 1-2 segments; see contrib/type_segments.py --heads\n"
        f"stem: @contrib/{b.name}\nend: @contrib/{r.name}\n", encoding="utf-8")
    print(f"{a.kind} heads: {len(top)} begins, {len(rests)} rests", file=sys.stderr)


if __name__ == "__main__":
    main()
