"""Weapon sound files from weapon events: <head ending in the weapon> x <event> x <sub-event + tail>.

BO6/BO7 weapon sound files are cut per animation event and filed per weapon:
`sat/wpn/ar/heron/reloads/fly_plr_ar_heron_raise_first_chamberopen.lnn.75.48000.all`,
`t10/wpn/smg/geasy9/reloads/p02_sm_geasy9_reload_empty_fast01_mvmnt01.tnn.75.48000.all`.
The head (directory + file prefix up to and including the weapon code) is fixed per weapon, the
event is the animation's (contrib/anim_to_foley.py measures ~16k of them from animations and foley
aliases), and the ending is a sub-event and the format tail.

Heads are measured from every known modern sound file that contains a `<class>_<weapon>` token
in its basename; endings are the final 1-2 tokens + tail of the same files. The plan crosses
heads x events x endings, so an event from any animation meets every weapon's files.

    python contrib/anim_to_foley.py --cross && python contrib/foley_sound_files.py
    confirm_plan contrib/foley_sound_files.plan.txt --game BLACKOP7
"""
from pathlib import Path
import argparse
import collections
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
CONTRIB = ROOT / "contrib"
MODERN = ("blackop6", "blackop7", "modwar7")
CLS = "ar|sm|pi|sh|lm|br|dm|sn|me|la|smg|pistol|lmg|dmr|shotgun|sniper|rifle|launcher|melee|special"
WPN = re.compile(r"(?:^|_)((?:%s)_[a-z][a-z0-9]*)_" % CLS)


def sounds():
    f = ROOT / "cod-name-db" / "csv" / "fnv1a_xsounds_v2.csv"
    for line in f.open(encoding="utf-8", errors="replace"):
        yield line.rstrip("\r\n").partition(",")[2].lower()
    for top in ("all_names", "findings"):
        for g in MODERN:
            for p in (ROOT / top / g).rglob("sound_asset*.txt"):
                for line in p.open(encoding="utf-8", errors="replace"):
                    yield line.rstrip("\r\n").partition(",")[2].lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ends", type=int, default=4000)
    ap.add_argument("--heads", type=int, default=0)
    a = ap.parse_args()
    heads, ends = collections.Counter(), collections.Counter()
    for n in sounds():
        if "/wpn/" not in n or "." not in n:
            continue
        d, _, base = n.rpartition("/")
        stem, dot, tail = base.partition(".")
        m = WPN.search(stem)
        if not m:
            continue
        heads[d + "/" + stem[:m.end(1)]] += 1
        parts = stem[m.end(1):].split("_")
        for k in (1, 2):
            if len(parts) > k + 1:
                ends["_" + "_".join(parts[-k:]) + dot + tail] += 1
        ends[dot + tail] += 1
    hl = [h for h, _ in heads.most_common(a.heads or None)]
    el = [e for e, _ in ends.most_common(a.ends)]
    nl = chr(10)
    (CONTRIB / "foley_sound_heads.txt").write_text("".join(h + nl for h in hl), encoding="utf-8")
    (CONTRIB / "foley_sound_ends.txt").write_text("".join(e + nl for e in el), encoding="utf-8")
    (CONTRIB / "foley_sound_files.plan.txt").write_text(nl.join([
        "label: weapon sound files -- per-weapon heads x weapon events x sub-event+tail endings",
        f"describe: {len(hl)} dir+prefix heads ending in a weapon code (measured on known modern weapon "
        f"sound files) x the events contrib/anim_to_foley.py measures x top {len(el)} endings; "
        "see contrib/foley_sound_files.py",
        "begin: @contrib/foley_sound_heads.txt", "stem: @contrib/anim_to_foley_x_events.txt",
        "end: @contrib/foley_sound_ends.txt", ""]), encoding="utf-8")
    print(f"{len(hl)} heads, {len(el)} ends", file=sys.stderr)


if __name__ == "__main__":
    main()
