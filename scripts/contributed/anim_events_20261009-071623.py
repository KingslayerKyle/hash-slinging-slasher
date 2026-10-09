"""Weapon animations from weapon events: <anim head ending in the weapon> x <event> x <short ending>.

The reverse of contrib/anim_to_foley.py. Foley aliases are cut per animation event, so an event
seen in a foley alias (`fly_plr_ar_condor_inspect_empty_fast02_15`) or on a sibling weapon's
animation is a candidate animation for every weapon: `sat_vm_ar_condor_inspect_empty_fast02`.

Heads (prefix up to and including `<class>_<weapon>`: `sat_vm_ar_condor`, `vm_p04_sm_lwhiskey`,
`jup_vm_jp01_sh_aromeo410`) are measured on known modern animations; events are the ones
anim_to_foley.py --cross wrote; endings are bare plus the top short tails animations carry after
an event (`_ads`, `_settle`, `_loop`, `_in`, `_out`, ...).

    python contrib/anim_to_foley.py --cross && python contrib/anim_events.py
    confirm_plan contrib/anim_events.plan.txt --game BLACKOP7
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
MODERN = ("blackop6", "blackop7", "yamyamok", "modwar22", "modwar7")
CLS = "ar|sm|pi|sh|lm|br|dm|sn|me|la|ww|smg|pistol|lmg|dmr|shotgun|sniper|rifle|launcher|melee|special"
HEAD = re.compile(r"^((?:[a-z0-9]+_)?(?:(?:vm|wm)_)?(?:[a-z]{0,2}p\d*_)?(?:%s)_[a-z][a-z0-9]*)_(.+)$" % CLS)


def anims():
    f = ROOT / "cod-name-db" / "csv" / "fnv1a_xanims_v2.csv"
    for line in f.open(encoding="utf-8", errors="replace"):
        yield line.rstrip("\r\n").partition(",")[2].lower()
    for top in ("all_names", "findings"):
        for g in MODERN:
            for p in (ROOT / top / g).rglob("xanim*.txt"):
                for line in p.open(encoding="utf-8", errors="replace"):
                    yield line.rstrip("\r\n").partition(",")[2].lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ends", type=int, default=60)
    a = ap.parse_args()
    heads, tails = collections.Counter(), collections.Counter()
    events = set((CONTRIB / "anim_to_foley_x_events.txt").read_text(encoding="utf-8").split())
    for n in anims():
        m = HEAD.match(n)
        if not m:
            continue
        heads[m.group(1)] += 1
        rest = "_" + m.group(2)
        # the short tail after a known event, when the rest is <event><tail>
        parts = rest.split("_")[1:]
        for k in (1, 2):
            if len(parts) > k and "_" + "_".join(parts[:-k]) in events:
                tails["_" + "_".join(parts[-k:])] += 1
    tl = [t for t, _ in tails.most_common(a.ends)]
    nl = chr(10)
    (CONTRIB / "anim_events_heads.txt").write_text("".join(h + nl for h in sorted(heads)), encoding="utf-8")
    (CONTRIB / "anim_events_ends.txt").write_text("".join(t + nl for t in tl), encoding="utf-8")
    (CONTRIB / "anim_events.plan.txt").write_text(nl.join([
        "label: weapon animations -- per-weapon anim heads x weapon events x short endings",
        f"describe: {len(heads)} heads ending in a weapon code (measured on known modern animations) x the "
        f"events contrib/anim_to_foley.py measures x bare and the top {len(tl)} short endings; "
        "see contrib/anim_events.py",
        "begin: @contrib/anim_events_heads.txt", "stem: @contrib/anim_to_foley_x_events.txt",
        "end: @contrib/anim_events_ends.txt", ""]), encoding="utf-8")
    print(f"{len(heads)} heads, {len(events)} events, {len(tl)} ends", file=sys.stderr)


if __name__ == "__main__":
    main()
