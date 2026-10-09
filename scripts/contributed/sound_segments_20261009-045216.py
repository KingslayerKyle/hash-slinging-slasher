"""Modern sound-file segment plan: every underscore-prefix of every known modern sound file,
crossed with the 1-3 segment endings those files carry -- the ending keeps its format tail
(`_04.tnn.85.48000.all`), so a stem only meets tails real files of that shape wear.

The same shape as contrib/type_segments.py, which never covered sound files: until 2026-10-09
modern searches did not hunt the `sndasset` pool at all (the config matcher compared the
canonical config name against the raw pool-map name, so `sound_asset` never resolved).

    python contrib/sound_segments.py --ends 12000
    confirm_plan contrib/seg_sound_asset.plan.txt --game BLACKOP6

`--heads` writes the mirror (top 1-2 segment beginnings x every known remainder+tail).
`--dots` spells directories with `.` (MWII/MWIII hash `iw9.dst.x_03.ln.75.48000.all`, not the
`/` display path the table stores) and writes `*_dots*` files; BO6/BO7 hash the `/` spelling.
"""
from pathlib import Path
import argparse
import collections
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
CONTRIB = ROOT / "contrib"
MODERN = ("blackop6", "blackop7", "yamyamok", "modwar22", "modwar7")


def known():
    for f in sorted((ROOT / "cod-name-db" / "csv").glob("fnv1a_xsounds_v2*.csv")):
        for line in f.open(encoding="utf-8", errors="replace"):
            yield line.rstrip("\r\n").partition(",")[2].lower()
    for top in ("all_names", "findings"):
        for game in MODERN:
            for f in sorted((ROOT / top / game).rglob("sound_asset*.txt")):
                for line in f.open(encoding="utf-8", errors="replace"):
                    key, sep, name = line.rstrip("\r\n").partition(",")
                    if sep:
                        yield name.lower()
    for f in sorted((ROOT / "submissions").rglob("sound_asset*.txt")):
        if not any(g.upper() in str(f).upper() for g in MODERN):
            continue
        for line in f.open(encoding="utf-8", errors="replace"):
            key, sep, name = line.rstrip("\r\n").partition(",")
            if sep:
                yield name.lower()


SFX = ""


def split(name):
    """`core/fly/x/step_land_04.ln.75.48000.all` -> (`core/fly/x/`, [step, land, 04], `.ln...`).
    With dotted directories the tail is the last four dot fields (`.ln.75.48000.all`)."""
    if "/" not in name:
        f = name.split(".")
        if len(f) < 6:
            return None
        lead, base, tail = ".".join(f[:-5]) + ".", f[-5], "." + ".".join(f[-4:])
        return lead, base.split("_"), tail
    head, slash, base = name.rpartition("/")
    stem, dot, tail = base.partition(".")
    if not dot or not stem:
        return None
    return head + slash, stem.split("_"), dot + tail


def main():
    CONTRIB.mkdir(parents=True, exist_ok=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--ends", type=int, default=12000)
    ap.add_argument("--min-stem", type=int, default=4)
    ap.add_argument("--heads", action="store_true")
    ap.add_argument("--dots", action="store_true")
    a = ap.parse_args()
    names = {n for n in known() if n}
    if a.dots:
        names = {n.replace("/", ".") for n in names}
    global SFX
    SFX = "_dots" if a.dots else ""
    if a.heads:
        return heads(a, names)
    stems, ends = set(), collections.Counter()
    for name in names:
        s = split(name)
        if not s:
            continue
        lead, parts, tail = s
        for n in range(1, len(parts)):
            stem = lead + "_".join(parts[:n])
            if len(stem) >= a.min_stem:
                stems.add(stem)
        for k in range(1, min(3, len(parts) - 1) + 1):
            ends["_" + "_".join(parts[-k:]) + tail] += 1
    top = [e for e, _ in ends.most_common(a.ends)]
    s, e = CONTRIB / f"seg_sound_asset{SFX}_stems.txt", CONTRIB / f"seg_sound_asset{SFX}_ends.txt"
    s.write_text("".join(x + "\n" for x in sorted(stems)), encoding="utf-8")
    e.write_text("".join(x + "\n" for x in top), encoding="utf-8")
    (CONTRIB / f"seg_sound_asset{SFX}.plan.txt").write_text(
        "label: sound-file segment plan -- modern sound stems x measured endings with format tail\n"
        f"describe: every underscore-prefix of every known modern sound file (xsounds_v2 + modern "
        f"findings), crossed with the top {len(top)} 1-3 segment endings+tails those files carry; "
        "see contrib/sound_segments.py\n"
        f"stem: @contrib/{s.name}\nend: @contrib/{e.name}\n", encoding="utf-8")
    print(f"sound_asset: {len(names)} names, {len(stems)} stems, {len(top)} endings", file=sys.stderr)


def heads(a, names):
    begins, rests = collections.Counter(), set()
    for name in names:
        s = split(name)
        if not s:
            continue
        lead, parts, tail = s
        for k in range(1, min(2, len(parts) - 1) + 1):
            begins[lead + "_".join(parts[:k])] += 1
            rests.add("_" + "_".join(parts[k:]) + tail)
    top = [b for b, _ in begins.most_common(a.ends)]
    b, r = CONTRIB / f"head_sound_asset{SFX}_begins.txt", CONTRIB / f"head_sound_asset{SFX}_rests.txt"
    b.write_text("".join(x + "\n" for x in top), encoding="utf-8")
    r.write_text("".join(x + "\n" for x in sorted(rests)), encoding="utf-8")
    (CONTRIB / f"head_sound_asset{SFX}.plan.txt").write_text(
        "label: sound-file head swap -- measured sound beginnings x every known remainder+tail\n"
        f"describe: top {len(top)} dir+1-2 segment beginnings of known modern sound files, crossed "
        "with every remainder+tail a known one leaves; see contrib/sound_segments.py --heads\n"
        f"stem: @contrib/{b.name}\nend: @contrib/{r.name}\n", encoding="utf-8")
    print(f"sound_asset heads: {len(top)} begins, {len(rests)} rests", file=sys.stderr)


if __name__ == "__main__":
    main()
